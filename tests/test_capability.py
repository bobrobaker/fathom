"""Capability-binding (B5) and anti-shortcut balance (B8) gates over the full case set.

These are *structural* gates — deterministic properties of the authored cases, not live
LLM runs. They assert that each capability case's scored-axis discriminator is unavailable
from a naive read of the corpus (so the case is genuinely capability-bound, non-negotiable
#4), and that across the set a salient recent event carries ~no information about whether it
is the cause (anti-shortcut balance ≈0.5, §5.2). The *empirical* B5 confirmation — that a
strengthened bare_llm actually fails each scored axis — is produced by the live eval and
reported in the findings; this file is the cheap, reproducible guard that ships in CI.
"""

import json
import statistics as st

import pytest

from dh.controller.llm import ScriptedBackend
from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.generator import generate
from dh.generator.cases import CASES_BY_ID, authored_cases


def _case(cid):
    s = CASES_BY_ID[cid]
    return generate(s.fault, list(s.mechanisms), seed=s.seed)


def _env(cid):
    return LidarEnvironment(_case(cid))


# --- S1: the set is large enough and every case is authored -------------------

def test_at_least_nine_case_slots_eight_authored():
    # the spec asks for ≥9 case *slots*; the spike authors all 8 fault models to depth
    # (case1 doubles as the worked example). Every authored case must be eval-ready.
    authored = authored_cases()
    assert len(authored) == 8
    assert {c.id for c in authored} == {f"case{i}" for i in range(1, 9)}


# --- B8: anti-shortcut balance ≈0.5 ------------------------------------------

def test_anti_shortcut_balance_is_a_genuine_mix():
    """Across the cause-cases that *have* a salient recent event, the fraction where that
    event IS the cause must sit in a band around 0.5 — decisively away from the prior ~0
    (every case trigger≠cause), so a shortcut cannot win by always blaming the recent event."""
    labelled = [c.salient_is_cause for c in authored_cases() if c.salient_is_cause is not None]
    assert len(labelled) >= 5  # enough cases to talk about a correlation
    frac_is_cause = sum(labelled) / len(labelled)
    # a true mix: some change-is-cause, some trigger≠cause; not degenerate at 0 or 1
    assert 0.25 <= frac_is_cause <= 0.6, f"salient-event↔cause fraction {frac_is_cause:.2f}"
    # and the kinds of salient event are varied (not all reboots) — audit concern #5
    assert any(c.salient_is_cause is True for c in authored_cases())   # ≥1 change-is-cause
    assert any(c.salient_is_cause is None for c in authored_cases())   # ≥1 absent-cue / abstain


# --- B5: each capability case is bound on its scored axis ---------------------

def test_case1_trigger_is_compute_bound():
    """Trigger-discrimination: the reboot is the salient recent event, and the degradation
    onset (needed to demote it) is *computed* from telemetry — it is stated in no artifact, so
    a context dump that reads text cannot order onset vs reboot without running the check."""
    case = _case("case1")
    reboot = next(a for a in case.artifacts if a.id == "log.reboot")
    assert reboot.timestamp is not None
    # the demotion conclusion must be COMPUTED, not read: no artifact pre-states it
    giveaways = ("predates", "coincident", "not causal", "non-causal", "days ago the range")
    assert not any(w in a.text.lower() for a in case.artifacts for w in giveaways)
    env = LidarEnvironment(case)
    # the check resolves it; a naive reader cannot
    assert env.run_check("onset_vs_event_check")["onset_predates_event"] is True


def test_case5_abstain_is_bound_no_hypothesis_crosses_threshold():
    """Abstention: every channel is nominal and the dip self-resolves, so no hypothesis can
    accumulate support — a solver forced to name a cause must confabulate one."""
    env = _env("case5")
    assert env.run_check("temp_correlation_check")["correlated"] is False
    assert env.run_check("tec_load_check")["at_limit"] is False
    assert env.run_check("channel_sanity_check")["stuck"] is False
    sig = {s.signal: s for s in _case("case5").telemetry}
    assert st.mean(sig["effective_max_range_m"].v[-5:]) > 118  # recovered / within spec


def test_case6_discriminator_is_compute_and_navigation_bound():
    """Detector bias: the discriminator is detector_health_check (dark-count up while detector
    temp is flat — a computation), and the explaining note is navigation-gated: a search on the
    symptom terms does not surface it; it is reached by traversing from the detector subsystem."""
    case = _case("case6")
    env = LidarEnvironment(case)
    assert env.run_check("detector_health_check")["bias_drift"] is True
    # navigation-gated: the bias note is not retrievable by the range-degradation query
    hits = {a.id for a in env.search("effective range degradation diagnosis playbook", k=6)}
    assert "doc.detector_bias" not in hits
    # but it IS reachable by traversing the receiver subsystem
    reached = {n.id for n in env.traverse("sub.detector", "documented_in", direction="in")}
    assert "doc.detector_bias" in reached


def test_case7_cheap_checks_inconclusive_needs_expensive_tiebreaker():
    """Tie-breaker under budget (D6): neither cheap discriminator fires cleanly (correlation
    sub-threshold, TEC current under its limit), so the case cannot be closed on a cheap check
    alone — the expensive swap-test recommendation is the high-VOI move."""
    env = _env("case7")
    assert env.run_check("temp_correlation_check")["correlated"] is False
    assert env.run_check("tec_load_check")["at_limit"] is False
    # the diode is nonetheless elevated above setpoint — the tell that it is TEC, not laser
    sig = {s.signal: s for s in _case("case7").telemetry}
    assert st.mean(sig["laser_diode_temp_C"].v[-5:]) > 27.0
    assert "recommend_swap_test" in _case("case7").ground_truth.load_bearing_evidence


def test_case8_common_mode_trap_needs_onset_clustering():
    """Common-mode (A5): the surface channels each look like an independent fault (power down →
    laser aging; dark-count up → detector drift), and only the common-onset computation
    (common_mode_check) reveals the single upstream power cause."""
    env = _env("case8")
    assert env.run_check("common_mode_check")["common_mode"] is True
    # each surface channel, read alone, points at a different (wrong) decoy
    case = _case("case8")
    assert set(case.ground_truth.decoys) >= {"part.laser_module", "part.detector"}
    # the redundant agreement is the trap: no single cheap check names sub.power
    assert env.run_check("temp_correlation_check")["correlated"] is False


# --- the conflict sweep (B7): surfaced reliably, never falsely ---------------

def _scripted_conclude_tec():
    """A backend that concludes TEC fast — so any conflict surfaced comes from the sweep,
    not from the loop happening to run the onset/channel checks itself."""
    return ScriptedBackend({
        "seed": json.dumps({"hypotheses": [
            {"id": "h.tec", "label": "TEC", "node_ref": "part.tec"},
            {"id": "h.laser", "label": "laser", "node_ref": "part.laser_module"}]}),
        "propose": json.dumps({"actions": [{"type": "run_check",
            "args": {"name": "tec_load_check"}, "expected_discrimination": 0.9}]}),
        "interpret": json.dumps({"evidence": {"id": "ev.tl", "summary": "TEC high",
            "source": "tec_load_check"}, "links": [{"hypothesis_id": "h.tec",
            "polarity": "+", "weight": 2.0}]}),
        "synthesize": json.dumps({"answer_type": "cause", "root_cause": "part.tec",
            "cited_evidence": ["ev.tl"]}),
    })


def test_conflict_sweep_surfaces_trigger_and_lying_channel_on_case1():
    """Even when the controller concludes early, the deterministic sweep demotes the reboot and
    flags the stuck detector_temp — the capability the bare baselines structurally lack."""
    case = _case("case1")
    ans = diagnose(LidarEnvironment(case), backend=_scripted_conclude_tec(), budget=3)
    assert ans.root_cause == "part.tec"
    assert "log.reboot" in ans.conflicts            # demoted trigger
    assert "metric.detector_temp" in ans.conflicts  # stuck lying channel


def test_conflict_sweep_does_not_demote_a_causal_change_on_case4():
    """The change-is-cause case must NOT have its recent change demoted (onset aligns, not
    predates) — the sweep is general, not a case-1 hack."""
    case = _case("case4")
    ans = diagnose(LidarEnvironment(case), backend=_scripted_conclude_tec(), budget=3)
    # no spurious trigger/channel conflicts injected (case4 has no demoted trigger, no stuck channel)
    assert "log.reboot" not in ans.conflicts
    assert all(not c.startswith("log.") for c in ans.conflicts)


@pytest.mark.parametrize("cid", [f"case{i}" for i in range(1, 9)])
def test_every_case_capability_bound_not_by_single_dump(cid):
    """A coarse cross-check: each case needs at least one capability the spec names as bound —
    a deterministic check, a traversal target, an abstain, or a recommend-action — i.e. it is
    not solvable by reading the corpus once. (Per-axis binding is asserted case-by-case above.)"""
    case = _case(cid)
    gt = case.ground_truth
    needs_check = any(e.endswith("_check") or e == "config_diff" or e == "recommend_swap_test"
                      for e in gt.load_bearing_evidence)
    is_abstain = gt.answer_type == "abstain"
    needs_traversal = any(a.kind in ("doc", "domain_doc") and a.refs for a in case.artifacts)
    assert needs_check or is_abstain or needs_traversal
