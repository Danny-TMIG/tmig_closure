# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group

"""End-to-end: HTTP surface + CLI."""

from fastapi.testclient import TestClient

from tmig_closure.__main__ import main
from tmig_closure.api import app

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
    payload = {
        "config": ["a"],
        "rules": [
            {"premises": ["a"], "conclusions": ["b"]},
            {"premises": ["b"], "conclusions": ["c"]},
        ],
    }
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
    payload = {
        "agents": [{"id": "x", "config": ["a"]}],
        "rules": [{"premises": ["a"], "conclusions": ["b"]}],
    }
    r = client.post("/agents/step", json=payload)
    assert r.status_code == 200
    assert r.json()["agents"][0]["config"] == ["a", "b"]


def test_symmetry_endpoint():
    r = client.post(
        "/symmetry/canonical", json={"items": ["c", "a", "b", "a"], "alphabet": ["a", "b", "c"]}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["canonical"] == ["a", "a", "b", "c"]
    assert body["count_vector"] == [2, 1, 1]


def test_cli_close(capsys):
    rc = main(["close", "--config", "a", "--rule", "a>b", "--rule", "b>c"])
    assert rc == 0
    out = capsys.readouterr().out
    assert '"a"' in out
    assert '"b"' in out
    assert '"c"' in out


def test_cli_bad_rule(capsys):
    rc = main(["close", "--config", "a", "--rule", "not-a-rule"])
    assert rc == 2
