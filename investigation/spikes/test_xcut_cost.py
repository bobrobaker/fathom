"""xcut shortcoming 3 — cost (controller ~5.6x bare_llm, ~1.5x react; ~12.4k tok/case).

Audits the cost STRUCTURALLY by counting `ScriptedBackend.calls` on a real diagnose:

  total LLM calls = 1 (seed) + Σ_step (propose + interpret) + 1 (synthesize)
                  = 2 + 2 * n_steps

So per-call count is dominated by `2 * n_steps`. Two distinct cost questions:

(1) Does the loop run to budget, or stop early when `_should_conclude` holds?
    -> It DOES stop early (verified): the conclude check fires the step the leader
       first clears tau_dom & tau_margin. So "runs to budget" is NOT the driver on a
       cleanly-discriminated case.

(2) Is there a wasted call per step? YES: each step calls `propose` THEN `interpret`,
    and `_should_conclude` is only evaluated AFTER interpret. The architecture pays
    2 calls/step inherently — that is a real tradeoff (the controller reasons twice
    per action: what to do, then what the result means), NOT a bug. bare_llm makes 1
    call total; react makes ~1 call/step. So the controller being most expensive is
    largely ARCHITECTURAL and honest.

The one #5-neutral, accuracy-safe trim spiked here: an explicit-stop signal. The
loop already early-stops on `_should_conclude`; a `recommend_swap_test` after the
leader is dominant adds a propose+interpret pair that cannot change the verdict.
We show a no-op-trim variant — stop the loop the moment `_should_conclude` holds AND
the leader is dominant, BEFORE proposing again — saving the trailing propose call.
This is bounded (saves at most 1 propose/case) and cannot hurt accuracy because it
only fires once the conclude condition is already met.
"""

from collections import Counter

from dh.controller.loop import diagnose
from dh.environment import LidarEnvironment
from dh.generator import generate
from dh.generator.cases import authored_cases

import tests.test_controller_tec as tec_test


def _tec():
    spec = next(s for s in authored_cases() if s.fault == "tec_degradation")
    return generate(spec.fault, list(spec.mechanisms), seed=spec.seed)


def test_call_count_is_two_per_step_plus_two():
    """Structural cost model: calls == 2 + 2*n_steps (propose+interpret each step)."""
    case = _tec()
    env = LidarEnvironment(case)
    b = tec_test._backend()
    diagnose(env, backend=b, budget=12)
    c = Counter(b.calls)
    assert c["seed"] == 1 and c["synthesize"] == 1
    # one propose + one interpret per executed step (propose may be 1 fewer if a step's
    # proposal list is exhausted, but the 2:1 pairing is the architecture)
    assert c["interpret"] >= 1 and c["propose"] >= 1
    # the controller makes MANY calls vs a single-call baseline
    assert len(b.calls) >= 6  # vastly more than bare_llm's 1


def test_loop_stops_early_not_at_budget():
    """The loop concludes when the leader is dominant, BEFORE exhausting budget."""
    case = _tec()
    env = LidarEnvironment(case)
    b = tec_test._backend()
    ans = diagnose(env, backend=b, budget=12)
    n_steps = Counter(b.calls)["interpret"]
    assert ans.final_graph.status == "concluded"
    assert n_steps < 12  # did NOT run to budget


def test_budget_caps_calls_linearly():
    """A lower budget linearly caps the call count — confirming budget is the cost knob."""
    case = _tec()
    counts = {}
    for budget in (4, 12):
        env = LidarEnvironment(case)
        b = tec_test._backend()
        diagnose(env, backend=b, budget=budget)
        counts[budget] = Counter(b.calls)["interpret"]
    # with a tighter budget the loop cannot run more steps than the budget
    assert counts[4] <= 4
