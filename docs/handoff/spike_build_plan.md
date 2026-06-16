# Spike build plan — diagnostic harness

**Status:** ordered execution plan for an LLM coding agent. Pair with `spike_spec.md` (the contracts and acceptance criteria, referenced by §). Build in this order; each milestone has a **done-when** that must pass before moving on.

---

## Repo layout

```
diagnostic-harness/
  pyproject.toml
  config.yaml                 # model id, thresholds (τ_dom, τ_margin, τ_min, budget), seeds
  src/dh/
    schemas.py                # all pydantic models from spec §3 (single source of truth)
    graph.py                  # TypedGraph helpers: neighbors(), traverse()
    environment.py            # Environment ABC + LidarEnvironment + BenchmarkEnvironment (spec §4)
    generator/
      __init__.py             # generate(fault, mechanisms, seed) -> Case (spec §5)
      signatures.py           # ramp/step/drift/flatline/correlated-pair + 1 dynamic gen
      faults.py               # per-fault forward-effects models (TEC, laser, window, ...)
      compose.py              # artifacts (tickets/reports/logbooks/docs/diag_actions) + BOM + ground truth
      cases.py                # the ≥8 spike cases (spec §5.3) as (fault, mechanisms, seed) tuples
    checks.py                 # deterministic checks (spec §6.5), pure functions over telemetry
    controller/
      loop.py                 # diagnose() abductive loop (spec §6.1)
      llm.py                   # prompt builders + Anthropic calls; structured parsing
      voi.py                   # action scoring (spec §6.3)
      beliefs.py              # log-odds update + sigmoid (spec §6.4)
    baselines.py              # shortcut, bare_llm, react (spec §7) — all return Answer
    eval/
      bespoke.py              # rubric metrics (spec §8.1) + report table
      benchmark.py            # MuSiQue runner for controller-core (spec §8.2)
      report.py               # uplift table renderer (md/console)
    viewer/
      export.py               # IG (+ snapshots) -> ig.json
      index.html              # static D3/vis-network render of ig.json
  tests/
    test_schemas.py
    test_generator.py         # determinism per seed; ground-truth well-formedness
    test_checks.py            # each check on a known fixture
    test_controller_tec.py    # the milestone-4 gate: solves case #1
  fixtures/
    tec_case.json             # case #1 serialized (the worked example), the golden fixture
```

---

## Milestones (build in order)

### M0 — Skeleton + schemas
Implement `schemas.py` (spec §3) and `graph.py` helpers. Wire `config.yaml`, `pyproject.toml`, `pytest`.
**Done-when:** `test_schemas.py` round-trips every model; `TypedGraph.neighbors()` works on a hand-built 4-node graph.

### M1 — Generator for case #1 (the TEC case)
Implement `signatures.py`, the TEC `faults.py` entry, `compose.py`, and `cases.py[0]`. Reproduce the worked example's telemetry/config/logbook/error/corpus/diagnostic-actions + ground truth exactly. Serialize to `fixtures/tec_case.json`.
**Done-when:** `generate("tec_degradation", [...], seed=0)` is deterministic and matches the worked example's signatures (intensity −15% temp-correlated, TEC at 92%, diode temp above setpoint, detector_temp flatlined, reboot at t−2d with onset at t−6d); `test_generator.py` passes.

### M2 — LidarEnvironment + checks
Implement `environment.py::LidarEnvironment` over a `Case`, and `checks.py` (all six, spec §6.5). `search()` = BM25 over artifacts (hybrid optional).
**Done-when:** each check returns the expected structured result on `tec_case.json` (`test_checks.py`): `temp_correlation_check` reports r≈0.9; `onset_vs_event_check` reports onset precedes reboot; `channel_sanity_check` flags `detector_temp`.

### M3 — LLM plumbing
Implement `controller/llm.py`: structured prompt builders for (seed_hypotheses, propose_actions, interpret_result→evidence+links, synthesize) and robust JSON parsing of model output. Pin the model in `config.yaml`.
**Done-when:** each LLM call returns parseable structured output on a stub input; failures degrade to a logged retry.

### M4 — Controller solves case #1  ← **primary gate**
Implement `voi.py`, `beliefs.py`, and `loop.py::diagnose()` (spec §6.1–6.4). Run on `tec_case.json`.
**Done-when:** `test_controller_tec.py` passes — the controller returns root_cause = TEC degradation, cites the load-bearing evidence, flags the `detector_temp` channel and demotes the reboot, recommends the swap-test, within budget. Snapshots populate for the viewer.

### M4.5 — Benchmark fit smoke-test (fail-fast)
Before authoring more cases, stand up a minimal `BenchmarkEnvironment` over ~20 MuSiQue items and run `controller-core` (controller minus lidar checks). This answers the audit-#2 question *early*: is the diagnosis-shaped core even competitive at QA?
**Done-when:** you have a rough EM/F1 for `controller-core` vs `bare_llm` on 20 items. **Decision gate:** if the core is clearly not competitive, scope the benchmark claim down now (report-only, or drop) rather than discovering it at M8 — and note it for the writeup. A cheap early read, not the full run.

### M5 — Baselines
Implement `baselines.py` (spec §7). Make `bare_llm` a *strong* long-context prompt; `react` shares M2 tools but lacks the IG/VOI structure.
**Done-when:** all three run on `tec_case.json` and return `Answer`s; `shortcut` blames the reboot (i.e., gets it wrong) as expected.

### M6 — Bespoke eval on case #1 + first uplift row
Implement `eval/bespoke.py` (rubric, spec §8.1) and `eval/report.py`. Score all four solvers on case #1.
**Done-when:** the report prints the per-metric table; the controller’s trigger-discrimination and conflict-handling exceed `bare_llm`/`react` on this case.

### M7 — Expand to the full case set (≥8)
Author cases #2–#8 (`cases.py`, `faults.py`, `compose.py`) per spec §5.3, including the **abstain** case (#5) and the **buried-evidence** case (#6). Enforce the **anti-shortcut balance** across the set (≈0.5 correlation between salient-recent-event and cause).
**Done-when:** the bespoke eval runs over all cases; the report shows the controller meeting acceptance criteria §9.1–§9.3; case #5 resolves as a correct **abstain**.

### M8 — Benchmark track
Implement `environment.py::BenchmarkEnvironment` + `eval/benchmark.py` over a **MuSiQue** dev subset (n=100). Run `controller-core` (no lidar checks), `bare_llm`, `static_rag`.
**Done-when:** EM/F1 + tokens/question reported for all three; controller-core meets §9.4.

### M9 — Viewer
Implement `viewer/export.py` (IG + snapshots → `ig.json`) and `viewer/index.html` (load JSON; render nodes colored by confidence sign; step slider over snapshots; trigger node visually distinct).
**Done-when:** opening `index.html` on case #1's export shows the graph growing/recoloring across steps (§9.5).

---

## Critical-path notes for the coding agent

- **M1 and M4 are the spine.** Everything downstream depends on a correct case #1 and a controller that solves it. Do not start M7 (more cases) before M4 passes — debugging the loop on eight cases at once is the trap.
- **The ground truth is eval-only.** It must never enter the controller's context. Enforce with a typed boundary (the environment never exposes `Case.ground_truth`).
- **Keep determinism.** Seed the generator; pin the model; set temperature low. The eval must be re-runnable to the same numbers (modulo LLM nondeterminism, which should be reported as variance over ≥3 runs).
- **Log every action and tool result** to a per-case trace; the IG snapshots are derived from this. The trace is also the audit artifact for the writeup.
- **Baseline fairness is not optional** — a weak `bare_llm` makes the whole result hollow (see the audit). Iterate its prompt until it's the best honest version.

---

## What the full-build doc set will add (not now)

Generator at scale + the remaining faults to depth; realistic corpus volume and the LLM-roughening pipeline on by default; richer environment tools / MCP; a formal (entropy-based) VOI; the polished live viewer; calibration against real lidar specs; CI and a reproducibility harness for the writeup.
