# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Tests for the language mastery subsystem."""

from __future__ import annotations

from pathlib import Path

import pytest

from tmig_closure.mastery_languages import (
    ATLAS,
    Competency,
    Mastery,
    Report,
    assess,
    classify_file,
    classify_path,
    languages,
)
from tmig_closure.mastery_languages.__main__ import main
from tmig_closure.mastery_languages.atlas import by_id
from tmig_closure.triad import FAIL, PASS, UNKNOWN


def _write(root: Path, name: str, body: str) -> Path:
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    return p


# ── atlas ──────────────────────────────────────────────────────────


def test_languages_listed():
    assert set(languages()) == {
        "python",
        "shell",
        "typescript",
        "javascript",
        "mermaid",
        "codeql",
        "other",
    }


def test_by_id_known():
    assert by_id("python").title == "Python"


def test_by_id_unknown():
    with pytest.raises(KeyError, match="unknown language"):
        by_id("rust")


def test_every_language_has_competencies():
    for lang in ATLAS:
        assert lang.competencies, lang.id


def test_every_competency_has_id_and_title():
    for lang in ATLAS:
        for c in lang.competencies:
            assert c.id
            assert c.title
            assert c.pattern is not None


def test_competency_is_frozen():
    from dataclasses import FrozenInstanceError

    c = Competency("x", "X", __import__("re").compile("x"))
    with pytest.raises(FrozenInstanceError):
        c.id = "y"


# ── classifier ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("main.py", "python"),
        ("x.pyi", "python"),
        ("build.sh", "shell"),
        ("run.bash", "shell"),
        ("a.zsh", "shell"),
        ("app.ts", "typescript"),
        ("app.tsx", "typescript"),
        ("m.mts", "typescript"),
        ("cli.js", "javascript"),
        ("ui.jsx", "javascript"),
        ("diagram.mmd", "mermaid"),
        ("query.ql", "codeql"),
        ("query.qll", "codeql"),
        ("README.md", "other"),
        ("Makefile", "other"),
        ("noext", "other"),
        ("weird.PY", "python"),
    ],
)
def test_classify_file(name, expected):
    assert classify_file(name) == expected


def test_classify_path_groups(tmp_path: Path):
    _write(tmp_path, "a.py", "x = 1")
    _write(tmp_path, "b.sh", "echo hi")
    _write(tmp_path, "c.ts", "const x = 1")
    _write(tmp_path, "readme.md", "# hi")
    _write(tmp_path, "sub/d.py", "y = 2")
    groups = classify_path(tmp_path)
    assert set(groups) == {"python", "shell", "typescript", "other"}
    assert len(groups["python"]) == 2


def test_classify_path_skips_hidden(tmp_path: Path):
    _write(tmp_path, ".git/x.py", "x")
    _write(tmp_path, "__pycache__/y.py", "y")
    _write(tmp_path, "node_modules/z.py", "z")
    _write(tmp_path, "ok.py", "ok")
    groups = classify_path(tmp_path)
    assert len(groups.get("python", [])) == 1


def test_classify_path_missing(tmp_path: Path):
    assert classify_path(tmp_path / "nope") == {}


# ── mastery / report ───────────────────────────────────────────────


def test_mastery_state_pass():
    m = Mastery("python", 1, (Competency("a", "A", True),))
    assert m.state() is PASS


def test_mastery_state_fail():
    m = Mastery("python", 1, (Competency("a", "A", False),))
    assert m.state() is FAIL


def test_mastery_state_unknown_partial():
    m = Mastery("python", 1, (Competency("a", "A", True), Competency("b", "B", False)))
    assert m.state() is UNKNOWN


def test_mastery_state_unknown_no_files():
    m = Mastery("python", 0, (Competency("a", "A", True),))
    assert m.state() is UNKNOWN


def test_mastery_state_unknown_no_competencies():
    m = Mastery("python", 1, ())
    assert m.state() is UNKNOWN


def test_report_triad_empty():
    r = Report(root=Path("."))
    assert r.verdict() == "UNKNOWN"


def test_report_triad_mixed():
    r = Report(root=Path("."))
    r.per_language["python"] = Mastery("python", 1, (Competency("a", "A", True),))
    r.per_language["shell"] = Mastery("shell", 1, (Competency("a", "A", True),))
    assert r.verdict() == "PASS"


# ── assess ─────────────────────────────────────────────────────────


def test_assess_missing_root(tmp_path: Path):
    rep = assess(tmp_path / "nope")
    assert all(m.files == 0 for m in rep.per_language.values())
    assert rep.verdict() == "UNKNOWN"


def test_assess_python_full_mastery(tmp_path: Path):
    src = (
        "from __future__ import annotations\n"
        "from dataclasses import dataclass\n"
        "from enum import StrEnum\n"
        "import contextlib\n"
        "from typing import Protocol\n\n"
        "class P(Protocol):\n    def f(self) -> int: ...\n\n"
        "@dataclass(slots=True)\nclass D:\n    x: int = 0\n\n"
        "class E(StrEnum):\n    A = 'a'\n\n"
        "async def af() -> int:\n    return await g()\n\n"
        "def g():\n    return 1\n\n"
        "def gen():\n    yield from []\n\n"
        "@contextlib.contextmanager\ndef cm():\n    yield\n\n"
        "with cm():\n    pass\n\n"
        "xs = [x for x in range(3)]\n"
        "s = f'{xs[0]}'\n\n"
        "match xs:\n    case []:\n        pass\n"
    )
    _write(tmp_path, "m.py", src)
    rep = assess(tmp_path)
    py = rep.per_language["python"]
    assert py.files == 1
    assert py.covered == py.total, [c for c in py.competencies if not c.hit]


def test_assess_shell_partial(tmp_path: Path):
    _write(tmp_path, "s.sh", "#!/bin/bash\nset -euo pipefail\necho hi\n")
    rep = assess(tmp_path)
    sh = rep.per_language["shell"]
    assert sh.files == 1
    assert 0 < sh.covered < sh.total


def test_assess_skips_oversize(tmp_path: Path):
    _write(tmp_path, "big.py", "x" * 2_000_000)
    rep = assess(tmp_path, max_bytes=1000)
    assert rep.per_language["python"].covered == 0


def test_assess_handles_read_errors(tmp_path: Path):
    p = tmp_path / "bad.py"
    p.write_bytes(b"\xff\xfe invalid utf8 \x00")
    rep = assess(tmp_path)
    # Should not raise
    assert rep.per_language["python"].files == 1


def test_assess_other_language(tmp_path: Path):
    _write(tmp_path, "notes.txt", "hello")
    rep = assess(tmp_path)
    assert rep.per_language["other"].files == 1


# ── CLI ────────────────────────────────────────────────────────────


def test_cli_verdict(tmp_path: Path, capsys):
    _write(tmp_path, "x.py", "x = 1")
    assert main([str(tmp_path), "verdict"]) == 0
    assert capsys.readouterr().out.strip() in {"PASS", "FAIL", "UNKNOWN", "CONFLICT"}


def test_cli_report(tmp_path: Path, capsys):
    _write(tmp_path, "x.py", "x = 1")
    assert main([str(tmp_path), "report"]) == 0
    import json as _json

    payload = _json.loads(capsys.readouterr().out)
    assert payload["verdict"] in {"PASS", "FAIL", "UNKNOWN", "CONFLICT"}
    assert "python" in payload["languages"]
    assert payload["languages"]["python"]["files"] == 1


def test_cli_default_root(capsys):
    assert main(["verdict"]) == 0
    capsys.readouterr()


def test_assess_io_error_returns_empty(tmp_path: Path, monkeypatch):
    """Cover the OSError branch in assess()."""
    (tmp_path / "x.py").write_text("x = 1")

    def boom(self, *a, **kw):
        raise OSError("simulated")

    monkeypatch.setattr(Path, "read_text", boom)
    rep = assess(tmp_path)
    assert rep.per_language["python"].covered == 0
