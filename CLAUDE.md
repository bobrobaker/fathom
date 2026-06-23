# Fathom

Fathom is a diagnostic harness: one abductive LLM **controller** (triage → maintain a
hypothesis differential → propose the single most-discriminating next action) run
against two environments — a generated **lidar** system-under-test and a QA
**benchmark** — through one `Environment` interface. Reasoning (the LLM) is separated
from evidence (deterministic checks, retrieval, graph traversal); the controller's live
state is an **Investigation Graph** the eval reads and a viewer renders. The point is a
clean, defensible **finding** — measured against strong, fair baselines on accuracy,
evidence quality, token cost, and calibrated abstention — that doubles as a portfolio
piece on AI-native test architecture. Built in two stages: a thin vertical **spike**
first, then the full MVP, spike-conditioned.

## Map

- `docs/road.md` — phase tracker. It is a *tracker*, not a spec; the brief is authoritative.
- `docs/handoff/` — the authoritative build brief. **Read `00_README_for_coding_agent.md`
  first** (read-order + non-negotiables); `spike_spec.md` wins on any conflict;
  `spike_build_plan.md` sets milestone order (M0→M9).
- `docs/decisions/` — design calls + why. `docs/debt.md` — deferred-work shelf.
- **Web viewer / front-end work → read `docs/viewer_dev.md` first** (architecture, bundle data
  contract, dev loop, D3/animation gotchas). The showpiece is `src/dh/viewer/site.html`.
- `src/dh/` — controller (loop/voi/beliefs/llm), generator, environment, baselines, eval,
  viewer. `tests/`, `fixtures/tec_case.json` (golden), `config.yaml` (model, thresholds, seeds).
- Governed product surfaces (lesson-routing menu, each with admission rules):
  - **Difficulty catalog** (mechanism IDs) — every case must be *capability-bound*
    (unsolvable by one context dump); anti-shortcut balance ≈0.5 across the set.
  - **Eval rubric** — two families (accuracy / capability), reported separately; never
    tune cases or baselines to manufacture a win.
  - **Baselines** — must be strong & fair (a best-honest `bare_llm`, a real `react`).
  - **Typed-link ontology** — tiered A/B/C; provisional, re-evaluated post-spike.

## Context hygiene

- Grep for symbols, fields, constants, and call sites before reading any file.
- Structure-scan before any markdown range read: `grep -n "^##" <file>.md` first, then
  bounded reads of only the needed sections. Applies to all docs, not just code.
- Reads over ~150 lines require a stated reason; prefer one complete function/class
  range over multiple partial reads.
- Separate required from conditional reads up front; read only files the change touches.
- Don't re-read what grep or prior output already answered.
- Constrain repo-wide greps to source extensions (e.g. `--include="*.py"`).

## Working here

- Validation: `.venv/bin/pytest`
- Pre-commit linter: ERROR blocks, WARN advises (`tools/lint.py`). Arm once on a fresh
  clone: `git config core.hooksPath .githooks`.
- **Never codify silently.** Rule and convention changes are proposed and accepted
  before writing — use `/codify`.
- **Design calls leave a record.** Project-internal design decisions land as
  date-slug files in `docs/decisions/` — the call plus its why — so a later session
  inherits the reasoning instead of relitigating it. Cross-cutting calls that outlive
  the project go to your portfolio-level decision store.
- Wrapping up mid-task: `/handoff` writes a decision-ready handoff to `handoffs/`.

## Dispatch

- The roadmap is `docs/road.md`; work descends roadmap → workstream → bucket
  (`docs/workstreams/`). Find the active workstream with
  `grep -r "^Progress:" docs/workstreams/ --include=workstream.md`.
- `/dispatch` turns a phase discussion into a workstream + buckets, or executes the
  next bucket per the workstream's execution protocol.

## Tech-debt

- After a logical chunk, pass over the functions you just edited and append any deferred
  work to `docs/debt.md` (`path:symbol — observation (why deferred)`). Not the roadmap
  or `docs/decisions/`. `/dispatch` surfaces shelf items whose files the next bucket
  touches, to fold in.
