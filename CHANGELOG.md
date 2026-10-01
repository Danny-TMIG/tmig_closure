# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Semantic Versioning: [semver.org](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-09-30

### Added

- **Kernel** (`core.py`): immediate-consequence operator `T_R`, Knaster–Tarski
  closure `cl_R`, `closure_steps` iterator, `ClosureError`.
- **Agents** (`agents.py`): `Agent`, synchronous `step`, `run_to_fixpoint`,
  `product`, `quorum`, `consensus`.
- **Symmetry** (`symmetry.py`): `canonical`, `count_vector`, `orbit_key`,
  `stabilizer_size`.
- **API** (`api.py`): `POST /closure`, `/agents/step`, `/agents/run`,
  `/symmetry/canonical`, plus `/health`, `/ready`, `/version`.
- **CLI**: `tmig close --config ... --rule ...`, `tmig serve`.
- **Tests**: 39 across 5 modules — kernel, agents, symmetry, HTTP e2e, and
  hypothesis-verified properties (extensive, monotone, idempotent, fixpoint-stable).
- **Model check** (`scripts/verify.py`): exhaustive on 3 primitives × 3 rulesets.
- **CI**: ruff + mypy strict + pytest on 3.12 and 3.13; CodeQL;
  dependency-review; gitleaks.
- **Release**: tag-triggered sdist+wheel, SPDX SBOM, SLSA provenance, GitHub release.
- **Docs**: `docs/theory.md`, four runbooks, two SLOs, ADR-0001 (why no LLM).

[Unreleased]: https://github.com/Danny-TMIG/tmig_closure/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Danny-TMIG/tmig_closure/releases/tag/v0.1.0
