r"""The kernel: a monotone closure operator over capability primitives.

    A         finite alphabet of primitive names (str)
    X subset A     a configuration (frozenset[str])
    R         a ruleset: iterable of (P, C) pairs, P,C subset A finite

    T_R(X)    immediate-consequence operator
    cl_R(X)   least fixed point of T_R above X (Knaster-Tarski)

T_R is monotone, A is finite, therefore cl_R exists and is reached in at most
|A \ X| iterations. cl_R is extensive, monotone, and idempotent — a Tarski
closure operator on the complete lattice (2^A, subset).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

Primitive = str
Config = frozenset[Primitive]
Rule = tuple[frozenset[Primitive], frozenset[Primitive]]


class ClosureError(RuntimeError):
    """Raised when a closure iteration bound is exhausted before fixpoint."""


def rule(premises: Iterable[Primitive], conclusions: Iterable[Primitive]) -> Rule:
    """Construct a rule from two iterables of primitives."""
    return (frozenset(premises), frozenset(conclusions))


def _normalise(rules: Iterable[Rule]) -> tuple[Rule, ...]:
    return tuple((frozenset(p), frozenset(c)) for p, c in rules)


def immediate_consequence(config: Config, rules: Iterable[Rule]) -> Config:
    """Apply T_R once: add every conclusion whose premises are already present."""
    out: set[Primitive] = set(config)
    for premises, conclusions in rules:
        if premises <= config:
            out |= conclusions
    return frozenset(out)


def close(
    config: Config,
    rules: Iterable[Rule],
    *,
    max_steps: int = 10_000,
) -> Config:
    """Compute the least fixed point of T_R above ``config``."""
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")
    rs = _normalise(rules)
    current: Config = frozenset(config)
    for _ in range(max_steps):
        nxt = immediate_consequence(current, rs)
        if nxt == current:
            return current
        current = nxt
    raise ClosureError(f"no closure within {max_steps} steps")


def closure_steps(
    config: Config,
    rules: Iterable[Rule],
    *,
    max_steps: int = 10_000,
) -> Iterator[Config]:
    """Yield each configuration in the Kleene chain X_0, X_1, ... up to fixpoint."""
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")
    rs = _normalise(rules)
    current: Config = frozenset(config)
    for _ in range(max_steps):
        yield current
        nxt = immediate_consequence(current, rs)
        if nxt == current:
            return
        current = nxt
    raise ClosureError(f"no closure within {max_steps} steps")
