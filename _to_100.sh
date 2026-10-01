#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
say(){ printf '\033[1;36m==> %s\033[0m\n' "$*"; }

# ── 1. pyproject.toml: exclude if __name__ + pragma lines ─────
say "coverage exclusions in pyproject.toml"
.venv/bin/python - <<'PY'
from pathlib import Path
p = Path("pyproject.toml")
s = p.read_text()
block = (
    "[tool.coverage.report]\n"
    'exclude_lines = [\n'
    '    "pragma: no cover",\n'
    '    "if __name__ == .__main__.:",\n'
    '    "if TYPE_CHECKING:",\n'
    '    "raise NotImplementedError",\n'
    ']\n'
)
if "[tool.coverage.report]" in s:
    # replace the entire [tool.coverage.report] section, preserving other sections
    import re
    pat = re.compile(r'\[tool\.coverage\.report\][^\[]*', re.DOTALL)
    s = pat.sub(block + "\n", s, count=1)
else:
    s = s.rstrip() + "\n\n" + block
p.write_text(s)
print("pyproject: exclude_lines set")
PY

# ── 2. Final coverage tests ───────────────────────────────────
say "tests to hit the last 2%"
cat > tests/test_coverage_final.py <<'PY'
"""Close the final coverage gaps.

After test_coverage_gaps.py, the only misses were:

  __main__.py          54, 58    -- trailing `return 0` (unreachable via
                                    argparse), plus the `if __name__` block
                                    (only hit in a subprocess)
  logging_config.py    29->31    -- the "json_output is None" branch, one
                                    side of which was never taken

Strategy:
  - `return 0`       : monkeypatch argparse to return an unknown cmd
  - `if __name__`    : covered by subprocess + excluded in pyproject
  - logging branch   : call configure with each json_output combination
"""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys

from tmig_closure.__main__ import main
from tmig_closure.logging_config import JsonFormatter, configure


# ── __main__.py ─────────────────────────────────────────────────

def test_main_unknown_cmd_reaches_trailing_return(monkeypatch):
    """Force the code path to the trailing `return 0`.

    argparse `required=True` normally prevents an unknown cmd, but the
    code path is defensive — this test makes it reachable by mocking.
    """
    class FakeArgs:
        cmd = "not-a-real-command"

    monkeypatch.setattr(
        argparse.ArgumentParser, "parse_args",
        lambda self, *a, **kw: FakeArgs(),
    )
    assert main([]) == 0


def test_dunder_main_runs_as_script():
    """Exercise the `if __name__ == '__main__': sys.exit(main())` block."""
    r = subprocess.run(
        [sys.executable, "-m", "tmig_closure", "--version"],
        capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0
    assert "tmig_closure" in r.stdout


# ── logging_config.py ───────────────────────────────────────────

def _clean_logger() -> logging.Logger:
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    if hasattr(root, "_tmig_configured"):
        delattr(root, "_tmig_configured")
    return root


def test_configure_explicit_true_skips_env():
    """json_output=True: `if json_output is None` is False."""
    root = _clean_logger()
    configure(json_output=True)
    assert isinstance(root.handlers[0].formatter, JsonFormatter)


def test_configure_explicit_false_skips_env():
    """json_output=False: `if json_output is None` is False (other side)."""
    root = _clean_logger()
    configure(json_output=False)
    assert not isinstance(root.handlers[0].formatter, JsonFormatter)


def test_configure_none_reads_env(monkeypatch):
    """json_output=None (default): `if json_output is None` is True."""
    monkeypatch.setenv("TMIG_LOG_JSON", "false")
    root = _clean_logger()
    configure()
    assert not isinstance(root.handlers[0].formatter, JsonFormatter)


def test_configure_level_from_env(monkeypatch):
    monkeypatch.setenv("TMIG_LOG_LEVEL", "warning")
    root = _clean_logger()
    configure(json_output=True)
    assert root.level == logging.WARNING


def test_configure_explicit_level_overrides_env(monkeypatch):
    monkeypatch.setenv("TMIG_LOG_LEVEL", "debug")
    root = _clean_logger()
    configure(level="error", json_output=True)
    assert root.level == logging.ERROR
PY

# ── 3. Lint + test ──────────────────────────────────────────────
say "make check"
.venv/bin/ruff check --fix src tests || true
.venv/bin/ruff format src tests || true
set +e
make check 2>&1 | tail -25
RC=${PIPESTATUS[0]}
set -e
if [[ $RC -ne 0 ]]; then
    echo "make check failed (rc=$RC) — aborting before commit"
    exit 1
fi

# ── 4. Commit + push ────────────────────────────────────────────
say "commit"
git add -A
git commit -s -m "test: reach 100% statement and branch coverage

- pyproject.toml: exclude if __name__ blocks and pragma: no cover
- test_coverage_final.py:
  * main() trailing return via mocked argparse (defensive path)
  * subprocess invocation of the module entry point
  * configure(): all four json_output/level combinations
- logging_config: cover the 'json_output is None' branch both ways"
git push || true

# ── 5. Show the final table ─────────────────────────────────────
say "final coverage"
.venv/bin/pytest --cov=tmig_closure --cov-report=term-missing -q 2>&1 | tail -22

# ── 6. Verify CI will agree ────────────────────────────────────
say "pushing kicks CI"
sleep 4
gh run list --repo Danny-TMIG/tmig_closure --workflow ci.yml --limit 2 \
  --json status,conclusion,event,headBranch \
  --jq '.[] | "\(.status)  \(.conclusion // "running")  \(.event)  \(.headBranch)"' || true
