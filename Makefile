# disable convention and refactoring lint warnings
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

notebook-do-lint:
	@mkdir -p build/reports;
	$(PYTHON_RUNNER) nbqa isort --check-only --profile=black --line-length=$(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(NOTEBOOK_LINT_TARGET)
	$(PYTHON_RUNNER) nbqa black --check --line-length=$(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(NOTEBOOK_LINT_TARGET)
	$(PYTHON_RUNNER) nbqa flake8 --show-source --statistics --max-line-length=$(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_FLAKE8) $(NOTEBOOK_SWITCHES_FOR_FLAKE8) $(NOTEBOOK_LINT_TARGET)

python-do-lint:
	@mkdir -p build/reports;
	$(PYTHON_RUNNER) isort --check-only --profile black --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(PYTHON_LINT_TARGET)
	$(PYTHON_RUNNER) black --exclude .+\.ipynb --check --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(PYTHON_LINT_TARGET)
	$(PYTHON_RUNNER) flake8 --show-source --statistics --max-line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_FLAKE8) $(PYTHON_LINT_TARGET)
