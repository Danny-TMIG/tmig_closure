# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group

"""Symmetry reduction: canonical forms and count-vectors."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from math import factorial

Primitive = str


def canonical(items: Iterable[Primitive]) -> tuple[Primitive, ...]:
    """Sorted tuple — lexicographically least representative of the orbit."""
    return tuple(sorted(items))


def count_vector(
    items: Iterable[Primitive],
    alphabet: Iterable[Primitive],
) -> tuple[int, ...]:
    """Histogram of items over the sorted alphabet. S_alphabet-invariant."""
    counts = Counter(items)
    return tuple(counts[p] for p in sorted(alphabet))


def orbit_key(items: Iterable[Primitive]) -> tuple[tuple[Primitive, int], ...]:
    """Deterministic key uniquely identifying the orbit of items under S_A."""
    counts = Counter(items)
    return tuple(sorted(counts.items()))


def stabilizer_size(items: Iterable[Primitive]) -> int:
    """|Stab(x)| = product of factorials of multiplicities."""
    counts = Counter(items)
    out = 1
    for m in counts.values():
        out *= factorial(m)
    return out
