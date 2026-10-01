# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""``python -m tmig_closure`` / ``tmig`` — CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys

from tmig_closure import __version__, close, rule
from tmig_closure.core import ClosureError


def main(argv: list[str] | None = None) -> int:
    """Run the CLI.

    Subcommands:
        close   compute the closure of a config under a rule set
        serve   run the HTTP API via uvicorn

    Returns 0 on success, 2 for bad rule syntax, 3 if closure fails
    to converge, and 0 for the serve path.
    """
    p = argparse.ArgumentParser(prog="tmig", description="tmig_closure CLI")
    p.add_argument("--version", action="version", version=f"tmig_closure {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("close", help="compute closure of a config under rules")
    c.add_argument("--config", required=True, help="comma-separated primitives")
    c.add_argument("--rule", action="append", default=[], metavar="PRE>POST")

    sub.add_parser("serve", help="run the API (uvicorn)")

    args = p.parse_args(argv)

    if args.cmd == "serve":
        import uvicorn

        uvicorn.run("tmig_closure.asgi:app", host="127.0.0.1", port=8000)
        return 0

    if args.cmd == "close":
        cfg = frozenset(x.strip() for x in args.config.split(",") if x.strip())
        rules = []
        for r in args.rule:
            if ">" not in r:
                print(f"bad rule: {r}", file=sys.stderr)
                return 2
            pre, _, post = r.partition(">")
            rules.append(
                rule(
                    (x.strip() for x in pre.split(",") if x.strip()),
                    (x.strip() for x in post.split(",") if x.strip()),
                )
            )
        try:
            result = close(cfg, rules)
        except ClosureError as e:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
            return 3
        print(json.dumps({"closure": sorted(result)}))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
