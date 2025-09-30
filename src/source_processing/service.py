import asyncio
import json
import time
import traceback
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path

from faststream.rabbit import RabbitBroker

from src.api import OllamaClient, TranscriptionClient, get_video_from_archive
from src.source_processing.utils import delete_file
from src.log import log
from src.promts import search_news_stories_system_prompt, summarize_news_story_system_prompt
from src.sources import SourceModel
from src.sources.schemas import StorylineMessage


class Subtitle:
    def __init__(self, start: float, end: float, text: str):
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return f"[{self.start:.2f}-{self.end:.2f}] {self.text}"


class SourceProcessing:
    def __init__(self, source: SourceModel, mq_client: RabbitBroker, chunk_duration: int = 60):
        self._chunk_duration = chunk_duration
        self._time = int(datetime.now(timezone.utc).timestamp()) - (self._chunk_duration * 3 // 2)
        self._ai_search = OllamaClient(search_news_stories_system_prompt)
        self._ai_summarization = OllamaClient(summarize_news_story_system_prompt)
        self._transcription_client = TranscriptionClient()
        self._mq = mq_client
        self._source = source
        self._subtitles: list[Subtitle] = []
        self._max_subtitles = 100

    def _add_subtitles(self, subtitles: list[Subtitle]) -> None:
        """
        Add multiple subtitles to the list of subtitles.
        """
        count_to_delete = max(len(self._subtitles) + len(subtitles) - self._max_subtitles, 0)
        self._subtitles = self._subtitles[count_to_delete:]
        self._subtitles += subtitles

    def _get_subtitles_in_interval(
        self, start: float, end: float, presicion: float = 1.0
    ) -> list[Subtitle]:
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
            subtitle for subtitle in self._subtitles if subtitle.end >= end - presicion
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
            url = f"{self._source.archive_url}/archive-{self._time}-{self._chunk_duration - 5}.mp4?token={self._source.archive_token}"
            await get_video_from_archive(url, filepath)
        except Exception as err:
            log.error("An error occurred: %s", err)
        else:
            try:
                log.info("Transcribing...")
                segments = await self._transcription_client.transcribe(filepath)
            except Exception as e:
                log.error("Transcribing process error: %s", e)
                log.error("Full traceback: %s", traceback.format_exc())
            else:
                subtitles = [
                    Subtitle(
                        start=self._time + segment["start"],
                        end=self._time + segment["end"],
                        text=segment["text"],
                    )
                    for segment in segments
                ]
                self._add_subtitles(subtitles)

                content = self._serialize_subtitles(self._subtitles)
                log.info("content: %s", self._serialize_subtitles(subtitles))
                try:
                    log.info("Content for search: %s", content)
                    search_result = await self._ai_search.chat(content=content)
                    search_result = json.loads(search_result)
                    log.info("Search result: %s", search_result)
                except JSONDecodeError as e:
                    log.error("JSONDecodeError: %s", e)
                except Exception as e:
                    log.error(f"Unexpected error: {e}")
                else:
                    if (
                        isinstance(search_result, dict)
                        and "intervals" in search_result
                        and search_result["intervals"]
                        and all(isinstance(interval, dict) for interval in search_result["intervals"])
                    ):
                        for interval in search_result["intervals"]:
                            start_interval, end_interval = map(
                                    float,
                                    [t for t in interval.strip().split("-")],
                                )
                            subtitles_in_interval = self._get_subtitles_in_interval(
                                start_interval, end_interval
                            )
                            self._remove_subtitles(end_interval)
                            content = self._serialize_subtitles(subtitles_in_interval)
                            try:
                                log.info("content for summary: %s", content)
                                summary_result_json = await self._ai_summarization.chat(
                                    content=content
                                )
                                summary_result = json.loads(summary_result_json)

                                storyline_message = StorylineMessage(
                                    start_time=datetime.fromtimestamp(start_interval),
                                    end_time=datetime.fromtimestamp(end_interval),
                                    title=summary_result["title"],
                                    summary=summary_result["summary"],
                                    summary_ru=summary_result["summary_ru"],
                                    temperature=summary_result["temperature"],
                                    source_id=self._source.id,
                                    tags=summary_result["tags"],
                                )
                                log.info("Summary result: %s", summary_result)
                            except JSONDecodeError as e:
                                log.error("JSONDecode Error: %s", e)
                            except Exception as e:
                                log.error(f"Unexpected error: {e}")
                            else:
                                await self._mq.publish(storyline_message, 'new_storyline')
                                log.info(f"Storyline message: {storyline_message.model_dump()}")
            finally:
                await delete_file(filepath)

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
