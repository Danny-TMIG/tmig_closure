# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Map a Run's status/conclusion to a four-valued verification state."""

from __future__ import annotations

from tmig_closure.mastery.run import Run
from tmig_closure.triad import CONFLICT, FAIL, PASS, UNKNOWN, VState

_IN_PROGRESS = frozenset({"queued", "in_progress", "requested", "waiting", "pending"})
_FAILURE = frozenset({"failure", "cancelled", "timed_out", "action_required", "startup_failure"})
_NEUTRAL = frozenset({"skipped", "neutral", ""})


def classify(run: Run) -> VState:
    """Resolve a run to a Belnap FOUR state."""
    if run.status in _IN_PROGRESS:
        return UNKNOWN
    if run.status == "completed":
        if run.conclusion == "success":
            return PASS
        if run.conclusion in _FAILURE:
            return FAIL
        if run.conclusion in _NEUTRAL:
            return UNKNOWN
        return CONFLICT
    return CONFLICT
