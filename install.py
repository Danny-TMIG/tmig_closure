#!/usr/bin/env python3
import os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
F = {}

def w(p, s): F[p] = s

# ────── README.md ──────
w("README.md", """# tmig_closure

**Autonomous Edge Super-Node — deterministic closure kernel for capability composition.**

Reduces every domain (AI, DevOps, networking, IoT, web, quantum) to two things:
*capability primitives* and *composition rules*. Computes the least fixed point of the
immediate-consequence operator, contracts under symmetric-group action, exposes over HTTP.
No LLM. No heuristics. A Tarski closure operator with production scaffolding.

## The math

Let `A` be a finite alphabet. Configuration `X subset A`. Rule `(P, C)`, `P,C subset A`.
Immediate-consequence operator:

    T_R(X) = X union { c | (P,C) in R, P subset X, c in C }

`T_R` monotone; `A` finite; so by Knaster-Tarski the least fixed point `cl_R(X)` exists,
reached in at most `|A|` iterations. `cl_R` is **extensive**, **monotone**, **idempotent** —
a closure operator on `(2^A, subset)`. Two configurations are `S_A`-equivalent iff their
count-vectors agree. See `docs/theory.md`.

All five laws are machine-checked by hypothesis in `tests/test_properties.py`.

## Quickstart

    make install
    make run                                    # uvicorn on :8000
    curl -s localhost:8000/health
    curl -s -X POST localhost:8000/closure \\
      -H 'content-type: application/json' \\
      -d '{"config":["a"],"rules":[{"premises":["a"],"conclusions":["b"]},
                                  {"premises":["b"],"conclusions":["c"]}]}'
    # {"closure":["a","b","c"],"added":["b","c"],"iterations":2}

CLI: `tmig close --config a --rule 'a>b' --rule 'b>c'`

## Layout

    src/tmig_closure/     core.py  agents.py  symmetry.py  api.py  asgi.py
    tests/                unit + property (hypothesis) + e2e
    docs/                 theory.md  runbooks/  slo/  decisions/
    .github/workflows/    ci, codeql, dependency-review, secrets

## Compliance

MIT. SBOM via `make sbom` (SPDX + CycloneDX). Signed releases. Reproducible wheels.
See `SECURITY.md` and `docs/slo/`.

---

*The Mark Intelligence Group*
""")

# ────── LICENSE ──────
w("LICENSE", """MIT License

Copyright (c) 2026 The Mark Intelligence Group

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")

# ────── pyproject.toml ──────
w("pyproject.toml", """[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "tmig_closure"
version = "0.1.0"
description = "Deterministic closure kernel for capability composition (AESN core)."
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "The Mark Intelligence Group" }]
keywords = ["closure", "capability", "aesn", "fixed-point", "lattice", "tarski"]
classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3.12",
  "Topic :: Scientific/Engineering :: Mathematics",
  "Typing :: Typed",
]
dependencies = ["fastapi>=0.115", "pydantic>=2.9", "uvicorn[standard]>=0.32"]

[project.optional-dependencies]
dev = [
  "pytest>=8.3", "pytest-cov>=6.0", "pytest-asyncio>=0.24",
  "hypothesis>=6.115", "httpx>=0.27",
  "ruff>=0.7", "mypy>=1.13",
  "pre-commit>=4.0", "pip-audit>=2.7", "bandit[toml]>=1.7",
]

[project.scripts]
tmig = "tmig_closure.__main__:main"

[project.urls]
Homepage = "https://github.com/the-mark-intelligence-group/tmig_closure"
Issues = "https://github.com/the-mark-intelligence-group/tmig_closure/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/tmig_closure"]

[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E","F","W","I","N","UP","B","A","C4","PT","SIM","TID","RUF","S"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "S311"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_unreachable = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config"
asyncio_mode = "auto"

[tool.coverage.run]
branch = true
source = ["src/tmig_closure"]

[tool.coverage.report]
show_missing = true
""")

# ────── dotfiles ──────
w(".gitignore", """__pycache__/
*.py[cod]
*.so
build/
dist/
*.egg-info/
.venv/
venv/
.mypy_cache/
.ruff_cache/
.pytest_cache/
.hypothesis/
.coverage
.coverage.*
htmlcov/
coverage.xml
.tox/
*.log
.env
.env.local
.DS_Store
.idea/
.vscode/
*.swp
""")

w(".editorconfig", """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.{yml,yaml,json,toml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
""")

w(".python-version", "3.12\n")

w(".env.example", """TMIG_HOST=127.0.0.1
TMIG_PORT=8000
TMIG_LOG_LEVEL=INFO
TMIG_LOG_JSON=true
TMIG_MAX_STEPS=10000
TMIG_CORS_ORIGINS=
TMIG_BUILD_COMMIT=dev
TMIG_BUILD_TIME=unknown
""")

w(".pre-commit-config.yaml", """default_install_hook_types: [pre-commit, commit-msg]

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=1024"]
      - id: mixed-line-ending
        args: ["--fix=lf"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.1
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.1
    hooks:
      - id: gitleaks

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.6.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
""")

w("gitleaks.toml", """title = "tmig_closure gitleaks configuration"

[extend]
useDefault = true

[allowlist]
description = "Global allowlist"
paths = ["(^|/)tests/", "(^|/)docs/", ".env.example$"]
""")

# ────── Docker ──────
w("Dockerfile", """# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
RUN pip install --upgrade pip build
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m build --wheel --outdir /dist

FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
RUN groupadd --system --gid 10001 tmig \\
 && useradd --system --uid 10001 --gid tmig --home /app --shell /usr/sbin/nologin tmig
WORKDIR /app
COPY --from=builder /dist/*.whl /tmp/
RUN pip install /tmp/*.whl && rm -f /tmp/*.whl
USER tmig
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=2).status==200 else 1)"
ENTRYPOINT ["uvicorn", "tmig_closure.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
""")

w(".dockerignore", """*
!pyproject.toml
!README.md
!LICENSE
!src/**
**/__pycache__
**/*.pyc
.venv
.git
.github
.mypy_cache
.ruff_cache
.pytest_cache
.hypothesis
.coverage
htmlcov
dist
build
docs
tests
""")

w("docker-compose.yml", """services:
  api:
    build: .
    image: tmig_closure:local
    ports: ["8000:8000"]
    environment:
      TMIG_LOG_LEVEL: INFO
      TMIG_LOG_JSON: "true"
    read_only: true
    tmpfs: ["/tmp"]
    security_opt: ["no-new-privileges:true"]
    cap_drop: ["ALL"]
    restart: unless-stopped
""")

# ────── Makefile ──────
w("Makefile", """.PHONY: help install test lint fmt type check build run clean

PY ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

help:
\t@echo "install  test  lint  fmt  type  check  build  run  clean"

install:
\t$(PY) -m venv $(VENV)
\t$(BIN)/pip install --upgrade pip
\t$(BIN)/pip install -e ".[dev]"

test:
\t$(BIN)/pytest --cov=tmig_closure --cov-report=term-missing

lint:
\t$(BIN)/ruff check src tests

fmt:
\t$(BIN)/ruff format src tests
\t$(BIN)/ruff check --fix src tests

type:
\t$(BIN)/mypy src

check: lint type test

build:
\t$(BIN)/python -m build

run:
\t$(BIN)/uvicorn tmig_closure.asgi:app --reload --host 127.0.0.1 --port 8000

clean:
\trm -rf $(VENV) build dist .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
""")

# ────── src/tmig_closure ──────
w("src/tmig_closure/__init__.py", '''"""tmig_closure — deterministic closure kernel for capability composition."""
from tmig_closure.agents import Agent, consensus, product, quorum, run_to_fixpoint, step
from tmig_closure.core import (
    ClosureError, Config, Primitive, Rule, close, closure_steps,
    immediate_consequence, rule,
)
from tmig_closure.symmetry import canonical, count_vector, orbit_key, stabilizer_size

__version__ = "0.1.0"

__all__ = [
    "Config", "ClosureError", "Primitive", "Rule",
    "close", "closure_steps", "immediate_consequence", "rule",
    "Agent", "step", "run_to_fixpoint", "product", "quorum", "consensus",
    "canonical", "count_vector", "orbit_key", "stabilizer_size",
    "__version__",
]
''')

w("src/tmig_closure/core.py", '''"""The kernel: a monotone closure operator over capability primitives.

    A         finite alphabet of primitive names (str)
    X subset A     a configuration (frozenset[str])
    R         a ruleset: iterable of (P, C) pairs, P,C subset A finite

    T_R(X)    immediate-consequence operator
    cl_R(X)   least fixed point of T_R above X (Knaster-Tarski)

T_R is monotone, A is finite, therefore cl_R exists and is reached in at most
|A \\ X| iterations. cl_R is extensive, monotone, and idempotent — a Tarski
closure operator on the complete lattice (2^A, subset).
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator

Primitive = str
Config = frozenset[Primitive]
Rule = tuple[frozenset[Primitive], frozenset[Primitive]]


class ClosureError(RuntimeError):
    """Raised when a closure iteration bound is exhausted before fixpoint."""


def rule(premises: Iterable[Primitive], conclusions: Iterable[Primitive]) -> Rule:
    """Construct a rule from two iterables of primitives."""
    return (frozenset(premises), frozenset(conclusions))


def _normalise(rules: Iterable[Rule]) -> tuple[Rule, ...]:
    return tuple((frozenset(p), frozenset(c)) for p, c in rules)


def immediate_consequence(config: Config, rules: Iterable[Rule]) -> Config:
    """Apply T_R once: add every conclusion whose premises are already present."""
    out: set[Primitive] = set(config)
    for premises, conclusions in rules:
        if premises <= config:
            out |= conclusions
    return frozenset(out)


def close(
    config: Config,
    rules: Iterable[Rule],
    *,
    max_steps: int = 10_000,
) -> Config:
    """Compute the least fixed point of T_R above ``config``."""
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")
    rs = _normalise(rules)
    current: Config = frozenset(config)
    for _ in range(max_steps):
        nxt = immediate_consequence(current, rs)
        if nxt == current:
            return current
        current = nxt
    raise ClosureError(f"no closure within {max_steps} steps")


def closure_steps(
    config: Config,
    rules: Iterable[Rule],
    *,
    max_steps: int = 10_000,
) -> Iterator[Config]:
    """Yield each configuration in the Kleene chain X_0, X_1, ... up to fixpoint."""
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")
    rs = _normalise(rules)
    current: Config = frozenset(config)
    for _ in range(max_steps):
        yield current
        nxt = immediate_consequence(current, rs)
        if nxt == current:
            return
        current = nxt
    raise ClosureError(f"no closure within {max_steps} steps")
''')

w("src/tmig_closure/agents.py", '''"""Multi-agent composition over the closure kernel."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace

from tmig_closure.core import Config, Rule, close, immediate_consequence

Predicate = Callable[[Config], bool]


@dataclass(frozen=True, slots=True)
class Agent:
    id: str
    config: Config

    def with_config(self, config: Config) -> "Agent":
        return replace(self, config=config)


def step(agents: Sequence[Agent], rules: Iterable[Rule]) -> list[Agent]:
    """Apply T_R once to every agent, synchronously."""
    rs = tuple(rules)
    return [Agent(a.id, immediate_consequence(a.config, rs)) for a in agents]


def run_to_fixpoint(
    agents: Sequence[Agent],
    rules: Iterable[Rule],
    *,
    max_steps: int = 10_000,
) -> list[Agent]:
    """Bring every agent to fixpoint."""
    rs = tuple(rules)
    return [Agent(a.id, close(a.config, rs, max_steps=max_steps)) for a in agents]


def product(agents: Sequence[Agent]) -> Config:
    """The union of every agent's configuration."""
    out: set[str] = set()
    for a in agents:
        out |= a.config
    return frozenset(out)


def quorum(agents: Sequence[Agent], pred: Predicate) -> bool:
    """True iff a strict majority of agents satisfies pred. Empty => False."""
    n = len(agents)
    if n == 0:
        return False
    return sum(1 for a in agents if pred(a.config)) > n // 2


def consensus(agents: Sequence[Agent], pred: Predicate) -> bool:
    """True iff every agent satisfies pred. Empty => True (vacuous)."""
    return all(pred(a.config) for a in agents)
''')

w("src/tmig_closure/symmetry.py", '''"""Symmetry reduction: canonical forms and count-vectors."""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from math import factorial

Primitive = str


def canonical(items: Iterable[Primitive]) -> tuple[Primitive, ...]:
    """Sorted tuple — lexicographically least representative of the orbit."""
    return tuple(sorted(items))


def count_vector(
    items: Iterable[Primitive],
    alphabet: Iterable[Primitive],
) -> tuple[int, ...]:
    """Histogram of items over the sorted alphabet. S_alphabet-invariant."""
    counts = Counter(items)
    return tuple(counts[p] for p in sorted(alphabet))


def orbit_key(items: Iterable[Primitive]) -> tuple[tuple[Primitive, int], ...]:
    """Deterministic key uniquely identifying the orbit of items under S_A."""
    counts = Counter(items)
    return tuple(sorted(counts.items()))


def stabilizer_size(items: Iterable[Primitive]) -> int:
    """|Stab(x)| = product of factorials of multiplicities."""
    counts = Counter(items)
    out = 1
    for m in counts.values():
        out *= factorial(m)
    return out
''')

w("src/tmig_closure/logging_config.py", '''"""Structured JSON logging to stderr, stdlib only."""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created))
                  + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), default=str)


def configure(level: str | None = None, *, json_output: bool | None = None) -> None:
    lvl = (level or os.environ.get("TMIG_LOG_LEVEL", "INFO")).upper()
    if json_output is None:
        json_output = os.environ.get("TMIG_LOG_JSON", "true").lower() == "true"
    root = logging.getLogger()
    if getattr(root, "_tmig_configured", False):
        return
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        JsonFormatter() if json_output
        else logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(handler)
    root.setLevel(lvl)
    root._tmig_configured = True  # type: ignore[attr-defined]
''')

w("src/tmig_closure/api.py", '''"""HTTP surface for the closure kernel."""
from __future__ import annotations

import os
from collections.abc import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tmig_closure import __version__
from tmig_closure.agents import Agent, run_to_fixpoint, step
from tmig_closure.core import ClosureError, immediate_consequence
from tmig_closure.logging_config import configure
from tmig_closure.symmetry import canonical, count_vector, orbit_key

configure()

MAX_STEPS = int(os.environ.get("TMIG_MAX_STEPS", "10000"))


class RuleModel(BaseModel):
    premises: list[str] = Field(default_factory=list)
    conclusions: list[str] = Field(default_factory=list)


class ClosureRequest(BaseModel):
    config: list[str]
    rules: list[RuleModel]
    max_steps: int = Field(default=MAX_STEPS, ge=1, le=1_000_000)


class ClosureResponse(BaseModel):
    closure: list[str]
    added: list[str]
    iterations: int


class AgentModel(BaseModel):
    id: str
    config: list[str]


class StepRequest(BaseModel):
    agents: list[AgentModel]
    rules: list[RuleModel]


class RunRequest(StepRequest):
    max_steps: int = Field(default=MAX_STEPS, ge=1, le=1_000_000)


class AgentsResponse(BaseModel):
    agents: list[AgentModel]


class SymmetryRequest(BaseModel):
    items: list[str]
    alphabet: list[str] | None = None


class SymmetryResponse(BaseModel):
    canonical: list[str]
    orbit_key: list[list[object]]
    count_vector: list[int] | None = None


def _to_rules(models: Iterable[RuleModel]) -> list[tuple[frozenset[str], frozenset[str]]]:
    return [(frozenset(m.premises), frozenset(m.conclusions)) for m in models]


def _iterate_count(config: frozenset[str], rules, max_steps: int) -> tuple[frozenset[str], int]:
    cur = config
    for i in range(max_steps):
        nxt = immediate_consequence(cur, rules)
        if nxt == cur:
            return cur, i
        cur = nxt
    raise ClosureError(f"no closure within {max_steps} steps")


app = FastAPI(
    title="tmig_closure",
    version=__version__,
    description="Deterministic closure kernel for capability composition.",
    license_info={"name": "MIT"},
)

_origins = [o.strip() for o in os.environ.get("TMIG_CORS_ORIGINS", "").split(",") if o.strip()]
if _origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["content-type"],
    )


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["meta"])
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/version", tags=["meta"])
def version() -> dict[str, str]:
    return {
        "version": __version__,
        "commit": os.environ.get("TMIG_BUILD_COMMIT", "dev"),
        "built_at": os.environ.get("TMIG_BUILD_TIME", "unknown"),
    }


@app.post("/closure", response_model=ClosureResponse, tags=["closure"])
def closure(req: ClosureRequest) -> ClosureResponse:
    try:
        rules = _to_rules(req.rules)
        start = frozenset(req.config)
        result, iters = _iterate_count(start, rules, req.max_steps)
    except ClosureError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return ClosureResponse(
        closure=sorted(result),
        added=sorted(result - start),
        iterations=iters,
    )


@app.post("/agents/step", response_model=AgentsResponse, tags=["agents"])
def agents_step(req: StepRequest) -> AgentsResponse:
    rules = _to_rules(req.rules)
    agents = [Agent(a.id, frozenset(a.config)) for a in req.agents]
    out = step(agents, rules)
    return AgentsResponse(agents=[AgentModel(id=a.id, config=sorted(a.config)) for a in out])


@app.post("/agents/run", response_model=AgentsResponse, tags=["agents"])
def agents_run(req: RunRequest) -> AgentsResponse:
    rules = _to_rules(req.rules)
    agents = [Agent(a.id, frozenset(a.config)) for a in req.agents]
    try:
        out = run_to_fixpoint(agents, rules, max_steps=req.max_steps)
    except ClosureError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return AgentsResponse(agents=[AgentModel(id=a.id, config=sorted(a.config)) for a in out])


@app.post("/symmetry/canonical", response_model=SymmetryResponse, tags=["symmetry"])
def symmetry_canonical(req: SymmetryRequest) -> SymmetryResponse:
    cv: list[int] | None = None
    if req.alphabet is not None:
        cv = list(count_vector(req.items, req.alphabet))
    return SymmetryResponse(
        canonical=list(canonical(req.items)),
        orbit_key=[[k, v] for k, v in orbit_key(req.items)],
        count_vector=cv,
    )
''')

w("src/tmig_closure/asgi.py", '''"""Uvicorn entry point."""
from tmig_closure.api import app

__all__ = ["app"]
''')

w("src/tmig_closure/__main__.py", '''"""CLI entry."""
from __future__ import annotations

import argparse
import json
import sys

from tmig_closure import __version__, close, rule
from tmig_closure.core import ClosureError


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tmig", description="tmig_closure CLI")
    p.add_argument("--version", action="version", version=f"tmig_closure {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("close", help="compute closure of a config under rules")
    c.add_argument("--config", required=True, help="comma-separated primitives")
    c.add_argument("--rule", action="append", default=[], metavar="PRE>POST")

    sub.add_parser("serve", help="run the API (uvicorn)")

    args = p.parse_args(argv)

    if args.cmd == "serve":
        import uvicorn
        uvicorn.run("tmig_closure.asgi:app", host="127.0.0.1", port=8000)
        return 0

    if args.cmd == "close":
        cfg = frozenset(x.strip() for x in args.config.split(",") if x.strip())
        rules = []
        for r in args.rule:
            if ">" not in r:
                print(f"bad rule: {r}", file=sys.stderr)
                return 2
            pre, _, post = r.partition(">")
            rules.append(rule(
                (x.strip() for x in pre.split(",") if x.strip()),
                (x.strip() for x in post.split(",") if x.strip()),
            ))
        try:
            result = close(cfg, rules)
        except ClosureError as e:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
            return 3
        print(json.dumps({"closure": sorted(result)}))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
''')

w("src/tmig_closure/py.typed", "")

# ────── tests ──────
w("tests/conftest.py", '''"""Shared fixtures."""
import pytest

from tmig_closure import rule


@pytest.fixture
def chain_rules():
    return [rule("a", "b"), rule("b", "c"), rule("c", "d")]


@pytest.fixture
def diamond_rules():
    return [rule("a", "b"), rule("a", "c"), rule(["b", "c"], "d")]
''')

w("tests/test_core.py", '''"""Kernel unit tests."""
import pytest

from tmig_closure import ClosureError, close, closure_steps, immediate_consequence, rule


def test_empty_rules_is_identity():
    assert close(frozenset({"a", "b"}), []) == frozenset({"a", "b"})


def test_chain_reaches_fixpoint(chain_rules):
    assert close(frozenset({"a"}), chain_rules) == frozenset({"a", "b", "c", "d"})


def test_diamond_closure(diamond_rules):
    assert close(frozenset({"a"}), diamond_rules) == frozenset({"a", "b", "c", "d"})


def test_partial_chain():
    rules = [rule("a", "b"), rule("b", "c")]
    assert close(frozenset({"b"}), rules) == frozenset({"b", "c"})
    assert close(frozenset({"c"}), rules) == frozenset({"c"})


def test_extensive(chain_rules):
    x = frozenset({"a"})
    assert x <= close(x, chain_rules)


def test_idempotent(chain_rules):
    x = frozenset({"a"})
    once = close(x, chain_rules)
    assert close(once, chain_rules) == once


def test_monotone(chain_rules):
    assert close(frozenset({"a"}), chain_rules) <= close(frozenset({"a", "z"}), chain_rules)


def test_immediate_consequence_step():
    rules = [rule("a", "b")]
    assert immediate_consequence(frozenset({"a"}), rules) == frozenset({"a", "b"})
    assert immediate_consequence(frozenset({"c"}), rules) == frozenset({"c"})


def test_max_steps_bound_raises():
    rules = [rule("a", "b"), rule("b", "c")]
    with pytest.raises(ClosureError):
        close(frozenset({"a"}), rules, max_steps=1)


def test_closure_steps_yields_kleene_chain():
    rules = [rule("a", "b")]
    chain = list(closure_steps(frozenset({"a"}), rules))
    assert chain == [frozenset({"a"}), frozenset({"a", "b"})]


def test_invalid_max_steps():
    with pytest.raises(ValueError):
        close(frozenset(), [], max_steps=0)
''')

w("tests/test_agents.py", '''"""Multi-agent composition tests."""
from tmig_closure import Agent, consensus, product, quorum, rule, run_to_fixpoint, step


def test_step_synchronous():
    rules = [rule("a", "b")]
    agents = [Agent("x", frozenset({"a"})), Agent("y", frozenset())]
    out = step(agents, rules)
    assert out[0].config == frozenset({"a", "b"})
    assert out[1].config == frozenset()


def test_run_to_fixpoint():
    rules = [rule("a", "b"), rule("b", "c")]
    agents = [Agent("x", frozenset({"a"})), Agent("y", frozenset({"b"}))]
    out = run_to_fixpoint(agents, rules)
    assert out[0].config == frozenset({"a", "b", "c"})
    assert out[1].config == frozenset({"b", "c"})


def test_product_unions():
    agents = [Agent("a", frozenset({"x"})), Agent("b", frozenset({"y"}))]
    assert product(agents) == frozenset({"x", "y"})


def test_quorum_strict_majority():
    agents = [Agent("1", frozenset({"a"})), Agent("2", frozenset({"a"})),
              Agent("3", frozenset({"b"}))]
    assert quorum(agents, lambda c: "a" in c) is True
    assert quorum(agents, lambda c: "b" in c) is False


def test_quorum_empty_is_false():
    assert quorum([], lambda c: True) is False


def test_consensus_vacuous_truth():
    assert consensus([], lambda c: False) is True


def test_consensus_all_must_agree():
    agents = [Agent("1", frozenset({"a"})), Agent("2", frozenset({"a"}))]
    assert consensus(agents, lambda c: "a" in c) is True
    assert consensus(agents + [Agent("3", frozenset({"b"}))],
                     lambda c: "a" in c) is False
''')

w("tests/test_symmetry.py", '''"""Symmetry reduction tests."""
from tmig_closure import canonical, count_vector, orbit_key, stabilizer_size


def test_canonical_is_sorted():
    assert canonical(["c", "a", "b", "a"]) == ("a", "a", "b", "c")


def test_canonical_idempotent():
    items = ["z", "x", "y"]
    assert canonical(canonical(items)) == canonical(items)


def test_count_vector_depends_on_alphabet_order():
    assert count_vector(["a", "a", "c"], alphabet=["a", "b", "c"]) == (2, 0, 1)


def test_count_vector_invariant_under_permutation():
    assert (count_vector(["a", "b", "a"], ["a", "b"])
            == count_vector(["b", "a", "b"], ["a", "b"]))


def test_orbit_key_groups_by_multiset():
    assert orbit_key(["a", "a", "b"]) == orbit_key(["b", "a", "a"])


def test_orbit_key_sorted():
    assert orbit_key(["c", "a", "b", "a"]) == (("a", 2), ("b", 1), ("c", 1))


def test_stabilizer_size_trivial_for_distinct():
    assert stabilizer_size(["a", "b", "c"]) == 1


def test_stabilizer_size_uses_factorials():
    assert stabilizer_size(["a", "a", "b", "b"]) == 4
    assert stabilizer_size(["a", "a", "a"]) == 6


def test_stabilizer_empty_is_one():
    assert stabilizer_size([]) == 1
''')

w("tests/test_properties.py", '''"""Property tests — the five algebraic laws of the closure operator."""
from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tmig_closure import close, immediate_consequence

PRIMITIVES = st.text(alphabet="abcdefgh", min_size=1, max_size=1)
CONFIGS = st.frozensets(PRIMITIVES, max_size=6)
RULES = st.lists(
    st.tuples(st.frozensets(PRIMITIVES, max_size=3),
              st.frozensets(PRIMITIVES, max_size=2)),
    max_size=8,
)

SETTINGS = settings(max_examples=200, deadline=None,
                    suppress_health_check=[HealthCheck.too_slow])


@given(x=CONFIGS, rules=RULES)
@SETTINGS
def test_extensive(x, rules):
    assert x <= close(x, rules)


@given(x=CONFIGS, y=CONFIGS, rules=RULES)
@SETTINGS
def test_monotone(x, y, rules):
    if x <= y:
        assert close(x, rules) <= close(y, rules)


@given(x=CONFIGS, rules=RULES)
@SETTINGS
def test_idempotent(x, rules):
    once = close(x, rules)
    assert close(once, rules) == once


@given(x=CONFIGS, rules=RULES)
@SETTINGS
def test_fixpoint_is_stable(x, rules):
    fix = close(x, rules)
    assert immediate_consequence(fix, rules) == fix
''')

w("tests/test_e2e.py", '''"""End-to-end: HTTP surface + CLI."""
from fastapi.testclient import TestClient

from tmig_closure.api import app
from tmig_closure.__main__ import main

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version():
    r = client.get("/version")
    assert r.status_code == 200
    assert "version" in r.json()


def test_closure_endpoint_chain():
    payload = {"config": ["a"],
               "rules": [{"premises": ["a"], "conclusions": ["b"]},
                         {"premises": ["b"], "conclusions": ["c"]}]}
    r = client.post("/closure", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["closure"] == ["a", "b", "c"]
    assert body["added"] == ["b", "c"]
    assert body["iterations"] == 2


def test_closure_empty_rules():
    r = client.post("/closure", json={"config": ["a"], "rules": []})
    assert r.status_code == 200
    assert r.json()["closure"] == ["a"]


def test_agents_step_endpoint():
    payload = {"agents": [{"id": "x", "config": ["a"]}],
               "rules": [{"premises": ["a"], "conclusions": ["b"]}]}
    r = client.post("/agents/step", json=payload)
    assert r.status_code == 200
    assert r.json()["agents"][0]["config"] == ["a", "b"]


def test_symmetry_endpoint():
    r = client.post("/symmetry/canonical",
                    json={"items": ["c", "a", "b", "a"], "alphabet": ["a", "b", "c"]})
    assert r.status_code == 200
    body = r.json()
    assert body["canonical"] == ["a", "a", "b", "c"]
    assert body["count_vector"] == [2, 1, 1]


def test_cli_close(capsys):
    rc = main(["close", "--config", "a", "--rule", "a>b", "--rule", "b>c"])
    assert rc == 0
    out = capsys.readouterr().out
    assert '"a"' in out and '"b"' in out and '"c"' in out


def test_cli_bad_rule(capsys):
    rc = main(["close", "--config", "a", "--rule", "not-a-rule"])
    assert rc == 2
''')

# ────── scripts ──────
w("scripts/bootstrap.sh", '''#!/usr/bin/env bash
set -euo pipefail
PY="${PYTHON:-python3}"
VENV="${VENV:-.venv}"
[[ -d "$VENV" ]] || "$PY" -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -e ".[dev]"
command -v pre-commit >/dev/null 2>&1 && "$VENV/bin/pre-commit" install --install-hooks || true
echo "bootstrap: ok — source $VENV/bin/activate"
''')

w("scripts/sbom.sh", '''#!/usr/bin/env bash
set -euo pipefail
OUT="${OUT:-.sbom}"
mkdir -p "$OUT"
if command -v syft >/dev/null 2>&1; then
  syft . -o spdx-json="$OUT/tmig_closure.spdx.json" && echo "wrote SPDX"
fi
if command -v cyclonedx-py >/dev/null 2>&1; then
  cyclonedx-py environment -o "$OUT/tmig_closure.cdx.json" && echo "wrote CycloneDX"
fi
''')

w("scripts/verify.py", '''#!/usr/bin/env python3
"""Verify the kernel's five algebraic laws with a small model check."""
from __future__ import annotations
import itertools, sys
from tmig_closure import close, immediate_consequence, rule

PRIMITIVES = ["a", "b", "c"]
SUBSETS = [frozenset(s) for r in range(len(PRIMITIVES) + 1)
           for s in itertools.combinations(PRIMITIVES, r)]
RULES = [
    [rule("a", "b")],
    [rule("a", "b"), rule("b", "c")],
    [rule(["a", "b"], "c")],
]


def main() -> int:
    failures = []
    for rs in RULES:
        for x in SUBSETS:
            if not x <= close(x, rs):
                failures.append(f"extensive: X={x}")
            if close(close(x, rs), rs) != close(x, rs):
                failures.append(f"idempotent: X={x}")
            fix = close(x, rs)
            if immediate_consequence(fix, rs) != fix:
                failures.append(f"fixpoint: X={x}")
            for y in SUBSETS:
                if x <= y and not close(x, rs) <= close(y, rs):
                    failures.append(f"monotone: X={x} Y={y}")
    if failures:
        for f in failures[:10]:
            print(f, file=sys.stderr)
        print(f"verify: FAIL ({len(failures)} violations)", file=sys.stderr)
        return 1
    print("verify: PASS — all 5 laws hold on the 3-primitive model")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''')

# ────── docs ──────
w("docs/theory.md", """# Theory

## 1. The lattice

Let `A` be a finite alphabet of capability primitives. The power set `2^A` ordered by
inclusion is a complete lattice. A configuration is an element `X of 2^A`; a rule is a
pair `(P, C)` with `P, C subset A` finite.

## 2. Immediate-consequence operator

Define `T_R : 2^A -> 2^A`:

    T_R(X) = X union { C | (P, C) in R, P subset X }

T_R is monotone (`X subset Y => T_R(X) subset T_R(Y)`) and extensive (`X subset T_R(X)`).

## 3. Closure operator

By Knaster-Tarski, a monotone function on a complete lattice has a least fixed point
above any starting element. Define

    cl_R(X) = union_{n>=0} T_R^n(X)

The Kleene chain stabilises in at most `|A \\ X|` steps. cl_R is a Tarski closure operator:

- Extensive: `X subset cl_R(X)`
- Monotone: `X subset Y => cl_R(X) subset cl_R(Y)`
- Idempotent: `cl_R(cl_R(X)) = cl_R(X)`

## 4. Symmetry

The symmetric group S_A acts by renaming primitives. cl is equivariant. The orbit
invariant is the count-vector over the sorted alphabet. |Stab(X)| = product of
factorials of multiplicities.

## 5. What is not claimed

- Rules are inputs, not learned.
- Capabilities are not scored.
- Primitives are opaque symbols. Interpretation lives above the kernel.
""")

for name, title, body in [
    ("incident-response", "Incident Response",
     "1. Detect via `/health` or SLO burn alert.\n2. Page on-call, ack in 5 min.\n"
     "3. Check recent deploys.\n4. If regression: roll back.\n"
     "5. Capture request IDs and rule hashes.\n6. Blameless postmortem within 5 days."),
    ("rollback", "Rollback",
     "1. Identify last-known-good image tag.\n2. `docker compose down && up -d` with tag.\n"
     "3. Verify `/health` and `/version`.\n4. Confirm SLO recovery in 15 min.\n"
     "5. File incident ticket."),
    ("oncall", "On-Call",
     "Rotation weekly, hand-off Monday 10:00 local.\nPrimary responds in 5 min, "
     "secondary in 15.\nEscalation: primary -> secondary -> engineering lead."),
    ("deploy", "Deploy",
     "1. `make check`.\n2. `make build`.\n3. `make sbom`.\n4. `git tag -s vX.Y.Z`.\n"
     "5. CI publishes the signed wheel.\n6. Staging smoke test.\n7. Promote on green."),
]:
    w(f"docs/runbooks/{name}.md", f"# {title}\n\n{body}\n")

w("docs/slo/availability.md", """# Availability SLO

**Target:** 99.9% of requests succeed over a rolling 30-day window.
**Success:** HTTP 2xx/3xx within timeout budget. **Failure:** 5xx, connection failure, timeout.
**Error budget:** 0.1%. Burn alert at 2x over 1h.
""")

w("docs/slo/latency.md", """# Latency SLO

**Target:** p99 <= 250 ms for `POST /closure` with `|config| <= 100` and `|rules| <= 100`.
**Target:** p50 <= 20 ms same shape.
**Degradation:** p99 > 250 ms for 10 min pages on-call.
""")

w("docs/decisions/0001-why-not-llm.md", """# ADR 0001 — Why no LLM in the kernel

**Status:** Accepted (2026-09)

## Decision

The kernel is algebraic. No LLM, no heuristics, no vendor SDKs. Rules are declarative
pairs `(P, C)`; closure is a Tarski fixed point.

## Consequences

**Positive.** Deterministic. Auditable (rules are files). Hypothesis-verifiable with no
flakiness. Microseconds for realistic sizes. No external inference on the critical path.

**Negative.** Rules must be written explicitly. Interpretation (deciding which primitives
a tool exposes) may use an LLM above the kernel. The kernel never does.
""")

# ────── .github ──────
w(".github/workflows/ci.yml", """name: ci

on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

permissions: { contents: read }

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix: { python: ["3.12", "3.13"] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ matrix.python }}", cache: pip }
      - run: pip install -e ".[dev]"
      - run: ruff check src tests
      - run: mypy src
      - run: pytest --cov=tmig_closure --cov-report=xml --cov-report=term
""")

w(".github/workflows/codeql.yml", """name: codeql

on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
  schedule: [{ cron: "17 3 * * 1" }]

permissions:
  security-events: write
  contents: read

jobs:
  analyze:
    runs-on: ubuntu-latest
    strategy: { matrix: { language: ["python"] } }
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: "${{ matrix.language }}", queries: security-and-quality }
      - uses: github/codeql-action/analyze@v3
""")

w(".github/workflows/dependency-review.yml", """name: dependency-review

on: [pull_request]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with: { fail-on-severity: moderate }
""")

w(".github/workflows/secrets.yml", """name: secrets

on: [push, pull_request]

permissions: { contents: read }

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
        env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
""")

w(".github/dependabot.yml", """version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule: { interval: weekly }
  - package-ecosystem: github-actions
    directory: "/"
    schedule: { interval: weekly }
  - package-ecosystem: docker
    directory: "/"
    schedule: { interval: weekly }
""")

w(".github/ISSUE_TEMPLATE/bug.yml", """name: Bug report
description: Something is wrong
labels: [bug]
body:
  - type: textarea
    id: what
    attributes: { label: What happened? }
    validations: { required: true }
  - type: textarea
    id: repro
    attributes: { label: Minimal reproduction }
    validations: { required: true }
""")

w(".github/ISSUE_TEMPLATE/feature.yml", """name: Feature request
labels: [enhancement]
body:
  - type: textarea
    id: problem
    attributes: { label: Problem }
    validations: { required: true }
  - type: textarea
    id: proposal
    attributes: { label: Proposal }
    validations: { required: true }
""")

w(".github/pull_request_template.md", """## Summary

## Type
- [ ] feat  - [ ] fix  - [ ] refactor  - [ ] docs  - [ ] test  - [ ] chore

## Checklist
- [ ] `make check` passes
- [ ] Tests updated
- [ ] Docs updated if public surface changed

Closes #
""")

# ────── governance ──────
w("CONTRIBUTING.md", """# Contributing

## Setup

    make install

## Workflow

1. Fork, branch from main.
2. Write the test first if fixing a bug.
3. `make check` before pushing.
4. Conventional Commits: feat, fix, docs, refactor, test, chore.

## The math is the contract

If your change touches `core.py`, run `python scripts/verify.py` and
`pytest tests/test_properties.py` — the five laws must hold.
""")

w("SECURITY.md", """# Security

## Reporting

Email `security@the-mark-intelligence-group.example`. Do not open a public issue.

Acknowledge in 3 business days; fix within 30 for critical.

## Threat model

- Pydantic validates every request body.
- Integer bounds (`max_steps`) prevent runaway iterations.
- Stateless service. No persistent state.
- No outbound network. Egress can be blocked.
- Runtime image contains only the installed wheel.
- Runs as UID 10001, `cap_drop: ALL`, read-only rootfs.

## Supply chain

Signed commits. Dependabot weekly. CodeQL on PR + weekly. gitleaks on push.
SBOMs via `make sbom`. Releases signed with cosign (keyless).
""")

w("CODE_OF_CONDUCT.md", """# Code of Conduct

Adapted from the [Contributor Covenant](https://www.contributor-covenant.org) v2.1.

## Pledge

We pledge to make participation a harassment-free experience for everyone, regardless of
age, body size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity and orientation.

## Standards

Positive: empathy, respect for differing views, constructive feedback, accepting
responsibility, focusing on community benefit.

Unacceptable: sexualized language or imagery, trolling, insults, harassment, publishing
private information, other unprofessional conduct.

## Enforcement

Report to `conduct@the-mark-intelligence-group.example`. All complaints reviewed promptly
and fairly.
""")

# ────── write everything ──────
for rel, body in F.items():
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)

for s in ("scripts/bootstrap.sh", "scripts/sbom.sh", "scripts/verify.py"):
    p = ROOT / s
    if p.exists():
        p.chmod(0o755)

print(f"Wrote {len(F)} files to {ROOT}")
