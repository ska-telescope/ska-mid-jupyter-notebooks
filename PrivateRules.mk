python-lint-isort:
	isort --diff --profile black --profile black -w 99  src/ tests/ 

python-lint-black:
	black --diff --line-length 99 src/ tests/

python-lint-pylint:
	pylint --output-format=parseable  src/ tests/

python-lint-flake8:
	flake8 --show-source --statistics --max-line-length 99 src/ tests/

python-lint-mypy:
	mypy --config-file mypy.ini src/

python-lint-all: python-lint-isort python-lint-black python-lint-pylint python-lint-flake8 python-lint-mypy

count:
	find src/ -name "*.py" | xargs wc -l
	find tests/ -name "*.py" | xargs wc -l
