"""M4 gate — the primary spine test (spec §6.1–6.4, build plan M4).

A ScriptedBackend supplies the LLM judgments while the REAL LidarEnvironment executes
the checks, so this verifies the loop end to end: VOI selection, real check execution,
deterministic belief aggregation, conflict propagation, stop conditions, snapshots, and
synthesis. The controller must conclude TEC degradation, cite the load-bearing evidence,
flag the stuck channel, demote the reboot, recommend the swap-test, and stay within budget.

The scripted judgments stand in for a competent model (live quality is measured by the
eval at M6+); the logic under test is fathom's, not the model's.
"""

import json

import pytest

from dh.controller import beliefs
from dh.controller.llm import ScriptedBackend
from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.generator import generate

SEED_HYPS = {"hypotheses": [
    {"id": "h.tec", "label": "TEC degradation", "node_ref": "part.tec"},
    {"id": "h.laser", "label": "laser power aging", "node_ref": "part.laser_module"},
    {"id": "h.optics", "label": "window contamination", "node_ref": "sub.optics"},
    {"id": "h.detector", "label": "detector bias drift", "node_ref": "sub.detector"},
    {"id": "h.calib", "label": "calibration drift", "node_ref": "sub.calibration"},
]}

# action proposals, popped in order — the loop picks the single proposed action each step
PROPOSE = [
    {"actions": [{"type": "run_check", "args": {"name": "config_diff"},
                  "expected_discrimination": 0.4}]},
    {"actions": [{"type": "run_check", "args": {"name": "spatial_intensity_check"},
                  "expected_discrimination": 0.4}]},
    {"actions": [{"type": "run_check", "args": {"name": "channel_sanity_check",
                  "signal": "detector_temp_C"}, "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "onset_vs_event_check",
                  "signal": "effective_max_range_m", "event_id": "log.reboot"},
                  "expected_discrimination": 0.6}]},
    {"actions": [{"type": "run_check", "args": {"name": "temp_correlation_check"},
                  "expected_discrimination": 0.9}]},
    {"actions": [{"type": "recommend_swap_test", "args": {}, "expected_discrimination": 0.8}]},
    {"actions": [{"type": "run_check", "args": {"name": "tec_load_check"},
                  "expected_discrimination": 0.8}]},
]

# evidence interpretations, aligned with PROPOSE order
INTERPRET = [
    {"evidence": {"id": "ev.config", "summary": "no config change", "source": "config_diff"},
     "links": [{"hypothesis_id": "h.calib", "polarity": "-", "weight": 1.0}]},
    {"evidence": {"id": "ev.spatial", "summary": "uniform intensity drop",
                  "source": "spatial_intensity_check"},
     "links": [{"hypothesis_id": "h.optics", "polarity": "-", "weight": 1.0}]},
    {"evidence": {"id": "ev.channel", "summary": "detector_temp stuck (var≈0)",
                  "source": "channel_sanity_check"},
     "links": [], "conflicts": ["metric.detector_temp"]},
    {"evidence": {"id": "ev.onset", "summary": "degradation onset precedes the reboot",
                  "source": "onset_vs_event_check"},
     "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.15}],
     "conflicts": ["log.reboot"]},
    {"evidence": {"id": "ev.tempcorr", "summary": "intensity tracks diode temp r=-0.88",
                  "source": "temp_correlation_check"},
     "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.5},
               {"hypothesis_id": "h.laser", "polarity": "-", "weight": 0.4}]},
    {},  # recommend_swap_test → no evidence
    {"evidence": {"id": "ev.tecload", "summary": "TEC current at 91% of limit",
                  "source": "tec_load_check"},
     "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.5}]},
]

SYNTH = {
    "answer_type": "cause", "root_cause": "part.tec",
    "causal_chain": ["part.tec", "metric.diode_temp", "metric.laser_power",
                     "metric.intensity", "kpi.effective_range"],
    "cited_evidence": ["ev.tecload", "ev.tempcorr", "ev.onset", "ev.channel", "ev.bogus"],
    "ruled_out": ["part.laser_module", "sub.optics", "sub.calibration"],
    "conflicts": ["metric.detector_temp", "log.reboot"],
    "recommended_action": "Run a laser-module swap-test to isolate laser vs thermal "
                          "before replacing the TEC module.",
}


def _backend() -> ScriptedBackend:
    return ScriptedBackend({
        "seed": json.dumps(SEED_HYPS),
        "propose": [json.dumps(p) for p in PROPOSE],
        "interpret": [json.dumps(i) for i in INTERPRET],
        "synthesize": json.dumps(SYNTH),
    })


@pytest.fixture(scope="module")
def run():
    case = generate("tec_degradation", ["D1", "B5", "D5", "A2"], seed=0)
    env = LidarEnvironment(case)
    answer = diagnose(env, backend=_backend(), budget=12)
    return case, answer


# --- accuracy ----------------------------------------------------------------

def test_concludes_tec_root_cause(run):
    case, ans = run
    assert ans.answer_type == "cause"
    assert ans.root_cause == "part.tec" == case.ground_truth.root_cause


def test_did_not_blame_the_trigger(run):
    case, ans = run
    trigger = case.ground_truth.trigger
    assert ans.root_cause != trigger
    assert trigger in ans.conflicts  # reboot demoted, not named as cause


# --- capability family -------------------------------------------------------

def test_cites_load_bearing_evidence(run):
    _case, ans = run
    assert {"ev.tecload", "ev.tempcorr", "ev.onset"} <= set(ans.cited_evidence)
    assert "ev.bogus" not in ans.cited_evidence  # hallucinated citation filtered


def test_surfaces_all_conflicts(run):
    case, ans = run
    assert set(case.ground_truth.conflicts) <= set(ans.conflicts)  # lying channel + trigger


def test_recommends_swap_test(run):
    _case, ans = run
    assert "swap" in (ans.recommended_action or "").lower()


# --- belief state & loop mechanics -------------------------------------------

def test_tec_is_the_confident_leader(run):
    _case, ans = run
    top, conf, margin = beliefs.leader(ans.final_graph)
    assert top.id == "h.tec" and top.node_ref == "part.tec"
    assert conf > 0.70 and margin > 0.20  # the §6.2 conclude condition


def test_decoy_is_down_weighted(run):
    _case, ans = run
    laser = next(h for h in ans.final_graph.hypotheses if h.id == "h.laser")
    assert beliefs.confidence(laser) < 0.5  # the discriminator demoted the decoy


def test_within_budget_and_concluded(run):
    _case, ans = run
    ig = ans.final_graph
    assert ig.status == "concluded"
    # one seed snapshot + one per executed step (≤budget) + final
    assert 1 < len(ig.snapshots) <= 12 + 2


def test_snapshots_grow_and_are_detached(run):
    _case, ans = run
    snaps = ans.final_graph.snapshots
    # evidence count is non-decreasing across snapshots (the graph grows)
    counts = [len(s.evidence) for s in snaps]
    assert counts == sorted(counts) and counts[-1] >= 5
    # snapshots are detached copies, not nested
    assert all(s.snapshots == [] for s in snaps)


def test_real_checks_executed(run):
    """The scripted interpretations rode on real check executions (provenance present)."""
    _case, ans = run
    sources = {e.source for e in ans.final_graph.evidence}
    assert {"tec_load_check", "temp_correlation_check", "onset_vs_event_check"} <= sources
