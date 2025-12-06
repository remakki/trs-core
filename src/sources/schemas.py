from datetime import datetime

from pydantic import BaseModel


class StorylineMessage(BaseModel):
    start_time: datetime
    end_time: datetime
    title: str
    summary: str
    summary_ru: str | None = None
    temperature: str

    source_id: int

    tags: list[str]
