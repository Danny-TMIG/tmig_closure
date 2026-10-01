# tmig_closure

<!-- SPDX-License-Identifier: MIT -->

![ci](https://github.com/Danny-TMIG/tmig_closure/actions/workflows/ci.yml/badge.svg)
![codeql](https://github.com/Danny-TMIG/tmig_closure/actions/workflows/codeql.yml/badge.svg)
![license](https://img.shields.io/badge/license-MIT-blue.svg)
![python](https://img.shields.io/badge/python-3.12%2B-blue.svg)

**Autonomous Edge Super-Node — deterministic closure kernel for capability composition.**

Reduces every domain (AI, DevOps, networking, IoT, web, quantum) to two things:
*capability primitives* and *composition rules*. Computes the least fixed point of the
immediate-consequence operator, contracts under symmetric-group action, exposes over HTTP.
No LLM. No heuristics. A Tarski closure operator with production scaffolding.

## The math

Let `A` be a finite alphabet. Configuration `X subset A`. Rule `(P, C)`, `P,C subset A`.
Immediate-consequence operator:

    T_R(X) = X union { c | (P,C) in R, P subset X, c in C }

`T_R` monotone; `A` finite; so by Knaster-Tarski the least fixed point `cl_R(X)` exists,
reached in at most `|A|` iterations. `cl_R` is **extensive**, **monotone**, **idempotent** —
a closure operator on `(2^A, subset)`. Two configurations are `S_A`-equivalent iff their
count-vectors agree. See `docs/theory.md`.

All five laws are machine-checked by hypothesis in `tests/test_properties.py`.

## Quickstart

    make install
    make run                                    # uvicorn on :8000
    curl -s localhost:8000/health
    curl -s -X POST localhost:8000/closure \
      -H 'content-type: application/json' \
      -d '{"config":["a"],"rules":[{"premises":["a"],"conclusions":["b"]},
                                  {"premises":["b"],"conclusions":["c"]}]}'
    # {"closure":["a","b","c"],"added":["b","c"],"iterations":2}

CLI: `tmig close --config a --rule 'a>b' --rule 'b>c'`

## Layout

    src/tmig_closure/     core.py  agents.py  symmetry.py  api.py  asgi.py
    tests/                unit + property (hypothesis) + e2e
    docs/                 theory.md  runbooks/  slo/  decisions/
    .github/workflows/    ci, codeql, dependency-review, secrets

## Compliance

MIT. SBOM via `make sbom` (SPDX + CycloneDX). Signed releases. Reproducible wheels.
See `SECURITY.md` and `docs/slo/`.

---

*The Mark Intelligence Group*
