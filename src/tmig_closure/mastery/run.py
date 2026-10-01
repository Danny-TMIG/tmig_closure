# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""The Run value object -- the 16 fields of a GitHub Actions run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_ALIASES: dict[str, str] = {
    "attempt": "attempt",
    "conclusion": "conclusion",
    "createdAt": "created_at",
    "databaseId": "database_id",
    "displayTitle": "display_title",
    "event": "event",
    "headBranch": "head_branch",
    "headSha": "head_sha",
    "name": "name",
    "number": "number",
    "startedAt": "started_at",
    "status": "status",
    "updatedAt": "updated_at",
    "url": "url",
    "workflowDatabaseId": "workflow_database_id",
    "workflowName": "workflow_name",
}

_INT_FIELDS = frozenset({"attempt", "database_id", "number", "workflow_database_id"})


@dataclass(frozen=True, slots=True)
class Run:
    """A single GitHub Actions workflow run."""

    attempt: int
    conclusion: str
    created_at: str
    database_id: int
    display_title: str
    event: str
    head_branch: str
    head_sha: str
    name: str
    number: int
    started_at: str
    status: str
    updated_at: str
    url: str
    workflow_database_id: int
    workflow_name: str

    @classmethod
    def from_gh(cls, raw: dict[str, Any]) -> Run:
        """Build a Run from the JSON object returned by gh."""
        kwargs: dict[str, Any] = {}
        for src, dst in _ALIASES.items():
            v = raw.get(src)
            if v is None:
                kwargs[dst] = 0 if dst in _INT_FIELDS else ""
            else:
                kwargs[dst] = v
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Return the 16 fields under their GitHub names."""
        return {k: getattr(self, v) for k, v in _ALIASES.items()}
