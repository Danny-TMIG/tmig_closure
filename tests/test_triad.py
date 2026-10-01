# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Tests for the conformance x coherence x coordination triad."""
from __future__ import annotations

import pytest

from tmig_closure import rule
from tmig_closure.triad import (
    ALL_STATES,
    CONFLICT,
    FAIL,
    PASS,
    UNKNOWN,
    Triad,
    VState,
    coherence,
    conformance,
    consensus_v,
    coordination,
    join_know,
    join_truth,
    meet_know,
    meet_truth,
    quorum_v,
    verify,
)

# ── VState ─────────────────────────────────────────────────────

def test_vstate_names():
    assert UNKNOWN.name == "UNKNOWN"
    assert PASS.name == "PASS"
    assert FAIL.name == "FAIL"
    assert CONFLICT.name == "CONFLICT"


def test_vstate_rejects_bad_t():
    with pytest.raises(ValueError, match="coordinates"):
        VState(2, 0)


def test_vstate_rejects_bad_f():
    with pytest.raises(ValueError, match="coordinates"):
        VState(0, -1)


def test_vstate_to_dict():
    assert PASS.to_dict() == {"t": 1, "f": 0, "name": "PASS"}


def test_vstate_repr():
    assert repr(FAIL) == "FAIL"


def test_all_states_complete():
    assert set(ALL_STATES) == {UNKNOWN, PASS, FAIL, CONFLICT}


# ── lattice ops ────────────────────────────────────────────────

def test_meet_truth_table():
    assert meet_truth(PASS, PASS) == PASS
    assert meet_truth(PASS, FAIL) == FAIL
    assert meet_truth(UNKNOWN, PASS) == UNKNOWN
    assert meet_truth(CONFLICT, PASS) == CONFLICT


def test_join_truth_table():
    assert join_truth(FAIL, FAIL) == FAIL
    assert join_truth(PASS, FAIL) == PASS
    assert join_truth(UNKNOWN, PASS) == PASS
    assert join_truth(CONFLICT, FAIL) == CONFLICT


def test_join_know_table():
    assert join_know(UNKNOWN, PASS) == PASS
    assert join_know(FAIL, PASS) == CONFLICT
    assert join_know(UNKNOWN, FAIL) == FAIL
    assert join_know(CONFLICT, UNKNOWN) == CONFLICT


def test_meet_know_table():
    assert meet_know(UNKNOWN, PASS) == UNKNOWN
    assert meet_know(CONFLICT, PASS) == PASS
    assert meet_know(FAIL, CONFLICT) == FAIL
    assert meet_know(CONFLICT, UNKNOWN) == UNKNOWN


# ── quorum_v ───────────────────────────────────────────────────

def test_quorum_empty():
    assert quorum_v([]) == CONFLICT


def test_quorum_majority_pass():
    assert quorum_v([PASS, PASS, FAIL]) == PASS


def test_quorum_majority_fail():
    assert quorum_v([FAIL, FAIL, PASS]) == FAIL


def test_quorum_tie():
    assert quorum_v([PASS, FAIL]) == CONFLICT


# ── consensus_v ────────────────────────────────────────────────

def test_consensus_empty():
    assert consensus_v([]) == UNKNOWN


def test_consensus_unanimous():
    assert consensus_v([PASS, PASS, PASS]) == PASS


def test_consensus_mixed():
    assert consensus_v([PASS, FAIL]) == CONFLICT


# ── conformance ────────────────────────────────────────────────

def test_conformance_same_closure():
    rules = [rule("a", "b")]
    assert conformance(frozenset({"a"}), frozenset({"a"}), rules) == PASS


def test_conformance_different_closure():
    rules = [rule("a", "b")]
    assert conformance(frozenset({"a"}), frozenset({"z"}), rules) == FAIL


def test_conformance_closure_error():
    rules = [rule("a", "b"), rule("b", "c")]
    assert conformance(frozenset({"a"}), frozenset({"a"}), rules, max_steps=1) == UNKNOWN


# ── coherence ──────────────────────────────────────────────────

def test_coherence_same_multiset():
    assert coherence(frozenset({"a", "b"}), frozenset({"b", "a"})) == PASS


def test_coherence_different_multiset_no_alphabet():
    assert coherence(frozenset({"a"}), frozenset({"b"})) == FAIL


def test_coherence_alphabet_match():
    # Orbit keys differ (y vs z), but projected onto ["x"] both are {x}
    a = frozenset({"x", "y"})
    b = frozenset({"x", "z"})
    assert coherence(a, b, alphabet=["x"]) == PASS


def test_coherence_alphabet_mismatch():
    a = frozenset({"x"})
    b = frozenset({"y"})
    assert coherence(a, b, alphabet=["x", "y"]) == FAIL


# ── coordination ───────────────────────────────────────────────

def test_coordination_quorum():
    assert coordination([PASS, PASS, FAIL], mode="quorum") == PASS


def test_coordination_consensus():
    assert coordination([PASS, PASS], mode="consensus") == PASS


def test_coordination_conjunction():
    assert coordination([PASS, PASS], mode="conjunction") == PASS
    assert coordination([PASS, FAIL], mode="conjunction") == FAIL


def test_coordination_disjunction():
    assert coordination([FAIL, PASS], mode="disjunction") == PASS
    assert coordination([FAIL, FAIL], mode="disjunction") == FAIL


def test_coordination_merge():
    assert coordination([PASS, FAIL], mode="merge") == CONFLICT
    assert coordination([UNKNOWN, PASS], mode="merge") == PASS


def test_coordination_conjunction_empty():
    assert coordination([], mode="conjunction") == PASS


def test_coordination_unknown_mode():
    with pytest.raises(ValueError, match="unknown coordination mode"):
        coordination([PASS], mode="not-a-mode")


# ── Triad ──────────────────────────────────────────────────────

def test_triad_to_dict():
    t = Triad(PASS, FAIL, UNKNOWN)
    d = t.to_dict()
    assert d["conformance"]["name"] == "PASS"
    assert d["coherence"]["name"] == "FAIL"
    assert d["coordination"]["name"] == "UNKNOWN"


def test_triad_verdict_pass():
    assert Triad(PASS, PASS, PASS).verdict() == "PASS"


def test_triad_verdict_fail():
    assert Triad(PASS, FAIL, PASS).verdict() == "FAIL"
    assert Triad(FAIL, CONFLICT, UNKNOWN).verdict() == "FAIL"


def test_triad_verdict_conflict():
    assert Triad(PASS, CONFLICT, PASS).verdict() == "CONFLICT"


def test_triad_verdict_unknown():
    assert Triad(PASS, UNKNOWN, PASS).verdict() == "UNKNOWN"


def test_triad_conjunction():
    t = Triad(PASS, PASS, PASS).conjunction(Triad(PASS, FAIL, PASS))
    assert t.coherence == FAIL


def test_triad_disjunction():
    t = Triad(FAIL, FAIL, FAIL).disjunction(Triad(PASS, PASS, PASS))
    assert t.verdict() == "PASS"


def test_triad_merge():
    t = Triad(PASS, UNKNOWN, UNKNOWN).merge(Triad(FAIL, PASS, PASS))
    assert t.conformance == CONFLICT
    assert t.coherence == PASS
    assert t.coordination == PASS


# ── verify ─────────────────────────────────────────────────────

def test_verify_pass():
    t = verify(frozenset({"a"}), frozenset({"a"}), [rule("a", "b")])
    assert t.verdict() == "PASS"


def test_verify_closure_error():
    rules = [rule("a", "b"), rule("b", "c")]
    t = verify(frozenset({"a"}), frozenset({"a"}), rules, max_steps=1)
    assert t.verdict() == "UNKNOWN"
    assert t.coordination == UNKNOWN


def test_verify_disagreement_produces_fail_or_conflict():
    t = verify(frozenset(), frozenset({"a"}), [rule("a", "b")])
    assert t.verdict() in ("FAIL", "CONFLICT")
