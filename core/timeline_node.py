import aenum
from pydantic import Field
from core.model.data_model import DataModel
from datetime import date


current_id = 0


def next_id() -> int:
    global current_id
    current_id += 1
    return current_id


class ContentType(aenum.StrEnum):
    TEXT = "text"
    VIDEO = "video"
    URL = "url"
    CITATION = "citation"


class TimelineContent(DataModel):
    content_type: ContentType = Field(ContentType.TEXT)
    content: str


class TimelineNode(DataModel):
    id: int = Field(default_factory=next_id, frozen=True)
    parents: list[int] = Field(default_factory=list)
    children: list[int] = Field(default_factory=list)

    heading: str
    date_start: date
    date_end: date

    contents: list[TimelineContent] = Field(default_factory=list)
    misconceptions: list[str] = Field(default_factory=list)