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
from dh.schemas import Answer, EvidenceItem, EvidenceLink, InvestigationGraph

# Deterministic weight for the change-is-cause promotion (mirrors the demote side). Sized like a
# strong-but-not-saturating discriminator (≈ one concordant LLM item, |LLR|≈1.5) so it makes a
# genuinely-aligned change the leader without pinning it past the MAX_LOG_ODDS clamp on its own.
CHANGE_CAUSE_WEIGHT = 1.5

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


_CM_PROMOTE_WEIGHT = 1.5    # |LLR| for the shared upstream cause (≈7× odds; clears τ_dom with margin)
_CM_DECOY_WEIGHT = 0.8      # |LLR| against each surface decoy (common-mode argues against indep faults)


def _affects_ancestors(case, node_id: str) -> set[str]:
    """Upstream subsystems reachable by walking `affects` edges inward from `node_id`."""
    aff_in: dict[str, list[str]] = {}
    for e in case.graph.edges:
        if e.type == "affects":
            aff_in.setdefault(e.dst, []).append(e.src)
    seen: set[str] = set()
    stack = list(aff_in.get(node_id, []))
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        stack.extend(aff_in.get(x, []))
    return seen


def _promote_common_mode(ig: InvestigationGraph, env: Environment, known_ids) -> None:
    """Deterministic PROMOTION, symmetric to the demotion sweep (fixes the M3 asymmetry, M2 gap).

    The demotion sweep can only knock a salient event/channel down; nothing ever credits *the
    shared upstream cause* of a common-mode failure, so on `salient_is_cause` common-mode cases
    the surface decoys win the belief math. This routine closes that gap structurally:

      1. `common_mode_check` reports `common_mode=true` (≥2 nominally-independent channels degrade
         with a clustered onset — one cause hit them all, not several independent faults).
      2. Map each *moved* channel (≥5% baseline→recent, same rule the check uses) to the subsystem
         that `measured_by` it; require ≥2 distinct degraded subsystems (a real single-subsystem
         fault, e.g. laser aging, is correctly excluded — it owns only one).
      3. In the graph's own `affects` DAG, find the subsystems upstream of *all* degraded ones
         (their common ancestors) — the convergence points a single upstream cause could occupy.
      4. Among those, promote the one with a *recently-changed config* `part_of` it (config_diff +
         the graph's part_of topology). Requiring a concrete recent change disambiguates which
         common ancestor is the cause and prevents a spurious promotion when no upstream change
         exists. Add a POSITIVE belief link to the hypothesis on that subsystem and NEGATIVE links
         to the surface decoys (common-mode is evidence *against* the independent-fault reading).

    General by construction: it fires only on the structural common-mode signature and reads the
    cause off the case's own affects/part_of topology + config_diff — no case names, no per-case
    constants. No common-mode signal, or no recently-changed upstream config ⇒ no-op. This is the
    promotion the demotion-only layer structurally lacked — not a tuning of cases/scoring (#5).
    """
    if "run_check" not in env.capabilities() or not hasattr(env, "_case"):
        return
    case = env._case  # type: ignore[attr-defined]
    try:
        cm = env.run_check("common_mode_check", {})
    except (NotSupported, KeyError, ValueError):
        return
    if not cm.get("common_mode"):
        return

    # (2) moved channels → degraded subsystems (direct `measured_by` ownership only)
    try:
        signals = env.list_signals()
    except NotSupported:
        return
    moved_metrics: set[str] = set()
    sig2metric = {n.props.get("signal"): n.id for n in case.graph.nodes
                  if n.props.get("signal")}
    for sig in signals:
        try:
            ts = env.query_telemetry(sig)
        except (NotSupported, KeyError, ValueError):
            continue
        if len(ts.v) < 6:
            continue
        base = sum(ts.v[:3]) / 3.0
        recent = sum(ts.v[-3:]) / 3.0
        if base and abs(recent - base) / abs(base) >= 0.05 and sig in sig2metric:
            moved_metrics.add(sig2metric[sig])
    deg_subs = {e.src for e in case.graph.edges
                if e.type == "measured_by" and e.dst in moved_metrics
                and e.src.startswith("sub.")}
    if len(deg_subs) < 2:
        return

    # (3) common upstream ancestors of every degraded subsystem
    common: set[str] | None = None
    for ds in deg_subs:
        anc = _affects_ancestors(case, ds) | {ds}
        common = anc if common is None else (common & anc)
    common = {c for c in (common or set()) if c.startswith("sub.")}
    if not common:
        return

    # (4) the common ancestor with a recently-changed config part_of it
    try:
        changed = {ch["key"] for ch in env.run_check("config_diff", {}).get("changed", [])}
    except (NotSupported, KeyError, ValueError):
        changed = set()
    if not changed:
        return
    cfg_subsys = {e.src: e.dst for e in case.graph.edges
                  if e.type == "part_of" and e.src.startswith("config.")}
    changed_cfg = {n.id for n in case.graph.nodes if n.type == "config" and n.name in changed}
    promoted = {cfg_subsys[c] for c in changed_cfg
                if cfg_subsys.get(c) in common}
    promoted = {p for p in promoted if p not in deg_subs}  # the cause is upstream, not a victim
    if not promoted:
        return

    # add a real EvidenceItem + belief links so the promotion enters log_odds (not just text)
    ev_id = "ev.common_mode"
    if not any(e.id == ev_id for e in ig.evidence):
        ig.evidence.append(EvidenceItem(
            id=ev_id, source="common_mode_check",
            summary=cm.get("summary", "common-mode signature: one upstream cause, not independent faults")))
    target_subs = promoted
    for h in ig.hypotheses:
        if h.node_ref in target_subs:
            if not any(ln.evidence_id == ev_id and ln.hypothesis_id == h.id for ln in ig.links):
                ig.links.append(EvidenceLink(evidence_id=ev_id, hypothesis_id=h.id,
                                             polarity="+", weight=_CM_PROMOTE_WEIGHT))
        elif h.node_ref in deg_subs:  # the surface decoys the common-mode reading argues against
            if not any(ln.evidence_id == ev_id and ln.hypothesis_id == h.id for ln in ig.links):
                ig.links.append(EvidenceLink(evidence_id=ev_id, hypothesis_id=h.id,
                                             polarity="-", weight=_CM_DECOY_WEIGHT))


def _change_cause_subsystem(env: Environment, event_id: str) -> str | None:
    """If `event_id` is a logbook event that references a config node which *genuinely changed*
    (the key appears in `config_diff.changed`), return the subsystem that config is `part_of` —
    i.e. the subsystem a real, recent change implicates. Else None.

    Structural, not nominal: the path is `event --references--> config --part_of--> subsystem`,
    and the change is confirmed by the same deterministic `config_diff` the controller already
    runs. A service/inspection log that references a subsystem but changed no config returns None
    (no config_diff entry), so this fires only on an actual change."""
    if not hasattr(env, "_case"):
        return None
    try:
        changed = {c.get("key") for c in env.run_check("config_diff", {}).get("changed", [])}
    except (NotSupported, KeyError, ValueError):
        return None
    if not changed:
        return None
    referenced = [e.dst for e in env._case.graph.edges  # type: ignore[attr-defined]
                  if e.src == event_id and e.type == "references"]
    cfg_by_id = {n.id: n for n in env._case.graph.nodes if n.type == "config"}  # type: ignore[attr-defined]
    for cid in referenced:
        cfg = cfg_by_id.get(cid)
        if cfg is None or cfg.name not in changed:
            continue
        for e in env._case.graph.edges:  # type: ignore[attr-defined]
            if e.type == "part_of" and e.src == cid:
                return e.dst
    return None


def _promote_change_cause(ig: InvestigationGraph, event_id: str, subsystem_id: str) -> None:
    """Credit the hypothesis implicated by an aligned recent change with a positive belief link.

    Match the hypothesis by `node_ref`: the subsystem itself, or any config/part that is the
    subsystem (the differential may carry either granularity). Idempotent — re-running adds no
    duplicate link/evidence. Adds to belief math (a link), not just the synthesize prompt."""
    targets = [h for h in ig.hypotheses if h.node_ref == subsystem_id]
    if not targets:
        return
    evid = f"ev.change_cause_{event_id}"
    if not any(e.id == evid for e in ig.evidence):
        ig.evidence.append(EvidenceItem(
            id=evid, source="onset_vs_event_check",
            summary=(f"{event_id}: a recent config change to {subsystem_id} aligns with the "
                     "degradation onset → the change is the cause")))
    for h in targets:
        if not any(ln.evidence_id == evid and ln.hypothesis_id == h.id for ln in ig.links):
            ig.links.append(EvidenceLink(evidence_id=evid, hypothesis_id=h.id,
                                         polarity="+", weight=CHANGE_CAUSE_WEIGHT))


def _finalize_conflicts(ig: InvestigationGraph, env: Environment, known_ids) -> None:
    """The controller's structural thoroughness (spec §6.5 playbook): before finalizing, run the
    deterministic discriminators a complete diagnosis always owes — order the degradation onset
    against the *most salient recent event* and act on it *symmetrically*: demote it iff the onset
    predates it (coincident, D1), or *promote* the implicated subsystem iff the onset aligns with a
    recent config change that event made (the change IS the cause) — and sanity-check every channel
    for a stuck/lying sensor (B5). These are deterministic conclusions of deterministic checks, so
    they are aggregated mechanically (no LLM): the demote adds the event id to conflicts; the
    promote adds a positive belief link, so the sweep enters the belief math (not just the
    synthesize prompt). General by construction: no recent event / no real config change / no stuck
    channel ⇒ no-op; a recent event with no config change is never promoted; a coincident event
    (onset predates) is demoted, not promoted. This is the conflict-surfacing the bare baselines
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

    # 1) order onset vs the most salient recent event — symmetric:
    #    onset predates it  → coincident, demote (add to conflicts)
    #    onset aligns + it made a real config change → the change IS the cause, promote its
    #    subsystem's hypothesis (add a positive belief link)
    try:
        logs = [a for a in env.read_logbook() if a.timestamp is not None]
    except NotSupported:
        logs = []
    if logs:
        latest = max(logs, key=lambda a: a.timestamp)
        try:
            r = env.run_check("onset_vs_event_check", {"event_id": latest.id})
        except (NotSupported, KeyError, ValueError):
            r = None
        if r is not None:
            if r.get("onset_predates_event"):
                _note(latest.id, "ev.trigger_demoted",
                      f"{latest.id}: degradation onset predates it → coincident, not causal")
            else:
                sub = _change_cause_subsystem(env, latest.id)
                if sub is not None:
                    _promote_change_cause(ig, latest.id, sub)

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
    _promote_common_mode(ig, env, known_ids)  # structural promotion of a shared upstream cause
    beliefs.update_beliefs(ig, prior)         # fold the sweep's links into log_odds before stopping
    _snapshot(ig)
    _trace_step(ig, action="conflict_sweep", args=None,
                rationale="order onset vs the salient recent event; sanity-check channels",
                voi=0.0, evidence_id=None,
                conflicts_added=[c for c in ig.conflicts if c not in conflicts_before])

    _top, conf, margin = beliefs.leader(ig)
    # Abstain when the leader is not CONFIDENT (conf) OR not DOMINANT (margin). A conf-only gate
    # (the old code) concludes a single cause on a dispersed differential — several comparably-
    # supported hypotheses — which is exactly the "no single clean cause" state that should abstain
    # (M4). Reuse tau_margin, the same dominance bar the `_should_conclude` stop already trusts, so
    # a conclusion and a non-abstention agree. tau_min stays the budget-exhausted confidence floor.
    abstain = conf <= th["tau_min"] or margin <= th["tau_margin"]
    answer = synthesize(backend, ig, abstain=abstain)
    ig.status = "abstained" if answer.answer_type == "abstain" else "concluded"
    ig.recommended_action = answer.recommended_action or ig.recommended_action
    _snapshot(ig)
    _trace_step(ig, action="synthesize",
                args={"answer_type": answer.answer_type, "root_cause": answer.root_cause},
                rationale="conclude or abstain from the differential", voi=0.0,
                evidence_id=None, conflicts_added=[])
    return answer
