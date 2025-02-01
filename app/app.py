import logging

import flask
import flask_cors
import flask_socketio

from datetime import date

from core.model.timeline import Timeline
from core.model.timeline_node import TimelineNode

ichack25_app = flask.Flask(__name__, static_folder=None)
ichack25_app.url_map.strict_slashes = False
cors = flask_cors.CORS(ichack25_app, supports_credentials=True)
socketio = flask_socketio.SocketIO(ichack25_app)


@ichack25_app.route('/')
def index():
    return "Hello World!"


@socketio.on("connect")
def handle_connect():
    logging.info("client connected")


@socketio.on("disconnect")
def handle_disconnect():
    logging.info("client disconnected")


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


logging.info(
    f":: Available app routes ::\n{ichack25_app.url_map}"
)
