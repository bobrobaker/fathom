"""Deterministic spike for case5 `no_clean_cause` — the controller fails to ABSTAIN.

Gold: root_cause=None, answer_type="abstain" (the correct answer is abstention — every
real check on this case reads nominal/at-spec, so no single hypothesis is supported by
discriminating evidence). The controller instead concludes a wrong cause: accuracy=0,
abstention_calibration=0.

This spike drives the REAL LidarEnvironment(case5) + REAL diagnose()/beliefs/voi/scorer
with a ScriptedBackend whose interpret judgments are FAITHFUL to a competent LLM on this
ambiguous case (built from the real check payloads, verified below):

    config_diff           -> no relevant config change
    spatial_intensity     -> uniform drop (rules out window contamination)
    tec_load_check        -> TEC at 47% of limit (well within spec)
    temp_correlation      -> r=-0.24 (no correlation)
    detector_health_check -> no isolated bias signature
    channel_sanity_check  -> all channels live
    common_mode_check     -> no common-mode signature
    onset_vs_event_check  -> degradation onset PRECEDES the reboot (coincident, not causal)

The M1 failure: a competent LLM reading these *nominal* results does NOT cleanly rule
everything out — on an ambiguous case it credits weak mixed support ("TEC current is
fine, so it's behaving — mild + for h.tec"; "no config change, so calibration is the
likely culprit — mild + for h.calib"; etc.). Several hypotheses accumulate to the +3.0
log-odds clamp (conf 0.953) at once. The abstain gate `abstain = conf <= tau_min=0.55`
sees a high leader confidence and never trips, so the controller CONCLUDES — even though
the differential is *dispersed* (several hypotheses near the clamp; margin ≈ 0) and the
reboot demotion (M2) never entered the belief math.

We do NOT cheat by scripting an abstain. We script honest per-step interpretations; the
machinery's gate is what decides conclude-vs-abstain. The fix must flip that decision.
"""

import json

import pytest

from dh.controller import beliefs
from dh.controller.llm import ScriptedBackend
from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.eval.bespoke import score
from dh.generator import generate
from dh.generator.cases import CASES


# --- faithful scripted LLM for the no-clean-cause case -----------------------

SEED_HYPS = {"hypotheses": [
    {"id": "h.tec", "label": "TEC degradation", "node_ref": "part.tec"},
    {"id": "h.laser", "label": "laser power aging", "node_ref": "part.laser_module"},
    {"id": "h.optics", "label": "window contamination", "node_ref": "sub.optics"},
    {"id": "h.detector", "label": "detector bias drift", "node_ref": "sub.detector"},
    {"id": "h.calib", "label": "calibration drift", "node_ref": "sub.calibration"},
]}

PROPOSE = [
    {"actions": [{"type": "run_check", "args": {"name": "config_diff"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "spatial_intensity_check"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "tec_load_check"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "temp_correlation_check"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "detector_health_check"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "onset_vs_event_check",
                  "event_id": "log.reboot"}, "expected_discrimination": 0.6}]},
]

# Faithful interpretations of the (real) nominal payloads. This is the M1 pattern: an
# ambiguous case where nominal readings get credited as weak mixed support rather than
# clean rule-outs, so several hypotheses drift up toward the clamp simultaneously.
INTERPRET = [
    # config_diff: no config change. Weak + to "not a config/calib problem caused by a
    # change" is wrong-headed but is what an over-crediting model emits: reads "system
    # config is clean" as mild support that the hardware hypotheses are in play.
    {"evidence": {"id": "ev.config", "summary": "no relevant config change",
                  "source": "config_diff"},
     "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.9},
               {"hypothesis_id": "h.detector", "polarity": "+", "weight": 0.9},
               {"hypothesis_id": "h.calib", "polarity": "-", "weight": 0.6}]},
    # spatial_intensity: uniform drop -> rules out window contamination, credits the rest.
    {"evidence": {"id": "ev.spatial", "summary": "uniform intensity drop across regions",
                  "source": "spatial_intensity_check"},
     "links": [{"hypothesis_id": "h.optics", "polarity": "-", "weight": 1.2},
               {"hypothesis_id": "h.tec", "polarity": "+", "weight": 1.1},
               {"hypothesis_id": "h.laser", "polarity": "+", "weight": 2.0},
               {"hypothesis_id": "h.detector", "polarity": "+", "weight": 1.6}]},
    # tec_load_check: 47% of limit (in spec). M1: at-spec read credited POSITIVELY to TEC
    # ("the TEC is operating normally and present" -> still a live suspect).
    {"evidence": {"id": "ev.tecload", "summary": "TEC current 1.19A = 47% of 2.5A limit",
                  "source": "tec_load_check"},
     "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 1.3}]},
    # temp_correlation: r=-0.24 (no correlation). Over-credited as supporting calib/detector.
    {"evidence": {"id": "ev.tempcorr", "summary": "intensity vs diode temp r=-0.24 (weak)",
                  "source": "temp_correlation_check"},
     "links": [{"hypothesis_id": "h.calib", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "h.detector", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "h.laser", "polarity": "-", "weight": 0.5}]},
    # detector_health: no isolated bias signature. Mixed weak crediting again.
    {"evidence": {"id": "ev.dethealth", "summary": "no isolated detector bias signature",
                  "source": "detector_health_check"},
     "links": [{"hypothesis_id": "h.detector", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "h.calib", "polarity": "+", "weight": 1.0}]},
    # onset_vs_event: onset precedes reboot -> reboot demoted (conflicts only; M2: this
    # never becomes a belief link). A faithful model also credits "no clean trigger" weakly.
    {"evidence": {"id": "ev.onset", "summary": "degradation onset precedes the reboot",
                  "source": "onset_vs_event_check"},
     "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.4}],
     "conflicts": ["log.reboot"]},
]

# A competent synthesizer obeys the loop's gate: if the loop instructs ABSTAIN (prompt
# carries the ABSTAIN sentence) it abstains; otherwise it con-concludes its best guess.
CAUSE_SYNTH = {
    "answer_type": "cause", "root_cause": "part.tec",
    "causal_chain": ["part.tec", "metric.intensity", "kpi.effective_range"],
    "cited_evidence": ["ev.tecload", "ev.tempcorr"],
    "ruled_out": ["sub.optics"], "conflicts": ["log.reboot"],
    "recommended_action": None,
}
ABSTAIN_SYNTH = {
    "answer_type": "abstain", "root_cause": None,
    "causal_chain": [], "cited_evidence": [], "ruled_out": [],
    "conflicts": ["log.reboot"],
    "recommended_action": "No single cause is supported; recommend a swap-test sweep.",
}


class FaithfulBackend(ScriptedBackend):
    """ScriptedBackend that models a competent synthesizer obeying the loop's gate:
    when the loop's synthesize prompt instructs ABSTAIN, return abstain; else conclude.
    This is NOT cheating — the *gate* decides; the model just follows the instruction a
    real LLM would. interpret/seed/propose stay fully faithful & gate-independent."""

    def complete(self, prompt, *, system=None, max_tokens=1024):
        from dh.controller.llm import _read_tag
        if _read_tag(prompt) == "synthesize":
            self.calls.append("synthesize")
            return json.dumps(ABSTAIN_SYNTH if "ABSTAIN" in prompt else CAUSE_SYNTH)
        return super().complete(prompt, system=system, max_tokens=max_tokens)


def _backend() -> FaithfulBackend:
    return FaithfulBackend({
        "seed": json.dumps(SEED_HYPS),
        "propose": [json.dumps(p) for p in PROPOSE],
        "interpret": [json.dumps(i) for i in INTERPRET],
    })


@pytest.fixture(scope="module")
def run():
    spec = next(c for c in CASES if c.id == "case5")
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    env = LidarEnvironment(case)
    answer = diagnose(env, backend=_backend(), budget=12)
    return case, answer


# --- structural confirmation: gold really is abstain, scorer keys on answer_type ---

def test_gold_is_abstain(run):
    case, _ans = run
    assert case.ground_truth.answer_type == "abstain"
    assert case.ground_truth.root_cause is None


def test_differential_is_saturated_and_dispersed(run):
    """The M1 signature: several hypotheses ride the +3.0 clamp at once, margin ~ 0."""
    _case, ans = run
    confs = sorted((beliefs.confidence(h) for h in ans.final_graph.hypotheses),
                   reverse=True)
    top, conf, margin = beliefs.leader(ans.final_graph)
    saturated = [c for c in confs if c > 0.90]
    assert len(saturated) >= 2, f"expected dispersed saturation, got {confs}"
    assert margin < 0.10, f"expected near-zero margin, got {margin}"
    assert conf > 0.55, "leader must clear tau_min so the conf-only gate never trips"


# --- headline: the controller must ABSTAIN on a saturated-but-dispersed state ---
# BEFORE the fix this test FAILS (the controller concludes part.tec: answer_type=="cause",
# accuracy 0, abstention_calibration 0). AFTER the M4 margin-gate fix it PASSES (abstains).

def test_controller_abstains_on_no_clean_cause(run):
    """The correct answer is abstain; the dispersed differential must trip the gate."""
    _case, ans = run
    assert ans.answer_type == "abstain"
    assert ans.root_cause is None


def test_scorer_rewards_correct_abstain(run):
    """With the fix, the abstain-keyed scorer gives full accuracy + calibration."""
    case, ans = run
    s = score(ans, case, solver="controller")
    assert s.accuracy == 1.0
    assert s.abstention_calibration == 1.0
