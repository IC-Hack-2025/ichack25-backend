import logging

import flask
import flask_cors


from datetime import date
from core.timeline_node import TimelineNode


ichack25_app = flask.Flask(__name__, static_folder=None)
ichack25_app.url_map.strict_slashes = False
cors = flask_cors.CORS(ichack25_app, supports_credentials=True)


@ichack25_app.route('/')
def index():
    return "Hello World!"

@ichack25_app.route('/test')
def test():
    node = TimelineNode(
        [],
        [],
        "Tom's Life",
        date(2006, 2, 24),
        date(2026, 6, 25),
        []
    ) 
    logging.info(node.to_json())
    return ""

logging.info(
    f":: Available app routes ::\n{ichack25_app.url_map}"
)
