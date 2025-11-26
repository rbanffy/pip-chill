.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help: ## Show this help
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


# -------- Cleaning --------------------------------------------------------------------------------

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/ dist/ .eggs/
	find . \( -name '*.egg-info' -o -name '*.egg' \) -exec rm -rf {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.py[co]' -delete
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -type d -exec rm -rf {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/ .coverage htmlcov/

# -------- Development / Testing -------------------------------------------------------------------

VENV_DIR := .venv
PY := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

venv:  ## create virtual environment
	@test -d $(VENV_DIR) || python -m venv $(VENV_DIR)
	@$(PIP) install --upgrade pip setuptools wheel

install: venv clean  ## install package in editable mode
	$(PIP) install -e ".[dev,test,docs]"

lint: venv ## check style with flake8
	$(PIP) install flake8 flake8-bugbear flake8-import-order pylint
	$(VENV_DIR)/bin/flake8 pip_chill tests
	$(VENV_DIR)/bin/pylint pip_chill --exit-zero

test: venv ## run tests quickly
	$(PIP) install pytest
	$(VENV_DIR)/bin/pytest

coverage: venv ## run coverage
	$(PIP) install coverage pytest
	$(VENV_DIR)/bin/coverage run --source pip_chill -m pytest
	$(VENV_DIR)/bin/coverage report -m
	$(VENV_DIR)/bin/coverage html
	$(BROWSER) htmlcov/index.html

# -------- Documentation ---------------------------------------------------------------------------

docs: venv ## generate Sphinx HTML documentation
	$(PIP) install sphinx
	rm -f docs/pip_chill.rst docs/modules.rst
	sphinx-apidoc -o docs/ pip_chill
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

# -------- Packaging / Release ---------------------------------------------------------------------

build: venv clean ## build source and wheel package
	$(PIP) install build
	$(PY) -m build
	@ls -l dist

dist: build

release: venv clean ## build and upload release
	$(PIP) install twine
	$(PY) -m build
	$(PY) -m twine upload dist/*
