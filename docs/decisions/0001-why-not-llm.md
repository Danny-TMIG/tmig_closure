# ADR 0001 — Why no LLM in the kernel

**Status:** Accepted (2026-09)

## Decision

The kernel is algebraic. No LLM, no heuristics, no vendor SDKs. Rules are declarative
pairs `(P, C)`; closure is a Tarski fixed point.

## Consequences

**Positive.** Deterministic. Auditable (rules are files). Hypothesis-verifiable with no
flakiness. Microseconds for realistic sizes. No external inference on the critical path.

**Negative.** Rules must be written explicitly. Interpretation (deciding which primitives
a tool exposes) may use an LLM above the kernel. The kernel never does.
