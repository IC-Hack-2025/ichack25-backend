import logging

import flask
import flask_cors


ichack25_app = flask.Flask(__name__, static_folder=None)
ichack25_app.url_map.strict_slashes = False
cors = flask_cors.CORS(ichack25_app, supports_credentials=True)


@ichack25_app.route('/')
def index():
    return "Hello Dev!"


logging.info(
    f":: Available app routes ::\n{ichack25_app.url_map}"
)
