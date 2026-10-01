# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Engine mastery — resolve every engine, fold into a Triad."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass, field

from tmig_closure.mastery_engines.atlas import (
    ENGINES,
    Engine,
    engines_of,
    families,
)
from tmig_closure.mastery_engines.unified import (
    ros2_profile,
    ros_topic,
    uns_path,
    usd_prim,
)
from tmig_closure.triad import (
    FAIL,
    PASS,
    UNKNOWN,
    Triad,
    VState,
    join_know,
    meet_truth,
)

Resolver = Callable[[str], str | None]


def _default_resolver(cmd: str) -> str | None:
    """Look up a binary on PATH. Returns the path or None."""
    head = cmd.split()[0]
    return shutil.which(head)


def resolve_all(resolver: Resolver | None = None) -> dict[str, str | None]:
    """Resolve every engine command, returning a mapping engine.id -> path or None."""
    r = resolver or _default_resolver
    return {e.id: r(e.command) for e in ENGINES}


@dataclass(frozen=True, slots=True)
class EngineState:
    """An engine and whether its binary resolves on this host."""

    engine: Engine
    path: str | None

    @property
    def present(self) -> bool:
        """True iff the engine's command resolves."""
        return self.path is not None

    def state(self) -> VState:
        """PASS if present, FAIL if absent."""
        return PASS if self.present else FAIL


@dataclass(frozen=True, slots=True)
class FamilyMastery:
    """Mastery of one family of engines."""

    family: str
    engines: tuple[EngineState, ...]

    @property
    def present(self) -> int:
        """Number of engines present."""
        return sum(1 for e in self.engines if e.present)

    @property
    def total(self) -> int:
        """Total engines in this family."""
        return len(self.engines)

    def state(self) -> VState:
        """PASS at 100%, FAIL at 0%, UNKNOWN in between."""
        if self.total == 0:
            return UNKNOWN
        ratio = self.present / self.total
        if ratio >= 1.0:
            return PASS
        if ratio <= 0.0:
            return FAIL
        return UNKNOWN

    def prims(self) -> dict[str, dict[str, object]]:
        """Per-engine USD/UNS/ROS views."""
        return {
            e.engine.id: {
                "usd": usd_prim(e.engine),
                "uns": uns_path(e.engine),
                "ros": ros_topic(e.engine),
                "qos": ros2_profile(e.engine),
            }
            for e in self.engines
        }


@dataclass(slots=True)
class EngineReport:
    """Full mastery report across every family."""

    per_family: dict[str, FamilyMastery] = field(default_factory=dict)

    def states(self) -> list[VState]:
        """One VState per family."""
        return [m.state() for m in self.per_family.values()]

    def triad(self) -> Triad:
        """Fold family states into a Triad."""
        states = self.states()
        if not states:
            return Triad(UNKNOWN, UNKNOWN, UNKNOWN)
        c = states[0]
        h = states[0]
        d = states[0]
        for s in states[1:]:
            c = meet_truth(c, s)
            h = join_know(h, s)
            d = join_know(d, s)
        return Triad(c, h, d)

    def verdict(self) -> str:
        """Return the triad verdict."""
        return self.triad().verdict()


def assess(resolver: Resolver | None = None) -> EngineReport:
    """Resolve every engine and build a report."""
    r = resolver or _default_resolver
    report = EngineReport()
    for fam in families():
        rows = tuple(EngineState(e, r(e.command)) for e in engines_of(fam))
        report.per_family[fam] = FamilyMastery(family=fam, engines=rows)
    return report
