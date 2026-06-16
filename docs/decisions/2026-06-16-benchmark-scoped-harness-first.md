# Benchmark track: harness built + mechanism proven; real MuSiQue run deferred

**Date:** 2026-06-16 · **Status:** accepted · **Milestones:** M4.5 (decision gate), M8

## Decision

Build the benchmark **harness** (`src/dh/eval/benchmark.py`: `controller_core`,
`static_rag`, `bare_llm` over `BenchmarkEnvironment`; EM/token-F1; tokens/q) and prove the
**mechanism** live on a synthetic multi-hop item — the controller-core degrades to
search-only and answers (verified: EM 1.0, ~183 tokens). **Defer** the real MuSiQue dev
subset (n=20 fail-fast → n=100) until a dataset download (the `benchmark` extra) and a live
token budget are in hand.

## Why

- The M4.5 gate is explicitly a *fail-fast scope decision* (build plan): if the
  diagnosis-shaped core isn't competitive at QA, scope the claim down rather than discover it
  at M8. With no `datasets` install and a finite subscription-token budget this session, the
  honest move is to make the harness real and one command away, not to fake a number.
- The synthetic fixture proves plumbing, **not** competitiveness (its answers sit directly in
  a passage). A real EM/F1 read requires MuSiQue's genuine multi-hop items.
- This is the spec-sanctioned outcome: acceptance T4 allows the benchmark to be "scoped down
  to report-only" (spec §9), and success S1–S4 does not depend on the benchmark at all.

## The scoped next step

1. `pip install -e ".[benchmark]"`; add a `tools/load_musique.py` → `list[BenchmarkItem]`.
2. `run_benchmark(items[:20], get_backend())` — the fail-fast read; if controller-core is not
   competitive with `bare_llm`/`static_rag` at comparable tokens, report-only and note it.
3. If competitive, run n=100 and add the table to the writeup (M8).

The lidar finding (the portfolio core) stands independently of this track.
