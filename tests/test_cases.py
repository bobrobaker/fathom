"""M7 (partial) — the symmetry (#2) and abstain (#5) cases (spec §5.3).

Case #2 (laser aging) is the decoy-as-true-cause: same symptom, no thermal signature —
the controller must not reflexively blame TEC. Case #5 has no clean cause — the correct
answer is a calibrated abstain.
"""

import json
import statistics as st

import pytest

from dh.controller.llm import ScriptedBackend
from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.generator import generate
from dh.generator.cases import CASES_BY_ID, authored_cases


@pytest.fixture(scope="module")
def laser():
    return generate("laser_aging", ["D5", "A1"], seed=1)


@pytest.fixture(scope="module")
def abstain():
    return generate("no_clean_cause", ["E1"], seed=4)


# --- case #2: laser aging (symmetry vs TEC) ----------------------------------

def test_laser_has_no_thermal_signature(laser):
    env = LidarEnvironment(laser)
    assert env.run_check("temp_correlation_check")["correlated"] is False  # not temp-driven
    assert env.run_check("tec_load_check")["at_limit"] is False            # TEC nominal
    assert env.run_check("channel_sanity_check")["stuck"] is False         # no lying channel
    sig = {s.signal: s for s in laser.telemetry}
    assert st.mean(sig["laser_power_mW"].v[-5:]) < 45      # power actually dropped
    assert abs(st.mean(sig["laser_diode_temp_C"].v[-5:]) - 25.2) < 1.0  # diode nominal


def test_laser_ground_truth(laser):
    gt = laser.ground_truth
    assert gt.answer_type == "cause" and gt.root_cause == "part.laser_module"
    assert "part.tec" in gt.decoys  # TEC is now the (false) decoy
    assert not any(a.id == "err.tec_load" for a in laser.artifacts)  # no TEC error


# --- case #5: no clean cause (abstain) ---------------------------------------

def test_abstain_ground_truth_and_nominal(abstain):
    gt = abstain.ground_truth
    assert gt.answer_type == "abstain" and gt.root_cause is None
    env = LidarEnvironment(abstain)
    assert env.run_check("temp_correlation_check")["correlated"] is False
    assert env.run_check("tec_load_check")["at_limit"] is False
    sig = {s.signal: s for s in abstain.telemetry}
    assert st.mean(sig["effective_max_range_m"].v[-5:]) > 118  # recovered / within spec


def test_controller_abstains_when_evidence_is_weak(abstain):
    """With no hypothesis crossing τ_min, the controller must abstain (E1)."""
    backend = ScriptedBackend({
        "seed": json.dumps({"hypotheses": [
            {"id": "h.tec", "label": "TEC", "node_ref": "part.tec"},
            {"id": "h.laser", "label": "laser", "node_ref": "part.laser_module"}]}),
        "propose": [
            json.dumps({"actions": [{"type": "run_check",
                        "args": {"name": "temp_correlation_check"}, "expected_discrimination": 0.5}]}),
            json.dumps({"actions": [{"type": "run_check",
                        "args": {"name": "tec_load_check"}, "expected_discrimination": 0.5}]}),
        ],
        # evidence with no links → no hypothesis accumulates weight → leader stays ~0.5
        "interpret": [
            json.dumps({"evidence": {"id": "ev.tc", "summary": "no correlation",
                        "source": "temp_correlation_check"}, "links": []}),
            json.dumps({"evidence": {"id": "ev.tl", "summary": "TEC nominal",
                        "source": "tec_load_check"}, "links": []}),
        ],
        "synthesize": json.dumps({"answer_type": "abstain"}),
    })
    ans = diagnose(LidarEnvironment(abstain), backend=backend, budget=6)
    assert ans.answer_type == "abstain"
    assert ans.root_cause is None
    assert ans.final_graph.status == "abstained"


# --- case #3: window contamination (spatial) ---------------------------------

@pytest.fixture(scope="module")
def window():
    return generate("window_contamination", ["C-spatial", "A3"], seed=2)


def test_window_is_spatially_localized(window):
    env = LidarEnvironment(window)
    assert env.run_check("spatial_intensity_check")["localized"] is True  # the discriminator
    assert env.run_check("temp_correlation_check")["correlated"] is False  # not thermal
    assert env.run_check("tec_load_check")["at_limit"] is False            # not thermal


def test_window_ground_truth_and_consistent_corpus(window):
    gt = window.ground_truth
    assert gt.answer_type == "cause" and gt.root_cause == "part.window"
    # the "window cleaned, no improvement" action is excluded — it would contradict the cause
    assert not any(a.id == "act.window_clean" for a in window.artifacts)


# --- registry ----------------------------------------------------------------

def test_four_cases_authored():
    ids = {c.id for c in authored_cases()}
    assert {"case1", "case2", "case3", "case5"} <= ids
    assert all(CASES_BY_ID[i].authored for i in ids)
