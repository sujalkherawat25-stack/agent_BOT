from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    user_id: str | None = None
    conversation_id: str | None = None
    timezone: str = "UTC"


class RouteDecision(BaseModel):
    mode: Literal["CHAT", "RESEARCH", "PRODUCTIVITY", "MEMORY_LOOKUP", "MIXED"]
    confidence: float = Field(ge=0, le=1)
    needs_web: bool = False
    needs_memory: bool = False
    memory_scopes: list[str] = []
    needs_task_state: bool = False
    risk: Literal["READ_ONLY", "INTERNAL_WRITE", "EXTERNAL_WRITE", "HIGH_IMPACT"] = "READ_ONLY"
    expected_output: Literal["ANSWER", "RESEARCH_REPORT", "TASK_MUTATION", "REMINDER", "PLAN", "MIXED_RESULT"] = "ANSWER"


class RunBudget(BaseModel):
    max_model_calls: int = 3
    max_total_tokens: int = 4000
    max_tool_calls: int = 3
    max_wall_seconds: int = 60
    max_estimated_cost_usd: float = 0.10


class ReminderView(BaseModel):
    id: str
    message: str
    trigger_at: datetime
    timezone: str
    status: str


class CreateReminderRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    trigger_at: datetime
    timezone: str = "UTC"
    idempotency_key: str | None = None
