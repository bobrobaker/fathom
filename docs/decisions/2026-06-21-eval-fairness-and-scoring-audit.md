# Eval fairness & scoring audit: react made fair, scorer de-quirked

> **SUPERSEDED IN PART (2026-06-22).** The *fairness/scoring fixes* (react, scorer) still hold. But
> the **thesis-negative 4/8 finding** and the decision to **shelve the interpret-prompt over-crediting
> fix to Phase 2** are superseded: the controller investigation (branch `investigate-controller`)
> implemented that fix (the M1 affirmative-evidence gate) and others, reaching **8/8 live**. Current
> result: `investigation/RESULTS.md`; tracker: `docs/road.md` Phase 1 Note (2026-06-22). This remains
> the provenance of the 2026-06-21 decisions, not current truth.

**Date:** 2026-06-21 · **Status:** accepted · **Milestones:** A3 (live eval), A4 (findings) · **Surfaces:** `src/dh/baselines.py`, `src/dh/eval/bespoke.py`, `tools/run_eval.py`

## Context

Driving the live A3 run, `react` scored **all-zeros on every case/run**. An audit of the
running eval's own captured prompt (not a guess) traced it to harness defects at the
prompt/parse boundary — `react`'s loop logic was sound (scripted tests pass); its correct
reasoning just never survived into the scored `Answer`. A follow-on audit of the scorer found
two scoring quirks of the same class (a number that doesn't measure what it claims).

## Decisions

**React baseline — three fairness fixes (non-negotiable #3; each makes react *stronger*, so
safe under #5):**

1. **`run_check` arg-key mismatch** — the model keyed the check name as `check_id`; the
   executor read `args["name"]` → `""` → "unknown check" → every check errored → react burned
   its step budget and abstained. Fix: executor accepts `name`/`check_id`/`check`/`check_name`,
   **and** the react prompt now states `run_check args={"name":…}`. Root cause of the all-zeros.
2. **Citation format** — react cited `"tec_load_check: <prose>"`; the scorer's `_canon` does
   `split(":")[-1]`, grabbing the prose, never the id → evF1=0 despite citing the right checks.
   Fix: react prompt requires **bare ids** in causal_chain / cited_evidence / ruled_out / conflicts.
3. **Prompt-guidance parity** — `bare_llm`'s body coaches "distinguish a true cause from a
   merely salient recent event; note unreliable channels"; react's did not, so it never surfaced
   the decoys into `conflicts` → trig=0, conf=0. Fix: mirror `bare_llm`'s exact framing into
   react's prompt (parity, **not** rubric hints). After parity react scores case1 acc/loc/trig/
   conf=1.0, evF1=0.60 — competitive with the controller. The original all-zeros would have been
   a **false controller win**; the controller must now earn uplift on the *hard* cases.

**Scorer — two scoring fixes (`bespoke.py`):**

1. **`evidence_f1` no longer double-penalises hallucination.** Old `precision_denom =
   len(pred) + len(hallucinated)` double-counted: a fabricated id already lives in `pred` (it
   canonicalises to itself and never matches gold), so it was a false positive *and* an extra
   denominator term. Now standard F1 (`tp/len(pred)`); hallucinated ids are reported in
   `CaseScore.extra` rather than silently double-weighted.
2. **`conflict_handling` is now F1, not recall.** Old `|surfaced ∩ gold| / |gold|` had no
   precision term, so a solver could score 1.0 by dumping every id into `conflicts` (and
   `trigger_discrimination` keys off the same set). Now `_f1(surfaced, gold_conf)` penalises
   over-surfacing. **This diverged from the authoritative `spike_spec.md` §8.1 (which defined it
   as recall, "fraction surfaced") — caught in the audit and reconciled: §8.1 was updated to F1
   with user sign-off (2026-06-21), so spec and code agree.** Side effect: on empty-gold-conflict
   cases (4/6/8), surfacing a false conflict now scores 0.0 (was 1.0 under recall).

**Noted, not yet fixed (for the A4 findings, no re-run needed):** cost is reported as
`total_tokens` (includes each solver's system-prompt scaffold ×calls, inflating the
controller's premium); the meter's scaffold-netted `content_tokens` (B10) is logged but never
reaches the report — A4 should use content tokens and *verify* B10's "small & constant scaffold"
claim. The headline capability **mean** dilutes the real gap by averaging in
`abstention_calibration` (≈1.0 for every answering solver) — report per-metric.

## Workflow adopted

**Audit → fix → run a small *segment* → audit the real results in context → only then expand**,
looping until no bugs remain and the full set is done. This replaced the launch-full-run /
discover-bug / kill-restart thrash (hit twice: react all-zeros, then the scorer quirks). The
in-flight run can never adopt a code fix — `score()` runs on the module loaded at launch — so a
fix only lands via a fresh segment.

## Cost root cause & the n=1 deliverable (2026-06-21)

The eval ate ~40% of a session's subscription allotment. Root cause (measured via
`claude -p --output-format json`): **~22.6k tokens of scaffolding per call** — the auto-discovered
global `~/.claude/CLAUDE.md` + dynamic system sections — loaded on *every* `claude -p` invocation,
independent of prompt size. The model is correctly sonnet; overhead × ~300–400 calls is the burn.
`MeteredBackend` never sees this (it counts only our chars/4), so its docstring claim "little hidden
scaffolding remains" is **false** and the eval's reported cost is a ~15× undercount. Fixes shelved in
`docs/debt.md` (none free: `--exclude-dynamic-system-prompt-sections`, skip global CLAUDE.md,
`--bare`+API key, lower budget; plus capture real `usage`).

**Decisions (user, 2026-06-21):** (1) **No n=3** — budget won't bear it; ship the **n=1 all-8-case
set** (`reports/bespoke.md`) with explicit "variance not characterized" + cost-undercount caveats;
S1's ≥3-run criterion is a known unmet limitation, revisit after the overhead fix. (2) The controller
over-saturation/abstention weakness is **reported as-is, interpret-prompt fix shelved to Phase 2** —
patching it against these 8 cases would overfit a thesis-negative into a manufactured win (#5).

**The n=1 finding (indicative, not variance-backed):** controller accuracy **4/8 — the worst LLM
solver** (bare_llm 6, react 5, shortcut 2). It handles physical-fault salient≠cause cases (1,2,3,6)
but fails its *claimed-strength* axes: change-is-cause (4,8), abstain (5), tie-breaker (7). Its
capability edge is largely the deterministic conflict sweep, which react matches via reasoning. A
clean, defensible, **largely thesis-negative** result — a valid spike outcome per §0/§9.

## Why

A baseline that scores 0 because the harness can't read its answer — not because it is weak —
manufactures a false win for the controller, the exact failure non-negotiable #3 guards against.
Each defect lived where free-text meets the deterministic harness; verifying **structurally**
(the live prompt, the call graph, the scorer arithmetic) rather than nominally is what surfaced
them. All fixes either strengthen a baseline or correct a metric toward its stated definition —
never tuned to a win (#5).
