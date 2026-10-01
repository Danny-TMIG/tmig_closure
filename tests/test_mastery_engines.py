# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""Tests for the engine mastery subsystem."""

from __future__ import annotations

import pytest

from tmig_closure.mastery_engines import (
    ENGINES,
    ROS2_QOS,
    ROS_NS,
    UNS_ROOT,
    USD_ROOT,
    EngineReport,
    EngineState,
    FamilyMastery,
    assess,
    engines_of,
    families,
    resolve_all,
    ros2_profile,
    ros_topic,
    uns_path,
    usd_prim,
)
from tmig_closure.mastery_engines.__main__ import main
from tmig_closure.mastery_engines.atlas import by_id
from tmig_closure.triad import FAIL, PASS, UNKNOWN

# ── atlas ────────────────────────────────────────────────────────────


def test_families_listed():
    assert set(families()) == {
        "language",
        "format",
        "build",
        "package",
        "datastore",
        "ai",
        "quantum",
        "tensor",
        "nlp",
    }


def test_engines_total():
    assert len(ENGINES) >= 90


def test_every_engine_has_fields():
    for e in ENGINES:
        assert e.id
        assert e.family
        assert e.command


def test_engines_of_known():
    assert len(engines_of("quantum")) == 6


def test_engines_of_unknown():
    with pytest.raises(KeyError, match="unknown family"):
        engines_of("wat")


def test_by_id_known():
    assert by_id("python").family == "language"


def test_by_id_unknown():
    with pytest.raises(KeyError, match="unknown engine"):
        by_id("cobol2")


# ── unified substrate ────────────────────────────────────────────────


def test_usd_prim_path():
    assert usd_prim(by_id("python")) == f"{USD_ROOT}/Language/Python"


def test_uns_path_shape():
    assert uns_path(by_id("docker")) == f"{UNS_ROOT}/Build/docker"


def test_ros_topic_shape():
    assert ros_topic(by_id("redis")) == f"{ROS_NS}/datastore/redis"


def test_ros2_profile_known():
    p = ros2_profile(by_id("python"))
    assert p["reliability"] == "reliable"
    assert p["durability"] == "transient_local"


def test_ros2_profile_every_family_covered():
    for f in families():
        assert f in ROS2_QOS


def test_ros2_profile_is_copy():
    a = ros2_profile(by_id("python"))
    a["reliability"] = "mutated"
    assert ROS2_QOS["language"]["reliability"] == "reliable"


# ── mastery ──────────────────────────────────────────────────────────


def test_engine_state_present():
    s = EngineState(by_id("python"), "/usr/bin/python3")
    assert s.present is True
    assert s.state() is PASS


def test_engine_state_absent():
    s = EngineState(by_id("python"), None)
    assert s.present is False
    assert s.state() is FAIL


def test_family_mastery_empty():
    m = FamilyMastery("x", ())
    assert m.present == 0
    assert m.total == 0
    assert m.state() is UNKNOWN


def test_family_mastery_all_present():
    m = FamilyMastery(
        "x",
        (
            EngineState(by_id("python"), "/a"),
            EngineState(by_id("rust"), "/b"),
        ),
    )
    assert m.state() is PASS


def test_family_mastery_none_present():
    m = FamilyMastery(
        "x",
        (
            EngineState(by_id("python"), None),
            EngineState(by_id("rust"), None),
        ),
    )
    assert m.state() is FAIL


def test_family_mastery_partial():
    m = FamilyMastery(
        "x",
        (
            EngineState(by_id("python"), "/a"),
            EngineState(by_id("rust"), None),
        ),
    )
    assert m.state() is UNKNOWN


def test_family_mastery_prims():
    m = FamilyMastery("language", (EngineState(by_id("python"), "/a"),))
    view = m.prims()["python"]
    assert view["usd"].startswith(USD_ROOT)
    assert view["uns"].startswith(UNS_ROOT)
    assert view["ros"].startswith(ROS_NS)
    assert view["qos"]["reliability"] == "reliable"


def test_report_empty_triad():
    r = EngineReport()
    assert r.verdict() == "UNKNOWN"


def test_report_states_and_triad():
    r = EngineReport()
    r.per_family["language"] = FamilyMastery("language", (EngineState(by_id("python"), "/a"),))
    r.per_family["build"] = FamilyMastery("build", (EngineState(by_id("docker"), "/b"),))
    assert len(r.states()) == 2
    assert r.verdict() == "PASS"


def test_resolve_all_injected():
    paths = resolve_all(lambda cmd: f"/fake/{cmd.split()[0]}")
    assert all(p is not None for p in paths.values())
    assert len(paths) == len(ENGINES)


def test_assess_all_present():
    rep = assess(lambda cmd: "/fake/bin")
    for m in rep.per_family.values():
        assert m.state() is PASS
    assert rep.verdict() == "PASS"


def test_assess_none_present():
    rep = assess(lambda cmd: None)
    for m in rep.per_family.values():
        assert m.state() is FAIL
    assert rep.verdict() == "FAIL"


def test_assess_partial():
    """Partial presence -> UNKNOWN for the populated family, FAIL elsewhere."""

    def r(cmd: str) -> str | None:
        return "/fake/bin" if cmd in ("python3", "cargo") else None

    rep = assess(r)
    assert rep.per_family["language"].state() is UNKNOWN
    assert rep.per_family["quantum"].state() is FAIL


def test_assess_default_resolver():
    rep = assess()  # uses shutil.which, whatever is on the host
    assert set(rep.per_family) == set(families())


# ── CLI ──────────────────────────────────────────────────────────────


def test_cli_atlas(capsys):
    assert main(["atlas"]) == 0
    import json as _j

    p = _j.loads(capsys.readouterr().out)
    assert p["total"] == len(ENGINES)
    assert "language" in p["families"]


def test_cli_verdict(capsys):
    assert main(["verdict"]) == 0
    assert capsys.readouterr().out.strip() in {"PASS", "FAIL", "UNKNOWN", "CONFLICT"}


def test_cli_report(capsys):
    assert main(["report"]) == 0
    import json as _j

    p = _j.loads(capsys.readouterr().out)
    assert "verdict" in p
    assert "families" in p


def test_cli_family_known(capsys):
    assert main(["family", "quantum"]) == 0
    import json as _j

    p = _j.loads(capsys.readouterr().out)
    assert p["family"] == "quantum"
    assert p["total"] == 6


def test_cli_family_unknown(capsys):
    assert main(["family", "nope"]) == 2
    assert "unknown family" in capsys.readouterr().err
