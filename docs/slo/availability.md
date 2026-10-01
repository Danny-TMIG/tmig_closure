# Availability SLO

<!-- SPDX-License-Identifier: MIT -->

**Target:** 99.9% of requests succeed over a rolling 30-day window.
**Success:** HTTP 2xx/3xx within timeout budget. **Failure:** 5xx, connection failure, timeout.
**Error budget:** 0.1%. Burn alert at 2x over 1h.
