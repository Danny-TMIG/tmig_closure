# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""CLI: ``python -m tmig_closure.mastery_languages``."""

from __future__ import annotations

import argparse
import json
import sys

from tmig_closure.mastery_languages.mastery import assess


def _parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    p = argparse.ArgumentParser(prog="python -m tmig_closure.mastery_languages")
    p.add_argument("root", nargs="?", default=".")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("report", help="full mastery report as JSON")
    sub.add_parser("verdict", help="just the triad verdict")
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success."""
    args = _parser().parse_args(argv)
    rep = assess(args.root)
    if args.cmd == "verdict":
        print(rep.verdict())
        return 0
    payload = {
        "root": str(rep.root),
        "verdict": rep.verdict(),
        "languages": {
            lid: {
                "files": m.files,
                "covered": m.covered,
                "total": m.total,
                "state": m.state().name,
            }
            for lid, m in rep.per_language.items()
        },
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
