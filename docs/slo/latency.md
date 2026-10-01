# Latency SLO

<!-- SPDX-License-Identifier: MIT -->

**Target:** p99 <= 250 ms for `POST /closure` with `|config| <= 100` and `|rules| <= 100`.
**Target:** p50 <= 20 ms same shape.
**Degradation:** p99 > 250 ms for 10 min pages on-call.
