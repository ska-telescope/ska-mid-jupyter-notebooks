"""Store the project path."""

import os
import pathlib


def project_root() -> pathlib.Path:
    """
    Set project root path.

    :return: path name
    """
    return pathlib.Path(os.path.dirname(os.path.abspath(__file__)), "../../../")
