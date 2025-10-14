.PHONY: all format lint test tests test_watch integration_tests docker_tests help extended_tests

# Default target executed when no arguments are given to make.
all: help

PYTHON ?= python3
PYTEST_ENV = PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

# Define a variable for the test file path.
TEST_FILE ?= tests/unit_tests/

test:
	$(PYTEST_ENV) $(PYTHON) -m pytest $(TEST_FILE)

integration_tests:
	$(PYTEST_ENV) $(PYTHON) -m pytest tests/integration_tests 

test_watch:
	$(PYTEST_ENV) $(PYTHON) -m ptw --snapshot-update --now . -- -vv tests/unit_tests

test_profile:
	$(PYTEST_ENV) $(PYTHON) -m pytest -vv tests/unit_tests/ --profile-svg

extended_tests:
	$(PYTEST_ENV) $(PYTHON) -m pytest --only-extended $(TEST_FILE)


######################
# LINTING AND FORMATTING
######################

# Define a variable for Python and notebook files.
PYTHON_FILES=src/
MYPY_CACHE=.mypy_cache
lint format: PYTHON_FILES=.
lint_diff format_diff: PYTHON_FILES=$(shell git diff --name-only --diff-filter=d main | grep -E '\.py$$|\.ipynb$$')
lint_package: PYTHON_FILES=src
lint_tests: PYTHON_FILES=tests
lint_tests: MYPY_CACHE=.mypy_cache_test

lint lint_diff lint_package lint_tests:
	$(PYTHON) -m ruff check .
	[ "$(PYTHON_FILES)" = "" ] || $(PYTHON) -m ruff format $(PYTHON_FILES) --diff
	[ "$(PYTHON_FILES)" = "" ] || $(PYTHON) -m ruff check --select I $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || $(PYTHON) -m mypy --strict $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || mkdir -p $(MYPY_CACHE) && $(PYTHON) -m mypy --strict $(PYTHON_FILES) --cache-dir $(MYPY_CACHE)

format format_diff:
	$(PYTHON) -m ruff format $(PYTHON_FILES)
	$(PYTHON) -m ruff check --select I --fix $(PYTHON_FILES)

spell_check:
	$(PYTHON) -m codespell --toml pyproject.toml

spell_fix:
	$(PYTHON) -m codespell --toml pyproject.toml -w

######################
# HELP
######################

help:
	@echo '----'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'test                         - run unit tests'
	@echo 'tests                        - run unit tests'
	@echo 'test TEST_FILE=<test_file>   - run all tests in file'
	@echo 'test_watch                   - run unit tests in watch mode'
