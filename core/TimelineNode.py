from core.model.data_model import DataModel
from datetime import date

current_id = 0

def next_id() -> int:
    global current_id
    current_id += 1
    return current_id

class TimelineContent(DataModel):
    _VALID_KINDS = ["video", "text", "url", "citation"]

    kind: str
    content: str

    def __init__(self, kind: str, content: str):
        if kind not in self._VALID_KINDS:
            raise ValueError("TimelineContent was initialised with invalid kind!")
    
        self.kind = kind
        self.content = content

class TimelineNode(DataModel):
    node_id: int
    parents: list[int]
    children: list[int]
    heading: str
    date_start: date
    date_end: date
    contents: list[TimelineContent]

    def __init__(
        self,
        parents: list[int],
        children: list[int],
        heading: str,
        date_start: date,
        date_end: date,
        contents: list[TimelineContent]
    ):
        self.node_id = next_id()

        self.parents = parents
        self.children = children
        self.heading = heading
        self.date_start = date_start
        self.date_end = date_end
        self.contents = contents
  