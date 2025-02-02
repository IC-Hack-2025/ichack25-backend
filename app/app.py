import logging

import flask
import flask_cors
import flask_socketio
from time import sleep

from core.model import Timeline
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
    if not isinstance(data, str):
        flask_socketio.emit("transmission_finished")
        return

    session = session_handler.get_session(flask.request.sid)
    session.clear_timeline()
    TimelineGenerator.generate_timeline(session.timeline, data)
    [_ for _ in TimelineGenerator.continue_timeline(session.timeline, 3)]
    sleep(1)
    flask_socketio.emit("transmission_finished")


@socketio.on("extend_timeline")
def handle_extend_timeline(node_id: int):
    if not isinstance(node_id, int):
        flask_socketio.emit("transmission_finished")
        return

    session = session_handler.get_session(flask.request.sid)
    [_ for _ in TimelineGenerator.continue_timeline(session.timeline, 3, node_id)]
    sleep(1)
    flask_socketio.emit("transmission_finished")


@ichack25_app.route('/')
def index():
    return flask.render_template('debug.html')


@ichack25_app.route('/query/create', methods=['POST'], endpoint="query_create")
def query_create():
    if flask.request.is_json:
        data = flask.request.get_json()
    else:
        data = flask.request.form.to_dict()
    if data is None or type(data) is not dict:
        flask.abort(400)
    query_text = data.get('query', None)
    if query_text is None:
        flask.abort(400)

    logging.info(f"Creating an event query: {query_text}")
    tg = TimelineGenerator()
    timeline = Timeline()
    tg.generate_timeline(timeline, query_text)
    _ = [_ for _ in tg.continue_timeline(timeline)]
    return timeline.to_json()


logging.info(
    f":: Available app routes ::\n{ichack25_app.url_map}"
)
