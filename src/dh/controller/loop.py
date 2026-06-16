"""The abductive controller loop — `diagnose()` (spec §6.1).

Triage → seed a hypothesis differential → repeatedly pick the single highest-VOI
action, execute it deterministically, and let the LLM interpret the result into
weighted evidence — until the leader is dominant (§6.2) or the budget runs out.
The Investigation Graph is the single source of truth: the loop writes it, appends a
per-step snapshot for the viewer, and synthesizes the final Answer from it (cause +
chain + citations, or a calibrated abstain).

Reasoning (the LLM, via `llm`) is separated from evidence (deterministic checks /
retrieval / traversal, via the `Environment`); belief aggregation and VOI are pure
code (`beliefs`, `voi`).
"""

from __future__ import annotations

import json
import logging

from dh import config
from dh.controller import beliefs, voi
from dh.controller.llm import (
    ActionProposal,
    LLMBackend,
    get_backend,
    interpret_result,
    propose_actions,
    seed_hypotheses,
    synthesize,
)
from dh.environment import Environment, NotSupported
from dh.schemas import Answer, InvestigationGraph

log = logging.getLogger("dh.loop")


# --- triage helpers ----------------------------------------------------------

def _seed_candidates(env: Environment) -> list[dict]:
    """Subsystems/parts upstream of the symptom (affects-in BFS) + their components.

    Uses only the `Environment` interface (1-hop `traverse`), composed into a bounded
    BFS — the graph's navigation role, not a full node dump.
    """
    try:
        start = env.symptom_node_id()  # type: ignore[attr-defined]
    except (NotSupported, AttributeError, KeyError):
        return []
    subsystems: dict[str, str] = {}
    visited, frontier = {start}, [start]
    for _ in range(5):  # depth bound
        nxt: list[str] = []
        for nid in frontier:
            for n in env.traverse(nid, "affects", "in"):
                if n.id in visited:
                    continue
                visited.add(n.id)
                nxt.append(n.id)
                if n.type in ("subsystem", "part_type"):
                    subsystems[n.id] = n.name
        frontier = nxt
        if not frontier:
            break
    candidates: dict[str, str] = dict(subsystems)
    for sid, _name in subsystems.items():  # drill subsystem → its part_types (BOM)
        for p in env.traverse(sid, "part_of", "in"):
            candidates[p.id] = p.name
    return [{"id": i, "name": n} for i, n in candidates.items()]


def _playbook_text(env: Environment) -> str | None:
    try:
        hits = env.search("playbook differential diagnosing range degradation", k=2)
    except NotSupported:
        return None
    for a in hits:
        if a.kind in ("procedure", "doc", "domain_doc"):
            return a.text
    return hits[0].text if hits else None


def _action_menu(env: Environment) -> list[str]:
    if "run_check" in env.capabilities() and hasattr(env, "list_checks"):
        return list(env.list_checks())  # type: ignore[attr-defined]
    return []


# --- execution ---------------------------------------------------------------

def _execute(env: Environment, a: ActionProposal) -> dict:
    """Run an action deterministically; failures return an `error` result, not a crash."""
    try:
        if a.type == "run_check":
            return env.run_check(a.args.get("name", ""), a.args)
        if a.type == "traverse":
            nodes = env.traverse(a.args["node_id"], a.args["edge_type"],
                                 a.args.get("direction", "out"))
            return {"neighbors": [n.model_dump() for n in nodes]}
        if a.type == "search":
            hits = env.search(a.args.get("query", ""), a.args.get("k", 5))
            return {"results": [{"id": h.id, "kind": h.kind, "text": h.text} for h in hits]}
        if a.type == "recommend_swap_test":
            # an untried diagnostic action has no timestamp (it hasn't happened yet)
            untried = [x for x in env.read_diagnostic_actions() if x.timestamp is None]
            rec = untried[0].text if untried else "Recommend a discriminating swap-test."
            return {"recommended": rec, "status": "recommended"}
    except (NotSupported, KeyError, ValueError) as e:
        log.warning("action %s failed: %s", a.type, e)
        return {"error": str(e)}
    return {"error": f"unknown action type {a.type}"}


def _snapshot(ig: InvestigationGraph) -> None:
    """Append a deep copy of the IG *without* its snapshots (avoids O(n²) nesting)."""
    ig.snapshots.append(ig.model_copy(deep=True, update={"snapshots": []}))


def _action_key(a: ActionProposal) -> str:
    return f"{a.type}:{json.dumps(a.args, sort_keys=True)}"


def _should_conclude(ig: InvestigationGraph, th: dict) -> bool:
    _top, conf, margin = beliefs.leader(ig)
    return conf > th["tau_dom"] and margin > th["tau_margin"]


# --- the loop ----------------------------------------------------------------

def diagnose(
    env: Environment,
    backend: LLMBackend | None = None,
    budget: int | None = None,
    prior: float = 0.0,
) -> Answer:
    """Run the abductive loop on `env` and return the final Answer (spec §6.1)."""
    backend = backend or get_backend()
    if backend is None:
        raise RuntimeError("no LLM backend available (set a key, install the claude CLI, "
                           "or pass a ScriptedBackend)")
    th = config.thresholds()
    budget = budget if budget is not None else config.budget()
    cost_table = voi.costs()

    known_ids = env.node_ids() if hasattr(env, "node_ids") else None  # type: ignore[attr-defined]

    ig = InvestigationGraph(symptom=env.symptom())
    ig.hypotheses = seed_hypotheses(backend, ig.symptom, _seed_candidates(env),
                                    _playbook_text(env))
    beliefs.update_beliefs(ig, prior)
    _snapshot(ig)

    seen: set[str] = set()
    recommended = False
    for _step in range(budget):
        proposals = [a for a in propose_actions(backend, ig, _action_menu(env),
                                                env.capabilities())
                     if _action_key(a) not in seen
                     and not (recommended and a.type == "recommend_swap_test")]
        best = voi.select(proposals, cost_table)
        if best is None:
            log.info("no new actions proposed; stopping early")
            break
        seen.add(_action_key(best))
        result = _execute(env, best)
        ev, links, conflicts = interpret_result(backend, ig, best, result)
        if ev:
            ig.evidence.append(ev)
            ig.links.extend(links)
        for c in conflicts:
            if known_ids is not None and c not in known_ids:
                continue  # drop hallucinated conflict ids; keep real node/signal ids
            if c not in ig.conflicts:
                ig.conflicts.append(c)
        recommended = recommended or best.type == "recommend_swap_test"
        if best.type == "recommend_swap_test":
            ig.recommended_action = result.get("recommended") or ig.recommended_action
        beliefs.update_beliefs(ig, prior)
        _snapshot(ig)
        if _should_conclude(ig, th):
            log.info("conclude condition met at step %d", _step)
            break

    _top, conf, _margin = beliefs.leader(ig)
    abstain = conf <= th["tau_min"]
    answer = synthesize(backend, ig, abstain=abstain)
    ig.status = "abstained" if answer.answer_type == "abstain" else "concluded"
    ig.recommended_action = answer.recommended_action or ig.recommended_action
    _snapshot(ig)
    return answer
