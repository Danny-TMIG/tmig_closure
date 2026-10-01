"""HTTP surface for the closure kernel."""

from __future__ import annotations

import os
from collections.abc import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tmig_closure import __version__
from tmig_closure.agents import Agent, run_to_fixpoint, step
from tmig_closure.core import ClosureError, immediate_consequence
from tmig_closure.logging_config import configure
from tmig_closure.symmetry import canonical, count_vector, orbit_key

configure()

MAX_STEPS = int(os.environ.get("TMIG_MAX_STEPS", "10000"))


class RuleModel(BaseModel):
    premises: list[str] = Field(default_factory=list)
    conclusions: list[str] = Field(default_factory=list)


class ClosureRequest(BaseModel):
    config: list[str]
    rules: list[RuleModel]
    max_steps: int = Field(default=MAX_STEPS, ge=1, le=1_000_000)


class ClosureResponse(BaseModel):
    closure: list[str]
    added: list[str]
    iterations: int


class AgentModel(BaseModel):
    id: str
    config: list[str]


class StepRequest(BaseModel):
    agents: list[AgentModel]
    rules: list[RuleModel]


class RunRequest(StepRequest):
    max_steps: int = Field(default=MAX_STEPS, ge=1, le=1_000_000)


class AgentsResponse(BaseModel):
    agents: list[AgentModel]


class SymmetryRequest(BaseModel):
    items: list[str]
    alphabet: list[str] | None = None


class SymmetryResponse(BaseModel):
    canonical: list[str]
    orbit_key: list[list[object]]
    count_vector: list[int] | None = None


def _to_rules(models: Iterable[RuleModel]) -> list[tuple[frozenset[str], frozenset[str]]]:
    return [(frozenset(m.premises), frozenset(m.conclusions)) for m in models]


def _iterate_count(
    config: frozenset[str],
    rules: list[tuple[frozenset[str], frozenset[str]]],
    max_steps: int,
) -> tuple[frozenset[str], int]:
    cur = config
    for i in range(max_steps):
        nxt = immediate_consequence(cur, rules)
        if nxt == cur:
            return cur, i
        cur = nxt
    raise ClosureError(f"no closure within {max_steps} steps")


app = FastAPI(
    title="tmig_closure",
    version=__version__,
    description="Deterministic closure kernel for capability composition.",
    license_info={"name": "MIT"},
)

_origins = [o.strip() for o in os.environ.get("TMIG_CORS_ORIGINS", "").split(",") if o.strip()]
if _origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["content-type"],
    )


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["meta"])
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/version", tags=["meta"])
def version() -> dict[str, str]:
    return {
        "version": __version__,
        "commit": os.environ.get("TMIG_BUILD_COMMIT", "dev"),
        "built_at": os.environ.get("TMIG_BUILD_TIME", "unknown"),
    }


@app.post("/closure", response_model=ClosureResponse, tags=["closure"])
def closure(req: ClosureRequest) -> ClosureResponse:
    try:
        rules = _to_rules(req.rules)
        start = frozenset(req.config)
        result, iters = _iterate_count(start, rules, req.max_steps)
    except ClosureError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return ClosureResponse(
        closure=sorted(result),
        added=sorted(result - start),
        iterations=iters,
    )


@app.post("/agents/step", response_model=AgentsResponse, tags=["agents"])
def agents_step(req: StepRequest) -> AgentsResponse:
    rules = _to_rules(req.rules)
    agents = [Agent(a.id, frozenset(a.config)) for a in req.agents]
    out = step(agents, rules)
    return AgentsResponse(agents=[AgentModel(id=a.id, config=sorted(a.config)) for a in out])


@app.post("/agents/run", response_model=AgentsResponse, tags=["agents"])
def agents_run(req: RunRequest) -> AgentsResponse:
    rules = _to_rules(req.rules)
    agents = [Agent(a.id, frozenset(a.config)) for a in req.agents]
    try:
        out = run_to_fixpoint(agents, rules, max_steps=req.max_steps)
    except ClosureError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return AgentsResponse(agents=[AgentModel(id=a.id, config=sorted(a.config)) for a in out])


@app.post("/symmetry/canonical", response_model=SymmetryResponse, tags=["symmetry"])
def symmetry_canonical(req: SymmetryRequest) -> SymmetryResponse:
    cv: list[int] | None = None
    if req.alphabet is not None:
        cv = list(count_vector(req.items, req.alphabet))
    return SymmetryResponse(
        canonical=list(canonical(req.items)),
        orbit_key=[[k, v] for k, v in orbit_key(req.items)],
        count_vector=cv,
    )
