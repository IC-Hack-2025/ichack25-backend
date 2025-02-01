from typing import Optional

from pydantic import Field
from core.model.data_model import DataModel
from core.model.timeline_node import TimelineNode, TimelineConnection


class Timeline(DataModel):
    heading: str
    description: str
    root_id: Optional[int] = None
    nodes: list[TimelineNode] = Field(default_factory=list)
    arcs: list[TimelineConnection] = Field(default_factory=list)

    def add_node(self, node: TimelineNode):
        self.nodes.append(node)
        if self.root_id is None:
            self.root_id = node.id
