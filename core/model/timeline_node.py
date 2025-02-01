from typing import Union

import aenum
from pydantic import Field
from core.model.data_model import DataModel
from datetime import date


class ContentType(aenum.StrEnum):
    TEXT = "text"
    VIDEO = "video"
    URL = "url"
    CITATION = "citation"


class ConnectionType(aenum.StrEnum):
    CAUSED = "caused"
    INFLUENCED = "influenced"


class TimelineContent(DataModel):
    content_type: ContentType = Field(default=ContentType.TEXT)
    content: str


class TimelineNode(DataModel):
    heading: str
    date_start: Union[date, str]
    date_end: Union[date, str]

    contents: list[TimelineContent] = Field(default_factory=list)
    misconceptions: list[str] = Field(default_factory=list)


class TimelineConnection(DataModel):
    from_id: int
    to_id: int

    connection_type: ConnectionType = Field(ConnectionType.CAUSED)
