# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Classify a path or filename to a language id."""

from __future__ import annotations

from pathlib import Path

from tmig_closure.mastery_languages.atlas import ATLAS

_EXT_TO_LANG: dict[str, str] = {ext: lang.id for lang in ATLAS for ext in lang.extensions}


def classify_file(path: Path | str) -> str:
    """Return the language id for a file path.

    Unrecognized extensions fall through to ``"other"``. Files without
    an extension also fall through to ``"other"``.
    """
    p = Path(path)
    return _EXT_TO_LANG.get(p.suffix.lower(), "other")


def classify_path(root: Path | str) -> dict[str, list[Path]]:
    """Walk ``root`` and group every regular file by language id.

    Hidden directories (``.git``, ``__pycache__``, ``node_modules``,
    ``.venv``) are skipped. Paths returned are absolute.
    """
    root = Path(root).resolve()
    out: dict[str, list[Path]] = {}
    if not root.exists():
        return out
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(
            part.startswith(".") or part in {"__pycache__", "node_modules"}
            for part in p.relative_to(root).parts
        ):
            continue
        out.setdefault(classify_file(p), []).append(p)
    return out
