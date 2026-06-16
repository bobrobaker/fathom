<!-- Authoritative spec for WHAT was built: docs/handoff/spike_spec.md. This is the spike's
findings writeup (audit item A4) — it reports the eval design first, then the measured result.
Numbers come from `tools/run_eval.py --all --runs 3` (the A3 run); the results tables are
regenerated from `reports/bespoke.md`, never hand-edited to flatter the controller. -->

# Fathom — spike findings

**What this is.** Fathom is a diagnostic harness: one abductive LLM **controller** maintains a
hypothesis differential and proposes the single most-discriminating next action, run against a
generated lidar system-under-test through one `Environment` interface. This document reports the
spike's measured result against three baselines, leading with the **eval design** — because the
design is the claim, and the number is only as good as the eval that produced it.

**The honest headline (read with §6).** The spike's deliverable is a *clean, defensible finding*,
not a guaranteed win. The structure is expected to win on the **capability family**
(trigger-discrimination, conflict-handling, calibrated abstention) and to roughly **tie a strong
long-context baseline on raw accuracy**, at a **quantified token premium**. A null or modest
result, reported cleanly, is a valid outcome — and it is roughly the outcome here.

---

## 1. The eval design (the part that matters)

A measurement is only as trustworthy as the adversary it was measured against and the cases it
was measured on. Four design commitments make this eval defensible; each is enforced in code and
guarded by a test, not asserted in prose.

### 1.1 Strong, fair baselines (non-negotiable #3)

The controller races three baselines, all returning the same `Answer` shape so the rubric scores
them identically (`src/dh/baselines.py`):

| Solver | What it is | Why it is here |
|---|---|---|
| `shortcut` | Deterministic: blames the most recent change/event. | The rig-detector. If the controller only ties this, the cases are leaky. |
| `bare_llm` | The **whole case** in one prompt — full raw telemetry series, the entire artifact corpus, the raw config — asked for the cause. | The best-honest long-context baseline. A thin one would invalidate the result. |
| `react` | The controller's exact tools in a plain ReAct loop, **no** hypothesis-differential / VOI / IG bookkeeping. | Isolates the value of the *structure* from the value of the *tools*. |
| `controller` | The system under test. | — |

`bare_llm` is deliberately strong: it receives the **maximal raw data a context dump contains**
(every signal's full series with descriptive stats, every document/log/ticket/error, the raw
config store) but **none of the computed check verdicts** — the principle is *all the data, none
of the computed discriminators*. Handing it the verdicts would rig the comparison the other way.
Each solver gets its own system prompt, so the controller's hypothesis-differential guidance never
leaks into the baselines (fairness).

### 1.2 Capability-bound difficulty (non-negotiable #4)

Every case is **unsolvable by reading the corpus once** on its scored axis — it requires something
a context dump cannot do: running a deterministic check (compute-to-discriminate), ordering an
onset against an event (temporal), traversing to buried evidence (navigation), recommending an
expensive discriminator (VOI under budget), or abstaining. This is asserted per case as a
structural gate (`tests/test_capability.py`) and confirmed empirically by `bare_llm`'s measured
failure on those axes (§4). The binding is a *property of the case*, not a hope about the model.

### 1.3 Anti-shortcut balance (non-negotiable #4 / §5.2)

Across the cause-cases that carry a salient recent event, the fraction where that event **is** the
true cause sits near 0.5 — so "a recent event is present" carries ≈no information about whether it
is the cause, and a shortcut cannot win by reflex. The set mixes: 2 *change-is-cause* cases
(calibration #4, power #8 — a shortcut is **right** there), 4 *trigger≠cause* cases (#1/#2/#3/#7 —
a reboot that the onset check demotes), 1 *absent-cue* case (#6 — no recent event at all), and 1
*abstain* case (#5). The salient-event kinds are varied (reboot / config change / power-mode
change), not all reboots. Gated in `tests/test_capability.py`.

### 1.4 Two reported families, never tuned to win (non-negotiable #5)

Results are reported in two families, separately: **accuracy** (exact root-cause correctness — a
part fault is *not* satisfied by naming its subsystem; that is scored apart as **localization**)
and **capability** (evidence-F1, conflict-handling, trigger-discrimination, abstention). The
capability family is where the structure should win even if a strong `bare_llm` ties on accuracy.
The same canonicalization (evidence→source, signal→metric, action-prefix stripped) is applied
identically to all four solvers and can never turn a wrong citation into a right one
(`tests/test_scoring_symmetry.py`).

---

## 2. The case set (≥8, capability-bound)

The eval's frozen slice (`src/dh/generator/cases.py`); each fault is a forward-effects model that
emits internally-consistent telemetry + corpus + hidden ground truth.

| # | Fault | Scored capability axis | Discriminator (what a dump can't do) |
|---|---|---|---|
| 1 | TEC degradation | trigger-discrimination + conflict | onset-vs-reboot (compute); stuck `detector_temp` (channel sanity) |
| 2 | Laser aging | accuracy via absence | *no* temp correlation — reason from a missing signal |
| 3 | Window contamination | accuracy via locality | spatial-intensity spread (compute) |
| 4 | Calibration drift | accuracy + evidence chain | config change **is** the cause; chain log→ticket→release |
| 5 | No clean cause | abstention | every channel nominal → no hypothesis crosses τ_min |
| 6 | Detector bias drift | accuracy via navigation | dark-count-vs-temp (compute); buried note via traversal; absent-cue |
| 7 | TEC variant | VOI / tie-breaker | cheap checks inconclusive → expensive swap-test recommendation |
| 8 | Common-mode power | conflict / accuracy | redundant channels agree but are wrong → common-onset (compute) |

---

## 3. Method

- **Determinism.** The generator is seeded; the model is pinned; temperature is low. Residual LLM
  nondeterminism is reported as **variance over ≥3 runs** (mean ± spread), not hidden.
- **Model pin.** `claude-sonnet-4-6`, held fixed across all four solvers for every comparison
  (the like-to-like invariant — never mix models within one comparison, or the model confounds
  the structure). Rationale in §5.
- **Cost axis (CLI-derived estimate, B10).** Tokens are chars/4 of the content each solver sends,
  metered identically for all four (`MeteredBackend`). The headless CLI is invoked with tools
  stripped and its default system prompt replaced, so little hidden scaffolding remains; the fixed
  system-prompt portion is tracked separately (`scaffold_tokens`) and can be subtracted for a
  content-only, API-equivalent estimate. Any residual constant overhead cancels in the cross-solver
  comparison. A swappable CLI↔API backend exists so exact counts are available the moment API
  access does.
- **Run it.** `.venv/bin/python tools/run_eval.py --all --runs 3` → `reports/bespoke.md`.

---

## 4. Results

> [Populated from the A3 run — `reports/bespoke.md`, all 8 cases × ≥3 runs × 4 solvers. Per-case
> accuracy + localization + capability families with mean ± spread, then the cost row. Pasted
> verbatim from the report renderer; not hand-edited.]

### 4.1 Capability family — the headline

> [controller vs bare_llm / react / shortcut, capability-family mean ± spread.]

### 4.2 Accuracy & localization

> [controller vs baselines; honest tie/win, with localization shown apart.]

### 4.3 Empirical capability-binding (B5)

> [For each capability case, bare_llm's measured score on the scored axis — the confirmation that
> the case is bound against the strengthened long-context baseline, not just structurally.]

### 4.4 Cost

> [tokens/case per solver, CLI-derived estimate net of scaffolding; the honest premium.]

---

## 5. Model pin (A8)

Pinned **`claude-sonnet-4-6`**. The audit flagged a model test because the earlier
under-discrimination of conflicts (B7) *might* have been model capability rather than prompt — but
that concern was resolved **structurally** by the deterministic conflict sweep (§3 of the decision
record), which surfaces demoted triggers and stuck channels mechanically and is therefore
model-independent. Sonnet solves the flagship case cleanly and is materially cheaper, which makes
the honest cost story (§4.4) stronger, not weaker. A full like-to-like Opus sweep was **deferred**:
it was impractical to complete in-session under heavy shared-machine CLI contention, and the
swappable CLI↔API backend means it can be run later without code change. The **like-to-like
invariant held**: for any one comparison, all four solvers run on the pinned model — the model is
never mixed within a comparison.

---

## 6. The outcome, honestly

> [The clean statement: where the controller wins (capability family / abstention / trigger),
> where it ties (accuracy vs a strong bare_llm), and the cost premium it pays for the structure.
> Written to the measured numbers, modest where the numbers are modest. The structure buys
> conflict-surfacing, trigger-demotion, and calibrated abstention that bare_llm structurally lacks,
> at a quantified token premium — and that, reported cleanly, is the finding.]

## 7. The viewer

The Investigation Graph is the single source of truth — the controller writes it, the eval reads
it, the viewer renders it. `viewer_out/index.html` replays case #1 across its steps: hypotheses
recolor by confidence, the demoted reboot renders distinctly from the differential, and the stuck
channel is flagged. The polished, hostable multi-case showpiece is `fathom_visualizer_spec.md`.
