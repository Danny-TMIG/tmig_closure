# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""CLI for autonomous mastery."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from tmig_closure.mastery.ledger import Ledger
from tmig_closure.mastery.mastery import Mastery


def _build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the mastery CLI."""
    p = argparse.ArgumentParser(prog="python -m tmig_closure.mastery")
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--ledger", default=".mastery/ledger.jsonl")
    p.add_argument("--max-attempts", type=int, default=3)
    p.add_argument("--limit", type=int, default=50)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("observe")
    sub.add_parser("plan")
    sub.add_parser("cycle")
    loop = sub.add_parser("loop")
    loop.add_argument("--cycles", type=int, default=10)
    loop.add_argument("--delay", type=float, default=30.0)
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success, 2 on gh failure."""
    args = _build_parser().parse_args(argv)
    ledger = Ledger(Path(args.ledger))
    mastery = Mastery(
        repo=args.repo, ledger=ledger, max_attempts=args.max_attempts, limit=args.limit
    )

    if args.cmd == "status":
        print(json.dumps(mastery.stats(), indent=2))
        return 0

    if args.cmd in ("observe", "plan", "cycle"):
        try:
            if args.cmd == "observe":
                payload = [r.to_dict() for r in mastery.observe()]
            elif args.cmd == "plan":
                payload = [d.to_dict() for d in mastery.plan(mastery.observe())]
            else:
                payload = [d.to_dict() for d in mastery.cycle()]
        except RuntimeError as e:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
            return 2
        print(json.dumps(payload, indent=2))
        return 0

    if args.cmd == "loop":
        for i in range(args.cycles):
            try:
                decisions = mastery.cycle()
            except RuntimeError as e:
                print(json.dumps({"cycle": i, "error": str(e)}))
                return 2
            print(json.dumps({"cycle": i, "decisions": len(decisions)}))
            if i + 1 < args.cycles:
                time.sleep(args.delay)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
