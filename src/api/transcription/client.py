from pathlib import Path

import httpx

from src.api.base_client import BaseClient
from src.api.transcription.schemas import Segment
from src.config import settings


class TranscriptionClient(BaseClient):
    def __init__(self):
        super().__init__(
            settings.TRANSCRIPTION_BASE_URL,
            {
                "username": settings.TRANSCRIPTION_USERNAME,
                "password": settings.TRANSCRIPTION_PASSWORD,
            },
        )

    async def login(self) -> None:
        """
        Login to the transcription service.
        """
        endpoint = f"{self._base_url}/api/v1/auth/login"

        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, json=self._credentials)
            response.raise_for_status()
            data = response.json()

        token = data["access_token"]
        self._headers["Authorization"] = f"Bearer {token}"

    async def transcribe(
        self,
        audio_file_path: str | Path,
        language: str = "en",
        result_format: str = "srt",
        model: str = "turbo",
    ) -> list[Segment]:
        """
        Transcribe an audio file using the transcription service.
        """
        if "Authorization" not in self._headers:
            await self.login()

        endpoint = f"{self._base_url}/api/v1/transcription/transcribe"

        audio_path = Path(audio_file_path)
        files = {
            "file": (audio_path.name, open(audio_path, "rb"), "audio/mpeg"),
        }
        data = {
            "language": language,
            "result_format": result_format,
            "model": model,
        }

        response = await self._post(endpoint=endpoint, files=files, data=data)
        result = response.json()
        return result["srt"]
