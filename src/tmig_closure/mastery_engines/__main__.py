# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""CLI: python -m tmig_closure.mastery_engines [report|verdict|family <id>]."""

from __future__ import annotations

import argparse
import json
import sys

from tmig_closure.mastery_engines.atlas import ENGINES, engines_of, families
from tmig_closure.mastery_engines.mastery import assess


def _parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    p = argparse.ArgumentParser(prog="python -m tmig_closure.mastery_engines")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("report")
    sub.add_parser("verdict")
    sub.add_parser("atlas")
    f = sub.add_parser("family")
    f.add_argument("id")
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success, 2 for unknown family."""
    args = _parser().parse_args(argv)

    if args.cmd == "atlas":
        print(
            json.dumps(
                {
                    "families": list(families()),
                    "total": len(ENGINES),
                    "per_family": {f: len(engines_of(f)) for f in families()},
                },
                indent=2,
            )
        )
        return 0

    if args.cmd == "family":
        if args.id not in families():
            print(json.dumps({"error": f"unknown family: {args.id}"}), file=sys.stderr)
            return 2
        rep = assess()
        m = rep.per_family[args.id]
        print(
            json.dumps(
                {
                    "family": args.id,
                    "present": m.present,
                    "total": m.total,
                    "state": m.state().name,
                    "engines": {
                        e.engine.id: {"present": e.present, "path": e.path} for e in m.engines
                    },
                },
                indent=2,
            )
        )
        return 0

    rep = assess()
    if args.cmd == "verdict":
        print(rep.verdict())
        return 0

    print(
        json.dumps(
            {
                "verdict": rep.verdict(),
                "families": {
                    f: {"present": m.present, "total": m.total, "state": m.state().name}
                    for f, m in rep.per_family.items()
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
