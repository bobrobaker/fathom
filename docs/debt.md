# Fathom — tech-debt shelf

Project-local deferred work: refactors, architecture concerns, "fix later" items
spotted while editing. One row per item, append-only; check off when done, delete when
it stops mattering. Not the roadmap (planned work) or `docs/decisions/` (calls made) —
this is debt discovered mid-implementation.

**Capture trigger:** after a logical chunk, make one pass over the functions you just
edited and append anything deferred here, with enough locus to act on it cold.

**Row format:** `- [ ] path:symbol — observation (why deferred)`

## Shelf

<!-- e.g. - [ ] auth/session.py:refresh_token — re-derives the key every call (hot path); cache once the format stabilizes -->

- [ ] src/dh/generator/faults.py:FAULTS — author cases #3 (window_contamination, spatial), #4 (calibration_drift, post-release config+chained), #6 (detector_bias_drift, buried evidence via traversal), #7 (tec variant, expensive tie-breaker), #8 (common_mode_power). Specs already in cases.py; compose is generalized. Needed for S1 (≥9 cases). Enforce anti-shortcut balance ≈0.5 across the set as they land (#2/#5 already decorrelate salient-event from cause).
- [ ] src/dh/generator/compose.py:_build_corpus — the corpus is currently shared across faults, but some artifacts encode fault-specific conclusions (act.window_clean says "no improvement → not contamination", which is correct for #1 but would CONTRADICT #3 window_contamination where the window IS the cause). Before authoring #3/#4/#6, make diagnostic-action results + prior-report conclusions fault-aware (a per-fault corpus delta on FaultFacts), so each case stays internally consistent (the generator's core contract). This is why #3 wasn't rushed in this pass.
- [ ] tools/run_eval.py — run `--all --runs 3` once the full case set exists to produce the ≥3-run variance report (S1). Currently demonstrated at n=1 on case1 (reports/bespoke_case1.md).
- [ ] src/dh/eval/benchmark.py — add tools/load_musique.py (the `benchmark` extra) and run the n=20 fail-fast then n=100 read; harness + live mechanism are done (see decision record).
- [ ] src/dh/controller/llm.py:interpret_result — live model under-discriminates the decoy (laser stays ~0.99 alongside TEC) and doesn't always surface the demoted trigger (log.reboot) as a conflict. Prompt-quality, the iterated artifact per spec §6.6; the M6 capability-family eval quantifies it. Don't over-tune to manufacture a win (non-negotiable #5) — iterate the propose/interpret prompts, then re-measure.
- [ ] src/dh/controller/llm.py:interpret_result — live evidence `source` comes back as the action key ("run_check:tec_load_check") not the check name ("tec_load_check"), so evidence-F1 vs gt.load_bearing_evidence will miss. Normalize source to the check/artifact id when scoring at M6 (or in interpret). Also map signal↔metric node (detector_temp_C ↔ metric.detector_temp) for conflict-handling scoring.
- [ ] src/dh/environment.py:_bm25_rank — plain BM25, no stemming (search "founder" misses "founded"); the `hybrid` extra (sentence-transformers) is the intended fix (spec §10 "hybrid optional"). Deferred: lexical search is adequate for case #1's small corpus; hybrid matters at corpus-volume cases (#6) and the benchmark.
- [ ] src/dh/environment.py:LidarEnvironment.query_telemetry — the `condition` arg is accepted but ignored (no D3/D4 condition-dependent signals in case #1). Deferred: wire it when authoring the intermittent (D3) / bifurcation (D4) cases at M7.
- [ ] src/dh/schemas.py:InvestigationGraph.snapshots — the loop's `ig.snapshots.append(deepcopy(ig))` (spec §6.1) will recursively copy prior snapshots into each new one (O(n²) memory, nested). When wiring the loop at M4, snapshot a snapshots-stripped copy (e.g. `ig.model_copy(deep=True, update={"snapshots": []})`). Deferred: no loop exists yet at M0, so it can't be exercised or tested.
