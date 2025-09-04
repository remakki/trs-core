import asyncio
import json
import time
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from faststream.rabbit import RabbitBroker

from src.api import TranscriptionClient, get_video_from_archive, OllamaClient
from src.config import settings
from src.log import log
from src.flow_processing.utils import delete_file

from src.promts import search_news_stories_system_prompt, summarize_news_story_system_prompt

class Subtitle:
    def __init__(self, start: float, end: float, text: str):
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return f"[{self.start:.2f}-{self.end:.2f}] {self.text}"


class FlowProcessing:
    def __init__(self, flow: dict[str, Any], mq_client: RabbitBroker, chunk_duration: int = 60):
        self._chunk_duration = chunk_duration
        self._time = int(datetime.now(timezone.utc).timestamp()) - (self._chunk_duration * 3 // 2)
        self._ai_search = OllamaClient(search_news_stories_system_prompt)
        self._ai_summarization = OllamaClient(summarize_news_story_system_prompt)
        self._transcription_client = TranscriptionClient()
        self._mq = mq_client
        self._flow_info = flow
        self._subtitles: list[Subtitle] = []

    def _get_subtitles_in_interval(self, start: float, end: float, presicion: float = 1.0) -> list[Subtitle]:
        """
        Get subtitles in the specified time interval with a given precision.
        """
        return [
            subtitle
            for subtitle in self._subtitles
            if subtitle.start >= start - presicion and subtitle.end <= end + presicion
        ]

    def _remove_subtitles(self, end: float, presicion: float = 1.0) -> None:
        """
        Remove subtitles that end before the specified time with a given precision.
        """
        self._subtitles = [
            subtitle
            for subtitle in self._subtitles
            if subtitle.end >= end - presicion
        ]

    @staticmethod
    def _serialize_subtitles(subtitles: list[Subtitle], line_sep: str = "\n") -> str:
        """
        Serialize a list of Subtitle objects into a single string with specified line separator.
        """
        return line_sep.join(map(str, subtitles))

    async def _iteration(self):
        try:
            filepath = Path("data") / f"{self._time}-{self._chunk_duration}.mp4"
            url = f"{self._flow_info['archive_url']}/archive-{self._time}-{self._chunk_duration - 5}.mp4?token={self._flow_info['archive_token']}"
            await get_video_from_archive(url, filepath)
        except Exception as err:
            log.error("An error occurred: %s", err)
        else:
            try:
                log.info("Transcribing...")
                segments = await self._transcription_client.transcribe(filepath)
            except Exception as e:
                log.error("Transcribing process error: %s", e)
            else:
                await delete_file(filepath)
                subtitles = [
                    Subtitle(
                        start=self._time + segment["start"],
                        end=self._time + segment["end"],
                        text=segment["text"],
                    )
                    for segment in segments
                ]
                self._subtitles.extend(subtitles)

                content = self._serialize_subtitles(self._subtitles)
                log.info("content: %s", content)
                try:
                    search_result = await self._ai_search.chat(content=content)
                    search_result = json.loads(search_result)
                except JSONDecodeError as e:
                    log.error("JSONDecodeError: %s", e)
                except Exception as e:
                    log.error(f"Unexpected error: {e}")
                else:
                    if search_result["intervals"]:
                        for interval in search_result["intervals"]:
                            start_interval, end_interval = map(
                                int,
                                map(
                                    float,
                                    [t for t in interval.strip().split("-")],
                                ),
                            )
                            subtitles_in_interval = self._get_subtitles_in_interval(
                                start_interval, end_interval
                            )
                            self._remove_subtitles(end_interval)  # remove subtitles from list
                            content = self._serialize_subtitles(subtitles_in_interval)
                            try:
                                summary_result_json = await self._ai_summarization.chat(
                                    content=content
                                )
                                summary_result = json.loads(summary_result_json)
                            except JSONDecodeError as e:
                                log.error("JSONDecode Error: %s", e)
                            except Exception as e:
                                log.error(f"Unexpected error: {e}")
                            else:
                                # save to DB

                                notice_info = {
                                    "chat_id": self._flow_info["channel"],
                                    "time_range": interval,
                                    **summary_result,
                                }
                                await self._mq.publish(notice_info, settings.RABBITMQ_QUEUE)


    async def process(self) -> None:
        while True:
            start_time_counter = time.perf_counter()
            await self._iteration()
            end_time_counter = time.perf_counter()

            duration_execution = end_time_counter - start_time_counter
            log.info("Duration execution: %s", str(duration_execution))
            if duration_execution < self._chunk_duration:
                await asyncio.sleep(self._chunk_duration - duration_execution)
            self._time += self._chunk_duration
