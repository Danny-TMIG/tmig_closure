# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group

"""tmig_closure — deterministic closure kernel for capability composition."""

from tmig_closure.agents import Agent, consensus, product, quorum, run_to_fixpoint, step
from tmig_closure.core import (
    ClosureError,
    Config,
    Primitive,
    Rule,
    close,
    closure_steps,
    immediate_consequence,
    rule,
)
from tmig_closure.symmetry import canonical, count_vector, orbit_key, stabilizer_size

__version__ = "0.1.0"

__all__ = [
    "Agent",
    "ClosureError",
    "Config",
    "Primitive",
    "Rule",
    "__version__",
    "canonical",
    "close",
    "closure_steps",
    "consensus",
    "count_vector",
    "immediate_consequence",
    "orbit_key",
    "product",
    "quorum",
    "rule",
    "run_to_fixpoint",
    "stabilizer_size",
    "step",
]
