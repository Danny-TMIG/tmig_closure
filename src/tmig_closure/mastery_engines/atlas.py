# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""The engine atlas — every binary in the stack, classified by family."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Engine:
    """One engine: an id, its family, the command that proves it exists."""

    id: str
    family: str
    command: str


@dataclass(frozen=True, slots=True)
class Family:
    """A family of engines sharing a namespace prefix."""

    id: str
    title: str


FAMILIES: tuple[Family, ...] = (
    Family("language", "Languages"),
    Family("format", "Data Formats"),
    Family("build", "Build Systems"),
    Family("package", "Package Managers"),
    Family("datastore", "Datastores"),
    Family("ai", "AI / ML"),
    Family("quantum", "Quantum"),
    Family("tensor", "Tensor / Numeric"),
    Family("nlp", "NLP"),
)


_RAW: dict[str, list[tuple[str, str]]] = {
    "language": [
        ("python", "python3"),
        ("rust", "cargo"),
        ("go", "go"),
        ("swift", "swiftc"),
        ("node", "node"),
        ("perl", "perl"),
        ("ruby", "ruby"),
        ("php", "php"),
        ("java", "javac"),
        ("kotlin", "kotlinc"),
        ("scala", "scalac"),
        ("groovy", "groovyc"),
        ("c", "clang"),
        ("cpp", "clang++"),
        ("fortran", "gfortran"),
        ("haskell", "ghc"),
        ("erlang", "erlc"),
        ("elixir", "elixirc"),
        ("lua", "lua"),
        ("tcl", "tclsh"),
        ("r", "Rscript"),
        ("julia", "julia"),
        ("bash", "bash"),
        ("zsh", "zsh"),
        ("powershell", "pwsh"),
        ("dotnet", "dotnet"),
        ("dart", "dart"),
        ("typescript", "tsc"),
        ("objectivec", "clang"),
        ("ocaml", "ocamlopt"),
        ("nim", "nim"),
        ("zig", "zig"),
        ("crystal", "crystal"),
        ("wasm", "wasm-pack"),
        ("cuda", "nvcc"),
        ("opencl", "clang"),
        ("verilog", "iverilog"),
        ("vhdl", "ghdl"),
        ("matlab", "matlab"),
        ("wolfram", "wolframscript"),
        ("smalltalk", "gst"),
        ("prolog", "swipl"),
        ("clojure", "clj"),
        ("scheme", "guile"),
        ("commonlisp", "sbcl"),
        ("fsharp", "fsharpc"),
        ("reasonml", "rebuild"),
        ("ada", "gnatmake"),
        ("pascal", "fpc"),
        ("cobol", "cobc"),
        ("assembly", "nasm"),
        ("ml", "ocaml"),
    ],
    "format": [
        ("jsonnet", "jsonnet"),
        ("yaml", "yq"),
        ("graphql", "graphql"),
        ("sql", "sqlite3"),
        ("nosql", "mongo"),
    ],
    "build": [
        ("docker", "docker"),
        ("kubernetes", "kubectl"),
        ("terraform", "terraform"),
        ("ansible", "ansible-playbook"),
        ("nix", "nix-build"),
        ("bazel", "bazel"),
        ("make", "make"),
        ("cmake", "cmake"),
        ("gradle", "gradle"),
        ("maven", "mvn"),
    ],
    "package": [
        ("poetry", "poetry"),
        ("pip", "pip"),
        ("conda", "conda"),
        ("npm", "npm"),
        ("pnpm", "pnpm"),
        ("yarn", "yarn"),
        ("composer", "composer"),
    ],
    "datastore": [
        ("helm", "helm"),
        ("ipfs", "ipfs"),
        ("nats", "nats-server"),
        ("redis", "redis-server"),
        ("postgres", "psql"),
        ("mysql", "mysql"),
        ("sqlite", "sqlite3"),
        ("mongodb", "mongod"),
        ("influxdb", "influxd"),
        ("grafana", "grafana-server"),
        ("prometheus", "prometheus"),
    ],
    "ai": [
        ("openai", "openai"),
        ("huggingface", "transformers-cli"),
        ("torch", "python3 -m torch.utils.collect_env"),
        ("tensorflow", "python3 -c 'import tensorflow as tf;print(tf.__version__)'"),
        ("jax", "python3 -c 'import jax;print(jax.__version__)'"),
        ("onnx", "onnxruntime"),
        ("mlflow", "mlflow"),
        ("ray", "ray"),
        ("langchain", "python3 -m langchain"),
        ("autogen", "python3 -m autogen"),
    ],
    "quantum": [
        ("quantum_qiskit", "python3 -m qiskit"),
        ("quantum_cirq", "python3 -m cirq"),
        ("quantum_braket", "braket"),
        ("quantum_ionq", "ionq"),
        ("quantum_qsharp", "dotnet run --project qsharp"),
        ("quantum_xanadu", "python3 -m pennylane"),
    ],
    "tensor": [
        ("tensors", "python3 -c 'import torch, tensorflow; print(\"tensors ok\")'"),
    ],
    "nlp": [
        ("nltk", "python3 -m nltk.downloader punkt"),
    ],
}


def _build() -> tuple[Engine, ...]:
    out: list[Engine] = []
    for fam, rows in _RAW.items():
        for eid, cmd in rows:
            out.append(Engine(id=eid, family=fam, command=cmd))
    return tuple(out)


ENGINES: tuple[Engine, ...] = _build()


def families() -> tuple[str, ...]:
    """Every family id in atlas order."""
    return tuple(f.id for f in FAMILIES)


def engines_of(family: str) -> tuple[Engine, ...]:
    """Return all engines in a family, or raise KeyError."""
    if family not in families():
        raise KeyError(f"unknown family: {family!r}")
    return tuple(e for e in ENGINES if e.family == family)


def by_id(engine_id: str) -> Engine:
    """Look up an engine by id, or raise KeyError."""
    for e in ENGINES:
        if e.id == engine_id:
            return e
    raise KeyError(f"unknown engine: {engine_id!r}")
