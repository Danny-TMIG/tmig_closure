# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group

"""Multi-agent composition tests."""

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
    agents = [
        Agent("1", frozenset({"a"})),
        Agent("2", frozenset({"a"})),
        Agent("3", frozenset({"b"})),
    ]
    assert quorum(agents, lambda c: "a" in c) is True
    assert quorum(agents, lambda c: "b" in c) is False


def test_quorum_empty_is_false():
    assert quorum([], lambda c: True) is False


def test_consensus_vacuous_truth():
    assert consensus([], lambda c: False) is True


def test_consensus_all_must_agree():
    agents = [Agent("1", frozenset({"a"})), Agent("2", frozenset({"a"}))]
    assert consensus(agents, lambda c: "a" in c) is True
    assert consensus([*agents, Agent("3", frozenset({"b"}))], lambda c: "a" in c) is False
