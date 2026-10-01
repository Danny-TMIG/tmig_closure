#!/usr/bin/env bash
set -euo pipefail
OUT="${OUT:-.sbom}"
mkdir -p "$OUT"
if command -v syft >/dev/null 2>&1; then
  syft . -o spdx-json="$OUT/tmig_closure.spdx.json" && echo "wrote SPDX"
fi
if command -v cyclonedx-py >/dev/null 2>&1; then
  cyclonedx-py environment -o "$OUT/tmig_closure.cdx.json" && echo "wrote CycloneDX"
fi
