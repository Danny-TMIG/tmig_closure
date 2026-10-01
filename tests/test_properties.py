"""Property tests — the five algebraic laws of the closure operator."""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tmig_closure import close, immediate_consequence

PRIMITIVES = st.text(alphabet="abcdefgh", min_size=1, max_size=1)
CONFIGS = st.frozensets(PRIMITIVES, max_size=6)
RULES = st.lists(
    st.tuples(st.frozensets(PRIMITIVES, max_size=3), st.frozensets(PRIMITIVES, max_size=2)),
    max_size=8,
)

SETTINGS = settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])


@given(x=CONFIGS, rules=RULES)
@SETTINGS
def test_extensive(x, rules):
    assert x <= close(x, rules)


@given(x=CONFIGS, y=CONFIGS, rules=RULES)
@SETTINGS
def test_monotone(x, y, rules):
    if x <= y:
        assert close(x, rules) <= close(y, rules)


@given(x=CONFIGS, rules=RULES)
@SETTINGS
def test_idempotent(x, rules):
    once = close(x, rules)
    assert close(once, rules) == once


@given(x=CONFIGS, rules=RULES)
@SETTINGS
def test_fixpoint_is_stable(x, rules):
    fix = close(x, rules)
    assert immediate_consequence(fix, rules) == fix
