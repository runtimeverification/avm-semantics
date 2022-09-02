.PHONY: default all clean build install          \
        poetry-install                           \
        test test-unit test-integration          \
        format isort autoflake black             \
        check check-isort check-autoflake check-black check-flake8 check-mypy

default: check test-unit build

clean:
	rm -rf dist .mypy_cache
	find -type d -name __pycache__ -prune -exec rm -rf {} \;

build:
	poetry build

poetry-install:
	poetry install

POETRY_RUN := poetry run

# Tests

test: test-unit test-integration

test-unit: poetry-install
	$(POETRY_RUN) python -m pytest --ignore=src/tests/contracts

test-integration: poetry-install
	$(POETRY_RUN) python -m pytest src/tests/contracts


# Checks and formatting

format: isort autoflake black
check: check-isort check-autoflake check-black check-flake8 check-mypy

isort: poetry-install
	$(POETRY_RUN) isort src

check-isort: poetry-install
	$(POETRY_RUN) isort --check src

autoflake: poetry-install
	$(POETRY_RUN) autoflake src    \
	  --in-place                   \
	  --quiet                      \
	  --recursive                  \
	  --expand-star-imports        \
	  --remove-all-unused-imports  \
	  --ignore-init-module-imports \
	  --remove-duplicate-keys      \
	  --remove-unused-variables

check-autoflake: poetry-install
	$(POETRY_RUN) autoflake src    \
	  --j 1                        \
	  --check                      \
	  --recursive                  \
	  --expand-star-imports        \
	  --remove-all-unused-imports  \
	  --ignore-init-module-imports \
	  --remove-duplicate-keys      \
	  --remove-unused-variables

check-flake8: poetry-install
	$(POETRY_RUN) flake8 src

black: poetry-install
	$(POETRY_RUN) black src

check-black: poetry-install
	$(POETRY_RUN) black --check src

check-mypy: poetry-install
	$(POETRY_RUN) mypy src
