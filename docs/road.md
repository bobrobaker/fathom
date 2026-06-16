# Fathom Roadmap

## 1. How to use this doc

Purpose: orient sessions around project phase, history, next work, and bounded
implementation surfaces.

**This is a tracker, not a spec.** The authoritative plan is the build brief in
`docs/handoff/` — read `00_README_for_coding_agent.md` first. `spike_spec.md` is
authoritative for *what* to build (contracts, components, acceptance) and wins on any
conflict; `spike_build_plan.md` is authoritative for *order*. This doc tracks phase
status and points at the governing brief sections; it never duplicates the plan. See
`docs/decisions/2026-06-16-road-tracks-the-brief.md` for why.

Current phase marker:

`<----- Ongoing phase ----->`

A **phase** is a high-level deliverable with stable interfaces. A **workstream** is a
refinable effort inside a phase. A **bucket** is a bounded implementation slice,
usually sharing files, invariants, or tests.

---

## 2. Phase roadmap

### Phase 1 — The spike: measurable uplift (or its honest absence)

`<----- Ongoing phase ----->`

**Status:** not started. This is the next keystroke (`spike_build_plan.md`; the
full build is the *destination*, not now).

**Deliverable:** a runnable repo (per `spike_build_plan.md`, milestones M0→M9)
producing — the **bespoke eval report** (`controller` vs `shortcut`/`bare_llm`/`react`,
accuracy + capability families, variance over ≥3 runs); the **early MuSiQue read**
(M4.5; full M8 run if competitive); and the **Investigation-Graph viewer** rendering
case #1 across its steps.

**Surfaces:** `src/dh/` (`schemas`, `graph`, `environment`, `generator/`, `checks`,
`controller/`, `baselines`, `eval/`, `viewer/`), `tests/`, `fixtures/tec_case.json`
(golden), `config.yaml`, `pyproject.toml`. (The brief names the package `src/dh/`; it
owns the code layout.)

**Design:** authoritative in `docs/handoff/spike_spec.md` — contracts §3, environment
interface §4, generator §5, controller loop §6, baselines §7, evals §8, acceptance §9.
Non-negotiables (`00_README` §"Non-negotiable rules"):

- **Ground truth is eval-only** — `Case.ground_truth` never enters the controller's
  context; enforced at the environment boundary (the env never exposes it).
- **Determinism** — seed the generator, pin the model, low temperature; LLM
  nondeterminism reported as variance over ≥3 runs.
- **Baselines strong and fair** — a weak `bare_llm` invalidates the result.
- **Capability-bound difficulty** — if reading the whole corpus once solves a case, cut it.
- **Success = the finding, not the win** — ship on a clean, defensible measurement
  whether or not the controller beats the baselines.
- **Spine first** — M1 (case #1) and M4 (controller solves it) before authoring the
  rest; run the M4.5 benchmark smoke-test early.
- **Contract before code** — the §3 pydantic schemas are the data contract; they land
  as `src/dh/schemas.py`, the single source of truth (not duplicated into
  `docs/contracts/` — see the decisions record). This is M0.

**Milestone tracker** (gate each before the next; done-when in `spike_build_plan.md`):

- [ ] M0 — skeleton + schemas (`test_schemas` round-trips; `TypedGraph.neighbors()`)
- [ ] M1 — generator for case #1, the TEC case → `fixtures/tec_case.json` (spine)
- [ ] M2 — `LidarEnvironment` + the six deterministic checks (`test_checks`)
- [ ] M3 — LLM plumbing (structured prompt builders + robust JSON parsing)
- [ ] M4 — controller solves case #1 (`test_controller_tec`) ← primary gate (spine)
- [ ] M4.5 — benchmark fit smoke-test on ~20 MuSiQue items (fail-fast scope gate)
- [ ] M5 — baselines (`shortcut`, strong `bare_llm`, real `react`)
- [ ] M6 — bespoke eval on case #1 + first uplift row
- [ ] M7 — expand to the full case set (≥8), incl. abstain (#5) + buried-evidence (#6)
- [ ] M8 — benchmark track (MuSiQue n=100; `controller-core` vs `bare_llm`/`static_rag`)
- [ ] M9 — viewer (`ig.json` export + static `index.html`, evidence-colored, step slider)

**Validation:** `.venv/bin/pytest` (the milestone done-when gates: `test_schemas`,
`test_generator`, `test_checks`, `test_controller_tec`), plus the bespoke eval report
rendering and the viewer opening on case #1's export.

**Estimate:** large / multi-session (M0→M9). Dispatch into workstreams per milestone
cluster; the spine (M1, M4) is one focused workstream before any case-set expansion.

**Exit:** spike **success S1–S4** (`spike_spec.md` §9) — a well-formed, reproducible
eval (≥9 cases, capability-bound, anti-shortcut-balanced, ≥3 runs, variance reported);
strong & fair baselines; clean separate-family reporting whatever the outcome; the
viewer rendering case #1. Thesis-**confirmation T1–T4** (the controller actually wins)
is the hoped-for result, *not* the ship gate.

---

### Phase 2 — Full build A: scale, calibrate, lock schema (spike-gated)

**Status:** sketched; refine when Phase 1 exits and its findings are in hand.

**Deliverable:** scale the case set + difficulty catalog to realistic volume
(capability-bound throughout); calibrate the SUT numbers against real automotive-lidar
specs; lock the typed-link ontology to what the spike actually traversed. Governed by
`docs/handoff/full_build_spec.md` §1–§3, §9 (Phase A). Begins only after the spike's
finding, which may revise these claims by prior agreement.

**Exit:** realistic-volume labelled case set; schema locked to spike-validated links;
numbers calibrated; the generator standing alone as a clean engineering artifact.

---

### Phase 3 — Full build B: full harness + polished live viewer

**Status:** sketched; refine when Phase 2 exits.

**Deliverable:** the polished controller — formal entropy-reduction VOI alongside the
spike's LLM-scored version, richer tool/retrieval interfaces (optionally MCP),
controller/environment separation preserved — and the showpiece **live Investigation-
Graph viewer** (hypotheses appearing/recoloring, the demoted trigger, honest
abstention), reading the same IG state object. `full_build_spec.md` §4, §6.

**Exit:** the harness runs the full case set; the live viewer is the portfolio's lead demo.

---

### Phase 4 — Full build C: full eval suite + reproducibility + the writeup

**Status:** sketched; refine when Phase 3 exits.

**Deliverable:** the bespoke eval at scale + multiple benchmarks (MuSiQue + HotpotQA +
optional newer set, scope set by the spike's benchmark finding); a reproducibility
harness (seeds, pinned model, reported variance) so every writeup number is defensible;
CI running the eval on every change; and the **portfolio layer** — a writeup that leads
with the designed eval, the finding framed modestly and honestly, a README opening with
the eval and headline numbers + the live demo, lidar framing kept legible.
`full_build_spec.md` §5, §7, §8.

**Exit:** a presentable portfolio piece — eval-led writeup, reproducible numbers, the
live demo, the honest finding.
