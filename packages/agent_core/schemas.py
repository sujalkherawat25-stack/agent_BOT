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


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=4000)
    priority: Literal["low", "normal", "high"] = "normal"
    due_at: datetime | None = None


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=4000)
    priority: Literal["low", "normal", "high"] | None = None
    status: Literal["open", "in_progress", "done", "cancelled"] | None = None
    due_at: datetime | None = None


class TaskView(TaskCreateRequest):
    id: str
    user_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class MemoryCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    importance: int = Field(default=1, ge=1, le=5)


class MemoryView(MemoryCreateRequest):
    id: str
    created_at: datetime


class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    urls: list[str] = Field(min_length=1, max_length=10)


class ResearchCitation(BaseModel):
    source_id: str
    title: str | None
    url: str
    verified: bool
    snippet: str | None


class ResearchResponse(BaseModel):
    query: str
    summary: str
    citations: list[ResearchCitation]


class AgentSettingsRequest(BaseModel):
    provider: str = Field(default="xai", min_length=1, max_length=40)
    base_url: str = Field(default="https://api.x.ai/v1", min_length=8, max_length=500)
    fast_model: str = Field(default="grok-4.1-fast", min_length=1, max_length=120)
    balanced_model: str = Field(default="grok-4.1-fast", min_length=1, max_length=120)
    strong_model: str = Field(default="grok-4.6", min_length=1, max_length=120)
    tools: dict[str, bool] = Field(default_factory=lambda: {"reminders": True, "tasks": True, "research": False, "memory": False, "external_requests": False})


class AgentSettingsView(AgentSettingsRequest):
    api_key_configured: bool = False
