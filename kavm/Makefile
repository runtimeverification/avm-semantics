.PHONY: all clean                                                  \
        $(VENV_DEV_DIR) $(VENV_PROD_DIR)                           \
        test test-unit                                             \
        check-code-style black check-black isort check-isort       \
	autoflake check-autoflake check-mypy


all: check-code-style test

ifeq "$(origin KAVM_DEFINITION_DIR)" "undefined"
KAVM_DEFINITION_DIR := ../.build/usr/lib/kavm/avm-llvm/avm-execution-kompiled
endif
export KAVM_DEFINITION_DIR

# virtualenv

VENV_DEV_DIR := venv-dev
VENV_DEV     := $(VENV_DEV_DIR)/pyvenv.cfg
ACTIVATE_DEV := . $(VENV_DEV_DIR)/bin/activate

$(VENV_DEV):
	   virtualenv -p python3.8 $(VENV_DEV_DIR) \
	&& $(ACTIVATE_DEV)                         \
	&& pip install -r requirements/dev.txt     \
	&& pip install --editable .

$(VENV_DEV_DIR): $(VENV_DEV)
	@echo $(ACTIVATE_DEV)


VENV_PROD_DIR := venv-prod
VENV_PROD     := $(VENV_PROD_DIR)/pyvenv.cfg
ACTIVATE_PROD := . $(VENV_PROD_DIR)/bin/activate

$(VENV_PROD):
	   virtualenv -p python3.8 $(VENV_PROD_DIR) \
	&& $(ACTIVATE_PROD)                         \
	&& pip install -r requirements/base.txt     \
	&& pip install --editable . --no-deps

$(VENV_PROD_DIR): $(VENV_PROD)
	@echo $(ACTIVATE_PROD)


# Tests

test: test-unit test-integration

test-unit: $(VENV_DEV)
	$(ACTIVATE_DEV) && python -m pytest tests/unit

test-integration: test-integration-algod test-integration-kalgod

test-integration-algod: $(VENV_DEV)
	$(ACTIVATE_DEV) && python -m pytest --backend=algod tests/algod_integration

test-integration-kalgod:
	$(ACTIVATE_DEV) && python -m pytest --backend=kalgod tests/algod_integration

# Checks

check-code-style: check-isort check-autoflake check-black check-mypy

isort: $(VENV_DEV)
	$(ACTIVATE_DEV) && isort --profile black .

check-isort: $(VENV_DEV)
	$(ACTIVATE_DEV) && isort --profile black --check .

autoflake: $(VENV_DEV)
	$(ACTIVATE_DEV) && autoflake --in-place --remove-all-unused-imports --recursive src tests

check-autoflake: $(VENV_DEV)
	$(ACTIVATE_DEV) && autoflake --remove-all-unused-imports --recursive --check src tests

check-mypy: $(VENV_DEV)
	$(ACTIVATE_DEV) && mypy .

black: $(VENV_DEV)
	$(ACTIVATE_DEV) && black .

check-black: $(VENV_DEV)
	$(ACTIVATE_DEV) && black --check .

clean:
	rm -rf $(VENV_DEV_DIR) $(VENV_PROD_DIR) build src/kavm_pyk.egg-info .myp_cache
	find -type d -name __pycache__ -prune -exec rm -rf {} \;
