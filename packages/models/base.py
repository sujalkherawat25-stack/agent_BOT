from typing import Protocol
from pydantic import BaseModel


class ModelRequest(BaseModel):
    purpose: str
    system_instructions: str
    messages: list[dict]
    context_items: list[dict] = []
    reasoning_level: str | None = None
    max_output_tokens: int | None = None


class ModelResponse(BaseModel):
    text: str
    provider_response_id: str | None = None


class ModelProvider(Protocol):
    async def generate(self, request: ModelRequest) -> ModelResponse: ...
    async def generate_structured(self, request: ModelRequest, schema: type[BaseModel]) -> BaseModel: ...
