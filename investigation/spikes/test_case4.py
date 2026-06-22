"""Deterministic spike for case4 `calibration_drift` (salient_is_cause=True).

The recent `log.cal_update` (t=6.0) — a real cal_table v12→v13 change — IS the cause; gold
root_cause is `sub.calibration`. The controller scores accuracy=0 on this case. This spike
reproduces that miss with a ScriptedBackend whose per-step interpretations are FAITHFUL to the
real check payloads (built from `env.run_check(...)`, not reverse-engineered from the answer),
then shows the fix flips it to accuracy=1 while leaving the four passing-case patterns intact.

Two general mechanism bugs are exercised (briefing M2/M3, plus a synthesize disconnect):
  M2 — the deterministic conflict sweep adds text-only conflicts, never belief links.
  M3 — the sweep is demotion-only: it can demote a coincident event but never *promote*
       "the recent change IS the cause," so salient_is_cause=True cases get no credit.
  + synthesize lets the LLM re-pick root_cause freely, so even when the belief math ranks
    calibration top, the answer can name a different hypothesis.

The faithful failure narrative (what a competent-but-prompt-bounded model emits):
  - config_diff: cal_table changed → weak '+' to calibration (logged as "routine recalibration").
  - temp_correlation r≈0.00 → '-' thermal.    - tec_load 49% (at-spec) → small '+' thermal (M1).
  - spatial uniform → '-' optics.             - detector healthy → '-' detector.
  - onset_vs_event(log.cal_update): onset ALIGNS (predates=false). The interpret prompt frames
    onset only as a *demotion* trigger (act when predates=true), so an aligned onset yields NO
    link — the change-as-cause signal is dropped. Then synthesize names thermal (its at-spec
    reading was credited positively).

The test asserts the controller currently FAILS (names a non-calibration cause / calibration not
the dominant leader) and that the fix makes calibration the dominant leader AND the named cause,
scoring accuracy=1. Run against unpatched src it documents the red state (the failure asserts);
the GREEN assertions are guarded so the file is importable either way.

NOTE: `dh` resolves via the editable install pinned to the MAIN repo's src, so this worktree's
code is only exercised when its src is first on the path. The block below forces that; without it
the spike would silently test main-repo code.
"""
import json
import os
import sys

_WT_SRC = os.path.join(os.path.dirname(__file__), "..", "..", "src")
_WT_SRC = os.path.abspath(_WT_SRC)
if sys.path[0] != _WT_SRC:
    sys.path.insert(0, _WT_SRC)

import pytest  # noqa: E402

from dh.controller import beliefs  # noqa: E402
from dh.controller.llm import ScriptedBackend  # noqa: E402
from dh.controller import loop as loop_mod  # noqa: E402
from dh.controller.loop import diagnose  # noqa: E402
from dh.environment import LidarEnvironment  # noqa: E402
from dh.eval import bespoke  # noqa: E402
from dh.generator import generate  # noqa: E402
from dh.generator.cases import CASES_BY_ID  # noqa: E402

# The fix introduces this helper; its presence marks patched src.
PATCHED = hasattr(loop_mod, "_promote_change_cause")

SEED = {"hypotheses": [
    {"id": "h.thermal", "label": "TEC/thermal degradation", "node_ref": "sub.thermal"},
    {"id": "h.laser", "label": "laser power aging", "node_ref": "sub.laser"},
    {"id": "h.optics", "label": "window contamination", "node_ref": "sub.optics"},
    {"id": "h.detector", "label": "detector bias drift", "node_ref": "sub.detector"},
    {"id": "h.calib", "label": "calibration drift", "node_ref": "sub.calibration"},
]}

# One proposal per step, in order; padded so the loop never starves before the sweep runs.
PROPOSE = [
    {"actions": [{"type": "run_check", "args": {"name": "config_diff"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "temp_correlation_check"},
                  "expected_discrimination": 0.6}]},
    {"actions": [{"type": "run_check", "args": {"name": "tec_load_check"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "spatial_intensity_check"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "detector_health_check"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "onset_vs_event_check",
                  "signal": "effective_max_range_m", "event_id": "log.cal_update"},
                  "expected_discrimination": 0.7}]},
    {"actions": []},  # nothing left to propose → loop stops cleanly
]

# Faithful interpretations, aligned with PROPOSE — built from the REAL check payloads.
INTERPRET = [
    {"evidence": {"id": "ev.config", "summary": "cal_table_version v12->v13 (routine recalibration)",
                  "source": "config_diff"},
     "links": [{"hypothesis_id": "h.calib", "polarity": "+", "weight": 0.6}]},
    {"evidence": {"id": "ev.tempcorr", "summary": "intensity vs diode temp r=0.00 (no correlation)",
                  "source": "temp_correlation_check"},
     "links": [{"hypothesis_id": "h.thermal", "polarity": "-", "weight": 0.5}]},
    {"evidence": {"id": "ev.tecload", "summary": "TEC current 49% of limit (at spec)",
                  "source": "tec_load_check"},
     "links": [{"hypothesis_id": "h.thermal", "polarity": "+", "weight": 0.4}]},  # M1
    {"evidence": {"id": "ev.spatial", "summary": "uniform intensity drop (rules out window)",
                  "source": "spatial_intensity_check"},
     "links": [{"hypothesis_id": "h.optics", "polarity": "-", "weight": 0.8}]},
    {"evidence": {"id": "ev.detector", "summary": "no isolated detector bias signature",
                  "source": "detector_health_check"},
     "links": [{"hypothesis_id": "h.detector", "polarity": "-", "weight": 0.8}]},
    # onset aligns (predates=false) — prompt frames onset as demotion-only, so NO link (M3).
    {"evidence": {"id": "ev.onset", "summary": "degradation onset t=6 follows cal_update at t=6",
                  "source": "onset_vs_event_check"},
     "links": []},
    {},  # for the empty proposal step
]

# The synthesize LLM re-picks thermal as the cause (its at-spec reading was credited +).
SYNTH = {
    "answer_type": "cause", "root_cause": "h.thermal",
    "causal_chain": ["sub.thermal", "metric.intensity", "kpi.effective_range"],
    "cited_evidence": ["ev.tecload"], "ruled_out": ["sub.optics", "sub.detector"],
    "conflicts": [], "recommended_action": "Inspect the TEC module.",
}


def _backend() -> ScriptedBackend:
    return ScriptedBackend({
        "seed": json.dumps(SEED),
        "propose": [json.dumps(p) for p in PROPOSE],
        "interpret": [json.dumps(i) for i in INTERPRET],
        "synthesize": json.dumps(SYNTH),
    })


@pytest.fixture(scope="module")
def run():
    spec = CASES_BY_ID["case4"]
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    env = LidarEnvironment(case)
    answer = diagnose(env, backend=_backend(), budget=12)
    return case, answer


def test_scorer_credits_the_gold_cause():
    """Step 1 — the 0 is a real miss, not a scorer artifact: naming sub.calibration scores 1."""
    spec = CASES_BY_ID["case4"]
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    gt = case.ground_truth
    assert gt.root_cause == "sub.calibration"
    assert gt.root_cause in bespoke._exact_cause_set(gt.root_cause, case)


def test_case4_outcome(run):
    case, ans = run
    sc = bespoke.score(ans, case, solver="controller")
    top, conf, margin = beliefs.leader(ans.final_graph)
    if not PATCHED:
        # RED on unpatched src: the change-as-cause is never credited, synthesize re-picks thermal.
        assert sc.accuracy == 0.0
        assert ans.root_cause != "sub.calibration"
    else:
        # GREEN with the fix: deterministic promotion makes calibration the dominant leader and
        # synthesize is anchored to it → the gold cause is named.
        assert top.id == "h.calib" and top.node_ref == "sub.calibration"
        assert conf > 0.70 and margin > 0.20
        assert ans.root_cause == "sub.calibration"
        assert sc.accuracy == 1.0
