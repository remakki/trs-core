import asyncio

import ollama

from src.config import settings


class OllamaClient:
    def __init__(self, system_prompt: str, model: str | None = None) -> None:
        self._client = ollama.AsyncClient(
            host=settings.OLLAMA_BASE_URL,
            headers={"Authorization": f"Bearer {settings.OLLAMA_TOKEN}"},
        )
        self._model = model or settings.OLLAMA_MODEL
        self._messages = [{"role": "system", "content": system_prompt}]

    async def chat(self, content: str, model: str | None = None, timeout: float = 180.0) -> str:
        answer = await asyncio.wait_for(
            self._client.chat(
                model=model or self._model,
                messages=self._messages + [{"role": "user", "content": content}],
                format="json",
                options={
                    "temperature": 0.0,
                    "seed": 42,
                },
            ),
            timeout=timeout,
        )
        return answer["message"]["content"]
