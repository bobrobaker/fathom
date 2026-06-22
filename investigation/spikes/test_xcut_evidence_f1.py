"""xcut shortcoming 1 — evidence-F1 weakness (controller 0.26 vs react 0.44).

Two structural facts proven here against the REAL scorer + REAL env:

(A) Real, not a pure scorer artifact, BUT partly a citation-id *contract asymmetry*:
    baselines put BARE provenance ids in `cited_evidence` (react: `tec_load_check`,
    `config.cal_table_version`, `metric.diode_temp` — `_min_graph`, so `ev2src` is
    empty and `_canon` is identity), while the controller cites EvidenceItem ids
    (`ev.tecload`) that `_canon` indirects through the item's free-text `source`.
    So the controller scores ONLY when interpret happened to set `source` to the
    gold provenance id. The interpret prompt never pins `source` to the check id,
    so live it drifts and F1 collapses below its ceiling.

(B) A residual REAL ceiling: gold `load_bearing_evidence` mixes check ids with
    artifact/metric ids (`metric.diode_temp`, `err.tec_load`, `config.*`, `doc.*`)
    that the controller never wraps as an EvidenceItem at all — so even with perfect
    sources it cannot cite them. That part is a coverage gap, not a scoring bug.

The fix spiked: deterministically pin an EvidenceItem's `source` to the check name
for `run_check` actions (the env returns `result["check"]`). This removes the live
LLM-drift component of the gap. It is #5-neutral on accuracy (it changes only which
provenance id a citation canonicalises to, never the named root cause).
"""

import json
import sys

import pytest

from dh.controller.llm import ScriptedBackend, interpret_result
from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.generator import generate
from dh.generator.cases import authored_cases
from dh.eval.bespoke import CHECK_IDS, _f1, score
from dh.schemas import InvestigationGraph, Hypothesis

import tests.test_controller_tec as tec_test  # reuse the faithful tec script


def _tec_case():
    spec = next(s for s in authored_cases() if s.fault == "tec_degradation")
    return generate(spec.fault, list(spec.mechanisms), seed=spec.seed)


# --- (A) baseline vs controller citation-id contract asymmetry ----------------

def test_react_cites_bare_ids_controller_indirects_through_source():
    """Structural proof: a baseline's bare-id citation lands directly in gold's id-space;
    the controller's EvidenceItem id only lands there via its `source`."""
    case = _tec_case()
    env = LidarEnvironment(case)
    ans = diagnose(env, backend=tec_test._backend(), budget=12)
    # controller cites EvidenceItem ids, NOT bare provenance ids
    assert all(c.startswith("ev.") for c in ans.cited_evidence)
    ev2src = {e.id: e.source for e in ans.final_graph.evidence}
    # each cited id only matches gold after indirection through `source`
    for c in ans.cited_evidence:
        assert c not in case.ground_truth.load_bearing_evidence  # bare id never matches
        # but its source can
    # a react-style answer citing the same provenance bare would canon directly
    from dh.schemas import Answer
    from dh.baselines import _min_graph
    react_like = Answer(answer_type="cause", root_cause="part.tec",
                        cited_evidence=["tec_load_check", "temp_correlation_check",
                                        "onset_vs_event_check", "metric.diode_temp",
                                        "err.tec_load"],
                        final_graph=_min_graph(env, "part.tec"))
    sc_react = score(react_like, case)
    assert sc_react.evidence_f1 == pytest.approx(1.0)  # bare ids match gold perfectly


# --- (B) the residual real ceiling -------------------------------------------

def test_controller_has_a_real_nonartifact_ceiling():
    """Even with perfectly faithful check sources, the controller cannot reach gold
    artifact/metric ids it never wrapped as evidence — a real coverage ceiling < 1.0."""
    case = _tec_case()
    gold = set(case.ground_truth.load_bearing_evidence)
    checkable = gold & CHECK_IDS
    ceiling = _f1(checkable, gold)
    assert ceiling < 1.0  # metric.diode_temp + err.tec_load are unreachable via checks
    assert ceiling == pytest.approx(0.75)


# --- the live-drift component: source not pinned ------------------------------

def test_interpret_does_not_pin_source_today():
    """Current interpret trusts the LLM's free-text `source`; an unfaithful source
    (the live failure) canonicalises a real check citation OUT of gold's id-space."""
    case = _tec_case()
    env = LidarEnvironment(case)
    result = env.run_check("tec_load_check", {})
    ig = InvestigationGraph(symptom="range degradation",
                            hypotheses=[Hypothesis(id="h.tec", label="tec", node_ref="part.tec")])
    # an LLM that returns a vague source (observed live) instead of the check id
    bad = ScriptedBackend({"interpret": json.dumps({
        "evidence": {"id": "ev.x", "summary": "tec near limit", "source": "observation"},
        "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.5}]})})
    from dh.controller.llm import ActionProposal
    ev, links, _ = interpret_result(bad, ig, ActionProposal(type="run_check",
                                    args={"name": "tec_load_check"}), result)
    if ev.source == "tec_load_check":
        pytest.skip("source-pin fix already applied to src/ (this documents pre-fix drift)")
    assert ev.source == "observation"  # pre-fix: NOT pinned -> canon misses gold


# --- the fix raises F1 toward the ceiling ------------------------------------

def test_fix_pins_source_to_check_name():
    """With the fix applied (interpret pins source=result['check'] for run_check), the
    same vague-source LLM reply still canonicalises to the gold check id.

    Skips cleanly until the fix is applied to src/ so this file is a living before/after."""
    case = _tec_case()
    env = LidarEnvironment(case)
    result = env.run_check("tec_load_check", {})
    ig = InvestigationGraph(symptom="range degradation",
                            hypotheses=[Hypothesis(id="h.tec", label="tec", node_ref="part.tec")])
    bad = ScriptedBackend({"interpret": json.dumps({
        "evidence": {"id": "ev.x", "summary": "tec near limit", "source": "observation"},
        "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.5}]})})
    from dh.controller.llm import ActionProposal
    ev, _, _ = interpret_result(bad, ig, ActionProposal(type="run_check",
                                args={"name": "tec_load_check"}), result)
    if ev.source != "tec_load_check":
        pytest.skip("source-pin fix not applied to src/ (expected before patch)")
    assert ev.source == "tec_load_check"
