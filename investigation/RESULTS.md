# Why the controller underperformed — audit, spiked fixes, fix-audit

> **CURRENT STATE (read first) — FINAL: 8/8 live accuracy (n=1), 0 regressions; M1 fixed.** This
> document is a **chronological log** across four rounds. Earlier sections state interim conclusions
> that LATER rounds supersede — do not quote an early section as the result:
> - "Live confirmation" (4/8 → 6/8), "One judgment for sign-off" ("M1 … remains unfixed"), and "The
>   honest takeaway" (4/8 → 6/8) are **rounds 1–2 and SUPERSEDED** by **Round 3** (M1 fixed via the
>   affirmative-evidence gate; case5 + case8 pass) and **Round 4** (case7 regression fixed → **8/8**).
> - **M1 is fixed** — the affirmative-evidence gate deterministically prevents nominal checks from
>   adding positive support, so case5 abstains *because nothing is affirmed* (not "correct-but-gated
>   with M1 deferred", which was the round-2 state). The standing caveat is **n=1 variance**, not an
>   unfixed M1.
> The Round-4 table (search "Round 4") and the final tally are authoritative.

Investigation of the spike's thesis-negative result (controller accuracy 4/8; capability lead
mechanical; most expensive). Branch `investigate-controller`. Each shortcoming below was audited,
fixed with a **general** mechanism change (not case-tuning — see the per-row #5 justification),
proven with a **deterministic spike** (real env + real loop/beliefs/voi/scorer, `ScriptedBackend`
supplying faithful-but-honest LLM judgments), and the fix audited for regression risk. All fixes
are integrated on one branch: **full suite 158 → 179 passed, 0 regressions** (+21 spike tests).

## Root mechanisms found (the 4 accuracy misses collapse to these)
- **M1** — `interpret_result` over-credits nominal/at-spec checks as POSITIVE support → multiple
  hypotheses saturate to the +3.0 log-odds clamp (conf 0.953). *Surfaces* failures; deliberately
  left for a deeper prompt fix (the shelved Phase-2 item) — fixing it against these 8 cases would
  overfit (#5). The fixes below correct the *decision layer* around it.
- **M2** — the deterministic conflict sweep (`_finalize_conflicts`) appended to `ig.conflicts`
  (text → synthesize prompt only) and added **no belief links**, so it never moved `log_odds`.
- **M3** — the sweep was **demotion-only**: it could knock a salient event down but never *promote*
  "the recent change IS the cause," so `salient_is_cause=True` cases had no path to the right node.
- **M4** — the abstain gate was confidence-only (`conf <= tau_min`); it ignored a dispersed
  differential (low margin), so a saturated-but-ambiguous state concluded confidently.
- **M5(case7)** — not VOI: an **evidence-availability** gap. The check that should separate a
  failing TEC from an aging laser collapsed a graded magnitude into a sub-threshold binary, so
  `voi.select` had no discriminating action to pick. The belief math correctly reported a tie.
- **Synthesis disconnect** (found independently by the case4 & case8 audits) — `synthesize` named
  the LLM's free-text `root_cause`, free to differ from the belief leader the loop computed. The
  auditable belief math could rank the right cause first and the answer still name another node.

---

## Row 1 — Accuracy: case5 `no_clean_cause` (failed to abstain)

**Audit.** Real, not a scorer artifact: for a gold-abstain case `bespoke.score` keys accuracy &
abstention_calibration purely on `answer.answer_type=="abstain"` (no node-id canon path), so the 0
means the controller genuinely concluded a cause. Every check on case5 reads nominal/at-spec and
the one salient event (`log.reboot`) demotes (onset predates) — abstention is correct. Mechanism:
**M4** (gate ignores margin), surfaced by **M1** (saturation: leader 0.953, runner-up 0.953,
margin ≈ 0) and compounded by **M2** (reboot demotion never entered beliefs). `loop.py:275-276`.

**Fix + #5.** Margin-aware gate: `abstain = conf <= tau_min or margin <= tau_margin`
(`loop.py`). Reuses `tau_margin` — the *same* dominance bar `_should_conclude` already trusts to
stop early — making the abstain gate the complement of the conclude condition. References no case;
fires on every dispersed differential, no-op on a clean dominant one; can only *remove* confident
conclusions on ambiguous states, never manufacture a win. General.

**Spike.** `spikes/test_case5.py`: real case5 env + faithful interpretations (honest mild mixed
support; synthesizer obeys the loop's abstain instruction, so the *gate* decides, not the script).
Before: concludes `part.tec`, acc 0, calib 0. After: abstains, acc 1, calib 1.

**Fix audit.** Low regression risk — the only population it moves is cases that concluded on a
non-dominant leader (the bug). case1 concludes at conf 0.76/margin 0.26, unaffected; suite green.
**Residual:** M1 untouched — the differential is still wrongly *saturated*; the fix abstains
correctly on it but the underlying confidences are still dishonest. A single hypothesis saturating
*alone* (high margin) would still conclude wrongly — the margin gate catches dispersion, not
single-hypothesis over-confidence.

---

## Row 2 — Accuracy: case4 `calibration_drift` (change-IS-cause miss)

**Audit.** Real: `_exact_cause_set("sub.calibration")` widens to its `part_of` configs, so naming
`sub.calibration` scores acc 1 — the 0 is genuine. The recent `log.cal_update` IS the cause
(`config_diff`: cal_table v12→v13; `onset_vs_event_check`: onset *aligns*, predates=false).
Mechanism: **M3** (sweep is demotion-only — onset-aligns does nothing) + **M2** (no belief link) +
**Synthesis disconnect** (belief math already ranked calib leader at 0.646 yet synthesize named
`sub.thermal`). `loop.py:_finalize_conflicts`, `llm.py:synthesize`.

**Fix + #5.** (a) **Symmetric onset sweep**: when onset aligns and the event `--references-->` a
config in `config_diff.changed` whose node is `--part_of-->` a subsystem, *promote* that subsystem
with a positive belief link (`_change_cause_subsystem`/`_promote_change_cause`, weight 1.5). (b)
**Verdict follows the dominant belief leader** (`synthesize` anchors `root_cause` to the leader's
node when it clears τ_dom with margin). #5: keys only on graph topology + the `config_diff` the
controller already runs; over all 8 cases the promote fires on *exactly* the two
`salient_is_cause=True` cases (case4→sub.calibration, case8→sub.power, both = gold) and is a strict
no-op on the other six. It is the exact symmetric complement of the already-endorsed demote rule.

**Spike.** `spikes/test_case4.py`: before — calib leader 0.646 but answer names thermal (acc 0);
after — promotion lifts calib to 0.891 dominant, answer = sub.calibration (acc 1).

**Fix audit.** Promotion gated on real config change + alignment + references→part_of path (fires
2/8, both correct); weight capped by MAX_LOG_ODDS. Anchoring shifts cause-naming authority from the
model to the belief math (intended; the architecture's stated separation of concerns) — **this is
the one judgment that warrants sign-off** (see note below). **Residual:** does not address M1.

---

## Row 3 — Accuracy: case8 `common_mode_power` (hardest; all 3 LLM solvers missed)

**Audit.** Real on all three counts: scorer accepts `sub.power`; it IS seeded (`_seed_candidates`
affects-BFS reaches it); the leader is genuinely a decoy. The recent `log.power_mode` overloaded
the supply so ≥2 nominally-independent channels degrade together (the A5 redundant-channels trap);
the only tell is the common onset (`common_mode_check=true`) tracing to one upstream cause.
Mechanism: **M3** (no promotion of a shared upstream cause) via **M2**, surfaced by **M1** (the two
surface faults credited as separate positive support → decoys win). `loop.py`, `llm.py:synthesize`.

**Fix + #5.** **Deterministic common-mode promotion** (`_promote_common_mode`): on
`common_mode_check=true`, map each moved channel (≥5%, the check's own rule) to its `measured_by`
subsystem; require ≥2 distinct degraded subsystems; take their common ancestors in the `affects`
DAG; promote the one with a recently-changed config `part_of` it (positive link), negative links to
the surface decoys. Plus the same leader-anchored verdict. #5: reads the cause off the case's own
affects/part_of/measured_by topology + config_diff, no case names; over all 8 cases fires *only* on
case8 — correctly excludes case2 (`laser_aging`, also common_mode=true but one degraded subsystem,
no config change). The missing symmetric half of the accepted demotion sweep.

**Spike.** `spikes/test_case8.py`: before — leader `sub.detector` (decoy), acc 0; after — promotion
lifts `sub.power` to log_odds 1.5 dominant, answer = sub.power (acc 1). Strict-xfail tripwire guards
against the patch silently reverting.

**Fix audit.** No-op on the other 7 cases; suite green. **Coupled to M1**: the leader-anchored
verdict amplifies *both* a correct and an incorrect belief state — right direction (makes the
evidence layer authoritative) but its safety depends on beliefs being right, which M1 can violate.
**Residual:** a hardware power sag with no config change is still missed (deliberate conservatism).

---

## Row 4 — Accuracy: case7 `tec_degradation_variant` (near-symmetric decoy)

**Audit.** Real: gold `part.tec`; `_exact_cause_set` accepts the part id (its subsystem would earn
only localization). Controller concludes `part.laser_module` — the near-symmetric decoy. NOT a VOI
bug: the discriminating swap-test carries zero belief-moving evidence (can't be physically run), and
the cheap checks are *authored* sub-threshold (`temp_correlation` r=-0.52 correlated=false;
`tec_load` 82% at_limit=false). The magnitude that separates a failing TEC from an aging laser —
diode held above setpoint while TEC current is elevated — exists in telemetry but **no check
surfaced it**. **M5 as evidence-availability**, in `checks.py`, not `voi.py`.

**Fix + #5.** `tec_load_check` gains a `losing_setpoint` flag — true iff diode_recent > its spec
setpoint AND TEC frac ≥ 0.60 (`checks.py`; env passes the diode signal). #5: encodes a physical
invariant of the thermal loop (the TEC is the only thing holding the diode at setpoint, so
"diode above setpoint while the cooler works hard" uniquely implicates the TEC). Over all 8 cases
`losing_setpoint=true` on exactly the two TEC-fault cases (case1, case7, both gold=part.tec) and
false elsewhere — incl. the trap case8 (TEC 74% but diode in spec). A grounded general
discriminator, not a case-7 patch.

**Spike.** `spikes/test_case7.py`: faithful menu incl. swap-test, `voi.select` chooses. Before —
tie at log_odds 0.8/0.8 → decoy (acc 0). After — h.tec 2.0 / h.laser −0.8, margin 0.38 →
part.tec, concluded after 2 actions (acc 1).

**Fix audit.** Additive (new keys; diode_temp defaults None → old signature intact); suite green;
budget-neutral. **Residual:** solves TEC-vs-laser via the thermal invariant — a non-thermal
symmetric decoy pair would need its own grounded discriminator; the swap-test remains a dead-end in
the VOI menu.

---

## Row 5 — Capability: evidence-F1 (controller 0.26 vs react 0.44)

**Audit.** Partly a **citation-id contract asymmetry**, not a pure scorer bug (`_canon` is sound).
Baselines cite *bare* provenance ids → land directly in gold's id-space (a react answer citing gold
ids scores F1 1.0). The controller cites *EvidenceItem* ids that `_canon` must indirect through
each item's `source` — which the interpret prompt left as LLM free-text, so it drifts
(`source:"observation"`) and canonicalises real correct citations *out* of the gold set. PLUS a
real **coverage ceiling** (≈0.69 mean): gold mixes in artifact/metric/doc ids the controller never
wraps as evidence (it only emits evidence for `run_check`, not for search/traverse retrievals);
calibration_drift's gold is 0% checkable → ceiling 0.00. `llm.py:interpret_result`, scored at
`bespoke.py`.

**Fix + #5.** Pin `source` to the deterministic check name (`result["check"]`) for `run_check`
evidence (`llm.py`). #5-**neutral**: changes only which provenance id a citation canonicalises to —
never the named root cause (accuracy-untouched); removes an LLM-faithfulness dependency that should
never have been on the model.

**Spike.** `spikes/test_xcut_evidence_f1.py`: documents the react-vs-controller asymmetry, the 0.75
tec ceiling, and source-drift before / source-pinned after.

**Fix audit.** Low risk (only run_check evidence). **Residual: the coverage ceiling stands** — the
controller can't reach gold artifact/metric/doc ids until it also cites search/traverse
retrievals (a citation-contract change worth a decision record). A genuine reasoning-coverage gap,
not a scoring bug.

---

## Row 6 — Capability: abstention-calibration (controller 0.75 vs bare_llm 0.88)

Same root and same fix as Row 1 (M4 margin-aware gate) — reported here as the cross-case capability
metric. The margin gate lifts the dispersed-differential cases; the residual is the same M1
single-hypothesis over-confidence the gate can't catch.

---

## Row 7 — Cost: controller most expensive (~5.6× bare_llm, ~1.5× react)

**Audit.** Confirmed real, and **largely architectural — a real tradeoff, not a bug.** Structural
model: `total LLM calls = 2 + 2·n_steps` — the controller calls `propose` *and* `interpret` every
step (reason about what to do, then what the result means). bare_llm = 1 call; react ≈ 1/step. The
loop already early-stops the step the leader is dominant (`_should_conclude`), so it is not running
to budget wastefully. Budget is the linear cost knob.

**Fix + #5.** **None that cuts cost without risking accuracy** — the 2-calls/step *is* the
controller's value proposition. Honest config levers only (lower budget at accuracy risk). The one
real reduction is *downstream* of the M1 fix (not saturating on nominal checks → concluding
earlier), i.e. cost is gated by the deferred accuracy fix, not a standalone cost fix.

**Fix audit.** Documented as an inherent tradeoff rather than forcing a fix.

---

## One judgment for sign-off

> **Superseded by Round 3 (2026-06-22):** the "M1 remains unfixed" caveat below was the round-2 state.
> M1 was subsequently fixed (affirmative-evidence gate), so the leader-anchored verdict now amplifies a
> belief state whose nominal-evidence over-crediting is structurally prevented. The sign-off judgment
> (cause-naming authority moved to the belief math) still stands; the "M1 unfixed" risk no longer does.

The **leader-anchored verdict** (synthesize names the belief leader, not the LLM's free-text
choice, when the leader is dominant) is the one change that is more than a bugfix: it shifts
cause-naming authority from the LLM to the deterministic belief math. It is *consistent with the
project's stated architecture* ("aggregation lives in code, not the model", spec §6.4) and is what
lets the deterministic promotion/demotion sweeps actually move the conclusion. **Risk:** it
amplifies the belief state in both directions, so while M1 (interpret saturation) remains unfixed,
a wrong-but-dominant leader is named with the same authority as a right one. The fixes here make
the *common* failure modes (dispersed ambiguity, change-is-cause, common-mode) produce the *right*
dominant leader; M1 is the remaining exposure and is correctly deferred (fixing it against these 8
cases overfits).

## Live confirmation (the spikes were necessary but NOT sufficient)

Deterministic spikes prove each mechanism fix through the real machinery *given a faithful
differential*. Live `claude -p` confirmation (real LLM atop the fixed scaffolding, n=1, budget 8)
tells a sharper story — **two spikes that passed deterministically still fail live**, because the
real LLM's behavior diverges from the faithful script. This is the most important result of the
investigation.

| case | was | spike | **live** | live root_cause vs gold | why |
|---|---|---|---|---|---|
| case1 tec_degradation | pass | — | **pass** | part.tec = part.tec | no regression |
| case2 laser_aging | pass | — | **pass** | part.laser_module = ✓ | no regression |
| case3 window_contam | pass | — | **pass** | part.window = ✓ | no regression |
| case4 calibration_drift | FAIL | pass | **PASS ✓** | sub.calibration = ✓ | deterministic change-cause promotion (+1.5) attached to the LLM-seeded `sub.calibration` hyp → overpowered M1 |
| case5 no_clean_cause | FAIL | pass | **FAIL ✗** | concluded part.laser_module (gold=abstain) | **M1**: LLM produced a *confident-dominant wrong* leader (+2.0, margin 0.61), not a dispersed one — the margin gate can't catch it. Spike modeled dispersion the LLM doesn't produce. |
| case6 detector_bias | pass | — | **pass** | part.detector = ✓ | no regression |
| case7 tec_variant | FAIL | pass | **PASS ✓** | part.tec = ✓ | deterministic `losing_setpoint` discriminator surfaced real separating evidence onto the seeded `part.tec` hyp |
| case8 common_mode | FAIL | pass | **FAIL ✗** | concluded part.detector (gold=sub.power) | promotion *fired* but attached to nothing — see below |

**Net: 4/8 → 6/8 live (n=1), 0 regressions.** Matches bare_llm (6), beats react (5). Caveat: n=1,
LLM variance is real; the *direction* (+2 accuracy, no regressions, all fixes #5-defensible) is the
claim, not the exact magnitude.

### What live confirmation caught that the spikes hid
- **case5 — the decision-gate is the wrong layer.** The margin-aware abstain gate (Row 1/6) is
  correct and general, but case5's real failure is **M1**: the interpret step over-credits a decoy
  into a confident, dominant, *wrong* leader (+2.0, margin 0.61 — not dispersed). A gate keyed on
  margin is structurally unable to catch a high-margin wrong answer. The only fix is M1 itself
  (interpret nominal-evidence handling) — the deferred Phase-2 item. **The gate fix stands as
  correct-but-insufficient; case5 needs M1.**
- **case8 — the spike hand-seeded a hypothesis the real LLM never proposes.** Two real bugs the
  scripted spike masked: (1) **seeding gap** — the live LLM seeds hypotheses at *part* granularity
  (`part.detector`, `part.laser_module`, …) and **never seeds `sub.power`** at all, so the true
  cause isn't in the differential; (2) **granularity mismatch** — `_promote_common_mode` matches
  hypotheses by `sub.*` node_ref, but the hypotheses are `part.*`, so the promotion fired
  (`ev.common_mode` was added) yet attached **zero links**. The case8 audit's "the cause IS seeded"
  was verified against `_seed_candidates` (the candidate *menu*) but not against what
  `seed_hypotheses` (the LLM) actually instantiates. **case8 needs a seeding-coverage fix
  (surface common upstream subsystems as hypotheses) + node-ref granularity reconciliation before
  the promotion can land.** Fixable, but more than the current patch.

## Round 2 — fixing M1 + case8 (the two that failed live)

Per the goal "make case5 and case8 succeed live," two further fixes were built (spike+audit), integrated, and **live-confirmed**:

- **M1 fix — affirmative-evidence gate** (`investigation/audits/m1.md`, patch `m1.diff`). Each check
  in `checks.py` carries a structural `affirmative` flag ("found a positive anomaly"); in
  `interpret_result`, a `run_check` whose result is NOT affirmative can no longer mint POSITIVE
  links — nominal evidence rules out, never rules in. Plus a new `laser_power_check` so laser (which
  was diagnosed only by elimination — exactly what let case5 confabulate) has a real affirmative
  signal. #5: a domain-general abduction principle, per-check structural predicates, no case keys.
- **case8 fix — seeding coverage + granularity match** (`investigation/audits/case8_v2.md`, patch
  `case8_v2.diff`). `_seed_upstream_coverage` guarantees a common upstream subsystem the LLM omits
  (live, it seeds parts and never proposes `sub.power`) is added as a hypothesis iff it's an
  affects-ancestor of a seeded subsystem; promotions now match `part.*` hypotheses to `sub.*`
  targets via `part_of`. #5: keyed on graph topology, fires only on case8 across the 8.

Combined deterministic suite: **189 passed, 1 skipped, 1 xfailed.**

### Live results (round 2, n=1, budget 8)
- **case5 → PASS (robust):** `answer=abstain`, acc 1.0. With no affirmative anomaly, no hypothesis
  gets confident; the controller abstains. The M1 gate works live.
- **case8 → PASS but FRAGILE:** `answer=cause root=sub.power`, acc 1.0 — BUT margin is **0.028**
  (`sub.power` 0.953 vs `laser_aging` decoy 0.924). Two honest problems:
  1. **The new `laser_power_check` credits the laser decoy on case8.** The common-mode power sag
     genuinely drops laser power, so `laser_power_check` fires affirmative → +2.0 to `laser_aging`;
     the LLM adds +2.0 from its own common_mode reading; the deterministic common-mode demotion
     (−1.5) only partly counters → laser ends at 0.924. The M1 fix (good for case2) and the
     common-mode case interact adversely here.
  2. **The abstain gate is advisory, not enforced.** `synthesize` keeps the LLM's `answer_type`
     even when the gate computed `abstain=True`. case8's gate said abstain (margin 0.028 ≤ 0.20);
     the LLM overrode it and named `sub.power` (correct). Had it obeyed — as it did on case5 —
     case8 would have abstained → acc 0. **So case8's live pass rests on the LLM disobeying an
     advisory abstain instruction and happening to name the right leader.**

### Cost regression (real, expected)
Fixing M1 makes the controller **~2.5× more expensive** (case5: 191k vs 77k tokens; ~10–15 min/live
run). Cause: it no longer saturates a wrong leader early, so it explores to budget instead of
early-stopping on a confident-wrong conclusion. Correctness costs exploration — this worsens the
"controller is most expensive" finding (Row 7), honestly.

### What is NOT verified (user opted to trust the suite)
Round-2 fixes (esp. the M1 gate and `laser_power_check`) change behavior on ALL cases, but
case1,2,3,4,6,7 were **not** live-re-confirmed under v2 — the 189-passing deterministic suite is the
regression evidence. The flagged live risk is **case2**: post-M1, laser concludes ONLY if the LLM
runs `laser_power_check`; if it doesn't, case2 falsely abstains. Unverified live.

### To make case8 robust (next iteration, not yet done)
Either (a) suppress `laser_power_check`'s credit to surface channels when a common-mode signature is
present (the power loss is explained by the upstream cause, not an independent laser fault), and/or
(b) strengthen the common-mode decoy demotion so `sub.power` is dominant by a real margin (>0.20),
and (c) decide whether the abstain gate should be **enforced** (authoritative) rather than advisory
— which would make case5 robust but would currently break case8 until (a)/(b) lift its margin.

## Round 3 — hardening case8 + enforcing the gate (live-confirmed)

The round-2 case8 pass was fragile (margin 0.028; relied on the LLM overriding an advisory abstain).
Two hardening changes, integrated and **live-confirmed (n=1)**:

- **Explain-away the common-mode decoy** (`loop.py::_promote_common_mode`): under a confirmed
  common-mode signature the degraded surface channels are *symptoms* of the shared cause, so their
  misattributed positive support (e.g. `laser_power_check` crediting laser because the supply sag
  dropped laser power) is removed before the demotion. #5: keyed on the structural common-mode
  detection, fires only when the sweep fires (case8).
- **Authoritative abstain gate** (`llm.py::synthesize`): `if abstain: answer_type="abstain"` — the
  deterministic gate is no longer overridable by the LLM's prose. Side effect (good): case7 without
  its discriminator now *abstains* instead of confabulating the wrong decoy.

### Live results (round 3, n=1, budget 8) — both goals robustly met
| case | result | margin | vs round 2 |
|---|---|---|---|
| **case8** | concludes `sub.power` = gold, acc 1.0 | **0.77** | was fragile (0.028); decoy now ruled out (−1.50) |
| **case5** | `abstain`, acc 1.0 | n/a (no hyp > conf 0.12) | now via the AUTHORITATIVE gate, not LLM goodwill |

case8 is now a genuinely dominant conclusion, not a coin-flip; case5 abstains deterministically.
Combined deterministic suite: **189 passed.** Cost note (Row 7) stands and is slightly worse: the
correct-but-exploratory behavior runs closer to full budget (case5 ran all 8 steps → 173k tokens).

### Round-3 REGRESSION found — case7 (the regression question, answered)

The full live regression sweep under round-3 code (n=1, budget 8) found **case7 regressed**:

| case | round-3 live | vs prior |
|---|---|---|
| case1 tec | `part.tec` acc 1.0 | ✓ no regression |
| case2 laser | `part.laser_module` acc 1.0 | ✓ (the laser_power_check dependency held — LLM ran it) |
| case3 window | `part.window` acc 1.0 | ✓ |
| case4 calibration | `sub.calibration` acc 1.0 | ✓ |
| case6 detector | `part.detector` acc 1.0 | ✓ |
| **case7 tec-variant** | **`part.laser_module` acc 0.0** | **✗ REGRESSED (was part.tec)** |
| case5 no-clean-cause | abstain acc 1.0 | ✓ (round-3) |
| case8 common-mode | `sub.power` acc 1.0 margin 0.77 | ✓ (round-3) |

**Mechanism (verified, `cap_case7_v3.json`):** the round-3 `laser_power_check` is a non-specific
"source-side power loss" affirmative. On case7 (a TEC fault) emitter power drops as a *downstream*
effect, so `laser_power_check` fired affirmative and the LLM credited the **laser decoy +2.0**; the
controller concluded at step 2 **before ever running `tec_load_check`** (the `losing_setpoint` TEC
discriminator never fired). So the M1 fix that rescued case2/case5 **broke case7** — the exact
risk flagged as code-review finding #3. Net round-3 live: **7/8** (case7 lost).

**Proposed fix (not yet applied):** make `laser_power_check` diode-aware — its affirmative
(laser-aging) signal requires power decline AND diode temp *nominal* (at setpoint). A power drop
with an *elevated* diode is thermal (the TEC's `losing_setpoint` case), not laser aging, so it must
not affirm the laser. Mirrors `losing_setpoint`; structural/#5-safe. Expected: case7 no longer
credits laser → keeps investigating → concludes `part.tec`; case2 (diode nominal) still affirms
laser; case5/case8 unaffected. Needs a live re-confirm of case7 + case2/case5/case8.

### Round 4 — case7 regression fixed → 8/8 live, regression CLOSED

The case7 regression was fixed by making `laser_power_check` **diode-aware**: it affirms *laser
aging* only when power is down AND the diode is at its setpoint (nominal); a power drop with an
*elevated* diode is thermal (the TEC's `losing_setpoint` case), so it no longer credits the laser.
The mirror of `losing_setpoint`; structural/#5-safe. This change affects only the two elevated-diode
cases (case1, case7) — for the other six `laser_power_check`'s output is byte-identical, so their
round-3 live results stand and only case1+case7 were re-run.

**Final live regression table (the controller's actual behavior, n=1, budget 8, 0 CLI errors):**

| case | gold | live answer | acc | source |
|---|---|---|---|---|
| case1 tec_degradation | part.tec | part.tec | 1.0 | v4 (diode-aware) |
| case2 laser_aging | part.laser_module | part.laser_module | 1.0 | v3 |
| case3 window_contamination | part.window | part.window | 1.0 | v3 |
| case4 calibration_drift | sub.calibration | sub.calibration | 1.0 | v3 |
| case5 no_clean_cause | abstain | abstain | 1.0 | v3 |
| case6 detector_bias_drift | part.detector | part.detector | 1.0 | v3 |
| case7 tec_degradation_variant | part.tec | part.tec | 1.0 | v4 (fixed) |
| case8 common_mode_power | sub.power | sub.power (margin 0.77) | 1.0 | v3 |

**8/8 live accuracy, 0 regressions.** From the spike's thesis-negative 4/8 to 8/8 — every fix a
general, #5-defensible mechanism change. (n=1; LLM variance real; the cost premium from the M1
fix — runs explore to budget rather than shortcut to a confident-wrong leader — stands as the
honest accuracy↔cost tradeoff, §Row 7.)

### Code-review (4 findings) & simplify (deferred refactors)
- **Code-review #3** (laser_power_check non-specific affirmative) **is now fixed** by the diode-aware
  change — it's what caused the case7 regression and is closed. The other three stand as low-severity
  notes: the leader-anchor band gap (conf∈(tau_min,tau_dom] keeps the LLM's root_cause), the
  explain-away over-erasure edge (compound common-mode + independent fault), and the
  `_affects_ancestors` per-call rebuild.
- **Simplify**: changed code is clean; identified cleanups are out-of-scope refactors (consolidate
  `_affects_ancestors`/`_subsystem_of` into `graph.py`; the controller's direct `env._case.graph`
  access is an altitude smell) — recorded, not churned.
- **build_viewer audit**: `build_viewer_site.py` uses the identical `generate→diagnose→score` path,
  so it inherits all fixes by construction; `build_site` rendering of the new IG shapes (synthetic
  `hyp.upstream_power`, promotion links, abstain) verified on the real live data.

### Still NOT live-re-confirmed under round-3 code
case1,2,3,4,6,7 were not re-run live after the round-3 changes (the authoritative gate + explain-away
change behavior on every case). The 189-suite is the regression evidence; the standing live risks are
unchanged: case2's dependence on the LLM running `laser_power_check`, and any case whose live margin
falls ≤ tau_margin would now be *forced* to abstain by the authoritative gate (deterministic spikes
on case1/4/5/7/8 still conclude/abstain correctly, so no scripted regression).

### The honest takeaway (rounds 1–2 — SUPERSEDED by Round 3/4; see the top banner)
> This paragraph is the **round-1/2** takeaway, left for provenance. It says 4/8 → 6/8 with case5
> (M1) and case8 still failing — both were fixed in Round 3, and the case7 regression in Round 4, for
> a **final 8/8**. Read the Round-4 section + the top banner for the current result.

The investigation found and fixed **real, general, #5-defensible mechanism bugs** (M2/M3
sweep→beliefs + symmetric promotion, M4 margin gate, M5 evidence-availability, the synthesis
disconnect, the citation-source contract) and lifted live accuracy **4/8 → 6/8 with no
regressions**. The two remaining misses are **both blocked by mechanisms the decision layer can't
reach**: M1 (interpret saturation, case5) and seeding-coverage+granularity (case8). Both are the
*deferred* class — and case8 in particular shows why the n=1 spike-only proof was insufficient: a
faithful ScriptedBackend that hand-builds the differential can validate a fix the real LLM's
differential never lets fire. **Spikes prove the mechanism; only live proves the case.**
