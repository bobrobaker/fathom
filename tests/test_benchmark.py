"""M8/M4.5 (harness) — the benchmark track runs and scores (spec §8.2).

Scoring is SQuAD-style EM/token-F1; the three QA solvers run over a synthetic multi-hop
item via a scripted backend (agentic_rag does iterative retrieval). The real MuSiQue
run is the scoped next step (needs the dataset + a token budget).
"""

import inspect
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

def test_agentic_rag_iterates_then_answers():
    from dh.controller.llm import ScriptedBackend
    backend = ScriptedBackend({"qacore": [
        json.dumps({"query": "Ada Stone birthplace"}),  # round 1: refine the search
        json.dumps({"answer": "Berlin"}),               # round 2: answer
    ]})
    from dh.environment import BenchmarkEnvironment
    env = BenchmarkEnvironment(_item().question, _item().passages)
    assert bm.agentic_rag(env, backend) == "Berlin"
    assert backend.calls.count("qacore") == 2  # it iterated


def test_benchmark_shares_only_plumbing_not_the_controller_core():
    """Claim-test (spec §8.2 'shared core' language): the benchmark path shares ONLY LLM plumbing
    with the diagnostic controller — NOT the hypothesis differential / VOI / belief update /
    Investigation Graph / abstention. So a benchmark number cannot speak to whether the diagnostic
    *structure* (the project's thesis) generalizes; it tests the iterative-retrieval pattern only.

    Verified STRUCTURALLY (against the import graph), not nominally (a name/comment is not evidence
    — that confusion is the lesson this test guards). If a full-build refactor makes the two paths
    genuinely share a reasoning core, this fails — update it consciously then (and the docstrings /
    spec), which is exactly the point.
    """
    import ast

    tree = ast.parse(inspect.getsource(bm))
    plumbing = {"LLMBackend", "_call_json", "get_backend", "MeteredBackend"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("dh.controller"):
            assert node.module == "dh.controller.llm", \
                f"benchmark imports from reasoning module {node.module!r}"
            for alias in node.names:
                assert alias.name in plumbing, \
                    f"benchmark imports {alias.name!r} from the controller — not LLM plumbing"
    # and it never *calls* the reasoning entry points (identifier use, not prose)
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    reasoning = {"diagnose", "seed_hypotheses", "propose_actions", "interpret_result",
                 "synthesize", "update_beliefs", "InvestigationGraph"}
    leaked = used & reasoning
    assert not leaked, f"benchmark references controller reasoning {leaked} — re-examine 'shared core'"
    # what it DOES legitimately share: the LLM plumbing
    assert {"_call_json", "get_backend"} <= used


def test_run_benchmark_scores_all_solvers():
    from dh.controller.llm import ScriptedBackend
    backend = ScriptedBackend({
        "qacore": json.dumps({"answer": "Berlin"}),
        "qarag": json.dumps({"answer": "Berlin"}),
        "qabare": json.dumps({"answer": "Munich"}),  # bare gets it wrong here
    })
    results = bm.run_benchmark([_item()], backend=backend)
    assert results["agentic_rag"].summary()["EM"] == 1.0
    assert results["static_rag"].summary()["EM"] == 1.0
    assert results["bare_llm"].summary()["EM"] == 0.0
    assert all(r.summary()["tokens/q"] > 0 for r in results.values())


def test_render_benchmark_table():
    from dh.controller.llm import ScriptedBackend
    backend = ScriptedBackend({"qacore": json.dumps({"answer": "Berlin"}),
                               "qarag": json.dumps({"answer": "Berlin"}),
                               "qabare": json.dumps({"answer": "Berlin"})})
    md = bm.render_benchmark(bm.run_benchmark([_item()], backend=backend))
    assert "agentic_rag" in md and "EM" in md and "tokens/q" in md
