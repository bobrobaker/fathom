"""Spike: case8 `common_mode_power` — reproduce the LIVE failure, prove the fix.

The prior spike PASSED while live FAILED because it hand-seeded a `sub.power` hypothesis the
real LLM never proposes. This spike does NOT: it scripts `seed_hypotheses` to return the ACTUAL
live seeding (PART-granularity hypotheses, NO `sub.power` — copied from `cap_case8.json`) and the
ACTUAL live interpret links (the M1-inflated decoy `part.detector` reaching +2.5). It then proves:

  1. the seeding-coverage fix introduces `sub.power` as a hypothesis even though the LLM omitted it
     (because it is the `affects`-ancestor of every degraded subsystem);
  2. the granularity-matched common-mode promotion attaches links to it (and demotes the PART-level
     surface decoys), so `sub.power` becomes the dominant leader and the leader-anchored verdict
     names it → accuracy 1.0 against the gold `sub.power`.

Real LidarEnvironment + real diagnose/beliefs/voi/scorer; only the LLM is scripted.
"""

import json

import pytest

from dh.controller import beliefs
from dh.controller.llm import ScriptedBackend
from dh.controller.loop import (
    _hyps_in_subsystems,
    _promote_common_mode,
    _seed_candidates,
    _seed_upstream_coverage,
    diagnose,
)
from dh.environment import LidarEnvironment
from dh.eval.bespoke import _exact_cause_set, score
from dh.generator import generate
from dh.schemas import Hypothesis, InvestigationGraph

# --- the ACTUAL live seeding (cap_case8.json `hypotheses`): PART granularity, NO sub.power ----
LIVE_SEED = {"hypotheses": [
    {"id": "hyp.window_contamination", "label": "Window contamination", "node_ref": "part.window"},
    {"id": "hyp.laser_aging", "label": "Laser emitter output power degraded", "node_ref": "part.laser_module"},
    {"id": "hyp.detector_drift", "label": "Receiver detector responsivity drifted", "node_ref": "part.detector"},
    {"id": "hyp.thermal_tec", "label": "TEC module underperforming", "node_ref": "part.tec"},
    {"id": "hyp.calibration_drift", "label": "Calibration coefficients stale", "node_ref": "sub.calibration"},
]}

# the three checks the live run took, in order
LIVE_PROPOSE = [
    {"actions": [{"type": "run_check", "args": {"name": "spatial_intensity_check"}, "expected_discrimination": 0.8}]},
    {"actions": [{"type": "run_check", "args": {"name": "tec_load_check"}, "expected_discrimination": 0.8}]},
    {"actions": [{"type": "run_check", "args": {"name": "detector_health_check"}, "expected_discrimination": 0.8}]},
]

# the ACTUAL live interpret links (cap_case8.json `links`) — including the M1 over-credit that
# saturates the decoy part.detector to +2.5. This is the "realistic decoy over-crediting" the
# orchestrator required: a faithful-but-honest script would NOT flip the case; the live LLM's does.
LIVE_INTERPRET = [
    {"evidence": {"id": "ev.spatial_intensity_001", "summary": "uniform drop across regions",
                  "source": "spatial_intensity_check"},
     "links": [{"hypothesis_id": "hyp.window_contamination", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "hyp.laser_aging", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "hyp.detector_drift", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "hyp.thermal_tec", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "hyp.calibration_drift", "polarity": "+", "weight": 0.5}]},
    {"evidence": {"id": "ev.tec_load_001", "summary": "TEC nominal, losing_setpoint=false",
                  "source": "tec_load_check"},
     "links": [{"hypothesis_id": "hyp.thermal_tec", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "hyp.laser_aging", "polarity": "-", "weight": 0.5},
               {"hypothesis_id": "hyp.detector_drift", "polarity": "-", "weight": 0.5}]},
    {"evidence": {"id": "ev.detector_health_001", "summary": "dark counts +45%, bias_drift=true",
                  "source": "detector_health_check"},
     "links": [{"hypothesis_id": "hyp.detector_drift", "polarity": "+", "weight": 2.0},
               {"hypothesis_id": "hyp.thermal_tec", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "hyp.laser_aging", "polarity": "-", "weight": 1.0},
               {"hypothesis_id": "hyp.calibration_drift", "polarity": "-", "weight": 1.0}]},
]

# the live synthesize named part.detector; the leader-anchored verdict overrides it when the belief
# leader is dominant — so a passing run must override THIS wrong free-text to the dominant sub.power.
LIVE_SYNTH = {"answer_type": "cause", "root_cause": "part.detector",
              "causal_chain": ["part.detector"],
              "cited_evidence": ["ev.detector_health_001", "ev.common_mode"], "conflicts": []}


def _backend() -> ScriptedBackend:
    return ScriptedBackend({
        "seed": json.dumps(LIVE_SEED),
        "propose": [json.dumps(p) for p in LIVE_PROPOSE],
        "interpret": [json.dumps(i) for i in LIVE_INTERPRET],
        "synthesize": json.dumps(LIVE_SYNTH),
    })


def _run():
    case = generate("common_mode_power", [], seed=7)
    env = LidarEnvironment(case)
    ans = diagnose(env, backend=_backend(), budget=6)
    return case, env, ans


# --- the two live bugs, in isolation -----------------------------------------

def test_live_seed_omits_sub_power_and_coverage_fix_adds_it():
    """Bug 1 (seeding gap): the live LLM never seeds sub.power; the coverage fix must add it as a
    structurally-reachable upstream cause (affects-ancestor of the seeded parts' subsystems)."""
    case = generate("common_mode_power", [], seed=7)
    env = LidarEnvironment(case)
    ig = InvestigationGraph(symptom=env.symptom())
    ig.hypotheses = [Hypothesis(id=h["id"], label=h["label"], node_ref=h["node_ref"])
                     for h in LIVE_SEED["hypotheses"]]
    assert all(h.node_ref != "sub.power" for h in ig.hypotheses)        # the live gap
    _seed_upstream_coverage(ig, env, _seed_candidates(env))
    assert any(h.node_ref == "sub.power" for h in ig.hypotheses)        # the fix


def test_granularity_match_links_part_decoys_to_their_subsystem():
    """Bug 2 (granularity mismatch): the promotion must match a PART-granularity hypothesis
    (part.detector) to its degraded subsystem (sub.detector). The pre-fix `node_ref == sub.*`
    match attached zero links to the live part.* hypotheses."""
    case = generate("common_mode_power", [], seed=7)
    matched = _hyps_in_subsystems(
        InvestigationGraph(symptom="x", hypotheses=[
            Hypothesis(id="hyp.detector_drift", label="d", node_ref="part.detector")]),
        case, {"sub.detector"})
    assert [h.node_ref for h in matched] == ["part.detector"]


# --- the end-to-end fix: case8 flips to sub.power ----------------------------

def test_case8_concludes_sub_power_after_fix():
    """End-to-end: with the live seeding + live M1-inflated decoy, the fix makes sub.power the
    dominant leader and the verdict names it → accuracy 1.0 (was part.detector, acc 0)."""
    case, env, ans = _run()
    assert ans.answer_type == "cause"
    assert ans.root_cause == "sub.power" == case.ground_truth.root_cause

    # the belief math, not the model's prose, drives it: sub.power is the dominant leader
    top, conf, margin = beliefs.leader(ans.final_graph)
    assert top.node_ref == "sub.power"
    assert conf > 0.70 and margin > 0.20

    # the surface decoy part.detector (live +2.5) is demoted below the upstream cause
    det = next(h for h in ans.final_graph.hypotheses if h.node_ref == "part.detector")
    assert beliefs.confidence(det) < conf

    # the scorer accepts it (sub.power is a subsystem cause; its part_of configs also count)
    sc = score(ans, case, solver="controller")
    assert sc.accuracy == 1.0
    assert "sub.power" in _exact_cause_set(case.ground_truth.root_cause, case)


def test_promotion_attached_a_positive_link_to_sub_power():
    """The common-mode promotion entered the belief math (a link), not just text — the M2 gap the
    granularity mismatch reopened. A positive ev.common_mode link must reach the sub.power hyp."""
    _case, _env, ans = _run()
    ig = ans.final_graph
    sp = next(h for h in ig.hypotheses if h.node_ref == "sub.power")
    pos = [ln for ln in ig.links
           if ln.hypothesis_id == sp.id and ln.evidence_id == "ev.common_mode" and ln.polarity == "+"]
    assert pos, "common-mode promotion attached no positive link to sub.power"


def test_promotion_is_a_noop_on_a_non_common_mode_case():
    """#5 guard: the coverage fix adds a sub.power hypothesis on a NON-common-mode case too (it is
    structurally reachable), but with no common-mode + upstream config change the promotion never
    fires, so sub.power sits at prior and is NOT concluded. Case1 still concludes part.tec."""
    case = generate("tec_degradation", [], seed=0)
    env = LidarEnvironment(case)
    ig = InvestigationGraph(symptom=env.symptom())
    ig.hypotheses = [Hypothesis(id="h.tec", label="t", node_ref="part.tec"),
                     Hypothesis(id="h.laser", label="l", node_ref="part.laser_module")]
    _seed_upstream_coverage(ig, env, _seed_candidates(env))
    _promote_common_mode(ig, env, None)  # case1 is not common-mode → no link added
    assert not any(ln.evidence_id == "ev.common_mode" for ln in ig.links)
