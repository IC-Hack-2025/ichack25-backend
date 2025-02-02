import logging

import flask
import flask_cors
import flask_socketio
from core.process.timeline_generator import TimelineGenerator
from app.session import SessionHandler


ichack25_app = flask.Flask(__name__, static_folder=None)
ichack25_app.url_map.strict_slashes = False
flask_cors.CORS(ichack25_app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5000"}})
socketio = flask_socketio.SocketIO(ichack25_app, cors_allowed_origins="*")

session_handler = SessionHandler()


@socketio.on("connect")
def handle_connect():
    logging.info(f"client ${flask.request.sid} connected")


@socketio.on("disconnect")
def handle_disconnect():
    session_handler.clear_session(flask.request.sid)
    logging.info(f"client ${flask.request.sid} disconnected")


@socketio.on("request_timeline")
def handle_request_timeline(data: str):
    if data is not str:
        return

    session = session_handler.get_session(flask.request.sid)
    TimelineGenerator.generate_timeline(session.timeline, data)
    [_ for _ in TimelineGenerator.continue_timeline(session.timeline, 3)]
    flask_socketio.emit("transmission_finished")


@socketio.on("extend_timeline")
def handle_extend_timeline(node_id: int):
    if node_id is not int:
        return

    session = session_handler.get_session(flask.request.sid)
    [_ for _ in TimelineGenerator.continue_timeline(session.timeline, 3, node_id)]
    flask_socketio.emit("transmission_finished")


@ichack25_app.route('/')
def index():
    return flask.render_template('debug.html')


logging.info(
    f":: Available app routes ::\n{ichack25_app.url_map}"
)
