.PHONY: all clean                                                  \
        $(VENV_DEV_DIR) $(VENV_PROD_DIR)                           \
        test test-unit                                             \
        check-code-style black check-black isort check-isort       \
	check-flake8 check-mypy


all: check-code-style test


# virtualenv

VENV_DEV_DIR := venv-dev
VENV_DEV     := $(VENV_DEV_DIR)/pyvenv.cfg
ACTIVATE_DEV := . $(VENV_DEV_DIR)/bin/activate

$(VENV_DEV):
	   virtualenv -p python3.9 $(VENV_DEV_DIR) \
	&& $(ACTIVATE_DEV)                         \
	&& pip install -r requirements/dev.txt     \
	&& pip install --editable .

$(VENV_DEV_DIR): $(VENV_DEV)
	@echo $(ACTIVATE_DEV)


VENV_PROD_DIR := venv-prod
VENV_PROD     := $(VENV_PROD_DIR)/pyvenv.cfg
ACTIVATE_PROD := . $(VENV_PROD_DIR)/bin/activate

$(VENV_PROD):
	   virtualenv -p python3.9 $(VENV_PROD_DIR) \
	&& $(ACTIVATE_PROD)                         \
	&& pip install -r requirements/base.txt     \
	&& pip install --editable . --no-deps

$(VENV_PROD_DIR): $(VENV_PROD)
	@echo $(ACTIVATE_PROD)


# Tests

test: test-unit

test-unit: $(VENV_DEV)
	$(ACTIVATE_DEV) && python -m pytest --ignore=tests/contracts

test-integration: $(VENV_DEV)
	$(ACTIVATE_DEV) && python -m pytest tests/contracts

# Checks

check-code-style: check-isort check-flake8 check-black

isort: $(VENV_DEV)
	$(ACTIVATE_DEV) && isort --profile black .

check-isort: $(VENV_DEV)
	$(ACTIVATE_DEV) && isort --profile black --check .

check-flake8: $(VENV_DEV)
	$(ACTIVATE_DEV) && flake8 kavm_algod tests

check-mypy: $(VENV_DEV)
	$(ACTIVATE_DEV) && mypy .

black: $(VENV_DEV)
	$(ACTIVATE_DEV) && black --skip-string-normalization .

check-black: $(VENV_DEV)
	$(ACTIVATE_DEV) && black --check --skip-string-normalization .

clean:
	rm -rf $(VENV_DEV_DIR) $(VENV_PROD_DIR) build src/kavm_pyk.egg-info .myp_cache
	find -type d -name __pycache__ -prune -exec rm -rf {} \;
