# case8 `common_mode_power` (gold = `sub.power`) — v2 audit (live-failure fix)

The prior spike PASSED while live FAILED because it hand-seeded a `sub.power` hypothesis the real
LLM never proposes. This v2 reproduces the LIVE failure deterministically and fixes the two bugs
that hand-seeding masked.

Patch: `investigation/patches/case8_v2.diff` (src reverted after saving).
Spike: `investigation/spikes/test_case8_live.py` (5 tests, all green; +158 suite = 163 passed).

---

## Audit — the two live bugs (verified against `cap_case8.json`, n=1 live IG)

Both confirmed real (not scorer artifacts). `_exact_cause_set("sub.power", case)` = `{sub.power,
config.scan_params}` (a *subsystem* cause: the node itself plus configs `part_of` it), so naming
`sub.power` scores accuracy 1.0 — the live `0` is a genuine wrong answer (`part.detector`).

**Bug 1 — seeding gap (`llm.seed_hypotheses` / `loop.diagnose`).** The live LLM seeded 5
hypotheses at PART granularity — `part.detector, part.laser_module, part.tec, part.window,
sub.calibration` — and **never seeded `sub.power`**. `_seed_candidates` *does* return `sub.power`
in the menu (its affects-BFS reaches it), but `seed_hypotheses` lets the LLM pick and it dropped the
common upstream subsystem. So the true cause was not in the differential at all; nothing for any
promotion to credit.

**Bug 2 — granularity mismatch (`loop._promote_common_mode`).** The promotion sweep DID fire
(`ev.common_mode` was added to evidence) but attached **zero belief links**. It matched hypotheses
by `node_ref == subsystem_id`: `target_subs = {sub.power}`, `deg_subs = {sub.detector, sub.laser,
sub.thermal}` — while every live hypothesis is `part.*`. `part.detector ≠ sub.detector`, so neither
the positive target link nor the negative decoy links attached. The promotion was a no-op, and the
M1-saturated decoy `part.detector` (live `+2.5`, conf 0.924) won. (`_promote_change_cause` had the
same `node_ref ==` match; case4 only worked because the live LLM happened to seed `sub.calibration`
at subsystem granularity — it was one part-granularity seed away from the same silent no-op.)

These are M2/M3 (sweep→beliefs gap, demotion-only asymmetry) reopened by the live LLM's part-level
seeding; the decision layer cannot reach a cause that is neither seeded nor link-matched.

---

## Fix (diff in `case8_v2.diff`) — two structural changes, both #5-defensible

**(1) Seeding coverage — `_seed_upstream_coverage` (new), called in `diagnose` after
`seed_hypotheses`.** For every *subsystem* in the `_seed_candidates` menu that the LLM omitted, add
it as a hypothesis (at prior, no evidence) **iff** it is an `affects`-ancestor of some subsystem
already in the differential — i.e. an upstream convergence point a single cause could occupy. It
reads only the candidate menu the navigation already surfaced + the graph's own `affects` topology.
A purely downstream omitted candidate is not added; an added upstream hypothesis sits at prior and
is ruled out by negative evidence unless a promotion credits it.

**(2) Granularity matching in promotions — `_subsystem_of` + `_hyps_in_subsystems` (new), used by
`_promote_common_mode` and `_promote_change_cause`.** Match a promotion's target subsystem (and its
`deg_subs` decoys) to any hypothesis whose `node_ref` is the subsystem OR is `part_of`/within it,
using the graph's `part_of` topology (the same family the eval canonicalises over). So a `part.X`
hypothesis that is `part_of sub.X` is correctly promoted/demoted. This also hardens case4
(`_promote_change_cause` now matches a part-granularity calibration seed, not only a subsystem one).

**(3) Symmetric common-mode weight — `_CM_PROMOTE_WEIGHT == _CM_DECOY_WEIGHT == 1.5` (was promote
1.5 / decoy 0.8).** The common-mode signature is *one* datum: it is exactly as strong FOR the
convergent upstream cause as it is AGAINST each surface channel being an *independent* fault (the
channels co-moved, so the per-channel positive credits are consequences, not separate causes). Equal
magnitudes are the principled reading; the old 0.8 was sized when the spike hand-seeded a
non-inflated decoy. With the live M1-inflated `part.detector` (+2.5), a −0.8 demote leaves it above
`sub.power`; the symmetric −1.5 demote drops it to +1.0 (conf 0.731) below `sub.power` (conf 0.953,
margin 0.222), letting the leader-anchored verdict name `sub.power`.

### #5 justification — verified structurally across all 8 cases

- **Seeding coverage** keys on the candidate menu + `affects` topology, never a case/subsystem
  name. Empirically it adds exactly `sub.power` to every case (the only omitted candidate subsystem
  that is an upstream ancestor of the seeded parts' subsystems; `sub.thermal`/`sub.optics` are
  already covered via `part.tec`/`part.window`). On the 7 non-case8 cases that extra hypothesis
  sits at prior 0 and **never receives a promotion link** (verified: the promotion fires on
  *exactly* case8 across all 8 — see below), so it can only *enable* the right answer, never
  manufacture a wrong one.
- **Granularity match + symmetric weight** key on `part_of` topology and the common-mode
  signature, never a case name. The promotion's gate is unchanged (common_mode=true, ≥2 degraded
  subsystems, a recently-changed upstream config); it still fires on **exactly case8** — case2
  (`laser_aging`, also `common_mode=true`) is correctly excluded because it has **no config change**
  (`config_diff.any_change=False`), so no upstream cause is implicated. The match change only
  affects *which already-eligible* hypotheses the eligible promotion links to.

Per-case `promotion_fired` (uniform part-granularity seed): case1–7 = False, case8 = True.

---

## Spike — `investigation/spikes/test_case8_live.py`

Scripts the **actual live seeding** (`LIVE_SEED`: 5 part-granularity hyps, NO `sub.power`, copied
from `cap_case8.json`), the 3 live checks, and the **actual live interpret links** (`LIVE_INTERPRET`
including the M1 over-credit that saturates `part.detector` to +2.5), and a live `synthesize` that
names the wrong `part.detector` (so the leader-anchored verdict must override it). Real
`LidarEnvironment` + real `diagnose`/`beliefs`/`voi`/`scorer`; only the LLM is scripted. Does NOT
hand-seed `sub.power` — that was the prior spike's error.

Asserts:
- `test_live_seed_omits_sub_power_and_coverage_fix_adds_it` — the live seed lacks `sub.power`; the
  coverage fix adds it.
- `test_granularity_match_links_part_decoys_to_their_subsystem` — `part.detector` matches
  `sub.detector` (the live no-op is fixed).
- `test_case8_concludes_sub_power_after_fix` — end-to-end: `answer.root_cause == "sub.power"`,
  `sub.power` is the dominant leader (conf > 0.70, margin > 0.20), the surface decoy `part.detector`
  is demoted below it, and `score().accuracy == 1.0`.
- `test_promotion_attached_a_positive_link_to_sub_power` — the promotion entered the belief math (a
  `+ ev.common_mode` link reaches the `sub.power` hyp), not just text (the M2 gap).
- `test_promotion_is_a_noop_on_a_non_common_mode_case` — case1 gets a `sub.power` hyp too but the
  promotion never fires (no common-mode + upstream change), so it is not concluded.

**Before / after** (live seeding + live M1-inflated decoy, measured by reverting/applying the patch):

| | answer | `sub.power` hyp? | common-mode links | leader (conf, margin) |
|---|---|---|---|---|
| before | `part.detector` (acc 0) | no | none (no-op) | part.detector (0.924, 0.547) |
| after | `sub.power` (acc 1.0) | yes (`hyp.upstream_power`) | +1.5 → sub.power; −1.5 → each part decoy | sub.power (0.953, 0.222) |

(`sub.power` reaches +3.0 = clamp: +1.5 common-mode promotion AND +1.5 change-cause promotion both
fire legitimately — the power-mode change to `config.scan_params part_of sub.power` IS the cause.)

---

## Fix audit — regression risk, granularity-for-scorer, residual gaps

**Regression from the extra seeded hypothesis.** Full suite 158 → 163 (+5 spike), 0 regressions.
The added `sub.power` hyp sits at conf 0.5 on the 7 non-case8 cases. Risk it could (a) become a
spurious leader — no: it has no positive links unless the (case8-only) promotion fires; (b) lower a
winning case's *margin* by becoming the runner-up — bounded: a concluding case's leader is high
(≥0.73) and a 0.5 runner-up still yields margin ≥0.23 > τ_margin=0.20; the suite's full-`diagnose`
tests on case1/4/5/7/8 all pass; (c) block an abstain — no: case5 (abstain) is driven by the
margin-gate on a dispersed differential, and a flat 0.5 hyp does not raise the leader. The
conclude/abstain math behaves.

**Subsystem vs part granularity for the scorer (load-bearing).** `_exact_cause_set` accepts
`sub.power` (subsystem) and its `part_of` configs, but a `part.*` node `part_of sub.power` would
NOT score accuracy (that is localization). The leader-anchored verdict names `top.node_ref`, so the
*concluded* hypothesis must be the `sub.power`-granularity one. The seeding-coverage fix adds the
hypothesis at **subsystem** granularity (`node_ref = sub.power`), and the promotion links to it, so
the leader's `node_ref` is `sub.power` and the verdict scores 1.0. (Had we only demoted the part
decoys without seeding a subsystem-level cause, a surviving `part.*` leader would mis-score.)

**Residual gaps.**
- **M1 still unfixed.** The flip works because the symmetric −1.5 demote overcomes the live +2.5
  M1 inflation *with* the +3.0 double promotion — margin 0.222 clears τ_margin by only 0.022. A
  larger M1 over-credit, or a common-mode case where only the single common-mode promotion fires
  (no aligned config change to also trigger `_promote_change_cause`), would have a thinner margin
  and could fail to clear. The robust fix is M1 (interpret nominal-evidence handling), still
  deferred.
- **Hardware power sag with no config change** is still missed (the promotion requires a recently-
  changed upstream config — deliberate conservatism, unchanged).
- **n=1 caveat** stands: this proves the mechanism deterministically against the captured live
  differential; a fresh live run with a different seeding shape needs its own confirmation. But the
  coverage fix is exactly what de-risks seeding-shape variance — the upstream cause is now seeded
  regardless of what the LLM picks.
