"""A7 — the scoring id-space is symmetric across all four solvers (fairness, §8.1, C5).

The rubric canonicalises evidence ids before comparing to ground truth: an EvidenceItem id
is resolved to its `source`, an action prefix is stripped, and a raw signal name maps to its
metric node. This must be applied *identically* to every solver — so the controller's
structured `EvidenceItem(source="tec_load_check")` and a baseline's raw citation
`"tec_load_check"` for the same evidence land on the same id and earn the same credit — and it
must never launder a wrong citation into a right one.
"""

import pytest

from dh.eval.bespoke import _canon, _signal_to_metric, score
from dh.generator import generate
from dh.schemas import Answer, EvidenceItem, InvestigationGraph


@pytest.fixture(scope="module")
def case():
    return generate("tec_degradation", ["D1", "B5", "D5", "A2"], seed=0)


def _ans(root, cited, evidence=(), conflicts=()):
    return Answer(answer_type="cause", root_cause=root, cited_evidence=list(cited),
                  conflicts=list(conflicts),
                  final_graph=InvestigationGraph(symptom="x", evidence=list(evidence)))


# --- the same evidence canonicalises identically regardless of solver shape ---

def test_structured_and_raw_citation_collapse_to_same_id(case):
    sig2metric = _signal_to_metric(case)
    # controller: an EvidenceItem whose source is the check, cited by the item's own id
    ctrl_ev2src = {"ev.1": "run_check:tec_load_check"}
    ctrl = _canon("ev.1", sig2metric, ctrl_ev2src)
    # baseline: cites the check name (or the prefixed action key) directly, no EvidenceItem
    base = _canon("tec_load_check", sig2metric, {})
    base_prefixed = _canon("run_check:tec_load_check", sig2metric, {})
    assert ctrl == base == base_prefixed == "tec_load_check"


def test_signal_and_metric_node_collapse(case):
    sig2metric = _signal_to_metric(case)
    # a raw signal name and its metric node id are the same evidence
    assert _canon("laser_diode_temp_C", sig2metric, {}) == _canon("metric.diode_temp", sig2metric, {})


def test_identical_evidence_scores_identically_for_controller_and_baseline(case):
    gt = case.ground_truth
    # both cite exactly the load-bearing set, but the controller routes through EvidenceItems
    ev = [EvidenceItem(id=f"ev.{i}", summary="", source=src)
          for i, src in enumerate(gt.load_bearing_evidence)]
    controller = _ans("part.tec", [e.id for e in ev], evidence=ev)
    baseline = _ans("part.tec", gt.load_bearing_evidence)
    cs = score(controller, case, solver="controller")
    bs = score(baseline, case, solver="bare_llm")
    assert cs.evidence_f1 == pytest.approx(bs.evidence_f1)
    assert cs.evidence_f1 > 0.9  # both effectively cite the whole load-bearing set


# --- canonicalisation must not launder a wrong citation into a right one ------

def test_canon_does_not_turn_wrong_into_right(case):
    gt = case.ground_truth
    wrong = _ans("part.tec", ["report.prior_laser", "log.service"])  # real ids, not load-bearing
    s = score(wrong, case)
    # citing real-but-irrelevant artifacts earns no evidence credit beyond their true overlap
    gold = set(gt.load_bearing_evidence)
    assert "report.prior_laser" not in gold and "log.service" not in gold
    assert s.evidence_f1 < 0.34  # ≤ the floor from zero true positives among 2 cited vs 5 gold


def test_hallucinated_ids_penalise_every_solver_equally(case):
    # an id that is in no case at all dilutes precision identically no matter who cites it
    base = _ans("part.tec", list(case.ground_truth.load_bearing_evidence))
    halluc = _ans("part.tec", list(case.ground_truth.load_bearing_evidence) + ["totally.made.up"])
    assert score(halluc, case).evidence_f1 < score(base, case).evidence_f1
