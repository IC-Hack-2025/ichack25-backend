import os
from pathlib import Path

"""
Keep this file in the root of the project directory.
"""

PROJECT_ROOT_PATH = Path(__file__).parent
ENV_PATH = PROJECT_ROOT_PATH / ".env.local"

DATA_PATH = PROJECT_ROOT_PATH / ".data"
LOGS_PATH = PROJECT_ROOT_PATH / ".logs"

for path in [DATA_PATH, LOGS_PATH]:
    os.makedirs(path, exist_ok=True)
