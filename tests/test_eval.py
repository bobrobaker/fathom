"""M6 gate (spec §8.1, build plan M6).

The rubric scores constructed answers correctly; the report renders the two families;
and on case #1 the controller's capability family (esp. trigger-discrimination and
conflict-handling) exceeds bare_llm and react.

Answers are constructed (not live-run) so the rubric logic is tested deterministically;
the live numbers come from tools/run_eval.py over ≥3 runs.
"""

import pytest

from dh.eval import bespoke, report
from dh.eval.bespoke import CAPABILITY_FAMILY, score
from dh.generator import generate
from dh.schemas import Answer, EvidenceItem, InvestigationGraph


@pytest.fixture(scope="module")
def case():
    return generate("tec_degradation", ["D1", "B5", "D5", "A2"], seed=0)


def _ig(case, evidence=()):
    return InvestigationGraph(symptom="range down", evidence=list(evidence), status="concluded")


def _controller_answer(case) -> Answer:
    ev = [EvidenceItem(id="ev.tecload", summary="TEC 91%", source="tec_load_check"),
          EvidenceItem(id="ev.tempcorr", summary="r=-0.88", source="temp_correlation_check"),
          EvidenceItem(id="ev.onset", summary="onset<reboot", source="onset_vs_event_check")]
    return Answer(answer_type="cause", root_cause="part.tec",
                  cited_evidence=["ev.tecload", "ev.tempcorr", "ev.onset"],
                  conflicts=["metric.detector_temp", "log.reboot"],
                  recommended_action="swap-test", final_graph=_ig(case, ev))


def _bare_answer(case) -> Answer:
    return Answer(answer_type="cause", root_cause="part.tec",
                  cited_evidence=["report.prior_tec"], conflicts=["detector_temp_C"],
                  final_graph=_ig(case))


def _react_answer(case) -> Answer:
    return Answer(answer_type="cause", root_cause="part.tec",
                  cited_evidence=["tec_load_check"], conflicts=["detector_temp_C"],
                  final_graph=_ig(case))


def _shortcut_answer(case) -> Answer:
    return Answer(answer_type="cause", root_cause="log.reboot",
                  cited_evidence=["log.reboot"], conflicts=[], final_graph=_ig(case))


# --- rubric correctness ------------------------------------------------------

def test_accuracy_granularity_and_wrong(case):
    # exact part match earns accuracy AND localization
    s = score(_controller_answer(case), case)
    assert s.accuracy == 1.0 and s.localization == 1.0
    # C6: naming only the subsystem of a PART fault is NOT full accuracy — it is localization
    sub_ans = _controller_answer(case).model_copy(update={"root_cause": "sub.thermal"})
    s_sub = score(sub_ans, case)
    assert s_sub.accuracy == 0.0 and s_sub.localization == 1.0
    # the part-version is the same physical part → still exact
    rev_ans = _controller_answer(case).model_copy(update={"root_cause": "part.tec.revB"})
    assert score(rev_ans, case).accuracy == 1.0
    # blamed the reboot → neither right nor localized
    s_sc = score(_shortcut_answer(case), case)
    assert s_sc.accuracy == 0.0 and s_sc.localization == 0.0


def test_trigger_discrimination(case):
    assert score(_controller_answer(case), case).trigger_discrimination == 1.0  # noted, not cause
    assert score(_bare_answer(case), case).trigger_discrimination == 0.0        # didn't note it
    assert score(_shortcut_answer(case), case).trigger_discrimination == 0.0    # named it cause


def test_conflict_handling(case):
    # conflict_handling is F1 (decision 2026-06-21): precision penalises over-surfacing
    assert score(_controller_answer(case), case).conflict_handling == 1.0       # both, no extras
    assert score(_bare_answer(case), case).conflict_handling == pytest.approx(2 / 3)  # 1 of 2, P=1
    assert score(_shortcut_answer(case), case).conflict_handling == 0.0         # surfaced none
    # over-surfacing is penalised: dumping junk ids alongside the real conflicts drops precision,
    # so a solver cannot game the metric to 1.0 by listing everything (the #2 fix)
    spammy = _controller_answer(case).model_copy(update={
        "conflicts": ["metric.detector_temp", "log.reboot", "part.window", "sub.optics"]})
    assert score(spammy, case).conflict_handling < 1.0


def test_evidence_f1_and_hallucination_penalty(case):
    s = score(_controller_answer(case), case)
    assert s.evidence_f1 > 0.5  # cites 3/5 load-bearing via source normalisation
    # a hallucinated citation (id not in the case) drops precision
    bad = _controller_answer(case).model_copy(update={
        "cited_evidence": ["ev.tecload", "ev.tempcorr", "ev.onset", "totally.made.up"]})
    assert score(bad, case).evidence_f1 < s.evidence_f1


def test_abstention_calibration(case):
    assert score(_controller_answer(case), case).abstention_calibration == 1.0
    false_abstain = _controller_answer(case).model_copy(update={"answer_type": "abstain"})
    assert score(false_abstain, case).abstention_calibration == 0.0


# --- the headline: controller wins the capability family ---------------------

def test_controller_beats_baselines_on_capability(case):
    scores = {
        "controller": score(_controller_answer(case), case, solver="controller"),
        "bare_llm": score(_bare_answer(case), case, solver="bare_llm"),
        "react": score(_react_answer(case), case, solver="react"),
    }
    cap = {k: sum(getattr(v, m) for m in CAPABILITY_FAMILY) / len(CAPABILITY_FAMILY)
           for k, v in scores.items()}
    assert cap["controller"] > cap["bare_llm"]
    assert cap["controller"] > cap["react"]


# --- report rendering --------------------------------------------------------

def test_report_renders_two_families_and_headline(case):
    results = {
        "controller": [score(_controller_answer(case), case, solver="controller", tokens=1200)],
        "bare_llm": [score(_bare_answer(case), case, solver="bare_llm", tokens=3000)],
        "shortcut": [score(_shortcut_answer(case), case, solver="shortcut", tokens=0)],
    }
    md = report.render(results, case_id=case.id)
    assert "Accuracy family" in md and "Capability family" in md and "Cost" in md
    assert "controller" in md and "capability-family mean: controller" in md


def test_summarize_reports_variance():
    case = generate("tec_degradation", ["D1", "B5", "D5", "A2"], seed=0)
    a, b = _controller_answer(case), _shortcut_answer(case)
    mixed = [score(a, case), score(a, case), score(b, case)]  # 2 right, 1 wrong on accuracy
    summary = report.summarize(mixed)
    mean, sd = summary["accuracy"]
    assert 0 < mean < 1 and sd > 0  # variance surfaced
