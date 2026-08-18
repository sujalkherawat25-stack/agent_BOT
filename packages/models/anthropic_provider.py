import httpx

from models.base import ModelProvider, ModelRequest, ModelResponse


class AnthropicProvider(ModelProvider):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await httpx.AsyncClient(timeout=60).post(
            f"{self.base_url}/messages",
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": self.model, "system": request.system_instructions, "messages": request.messages, "max_tokens": request.max_output_tokens or 1200},
        )
        response.raise_for_status()
        body = response.json()
        text = "".join(item.get("text", "") for item in body.get("content", []) if item.get("type") == "text")
        return ModelResponse(text=text, provider_response_id=body.get("id"))

    async def generate_structured(self, request: ModelRequest, schema):
        response = await self.generate(request.model_copy(update={"system_instructions": request.system_instructions + " Return only valid JSON."}))
        return schema.model_validate_json(response.text)
