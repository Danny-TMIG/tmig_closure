# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Multi-agent composition over the closure kernel.

An :class:`Agent` is a named configuration. :func:`step` applies ``T_R``
once to each agent synchronously. :func:`run_to_fixpoint` brings every
agent to its own closure. :func:`quorum` and :func:`consensus` are the
two standard coordination predicates.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace

from tmig_closure.core import Config, Rule, close, immediate_consequence

Predicate = Callable[[Config], bool]
"""A test applied to a single agent's configuration."""


@dataclass(frozen=True, slots=True)
class Agent:
    """A named configuration."""

    id: str
    config: Config

    def with_config(self, config: Config) -> Agent:
        """Return a copy of this agent with a new configuration."""
        return replace(self, config=config)


def step(agents: Sequence[Agent], rules: Iterable[Rule]) -> list[Agent]:
    """Apply ``T_R`` once to every agent, synchronously."""
    rs = tuple(rules)
    return [Agent(a.id, immediate_consequence(a.config, rs)) for a in agents]


def run_to_fixpoint(
    agents: Sequence[Agent],
    rules: Iterable[Rule],
    *,
    max_steps: int = 10_000,
) -> list[Agent]:
    """Bring every agent to fixpoint."""
    rs = tuple(rules)
    return [Agent(a.id, close(a.config, rs, max_steps=max_steps)) for a in agents]


def product(agents: Sequence[Agent]) -> Config:
    """The union of every agent's configuration."""
    out: set[str] = set()
    for a in agents:
        out |= a.config
    return frozenset(out)


def quorum(agents: Sequence[Agent], pred: Predicate) -> bool:
    """True iff a strict majority of agents satisfies ``pred``.

    An empty ensemble returns False.
    """
    n = len(agents)
    if n == 0:
        return False
    return sum(1 for a in agents if pred(a.config)) > n // 2


def consensus(agents: Sequence[Agent], pred: Predicate) -> bool:
    """True iff every agent satisfies ``pred``.

    An empty ensemble returns True vacuously.
    """
    return all(pred(a.config) for a in agents)
