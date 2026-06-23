---
project: fathom
goal: Build the showpiece viewer redesign (KPI-rooted causal-graph model) — case1 vertical slice first, then generalize to case5/case6
created: 2026-06-22
status: open
---

## Goal

Rebuild the Investigation-Graph viewer from flat *symptom→hypotheses→evidence* columns into a
**KPI-rooted causal graph** (the controller's real backward-BFS substrate). Build the full pipeline
end-to-end on **case1 (TEC) first** (vertical slice), get user reaction, then point the same generic
code at case5 (abstain) + case6 (buried). **Work happens in the `fathom-viewer` worktree.**

## State

**Done AND verified:**
- `investigate-controller` (8/8 controller fix) merged into `master`; snapshot `52c885e`. Sole
  conflict was `docs/debt.md` (took branch superset). `llm.py` auto-merged (the predicted "3-way
  conflict" was wrong — cost-meter region byte-identical on both sides).
- 8/8 viewer bundles preserved + committed (`7b19dd5`) as tracked replay input at `viewer_site/`.
- `pytest` = **158 passed** on merged master (canonical `tests/` suite; `investigation/spikes/` not in
  `testpaths`).
- Revert anchor: tag **`viewer-baseline-8of8` → 7b19dd5**. Roll back via `git reset --hard
  viewer-baseline-8of8`.
- Cleanup done: `fathom-investigate` worktree removed; `investigate-controller` + `spike-completion`
  branches deleted.
- `fathom-viewer` worktree created on branch `viewer-spike` off `7b19dd5`.
- Baseline 8-case GUI served at **http://127.0.0.1:8777/** (hand-rolled SVG viewer, all 8 correct,
  case5 abstains) — user took "before" screenshots.

**Done, NOT built:** the alignment spec (`handoffs/fathom_visualizer_alignment_2026-06-22.md`) — design
agreed via `/grill-me`, zero code written.

**Not started:** all viewer-spike code.

**Orientation finding (verified):** the recorded bundles carry hypotheses (with `node_ref`), evidence,
links, per-step snapshots, trace — but **no graph topology** (no dim candidate map, no `affects`/`part_of`
edges, no depth). That gap is the enabling export change.

## Next actions

1. **Enabling export change — THERE IS NO EXISTING RE-EXPORT PATH; you must build one.** `export.py`
   today only has `case_bundle(live IG)`; the **only** producer of bundles is `tools/build_viewer_site.py`,
   which runs `diagnose()` **LIVE** (nondeterministic). ⚠️ **Do NOT run `build_viewer_site.py` to
   "refresh"** — it re-rolls the controller and would destroy the frozen 8/8 in `viewer_site/`. Build a
   **new offline re-export** (a function/script, no LLM) that:
   - (a) reads each recorded `viewer_site/case*.json`;
   - (b) regenerates the case deterministically: `spec = CASES_BY_ID[cid]; case = generate(spec.fault,
     list(spec.mechanisms), seed=spec.seed)` — exact sig `generate(fault: str, mechanisms: list[str],
     seed: int = 0)`;
   - (c) extracts the **BFS subgraph** — model on `loop.py::_seed_candidates` (affects-in BFS from
     `symptom_node_id`, depth ≤5, then `part_of` drill), BUT that helper returns only a *flattened
     candidate list with no edges/depth*, so write a NEW extractor that also captures **edges**
     (`affects`, `part_of`) and **depth-from-symptom**, plus `id/type/name` per node. Reading the
     regenerated `case.graph` **directly is fine here** — the export is **eval-side** (it already
     consumes `case.ground_truth` for `trigger`/`root_cause` rendering); the `env._case.graph` "altitude
     smell" was a *controller* concern, NOT an export one, so don't over-build an `Environment` wrapper;
   - (d) merges a `graph` block into the loaded bundle dict, rewrites the JSON (+ regenerate
     `bundles.js` / `manifest.json`).
   - **Verify:** the emitted subgraph node ids match the bundle's `node_ref`s (same seed → stable ids),
     and case1 renders a sane KPI→subsystem→part tree.
2. **D3 render rewrite** (`src/dh/viewer/site.html`): KPI-rooted layered DAG (depth L→R); hypotheses on
   real nodes (colored by belief), non-hypothesis candidates dim; evidence attached to its node; evidence
   lines pruned to dominant + relevant-opposing, opacity/width ∝ |weight|; staged choreography (KPI →
   BFS-expand → hypotheses color → per-step: action → evidence attaches → lines draw after a beat →
   recolor); flow-pulse animation only on the headline path (implicated node → KPI).
3. Build **case1 end-to-end**, get user reaction (Q7 timing is tentative), **then** generalize to
   case5/case6 (same generic code — abstain renders no-winner; buried = deeper graph).

## Key context

- **Spec (authoritative):** `handoffs/fathom_visualizer_alignment_2026-06-22.md` — firm decisions Q1–Q7,
  Tier 1/2/3 scope, build order. Supersedes the view sections of `handoffs/fathom_visualizer_spec.md`.
- **Replay input:** `viewer_site/case{1..8}.json` — the frozen 8/8 runs. **Never re-run to refresh** (n=1,
  nondeterministic). After the export change, a refresh is a sub-second offline re-export.
- **Decisions + why:** viewer+export only, controller untouched (protects the verified 8/8). D3 over
  cytoscape (max control for bespoke layered animation). Curated portfolio reel = case1/5/6 (baseline GUI
  shows all 8). Hypotheses are graph-derived (affects-BFS from KPI), seeded at triage — the outward
  "expansion" is faked in the viewer (Q3), controller unchanged.
- **Controller reality:** `loop.py::_seed_candidates` (affects-in BFS → subsystems → part_of drill) →
  `llm.py::seed_hypotheses` (LLM picks fault hypotheses, `node_ref`'d to nodes). All seeded at step 0.
- **Files:** `src/dh/viewer/export.py` (`case_bundle`, `build_site`, `_step_dict`); `src/dh/viewer/site.html`
  (hand-rolled SVG → rewrite in D3); `tools/build_viewer_site.py` (live build — only needed if regenerating
  bundles, which we avoid).
- **Dev loop:** view edits with `cd viewer_site && python -m http.server 8777` then open
  http://127.0.0.1:8777/ (a baseline server may already be running on 8777). Edit `site.html` + the
  bundles' `graph` block; refresh.
- **Gotchas:** (i) `build_viewer_site.py` is the ONLY existing bundle producer and it runs the controller
  LIVE — never use it to "refresh"; it re-rolls the nondeterministic 8/8 (see action 1). The viewer spike
  itself makes zero LLM calls. (ii) Live builds drive `claude -p` on ONE subscription limit — don't fan out
  agents / don't run with other `claude` sessions live (empty-stderr `claude CLI failed` = limit hit).

## Open decision

**Q7 animation choreography timing is tentative** — user said "lets do that for now, not 100% sure."
Build it as specced; expect the user to redline the timing/staging after seeing case1 move. Keep the
timeline data-driven so it's cheap to adjust.

## Pointers

- `handoffs/fathom_visualizer_alignment_2026-06-22.md` — the refined model (authoritative).
- `handoffs/fathom_visualizer_spec.md` — original viewer spec (hosting constraints, §5 pipeline).
- `docs/road.md` — Phase 1; viewer is the remaining critical-path build (note: top status block has stale
  "complete" framing contradicting the reopening section — owed to the findings/road rewrite, NOT viewer work).
- `investigation/RESULTS.md` — 8/8 audit trail; M1 IS fixed (not deferred); only standing caveat is n=1 variance.
- Owed follow-ups (NOT viewer work): `findings.md` thesis-negative→positive rewrite; the n=3 variance pass
  (load-bearing for any thesis-positive headline at n=1).
