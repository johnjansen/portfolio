# Makefile

.PHONY: install test lint clean run

# Default target
.DEFAULT_GOAL := run

# Configuration
PYTHON = python3
VENV = venv
SRC_DIR = src
CONFIG_DIR = config/development
PYTEST_FLAGS = -v
VENV_BIN = $(VENV)/bin
VENV_PYTHON = $(VENV_BIN)/python
VENV_PIP = $(VENV_BIN)/pip

# Environment setup
export PYTHONPATH := .:$(PYTHONPATH)  # Changed to include current directory
export CATWALK_ENV := development
export CATWALK_CONFIG_PATH := $(CONFIG_DIR)/config.yaml

install:
	pip install -e .

test: install
	PYTHONPATH=. pytest $(PYTEST_FLAGS) tests/  # Added explicit tests directory

lint:
	flake8 $(SRC_DIR)/
	black $(SRC_DIR)/ --check

format:
	black $(SRC_DIR)/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} +

run: install
	@echo "Starting Catwalk development server..."
	@echo "PYTHONPATH: $(PYTHONPATH)"
	@echo "Environment: $(CATWALK_ENV)"
	@echo "Config: $(CATWALK_CONFIG_PATH)"
	uvicorn catwalk.main:app --reload --host 0.0.0.0 --port 8000 --log-level info

venv:
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	@echo "Virtual environment created. Activate with: source $(VENV)/bin/activate"

setup: clean venv
	$(VENV_PIP) install -r requirements.txt
	@echo "Development environment setup complete"

# Helper targets for development
.PHONY: dev
dev: setup run

# Documentation generation
.PHONY: docs
docs:
	pdoc --html --output-dir docs/ $(SRC_DIR)

# Additional development helpers
.PHONY: check
check: lint test
	@echo "All checks passed!"
