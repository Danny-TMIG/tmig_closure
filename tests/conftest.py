# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group

"""Shared fixtures."""

import pytest

from tmig_closure import rule


@pytest.fixture
def chain_rules():
    return [rule("a", "b"), rule("b", "c"), rule("c", "d")]


@pytest.fixture
def diamond_rules():
    return [rule("a", "b"), rule("a", "c"), rule(["b", "c"], "d")]
