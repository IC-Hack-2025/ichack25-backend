from core.model.timeline import Timeline


class SessionHandler:
    sessions: dict[int, Timeline]

    def __init__(self):
        self.sessions = []

    def get_timeline(self, session_id: int) -> Timeline:
        return self.sessions.get(session_id, Timeline())

    def clear_timeline(self, session_id: int):
        self.sessions.pop(session_id)
