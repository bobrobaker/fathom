---
project: fathom
goal: Finish the spike bespoke-eval deliverable — fix per-call cost overhead, run variance-backed n=3, write A4 findings (controller is currently thesis-negative)
created: 2026-06-21
status: open
---

# Fathom — eval fairness & cost audit → n=1 shipped, n=3 + A4 pending

## Goal
Land the Phase-1 spike's bespoke-eval deliverable honestly. This session fixed the eval's
fairness/scoring bugs and shipped an **n=1** all-8-case report; the next session should make
the eval **affordable** (per-call cost is the blocker), run **n=3** for variance, then write
the **A4 findings doc**. Current measured result is **thesis-negative** (the controller loses).

## State

**Done AND verified** (ran live / tests green):
- **react baseline fixed — 3 fairness bugs** (`src/dh/baselines.py`). Was scoring all-zeros on
  every case (a harness bug, not weakness). Fixes: (1) `_react_execute` accepts check-name under
  `name`/`check_id`/`check`/`check_name` + prompt states `run_check args={"name":…}`; (2) prompt
  requires **bare ids** in causal_chain/cited_evidence/ruled_out/conflicts (scorer `_canon` does
  `split(":")[-1]`, so prose citations scored 0); (3) prompt parity with bare_llm's "distinguish
  cause from salient event / note channels" framing. Verified: live react on case1 went 0→
  acc/loc/trig/conf=1.0, evF1=0.60.
- **scorer fixes** (`src/dh/eval/bespoke.py`): #1 `evidence_f1` now standard F1 (removed the
  `+len(hallucinated)` double-penalty; hallucination reported in `CaseScore.extra`). #2
  `conflict_handling` now `_f1(surfaced, gold_conf)` (was recall — gameable by dumping ids).
  **spike_spec.md §8.1 reconciled to F1** (was authoritative "fraction surfaced"=recall).
- **158/158 tests pass** (`.venv/bin/pytest`). New regression tests: react alias variants,
  conflict over-surfacing guard.
- **n=1 all-8-case deliverable assembled** → `reports/bespoke.md` with 2 honest caveats baked in
  (variance not characterized; cost column is content-undercount). Per-case raw outputs in
  `reports/seg_case{2..8}.md` + case1 region.
- **Audited clean** (no bugs): ground-truth leakage (#1 invariant holds), conflict sweep
  (deterministic, observable-only), abstain logic, belief math, ground-truth consistency.

**Done but NOT variance-verified** (n=1 only — DO NOT treat as final):
- The headline finding: controller accuracy **4/8** (bare_llm 6, react 5, shortcut 2). Controller
  fails its *claimed-strength* axes — change-is-cause (4,8), abstain (5), tie-breaker (7) — and its
  capability edge is mostly the deterministic conflict sweep, which react matches by reasoning.
  **Indicative, not confirmed**: LLM variance is real (case1 flipped acc 0→1 across runs earlier).

**NOT done:**
- Per-call cost fix (diagnosed only). `MeteredBackend` real-`usage` fix. The n=3 run. A4 findings
  doc. The Phase-2 interpret-prompt fix (shelved by decision).

## Next actions (ordered)
1. **DONE 2026-06-22 — per-call cost overhead fixed (~280x cheaper input, on subscription).** The
   2026-06-21 root-cause hypothesis was WRONG (it blamed global CLAUDE.md + dynamic sections and
   recommended `--exclude-dynamic-system-prompt-sections` / scratch `$HOME` / OAuth token — all
   measured to NOT help or to HURT). The real fix, baked into `CLIBackend` and used automatically
   by `get_backend()`: **`--tools ""`** (removes the ~14-17k built-in tool DEFINITIONS — note
   `--allowed-tools ""` only removes permissions, not defs) **+ `--setting-sources project,local`**
   (drops the global CLAUDE.md). Per-call prefix ~21k → ~150 tokens; no API key, no token, auth
   intact. See `docs/decisions/2026-06-22-claude-cli-prompt-cache.md`.
2. **DONE 2026-06-22 — `MeteredBackend` reads real `usage`** (input / cache-creation-5m/1h /
   cache-read / output) and exposes price-weighted `cost_tokens` (sonnet-4-6 ratios: output 5.0x,
   read 0.1x, creation 1.25x/2.0x). run_eval.py + build_viewer_site.py report `cost_tokens`.
3. **Re-run n=3 — now affordable, config is automatic.** No flags to set; just run the harness.
   **Read the RUN PROTOCOL in `tools/run_eval.py`'s docstring.** Run **per-case with `--out`** so a
   failure doesn't lose prior cases or clobber the n=1 `reports/bespoke.md`:
       for c in case1 case2 case3 case4 case5 case6 case7 case8; do
         .venv/bin/python tools/run_eval.py --runs 3 --case $c --out reports/n3_$c.md
       done
   **Close other interactive `claude` sessions first** (subscription serializes under concurrency —
   monition t61) but do NOT kill the user's brain2 session.
   **Config A/B done 2026-06-22 (case1, controller, n=3):** NEW `--tools ""` → [detector, None, tec]
   1/3; OLD `--allowed-tools ""` → [detector, detector, tec] 1/3. Same accuracy + same answer set →
   the case1 flip is controller variance, NOT caused by `--tools ""`; the configs are comparable.
   NEW total `cost_tokens` ≈ half of OLD (input scaffolding gone; cost is now output-dominated, so
   total is ~2x not the ~280x input-axis figure). Caveat: NEW produced one `None`/abstain run OLD
   didn't — within n=3 noise but unresolved; a ≥3-run A/B on a STABLE case (not case1, a flipper)
   would settle behaviour-equivalence cleanly. (Throwaway runner: /tmp/fathom_config_ab.py.)
4. **Write A4 findings** (`docs/findings.md` §4): per-metric × per-case (NOT a single capability
   mean — several capability components are trivial/redundant per case), the honest thesis-negative
   result, real cost premium, two families separate. This IS the deliverable.

## Key context
- **Decisions (user, 2026-06-21):** no n=3 *this* session (budget); ship n=1. Report the controller
  weakness as-is; **shelve the interpret-prompt fix to Phase 2** (patching it against these 8 cases =
  overfitting a negative into a manufactured win, violates #5).
- **Workflow adopted:** audit → fix → run a *small segment* → audit results in context → only then
  expand. Replaced launch-full-run/kill-restart thrash. Note: an in-flight run can't adopt a code fix
  (`score()` runs on the module loaded at launch) — a fix only lands via a fresh run.
- **Controller weakness mechanism** (the why behind 4/8): interpret step over-credits nominal/at-spec
  checks as positive support → hypothesis saturates to the +3.0 log-odds clamp (conf 0.953) →
  `tau_min=0.55` only needs log-odds >~0.2 → abstention blocked. Same mechanism as the old case1
  regression. Existing "nominal argues against" prompt guidance is insufficient.
- **#5 is live**: never tune cases/baselines/scoring to manufacture a controller win. All fixes this
  session either strengthened a baseline or corrected a metric toward its definition.
- Files touched: `src/dh/baselines.py`, `src/dh/eval/bespoke.py`, `tools/run_eval.py` (shortcut
  trace), `tests/test_baselines.py`, `tests/test_eval.py`, `docs/handoff/spike_spec.md` (§8.1),
  `docs/decisions/2026-06-21-eval-fairness-and-scoring-audit.md`, `docs/debt.md`, `reports/bespoke.md`.

## Open decision
**Which cost-fix lever for action #1?** Options: (a) `--exclude-dynamic-system-prompt-sections` —
free, keeps subscription, partial reduction; (b) skip global CLAUDE.md via `--setting-sources`/scratch
`$HOME` — bigger win, must verify OAuth survives; (c) `--bare`+ANTHROPIC_API_KEY — full elimination
but switches to metered API $, off the subscription budget. **Recommendation: try (a)+(b) together,
measure with `--output-format json`; fall back to (c) only if OAuth can't be preserved.** Also lower
`--budget` 8→4 to ~halve controller calls if still too costly.

## Pointers
- Tracker: `docs/road.md` Phase 1 (the "Remaining critical path" section — now partly superseded:
  A3 is n=1-shipped, A4 pending).
- Decision record (authoritative for this session): `docs/decisions/2026-06-21-eval-fairness-and-scoring-audit.md`.
- Debt shelf (the cost-fix + interpret-prompt + n=3 items): `docs/debt.md` (2026-06-21 block).
- Deliverable: `reports/bespoke.md`. Spec: `docs/handoff/spike_spec.md` (§8.1 rubric, §9 exit S1).
