import logging
import time
from paths import LOGS_PATH

LOG_LEVEL = logging.INFO


def configure_logging():
    python_logs_file = LOGS_PATH / (time.asctime().replace(':', '-') + '.txt')
    logging.basicConfig(
        filename=python_logs_file,
        filemode='a',
        datefmt='%H:%M:%S',
        format='%(asctime)s │ %(message)s',
        level=LOG_LEVEL
    )
    console = logging.StreamHandler()
    console.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s │ %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().handlers.clear()
    logging.getLogger().addHandler(console)
