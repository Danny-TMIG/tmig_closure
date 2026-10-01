# Contributing

<!-- SPDX-License-Identifier: MIT -->

## Setup

    make install

## Workflow

1. Fork, branch from main.
2. Write the test first if fixing a bug.
3. `make check` before pushing.
4. Conventional Commits: feat, fix, docs, refactor, test, chore.

## The math is the contract

If your change touches `core.py`, run `python scripts/verify.py` and
`pytest tests/test_properties.py` — the five laws must hold.
