# SPDX-License-Identifier: MIT
# Copyright (c) 2026 The Mark Intelligence Group
"""The mastery atlas: per-language competency catalogs.

Each competency carries a regex that, when matched against a source file,
proves the file *uses* that feature. Mastery is the fold over the
competencies a project exercises.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Competency:
    """One mastery competency: an id, a human title, and a usage regex."""

    id: str
    title: str
    pattern: re.Pattern[str]


def _c(cid: str, title: str, pattern: str) -> Competency:
    """Build a Competency with a compiled regex (MULTILINE for ^ anchors)."""
    return Competency(cid, title, re.compile(pattern, re.MULTILINE))


@dataclass(frozen=True, slots=True)
class Language:
    """One language: extensions that identify it and its competency catalog."""

    id: str
    title: str
    extensions: tuple[str, ...]
    competencies: tuple[Competency, ...]


ATLAS: tuple[Language, ...] = (
    Language(
        id="python",
        title="Python",
        extensions=(".py", ".pyi"),
        competencies=(
            _c(
                "py-typing",
                "type annotations",
                r"->\s*\w|:\s*(?:int|str|float|bool|list|dict|set|tuple|Optional|Union|Iterable|Sequence)",
            ),
            _c("py-async", "async/await", r"\basync\s+def\b|\bawait\b"),
            _c(
                "py-context",
                "context managers",
                r"\bwith\s+\w|\bcontextmanager\b|__enter__|__exit__",
            ),
            _c("py-generators", "generators", r"\byield\b"),
            _c("py-decorators", "decorators", r"^\s*@\w"),
            _c("py-dataclass", "dataclasses", r"\bdataclass\b"),
            _c("py-slots", "slots", r"__slots__|slots=True"),
            _c(
                "py-comprehension",
                "comprehensions",
                r"\[[^\]]+\bfor\b|\([^\)]+\bfor\b|\{[^\}]+\bfor\b",
            ),
            _c("py-match", "structural pattern matching", r"^\s*match\s+\w+.*:\s*$"),
            _c("py-fstring", "f-strings", r"\bf['\"]"),
            _c("py-proto", "protocols/ABCs", r"\bProtocol\b|\bABC\b|\babstractmethod\b"),
            _c("py-enum", "enumerations", r"\bEnum\b|\bStrEnum\b|\bIntEnum\b"),
        ),
    ),
    Language(
        id="shell",
        title="Shell",
        extensions=(".sh", ".bash", ".zsh", ".ksh"),
        competencies=(
            _c("sh-strict", "strict mode", r"set\s+-[eux]|set\s+-o\s+(?:errexit|nounset|pipefail)"),
            _c("sh-func", "functions", r"^\s*\w+\s*\(\)\s*\{|^\s*function\s+\w+"),
            _c("sh-array", "arrays", r"\(\s*[\"']?\w+|\[\@\]|\[\*\]"),
            _c("sh-cond", "conditionals", r"\bif\s+\[\[|\bcase\b|\belif\b"),
            _c("sh-loop", "loops", r"\bfor\s+\w+\s+in\b|\bwhile\s+"),
            _c("sh-heredoc", "here-documents", r"<<-?['\"]?\w+"),
            _c("sh-subst", "command substitution", r"\$\(|`"),
            _c("sh-param-exp", "parameter expansion", r"\$\{\w+[:#%/]"),
            _c("sh-trap", "signal traps", r"\btrap\b"),
            _c("sh-pipe", "pipelines", r"\|\s*\w+"),
        ),
    ),
    Language(
        id="typescript",
        title="TypeScript",
        extensions=(".ts", ".tsx", ".mts", ".cts"),
        competencies=(
            _c("ts-interface", "interfaces", r"\binterface\s+\w+"),
            _c("ts-type", "type aliases", r"\btype\s+\w+\s*="),
            _c("ts-generic", "generics", r"<\s*[A-Z]\w*(?:\s*,\s*[A-Z]\w*)*\s*>"),
            _c("ts-union", "union/intersection types", r"\w+\s*\|\s*\w+|\w+\s*&\s*\w+"),
            _c("ts-async", "async/await", r"\basync\b|\bawait\b"),
            _c("ts-promise", "promises", r"\bPromise<|\bPromise\.|\.then\("),
            _c("ts-optional", "optional chaining", r"\?\."),
            _c("ts-nullish", "nullish coalescing", r"\?\?"),
            _c("ts-const-assert", "const assertions", r"\bas\s+const\b"),
            _c("ts-enum", "enums", r"\benum\s+\w+"),
            _c("ts-decorator", "decorators", r"^\s*@\w"),
            _c("ts-satisfies", "satisfies operator", r"\bsatisfies\b"),
        ),
    ),
    Language(
        id="javascript",
        title="JavaScript",
        extensions=(".js", ".jsx", ".mjs", ".cjs"),
        competencies=(
            _c("js-arrow", "arrow functions", r"=>"),
            _c("js-destructure", "destructuring", r"(?:const|let|var)\s*[\{\[]"),
            _c("js-spread", "spread/rest", r"\.\.\."),
            _c("js-template", "template literals", r"`[^`]*\$\{"),
            _c("js-async", "async/await", r"\basync\b|\bawait\b"),
            _c("js-promise", "promises", r"\bPromise\b|\.then\("),
            _c("js-class", "classes", r"\bclass\s+\w+"),
            _c("js-module", "ES modules", r"^\s*(?:import|export)\s"),
            _c("js-optional", "optional chaining", r"\?\."),
            _c("js-nullish", "nullish coalescing", r"\?\?"),
            _c("js-generator", "generators", r"\bfunction\s*\*|\byield\b"),
        ),
    ),
    Language(
        id="mermaid",
        title="Mermaid",
        extensions=(".mmd", ".mermaid"),
        competencies=(
            _c("mm-flow", "flowcharts", r"^\s*(?:graph|flowchart)\s+(?:TD|TB|BT|LR|RL)"),
            _c("mm-seq", "sequence diagrams", r"^\s*sequenceDiagram\b"),
            _c("mm-class", "class diagrams", r"^\s*classDiagram\b"),
            _c("mm-state", "state diagrams", r"^\s*stateDiagram"),
            _c("mm-er", "ER diagrams", r"^\s*erDiagram\b"),
            _c("mm-gantt", "gantt charts", r"^\s*gantt\b"),
            _c("mm-pie", "pie charts", r"^\s*pie\b"),
            _c("mm-git", "git graphs", r"^\s*gitGraph\b"),
            _c("mm-subgraph", "subgraphs", r"^\s*subgraph\b"),
            _c("mm-style", "styling/classDef", r"\bclassDef\b|\bstyle\s+\w+|\bclick\b"),
        ),
    ),
    Language(
        id="codeql",
        title="CodeQL",
        extensions=(".ql", ".qll"),
        competencies=(
            _c("ql-from", "from/where/select", r"^\s*from\b.*\bwhere\b.*\bselect\b"),
            _c("ql-class", "predicate classes", r"^\s*(?:abstract\s+)?class\s+\w+"),
            _c("ql-pred", "predicates", r"^\s*(?:predicate|member predicate)\s+\w+"),
            _c("ql-import", "imports", r"^\s*import\s+\w"),
            _c("ql-exists", "existential quantification", r"\bexists\s*\("),
            _c(
                "ql-agg",
                "aggregations",
                r"\bcount\s*\(|\bsum\s*\(|\bmin\s*\(|\bmax\s*\(|\bavg\s*\(",
            ),
            _c("ql-recursion", "recursive predicates", r"\)\s*\{[^}]*\b\w+\s*\("),
            _c("ql-module", "modules", r"^\s*module\s+\w+"),
            _c("ql-newtype", "newtypes", r"^\s*newtype\s+\w+"),
            _c("ql-dataclass", "dataclasses", r"^\s*dataclass\b"),
        ),
    ),
    Language(
        id="other",
        title="Other",
        extensions=(),
        competencies=(_c("other-source", "source files", r"\S"),),
    ),
)


def languages() -> tuple[str, ...]:
    """Return every language id, in atlas order."""
    return tuple(lang.id for lang in ATLAS)


def _index() -> dict[str, Language]:
    return {lang.id: lang for lang in ATLAS}


def by_id(language_id: str) -> Language:
    """Look up a language by id. Raises KeyError if unknown."""
    idx = _index()
    if language_id not in idx:
        raise KeyError(f"unknown language: {language_id!r}")
    return idx[language_id]
