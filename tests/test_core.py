# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group

"""Kernel unit tests."""

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
    with pytest.raises(ValueError, match="max_steps"):
        close(frozenset(), [], max_steps=0)
