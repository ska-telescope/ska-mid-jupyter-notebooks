import os
import pathlib


def project_root():
    return pathlib.Path(os.path.dirname(os.path.abspath(__file__)), "../../../")
