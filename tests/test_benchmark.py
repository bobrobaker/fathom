"""M8/M4.5 (harness) — the benchmark track runs and scores (spec §8.2).

Scoring is SQuAD-style EM/token-F1; the three QA solvers run over a synthetic multi-hop
item via a scripted backend (controller-core does iterative retrieval). The real MuSiQue
run is the scoped next step (needs the dataset + a token budget).
"""

import json

from dh.eval import benchmark as bm
from dh.eval.benchmark import BenchmarkItem, exact_match, token_f1
from dh.schemas import Artifact


def _item() -> BenchmarkItem:
    passages = [
        Artifact(id="p0", kind="passage", text="Acme Corp was founded by Ada Stone in 1990."),
        Artifact(id="p1", kind="passage", text="Ada Stone was born in Berlin, Germany."),
        Artifact(id="p2", kind="passage", text="Berlin is the capital of Germany."),
        Artifact(id="p3", kind="passage", text="Unrelated: the Nile is a river in Africa."),
    ]
    return BenchmarkItem(question="In what city was the founder of Acme Corp born?",
                         answer="Berlin", passages=passages)


# --- scoring -----------------------------------------------------------------

def test_exact_match_normalizes():
    assert exact_match("Berlin", "berlin") == 1.0
    assert exact_match("The Berlin ", "Berlin") == 1.0  # articles/case/space stripped
    assert exact_match("Munich", "Berlin") == 0.0


def test_token_f1_partial_credit():
    assert token_f1("New York City", "New York") > 0.5
    assert token_f1("Berlin", "Berlin") == 1.0
    assert token_f1("Paris", "Berlin") == 0.0


# --- solvers (scripted) ------------------------------------------------------

def test_controller_core_iterates_then_answers():
    from dh.controller.llm import ScriptedBackend
    backend = ScriptedBackend({"qacore": [
        json.dumps({"query": "Ada Stone birthplace"}),  # round 1: refine the search
        json.dumps({"answer": "Berlin"}),               # round 2: answer
    ]})
    from dh.environment import BenchmarkEnvironment
    env = BenchmarkEnvironment(_item().question, _item().passages)
    assert bm.controller_core(env, backend) == "Berlin"
    assert backend.calls.count("qacore") == 2  # it iterated


def test_run_benchmark_scores_all_solvers():
    from dh.controller.llm import ScriptedBackend
    backend = ScriptedBackend({
        "qacore": json.dumps({"answer": "Berlin"}),
        "qarag": json.dumps({"answer": "Berlin"}),
        "qabare": json.dumps({"answer": "Munich"}),  # bare gets it wrong here
    })
    results = bm.run_benchmark([_item()], backend=backend)
    assert results["controller_core"].summary()["EM"] == 1.0
    assert results["static_rag"].summary()["EM"] == 1.0
    assert results["bare_llm"].summary()["EM"] == 0.0
    assert all(r.summary()["tokens/q"] > 0 for r in results.values())


def test_render_benchmark_table():
    from dh.controller.llm import ScriptedBackend
    backend = ScriptedBackend({"qacore": json.dumps({"answer": "Berlin"}),
                               "qarag": json.dumps({"answer": "Berlin"}),
                               "qabare": json.dumps({"answer": "Berlin"})})
    md = bm.render_benchmark(bm.run_benchmark([_item()], backend=backend))
    assert "controller_core" in md and "EM" in md and "tokens/q" in md
