from typing import Union, Optional

import aenum
from pydantic import Field
from core.model.data_model import DataModel
from datetime import date


class ContentType(aenum.StrEnum):
    TEXT = "text"
    VIDEO = "video"
    URL = "url"
    CITATION = "citation"
    IMAGE = "image"
    MISCONCEPTION = "misconception"


class ConnectionType(aenum.StrEnum):
    CAUSED = "caused"
    INFLUENCED = "influenced"


class TimelineContent(DataModel):
    content_type: ContentType


class TimelineTextContent(TimelineContent):
    content_type: ContentType = Field(default=ContentType.TEXT)
    content: str
    isText: bool = True


class TimelineImageContent(TimelineContent):
    content_type: ContentType = Field(default=ContentType.IMAGE, frozen=True)
    title: str
    image_url: str
    link: str
    isText: bool = False


class TimelineConnection(DataModel):
    from_id: int
    to_id: int

    connection_type: ConnectionType = Field(ConnectionType.CAUSED)


class TimelineNode(DataModel):
    heading: str
    date_start: Union[date, str]
    date_end: Union[date, str]
    main_image_url: Optional[TimelineImageContent] = None
    contents: list[TimelineContent] = Field(default_factory=list)
    connections: list[TimelineConnection] = Field(default_factory=list)

    @property
    def full_description(self):
        return f" ".join(c.content for c in self.contents if type(c) is TimelineTextContent)

    @property
    def arcs_in(self) -> list[TimelineConnection]:
        return [c for c in self.connections if c.to_id == self.id]

    @property
    def arcs_out(self) -> list[TimelineConnection]:
        return [c for c in self.connections if c.from_id == self.id]

