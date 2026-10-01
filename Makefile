.PHONY: help install test lint fmt type check build run clean

PY ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

help:
	@echo "install  test  lint  fmt  type  check  build  run  clean"

install:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"

test:
	$(BIN)/pytest --cov=tmig_closure --cov-report=term-missing

lint:
	$(BIN)/ruff check src tests

fmt:
	$(BIN)/ruff format src tests
	$(BIN)/ruff check --fix src tests

type:
	$(BIN)/mypy src

check: lint type test

build:
	$(BIN)/python -m build

run:
	$(BIN)/uvicorn tmig_closure.asgi:app --reload --host 127.0.0.1 --port 8000

clean:
	rm -rf $(VENV) build dist .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov

docstrings:
	$(BIN)/interrogate -c pyproject.toml src/

audit:
	$(BIN)/bandit -q -c pyproject.toml -r src
	$(BIN)/pip-audit --strict || true

track: lint type test docstrings
	@$(BIN)/coverage report --fail-under=100
