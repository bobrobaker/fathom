# Handoff — Fathom spike: completion plan, concerns & audit requests

**Date:** 2026-06-16 · **Repo:** https://github.com/bobrobaker/fathom (private) ·
**Branch/commit:** `master` @ `4bb00f5` · **Tests:** 119 passing, linter clean.

**Status in one line:** the spike *vertical* is built and the *mechanism* works —
the controller solves the worked TEC case live and wins the capability family on
case #1 — but it is **not yet a shippable finding** (4/9 cases, n=1 run, no writeup,
an honest cost negative, benchmark unmeasured).

> ### How to use this file
> Three parts: **A** = work remaining, **B** = my top-10 concerns, **C** = excerpts I'd
> like a second opinion on. Under each item is a **▶ Reply:** slot — you (or another
> LLM) fill it with a decision/instruction, and I execute against it next session.
> "Success" = spec_spec.md §9 S1–S4; "confirmation" (the win) = T1–T4. Non-negotiables
> referenced are from `docs/handoff/00_README_for_coding_agent.md`.

---

## Part A — Work remaining to complete the spike

### A1. Per-fault corpus-delta refactor *(blocks A2 — do first)*
The corpus is currently shared across faults, but some artifacts encode fault-specific
*conclusions* (e.g. `act.window_clean` says "no improvement → not contamination" — true
for #1, but it would contradict #3 where the window IS the cause). I added a minimal
`exclude_artifacts` escape; authoring #4/#6/#7 cleanly needs diagnostic-action results +
prior-report conclusions to be fault-aware (a per-fault corpus delta on `FaultFacts`).
**▶ Reply:**

### A2. Author cases #4, #6, #7, #8 → reach ≥9 (S1)
Specs already in `src/dh/generator/cases.py`; generator is generalized. #4 calibration
(post-release config + chained evidence), #6 detector-bias (buried evidence via traversal),
#7 tec-variant (expensive tie-breaker / VOI), #8 common-mode power (one cause looks like
two faults). Each must be **capability-bound** (non-negotiable #4) and the set must hit
**anti-shortcut balance ≈0.5** (non-negotiable #4 / §5.2).
**▶ Reply:**

### A3. Run the ≥3-run variance eval across the full set (S1)
`tools/run_eval.py --all --runs 3` once the set exists. Currently only n=1 on case #1
(`reports/bespoke_case1.md`, gitignored). Variance over ≥3 runs is required by S1.
**▶ Reply:**

### A4. Write the results document *(the actual deliverable — does not exist)*
No findings/writeup file exists anywhere. Proposed `docs/findings.md`: thesis, rubric,
the per-case table (accuracy + capability families) with variance, the **cost caveat**,
the viewer, and a clean statement of the outcome (win or honest tie/loss, per S3).
**▶ Reply:**

### A5. Benchmark: validate or formally scope down
Harness + live mechanism are done (`src/dh/eval/benchmark.py`). Remaining: a
`tools/load_musique.py` (the `benchmark` extra), then n=20 fail-fast → n=100 — OR a
formal decision to scope the benchmark to report-only/drop per the M4.5 gate (T4 allows
this). See `docs/decisions/2026-06-16-benchmark-scoped-harness-first.md`.
**▶ Reply:** Decided (2026-06-16): **footnote**, do not validate-for-generalization. MuSiQue is a compositional chain with no rival-hypothesis adjudication, so a score tests retrieval/abstention/grounding, not the differential — report those (abstention + grounding, not EM alone). A differential-shaped domain (FEVER claim-verification) is the path to a real generalization claim, deferred to full-build (roadmap Phase 4). This **supersedes** the competitiveness framing in `spike-audit-response.md` A5. See `docs/decisions/2026-06-16-benchmark-tests-retrieval-not-differential.md`.

### A6. Live prompt iteration (capability quality)
The live model under-discriminates the decoy and doesn't always surface the demoted
trigger as a conflict. Iterate the `propose`/`interpret` prompts (the explicitly-iterated
artifact, §6.6), then **re-measure** — do NOT tune cases/scoring to compensate (#5).
**▶ Reply:**

### A7. Scoring id-space hygiene (fairness)
`interpret_result` returns evidence `source` as the action key (`run_check:tec_load_check`)
not the check name; the eval canonicalizes this and maps signal↔metric — verify it's
applied **symmetrically to all four solvers** so evidence-F1 / conflict-handling are fair.
**▶ Reply:**

### A8. Finalize the model pin
`config.yaml` pins `claude-sonnet-4-6` (provisional, flagged for M3). Confirm or change
before the writeup numbers are generated.
**▶ Reply:**

### A9. Smaller deferred items (low priority)
BM25 → hybrid (sentence-transformers) for corpus-volume cases; `query_telemetry(condition=)`
wiring for the D3/D4 cases; confirm the snapshot deepcopy fix holds at scale.
**▶ Reply:**

---

## Part B — Top 10 concerns

### B1. The headline rests on a single case (4/9 authored)
S1 is unmet. The capability uplift is demonstrated on case #1 only; it may not generalize.
**▶ Reply:**

### B2. n=1 — no variance, and the live runs already wobbled
Two live runs of case #1 disagreed on *which* conflicts got surfaced (channel vs trigger).
Will the capability-family win survive the ≥3-run average, or is it within noise?
**▶ Reply:**

### B3. The controller costs ~6× bare_llm's tokens (8619 vs 1443)
Confirmation criterion **T3 ("evidence-F1 ≥ bare_llm at ≤ its cost") is currently NOT met.**
Efficiency was one of the four stated axes. Is the capability uplift worth the cost in the
portfolio story, or does the loop need to get cheaper (fewer steps / smaller prompts)?
**▶ Reply:** Report it as an honest capability-vs-cost tradeoff (resolved in `spike-audit-response.md` B3): ~6× is normal for a bounded agentic loop; keep the number, do a modest reduction pass, frame as "structure buys capability `bare_llm` lacks at a quantified token premium." T3 is a confirmation criterion, not a success gate — a clean miss, reported, is fine. The VOI ablation (`docs/decisions/2026-06-16-voi-ablation-before-formalizing.md`) may cut steps if scored selection turns out not to earn its calls.

### B4. Is `bare_llm` genuinely "best honest"? (non-negotiable #3)
A weak `bare_llm` invalidates the whole result. It currently gets telemetry *summaries*
(baseline→recent + spec) and searched artifacts — **not** raw series or check outputs.
Is that the strongest fair version, or is it accidentally strawmanned (too thin) / too
strong (handed the discriminators)?
**▶ Reply:**

### B5. Are the cases truly capability-bound? (non-negotiable #4)
`bare_llm` got case #1 *accuracy* right from a context dump. The controller's win is on
the **capability family** (trigger/conflict), not accuracy. Each case must be unsolvable
by a single dump on *its scored axis* — otherwise it doesn't belong. Needs a per-case check.
**▶ Reply:**

### B6. Do the scoring relaxations quietly favor the controller? (non-negotiable #5)
Accuracy credits the part *or* its subsystem (`part_of`/`version_of` family); conflict/
evidence ids are canonicalized (signal↔metric, evidence→source). These are meant to be
fair to all solvers — but they need an adversarial read to confirm they don't tilt.
**▶ Reply:**

### B7. Live capability quality is shaky
Decoy (laser) stayed at conf ~0.99 next to TEC; the reboot wasn't always demoted into
`conflicts`. The capability number could shrink materially once averaged over cases/runs.
**▶ Reply:** Addressed structurally since the audit: the cumulative log-odds clamp (`beliefs.MAX_LOG_ODDS`) lets contradicting evidence pull a saturated decoy back down, and the deterministic conflict sweep (`loop._finalize_conflicts`) guarantees the demoted trigger / stuck channel surface in `conflicts`; A6 prompt iteration pushes discriminating actions. Re-measure over the ≥3-run A3 and report the averaged number even if it shrinks. The VOI ablation (`docs/decisions/2026-06-16-voi-ablation-before-formalizing.md`) tests whether scored selection actually improves discrimination here.

### B8. Anti-shortcut balance is currently skewed
All 4 authored cases have the reboot as a *coincidence/trigger*; **none** have the salient
recent event as the true cause. So `shortcut` is too easy to beat right now. Need ≥1 case
where a recent change IS the cause (else the ≈0.5 balance is violated, #4 / §5.2).
**▶ Reply:**

### B9. The benchmark claim is unvalidated (audit concern #2)
Is the diagnosis-shaped core even competitive at real multi-hop QA? Unknown. The synthetic
smoke is too easy to signal. This may need to be dropped or framed as report-only.
**▶ Reply:** Reframed: the right question is not "is it competitive" but "can MuSiQue validate the *differential*" — structurally it cannot. The benchmark solver `agentic_rag` shares only LLM plumbing with the controller, not hypotheses/VOI/beliefs/IG (verified in `handoffs/2026-06-16-lesson-unverified-load-bearing-claims.md`). So the benchmark tests retrieval/abstention/grounding, not the harness. Footnote it; FEVER for generalization. See `docs/decisions/2026-06-16-benchmark-tests-retrieval-not-differential.md`.

### B10. Reproducibility depends on the subscription CLI backend
The live numbers come from `claude -p` (nondeterministic, no usage API → token cost is a
chars/4 *estimate*). For a writeup promising "reproducible numbers," is CLI variance + an
estimated cost axis acceptable, or do we need the API-keyed path for the final run?
**▶ Reply:**

---

## Part C — Excerpts I'd like a second opinion to audit

### C1. The corpus-delta scope (`docs/debt.md`)
> "make diagnostic-action results + prior-report conclusions fault-aware (a per-fault corpus
> delta on FaultFacts), so each case stays internally consistent."

Question: how much per-fault corpus variation is *right* before it becomes per-case
hand-authoring (defeating the "generator" framing)? Where's the line?
**▶ Reply:**

### C2. `bare_llm`'s evidence digest (`src/dh/baselines.py:_telemetry_digest` / `_artifact_digest`)
It feeds per-signal `baseline≈X → recent≈Y` + spec, and artifacts gathered by 5 fixed
search queries. Is this the *best honest* long-context baseline, or should it get the full
series / a better retrieval / the raw config?
**▶ Reply:**

### C3. Belief weight clamp (`src/dh/controller/llm.py:MAX_WEIGHT = 2.0`)
Caps each evidence link's |LLR| at 2.0 to stop one piece of evidence saturating a
hypothesis. The value is hand-picked. Is clamping the right mechanism, and is 2.0 principled
or arbitrary? (It directly shapes the margins the §6.2 stop condition reads.)
**▶ Reply:**

### C4. Abstain logic (`src/dh/controller/loop.py` + `config.yaml` thresholds)
Abstain iff leader confidence ≤ `tau_min` (0.55). The "mutually-contradictory evidence"
abstain path (§6.2) is **not** implemented — only the low-confidence path. Is the simpler
rule enough for the E1 case, or does the contradiction trigger need building?
**▶ Reply:**

### C5. Evidence-F1 canonicalization (`src/dh/eval/bespoke.py:_canon`)
Normalizes evidence ids → source, strips action prefixes, maps signal→metric node. This
makes the controller's `EvidenceItem` ids comparable to a baseline's raw citations. Is the
mapping symmetric and fair, or does it advantage the structured solver?
**▶ Reply:**

### C6. Accuracy granularity (`src/dh/eval/bespoke.py:_cause_equivalents`)
Accuracy credits naming the root-cause part **or** its `part_of`/`version_of` neighbor
(so `sub.thermal` counts for `part.tec`). Fair robustness, or too lenient (lets a vague
"thermal" answer score as correct)?
**▶ Reply:**

---

## Pointers
- Milestone tracker + exit criteria: `docs/road.md`
- Design calls + why: `docs/decisions/` (LLM backend; benchmark scoping)
- Full deferred shelf: `docs/debt.md`
- The finding (n=1): `reports/bespoke_case1.md` · viewer: `viewer_out/index.html`
- Run the eval: `.venv/bin/pytest` (gates) · `tools/run_eval.py --runs 3 --budget 8` (live)
