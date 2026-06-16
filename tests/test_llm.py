"""M3 gate (spec §6.6, build plan M3).

Each structured call parses to typed output on a scripted backend; bad output
retries then degrades gracefully; backend selection follows key/CLI availability.
"""

import json

import pytest

from dh.controller import llm
from dh.controller.llm import (
    ActionProposal,
    ScriptedBackend,
    extract_json,
    get_backend,
)
from dh.schemas import EvidenceItem, Hypothesis, InvestigationGraph


# --- backend selection -------------------------------------------------------

def test_forced_stub_returns_none(monkeypatch):
    monkeypatch.setenv("DH_BACKEND", "stub")
    assert get_backend() is None


def test_prefers_anthropic_when_keyed(monkeypatch):
    monkeypatch.delenv("DH_BACKEND", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    b = get_backend("claude-sonnet-4-6")
    assert b is not None and b.name == "anthropic"


def test_uses_cli_when_unkeyed(monkeypatch):
    monkeypatch.delenv("DH_BACKEND", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(llm.shutil, "which", lambda exe: "/usr/bin/claude")
    b = get_backend("claude-sonnet-4-6")
    assert b is not None and b.name == "cli"


# --- JSON extraction ---------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ('{"a": 1}', {"a": 1}),
    ('```json\n{"a": 2}\n```', {"a": 2}),
    ('here you go: {"a": 3} cheers', {"a": 3}),
    ("no json here", {}),
    ("[1,2,3]", {}),  # top-level array is not a dict result
    ("", {}),
])
def test_extract_json(text, expected):
    assert extract_json(text) == expected


# --- the four structured calls (scripted) ------------------------------------

def test_seed_hypotheses_parses():
    backend = ScriptedBackend({"seed": json.dumps({"hypotheses": [
        {"id": "h.tec", "label": "TEC degradation", "node_ref": "part.tec"},
        {"id": "h.laser", "label": "laser aging", "node_ref": "part.laser_module"},
    ]})})
    hyps = llm.seed_hypotheses(backend, "range down", [{"id": "sub.thermal", "name": "Thermal"}])
    assert [h.id for h in hyps] == ["h.tec", "h.laser"]
    assert all(isinstance(h, Hypothesis) for h in hyps)


def test_seed_degrades_to_candidates_on_empty():
    backend = ScriptedBackend({"seed": "garbage not json"})
    cands = [{"id": "sub.thermal", "name": "Thermal"}, {"id": "sub.laser", "name": "Laser"}]
    hyps = llm.seed_hypotheses(backend, "range down", cands)
    assert {h.node_ref for h in hyps} == {"sub.thermal", "sub.laser"}  # fallback used


def test_propose_actions_parses_and_skips_malformed():
    backend = ScriptedBackend({"propose": json.dumps({"actions": [
        {"type": "run_check", "args": {"name": "tec_load_check"}, "expected_discrimination": 0.8},
        {"type": "not_a_type", "args": {}},  # malformed → skipped
    ]})})
    ig = InvestigationGraph(symptom="range down")
    actions = llm.propose_actions(backend, ig, ["tec_load_check"], {"run_check"})
    assert len(actions) == 1 and isinstance(actions[0], ActionProposal)
    assert actions[0].type == "run_check"


def test_interpret_result_builds_evidence_and_links():
    ig = InvestigationGraph(symptom="range down", hypotheses=[
        Hypothesis(id="h.tec", label="TEC"), Hypothesis(id="h.laser", label="laser")])
    backend = ScriptedBackend({"interpret": json.dumps({
        "evidence": {"id": "ev.1", "summary": "TEC at 91%", "source": "tec_load_check"},
        "links": [
            {"hypothesis_id": "h.tec", "polarity": "+", "weight": 1.5},
            {"hypothesis_id": "h.ghost", "polarity": "+", "weight": 9},  # unknown → dropped
            {"hypothesis_id": "h.laser", "polarity": "x", "weight": 1},  # bad polarity → dropped
        ],
        "conflicts": ["metric.detector_temp"],
    })})
    action = ActionProposal(type="run_check", args={"name": "tec_load_check"})
    ev, links, conflicts = llm.interpret_result(backend, ig, action, {"frac_of_limit": 0.91})
    assert isinstance(ev, EvidenceItem) and ev.id == "ev.1"
    assert [(l.hypothesis_id, l.polarity) for l in links] == [("h.tec", "+")]
    assert conflicts == ["metric.detector_temp"]


def test_interpret_degrades_on_empty():
    ig = InvestigationGraph(symptom="x", hypotheses=[Hypothesis(id="h.tec", label="TEC")])
    backend = ScriptedBackend({"interpret": "nope"})
    ev, links, conflicts = llm.interpret_result(
        backend, ig, ActionProposal(type="search"), {})
    assert ev is None and links == [] and conflicts == []


def test_synthesize_filters_citations_to_known_evidence():
    ig = InvestigationGraph(symptom="range down",
                            evidence=[EvidenceItem(id="ev.1", summary="x", source="s")],
                            conflicts=["metric.detector_temp"])
    backend = ScriptedBackend({"synthesize": json.dumps({
        "answer_type": "cause", "root_cause": "part.tec",
        "causal_chain": ["part.tec", "kpi.effective_range"],
        "cited_evidence": ["ev.1", "ev.hallucinated"],  # second is filtered out
        "ruled_out": ["part.laser_module"], "recommended_action": "swap-test",
    })})
    ans = llm.synthesize(backend, ig)
    assert ans.answer_type == "cause" and ans.root_cause == "part.tec"
    assert ans.cited_evidence == ["ev.1"]  # hallucinated citation dropped
    assert ans.final_graph is ig
    assert ans.conflicts == ["metric.detector_temp"]


def test_synthesize_abstain_path():
    ig = InvestigationGraph(symptom="intermittent")
    backend = ScriptedBackend({"synthesize": json.dumps({"answer_type": "abstain"})})
    ans = llm.synthesize(backend, ig, abstain=True)
    assert ans.answer_type == "abstain" and ans.root_cause is None


# --- retry + degradation in _call_json ---------------------------------------

class _FlakyBackend:
    """Returns bad output `n_bad` times, then valid JSON."""
    name = "flaky"

    def __init__(self, n_bad, good):
        self.n_bad, self.good, self.n = n_bad, good, 0

    def complete(self, prompt, *, system=None, max_tokens=1024):
        self.n += 1
        return "not json" if self.n <= self.n_bad else self.good


def test_call_json_retries_then_succeeds():
    backend = _FlakyBackend(1, '{"ok": 1}')
    out = llm._call_json(backend, "seed", "body", retries=2)
    assert out == {"ok": 1} and backend.n == 2  # one retry


def test_call_json_degrades_after_retries():
    backend = _FlakyBackend(99, "never")
    out = llm._call_json(backend, "seed", "body", retries=2)
    assert out == {} and backend.n == 3  # initial + 2 retries


def test_call_json_survives_backend_exception():
    class _Raises:
        name = "boom"
        def complete(self, *a, **k):
            raise RuntimeError("backend down")
    assert llm._call_json(_Raises(), "seed", "body", retries=1) == {}
