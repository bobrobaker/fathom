<!-- Authoritative spec for WHAT was built: docs/handoff/spike_spec.md. This is the spike's
findings writeup (audit item A4) — it reports the eval design first, then the measured result.
Numbers come from a single run per case (n=1, `tools/run_eval.py --all`), shipped under a budget
constraint (2026-06-21); the ≥3-run variance pass (A3) is deferred. The results tables are
regenerated from `reports/bespoke.md`, never hand-edited to flatter the controller. -->

# Fathom — spike findings

**What this is.** Fathom is a diagnostic harness: one abductive LLM **controller** maintains a
hypothesis differential and proposes the single most-discriminating next action, run against a
generated lidar system-under-test through one `Environment` interface. This document reports the
spike's measured result against three baselines, leading with the **eval design** — because the
design is the claim, and the number is only as good as the eval that produced it.

**The honest headline (read with §6).** The spike's deliverable is a *clean, defensible finding*,
not a guaranteed win — and the measured finding is **thesis-negative**. On raw accuracy the
controller places **last among the LLM solvers** (4/8 vs bare_llm 6, react 5), missing precisely
the cases the design frames as its strengths — change-is-cause (#4, #8), abstention (#5), the VOI
tie-breaker (#7). It leads the *capability-family mean*, but that lead is an artifact of two
near-saturated components — the **deterministic conflict sweep** and trigger-discrimination, both
1.00 on every case; on the two capability components that actually exercise reasoning (evidence-F1,
calibrated abstention) it sits **at or below** the field. And it pays the **highest token premium**
(~5.6× bare_llm). A null-or-negative result, reported cleanly with its mechanism (§6), is a valid
spike outcome — and it is the outcome here. **n=1: variance is uncharacterized (§3); the direction
is reportable, the magnitude is not variance-backed.**

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

- **Determinism & variance (n=1 caveat).** The generator is seeded; the model is pinned;
  temperature is low. Residual LLM nondeterminism is **real but uncharacterized here**: the results
  below are a **single run per case** (n=1), shipped under a budget constraint; the spec's ≥3-run
  variance pass (A3) is deferred. Evidence the variance matters: case #1 flipped accuracy 0→1 across
  runs in an earlier attempt. So per-case verdicts are **indicative, not variance-backed** — a
  1-run miss is not a confirmed loss. The reported *direction* (controller behind on accuracy, a
  cost premium) is consistent across the cases; individual magnitudes are not.
- **Model pin.** `claude-sonnet-4-6`, held fixed across all four solvers for every comparison
  (the like-to-like invariant — never mix models within one comparison, or the model confounds
  the structure). Rationale in §5.
- **Cost axis (real CLI `usage`, B10).** Tokens are metered identically for all four solvers
  (`MeteredBackend`), from the CLI's real per-call `usage` (`--output-format json`): uncached
  input, cache-creation (5m/1h), cache-read, and output. The headless backend strips its
  scaffolding to near-zero — `--tools ""` removes the ~14-17k of built-in tool definitions and
  `--setting-sources project,local` drops the global `CLAUDE.md`, taking the per-call prefix from
  ~21k to ~150 tokens (~280x cheaper per-call input than a default `claude -p`, all on
  subscription; see `docs/decisions/2026-06-22-claude-cli-prompt-cache.md`). So per-call cost is
  the solver's *actual* content (input + output), not a fixed overhead, and is output-dominated —
  the same meter wraps all four solvers, so any residual cancels in the comparison. The reported
  figure is price-weighted (`cost_tokens`: output 5.0x, cache_read 0.1x, creation 1.25x/2.0x;
  sonnet-4-6 ratios); the raw breakdown is retained so the price model can be revised. A swappable
  CLI↔API backend exists so exact billed counts are available the moment API access does.
- **Run it.** `.venv/bin/python tools/run_eval.py --all` → `reports/bespoke.md` (this writeup is
  n=1; add `--runs 3` for the deferred variance pass).

---

## 4. Results

> **n=1, single run per case** (budget constraint, 2026-06-21), from `reports/bespoke.md`. The
> ≥3-run variance pass is deferred; read every cell as indicative, not variance-backed (§3). Tables
> are regenerated from the report renderer, never hand-edited.

### 4.1 Capability family — decomposed, because the mean lies

The capability family is reported **per metric, not as a single mean** — the mean is dominated by
two components that are near-saturated for the controller and so flatter it. Per-metric mean across
the 8 cases (full per-case × per-metric tables in `reports/bespoke.md`):

| capability metric | controller | bare_llm | react | shortcut |
|---|---|---|---|---|
| conflict_handling | **1.00** | 0.33 | 0.71 | 0.38 |
| trigger_discrimination | **1.00** | 0.50 | 0.88 | 0.38 |
| evidence_f1 | 0.26 | 0.23 | **0.44** | 0.13 |
| abstention_calibration | 0.75 | **0.88** | 0.75 | 0.88 |
| *(naïve family mean)* | *0.75* | *0.48* | *0.69* | *0.44* |

The controller's two perfect rows are **not abductive reasoning** — `conflict_handling` and
(largely) `trigger_discrimination` come from the **deterministic conflict sweep** (§5), a mechanical
evidence layer that fires identically regardless of the LLM. On the two components that *do* exercise
reasoning and are not saturated — `evidence_f1` and `abstention_calibration` — the controller sits
**at or below** the field: behind react on evidence-F1 (0.26 vs 0.44) and behind bare_llm on
abstention (0.75 vs 0.88), the latter a metric the design names as a controller strength. The naïve
family mean (0.75, nominally ahead of react's 0.69) is therefore a **manufactured headline**;
reporting it as the win would violate non-negotiable #5. Honest read: the *structure's deterministic
layer* wins conflict/trigger handily; the *controller's reasoning* does not lead.

### 4.2 Accuracy & localization

| | controller | bare_llm | react | shortcut |
|---|---|---|---|---|
| **accuracy /8** | **4** | 6 | 5 | 2 |

The controller is **last among the three LLM solvers**. Worse, its four misses are the cases the
difficulty catalog frames as its raison d'être: calibration-drift (#4) and common-mode power (#8),
both *change-is-cause*; *no-clean-cause* (#5), the abstention case; and the *VOI tie-breaker* (#7).
bare_llm — a strong long-context dump — solves 6/8, including the tie-breaker. **Localization tracks
accuracy exactly on all 8 cases** (the controller never names the right subsystem while missing the
part), so the partial-credit axis offers no softening here.

### 4.3 Empirical capability-binding (B5) — holds on the capability axes, weak on accuracy

bare_llm's per-metric scores (§4.1) confirm the cases are **bound on the capability axes**: a maximal
context dump scores 0.33 conflict / 0.50 trigger / 0.23 evidence-F1 — it cannot reconstruct the
demoted-trigger / stuck-channel / cited-chain structure by reading the corpus once. But binding on
**raw accuracy is weak**: bare_llm gets 6/8 root causes right from the dump, so most cases are *not*
accuracy-bound against a strong long-context baseline. The honest claim is the narrow one — the cases
bind the **capability** axes, not the accuracy axis.

### 4.4 Cost

Marginal content tokens per solver (the ~21k-token `claude -p` prefix is identical across all four
solvers and cancels in the comparison — §3; these are the n=1 content counts, not the fixed
real-`usage` metering, which applies to future runs):

| | controller | bare_llm | react | shortcut |
|---|---|---|---|---|
| total content tokens (8 cases) | ~99.1k | ~17.7k | ~66.5k | 0 |
| per-case mean | ~12.4k | ~2.2k | ~8.3k | 0 |

The controller is the **most expensive** solver — ~5.6× bare_llm and ~1.5× react in marginal tokens
— while scoring **lowest on accuracy**. It pays the largest premium for the structure and, on this
n=1 slice, does not return accuracy for it.

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

The spike's measured finding is **thesis-negative, and that is the finding**. Stated cleanly:

1. **Accuracy: the controller loses.** 4/8 — last among the LLM solvers (bare_llm 6, react 5), and
   it misses on exactly the cases the design claims it should own: change-is-cause (#4, #8),
   abstention (#5), the VOI tie-breaker (#7).
2. **Capability: the lead is mechanical, not abductive.** The controller's capability-family edge is
   carried by the **deterministic conflict sweep** (conflict_handling and trigger_discrimination =
   1.00 on every case — a model-independent evidence layer, not the controller's reasoning). On the
   capability components that actually exercise reasoning it does **not** lead: evidence-F1 0.26
   (behind react), abstention 0.75 (behind bare_llm). react reproduces much of the conflict/trigger
   handling by plain reasoning.
3. **Cost: the controller pays the most** (~5.6× bare_llm, ~1.5× react in marginal tokens) — the
   worst quadrant: highest cost, lowest accuracy.

**Mechanism (the why behind 4/8).** The interpret step over-credits nominal / at-spec checks as
positive support, so the leading hypothesis saturates to the +3.0 log-odds clamp (conf 0.953); with
`tau_min=0.55` the abstention gate can no longer trip, and the controller becomes *confidently wrong*
on the change-is-cause and abstain cases. This is the same saturation that drove the earlier case-#1
regression; the existing "nominal argues against" prompt guidance is insufficient.

**Why it is not patched here.** Fixing the interpret prompt against these 8 cases would overfit a
negative into a manufactured win — a direct violation of non-negotiable #5. The fix is **shelved to
Phase 2** (decision, 2026-06-21), to be validated on held-out cases, not the ones that exposed it.

**What the structure genuinely buys.** A deterministic, model-independent conflict/trigger layer that
surfaces demoted triggers and stuck channels perfectly (1.00 everywhere) where bare_llm largely
cannot (0.33 / 0.50). That is real and defensible — but it is an *evidence-layer* win, and on this
slice it does not translate into the accuracy or calibrated-abstention advantage the thesis predicted.

**Confidence.** n=1; variance uncharacterized (§3). case #1 flipped accuracy 0→1 across runs, so
individual verdicts are indicative. The *direction* — controller behind on accuracy, ahead only on
the deterministic layer, most expensive — is consistent across the 8 cases and is what this writeup
reports; the magnitudes await the deferred ≥3-run pass.

## 7. The viewer

The Investigation Graph is the single source of truth — the controller writes it, the eval reads
it, the viewer renders it. `viewer_out/index.html` replays case #1 across its steps: hypotheses
recolor by confidence, the demoted reboot renders distinctly from the differential, and the stuck
channel is flagged. The polished, hostable multi-case showpiece is `fathom_visualizer_spec.md`.
