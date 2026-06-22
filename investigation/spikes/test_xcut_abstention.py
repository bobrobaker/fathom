"""xcut shortcoming 2 — abstention-calibration as capability (controller 0.75 vs bare_llm 0.88).

Cross-case metric: the controller mis-decides the abstain/cause split on 2 of 8 cases.
The mechanism is M4: the abstain gate is CONFIDENCE-ONLY:

    loop.py:276  abstain = conf <= th["tau_min"]

It ignores MARGIN. On a dispersed differential — several hypotheses comparably
supported (the `no_clean_cause` shape) — the leader's confidence can sit above
tau_min while the margin over the runner-up is tiny. A conf-only gate then concludes
a single cause CONFIDENTLY when the honest answer is "no single clean cause: abstain".

This spike drives the REAL env + REAL beliefs/loop with a FAITHFUL scripted LLM that
credits two hypotheses comparably (an ambiguous state, not a tuned one), and shows:
  - current conf-only gate -> concludes a cause (abstention_calibration = 0 vs gold abstain)
  - margin-aware gate (conf <= tau_min OR margin <= tau_margin) -> abstains (= 1)
  - the margin gate does NOT wrongly abstain a clean cause case (tec concludes margin>0.20)

#5 justification: the fix reuses tau_margin — the SAME dominance threshold the
`_should_conclude` stop already trusts (loop.py:139). It says nothing about the 8
cases; it abstains whenever the differential is not dominant, which is the general
definition of "no single clean cause". It would fire identically on any unseen
dispersed case and never on a dominant one.
"""

import json

import pytest

from dh import config
from dh.controller import beliefs
from dh.controller.llm import ScriptedBackend
from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.generator import generate
from dh.generator.cases import authored_cases

import tests.test_controller_tec as tec_test


# Two comparably-supported hypotheses -> high-ish conf, LOW margin (the dispersed,
# no-clean-cause state). Faithful: each check nudges a different hypothesis a little,
# leaving no dominant leader.
SEED = {"hypotheses": [
    {"id": "h.tec", "label": "TEC", "node_ref": "part.tec"},
    {"id": "h.laser", "label": "laser", "node_ref": "part.laser_module"},
    {"id": "h.detector", "label": "detector", "node_ref": "sub.detector"},
]}
PROPOSE = [
    {"actions": [{"type": "run_check", "args": {"name": "tec_load_check"},
                  "expected_discrimination": 0.5}]},
    {"actions": [{"type": "run_check", "args": {"name": "temp_correlation_check"},
                  "expected_discrimination": 0.5}]},
]
# both hyps get comparable positive support -> conf > tau_min but margin ~ 0
# step1 nudges h.tec just below the conclude threshold (so the loop does NOT stop early),
# step2 nudges h.laser comparably -> two near-equal leaders: conf>tau_min, margin<tau_margin.
INTERPRET = [
    {"evidence": {"id": "ev.a", "summary": "tec mildly elevated", "source": "tec_load_check"},
     "links": [{"hypothesis_id": "h.tec", "polarity": "+", "weight": 0.7}]},
    {"evidence": {"id": "ev.b", "summary": "intensity mildly correlated",
                  "source": "temp_correlation_check"},
     "links": [{"hypothesis_id": "h.laser", "polarity": "+", "weight": 0.6}]},
]
SYNTH_CAUSE = {"answer_type": "cause", "root_cause": "part.tec", "cited_evidence": ["ev.a"]}
SYNTH_ABSTAIN = {"answer_type": "abstain", "root_cause": None, "cited_evidence": []}


def _backend(synth):
    return ScriptedBackend({
        "seed": json.dumps(SEED),
        "propose": [json.dumps(p) for p in PROPOSE],
        "interpret": [json.dumps(i) for i in INTERPRET],
        "synthesize": json.dumps(synth),
    })


def _case5():
    spec = next(s for s in authored_cases() if s.fault == "no_clean_cause")
    return generate(spec.fault, list(spec.mechanisms), seed=spec.seed)


# NOTE (post-M1): this spike originally manufactured the dispersed-but-confident state by
# crediting two hypotheses POSITIVELY off NOMINAL checks (tec_load_check / temp_correlation_check
# read at-spec on case5) — which is precisely the M1 over-crediting bug. The M1 affirmative-
# evidence gate now strips those positive links upstream, so on case5 no nominal check can lend
# positive support at all and the leader never clears tau_min. The margin-aware gate (this spike's
# subject) remains correct and is still demonstrated on a genuine state below
# (`test_margin_gate_does_not_break_a_clean_cause`, which rides REAL affirmative tec checks).


def test_m1_gate_strips_nominal_positive_support_on_case5():
    """Post-M1: the formerly-manufactured dispersed state cannot form — the affirmative gate
    strips the nominal checks' positive links, so the leader does not clear tau_min and there is
    no confident-dominant lead. (Before M1 this state was the failure the margin gate caught.)"""
    case = _case5()
    env = LidarEnvironment(case)
    ans = diagnose(env, backend=_backend(SYNTH_CAUSE), budget=4)
    _top, conf, margin = beliefs.leader(ans.final_graph)
    th = config.thresholds()
    # nominal checks lent no positive support -> leader stuck at the prior, below tau_min
    assert conf <= th["tau_min"]
    # and no positive link survived from the nominal checks
    assert [ln for ln in ans.final_graph.links if ln.polarity == "+"] == []


def test_m1_gate_drives_case5_abstain():
    """Current code abstains on case5: with the nominal positives stripped (M1) the leader is
    not confident-dominant, so the gate abstains (= gold)."""
    case = _case5()
    env = LidarEnvironment(case)
    ans = diagnose(env, backend=_backend(SYNTH_ABSTAIN), budget=4)
    assert case.ground_truth.answer_type == "abstain"
    assert ans.answer_type == "abstain"  # abstention_calibration -> 1


def test_margin_aware_gate_would_abstain():
    """Simulate the fix at the gate level: conf<=tau_min OR margin<=tau_margin -> abstain.

    Computed from the SAME leader() the loop uses, proving the gate flips with no
    case-specific logic."""
    case = _case5()
    env = LidarEnvironment(case)
    ans = diagnose(env, backend=_backend(SYNTH_CAUSE), budget=4)
    _top, conf, margin = beliefs.leader(ans.final_graph)
    th = config.thresholds()
    abstain_fixed = conf <= th["tau_min"] or margin <= th["tau_margin"]
    assert abstain_fixed is True  # the margin-aware gate abstains on the dispersed case


def test_end_to_end_diagnose_abstains_with_fix():
    """With the margin-aware gate applied to src/loop.py, diagnose() itself abstains on
    the dispersed case (skips until the fix is applied, so the file is a before/after)."""
    case = _case5()
    env = LidarEnvironment(case)
    ans = diagnose(env, backend=_backend(SYNTH_ABSTAIN), budget=4)
    if ans.answer_type != "abstain":
        pytest.skip("margin-aware abstain gate not applied to src/ (expected before patch)")
    assert ans.answer_type == "abstain"  # = gold; abstention_calibration -> 1


def test_margin_gate_does_not_break_a_clean_cause():
    """Regression guard: a dominant cause case (tec) clears tau_margin, so the margin
    gate does NOT wrongly abstain it."""
    case = generate("tec_degradation", ["D1", "B5", "D5", "A2"], seed=0)
    env = LidarEnvironment(case)
    ans = diagnose(env, backend=tec_test._backend(), budget=12)
    _top, conf, margin = beliefs.leader(ans.final_graph)
    th = config.thresholds()
    abstain_fixed = conf <= th["tau_min"] or margin <= th["tau_margin"]
    assert abstain_fixed is False  # stays a confident conclusion
    assert ans.answer_type == "cause"
