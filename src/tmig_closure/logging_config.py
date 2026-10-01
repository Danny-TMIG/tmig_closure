"""Structured JSON logging to stderr, stdlib only."""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created))
            + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), default=str)


def configure(level: str | None = None, *, json_output: bool | None = None) -> None:
    lvl = (level or os.environ.get("TMIG_LOG_LEVEL", "INFO")).upper()
    if json_output is None:
        json_output = os.environ.get("TMIG_LOG_JSON", "true").lower() == "true"
    root = logging.getLogger()
    if getattr(root, "_tmig_configured", False):
        return
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        JsonFormatter()
        if json_output
        else logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root.addHandler(handler)
    root.setLevel(lvl)
    root._tmig_configured = True  # type: ignore[attr-defined]
