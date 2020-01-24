PY_DIRS=lti_provider
VE ?= ./ve
FLAKE8 ?= $(VE)/bin/flake8
REQUIREMENTS ?= test_reqs.txt
SYS_PYTHON ?= python3
PIP ?= $(VE)/bin/pip
PY_SENTINAL ?= $(VE)/sentinal
WHEEL_VERSION ?= 0.33.6
PIP_VERSION ?= 20.0.2
MAX_COMPLEXITY ?= 7
INTERFACE ?= localhost
RUNSERVER_PORT ?= 8000
PY_DIRS ?= $(APP)
DJANGO ?= "Django==1.11.27"


all: flake8 test

clean:
	rm -rf $(VE)
	find . -name '*.pyc' -exec rm {} \;

$(PY_SENTINAL):
	rm -rf $(VE)
	$(SYS_PYTHON) -m venv $(VE)
	$(PIP) install pip==$(PIP_VERSION)
	$(PIP) install --upgrade setuptools
	$(PIP) install wheel==$(WHEEL_VERSION)
	$(PIP) install --no-deps --requirement $(REQUIREMENTS) --no-binary cryptography
	$(PIP) install "$(DJANGO)"
	touch $@

test: $(REQUIREMENTS) $(PY_SENTINAL)
	./ve/bin/python runtests.py

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS) --max-complexity=$(MAX_COMPLEXITY)
