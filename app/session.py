from core.model.timeline import Timeline

from flask_socketio import emit
from collections import defaultdict


class EmittingTimeline(Timeline):
    def add_node(self, node):
        emit("add_node", node.to_dict())
        return super().add_node(node)

    def add_arc(self, arc):
        emit("add_arc", arc.to_dict())
        return super().add_arc(arc)


class Session:
    timeline: EmittingTimeline
    logs: list[str]

    def __init__(self):
        self.timeline = EmittingTimeline()

    def log(self, msg: str):
        self.logs.append(msg)
        emit("add-log", {"msg": msg})

    def get_logger(self):
        return self.log


class SessionHandler:
    sessions: defaultdict[str, Session]

    def __init__(self):
        self.sessions = defaultdict(Session)

    def get_session(self, session_id: str) -> Session:
        return self.sessions[session_id]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions.pop(session_id)
