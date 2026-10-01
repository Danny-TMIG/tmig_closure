# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Mastery assessment: score each language by competency coverage."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from tmig_closure.mastery_languages.atlas import ATLAS
from tmig_closure.mastery_languages.classifier import classify_file
from tmig_closure.triad import (
    FAIL,
    PASS,
    UNKNOWN,
    Triad,
    VState,
    join_know,
)


@dataclass(frozen=True, slots=True)
class Competency:
    """A competency and whether the codebase exercises it."""

    id: str
    title: str
    hit: bool


@dataclass(frozen=True, slots=True)
class Mastery:
    """Mastery of a single language across a set of files."""

    language: str
    files: int
    competencies: tuple[Competency, ...]

    @property
    def covered(self) -> int:
        """Number of competencies whose regex matched at least one file."""
        return sum(1 for c in self.competencies if c.hit)

    @property
    def total(self) -> int:
        """Total competencies catalogued for this language."""
        return len(self.competencies)

    def state(self) -> VState:
        """Map coverage to a Belnap FOUR state.

        PASS at 100%, FAIL at 0%, UNKNOWN in between (partial coverage
        is not a proof of either mastery or its absence).
        """
        if self.files == 0:
            return UNKNOWN
        if self.total == 0:
            return UNKNOWN
        ratio = self.covered / self.total
        if ratio >= 1.0:
            return PASS
        if ratio <= 0.0:
            return FAIL
        return UNKNOWN


@dataclass(slots=True)
class Report:
    """A full mastery report across every language in the atlas."""

    root: Path
    per_language: dict[str, Mastery] = field(default_factory=dict)

    def triad(self) -> Triad:
        """Fold every language's state into one triad.

        Conformance is meet_truth across languages (all must be PASS).
        Coherence is join_know (union of information).
        Coordination is join_know as well — one bag of observations.
        """
        states = [m.state() for m in self.per_language.values()]
        if not states:
            return Triad(UNKNOWN, UNKNOWN, UNKNOWN)
        conf = states[0]
        for s in states[1:]:
            conf = Triad(conf, s, s).conjunction(Triad(s, s, s)).conformance
        # simpler: fold with meet_truth
        from tmig_closure.triad import meet_truth

        c = states[0]
        for s in states[1:]:
            c = meet_truth(c, s)
        h = states[0]
        for s in states[1:]:
            h = join_know(h, s)
        d = states[0]
        for s in states[1:]:
            d = join_know(d, s)
        return Triad(c, h, d)

    def verdict(self) -> str:
        """Return the triad verdict."""
        return self.triad().verdict()


def scan(root: Path | str) -> dict[str, list[Path]]:
    """Return files under ``root`` grouped by language id."""
    root = Path(root).resolve()
    out: dict[str, list[Path]] = {}
    if not root.exists():
        return out
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(
            part.startswith(".") or part in {"__pycache__", "node_modules"}
            for part in p.relative_to(root).parts
        ):
            continue
        out.setdefault(classify_file(p), []).append(p)
    return out


def assess(root: Path | str, *, max_bytes: int = 1_000_000) -> Report:
    """Scan ``root`` and return a mastery Report per language.

    ``max_bytes`` caps the size of any single file read; larger files
    are ignored so a stray binary cannot blow up the scan.
    """
    root = Path(root).resolve()
    groups = scan(root)
    report = Report(root=root)
    for lang in ATLAS:
        files = groups.get(lang.id, [])
        competencies = []
        for comp in lang.competencies:
            hit = False
            for fp in files:
                try:
                    if fp.stat().st_size > max_bytes:
                        continue
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if comp.pattern.search(text):
                    hit = True
                    break
            competencies.append(Competency(comp.id, comp.title, hit))
        report.per_language[lang.id] = Mastery(
            language=lang.id,
            files=len(files),
            competencies=tuple(competencies),
        )
    return report
