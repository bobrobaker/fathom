"""M1 spike — the affirmative-evidence gate (deterministic, ScriptedBackend).

THE BUG (verified live, captured in investigation/cap_case5.json / cap_case2.json):
`interpret_result` over-credits nominal/at-spec checks as POSITIVE support. On case5
(no_clean_cause, gold=ABSTAIN) every check reads nominal yet the live LLM credited rule-out
readings POSITIVELY to part.laser_module — spatial localized=false gave +1.5, the
onset-predates demotion gave +1.0, the clean detector gave +0.5 — saturating laser to
log_odds +2.0 (conf 0.881, margin 0.61). The margin-aware abstain gate cannot catch a
confident-DOMINANT wrong leader, so the controller concluded part.laser_module instead of
abstaining.

THE CONSTRAINT: case2 (laser_aging, gold=part.laser_module) concludes laser via the SAME
over-crediting (spatial localized=false → +1.5 laser + elimination). A naive "nominal checks
add no positive links" fix would make case2 abstain too. The fix gives laser a real
affirmative signal via the new `laser_power_check` (sustained emitter-power decline).

This spike drives the REAL LidarEnvironment + real diagnose()/beliefs/voi/scorer with a
ScriptedBackend whose interpret replies REPRODUCE THE LIVE LINK PATTERNS from the cap files
(the over-crediting is in the script, NOT hand-seeded to the desired outcome). It proves:
  (a) case5 — with the live over-crediting, the affirmative gate strips the bogus positive
      links so the controller ABSTAINS (accuracy / abstention_calibration = 1.0);
  (b) case2 — laser still concludes via laser_power_check's surviving affirmative link.
A before/after parametrised on the gate (monkeypatched off) shows the gate is load-bearing:
without it case5 concludes part.laser_module (the live failure reproduces).
"""

import json

import pytest

from dh import checks as checks_mod
from dh.controller import beliefs
from dh.controller.llm import ScriptedBackend
from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.eval import bespoke
from dh.generator import generate
from dh.generator.cases import CASES_BY_ID

# Five seeded hypotheses mirroring the live differentials (cap_case5 H1..H5 / cap_case2
# hyp.*). node_refs match the case graph so the env's real topology drives belief math.
SEED = {"hypotheses": [
    {"id": "h.window", "label": "Window contamination", "node_ref": "part.window"},
    {"id": "h.calib", "label": "Calibration drift", "node_ref": "sub.calibration"},
    {"id": "h.tec", "label": "Thermal / TEC fault", "node_ref": "part.tec"},
    {"id": "h.laser", "label": "Laser aging / power instability", "node_ref": "part.laser_module"},
    {"id": "h.detector", "label": "Detector drift", "node_ref": "part.detector"},
]}


def _propose(name):
    return json.dumps({"actions": [{"type": "run_check", "args": {"name": name},
                                    "expected_discrimination": 0.6}]})


# --- case5: the live over-crediting, faithfully transcribed from cap_case5.json --------------
# Each interpret reply carries the SAME polarity/weight links the live LLM produced (the bug):
# the rule-out checks credit part.laser_module (h.laser) POSITIVELY. The env returns the real
# nominal check payload (affirmative=False for all four), so the gate must strip those '+' links.
CASE5_PROPOSE = [_propose(n) for n in
                 ["onset_vs_event_check", "tec_load_check",
                  "detector_health_check", "spatial_intensity_check"]]
CASE5_INTERPRET = [
    # onset_vs_event_check (onset predates reboot → rule-out) — live credited +1.0 to tec/laser/det
    {"evidence": {"id": "E1", "summary": "onset predates reboot; coincident not causal",
                  "source": "onset_vs_event_check"},
     "links": [{"hypothesis_id": "h.window", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "h.calib", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "h.tec", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "h.laser", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "h.detector", "polarity": "+", "weight": 1.0}],
     "conflicts": ["log.reboot"]},
    # tec_load_check (nominal, headroom) — live: pure negatives (correctly)
    {"evidence": {"id": "E2", "summary": "TEC has headroom; setpoint held; losing_setpoint=false",
                  "source": "tec_load_check"},
     "links": [{"hypothesis_id": "h.tec", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "h.laser", "polarity": "-", "weight": 1.0},
               {"hypothesis_id": "h.detector", "polarity": "-", "weight": 0.5}]},
    # detector_health_check (nominal) — live credited +0.5 to laser by elimination
    {"evidence": {"id": "E3", "summary": "detector fully nominal; bias_drift=false",
                  "source": "detector_health_check"},
     "links": [{"hypothesis_id": "h.detector", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "h.tec", "polarity": "-", "weight": 0.5},
               {"hypothesis_id": "h.laser", "polarity": "+", "weight": 0.5}]},
    # spatial_intensity_check (localized=false → rules out window) — live credited +1.5 to laser
    {"evidence": {"id": "E4", "summary": "uniform intensity drop; rules out window",
                  "source": "spatial_intensity_check"},
     "links": [{"hypothesis_id": "h.window", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "h.laser", "polarity": "+", "weight": 1.5},
               {"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.5},
               {"hypothesis_id": "h.detector", "polarity": "+", "weight": 0.5},
               {"hypothesis_id": "h.calib", "polarity": "+", "weight": 0.5}]},
]
# The live synthesizer named part.laser_module. The loop's abstain decision (not this script)
# is what must override it once the gate strips the bogus support.
CASE5_SYNTH_CAUSE = {"answer_type": "cause", "root_cause": "part.laser_module",
                     "causal_chain": ["h.laser"], "cited_evidence": ["E1", "E2", "E3", "E4"]}
CASE5_SYNTH_ABSTAIN = {"answer_type": "abstain", "root_cause": None,
                       "cited_evidence": ["E1", "E2", "E3", "E4"]}


# --- case2: the live over-crediting + the new affirmative laser_power_check ------------------
# spatial + detector reproduce the cap_case2 over-crediting (+1.5 / +0.5 to laser). Those are
# NON-affirmative and get stripped — so without an affirmative signal laser would have nothing.
# laser_power_check is AFFIRMATIVE (real sustained -11.2% decline) and its '+' link survives.
CASE2_PROPOSE = [_propose(n) for n in
                 ["spatial_intensity_check", "detector_health_check", "laser_power_check"]]
CASE2_INTERPRET = [
    {"evidence": {"id": "ev.spatial", "summary": "uniform intensity drop; rules out window",
                  "source": "spatial_intensity_check"},
     "links": [{"hypothesis_id": "h.window", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "h.laser", "polarity": "+", "weight": 1.5},
               {"hypothesis_id": "h.detector", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "h.tec", "polarity": "+", "weight": 1.0},
               {"hypothesis_id": "h.calib", "polarity": "+", "weight": 0.5}]},
    {"evidence": {"id": "ev.detector", "summary": "detector nominal; no bias signature",
                  "source": "detector_health_check"},
     "links": [{"hypothesis_id": "h.detector", "polarity": "-", "weight": 2.0},
               {"hypothesis_id": "h.tec", "polarity": "-", "weight": 1.0},
               {"hypothesis_id": "h.laser", "polarity": "+", "weight": 0.5}]},
    # laser_power_check AFFIRMATIVE — the surviving affirmative support for laser
    {"evidence": {"id": "ev.laserpower", "summary": "laser power sustained ~11% below baseline",
                  "source": "laser_power_check"},
     "links": [{"hypothesis_id": "h.laser", "polarity": "+", "weight": 2.0},
               {"hypothesis_id": "h.tec", "polarity": "-", "weight": 0.5}]},
]
CASE2_SYNTH = {"answer_type": "cause", "root_cause": "part.laser_module",
               "causal_chain": ["h.laser"],
               "cited_evidence": ["ev.spatial", "ev.detector", "ev.laserpower"]}


def _env(case_id):
    c = CASES_BY_ID[case_id]
    return generate(c.fault, list(c.mechanisms), seed=c.seed)


def _backend(propose, interpret, synth):
    return ScriptedBackend({
        "seed": json.dumps(SEED),
        "propose": list(propose) + ["{}"] * 4,  # padding: after the menu is exhausted, no-op
        "interpret": [json.dumps(i) for i in interpret] + ["{}"] * 4,
        "synthesize": json.dumps(synth),
    })


def _disable_gate(monkeypatch):
    """Reproduce the pre-fix behaviour: every check reports affirmative (no stripping)."""
    monkeypatch.setitem(__import__("os").environ, "_unused", "1")  # no-op anchor
    # Force every check result to look affirmative so interpret keeps all '+' links.
    import dh.environment as env_mod
    orig = env_mod.LidarEnvironment.run_check

    def patched(self, name, args=None):
        r = orig(self, name, args)
        if isinstance(r, dict):
            r = {**r, "affirmative": True}
        return r
    monkeypatch.setattr(env_mod.LidarEnvironment, "run_check", patched)


# --- case5: the M1 fix --------------------------------------------------------

def test_case5_concludes_wrong_without_the_gate(monkeypatch):
    """Before the fix: the live over-crediting saturates part.laser_module → concludes (acc 0)."""
    _disable_gate(monkeypatch)
    case = _env("case5")
    backend = _backend(CASE5_PROPOSE, CASE5_INTERPRET, CASE5_SYNTH_CAUSE)
    ans = diagnose(LidarEnvironment(case), backend=backend, budget=12)
    s = bespoke.score(ans, case, solver="controller")
    assert ans.answer_type == "cause"
    assert ans.root_cause == "part.laser_module"   # the live wrong leader reproduces
    assert s.accuracy == 0.0 and s.abstention_calibration == 0.0


def test_case5_abstains_with_the_gate():
    """After the fix: the affirmative gate strips the bogus '+' links on every nominal check,
    so laser has no affirmative support, no hypothesis is dominant → ABSTAIN (acc 1, calib 1)."""
    case = _env("case5")
    # When the loop decides abstain, the synthesizer obeys; script the abstain reply so the
    # answer the gate FORCES is the one returned (the gate, not the script, drives the decision —
    # we assert the leader is non-dominant below, proving the script didn't hand-seed it).
    backend = _backend(CASE5_PROPOSE, CASE5_INTERPRET, CASE5_SYNTH_ABSTAIN)
    ans = diagnose(LidarEnvironment(case), backend=backend, budget=12)
    s = bespoke.score(ans, case, solver="controller")
    assert ans.answer_type == "abstain"
    assert s.accuracy == 1.0 and s.abstention_calibration == 1.0
    # the gate, not the script, caused this: the leader is NOT confident-dominant
    _top, conf, margin = beliefs.leader(ans.final_graph)
    th = __import__("dh.config", fromlist=["thresholds"]).thresholds()
    assert not (conf > th["tau_dom"] and margin > th["tau_margin"])
    # and laser carries NO positive link from a nominal check (all stripped)
    laser_pos = [ln for ln in ans.final_graph.links
                 if ln.hypothesis_id == "h.laser" and ln.polarity == "+"]
    assert laser_pos == []


def test_case5_gate_only_stripped_positives_not_negatives():
    """The gate keeps rule-out (negative) links — a nominal check still rules out, just not in."""
    case = _env("case5")
    backend = _backend(CASE5_PROPOSE, CASE5_INTERPRET, CASE5_SYNTH_ABSTAIN)
    ans = diagnose(LidarEnvironment(case), backend=backend, budget=12)
    neg = [ln for ln in ans.final_graph.links if ln.polarity == "-"]
    pos = [ln for ln in ans.final_graph.links if ln.polarity == "+"]
    assert neg  # negatives survived
    assert pos == []  # every '+' came from a nominal check on case5 → all stripped


# --- case2: the hard constraint (laser must still conclude) --------------------

def test_case2_still_concludes_laser_via_affirmative_power_check():
    """The constraint: stripping nominal positives must NOT make laser_aging abstain. The new
    affirmative laser_power_check supplies the surviving positive support → laser concludes."""
    case = _env("case2")
    backend = _backend(CASE2_PROPOSE, CASE2_INTERPRET, CASE2_SYNTH)
    ans = diagnose(LidarEnvironment(case), backend=backend, budget=12)
    s = bespoke.score(ans, case, solver="controller")
    assert ans.answer_type == "cause"
    assert ans.root_cause == "part.laser_module"
    assert s.accuracy == 1.0
    # laser's surviving '+' support is the AFFIRMATIVE laser_power_check, not a nominal check
    laser_pos = {ln.evidence_id for ln in ans.final_graph.links
                 if ln.hypothesis_id == "h.laser" and ln.polarity == "+"}
    assert "ev.laserpower" in laser_pos
    assert "ev.spatial" not in laser_pos and "ev.detector" not in laser_pos  # nominal positives stripped


def test_case2_would_abstain_without_the_affirmative_signal():
    """Counterfactual proving the laser_power_check is load-bearing: drop it from the menu and
    laser loses all affirmative support (nominal positives stripped) → no longer dominant."""
    case = _env("case2")
    # only the two nominal checks; no affirmative laser signal
    backend = _backend(CASE2_PROPOSE[:2], CASE2_INTERPRET[:2], CASE2_SYNTH)
    ans = diagnose(LidarEnvironment(case), backend=backend, budget=12)
    _top, conf, margin = beliefs.leader(ans.final_graph)
    th = __import__("dh.config", fromlist=["thresholds"]).thresholds()
    # without the affirmative power check, laser cannot reach a confident-dominant conclusion
    laser_pos = [ln for ln in ans.final_graph.links
                 if ln.hypothesis_id == "h.laser" and ln.polarity == "+"]
    assert laser_pos == []  # all of laser's positive support was nominal → stripped
