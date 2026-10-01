#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
PY="${PYTHON:-python3}"
VENV="${VENV:-.venv}"
[[ -d "$VENV" ]] || "$PY" -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -e ".[dev]"
command -v pre-commit >/dev/null 2>&1 && "$VENV/bin/pre-commit" install --install-hooks || true
echo "bootstrap: ok — source $VENV/bin/activate"
