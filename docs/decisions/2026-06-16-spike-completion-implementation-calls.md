# Spike-completion implementation calls (2026-06-16)

Design calls made while executing the spike-completion audit response
(`handoffs/2026-06-16-spike-audit-response.md`). The audit response is the decision record on
*what* to do; this records the *how* and the *why* for the non-obvious implementation choices, so
a later session inherits the reasoning instead of relitigating it. The brief
(`docs/handoff/spike_spec.md`) still wins on any conflict.

## 1. Per-fault corpus delta replaces the `exclude_artifacts` stopgap (A1, C1)

`FaultFacts.corpus` is a list of `CorpusItem`s each fault declares; the shared structural corpus
(system model, playbook, prior-incident reports, generic logbook, swap-test) stays shared.
Conclusion-bearing items — the window-clean diagnostic *result*, the reboot event, the error log —
are per-fault facts, because their truth depends on the injected fault (cleaning a contaminated
window *would* improve intensity; a non-window fault's clean is a true no-op). The line (C1): a
variation that would change with the ground-truth fault is a *fact* (keep); one that exists only
to move difficulty/score is *tuning* (forbidden, #5). Whether a recent reboot happened in the
window is itself a per-case fact, so `reboot_event()` is in the per-fault delta — which is what
lets #6 be a genuine absent-cue case.

## 2. Deterministic conflict sweep — the real fix for shaky capability (A6 / B7)

**The problem (found by a live run, not the scripted gates):** the VOI loop optimizes for
*separating hypotheses*, so once the leader dominates by margin the controller concludes —
**before** running the onset and channel-sanity checks. On the flagship TEC case it returned the
right cause with an *empty* conflicts set (trigger-discrimination and conflict-handling both 0),
i.e. no visible capability advantage. Prompt nudges (A6) help but do not reliably overcome this,
because surfacing a demoted trigger / lying channel is *orthogonal* to picking the leader.

**The call:** before finalizing, the controller runs a deterministic sweep
(`loop._finalize_conflicts`) of the two discriminators the playbook always prescribes — order the
degradation onset against the *most salient recent event* (demote it iff the onset predates it,
D1), and sanity-check every channel for a stuck/lying sensor (B5). These are deterministic
conclusions of deterministic checks, so they are flagged mechanically (no LLM judgment). It is
**general by construction**: no recent event / no stuck channel ⇒ no-op; a recent change that IS
the cause (onset aligns, not predates — #4/#8) is correctly *not* demoted; the abstain case (#5)
correctly flags its coincident reboot. This is the controller's *structural thoroughness* — the
conflict-surfacing the bare baselines lack — not a tuning of cases or scoring (#5). It also makes
the capability metrics low-variance (deterministic where applicable), which is the honest way to
reduce the B2 wobble.

## 3. Strict accuracy + a separate localization metric (C6)

`accuracy` requires naming the *exact* cause (a part fault is not satisfied by its subsystem; a
subsystem/calibration/power fault accepts the subsystem or a `config` `part_of` it, and a
part-version counts as the same physical part). Getting only the right *subsystem* is scored apart
as `localization` (partial credit), reported in its own line — never folded into accuracy. This
stops a vague "thermal" answer from scoring a clean "tec" win and removes the B6 leniency worry.

## 4. `detector_health_check` must respect the lying channel (bug fix)

Adding the detector-bias discriminator for #6 created a false positive on #1: the TEC case's
secondary dark-count rise (+19%) plus the *stuck* `detector_temp` (flat because it is the lying
channel) read as "detector bias drift," spuriously supporting the detector decoy on the flagship
case. Fix: bias_drift requires a *substantial* dark rise (≥30%, so #6's +56% fires and #1's +19%
does not) **and** a *live* detector_temp channel — a frozen reading cannot establish "non-thermal."
General lesson: a check that reasons from a channel being flat must first confirm the channel is
not stuck.

## 5. Model pin: Sonnet (A8)

Pinned `claude-sonnet-4-6`. The audit asked to test Opus because B7's under-discrimination *might*
be model capability — but that concern was resolved *structurally* by the deterministic conflict
sweep (§2), which is model-independent. Sonnet solves the flagship case cleanly and is materially
cheaper, which strengthens the honest cost story (B3). A full like-to-like Opus sweep was deferred:
it was impractical to complete in-session under heavy shared-machine `claude -p` contention, and
the swappable CLI↔API backend means it can be run later without code change. **Like-to-like
invariant held:** all four solvers run on the pinned model for any one comparison.

## 6. Cost is a CLI-derived estimate, calibrated and symmetric (B10)

Tokens are chars/4 of the content each solver sends, metered identically for all four
(`MeteredBackend`). The headless CLI is invoked with tools stripped and its default system prompt
replaced, so little hidden scaffolding remains; the fixed system-prompt portion is tracked
separately (`scaffold_tokens` → `content_tokens` is the API-equivalent estimate) and cancels in
cross-solver comparisons. Every cost figure is labelled a CLI-derived estimate. The swappable
CLI↔API backend exists so exact counts (and a validation of the calibration) are available the
moment API access does.
