# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""USD / UNS / ROS / ROS2 — four substrates over one engine atlas.

Every engine has:
    a USD prim path (composition, layers, opinions)
    a UNS path (industrial namespace, topic tree)
    a ROS topic (pub/sub)
    a ROS2 QoS profile (reliability + durability)
"""

from __future__ import annotations

from tmig_closure.mastery_engines.atlas import Engine

USD_ROOT = "/World/Engines"
UNS_ROOT = "Enterprise/Engines"
ROS_NS = "/engines"

ROS2_QOS: dict[str, dict[str, str]] = {
    "language": {"reliability": "reliable", "durability": "transient_local"},
    "format": {"reliability": "reliable", "durability": "transient_local"},
    "build": {"reliability": "reliable", "durability": "volatile"},
    "package": {"reliability": "reliable", "durability": "volatile"},
    "datastore": {"reliability": "reliable", "durability": "transient_local"},
    "ai": {"reliability": "best_effort", "durability": "volatile"},
    "quantum": {"reliability": "reliable", "durability": "transient_local"},
    "tensor": {"reliability": "reliable", "durability": "transient_local"},
    "nlp": {"reliability": "reliable", "durability": "volatile"},
}


def _cap(s: str) -> str:
    """Capitalize first letter only."""
    return s[:1].upper() + s[1:]


def usd_prim(engine: Engine) -> str:
    """Return the USD prim path for an engine."""
    return f"{USD_ROOT}/{_cap(engine.family)}/{_cap(engine.id)}"


def uns_path(engine: Engine) -> str:
    """Return the UNS path for an engine."""
    return f"{UNS_ROOT}/{_cap(engine.family)}/{engine.id}"


def ros_topic(engine: Engine) -> str:
    """Return the ROS topic for an engine."""
    return f"{ROS_NS}/{engine.family}/{engine.id}"


def ros2_profile(engine: Engine) -> dict[str, str]:
    """Return the ROS2 QoS profile for an engine's family."""
    return dict(ROS2_QOS[engine.family])
