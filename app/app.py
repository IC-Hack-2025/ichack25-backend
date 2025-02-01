import logging

import flask
import flask_cors
import flask_socketio

from datetime import date

from ai import query_openai
from core.model.timeline import Timeline
from core.model.timeline_node import TimelineNode
from app.session_handler import SessionHandler


ichack25_app = flask.Flask(__name__, static_folder=None)
ichack25_app.url_map.strict_slashes = False
cors = flask_cors.CORS(ichack25_app, supports_credentials=True)
socketio = flask_socketio.SocketIO(ichack25_app)

session_handler = SessionHandler()


@socketio.on("connect")
def handle_connect():
    logging.info("client connected")


@socketio.on("disconnect")
def handle_disconnect():
    logging.info("client disconnected")


@socketio.on("request-timeline")
def handle_request_timeline(data: str):
    raise NotImplementedError()


@socketio.on("extend-timeline")
def handle_extend_timeline(node_id: str):
    raise NotImplementedError()


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
    result = query_openai(
        f"Tell me the events that were directly caused by or indirectly influenced by '{query_text}'. "
        f"List just their names and dates, no descriptions. Don't say any other text."
    )
    return result


logging.info(
    f":: Available app routes ::\n{ichack25_app.url_map}"
)
