from typing import List, Optional, Iterator
from pydantic import BaseModel
from ai import query_openai
from core.model.timeline_node import ConnectionType, TimelineConnection, TimelineNode, TimelineContent, \
    TimelineTextContent
import dateutil


EVENT_GRAPH_DEPTH: int = 3


class EventBaseResponse(BaseModel):
    date_start: str
    date_end: str
    heading: str
    desc: str
    causedEvents: list[str]
    influencedEvents: list[str]


class MisconceptionResponse(BaseModel):
    misconceptions: List[str]
    debunkingArguments: List[str]


class EventGraph:

    def __init__(self, start_event: str, depth: int = EVENT_GRAPH_DEPTH):
        self.start = start_event
        self.depth = depth

    def get(self, event_name: Optional[str] = None, curr_depth: int = 0) -> Iterator[TimelineNode | TimelineConnection]:
        if event_name is None:
            event_name = self.start
        if curr_depth > self.depth:
            return
        base_info: EventBaseResponse = self.get_base_info(event_name)
        misconceptions: MisconceptionResponse = self.get_misconceptions(event_name)
        try:
            date_start = dateutil.parser.parse(base_info.date_start, fuzzy=True)
        except ValueError:
            date_start = base_info.date_start
        try:
            date_end = dateutil.parser.parse(base_info.date_end, fuzzy=True)
        except ValueError:
            date_end = base_info.date_end
        node = TimelineNode(
            heading=base_info.heading,
            date_start=date_start,
            date_end=date_end,
        )
        node.contents = [TimelineTextContent(content=base_info.desc)]
        node.misconceptions = misconceptions.misconceptions

        yield node

        for causedEvent in base_info.causedEvents:
            for out in self.get(causedEvent, curr_depth + 1):
                if isinstance(out, TimelineNode):
                    edge = TimelineConnection(
                        from_id=node.id,
                        to_id=out.id,
                        connection_type=ConnectionType.CAUSED)
                    yield edge

        for influencedEvent in base_info.influencedEvents:
            for out in self.get(influencedEvent, curr_depth + 1):
                yield out
                if isinstance(out, TimelineNode):
                    edge = TimelineConnection(
                        from_id=node.id,
                        to_id=out.id,
                        connection_type=ConnectionType.INFLUENCED)
                    yield edge

    def get_base_info(self, event_name: str) -> EventBaseResponse:
        return query_openai(
            f"Describe {event_name} in a short paragraph. Also give the names of any events it caused, "
            f"and any events it influenced.",
            EventBaseResponse
        )

    def get_misconceptions(self, event_name: str) -> MisconceptionResponse:
        return query_openai(
            f"Give some common misconceptions about {event_name} and their debunking arguments.",
            MisconceptionResponse
        )


if __name__ == "__main__":
    g = EventGraph("The Battle of Hastings")
    for nodeOrEdge in g.get():
        print(nodeOrEdge)
