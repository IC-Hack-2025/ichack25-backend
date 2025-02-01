import logging

import flask
import flask_cors
import flask_socketio
from datetime import date
from core.model.timeline import Timeline
from core.model.timeline_node import TimelineNode
from core.process.timeline_generator import TimelineGenerator
from app.session import SessionHandler


ichack25_app = flask.Flask(__name__, static_folder=None)
ichack25_app.url_map.strict_slashes = False
cors = flask_cors.CORS(ichack25_app, supports_credentials=True)
socketio = flask_socketio.SocketIO(ichack25_app)

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
    session = session_handler.get_session(flask.request.sid)
    TimelineGenerator.generate_timeline(session.timeline, data)
    [_ for _ in TimelineGenerator.continue_timeline(session.timeline, 3)]
    flask_socketio.emit("transmission_finished")


@socketio.on("extend_timeline")
def handle_extend_timeline(node_id: str):
    if not node_id.isdigit():
        return
    session = session_handler.get_session(flask.request.sid)
    [_ for _ in TimelineGenerator.continue_timeline(session.timeline, 3, int(node_id))]
    flask_socketio.emit("transmission finished")


@ichack25_app.route('/')
def index():
    return flask.render_template('debug.html')


@ichack25_app.route('/after/<event>', methods=['GET'], )
def get_event(event: str):
    logging.info(f"fetching information about '{event}'")

    t = Timeline(
        heading="This is a timeline",
        description="This is a timeline description"
    )
    t.add_node(
        TimelineNode(
            heading="Placeholder",
            date_start=date(1970, 1, 1),
            date_end=date(1970, 1, 1)
        )
    )
    return t.to_json()


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
    timeline = tg.generate_timeline(query_text)
    _ = [_ for _ in tg.continue_timeline(timeline)]
    return timeline.to_json()


logging.info(
    f":: Available app routes ::\n{ichack25_app.url_map}"
)
