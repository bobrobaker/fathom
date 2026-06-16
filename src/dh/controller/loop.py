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
from dh.schemas import Answer, EvidenceItem, InvestigationGraph

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
            if p.type in ("part_type", "part_version"):  # not config (those part_of a subsystem too)
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
    """Append a deep copy of the IG *without* its snapshots/trace (avoids O(n²) nesting)."""
    ig.snapshots.append(ig.model_copy(deep=True, update={"snapshots": [], "trace": []}))


def _trace_step(ig: InvestigationGraph, *, action: str, args: dict | None, rationale: str,
                voi: float, evidence_id: str | None, conflicts_added: list[str]) -> None:
    """Record what the step did + the resulting differential — the viewer's reasoning panel
    (spec §3.3 / fathom_visualizer_spec §2). Aligned by index with `snapshots`."""
    top, conf, margin = beliefs.leader(ig)
    ig.trace.append({
        "action": action, "args": args or {}, "rationale": rationale, "voi": round(voi, 3),
        "evidence_id": evidence_id, "conflicts_added": conflicts_added,
        "leader": top.id if top else None, "leader_conf": round(conf, 3),
        "margin": round(margin, 3),
        "confidences": {h.id: round(beliefs.confidence(h), 3) for h in ig.hypotheses},
    })


def _action_key(a: ActionProposal) -> str:
    return f"{a.type}:{json.dumps(a.args, sort_keys=True)}"


def _should_conclude(ig: InvestigationGraph, th: dict) -> bool:
    _top, conf, margin = beliefs.leader(ig)
    return conf > th["tau_dom"] and margin > th["tau_margin"]


def _signal_to_metric_id(env: Environment, signal: str) -> str:
    """Map a telemetry signal to its metric/KPI node id (so a flagged channel lands in the
    same id-space the eval canonicalises to); fall back to the raw signal name."""
    if not hasattr(env, "_case"):
        return signal
    for n in env._case.graph.nodes:  # type: ignore[attr-defined]
        if n.type in ("metric", "KPI") and n.props.get("signal") == signal:
            return n.id
    return signal


def _finalize_conflicts(ig: InvestigationGraph, env: Environment, known_ids) -> None:
    """The controller's structural thoroughness (spec §6.5 playbook): before finalizing, run the
    two deterministic discriminators a complete diagnosis always owes — order the degradation
    onset against the *most salient recent event* (demote it iff the onset predates it, D1), and
    sanity-check every channel for a stuck/lying sensor (B5). These are deterministic conclusions
    of deterministic checks, so they are flagged mechanically (no LLM). General by construction:
    no recent event / no stuck channel ⇒ no-op; a recent change that IS the cause (onset aligns,
    not predates) is correctly NOT demoted. This is the conflict-surfacing the bare baselines
    structurally lack — never a tuning of cases or scoring (non-negotiable #5)."""
    if "run_check" not in env.capabilities():
        return

    def _note(cid: str, evid: str, summary: str) -> None:
        if known_ids is not None and cid not in known_ids:
            return
        if cid not in ig.conflicts:
            ig.conflicts.append(cid)
        if not any(e.id == evid for e in ig.evidence):
            ig.evidence.append(EvidenceItem(id=evid, summary=summary, source="onset_vs_event_check"
                                            if evid.startswith("ev.trigger") else "channel_sanity_check"))

    # 1) demote the most salient recent event if the degradation predates it
    try:
        logs = [a for a in env.read_logbook() if a.timestamp is not None]
    except NotSupported:
        logs = []
    if logs:
        latest = max(logs, key=lambda a: a.timestamp)
        try:
            r = env.run_check("onset_vs_event_check", {"event_id": latest.id})
            if r.get("onset_predates_event"):
                _note(latest.id, "ev.trigger_demoted",
                      f"{latest.id}: degradation onset predates it → coincident, not causal")
        except (NotSupported, KeyError, ValueError):
            pass

    # 2) flag any stuck/lying channel
    try:
        signals = env.list_signals()
    except NotSupported:
        signals = []
    for sig in signals:
        try:
            r = env.run_check("channel_sanity_check", {"signal": sig})
        except (NotSupported, KeyError, ValueError):
            continue
        if r.get("stuck"):
            mid = _signal_to_metric_id(env, sig)
            _note(mid, f"ev.stuck_{sig}", f"{sig} is stuck (≈zero variance) → unreliable channel")


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
    _trace_step(ig, action="seed", args=None, rationale="seed the differential from the symptom",
                voi=0.0, evidence_id=None, conflicts_added=[])

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
        added: list[str] = []
        for c in conflicts:
            if known_ids is not None and c not in known_ids:
                continue  # drop hallucinated conflict ids; keep real node/signal ids
            if c not in ig.conflicts:
                ig.conflicts.append(c)
                added.append(c)
        recommended = recommended or best.type == "recommend_swap_test"
        if best.type == "recommend_swap_test":
            ig.recommended_action = result.get("recommended") or ig.recommended_action
        beliefs.update_beliefs(ig, prior)
        _snapshot(ig)
        _trace_step(ig, action=best.type, args=best.args, rationale=best.rationale,
                    voi=voi.voi(best, cost_table), evidence_id=ev.id if ev else None,
                    conflicts_added=added)
        if _should_conclude(ig, th):
            log.info("conclude condition met at step %d", _step)
            break

    conflicts_before = set(ig.conflicts)
    _finalize_conflicts(ig, env, known_ids)  # structural conflict sweep before synthesis (§6.5)
    _snapshot(ig)
    _trace_step(ig, action="conflict_sweep", args=None,
                rationale="order onset vs the salient recent event; sanity-check channels",
                voi=0.0, evidence_id=None,
                conflicts_added=[c for c in ig.conflicts if c not in conflicts_before])

    _top, conf, _margin = beliefs.leader(ig)
    abstain = conf <= th["tau_min"]
    answer = synthesize(backend, ig, abstain=abstain)
    ig.status = "abstained" if answer.answer_type == "abstain" else "concluded"
    ig.recommended_action = answer.recommended_action or ig.recommended_action
    _snapshot(ig)
    _trace_step(ig, action="synthesize",
                args={"answer_type": answer.answer_type, "root_cause": answer.root_cause},
                rationale="conclude or abstain from the differential", voi=0.0,
                evidence_id=None, conflicts_added=[])
    return answer
