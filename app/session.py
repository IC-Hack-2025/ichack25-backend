from core.model.timeline import Timeline
from core.model.timeline_node import TimelineNode, TimelineConnection

from flask_socketio import emit


class Session:
    timeline: Timeline
    logs: list[str]

    def __init__(self):
        self.timeline = Timeline()

    def add_node(self, node: TimelineNode):
        self.timeline.add_node(node)
        emit("add-node", node.to_dict())

    def log(self, msg: str):
        self.logs.append(msg)
        emit("add-log", {"msg": msg})

    def get_logger(self):
        return self.log

    def add_arc(self, arc: TimelineConnection):
        self.timeline.add_arc(arc)
        emit("add-arc", arc.to_dict())


class SessionHandler:
    sessions: dict[str, Session]

    def __init__(self):
        self.sessions = dict()

    def get_session(self, session_id: int) -> Session:
        return self.sessions.get(session_id, Session())

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions.pop(session_id)
