# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""The mastery controller: observe, classify, decide, act, record."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from tmig_closure.mastery.classifier import classify
from tmig_closure.mastery.ledger import Ledger, Record
from tmig_closure.mastery.run import Run
from tmig_closure.triad import FAIL, PASS, UNKNOWN, VState

_GH_FIELDS = (
    "attempt,conclusion,createdAt,databaseId,displayTitle,event,"
    "headBranch,headSha,name,number,startedAt,status,updatedAt,url,"
    "workflowDatabaseId,workflowName"
)


class Action(StrEnum):
    """The three things mastery can do to a run."""

    RETRY = "retry"
    ESCALATE = "escalate"
    IGNORE = "ignore"


@dataclass(frozen=True, slots=True)
class Decision:
    """A per-run plan."""

    run: Run
    state: VState
    action: Action
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable view."""
        return {
            "run_id": self.run.database_id,
            "workflow": self.run.workflow_name,
            "state": self.state.name,
            "action": self.action.value,
            "note": self.note,
        }


class Mastery:
    """Autonomous loop over workflow runs."""

    def __init__(
        self, *, repo: str, ledger: Ledger, max_attempts: int = 3, limit: int = 50
    ) -> None:
        """Bind to a repo, ledger, and retry budget."""
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if limit < 1:
            raise ValueError("limit must be >= 1")
        self.repo = repo
        self.ledger = ledger
        self.max_attempts = max_attempts
        self.limit = limit

    def observe(self) -> list[Run]:
        """Fetch recent runs via gh run list --json."""
        cmd = [
            "gh",
            "run",
            "list",
            "--repo",
            self.repo,
            "--limit",
            str(self.limit),
            "--json",
            _GH_FIELDS,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"gh run list failed ({proc.returncode}): {proc.stderr.strip()}")
        return [Run.from_gh(row) for row in json.loads(proc.stdout)]

    def _prior_retries(self, run_id: int) -> int:
        return sum(1 for r in self.ledger if r.run_id == run_id and r.action == Action.RETRY.value)

    def decide(self, run: Run) -> Decision:
        """Choose the action for one run, using the ledger as memory."""
        state = classify(run)
        if state is PASS:
            return Decision(run, state, Action.IGNORE, "success")
        if state is UNKNOWN:
            return Decision(run, state, Action.IGNORE, "not finished")
        if state is FAIL:
            prior = self._prior_retries(run.database_id)
            if run.attempt >= self.max_attempts or prior >= self.max_attempts:
                return Decision(
                    run, state, Action.ESCALATE, f"attempt {run.attempt}, retries {prior}"
                )
            return Decision(run, state, Action.RETRY, f"attempt {run.attempt}, retries {prior}")
        return Decision(run, state, Action.ESCALATE, "conflicting fields")

    def plan(self, runs: list[Run]) -> list[Decision]:
        """Decide for every run."""
        return [self.decide(r) for r in runs]

    def act(self, decision: Decision) -> bool:
        """Execute one decision. True iff GitHub state changed."""
        if decision.action is Action.RETRY:
            return self._retry(decision.run)
        return False

    def _retry(self, run: Run) -> bool:
        cmd = ["gh", "run", "rerun", str(run.database_id), "--repo", self.repo]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return proc.returncode == 0

    def record(self, decision: Decision) -> Record:
        """Persist a decision and return the written record."""
        rec = Record(
            at=Ledger.now(),
            run_id=decision.run.database_id,
            workflow=decision.run.workflow_name,
            state=decision.state.name,
            action=decision.action.value,
            note=decision.note,
        )
        self.ledger.append(rec)
        return rec

    def cycle(self) -> list[Decision]:
        """Observe, decide, act, record -- one autonomy tick."""
        decisions = self.plan(self.observe())
        for d in decisions:
            self.act(d)
            self.record(d)
        return decisions

    def stats(self) -> dict[str, int]:
        """Count ledger entries by state and action."""
        out = {
            "UNKNOWN": 0,
            "PASS": 0,
            "FAIL": 0,
            "CONFLICT": 0,
            "retry": 0,
            "escalate": 0,
            "ignore": 0,
            "total": 0,
        }
        for r in self.ledger:
            out[r.state] = out.get(r.state, 0) + 1
            out[r.action] = out.get(r.action, 0) + 1
            out["total"] += 1
        return out
