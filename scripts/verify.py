#!/usr/bin/env python3
"""Verify the kernel's five algebraic laws with a small model check."""
from __future__ import annotations
import itertools, sys
from tmig_closure import close, immediate_consequence, rule

PRIMITIVES = ["a", "b", "c"]
SUBSETS = [frozenset(s) for r in range(len(PRIMITIVES) + 1)
           for s in itertools.combinations(PRIMITIVES, r)]
RULES = [
    [rule("a", "b")],
    [rule("a", "b"), rule("b", "c")],
    [rule(["a", "b"], "c")],
]


def main() -> int:
    failures = []
    for rs in RULES:
        for x in SUBSETS:
            if not x <= close(x, rs):
                failures.append(f"extensive: X={x}")
            if close(close(x, rs), rs) != close(x, rs):
                failures.append(f"idempotent: X={x}")
            fix = close(x, rs)
            if immediate_consequence(fix, rs) != fix:
                failures.append(f"fixpoint: X={x}")
            for y in SUBSETS:
                if x <= y and not close(x, rs) <= close(y, rs):
                    failures.append(f"monotone: X={x} Y={y}")
    if failures:
        for f in failures[:10]:
            print(f, file=sys.stderr)
        print(f"verify: FAIL ({len(failures)} violations)", file=sys.stderr)
        return 1
    print("verify: PASS — all 5 laws hold on the 3-primitive model")
    return 0


if __name__ == "__main__":
    sys.exit(main())
