"""case8 `common_mode_power` deterministic spike (investigation, NOT live).

Target: case8 (`salient_is_cause=True`, mechanisms A4/A5). Gold root_cause=`sub.power`,
trigger=None, conflicts=[]. A power-mode change overloaded the supply, so several
nominally-independent channels (laser power, dark count, TEC current) degrade *together*
with a common onset — looking like two/three separate faults. The `common_mode_check`
returns `common_mode=true`, and the real graph wires the shared upstream cause as
`sub.power -affects-> sub.thermal -affects-> {sub.laser, sub.detector}`.

The controller seeds `sub.power` (the affects-BFS reaches it) and the scorer accepts
`sub.power` — so the 0 is neither a seeding gap nor a scorer artifact. The failure is
that the LLM interpret step credits the *surface* faults (laser/detector decoys)
positively (M1) and the deterministic conflict sweep is demotion-only — it never runs
`common_mode_check` and never *promotes* the shared upstream cause into the belief math
(M3/M2). So the belief leader becomes a decoy and the answer misses `sub.power`.

This spike scripts a FAITHFUL-but-imperfect model (the live failure mode): it interprets
the real check payloads the way a competent model plausibly does — crediting the visible
laser-power drop and detector bias-drift to those decoys — and synthesizes the belief
leader. It drives the REAL env + REAL diagnose()/beliefs/conflict-sweep/scorer.

  - test_current_code_misses_sub_power : reproduces the miss (leader is a decoy; accuracy 0).
  - test_fix_concludes_sub_power       : with the common-mode promotion fix, leader and
                                         answer become sub.power (accuracy 1). xfails on
                                         current code, passes after the fix.
"""

import json

import pytest

from dh.controller import beliefs
from dh.controller.llm import ScriptedBackend
from dh.controller.loop import diagnose
from dh.eval.bespoke import score
from dh.environment import LidarEnvironment
from dh.generator import generate
from dh.generator.cases import CASES_BY_ID


# --- faithful scripted model (built from the real case graph + real check payloads) ----

# Seed differential — one hypothesis per real seeded candidate subsystem, including
# sub.power (the affects-BFS reaches it). node_ref points at the real subsystem id.
SEED_HYPS = {"hypotheses": [
    {"id": "h.laser", "label": "laser power aging", "node_ref": "sub.laser"},
    {"id": "h.detector", "label": "detector bias drift", "node_ref": "sub.detector"},
    {"id": "h.thermal", "label": "TEC degradation", "node_ref": "sub.thermal"},
    {"id": "h.optics", "label": "window contamination", "node_ref": "sub.optics"},
    {"id": "h.calib", "label": "calibration drift", "node_ref": "sub.calibration"},
    {"id": "h.power", "label": "scanner power supply", "node_ref": "sub.power"},
]}

# Real checks, proposed in order. These are the discriminating checks a competent model
# picks here; each rides a REAL env.run_check execution.
PROPOSE = [
    {"actions": [{"type": "run_check", "args": {"name": "config_diff"},
                  "expected_discrimination": 0.4}]},
    {"actions": [{"type": "run_check", "args": {"name": "common_mode_check"},
                  "expected_discrimination": 0.7}]},
    {"actions": [{"type": "run_check", "args": {"name": "detector_health_check"},
                  "expected_discrimination": 0.6}]},
    {"actions": [{"type": "run_check", "args": {"name": "temp_correlation_check"},
                  "expected_discrimination": 0.6}]},
]

# Faithful interpretations of the REAL payloads (config_diff: scan_params high_power_v2;
# common_mode: 3 channels, spread 1.25d, common_mode=true; detector_health: bias_drift=true;
# temp_correlation: r=0.14 no correlation). This is the LIVE failure mode (M1): the model
# reads the visible single-channel drops as support for the surface faults and does NOT
# convert the common-mode signature into upstream support for sub.power — the common-mode
# evidence is, at best, weakly noted, never promoting the shared cause.
INTERPRET = [
    # config_diff — a recent scan_params change; model notes it but can't place a subsystem
    {"evidence": {"id": "ev.config", "summary": "scan_params changed to high_power_v2",
                  "source": "config_diff"},
     "links": []},
    # common_mode_check — model SEES the common-mode flag but (the failure) does not know
    # which upstream node to credit, so it adds no upstream link.
    {"evidence": {"id": "ev.cm", "summary": "3 channels degraded, common onset (common-mode)",
                  "source": "common_mode_check"},
     "links": []},
    # detector_health — bias_drift=true reads as positive support for the detector decoy
    {"evidence": {"id": "ev.det", "summary": "dark-count +45%, detector temp live → bias drift",
                  "source": "detector_health_check"},
     "links": [{"hypothesis_id": "h.detector", "polarity": "+", "weight": 1.2}]},
    # temp_correlation no-correlation → laser power down without thermal → credit laser aging
    {"evidence": {"id": "ev.tc", "summary": "intensity not tracking diode temp (r=0.14)",
                  "source": "temp_correlation_check"},
     "links": [{"hypothesis_id": "h.laser", "polarity": "+", "weight": 1.2},
               {"hypothesis_id": "h.thermal", "polarity": "-", "weight": 0.6}]},
]

# Synthesize names the belief leader's node (a competent model follows the differential it
# was given). On current code the leader is a decoy; with the fix it is sub.power. We make
# the scripted answer track whatever the leader is by reading it in the backend builder —
# but to keep the script static, we name the decoy here and rely on the loop preferring the
# belief leader (the fix), which is the structural separation under test.
SYNTH_DECOY = {
    "answer_type": "cause", "root_cause": "sub.detector",
    "causal_chain": ["sub.detector", "metric.intensity", "kpi.effective_range"],
    "cited_evidence": ["ev.det", "ev.tc"],
    "ruled_out": ["sub.optics", "sub.calibration"],
    "recommended_action": "Replace the detector module.",
}


def _backend() -> ScriptedBackend:
    return ScriptedBackend({
        "seed": json.dumps(SEED_HYPS),
        "propose": [json.dumps(p) for p in PROPOSE],
        "interpret": [json.dumps(i) for i in INTERPRET],
        "synthesize": json.dumps(SYNTH_DECOY),
    })


def _run():
    spec = CASES_BY_ID["case8"]
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    env = LidarEnvironment(case)
    answer = diagnose(env, backend=_backend(), budget=12)
    return case, answer


# --- not-a-scorer-artifact / not-a-seeding-gap guards ------------------------

def test_sub_power_is_seeded_and_scorable():
    """Structural guard: the controller CAN name sub.power (seeded + scorer accepts it)."""
    from dh.controller.loop import _seed_candidates
    from dh.eval.bespoke import _exact_cause_set
    spec = CASES_BY_ID["case8"]
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    env = LidarEnvironment(case)
    assert any(c["id"] == "sub.power" for c in _seed_candidates(env))  # not a seeding gap
    assert "sub.power" in _exact_cause_set("sub.power", case)          # not a scorer artifact


# --- before/after -----------------------------------------------------------

@pytest.mark.xfail(reason="documents the PRE-FIX miss; the common-mode promotion fix flips this "
                          "to sub.power, so these bug-assertions no longer hold (expected).",
                   strict=True)
def test_current_code_misses_sub_power():
    """Reproduce the miss: PRE-FIX the belief leader is a decoy (sub.detector), accuracy 0.

    This is an xfail(strict): on current/fixed code the promotion makes sub.power the leader, so
    these PRE-FIX assertions fail (xfail). If someone reverts the fix, this test xpasses and
    strict-mode turns that into a failure — a tripwire that the bug is back."""
    case, ans = _run()
    top, _conf, _margin = beliefs.leader(ans.final_graph)
    sc = score(ans, case, solver="controller")
    # On current code: leader is a surface decoy, not sub.power, and accuracy is 0.
    assert top.node_ref != "sub.power"
    assert sc.accuracy == 0.0


def test_fix_concludes_sub_power():
    """With the common-mode promotion fix, the leader and answer become sub.power."""
    case, ans = _run()
    top, conf, _margin = beliefs.leader(ans.final_graph)
    sc = score(ans, case, solver="controller")
    assert top.node_ref == "sub.power", f"leader was {top.node_ref}"
    assert ans.root_cause == "sub.power", f"answer was {ans.root_cause}"
    assert sc.accuracy == 1.0
    # the promotion must be in the belief math (M2 fix), not just conflict text
    assert conf > 0.5
