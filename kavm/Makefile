.PHONY: default all clean build install          \
        venv-config poetry-install               \
        test test-unit test-integration          \
        test-scenarios test-bison-parsers        \
        format isort autoflake black             \
        check check-isort check-autoflake check-black check-flake8 check-mypy

default: check test-unit build

clean:
	rm -rf dist .mypy_cache
	find -type d -name __pycache__ -prune -exec rm -rf {} \;

THREADS := $(if $(THREADS),$(THREADS),1)
PYTHON_VERSION := $(if $(PYTHON_VERSION),$(PYTHON_VERSION),3.10.6)
POETRY_RUN := poetry run
PYTEST_ARGS := -n $(THREADS) $(if $(PYTEST_PROFILING),--profile,)

venv-config:
	poetry config --local virtualenvs.in-project true
	poetry config --local virtualenvs.create true
	poetry config --local virtualenvs.path .venv
	poetry config --local virtualenvs.path

build:
	poetry build

poetry-install: venv-config
	poetry install


# Tests

test: test-unit test-integration

test-unit: poetry-install
	$(POETRY_RUN) python -m pytest $(PYTEST_ARGS) src/tests/unit

test-scenarios: poetry-install
	$(POETRY_RUN) python -m pytest --verbose $(PYTEST_ARGS) src/tests/semantics/test_avm_scenarios.py

test-bison-parsers: poetry-install
	$(POETRY_RUN) python -m pytest --verbose $(PYTEST_ARGS) src/tests/semantics/test_bison_parsers.py

test-integration: test-integration-algod test-integration-kalgod

test-integration-algod: poetry-install
	$(POETRY_RUN) python -m pytest $(PYTEST_ARGS) --backend=algod src/tests/algod_integration

test-integration-kalgod:
	$(POETRY_RUN) python -m pytest $(PYTEST_ARGS) --backend=kalgod src/tests/algod_integration

# Profiling

clean-profiling:
	rm -rf ./prof

# generate a Markdown report (into stdout) based on the currently present profiling information
transient-profiling-report:
	@$(POETRY_RUN) python -m profiling ./prof/combined.prof

# Checks and formatting

format: autoflake isort black
check: check-flake8 check-mypy check-autoflake check-isort check-black

isort: poetry-install
	$(POETRY_RUN) isort src

check-isort: poetry-install
	$(POETRY_RUN) isort --check src

autoflake: poetry-install
	$(POETRY_RUN) autoflake --quiet --in-place src

check-autoflake: poetry-install
	$(POETRY_RUN) autoflake --quiet --check src

check-flake8: poetry-install
	$(POETRY_RUN) flake8 src

black: poetry-install
	$(POETRY_RUN) black src

check-black: poetry-install
	$(POETRY_RUN) black --check src

check-mypy: poetry-install
	$(POETRY_RUN) mypy src
