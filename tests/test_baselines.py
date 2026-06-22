"""M5 gate (spec §7, build plan M5).

All three baselines run on the TEC case and return Answers; `shortcut` blames the
reboot (gets it wrong) as designed.
"""

import json

import pytest

from dh import baselines
from dh.controller.llm import ScriptedBackend
from dh.environment import LidarEnvironment
from dh.generator import generate
from dh.schemas import Answer


@pytest.fixture(scope="module")
def case():
    return generate("tec_degradation", ["D1", "B5", "D5", "A2"], seed=0)


@pytest.fixture(scope="module")
def env(case):
    return LidarEnvironment(case)


# --- shortcut (deterministic) ------------------------------------------------

def test_shortcut_blames_the_reboot(env, case):
    ans = baselines.shortcut(env)
    assert isinstance(ans, Answer)
    assert ans.answer_type == "cause"
    assert ans.root_cause == "log.reboot"                 # the most recent event
    assert ans.root_cause != case.ground_truth.root_cause  # ...and it is wrong, by design
    assert case.ground_truth.trigger == ans.root_cause     # it blamed the trigger


# --- bare_llm (scripted) -----------------------------------------------------

def test_bare_llm_returns_answer(env):
    backend = ScriptedBackend({"bare": json.dumps({
        "answer_type": "cause", "root_cause": "part.tec",
        "causal_chain": ["part.tec", "kpi.effective_range"],
        "cited_evidence": ["report.prior_tec"], "ruled_out": ["part.laser_module"],
        "conflicts": ["detector_temp_C"], "recommended_action": "inspect TEC",
    })})
    ans = baselines.bare_llm(env, backend=backend)
    assert isinstance(ans, Answer) and ans.answer_type == "cause"
    assert ans.root_cause == "part.tec"
    assert ans.final_graph.symptom == env.symptom()


def test_bare_llm_degrades_on_garbage(env):
    ans = baselines.bare_llm(env, backend=ScriptedBackend({"bare": "not json"}))
    assert isinstance(ans, Answer)  # still a well-formed Answer (cause with null root)


# --- react (scripted: two tool calls, then a final) --------------------------

def test_react_runs_tools_then_concludes(env):
    backend = ScriptedBackend({"react": [
        json.dumps({"action": {"type": "run_check", "args": {"name": "temp_correlation_check"}}}),
        json.dumps({"action": {"type": "run_check", "args": {"name": "tec_load_check"}}}),
        json.dumps({"final": {"answer_type": "cause", "root_cause": "part.tec",
                              "causal_chain": ["part.tec", "kpi.effective_range"],
                              "cited_evidence": ["tec_load_check"],
                              "recommended_action": "swap-test the laser module"}}),
    ]})
    ans = baselines.react(env, backend=backend, max_steps=6)
    assert isinstance(ans, Answer) and ans.root_cause == "part.tec"
    assert backend.calls.count("react") == 3  # two tool turns + the final


def test_react_abstains_at_step_cap(env):
    # always proposes a tool, never finalizes → hits the cap and abstains
    backend = ScriptedBackend({"react":
        json.dumps({"action": {"type": "run_check", "args": {"name": "config_diff"}}})})
    ans = baselines.react(env, backend=backend, max_steps=3)
    assert ans.answer_type == "abstain"


@pytest.mark.parametrize("key", ["name", "check_id", "check", "check_name"])
def test_react_executor_accepts_check_name_aliases(env, key):
    # fairness regression: the live model keys the check name as check_id (not name); the
    # executor must still run the check, else react starves on errors and always abstains.
    obs = baselines._react_execute(env, {"type": "run_check", "args": {key: "tec_load_check"}})
    assert "error" not in obs or "unknown check" not in obs.get("error", "")


# --- registry ----------------------------------------------------------------

def test_solver_registry():
    assert set(baselines.SOLVERS) == {"shortcut", "bare_llm", "react"}
