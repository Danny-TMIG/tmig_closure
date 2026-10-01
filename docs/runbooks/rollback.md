# Rollback

<!-- SPDX-License-Identifier: MIT -->

1. Identify last-known-good image tag.
2. `docker compose down && up -d` with tag.
3. Verify `/health` and `/version`.
4. Confirm SLO recovery in 15 min.
5. File incident ticket.
