PY_DIRS=lti_provider
OUTPUT_PATH=ve
VE ?= ./ve
FLAKE8 ?= $(VE)/bin/flake8
REQUIREMENTS ?= test_reqs.txt
SYS_PYTHON ?= python
PIP ?= $(VE)/bin/pip
PY_SENTINAL ?= $(VE)/sentinal
WHEEL_VERSION ?= 0.30.0
VIRTUALENV ?= virtualenv.py
SUPPORT_DIR ?= requirements/virtualenv_support/
MAX_COMPLEXITY ?= 7
INTERFACE ?= localhost
RUNSERVER_PORT ?= 8000
PY_DIRS ?= $(APP)

all: flake8 test

clean:
	rm -rf $(OUTPUT_PATH)

$(PY_SENTINAL):
	rm -rf $(VE)
	$(SYS_PYTHON) $(VIRTUALENV) --extra-search-dir=$(SUPPORT_DIR) $(VE)
	$(PIP) install wheel==$(WHEEL_VERSION)
	$(PIP) install --use-wheel --no-deps --requirement $(REQUIREMENTS)
	touch $@

install-django: $(PY_SENTINAL)
	$(PIP) install "$(DJANGO)"

test: $(REQUIREMENTS) $(PY_SENTINAL)
	./ve/bin/python runtests.py

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS) --max-complexity=$(MAX_COMPLEXITY)
