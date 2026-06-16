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

- [x] src/dh/generator/faults.py:FAULTS — authored #4 (calibration_drift, change-is-cause), #6 (detector_bias_drift, absent-cue + buried evidence), #7 (tec variant, tie-breaker), #8 (common_mode_power). All 8 authored; anti-shortcut balance ≈0.33 (2 change-is-cause, 4 trigger≠cause, 1 absent-cue, 1 abstain), gated in test_capability.py.
- [x] src/dh/generator/compose.py:_build_corpus — replaced exclude_artifacts + the special-cased error tuple with one per-fault corpus **delta** (FaultFacts.corpus, CorpusItem). Shared structural corpus stays shared; conclusion-bearing items (window-clean result, reboot, error log) are per-fault facts each forward model declares (C1).
- [ ] tools/run_eval.py — run `--all --runs 3 --budget 8` to produce the ≥3-run variance report (S1, the live A3 run) + the showpiece `viewer_site/`. Case set + scoring ready. **Paused mid-run (session usage limit, 2026-06-16).**
- [ ] src/dh/checks.py:common_mode_check + controller interpret — **REGRESSION SIGNAL (verify live):** in the single A3 case1 run the controller scored acc=0 (wrong cause) though trig/conflict=1 (the sweep worked). The earlier pre-additions smoke got case1 right (acc=1). Captured evidence (the live propose-prompt) shows the LLM reading `common_mode=false` on case1's TEC **cascade** (staggered downstream onsets, spread≈4.25d) as "independent faults," crediting the laser/detector decoys and demoting TEC; compounded by 3 thermal hypotheses co-saturating at the +3.0 clamp (margin≈0 → no clean leader → synthesize mis-picks). The case8 checks (common_mode, detector_health) are cross-case confusers on case1. Fix candidates (need a live run to validate, so deferred): (a) common_mode_check distinguishes a causal *cascade* (one cause, lagged) from truly *independent* onsets rather than only "synchronous vs not"; (b) interpret prompt: a non-common-mode result does NOT imply independent faults (a cascade is also not common-mode); (c) reconsider seeding 5 overlapping thermal hypotheses. Re-measure case1 accuracy over ≥3 runs after any change (do NOT tune to manufacture a win, #5).
- [ ] src/dh/eval/benchmark.py — add tools/load_musique.py (the `benchmark` extra) and run the real n=20 fail-fast (A5). TIME-BOXED, not a ship-blocker; report-only if not competitive. Never ship the synthetic smoke (B9).
- [x] src/dh/controller/llm.py:interpret_result — A6 prompt iteration: SYSTEM_PROMPT + propose/interpret now push discriminating actions, negative links (contradict a decoy), and recording a demoted trigger / stuck channel in conflicts. Re-measure live (A3). B7 also handled structurally by the cumulative log-odds clamp (beliefs.MAX_LOG_ODDS).
- [x] src/dh/controller/llm.py:interpret_result — A7: evidence `source` action-key stripped to the check name and signals mapped to metric nodes, applied identically to all four solvers (test_scoring_symmetry.py). CHECK_IDS now matches the real check names (config_diff was mismatched before).
- [ ] src/dh/environment.py:_bm25_rank — plain BM25, no stemming; the `hybrid` extra (sentence-transformers) is the intended fix. Deferred (A9): lexical search is adequate at the spike's corpus volume; hybrid only matters at corpus-volume cases / the benchmark.
- [x] src/dh/environment.py:LidarEnvironment.query_telemetry — the `condition` arg now filters on a parallel `spec["conditions"]` tag list (graceful no-op when unpopulated); the full-build D3/D4 cases populate it.
- [x] src/dh/schemas.py:InvestigationGraph.snapshots — handled: loop._snapshot appends a snapshots-stripped deep copy (no O(n²) nesting).
