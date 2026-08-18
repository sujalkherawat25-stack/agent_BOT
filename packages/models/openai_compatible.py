import httpx

from models.base import ModelProvider, ModelRequest, ModelResponse


class OpenAICompatibleProvider(ModelProvider):
    """Provider-neutral adapter for an explicitly enabled endpoint."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def generate(self, request: ModelRequest) -> ModelResponse:
        payload = {"model": self.model, "messages": [{"role": "system", "content": request.system_instructions}, *request.messages]}
        if request.max_output_tokens:
            payload["max_tokens"] = request.max_output_tokens
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, json=payload)
            response.raise_for_status()
        body = response.json()
        choice = (body.get("choices") or [{}])[0]
        return ModelResponse(text=str((choice.get("message") or {}).get("content") or ""), provider_response_id=body.get("id"))

    async def generate_structured(self, request: ModelRequest, schema):
        response = await self.generate(request.model_copy(update={"system_instructions": request.system_instructions + " Return only valid JSON."}))
        return schema.model_validate_json(response.text)
