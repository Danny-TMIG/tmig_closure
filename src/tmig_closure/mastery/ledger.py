# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Append-only ledger of mastery decisions."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Record:
    """One mastery decision, immutable once written."""

    at: float
    run_id: int
    workflow: str
    state: str
    action: str
    note: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable view."""
        return asdict(self)


class Ledger:
    """Append-only JSONL store of Record values."""

    def __init__(self, path: Path | str) -> None:
        """Bind to a JSONL file path."""
        self.path = Path(path)

    def append(self, record: Record) -> None:
        """Write one record to the end of the file, fsynced."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.to_dict(), separators=(",", ":")))
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())

    def read(self) -> list[Record]:
        """Return every well-formed record in file order."""
        if not self.path.exists():
            return []
        out: list[Record] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw)
                out.append(
                    Record(
                        at=float(obj["at"]),
                        run_id=int(obj["run_id"]),
                        workflow=str(obj["workflow"]),
                        state=str(obj["state"]),
                        action=str(obj["action"]),
                        note=str(obj.get("note", "")),
                    )
                )
            except (KeyError, ValueError, TypeError):
                continue
        return out

    def __iter__(self) -> Iterator[Record]:
        """Iterate over history."""
        return iter(self.read())

    def __len__(self) -> int:
        """Return the number of records on disk."""
        return len(self.read())

    @classmethod
    def now(cls) -> float:
        """Current time, isolated so tests can freeze it."""
        return time.time()
