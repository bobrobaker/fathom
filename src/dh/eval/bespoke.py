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


# --- canonicalisation maps from a case ---------------------------------------

def _signal_to_metric(case: Case) -> dict[str, str]:
    return {n.props["signal"]: n.id for n in case.graph.nodes
            if n.type in ("metric", "KPI") and "signal" in n.props}


def _cause_equivalents(node_id: str | None, case: Case) -> set[str]:
    """A cause id plus its part_of/version_of family (granularity robustness)."""
    if not node_id:
        return set()
    equiv = {node_id}
    for e in case.graph.edges:
        if e.type in ("part_of", "version_of"):
            if e.src == node_id:
                equiv.add(e.dst)
            if e.dst == node_id:
                equiv.add(e.src)
    return equiv


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
        | {s.signal for s in case.telemetry} \
        | {f"{c}_check" for c in ["config_diff", "spatial_intensity", "temp_correlation",
                                  "tec_load", "channel_sanity", "onset_vs_event"]}

    s = CaseScore(solver=solver, tokens=tokens)

    # accuracy — both abstain, or root cause within the gt cause family
    if gt.answer_type == "abstain":
        s.accuracy = 1.0 if answer.answer_type == "abstain" else 0.0
    else:
        s.accuracy = 1.0 if (answer.answer_type == "cause" and answer.root_cause
                             in _cause_equivalents(gt.root_cause, case)) else 0.0

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
