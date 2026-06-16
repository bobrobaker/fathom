"""Benchmark track — agentic-retrieval generalization (spec §8.2, build plan M4.5/M8).

Runs the **shared core** (controller minus lidar checks: search-driven iterative
retrieval + answer selection) against `bare_llm` and `static_rag` on a QA passage set,
reporting answer-EM/F1 and tokens/question. Framed as *agentic retrieval generalization*,
not diagnosis (audit concern #2).

The harness is dataset-agnostic: feed it `BenchmarkItem`s. A MuSiQue loader lives in
`tools/` behind the optional `benchmark` extra; the synthetic fixture in the tests proves
the mechanism without a download. Per the M4.5 decision gate, the real MuSiQue n=100 run
is the scoped step once a token budget / dataset are in hand.
"""

from __future__ import annotations

import json
import re
import statistics as st
from dataclasses import dataclass, field

from dh.controller.llm import LLMBackend, _call_json, get_backend
from dh.environment import BenchmarkEnvironment
from dh.schemas import Artifact


@dataclass
class BenchmarkItem:
    question: str
    answer: str
    passages: list[Artifact]


# --- scoring (SQuAD-style) ---------------------------------------------------

def _normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(s.split())


def exact_match(pred: str, gold: str) -> float:
    return 1.0 if _normalize(pred) == _normalize(gold) else 0.0


def token_f1(pred: str, gold: str) -> float:
    p, g = _normalize(pred).split(), _normalize(gold).split()
    if not p or not g:
        return float(p == g)
    common = 0
    gg = list(g)
    for tok in p:
        if tok in gg:
            common += 1
            gg.remove(tok)
    if common == 0:
        return 0.0
    precision, recall = common / len(p), common / len(g)
    return 2 * precision * recall / (precision + recall)


# --- solvers (share the BenchmarkEnvironment) --------------------------------

def _answer_text(data: dict) -> str:
    return (data.get("answer") or "").strip()


def controller_core(env: BenchmarkEnvironment, backend: LLMBackend, rounds: int = 3) -> str:
    """Iterative retrieval + answer selection — the shared core, no lidar checks."""
    seen: dict[str, str] = {}
    query = env.symptom()
    for _r in range(rounds):
        for a in env.search(query, k=4):
            seen[a.id] = a.text
        body = (
            f"Question: {env.symptom()}\n"
            f"Retrieved passages:\n" + "\n".join(f"  [{i}] {t}" for i, t in seen.items()) + "\n"
            'Reply {"query": "<a more specific search query>"} to retrieve more, or '
            '{"answer": "<the short answer>"} when you can answer. Prefer answering once the '
            "passages contain the fact."
        )
        data = _call_json(backend, "qacore", body)
        if data.get("answer"):
            return _answer_text(data)
        query = data.get("query") or query
    body = (f"Question: {env.symptom()}\nPassages:\n"
            + "\n".join(f"  {t}" for t in seen.values())
            + '\nReply {"answer": "<short answer>"}.')
    return _answer_text(_call_json(backend, "qacore", body))


def static_rag(env: BenchmarkEnvironment, backend: LLMBackend, k: int = 4) -> str:
    """Single retrieval, then answer — the non-agentic RAG baseline."""
    passages = env.search(env.symptom(), k=k)
    body = (f"Question: {env.symptom()}\nPassages:\n"
            + "\n".join(f"  {a.text}" for a in passages)
            + '\nReply {"answer": "<short answer>"}.')
    return _answer_text(_call_json(backend, "qarag", body))


def bare_llm_qa(env: BenchmarkEnvironment, backend: LLMBackend, k: int = 12) -> str:
    """All retrievable passages in one shot — the strong long-context baseline."""
    passages = env.search(env.symptom(), k=k) or []
    body = (f"Question: {env.symptom()}\nAll passages:\n"
            + "\n".join(f"  {a.text}" for a in passages)
            + '\nReason over everything and reply {"answer": "<short answer>"}.')
    return _answer_text(_call_json(backend, "qabare", body))


CORE_SOLVERS = {"controller_core": controller_core, "static_rag": static_rag,
                "bare_llm": bare_llm_qa}


# --- runner ------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    solver: str
    em: list[float] = field(default_factory=list)
    f1: list[float] = field(default_factory=list)
    tokens: list[int] = field(default_factory=list)

    def summary(self) -> dict:
        return {"n": len(self.em),
                "EM": st.mean(self.em) if self.em else 0.0,
                "F1": st.mean(self.f1) if self.f1 else 0.0,
                "tokens/q": st.mean(self.tokens) if self.tokens else 0.0}


def run_benchmark(items: list[BenchmarkItem], backend: LLMBackend | None = None,
                  solvers: list[str] | None = None) -> dict[str, BenchmarkResult]:
    from dh.controller.llm import MeteredBackend

    backend = backend or get_backend()
    if backend is None:
        raise RuntimeError("benchmark needs an LLM backend")
    names = solvers or list(CORE_SOLVERS)
    results = {n: BenchmarkResult(solver=n) for n in names}
    for item in items:
        for n in names:
            env = BenchmarkEnvironment(item.question, item.passages)
            meter = MeteredBackend(backend)
            pred = CORE_SOLVERS[n](env, meter)
            results[n].em.append(exact_match(pred, item.answer))
            results[n].f1.append(token_f1(pred, item.answer))
            results[n].tokens.append(meter.total_tokens)
    return results


def render_benchmark(results: dict[str, BenchmarkResult]) -> str:
    lines = ["## Benchmark — agentic retrieval (controller-core vs baselines)", "",
             "| solver | n | EM | F1 | tokens/q |", "|---|---|---|---|---|"]
    for r in results.values():
        s = r.summary()
        lines.append(f"| {r.solver} | {s['n']} | {s['EM']:.2f} | {s['F1']:.2f} | {s['tokens/q']:.0f} |")
    return "\n".join(lines) + "\n"
