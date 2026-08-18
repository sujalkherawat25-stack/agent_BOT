import json
import httpx
from pydantic import BaseModel
from models.base import ModelProvider, ModelRequest, ModelResponse


class XAIProvider(ModelProvider):
    """Responses API adapter; domain code never imports xAI-specific client types."""
    endpoint = "https://api.x.ai/v1/responses"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key, self.model = api_key, model

    async def generate(self, request: ModelRequest) -> ModelResponse:
        payload = {"model": self.model, "input": [{"role": "system", "content": request.system_instructions}, *request.messages]}
        if request.max_output_tokens:
            payload["max_output_tokens"] = request.max_output_tokens
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self.endpoint, headers={"Authorization": f"Bearer {self.api_key}"}, json=payload)
            response.raise_for_status()
        body = response.json()
        text = "".join(part.get("text", "") for item in body.get("output", []) if item.get("type") == "message" for part in item.get("content", []))
        return ModelResponse(text=text, provider_response_id=body.get("id"))

    async def generate_structured(self, request: ModelRequest, schema: type[BaseModel]) -> BaseModel:
        constrained = request.model_copy(update={"system_instructions": request.system_instructions + " Return only JSON matching the requested schema."})
        response = await self.generate(constrained)
        return schema.model_validate(json.loads(response.text))
