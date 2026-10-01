# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Tests for the autonomous mastery controller."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from tmig_closure.mastery import (
    Action,
    Ledger,
    Mastery,
    Record,
    Run,
    classify,
)
from tmig_closure.mastery.__main__ import main
from tmig_closure.triad import CONFLICT, FAIL, PASS, UNKNOWN

RAW_SUCCESS: dict = {
    "attempt": 1,
    "conclusion": "success",
    "createdAt": "2026-10-01T00:00:00Z",
    "databaseId": 1001,
    "displayTitle": "feat: x",
    "event": "push",
    "headBranch": "main",
    "headSha": "abc123",
    "name": "ci",
    "number": 42,
    "startedAt": "2026-10-01T00:00:01Z",
    "status": "completed",
    "updatedAt": "2026-10-01T00:01:00Z",
    "url": "https://example/1001",
    "workflowDatabaseId": 900,
    "workflowName": "ci",
}

RAW_FAILURE = {**RAW_SUCCESS, "databaseId": 1002, "conclusion": "failure"}
RAW_RUNNING = {**RAW_SUCCESS, "databaseId": 1003, "conclusion": "", "status": "in_progress"}
RAW_CONFLICT = {**RAW_SUCCESS, "databaseId": 1004, "conclusion": "other"}


def run(raw: dict) -> Run:
    """Shorthand: build a Run from a raw JSON dict."""
    return Run.from_gh(raw)


def ok_proc(stdout: str = "[]") -> subprocess.CompletedProcess[str]:
    """A CompletedProcess that looks like a successful gh call."""
    return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=stdout, stderr="")


def err_proc(msg: str = "boom") -> subprocess.CompletedProcess[str]:
    """A CompletedProcess that looks like a failed gh call."""
    return subprocess.CompletedProcess(args=["gh"], returncode=1, stdout="", stderr=msg)


# ── Run ────────────────────────────────────────────────────────


def test_run_from_gh_all_fields() -> None:
    r = run(RAW_SUCCESS)
    assert r.attempt == 1
    assert r.conclusion == "success"
    assert r.created_at == "2026-10-01T00:00:00Z"
    assert r.database_id == 1001
    assert r.display_title == "feat: x"
    assert r.event == "push"
    assert r.head_branch == "main"
    assert r.head_sha == "abc123"
    assert r.name == "ci"
    assert r.number == 42
    assert r.started_at == "2026-10-01T00:00:01Z"
    assert r.status == "completed"
    assert r.updated_at == "2026-10-01T00:01:00Z"
    assert r.url == "https://example/1001"
    assert r.workflow_database_id == 900
    assert r.workflow_name == "ci"


def test_run_from_gh_defaults_when_missing() -> None:
    r = Run.from_gh({})
    assert r.attempt == 0
    assert r.database_id == 0
    assert r.conclusion == ""


def test_run_to_dict_roundtrip() -> None:
    assert run(RAW_SUCCESS).to_dict() == RAW_SUCCESS


# ── classify ───────────────────────────────────────────────────


def test_classify_success() -> None:
    assert classify(run(RAW_SUCCESS)) is PASS


def test_classify_failure() -> None:
    assert classify(run(RAW_FAILURE)) is FAIL


def test_classify_running() -> None:
    assert classify(run(RAW_RUNNING)) is UNKNOWN


def test_classify_neutral_conclusion() -> None:
    assert classify(run({**RAW_SUCCESS, "conclusion": "skipped"})) is UNKNOWN


def test_classify_unknown_conclusion() -> None:
    assert classify(run(RAW_CONFLICT)) is CONFLICT


def test_classify_unknown_status() -> None:
    assert classify(run({**RAW_SUCCESS, "status": "something_new"})) is CONFLICT


@pytest.mark.parametrize(
    "conclusion",
    [
        "failure",
        "cancelled",
        "timed_out",
        "action_required",
        "startup_failure",
    ],
)
def test_classify_every_failure_conclusion(conclusion: str) -> None:
    assert classify(run({**RAW_SUCCESS, "conclusion": conclusion})) is FAIL


@pytest.mark.parametrize(
    "status",
    [
        "queued",
        "in_progress",
        "requested",
        "waiting",
        "pending",
    ],
)
def test_classify_every_in_progress_status(status: str) -> None:
    assert classify(run({**RAW_SUCCESS, "status": status})) is UNKNOWN


# ── Ledger ─────────────────────────────────────────────────────


def test_ledger_append_and_read(tmp_path: Path) -> None:
    led = Ledger(tmp_path / "sub" / "led.jsonl")
    rec = Record(at=1.0, run_id=1, workflow="ci", state="PASS", action="ignore", note="ok")
    led.append(rec)
    assert len(led) == 1
    assert led.read()[0] == rec


def test_ledger_read_missing_file(tmp_path: Path) -> None:
    assert Ledger(tmp_path / "nope.jsonl").read() == []


def test_ledger_skips_blank_lines(tmp_path: Path) -> None:
    p = tmp_path / "l.jsonl"
    p.write_text("\n\n")
    assert Ledger(p).read() == []


def test_ledger_skips_malformed(tmp_path: Path) -> None:
    p = tmp_path / "l.jsonl"
    p.write_text(
        'not-json\n{"at":1.0,"run_id":1,"workflow":"x","state":"PASS","action":"ignore"}\n'
    )
    assert len(Ledger(p).read()) == 1


def test_ledger_iter(tmp_path: Path) -> None:
    led = Ledger(tmp_path / "l.jsonl")
    led.append(Record(1.0, 1, "ci", "PASS", "ignore", ""))
    led.append(Record(2.0, 2, "ci", "FAIL", "retry", ""))
    assert [r.run_id for r in led] == [1, 2]


def test_ledger_now_monotonic() -> None:
    assert Ledger.now() <= Ledger.now()


# ── Mastery ────────────────────────────────────────────────────


def _mastery(tmp_path: Path, **kw) -> Mastery:
    return Mastery(repo="o/r", ledger=Ledger(tmp_path / "l.jsonl"), **kw)


def test_mastery_rejects_bad_max_attempts(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="max_attempts"):
        _mastery(tmp_path, max_attempts=0)


def test_mastery_rejects_bad_limit(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="limit"):
        _mastery(tmp_path, limit=0)


def test_observe_parses_output(tmp_path: Path) -> None:
    payload = json.dumps([RAW_SUCCESS, RAW_FAILURE])
    with mock.patch("tmig_closure.mastery.mastery.subprocess.run", return_value=ok_proc(payload)):
        runs = _mastery(tmp_path).observe()
    assert [r.database_id for r in runs] == [1001, 1002]


def test_observe_raises_on_failure(tmp_path: Path) -> None:
    with (
        mock.patch(
            "tmig_closure.mastery.mastery.subprocess.run", return_value=err_proc("bad token")
        ),
        pytest.raises(RuntimeError, match="bad token"),
    ):
        _mastery(tmp_path).observe()


def test_decide_pass_is_ignore(tmp_path: Path) -> None:
    d = _mastery(tmp_path).decide(run(RAW_SUCCESS))
    assert d.state is PASS
    assert d.action is Action.IGNORE


def test_decide_unknown_is_ignore(tmp_path: Path) -> None:
    d = _mastery(tmp_path).decide(run(RAW_RUNNING))
    assert d.state is UNKNOWN
    assert d.action is Action.IGNORE


def test_decide_fail_retries(tmp_path: Path) -> None:
    d = _mastery(tmp_path).decide(run(RAW_FAILURE))
    assert d.state is FAIL
    assert d.action is Action.RETRY


def test_decide_fail_escalates_at_attempt_budget(tmp_path: Path) -> None:
    m = _mastery(tmp_path, max_attempts=1)
    d = m.decide(run({**RAW_FAILURE, "attempt": 1}))
    assert d.action is Action.ESCALATE


def test_decide_fail_escalates_after_prior_retries(tmp_path: Path) -> None:
    m = _mastery(tmp_path, max_attempts=1)
    m.ledger.append(Record(1.0, 1002, "ci", "FAIL", "retry", ""))
    assert m.decide(run(RAW_FAILURE)).action is Action.ESCALATE


def test_decide_conflict_escalates(tmp_path: Path) -> None:
    d = _mastery(tmp_path).decide(run(RAW_CONFLICT))
    assert d.state is CONFLICT
    assert d.action is Action.ESCALATE


def test_plan_returns_one_decision_per_run(tmp_path: Path) -> None:
    m = _mastery(tmp_path)
    assert len(m.plan([run(RAW_SUCCESS), run(RAW_FAILURE), run(RAW_RUNNING)])) == 3


def test_decision_to_dict(tmp_path: Path) -> None:
    d = _mastery(tmp_path).decide(run(RAW_FAILURE))
    assert d.to_dict()["action"] == "retry"
    assert d.to_dict()["run_id"] == 1002


def test_act_ignore_returns_false(tmp_path: Path) -> None:
    m = _mastery(tmp_path)
    assert m.act(m.decide(run(RAW_SUCCESS))) is False


def test_act_escalate_returns_false(tmp_path: Path) -> None:
    m = _mastery(tmp_path, max_attempts=1)
    assert m.act(m.decide(run({**RAW_FAILURE, "attempt": 1}))) is False


def test_act_retry_calls_gh_rerun(tmp_path: Path) -> None:
    m = _mastery(tmp_path)
    d = m.decide(run(RAW_FAILURE))
    with mock.patch(
        "tmig_closure.mastery.mastery.subprocess.run", return_value=ok_proc("")
    ) as mocked:
        assert m.act(d) is True
    cmd = mocked.call_args[0][0]
    assert cmd[:3] == ["gh", "run", "rerun"]
    assert "1002" in cmd


def test_act_retry_reports_failure(tmp_path: Path) -> None:
    m = _mastery(tmp_path)
    d = m.decide(run(RAW_FAILURE))
    with mock.patch("tmig_closure.mastery.mastery.subprocess.run", return_value=err_proc("nope")):
        assert m.act(d) is False


def test_record_appends(tmp_path: Path) -> None:
    m = _mastery(tmp_path)
    rec = m.record(m.decide(run(RAW_FAILURE)))
    assert rec.state == "FAIL"
    assert rec.action == "retry"
    assert len(m.ledger) == 1


def test_cycle_end_to_end(tmp_path: Path) -> None:
    m = _mastery(tmp_path)
    payload = json.dumps([RAW_SUCCESS, RAW_FAILURE, RAW_RUNNING])
    with mock.patch(
        "tmig_closure.mastery.mastery.subprocess.run", side_effect=[ok_proc(payload), ok_proc("")]
    ):
        decisions = m.cycle()
    assert len(decisions) == 3
    assert len(m.ledger) == 3


def test_stats_empty(tmp_path: Path) -> None:
    s = _mastery(tmp_path).stats()
    assert s["total"] == 0
    assert s["PASS"] == 0
    assert s["retry"] == 0


def test_stats_after_records(tmp_path: Path) -> None:
    m = _mastery(tmp_path)
    m.ledger.append(Record(1.0, 1, "ci", "FAIL", "retry", ""))
    m.ledger.append(Record(2.0, 2, "ci", "FAIL", "escalate", ""))
    m.ledger.append(Record(3.0, 3, "ci", "PASS", "ignore", ""))
    s = m.stats()
    assert s["FAIL"] == 2
    assert s["PASS"] == 1
    assert s["retry"] == 1
    assert s["escalate"] == 1
    assert s["ignore"] == 1
    assert s["total"] == 3


# ── CLI ────────────────────────────────────────────────────────


def _cli(tmp_path: Path, argv: list[str]) -> int:
    return main(["--repo", "o/r", "--ledger", str(tmp_path / "l.jsonl"), *argv])


def test_cli_status(tmp_path: Path, capsys) -> None:
    assert _cli(tmp_path, ["status"]) == 0
    assert json.loads(capsys.readouterr().out)["total"] == 0


def test_cli_observe(tmp_path: Path, capsys) -> None:
    payload = json.dumps([RAW_SUCCESS])
    with mock.patch("tmig_closure.mastery.mastery.subprocess.run", return_value=ok_proc(payload)):
        assert _cli(tmp_path, ["observe"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["databaseId"] == 1001


def test_cli_observe_error(tmp_path: Path, capsys) -> None:
    with mock.patch("tmig_closure.mastery.mastery.subprocess.run", return_value=err_proc("bad")):
        assert _cli(tmp_path, ["observe"]) == 2
    assert "bad" in capsys.readouterr().err


def test_cli_plan(tmp_path: Path, capsys) -> None:
    with mock.patch(
        "tmig_closure.mastery.mastery.subprocess.run",
        return_value=ok_proc(json.dumps([RAW_FAILURE])),
    ):
        assert _cli(tmp_path, ["plan"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["action"] == "retry"


def test_cli_plan_error(tmp_path: Path, capsys) -> None:
    with mock.patch("tmig_closure.mastery.mastery.subprocess.run", return_value=err_proc("no")):
        assert _cli(tmp_path, ["plan"]) == 2
    capsys.readouterr()


def test_cli_cycle(tmp_path: Path, capsys) -> None:
    with mock.patch(
        "tmig_closure.mastery.mastery.subprocess.run",
        side_effect=[ok_proc(json.dumps([RAW_FAILURE])), ok_proc("")],
    ):
        assert _cli(tmp_path, ["cycle"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == 1


def test_cli_cycle_error(tmp_path: Path, capsys) -> None:
    with mock.patch("tmig_closure.mastery.mastery.subprocess.run", return_value=err_proc("bad")):
        assert _cli(tmp_path, ["cycle"]) == 2
    capsys.readouterr()


def test_cli_loop(tmp_path: Path, capsys) -> None:
    with mock.patch("tmig_closure.mastery.mastery.subprocess.run", return_value=ok_proc("[]")):
        assert _cli(tmp_path, ["loop", "--cycles", "2", "--delay", "0"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 2


def test_cli_loop_error(tmp_path: Path, capsys) -> None:
    with mock.patch("tmig_closure.mastery.mastery.subprocess.run", return_value=err_proc("bad")):
        assert _cli(tmp_path, ["loop", "--cycles", "1"]) == 2
    capsys.readouterr()


def test_mastery_dunder_main_subprocess() -> None:
    """Cover the `if __name__ == '__main__'` guard via subprocess."""
    r = subprocess.run(
        [sys.executable, "-m", "tmig_closure.mastery", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert "repo" in r.stdout


def test_cli_unknown_cmd_reaches_trailing_return(monkeypatch, tmp_path: Path) -> None:
    """Reach the defensive trailing `return 0` at end of main().

    argparse normally prevents unknown commands via ``required=True``,
    but the fall-through is there for defensive completeness and must
    stay covered.
    """
    import argparse

    from tmig_closure.mastery import __main__ as mastery_main

    class FakeArgs:
        cmd = "not-a-real-command"
        repo = "o/r"
        ledger = str(tmp_path / "unused.jsonl")
        max_attempts = 3
        limit = 50

    monkeypatch.setattr(
        argparse.ArgumentParser,
        "parse_args",
        lambda self, *a, **kw: FakeArgs(),
    )
    assert mastery_main.main([]) == 0
