import logging
from datetime import datetime
from dotenv import load_dotenv

import paths


if __name__ == "__main__":
    start_time = datetime.now()
    load_dotenv(dotenv_path=paths.ENV_PATH)

    from logs import configure_logging
    configure_logging()

    logging.info("Starting Backend")

    from app import ichack25_app

    end_time = datetime.now()
    logging.info(f"--- Start up in {end_time - start_time} seconds ---")

    ichack25_app.run(host="0.0.0.0", port=5000, threaded=True, debug=True, use_reloader=False)
