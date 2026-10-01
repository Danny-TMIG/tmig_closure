# Deploy

<!-- SPDX-License-Identifier: MIT -->

1. `make check`.
2. `make build`.
3. `make sbom`.
4. `git tag -s vX.Y.Z`.
5. CI publishes the signed wheel.
6. Staging smoke test.
7. Promote on green.
