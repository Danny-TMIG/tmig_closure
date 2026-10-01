# Security

<!-- SPDX-License-Identifier: MIT -->

## Reporting

Email `security@the-mark-intelligence-group.example`. Do not open a public issue.

Acknowledge in 3 business days; fix within 30 for critical.

## Threat model

- Pydantic validates every request body.
- Integer bounds (`max_steps`) prevent runaway iterations.
- Stateless service. No persistent state.
- No outbound network. Egress can be blocked.
- Runtime image contains only the installed wheel.
- Runs as UID 10001, `cap_drop: ALL`, read-only rootfs.

## Supply chain

Signed commits. Dependabot weekly. CodeQL on PR + weekly. gitleaks on push.
SBOMs via `make sbom`. Releases signed with cosign (keyless).
