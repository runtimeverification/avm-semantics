.PHONY: all clean                                                  \
        $(VENV_DEV_DIR) $(VENV_PROD_DIR)                           \
        test test-unit                                             \
        check-code-style isort check-isort check-flake8 check-mypy


all: check-code-style test


# virtualenv

VENV_DEV_DIR := venv-dev
VENV_DEV     := $(VENV_DEV_DIR)/pyvenv.cfg
ACTIVATE_DEV := . $(VENV_DEV_DIR)/bin/activate

$(VENV_DEV):
	   virtualenv -p python3.8 $(VENV_DEV_DIR) \
	&& $(ACTIVATE_DEV)                         \
	&& pip install -r requirements/dev.txt

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

test: test-unit

test-unit: $(VUnitTestENV_DEV)
	$(ACTIVATE_DEV) && python3 -m unittest discover -s src


# Checks

check-code-style: check-isort check-flake8 check-mypy

isort: $(VENV_DEV)
	$(ACTIVATE_DEV) && isort src

check-isort: $(VENV_DEV)
	$(ACTIVATE_DEV) && isort --check src

check-flake8: $(VENV_DEV)
	$(ACTIVATE_DEV) && flake8 src

check-mypy: $(VENV_DEV)
	$(ACTIVATE_DEV) && mypy src


clean:
	rm -rf $(VENV_DEV_DIR) $(VENV_PROD_DIR) build src/kavm_pyk.egg-info .myp_cache
	find -type d -name __pycache__ -prune -exec rm -rf {} \;
