# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group

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
        argparse.ArgumentParser,
        "parse_args",
        lambda self, *a, **kw: FakeArgs(),
    )
    assert main([]) == 0


def test_dunder_main_runs_as_script():
    """Exercise the `if __name__ == '__main__': sys.exit(main())` block."""
    r = subprocess.run(
        [sys.executable, "-m", "tmig_closure", "--version"],
        capture_output=True,
        text=True,
        check=False,
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


# ── logging_config: extra-fields branch ────────────────────────


def test_json_formatter_includes_extra_fields() -> None:
    """Cover the loop body that copies selected `extra={...}` fields."""
    import json as _json
    import logging as _logging

    from tmig_closure.logging_config import JsonFormatter

    record = _logging.LogRecord(
        "t",
        _logging.INFO,
        __file__,
        1,
        "msg",
        (),
        None,
    )
    # Attach every field the formatter inspects.
    record.event = "verify"
    record.config_size = 3
    record.rule_count = 7
    record.iterations = 5
    record.request_id = "req-1"

    payload = _json.loads(JsonFormatter().format(record))
    assert payload["event"] == "verify"
    assert payload["config_size"] == 3
    assert payload["rule_count"] == 7
    assert payload["iterations"] == 5
    assert payload["request_id"] == "req-1"
