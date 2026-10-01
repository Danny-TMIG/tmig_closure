# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Structured JSON logging to stderr, stdlib only."""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON.

    Emits RFC 3339 UTC timestamps, level, logger name, message, an ``exc``
    field when exception info is attached, and any of a small set of extra
    fields if the caller supplied them via ``extra={...}``.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Render a log record as a JSON string."""
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created))
            + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for k in ("event", "config_size", "rule_count", "iterations", "request_id"):
            if hasattr(record, k):
                payload[k] = getattr(record, k)
        return json.dumps(payload, separators=(",", ":"), default=str)


def configure(level: str | None = None, *, json_output: bool | None = None) -> None:
    """Idempotently configure the root logger.

    ``level`` falls back to ``TMIG_LOG_LEVEL`` (default ``INFO``).
    ``json_output`` falls back to ``TMIG_LOG_JSON`` (default ``true``).
    Repeated calls are no-ops once ``_tmig_configured`` is set on the root
    logger. The two uvicorn loggers are aligned to the same level.
    """
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

    for noisy in ("uvicorn.access", "uvicorn.error"):
        logging.getLogger(noisy).setLevel(lvl)
    root._tmig_configured = True  # type: ignore[attr-defined]
