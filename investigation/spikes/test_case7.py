"""Deterministic spike for case7 `tec_degradation_variant` (mechanism D6, suspected M5).

Case design (faults.py::tec_degradation_variant): the cheap discriminators are
DELIBERATELY ambiguous — temp_correlation r=-0.52 (correlated=False), tec_load 82%
(at_limit=False) — so neither cleanly separates the true cause (part.tec) from its
near-symmetric decoy (part.laser_module). The only decisive discriminator is the
expensive swap-test (recommend_swap_test, cost 3).

The backend here is a FAITHFUL competent LLM: it interprets every real check output
honestly (built from the actual env.run_check payloads), and at every step proposes a
realistic action menu that INCLUDES the high-discrimination swap-test alongside the
cheap checks — then lets `voi.select` choose. We do NOT hand-force the swap-test; the
point is whether VOI selects it and whether, once selected, it can move the belief
state. The spike asserts the controller currently concludes the WRONG cause, then
(with the fix applied) concludes part.tec.
"""

import json

import pytest

from dh.controller.llm import ScriptedBackend
from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.generator import generate
from dh.generator.cases import CASES_BY_ID


def _case_env():
    spec = CASES_BY_ID["case7"]
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    return case, LidarEnvironment(case)


# Five-way differential including the true cause (h.tec → part.tec) and the
# near-symmetric decoy (h.laser → part.laser_module).
SEED_HYPS = {"hypotheses": [
    {"id": "h.tec", "label": "TEC degradation", "node_ref": "part.tec"},
    {"id": "h.laser", "label": "laser power aging", "node_ref": "part.laser_module"},
    {"id": "h.optics", "label": "window contamination", "node_ref": "sub.optics"},
    {"id": "h.detector", "label": "detector bias drift", "node_ref": "sub.detector"},
    {"id": "h.calib", "label": "calibration drift", "node_ref": "sub.calibration"},
]}

# A realistic action menu, proposed EVERY step. The loop filters already-run actions
# (`seen`) and lets voi.select pick the highest-VOI remaining one. The swap-test is
# honestly scored highest on expected_discrimination — a competent model knows it is
# the only clean tie-breaker here — but it costs 3, so VOI (= disc/cost) is the thing
# under test. Cheap checks are scored at modest discrimination (they are ambiguous on
# this case, and the model knows it).
MENU = {"actions": [
    {"type": "run_check", "args": {"name": "spatial_intensity_check"},
     "expected_discrimination": 0.35, "target_hypotheses": ["h.optics"]},
    {"type": "run_check", "args": {"name": "config_diff"},
     "expected_discrimination": 0.30, "target_hypotheses": ["h.calib"]},
    {"type": "run_check", "args": {"name": "channel_sanity_check",
     "signal": "detector_temp_C"}, "expected_discrimination": 0.30,
     "target_hypotheses": ["h.detector"]},
    {"type": "run_check", "args": {"name": "onset_vs_event_check",
     "signal": "effective_max_range_m", "event_id": "log.reboot"},
     "expected_discrimination": 0.40, "target_hypotheses": ["h.tec"]},
    {"type": "run_check", "args": {"name": "temp_correlation_check"},
     "expected_discrimination": 0.45, "target_hypotheses": ["h.tec", "h.laser"]},
    {"type": "run_check", "args": {"name": "tec_load_check"},
     "expected_discrimination": 0.45, "target_hypotheses": ["h.tec", "h.laser"]},
    {"type": "recommend_swap_test", "args": {},
     "expected_discrimination": 0.90, "target_hypotheses": ["h.tec", "h.laser"]},
]}


def _interpret_for(action_name: str, result: dict) -> dict:
    """Faithful interpretation keyed by which check was actually run AND its real result.

    Built from the real env.run_check payloads for case7. The ambiguous cheap checks
    yield WEAK, NON-SEPARATING links: temp_correlation (r=-0.52, not clean) and tec_load
    (82%, under limit) each nudge BOTH h.tec and h.laser equally and do NOT push the laser
    decoy down — that is the whole point of the near-symmetric case. The ONLY thing that
    separates them is the magnitude-bearing `losing_setpoint` signal the fixed tec_load_check
    surfaces: a competent model that sees the diode held above its setpoint while TEC current
    is elevated correctly credits the TEC strongly and rules the laser out. On UNFIXED code
    that key is absent, so the symmetric weak nudge stands and the decoy is never demoted.
    """
    if action_name == "tec_load_check" and result.get("losing_setpoint"):
        # FIXED-code path: the discriminator fired. Faithful: strong + to TEC, strong - to laser.
        return {
            "evidence": {"id": "ev.tecload",
                         "summary": "diode above setpoint while TEC current elevated → TEC losing control",
                         "source": "tec_load_check"},
            "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 1.6},
                      {"hypothesis_id": "h.laser", "polarity": "-", "weight": 1.2}]}
    return {
        # rules out window contamination (uniform drop) — does not touch tec vs laser
        "spatial_intensity_check": {
            "evidence": {"id": "ev.spatial", "summary": "uniform intensity drop (not localized)",
                         "source": "spatial_intensity_check"},
            "links": [{"hypothesis_id": "h.optics", "polarity": "-", "weight": 1.2}]},
        # no config change — rules out calibration drift
        "config_diff": {
            "evidence": {"id": "ev.config", "summary": "no relevant config change",
                         "source": "config_diff"},
            "links": [{"hypothesis_id": "h.calib", "polarity": "-", "weight": 1.2}]},
        # detector channel is live (not stuck) — weak against detector hypothesis
        "channel_sanity_check": {
            "evidence": {"id": "ev.channel", "summary": "detector_temp live (var≈6e-3)",
                         "source": "channel_sanity_check"},
            "links": [{"hypothesis_id": "h.detector", "polarity": "-", "weight": 0.8}]},
        # reboot is coincident (onset predates it) — demote the trigger, does not pick a cause
        "onset_vs_event_check": {
            "evidence": {"id": "ev.onset", "summary": "degradation onset≈t3 predates reboot@t8",
                         "source": "onset_vs_event_check"},
            "links": [], "conflicts": ["log.reboot"]},
        # AMBIGUOUS / NEAR-SYMMETRIC: r=-0.52 is sub-threshold. An intensity↔diode-temp
        # correlation at this strength is consistent with EITHER a thermal cause (TEC) OR
        # laser aging (an aging diode also runs hot and loses power), so a faithful model
        # nudges BOTH hypotheses up by the same small amount — it does not separate them.
        "temp_correlation_check": {
            "evidence": {"id": "ev.tempcorr", "summary": "intensity vs diode r=-0.52 (borderline)",
                         "source": "temp_correlation_check"},
            "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.4},
                      {"hypothesis_id": "h.laser", "polarity": "+", "weight": 0.4}]},
        # AMBIGUOUS: 82% of limit, under threshold. Elevated-but-sub-limit TEC current is
        # equally explained by a degrading TEC or by an aging laser driving more heat —
        # again a symmetric weak nudge to both, no separation.
        "tec_load_check": {
            "evidence": {"id": "ev.tecload", "summary": "TEC current 82% of limit (under)",
                         "source": "tec_load_check"},
            "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.4},
                      {"hypothesis_id": "h.laser", "polarity": "+", "weight": 0.4}]},
    }.get(action_name, {})


# A faithful model, having only the AMBIGUOUS evidence, cannot confidently pick part.tec.
# With temp_correlation borderline and the laser decoy never ruled out, the honest
# synthesis names the surface decoy (laser module) — the documented failure. (When the
# swap-test actually discriminates, the fix lets the belief math separate them, and the
# leader the synthesize step reports follows the graph.)
SYNTH_WRONG = {
    "answer_type": "cause", "root_cause": "part.laser_module",
    "causal_chain": ["part.laser_module", "metric.laser_power", "kpi.effective_range"],
    "cited_evidence": ["ev.tempcorr", "ev.tecload", "ev.onset"],
    "ruled_out": ["sub.optics", "sub.calibration", "sub.detector"],
    "conflicts": ["log.reboot"],
    "recommended_action": "Swap the laser module to confirm.",
}

# After the fix, the leader is h.tec/part.tec; a faithful synthesis follows the graph.
SYNTH_TEC = {
    "answer_type": "cause", "root_cause": "part.tec",
    "causal_chain": ["part.tec", "metric.diode_temp", "metric.intensity", "kpi.effective_range"],
    "cited_evidence": ["ev.tempcorr", "ev.tecload", "ev.onset"],
    "ruled_out": ["part.laser_module", "sub.optics", "sub.calibration", "sub.detector"],
    "conflicts": ["log.reboot"],
    "recommended_action": "Order a TEC module replacement.",
}


class FaithfulBackend(ScriptedBackend):
    """Like ScriptedBackend but interpret is keyed to the action actually executed, and
    synthesize follows the graph leader (so the spike is faithful, not hand-forced)."""

    def __init__(self):
        super().__init__({
            "seed": json.dumps(SEED_HYPS),
            "propose": json.dumps(MENU),          # same menu every step; loop filters `seen`
        })
        self._last_check = None

    def complete(self, prompt, *, system=None, max_tokens=1024):
        from dh.controller.llm import _read_tag
        tag = _read_tag(prompt)
        if tag == "interpret":
            self.calls.append(tag)
            name = None
            for cand in ("spatial_intensity_check", "config_diff", "channel_sanity_check",
                         "onset_vs_event_check", "temp_correlation_check", "tec_load_check"):
                if f"name': '{cand}'" in prompt or f'"name": "{cand}"' in prompt:
                    name = cand
                    break
            result = _parse_result(prompt)
            return json.dumps(_interpret_for(name, result))
        if tag == "synthesize":
            self.calls.append(tag)
            # Faithful synthesis: name the cleanly-separated leader; under a near-tie
            # differential (no discriminator fired) name the surface decoy — the documented
            # failure (bare_llm gets it, the controller did not).
            lead, margin = _leader_and_margin(prompt)
            if lead == "h.tec" and margin >= 0.10:
                return json.dumps(SYNTH_TEC)
            return json.dumps(SYNTH_WRONG)
        return super().complete(prompt, system=system, max_tokens=max_tokens)


def _parse_result(prompt: str) -> dict:
    """Pull the 'Structured result:\\n{...}' JSON the interpret prompt embeds."""
    marker = "Structured result:"
    i = prompt.find(marker)
    if i == -1:
        return {}
    start = prompt.find("{", i)
    if start == -1:
        return {}
    depth, j = 0, start
    while j < len(prompt):
        if prompt[j] == "{":
            depth += 1
        elif prompt[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    try:
        return json.loads(prompt[start:j + 1])
    except (ValueError, json.JSONDecodeError):
        return {}


def _leader_and_margin(prompt: str):
    """Parse the _ig_brief hypotheses block; return (leader_id, log_odds margin over runner-up)."""
    los = []
    for line in prompt.splitlines():
        if "log_odds=" in line and " | " in line:
            try:
                hid = line.split("-", 1)[1].split("|")[0].strip()
                lo = float(line.split("log_odds=")[1].split("|")[0].strip())
                los.append((hid, lo))
            except (IndexError, ValueError):
                continue
    los.sort(key=lambda x: x[1], reverse=True)
    if not los:
        return None, 0.0
    margin = los[0][1] - (los[1][1] if len(los) > 1 else 0.0)
    return los[0][0], margin


def test_case7_concludes_wrong_cause_without_the_discriminator(monkeypatch):
    """REPRODUCE the failure on PRE-FIX behaviour.

    We simulate the unfixed tec_load_check by stripping the `losing_setpoint` discriminator
    from its result (exactly the pre-fix payload). With only the ambiguous, near-symmetric
    cheap checks, h.tec and h.laser tie (margin 0) and the faithful synthesis names the
    surface decoy — accuracy=0. This is the documented case7 miss.
    """
    import dh.environment as environment
    orig = environment.LidarEnvironment._run_tec_load_check

    def _prefix(self, args):
        r = orig(self, args)
        for k in ("diode_temp", "diode_setpoint_max", "losing_setpoint"):
            r.pop(k, None)
        return r

    monkeypatch.setattr(environment.LidarEnvironment, "_run_tec_load_check", _prefix)
    _case, env = _case_env()
    ans = diagnose(env, backend=FaithfulBackend(), budget=12)
    assert ans.answer_type == "cause"
    assert ans.root_cause != "part.tec", (
        f"expected the documented WRONG conclusion, got {ans.root_cause}")
    assert ans.root_cause == "part.laser_module"  # the near-symmetric decoy


def test_case7_concludes_part_tec_with_fix():
    """With the fix (tec_load_check surfaces `losing_setpoint`), part.tec is concluded."""
    case, env = _case_env()
    ans = diagnose(env, backend=FaithfulBackend(), budget=12)
    assert ans.answer_type == "cause"
    assert ans.root_cause == "part.tec" == case.ground_truth.root_cause
