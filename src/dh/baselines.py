"""Baselines (spec §7) — strong and fair, all returning `Answer` (non-negotiable #3).

- `shortcut`  — blames the most recent change/event. The rig-detector: the controller
  must beat it or the cases are leaky. Deterministic, no LLM.
- `bare_llm`  — the whole case (telemetry summaries + every artifact) in one prompt,
  asked for the root cause + evidence. A genuinely strong long-context prompt.
- `react`     — the controller's tools in a plain ReAct loop, but WITHOUT the
  hypothesis-differential / IG bookkeeping and VOI selection — isolates the structure.

`bare_llm`/`react` never see `Case.ground_truth`: they only touch the `Environment`.
The baselines fill `final_graph` minimally so the eval scores all four solvers identically.
"""

from __future__ import annotations

import json
import logging
import statistics as st

from dh.controller.llm import LLMBackend, _call_json, get_backend
from dh.controller.loop import _seed_candidates
from dh.environment import Environment, NotSupported
from dh.schemas import Answer, Hypothesis, InvestigationGraph

log = logging.getLogger("dh.baselines")


def _min_graph(env: Environment, root: str | None = None) -> InvestigationGraph:
    ig = InvestigationGraph(symptom=env.symptom(), status="concluded")
    if root:
        ig.hypotheses = [Hypothesis(id=f"h.{root}", label=root, node_ref=root)]
    return ig


# --- shortcut (deterministic) ------------------------------------------------

def shortcut(env: Environment, backend: LLMBackend | None = None) -> Answer:
    """Blame the most recent change or event (config change, else latest logbook entry)."""
    root, cited = None, []
    try:
        changed = env.run_check("config_diff", {}).get("changed", [])
    except NotSupported:
        changed = []
    if changed:
        root = f"config.{changed[-1]['key']}"
        cited = [root]
    else:
        try:
            logs = [a for a in env.read_logbook() if a.timestamp is not None]
        except NotSupported:
            logs = []
        if logs:
            latest = max(logs, key=lambda a: a.timestamp)
            root, cited = latest.id, [latest.id]
    return Answer(answer_type="cause" if root else "abstain", root_cause=root,
                  cited_evidence=cited, recommended_action="investigate the most recent change",
                  final_graph=_min_graph(env, root))


# --- bare_llm (strong long-context) ------------------------------------------

def _telemetry_digest(env: Environment) -> str:
    lines = []
    for sig in env.list_signals():
        s = env.query_telemetry(sig)
        base = st.mean(s.v[:8]) if len(s.v) >= 8 else st.mean(s.v)
        recent = st.mean(s.v[-5:]) if len(s.v) >= 5 else st.mean(s.v)
        spec = f" spec={s.spec}" if s.spec else ""
        lines.append(f"  {sig}: baseline≈{base:.3f} → recent≈{recent:.3f}{spec}")
    return "\n".join(lines)


def _artifact_digest(env: Environment) -> str:
    arts = []
    for q in ("range degradation playbook", "TEC thermal laser", "reboot maintenance",
              "prior incident", "window clean swap test"):
        for a in env.search(q, k=5):
            arts.append(a)
    seen, out = set(), []
    for a in arts:
        if a.id in seen:
            continue
        seen.add(a.id)
        ts = f" t={a.timestamp}" if a.timestamp is not None else ""
        out.append(f"  [{a.id}] ({a.kind}{ts}) {a.text}")
    return "\n".join(out)


def _candidate_legend(env: Environment) -> str:
    return ", ".join(f"{c['id']}" for c in _seed_candidates(env)) or "(none)"


def bare_llm(env: Environment, backend: LLMBackend | None = None) -> Answer:
    """Dump all telemetry summaries + artifacts; ask for the root cause in one shot."""
    backend = backend or get_backend()
    if backend is None:
        raise RuntimeError("bare_llm needs an LLM backend")
    body = (
        f"Symptom: {env.symptom()}\n\n"
        f"Telemetry summaries (every signal):\n{_telemetry_digest(env)}\n\n"
        f"Documents / logs / actions:\n{_artifact_digest(env)}\n\n"
        f"Candidate root-cause node ids (answer with exactly one): {_candidate_legend(env)}\n\n"
        "Identify the single most likely root cause. Distinguish a true cause from a merely "
        "salient recent event, and note any unreliable channels. Return "
        '{"answer_type":"cause"|"abstain","root_cause":node_id,"causal_chain":[node_ids],'
        '"cited_evidence":[artifact_ids],"ruled_out":[node_ids],"conflicts":[ids],'
        '"recommended_action":str}.'
    )
    data = _call_json(backend, "bare", body, max_tokens=1536)
    candidate_ids = {c["id"] for c in _seed_candidates(env)}
    root = data.get("root_cause")
    answer_type = data.get("answer_type") if data.get("answer_type") in ("cause", "abstain") else "cause"
    return Answer(
        answer_type=answer_type,
        root_cause=root if answer_type == "cause" else None,
        causal_chain=[c for c in data.get("causal_chain", []) if isinstance(c, str)],
        cited_evidence=[c for c in data.get("cited_evidence", []) if isinstance(c, str)],
        ruled_out=[c for c in data.get("ruled_out", []) if isinstance(c, str)],
        conflicts=[c for c in data.get("conflicts", []) if isinstance(c, str)],
        recommended_action=data.get("recommended_action"),
        final_graph=_min_graph(env, root if root in candidate_ids else None),
    )


# --- react (tools, no IG/VOI structure) --------------------------------------

REACT_SYSTEM = (
    "You are a diagnostic agent with tools. Think step by step; each turn call ONE tool or "
    "give a final answer. Never assert a measurement you have not retrieved. Reply ONLY JSON."
)


def react(env: Environment, backend: LLMBackend | None = None, max_steps: int = 10) -> Answer:
    """Plain ReAct over the controller's tools — no differential, no VOI bookkeeping."""
    backend = backend or get_backend()
    if backend is None:
        raise RuntimeError("react needs an LLM backend")
    caps = env.capabilities()
    checks = env.list_checks() if hasattr(env, "list_checks") else []  # type: ignore[attr-defined]
    candidate_ids = {c["id"] for c in _seed_candidates(env)}
    transcript: list[str] = []

    for _step in range(max_steps):
        body = (
            f"Symptom: {env.symptom()}\n"
            f"Tools: {sorted(caps)}; checks={checks}\n"
            f"Candidate root-cause node ids: {sorted(candidate_ids) or '(none)'}\n"
            f"History so far:\n" + ("\n".join(transcript) or "  (empty)") + "\n"
            'Reply with either {"action":{"type","args"}} to use a tool '
            "(type ∈ run_check|search|traverse|read_logbook|read_errors|read_diagnostic_actions) "
            'or {"final":{"answer_type","root_cause","causal_chain","cited_evidence",'
            '"ruled_out","conflicts","recommended_action"}} when confident.'
        )
        data = _call_json(backend, "react", body, max_tokens=1024)
        if "final" in data:
            f = data["final"] or {}
            at = f.get("answer_type") if f.get("answer_type") in ("cause", "abstain") else "cause"
            root = f.get("root_cause")
            return Answer(
                answer_type=at, root_cause=root if at == "cause" else None,
                causal_chain=[c for c in f.get("causal_chain", []) if isinstance(c, str)],
                cited_evidence=[c for c in f.get("cited_evidence", []) if isinstance(c, str)],
                ruled_out=[c for c in f.get("ruled_out", []) if isinstance(c, str)],
                conflicts=[c for c in f.get("conflicts", []) if isinstance(c, str)],
                recommended_action=f.get("recommended_action"),
                final_graph=_min_graph(env, root if root in candidate_ids else None),
            )
        action = data.get("action") or {}
        obs = _react_execute(env, action)
        transcript.append(f"  action={json.dumps(action)} -> {json.dumps(obs)[:300]}")

    log.info("react hit step cap; abstaining")
    return Answer(answer_type="abstain", recommended_action="needs more investigation",
                  final_graph=_min_graph(env))


def _react_execute(env: Environment, action: dict) -> dict:
    t, args = action.get("type"), action.get("args", {}) or {}
    try:
        if t == "run_check":
            return env.run_check(args.get("name", ""), args)
        if t == "search":
            return {"results": [{"id": a.id, "text": a.text}
                                for a in env.search(args.get("query", ""), args.get("k", 4))]}
        if t == "traverse":
            return {"neighbors": [n.model_dump() for n in
                                  env.traverse(args["node_id"], args["edge_type"],
                                               args.get("direction", "out"))]}
        if t == "read_logbook":
            return {"events": [a.model_dump() for a in env.read_logbook()]}
        if t == "read_errors":
            return {"errors": [a.model_dump() for a in env.read_errors()]}
        if t == "read_diagnostic_actions":
            return {"actions": [a.model_dump() for a in env.read_diagnostic_actions()]}
    except (NotSupported, KeyError, ValueError) as e:
        return {"error": str(e)}
    return {"error": f"unknown action {t}"}


SOLVERS = {"shortcut": shortcut, "bare_llm": bare_llm, "react": react}
