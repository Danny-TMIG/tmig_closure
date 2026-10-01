"""Tests that close the remaining statement/branch coverage gaps.

Targets, by file:
  __main__.py        serve path, bad-rule path, ClosureError path
  agents.py          with_config
  api.py             /ready, /agents/run, /agents/run error, CORS, version commit
  core.py            closure_steps max_steps exhaustion, invalid max_steps
  logging_config.py  exception formatting, non-JSON configure, idempotency
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

from tmig_closure import Agent, ClosureError, close, closure_steps, rule
from tmig_closure.__main__ import main
from tmig_closure.api import app
from tmig_closure.logging_config import JsonFormatter, configure

client = TestClient(app)


# ── __main__.py ──────────────────────────────────────────────────


def test_main_serve_invokes_uvicorn(monkeypatch):
    called: dict = {}

    def fake_run(target, host=None, port=None):
        called["target"] = target
        called["host"] = host
        called["port"] = port

    import uvicorn

    monkeypatch.setattr(uvicorn, "run", fake_run)

    rc = main(["serve"])
    assert rc == 0
    assert called["target"] == "tmig_closure.asgi:app"
    assert called["port"] == 8000


def test_main_close_closure_error(capsys, monkeypatch):
    """Force ClosureError so the except branch runs."""

    def boom(*a, **kw):
        raise ClosureError("simulated")

    monkeypatch.setattr("tmig_closure.__main__.close", boom)
    rc = main(["close", "--config", "a", "--rule", "a>b"])
    assert rc == 3
    err = capsys.readouterr().err
    assert "simulated" in err


def test_main_bad_rule_returns_2(capsys):
    rc = main(["close", "--config", "a", "--rule", "no-arrow-here"])
    assert rc == 2
    assert "bad rule" in capsys.readouterr().err


def test_module_entrypoint_runs():
    """Execute `python -m tmig_closure` --version as a real subprocess."""
    r = subprocess.run(
        [sys.executable, "-m", "tmig_closure", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert "tmig_closure" in r.stdout


# ── agents.py ────────────────────────────────────────────────────


def test_agent_with_config_returns_new_instance():
    a = Agent("a", frozenset({"x"}))
    b = a.with_config(frozenset({"y"}))
    assert a is not b
    assert a.id == b.id == "a"
    assert b.config == frozenset({"y"})
    assert a.config == frozenset({"x"})  # original untouched


# ── api.py ───────────────────────────────────────────────────────


def test_api_ready():
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_api_version_uses_env(monkeypatch):
    monkeypatch.setenv("TMIG_BUILD_COMMIT", "deadbeef")
    monkeypatch.setenv("TMIG_BUILD_TIME", "2026-01-01T00:00:00Z")
    r = client.get("/version")
    body = r.json()
    assert body["commit"] == "deadbeef"
    assert body["built_at"] == "2026-01-01T00:00:00Z"


def test_agents_run_reaches_fixpoint():
    payload = {
        "agents": [{"id": "a", "config": ["a"]}, {"id": "b", "config": []}],
        "rules": [
            {"premises": ["a"], "conclusions": ["b"]},
            {"premises": ["b"], "conclusions": ["c"]},
        ],
    }
    r = client.post("/agents/run", json=payload)
    assert r.status_code == 200
    agents = {a["id"]: a["config"] for a in r.json()["agents"]}
    assert agents["a"] == ["a", "b", "c"]
    assert agents["b"] == []


def test_agents_run_max_steps_too_low_returns_422():
    payload = {
        "agents": [{"id": "a", "config": ["a"]}],
        "rules": [
            {"premises": ["a"], "conclusions": ["b"]},
            {"premises": ["b"], "conclusions": ["c"]},
        ],
        "max_steps": 1,
    }
    r = client.post("/agents/run", json=payload)
    assert r.status_code == 422
    assert "no closure" in r.json()["detail"]


def test_symmetry_without_alphabet_returns_null_count_vector():
    r = client.post("/symmetry/canonical", json={"items": ["b", "a", "a"]})
    assert r.status_code == 200
    body = r.json()
    assert body["canonical"] == ["a", "a", "b"]
    assert body["count_vector"] is None
    assert body["orbit_key"] == [["a", 2], ["b", 1]]


def test_closure_endpoint_max_steps_exhausted():
    payload = {
        "config": ["a"],
        "rules": [
            {"premises": ["a"], "conclusions": ["b"]},
            {"premises": ["b"], "conclusions": ["c"]},
        ],
        "max_steps": 1,
    }
    r = client.post("/closure", json=payload)
    assert r.status_code == 422


def test_cors_middleware_when_origins_set(monkeypatch):
    """Reload the module with TMIG_CORS_ORIGINS set to hit the branch."""
    import importlib

    monkeypatch.setenv("TMIG_CORS_ORIGINS", "https://example.com, https://other.test")
    import tmig_closure.api as api_mod

    importlib.reload(api_mod)
    try:
        with TestClient(api_mod.app) as c:
            r = c.options(
                "/closure",
                headers={
                    "Origin": "https://example.com",
                    "Access-Control-Request-Method": "POST",
                },
            )
            assert r.status_code in (200, 204)
            assert r.headers.get("access-control-allow-origin") == "https://example.com"
    finally:
        monkeypatch.delenv("TMIG_CORS_ORIGINS", raising=False)
        importlib.reload(api_mod)


# ── core.py ──────────────────────────────────────────────────────


def test_closure_steps_raises_on_exhaustion():
    rules = [rule("a", "b"), rule("b", "c")]
    with pytest.raises(ClosureError):
        list(closure_steps(frozenset({"a"}), rules, max_steps=1))


def test_closure_steps_invalid_max_steps():
    with pytest.raises(ValueError, match="max_steps"):
        list(closure_steps(frozenset(), [], max_steps=0))


def test_close_negative_max_steps_rejected():
    with pytest.raises(ValueError, match="max_steps"):
        close(frozenset(), [], max_steps=-1)


# ── logging_config.py ────────────────────────────────────────────


def test_json_formatter_includes_exception():
    fmt = JsonFormatter()
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        record = logging.LogRecord(
            "t",
            logging.ERROR,
            __file__,
            1,
            "msg",
            (),
            sys.exc_info(),
        )
    payload = json.loads(fmt.format(record))
    assert payload["level"] == "ERROR"
    assert "exc" in payload
    assert "RuntimeError" in payload["exc"]


def test_configure_non_json_output(monkeypatch, capsys):
    monkeypatch.setenv("TMIG_LOG_JSON", "false")
    monkeypatch.setenv("TMIG_LOG_LEVEL", "DEBUG")
    root = logging.getLogger()
    # clear the _tmig_configured marker so configure re-runs
    if hasattr(root, "_tmig_configured"):
        delattr(root, "_tmig_configured")
    configure()
    logging.getLogger("t").warning("hello")
    captured = capsys.readouterr()
    assert "hello" in captured.err


def test_configure_is_idempotent(monkeypatch):
    monkeypatch.setenv("TMIG_LOG_JSON", "true")
    root = logging.getLogger()
    if hasattr(root, "_tmig_configured"):
        delattr(root, "_tmig_configured")
    configure()
    n1 = len(root.handlers)
    configure()  # second call must be a no-op
    n2 = len(root.handlers)
    assert n1 == n2
