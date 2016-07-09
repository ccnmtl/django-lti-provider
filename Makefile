PY_DIRS=lti_provider
OUTPUT_PATH=ve
VE ?= ./ve
FLAKE8 ?= $(VE)/bin/flake8
REQUIREMENTS ?= test_reqs.txt
SYS_PYTHON ?= python
PIP ?= $(VE)/bin/pip
PY_SENTINAL ?= $(VE)/sentinal
PYPI_URL ?= https://pypi.ccnmtl.columbia.edu/
WHEEL_VERSION ?= 0.24.0
VIRTUALENV ?= virtualenv
SUPPORT_DIR ?= requirements/virtualenv_support/
MAX_COMPLEXITY ?= 7
INTERFACE ?= localhost
RUNSERVER_PORT ?= 8000
PY_DIRS ?= $(APP)

all: test flake8

clean:
	rm -rf $(OUTPUT_PATH)

$(PY_SENTINAL):
	rm -rf $(VE)
	$(VIRTUALENV) --never-download $(VE)
	$(PIP) install --index-url=$(PYPI_URL) wheel==$(WHEEL_VERSION)
	$(PIP) install --use-wheel --no-deps --index-url=$(PYPI_URL) --requirement $(REQUIREMENTS)
	touch $@

test: $(REQUIREMENTS) $(PY_SENTINAL)
	./ve/bin/python runtests.py

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS) --max-complexity=$(MAX_COMPLEXITY)