from typing import List, Optional, Iterator, Type
from pydantic import BaseModel
from openai import OpenAI
from core.model.timeline_node import ConnectionType, ContentType, TimelineConnection, TimelineContent, TimelineNode

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".env.local")

EVENT_GRAPH_DEPTH = 3
client = OpenAI()

def get_response(content: str, response_type: Type[BaseModel]) -> Optional[BaseModel]:
    return client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": content},
        ],
        response_format=response_type
    ).choices[0].message.parsed


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
        desc_content: TimelineContent = TimelineContent(content_type=ContentType.TEXT,
                                                        content=base_info.desc)
        node = TimelineNode(heading=base_info.heading,
                            date_start=base_info.date_start,
                            date_end=base_info.date_end,
                            contents=[desc_content],
                            misconceptions=misconceptions.misconceptions)
        yield node
        for causedEvent in base_info.causedEvents:
            for out in self.get(causedEvent, curr_depth + 1):
                yield out
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
        return get_response(f"Describe {event_name} in a short paragraph. Also give the names of any events it caused, and any events it influenced.", EventBaseResponse)
    def get_misconceptions(self, event_name: str) -> MisconceptionResponse:
        return get_response(f"Give some common misconceptions about {event_name} and their debunking arguments.",
                            MisconceptionResponse)


if __name__ == "__main__":
    g = EventGraph("The Battle of Hastings")
    for nodeOrEdge in g.get():
        print(nodeOrEdge)
