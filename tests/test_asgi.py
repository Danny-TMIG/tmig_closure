# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group

"""ASGI + CLI entry-point coverage."""

import subprocess
import sys
from pathlib import Path

from tmig_closure.asgi import app


def test_asgi_app_is_fastapi() -> None:
    assert app.title == "tmig_closure"
    assert app.version


def test_cli_version() -> None:
    r = subprocess.run(
        [sys.executable, "-m", "tmig_closure", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert "tmig_closure" in r.stdout


def test_cli_close_smoke() -> None:
    r = subprocess.run(
        [sys.executable, "-m", "tmig_closure", "close", "--config", "a", "--rule", "a>b"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert '"a"' in r.stdout
    assert '"b"' in r.stdout


def test_py_typed_marker() -> None:
    marker = Path(__file__).resolve().parent.parent / "src/tmig_closure/py.typed"
    assert marker.exists()
