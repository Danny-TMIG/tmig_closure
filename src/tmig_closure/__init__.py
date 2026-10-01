# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""tmig_closure -- deterministic closure kernel for capability composition."""

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
from tmig_closure.mastery_engines import (
    ENGINES as ENGINE_ATLAS,
)
from tmig_closure.mastery_engines import (
    assess as assess_engines,
)
from tmig_closure.mastery_engines import (
    families as engine_families,
)
from tmig_closure.mastery_languages import (
    ATLAS as LANGUAGES_ATLAS,
)
from tmig_closure.mastery_languages import (
    assess as assess_languages,
)
from tmig_closure.mastery_languages import (
    classify_file as classify_language,
)
from tmig_closure.mastery_languages import (
    languages as language_ids,
)
from tmig_closure.symmetry import canonical, count_vector, orbit_key, stabilizer_size
from tmig_closure.triad import (
    ALL_STATES,
    CONFLICT,
    FAIL,
    PASS,
    UNKNOWN,
    Triad,
    VState,
    coherence,
    conformance,
    consensus_v,
    coordination,
    join_know,
    join_truth,
    meet_know,
    meet_truth,
    quorum_v,
    verify,
)

__version__ = "0.2.0"

__all__ = [
    "ALL_STATES",
    "CONFLICT",
    "ENGINE_ATLAS",
    "FAIL",
    "LANGUAGES_ATLAS",
    "PASS",
    "UNKNOWN",
    "Agent",
    "ClosureError",
    "Config",
    "Primitive",
    "Rule",
    "Triad",
    "VState",
    "__version__",
    "assess_engines",
    "assess_languages",
    "canonical",
    "classify_language",
    "close",
    "closure_steps",
    "coherence",
    "conformance",
    "consensus",
    "consensus_v",
    "coordination",
    "count_vector",
    "engine_families",
    "immediate_consequence",
    "join_know",
    "join_truth",
    "language_ids",
    "meet_know",
    "meet_truth",
    "orbit_key",
    "product",
    "quorum",
    "quorum_v",
    "rule",
    "run_to_fixpoint",
    "stabilizer_size",
    "step",
    "verify",
]
