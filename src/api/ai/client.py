import asyncio

import ollama

from src.config import settings


class OllamaClient:
    def __init__(self, system_prompt: str | None = None, model: str | None = None) -> None:
        self._client = ollama.AsyncClient(
            host=settings.OLLAMA_BASE_URL,
            headers={"Authorization": f"Bearer {settings.OLLAMA_TOKEN}"},
        )
        self._model = model or settings.OLLAMA_MODEL
        self._messages = [{"role": "system", "content": system_prompt}] if system_prompt else []

    async def chat(self, content: str, system_prompt: str | None = None, model: str | None = None, timeout: float = 180.0) -> str:
        messages = self._messages + [{"role": "user", "content": content}]
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        answer = await asyncio.wait_for(
            self._client.chat(
                model=model or self._model,
                messages=messages,
            ),
            timeout=timeout,
        )
        return answer["message"]["content"]
