from datetime import datetime, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_core.events import stream
from agent_core.router import route
from agent_core.schemas import AgentSettingsRequest, AgentSettingsView, ChatMessageRequest, CreateReminderRequest, ReminderView
from harnesses.productivity.intent import parse_reminder
from harnesses.productivity.service import create_and_verify_reminder
from models.base import ModelRequest
from models.openai_compatible import OpenAICompatibleProvider
from models.secrets import provider_secret
from storage.db import AgentRunRow, AgentSettingsRow, AuditEventRow, ConversationRow, MessageRow, ReminderRow, UserRow, session

router = APIRouter()


async def user_for(session: AsyncSession, user_id: str | None, timezone_name: str) -> UserRow:
    if user_id:
        found = await session.get(UserRow, user_id)
        if found:
            return found
    user = UserRow(id=user_id or str(uuid4()), timezone=timezone_name)
    session.add(user)
    await session.flush()
    return user


@router.get("/health")
async def health() -> dict:
    return {"ok": True, "service": "personal-agent", "version": "0.1.0"}


def settings_view(value: AgentSettingsRow | None) -> AgentSettingsView:
    if value is None:
        return AgentSettingsView()
    return AgentSettingsView(provider=value.provider, base_url=value.base_url, fast_model=value.fast_model, balanced_model=value.balanced_model, strong_model=value.strong_model, tools=value.tools_json)


@router.get("/settings", response_model=AgentSettingsView)
async def get_settings(user_id: str, db: AsyncSession = Depends(session)):
    return settings_view(await db.get(AgentSettingsRow, user_id))


@router.put("/settings", response_model=AgentSettingsView)
async def put_settings(request: AgentSettingsRequest, user_id: str, timezone_name: str = "UTC", db: AsyncSession = Depends(session)):
    user = await user_for(db, user_id, timezone_name)
    value = await db.get(AgentSettingsRow, user.id)
    if value is None:
        value = AgentSettingsRow(user_id=user.id)
        db.add(value)
    value.provider = request.provider
    value.base_url = request.base_url
    value.fast_model = request.fast_model
    value.balanced_model = request.balanced_model
    value.strong_model = request.strong_model
    value.tools_json = request.tools
    db.add(AuditEventRow(user_id=user.id, run_id=None, event_type="SETTINGS_UPDATED", payload_json={"provider": request.provider, "tools": request.tools}))
    await db.commit()
    return settings_view(value)


async def model_answer(message: str, preferences: AgentSettingsRow | None) -> str:
    if preferences is None or not preferences.tools_json.get("external_requests", False):
        return "External provider requests are disabled. Enable that permission in Settings before using an LLM API."
    secret = provider_secret(preferences.provider)
    if not secret and preferences.provider not in {"local", "ollama"}:
        return "No API key is configured for this provider. Add it in Settings, then try again."
    provider = OpenAICompatibleProvider(preferences.base_url, secret or "local", preferences.strong_model)
    response = await provider.generate(ModelRequest(purpose="chat", system_instructions="You are Memento, a concise local personal agent. Be helpful and honest about available tools.", messages=[{"role": "user", "content": message}], max_output_tokens=1200))
    return response.text or "The provider returned an empty response."


@router.post("/chat/messages")
async def post_message(request: ChatMessageRequest, db: AsyncSession = Depends(session)):
    user = await user_for(db, request.user_id, request.timezone)
    conversation = await db.get(ConversationRow, request.conversation_id) if request.conversation_id else None
    if conversation is None:
        conversation = ConversationRow(user_id=user.id, title=request.message[:80])
        db.add(conversation)
        await db.flush()
    decision = route(request.message)
    run = AgentRunRow(user_id=user.id, conversation_id=conversation.id, goal=request.message, mode=decision.mode.lower(), status="running", budget_json={"max_wall_seconds": 60})
    db.add_all([MessageRow(conversation_id=conversation.id, role="user", content=request.message), run, AuditEventRow(user_id=user.id, run_id=run.id, event_type="USER_MESSAGE_RECEIVED", payload_json={})])
    await db.flush()
    events: list[tuple[str, dict]] = [("run.started", {"status": "routing", "label": "Understanding request…"}), ("run.status_changed", {"status": "working", "label": "Preparing a safe action…"})]
    preferences = await db.get(AgentSettingsRow, user.id)
    reminder_enabled = preferences is None or preferences.tools_json.get("reminders", True)
    if decision.mode == "PRODUCTIVITY" and not reminder_enabled:
        answer = "Reminders are disabled in Settings, so I did not create anything. Enable Reminders in Tools to allow this action."
        run.status, run.completed_at = "completed", datetime.now(timezone.utc)
        db.add(MessageRow(conversation_id=conversation.id, role="assistant", content=answer))
        await db.commit()
        events.extend([("token", {"text": answer}), ("run.completed", {"status": "completed"})])
    elif decision.mode == "PRODUCTIVITY":
        try:
            intent = parse_reminder(request.message, user.timezone)
            reminder = await create_and_verify_reminder(db, user_id=user.id, run=run, message=intent.title, trigger_at=intent.trigger_at, tz=intent.timezone)
            answer = f"I’ll remind you to {reminder.message} at {reminder.trigger_at.astimezone(ZoneInfo(user.timezone)).strftime('%a, %b %d at %I:%M %p %Z')}."
            db.add(MessageRow(conversation_id=conversation.id, role="assistant", content=answer))
            await db.commit()
            events.extend([( "tool.completed", {"tool": "create_reminder", "status": "verified", "reminder": {"id": reminder.id, "message": reminder.message, "trigger_at": reminder.trigger_at.isoformat()}}), ("token", {"text": answer}), ("run.completed", {"status": "completed"})])
        except ValueError as error:
            run.status = "failed"
            db.add(AuditEventRow(user_id=user.id, run_id=run.id, event_type="RUN_FAILED", payload_json={"reason": str(error)}))
            await db.commit()
            events.extend([( "run.failed", {"status": "failed", "label": str(error)}), ("token", {"text": str(error)})])
    else:
        try:
            answer = await model_answer(request.message, preferences)
        except Exception as error:
            answer = f"The configured provider could not answer: {error}"
        run.status, run.completed_at = "completed", datetime.now(timezone.utc)
        db.add(MessageRow(conversation_id=conversation.id, role="assistant", content=answer))
        await db.commit()
        events.extend([( "token", {"text": answer}), ("run.completed", {"status": "completed"})])
    return StreamingResponse(stream(events, run.id), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/reminders", response_model=list[ReminderView])
async def list_reminders(user_id: str, db: AsyncSession = Depends(session)):
    result = await db.scalars(select(ReminderRow).where(ReminderRow.user_id == user_id).order_by(ReminderRow.trigger_at))
    return [ReminderView(id=row.id, message=row.message, trigger_at=row.trigger_at, timezone=row.timezone, status=row.status) for row in result]


@router.post("/reminders", response_model=ReminderView)
async def create_reminder(request: CreateReminderRequest, user_id: str, db: AsyncSession = Depends(session)):
    user = await user_for(db, user_id, request.timezone)
    preferences = await db.get(AgentSettingsRow, user.id)
    if preferences is not None and not preferences.tools_json.get("reminders", True):
        raise HTTPException(403, "Reminders are disabled in Settings")
    run = AgentRunRow(user_id=user.id, conversation_id=(await ensure_conversation(db, user.id)).id, goal=request.message, mode="productivity", status="running")
    db.add(run); await db.flush()
    reminder = await create_and_verify_reminder(db, user_id=user.id, run=run, message=request.message, trigger_at=request.trigger_at, tz=request.timezone)
    return ReminderView(id=reminder.id, message=reminder.message, trigger_at=reminder.trigger_at, timezone=reminder.timezone, status=reminder.status)


async def ensure_conversation(db: AsyncSession, user_id: str) -> ConversationRow:
    conversation = ConversationRow(user_id=user_id, title="API reminder")
    db.add(conversation); await db.flush()
    return conversation


@router.get("/runs/{run_id}")
async def get_run(run_id: str, db: AsyncSession = Depends(session)):
    run = await db.get(AgentRunRow, run_id)
    if run is None: raise HTTPException(404, "Run not found")
    return {"id": run.id, "status": run.status, "mode": run.mode, "goal": run.goal}
