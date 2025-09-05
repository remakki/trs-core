from pathlib import Path

import aiofiles
import aiohttp

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

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=self._credentials) as response:
                response.raise_for_status()
                data = await response.json()

        token = data["access_token"]
        self._headers["Authorization"] = f"Bearer {token}"
        print(self._headers)

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

        async with aiofiles.open(audio_file_path, "rb") as f:
            file_bytes = await f.read()

        form = aiohttp.FormData()
        form.add_field("file", file_bytes, filename=Path(audio_file_path).name)
        form.add_field("language", language)
        form.add_field("result_format", result_format)
        form.add_field("model", model)
        print(form)

        response = await self._post(endpoint=endpoint, data=form)
        print(response)
        result = await response.json()
        return result["srt"]
