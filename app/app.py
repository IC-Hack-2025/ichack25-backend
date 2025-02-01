import logging
import json

import flask
import flask_cors

from datetime import date
from core.timeline_node import Timeline, TimelineConnection, TimelineNode

ichack25_app = flask.Flask(__name__, static_folder=None)
ichack25_app.url_map.strict_slashes = False
cors = flask_cors.CORS(ichack25_app, supports_credentials=True)


@ichack25_app.route('/')
def index():
    return "Hello World!"


@ichack25_app.route('/test')
def test():
    node = TimelineNode(
        heading="Tom's Life",
        date_start=date(2006, 2, 24),
        date_end=date(2026, 6, 25),
    )
    return node.to_json()

@ichack25_app.route('/after/<event>')
def event(event: str):
    logging.info("fetching information about {event}")

    return Timeline(
        nodes=[
            TimelineNode(
                heading="Placeholder",
                date_start=date(1970, 1, 1),
                date_end=date(1970, 1, 1)
            )
        ],
        arcs=[]
    ).to_json()


logging.info(
    f":: Available app routes ::\n{ichack25_app.url_map}"
)
