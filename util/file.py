from pathlib import Path

import paths


def project_standard_path_format(path: Path):
    if path.is_absolute() and path.is_relative_to(paths.PROJECT_ROOT_PATH):
        path = path.relative_to(paths.PROJECT_ROOT_PATH)
    return path.as_posix()


def from_project_standard_path_format(path: str | Path):
    if type(path) is str:
        path = Path(path)
    if not path.is_absolute():
        path = paths.PROJECT_ROOT_PATH / path
    return path
