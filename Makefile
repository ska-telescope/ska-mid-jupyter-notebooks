# disable convention and refactoring lint warnings
PYTHON_SWITCHES_FOR_PYLINT += --disable=C,R,W0612,E0401,W0611,W0105,E1121,W0511,W0104,E0611
PYTHON_SWITCHES_FOR_FLAKE8 += --extend-ignore=E402,F704,F401,E501,W503

PYTHON_LINE_LENGTH = 99
PYTHON_RUNNER := poetry run
DOCS_SPHINXBUILD := poetry run python -m sphinx

PYTHON_VARS_AFTER_PYTEST += --ignore=tests/unit/ska_mid_jupyter_notebooks/test_configure_resource.py --ignore=tests/unit/ska_mid_jupyter_notebooks/test_obsconfig.py --ignore=tests/unit/ska_mid_jupyter_notebooks/test_sb_generate.py --ignore=tests/unit/ska_mid_jupyter_notebooks/test_target_spec_mid.py

include .make/oci.mk

include .make/python.mk

include .make/base.mk

-include PrivateRules.mk

NOTEBOOK_LINT_TARGET=./notebooks || true
