# disable convention and refactoring lint warnings
PYTHON_SWITCHES_FOR_PYLINT += --disable=C,R,W0612,E0401,W0611,W0105,E1121,W0511

# resolve various conflicts with Black formatting
PYTHON_SWITCHES_FOR_FLAKE8 += --extend-ignore=E501,W291,W503,F401,E402,F541,F704,F841

PYTHON_LINE_LENGTH = 99
PYTHON_RUNNER := poetry run
DOCS_SPHINXBUILD := poetry run python -m sphinx

include .make/oci.mk

include .make/python.mk

include .make/base.mk

include PrivateRules.mk
