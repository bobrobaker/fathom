"""Bespoke rubric — per case, vs ground truth (spec §8.1).

Two families, reported separately (§8.1):
  - accuracy   : root-cause correctness.
  - capability : evidence-F1, conflict-handling, trigger-discrimination, abstention-
                 calibration — where the structure should win even if a strong bare_llm
                 ties on accuracy.
Plus cost (tokens) reported alongside.

Scoring is granularity- and id-space-robust so it is *fair to every solver*: a part and
its subsystem count as the same cause (via part_of/version_of); a signal and its metric
node are the same id; controller EvidenceItem ids are normalised to their `source` so they
live in the same space as a baseline's raw citations. Never tune this to manufacture a win
(non-negotiable #5) — the same canonicalisation applies to all four solvers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dh.schemas import Answer, Case, InvestigationGraph

ACCURACY_FAMILY = ["accuracy"]
CAPABILITY_FAMILY = ["evidence_f1", "conflict_handling", "trigger_discrimination",
                     "abstention_calibration"]
LOCALIZATION_FAMILY = ["localization"]

# The canonical evidence ids a solver may legitimately cite that are not graph/artifact/signal
# ids: deterministic check names (the `check` field each returns) + the recommend action. Used
# both to canonicalise and to detect hallucinated citations — identically for all four solvers.
CHECK_IDS = {
    "config_diff", "spatial_intensity_check", "temp_correlation_check", "tec_load_check",
    "channel_sanity_check", "onset_vs_event_check", "detector_health_check",
    "common_mode_check", "recommend_swap_test",
}


# --- canonicalisation maps from a case ---------------------------------------

def _signal_to_metric(case: Case) -> dict[str, str]:
    return {n.props["signal"]: n.id for n in case.graph.nodes
            if n.type in ("metric", "KPI") and "signal" in n.props}


def _node_type(node_id: str, case: Case) -> str | None:
    return next((n.type for n in case.graph.nodes if n.id == node_id), None)


def _exact_cause_set(node_id: str | None, case: Case) -> set[str]:
    """Ids that count as naming the *exact* cause (C6 — strict accuracy).

    The node itself, plus its `version_of` family (the same physical part across revisions,
    e.g. part.tec ↔ part.tec.revB). For a *subsystem-level* cause (calibration/power, where
    the subsystem itself is the fault), naming a `config` that is `part_of` it also counts —
    that is at least as specific as the subsystem. A part fault is NOT satisfied by naming its
    subsystem (that is localization, scored separately): a 'thermal' answer does not earn
    accuracy for a 'tec' fault."""
    if not node_id:
        return set()
    s = {node_id}
    for e in case.graph.edges:
        if e.type == "version_of":
            if e.src == node_id:
                s.add(e.dst)
            if e.dst == node_id:
                s.add(e.src)
    if _node_type(node_id, case) == "subsystem":
        for e in case.graph.edges:
            if e.type == "part_of" and e.dst == node_id and _node_type(e.src, case) == "config":
                s.add(e.src)
    return s


def _subsystem_of(node_id: str | None, case: Case) -> str | None:
    """The subsystem a part/config belongs to (`part_of`), or the node itself if a subsystem."""
    if not node_id:
        return None
    for e in case.graph.edges:
        if e.type == "part_of" and e.src == node_id:
            return e.dst
    return node_id if _node_type(node_id, case) == "subsystem" else None


def _localization_set(node_id: str | None, case: Case) -> set[str]:
    """Ids that count as localizing to the right *subsystem* (partial credit, reported apart
    from accuracy): the exact cause, its subsystem, and everything `part_of` that subsystem."""
    s = _exact_cause_set(node_id, case)
    sub = _subsystem_of(node_id, case)
    if sub:
        s.add(sub)
        s |= {e.src for e in case.graph.edges if e.type == "part_of" and e.dst == sub}
    return s


def _canon(idv: str, sig2metric: dict[str, str], ev2src: dict[str, str]) -> str:
    v = ev2src.get(idv, idv)        # EvidenceItem id → its source/provenance
    v = v.split(":")[-1].strip()    # strip an action prefix ("run_check:tec_load_check")
    return sig2metric.get(v, v)     # signal name → metric node id


def _canon_set(ids, sig2metric, ev2src) -> set[str]:
    return {_canon(i, sig2metric, ev2src) for i in ids if isinstance(i, str)}


# --- the rubric --------------------------------------------------------------

@dataclass
class CaseScore:
    solver: str
    accuracy: float = 0.0
    localization: float = 0.0       # right subsystem (partial credit), reported apart from accuracy
    evidence_f1: float = 0.0
    conflict_handling: float = 0.0
    trigger_discrimination: float = 0.0
    abstention_calibration: float = 0.0
    tokens: int = 0
    extra: dict = field(default_factory=dict)

    def family(self, names: list[str]) -> dict[str, float]:
        return {n: getattr(self, n) for n in names}


def _f1(pred: set[str], gold: set[str], hallucinated: set[str]) -> float:
    """F1 of pred vs gold; hallucinated citations dilute precision (§8.1)."""
    if not gold and not pred:
        return 1.0
    tp = len(pred & gold)
    precision_denom = len(pred) + len(hallucinated)
    precision = tp / precision_denom if precision_denom else 0.0
    recall = tp / len(gold) if gold else 0.0
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0


def score(answer: Answer, case: Case, *, solver: str = "", tokens: int = 0) -> CaseScore:
    gt = case.ground_truth
    fg: InvestigationGraph = answer.final_graph
    sig2metric = _signal_to_metric(case)
    ev2src = {e.id: e.source for e in fg.evidence}
    valid_case_ids = {n.id for n in case.graph.nodes} | {a.id for a in case.artifacts} \
        | {s.signal for s in case.telemetry} | CHECK_IDS

    s = CaseScore(solver=solver, tokens=tokens)

    # accuracy — both abstain, or root cause is the EXACT cause (C6: strict; a part fault is
    # not satisfied by its subsystem). localization (right subsystem) is scored separately.
    if gt.answer_type == "abstain":
        s.accuracy = 1.0 if answer.answer_type == "abstain" else 0.0
        s.localization = s.accuracy
    else:
        named = answer.root_cause if answer.answer_type == "cause" else None
        s.accuracy = 1.0 if named in _exact_cause_set(gt.root_cause, case) else 0.0
        s.localization = 1.0 if named in _localization_set(gt.root_cause, case) else 0.0

    # evidence-F1 — canonicalised cited vs load-bearing; out-of-case ids are hallucinations
    cited = _canon_set(answer.cited_evidence, sig2metric, ev2src)
    gold_ev = _canon_set(gt.load_bearing_evidence, sig2metric, ev2src)
    hallucinated = {c for c in answer.cited_evidence
                    if c not in valid_case_ids and c not in ev2src}
    s.evidence_f1 = _f1(cited, gold_ev, hallucinated)

    # conflict-handling — fraction of gt conflicts surfaced
    surfaced = _canon_set(answer.conflicts, sig2metric, ev2src)
    gold_conf = _canon_set(gt.conflicts, sig2metric, ev2src)
    s.conflict_handling = (len(surfaced & gold_conf) / len(gold_conf)) if gold_conf else 1.0

    # trigger-discrimination — trigger exists, not named as cause, and noted
    if gt.trigger:
        trg = _canon(gt.trigger, sig2metric, ev2src)
        named_cause = _canon(answer.root_cause or "", sig2metric, ev2src)
        s.trigger_discrimination = 1.0 if (trg != named_cause and trg in surfaced) else 0.0
    else:
        s.trigger_discrimination = 1.0  # no trigger to be fooled by

    # abstention-calibration — correct on the abstain/cause decision
    s.abstention_calibration = 1.0 if (answer.answer_type == "abstain") == \
        (gt.answer_type == "abstain") else 0.0

    return s
