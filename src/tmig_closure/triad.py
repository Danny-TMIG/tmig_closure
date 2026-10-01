# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Conformance x Coherence x Coordination -- the verification triad.

Three orthogonal questions over a configuration space:

    Conformance   does the artifact match its declaration?
    Coherence     do two artifacts agree under primitive renaming?
    Coordination  do many agents agree on a fixpoint?

Each axis resolves to a state in Belnap's FOUR lattice:

    UNKNOWN  (0, 0)  neither proven
    PASS     (1, 0)  proven true
    FAIL     (0, 1)  proven false
    CONFLICT (1, 1)  both proven

The triad is the product of three states. Composition is pointwise,
so the triad algebra inherits commutativity, associativity, and
idempotence from the lattice. Every axis reduces to the closure
kernel in :mod:`tmig_closure.core`.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from tmig_closure.agents import Agent, run_to_fixpoint
from tmig_closure.core import ClosureError, Config, Rule, close
from tmig_closure.symmetry import count_vector, orbit_key


@dataclass(frozen=True, slots=True)
class VState:
    """A verification state: truth (t) and falsity (f) as bits.

    Only four combinations are valid; the constructor rejects the rest.
    """

    t: int
    f: int

    def __post_init__(self) -> None:
        """Reject coordinates outside ``{0, 1}``."""
        if self.t not in (0, 1) or self.f not in (0, 1):
            raise ValueError(
                f"VState coordinates must be 0 or 1, got ({self.t}, {self.f})"
            )

    @property
    def name(self) -> str:
        """The canonical name: ``UNKNOWN``, ``PASS``, ``FAIL``, or ``CONFLICT``."""
        return {(0, 0): "UNKNOWN", (1, 0): "PASS",
                (0, 1): "FAIL", (1, 1): "CONFLICT"}[(self.t, self.f)]

    def to_dict(self) -> dict[str, int | str]:
        """Return a JSON-serializable view of this state."""
        return {"t": self.t, "f": self.f, "name": self.name}

    def __repr__(self) -> str:
        return self.name


UNKNOWN = VState(0, 0)
"""Neither a proof nor a disproof has been established."""

PASS = VState(1, 0)
"""A proof has been established."""

FAIL = VState(0, 1)
"""A disproof has been established."""

CONFLICT = VState(1, 1)
"""Both a proof and a disproof have been established."""

ALL_STATES: tuple[VState, ...] = (UNKNOWN, PASS, FAIL, CONFLICT)
"""Every valid state, for exhaustive checks."""


def meet_truth(a: VState, b: VState) -> VState:
    """Conjunction in the truth order: both must hold."""
    return VState(min(a.t, b.t), max(a.f, b.f))


def join_truth(a: VState, b: VState) -> VState:
    """Disjunction in the truth order: either may hold."""
    return VState(max(a.t, b.t), min(a.f, b.f))


def join_know(a: VState, b: VState) -> VState:
    """Union of information between two states."""
    return VState(max(a.t, b.t), max(a.f, b.f))


def meet_know(a: VState, b: VState) -> VState:
    """Common information between two states."""
    return VState(min(a.t, b.t), min(a.f, b.f))


def _fold(
    states: Iterable[VState],
    op: Callable[[VState, VState], VState],
    empty: VState,
) -> VState:
    """Reduce ``states`` left-to-right with ``op``, or return ``empty``."""
    it = iter(states)
    try:
        acc = next(it)
    except StopIteration:
        return empty
    for x in it:
        acc = op(acc, x)
    return acc


def quorum_v(states: Iterable[VState]) -> VState:
    """Strict-majority fold over a finite collection of states.

    An empty collection and a tie both resolve to ``CONFLICT``.
    """
    s = tuple(states)
    if not s:
        return CONFLICT
    n = len(s)
    p = sum(1 for x in s if x == PASS)
    f = sum(1 for x in s if x == FAIL)
    if p > n // 2:
        return PASS
    if f > n // 2:
        return FAIL
    return CONFLICT


def consensus_v(states: Iterable[VState]) -> VState:
    """Unanimous agreement, else ``CONFLICT``. Empty yields ``UNKNOWN``."""
    s = tuple(states)
    if not s:
        return UNKNOWN
    return s[0] if all(x == s[0] for x in s) else CONFLICT


def conformance(
    declared: Config,
    actual: Config,
    rules: Iterable[Rule],
    *,
    max_steps: int = 10_000,
) -> VState:
    """Does the artifact match its declaration?

    Passes iff ``close(declared)`` and ``close(actual)`` are equal.
    Returns ``UNKNOWN`` when either closure fails to converge.
    """
    try:
        d = close(declared, rules, max_steps=max_steps)
        a = close(actual, rules, max_steps=max_steps)
    except ClosureError:
        return UNKNOWN
    return PASS if d == a else FAIL


def coherence(
    a: Config,
    b: Config,
    *,
    alphabet: Iterable[str] | None = None,
) -> VState:
    """Do two artifacts agree under primitive renaming?

    Without ``alphabet``, compares the orbit key (multiset of
    primitives). With ``alphabet``, compares the count-vector over
    that alphabet, which projects both configurations onto the
    same coordinate space.
    """
    if orbit_key(a) == orbit_key(b):
        return PASS
    if alphabet is not None:
        return PASS if count_vector(a, alphabet) == count_vector(b, alphabet) else FAIL
    return FAIL


def coordination(states: Iterable[VState], *, mode: str = "quorum") -> VState:
    """Do many agents agree together?

    Folds a sequence of per-agent verdicts into one state. Modes:

        quorum       strict majority (ties -> CONFLICT)
        consensus    unanimous agreement (mixed -> CONFLICT)
        conjunction  every state must be PASS
        disjunction  at least one state is PASS
        merge        union of information
    """
    fns: dict[str, Callable[[Iterable[VState]], VState]] = {
        "quorum": quorum_v,
        "consensus": consensus_v,
        "conjunction": lambda s: _fold(s, meet_truth, PASS),
        "disjunction": lambda s: _fold(s, join_truth, FAIL),
        "merge": lambda s: _fold(s, join_know, UNKNOWN),
    }
    if mode not in fns:
        raise ValueError(f"unknown coordination mode: {mode!r}")
    return fns[mode](states)


@dataclass(frozen=True, slots=True)
class Triad:
    """The product of three verification states."""

    conformance: VState
    coherence: VState
    coordination: VState

    def to_dict(self) -> dict[str, dict[str, int | str]]:
        """Return a JSON-serializable view of the triad."""
        return {
            "conformance": self.conformance.to_dict(),
            "coherence": self.coherence.to_dict(),
            "coordination": self.coordination.to_dict(),
        }

    def verdict(self) -> str:
        """Reduce the triad to one of: ``PASS``, ``FAIL``, ``CONFLICT``, ``UNKNOWN``.

        Priority: FAIL beats CONFLICT beats UNKNOWN beats PASS.
        """
        states = (self.conformance, self.coherence, self.coordination)
        if any(s == FAIL for s in states):
            return "FAIL"
        if any(s == CONFLICT for s in states):
            return "CONFLICT"
        if any(s == UNKNOWN for s in states):
            return "UNKNOWN"
        return "PASS"

    def conjunction(self, other: Triad) -> Triad:
        """Pointwise AND under the truth order."""
        return Triad(
            meet_truth(self.conformance, other.conformance),
            meet_truth(self.coherence, other.coherence),
            meet_truth(self.coordination, other.coordination),
        )

    def disjunction(self, other: Triad) -> Triad:
        """Pointwise OR under the truth order."""
        return Triad(
            join_truth(self.conformance, other.conformance),
            join_truth(self.coherence, other.coherence),
            join_truth(self.coordination, other.coordination),
        )

    def merge(self, other: Triad) -> Triad:
        """Pointwise union of information."""
        return Triad(
            join_know(self.conformance, other.conformance),
            join_know(self.coherence, other.coherence),
            join_know(self.coordination, other.coordination),
        )


def verify(
    declared: Config,
    actual: Config,
    rules: Iterable[Rule],
    *,
    alphabet: Iterable[str] | None = None,
    max_steps: int = 10_000,
) -> Triad:
    """Three-axis verification of ``declared`` against ``actual``.

    Runs each axis once and returns the resulting triad. Coordination
    is measured by running both configurations as a two-agent ensemble
    and requiring them to agree on the fixpoint.
    """
    c = conformance(declared, actual, rules, max_steps=max_steps)
    h = coherence(declared, actual, alphabet=alphabet)

    agents = [
        Agent("declared", frozenset(declared)),
        Agent("actual", frozenset(actual)),
    ]
    try:
        final = run_to_fixpoint(agents, rules, max_steps=max_steps)
    except ClosureError:
        return Triad(c, h, UNKNOWN)
    states = [PASS if a.config == final[0].config else FAIL for a in final]
    return Triad(c, h, coordination(states))
