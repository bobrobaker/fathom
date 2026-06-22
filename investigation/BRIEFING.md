# Investigation briefing — why the controller underperforms (orchestrator → auditors)

You are auditing ONE shortcoming of Fathom's abductive **controller** (the `diagnose()` loop).
The spike eval found the controller **thesis-negative**: accuracy 4/8 (bare_llm 6, react 5), its
capability "lead" comes from a deterministic layer not from reasoning, and it is the most
expensive solver. Your job: audit your assigned shortcoming, trace it to exact code, propose a
fix, **prove the fix with a deterministic spike**, and audit the fix. This briefing is the shared
ground truth so you don't re-derive the pipeline.

## Non-negotiable #5 (read this first)
Never tune cases / baselines / scoring to manufacture a controller win. A legitimate fix corrects
a **general mechanism bug** (applies uniformly to every case, would help unseen cases). An
illegitimate fix special-cases the 8 cases that exposed the problem. **Every proposed fix must
carry a one-paragraph #5 justification** arguing structurally (not nominally) why it is general.
If the cleanest fix can't be justified as general, say so — a documented "can't fix without
overfitting" is a valid result.

## The pipeline (files, all under `src/dh/`)
`controller/loop.py::diagnose` orchestrates:
1. `seed_hypotheses` (llm) — differential from symptom + affects-neighbors + playbook.
2. loop over budget (config.yaml `controller.budget=12`): `propose_actions` (llm) →
   `voi.select` → `_execute` (real `Environment`, deterministic) → `interpret_result` (llm) →
   `beliefs.update_beliefs` → stop if `_should_conclude`.
3. `_finalize_conflicts` — deterministic conflict sweep (onset-vs-event demotion + stuck-channel).
4. abstain gate: `abstain = leader_conf <= tau_min` → `synthesize` (llm).

Belief math (`controller/beliefs.py`): each evidence→hyp link has polarity (+/-) and weight
(|LLR|, capped `MAX_WEIGHT=2.0`). `update_beliefs`: `log_odds = prior + Σ(sign·weight)`, clamped
to `±MAX_LOG_ODDS=3.0` (so conf saturates at sigmoid(3.0)≈0.953). `confidence=sigmoid(log_odds)`.
Thresholds (config.yaml): `tau_dom=0.70`, `tau_margin=0.20`, `tau_min=0.55`.

## Root mechanisms the orchestrator already suspects (verify, don't assume)
- **M1 — interpret over-credits nominal/at-spec checks as POSITIVE support.** The interpret prompt
  *asks* for negative links on nominal readings, but observed live the LLM credits at-spec/at-limit
  readings positively to the leader → multiple hypotheses saturate to the +3.0 clamp (conf 0.953).
  Seen live: H4=3.00, H2=2.50, H3=2.50 simultaneously, with `tec_load_check at_limit=true` (91% of
  rated) credited *positively* to the leader.
- **M2 — the deterministic conflict sweep never enters the belief math.** `_finalize_conflicts`
  appends ids to `ig.conflicts` (text only, fed to the synthesize prompt) but adds **no links**, so
  demoting a salient event or flagging a stuck channel does NOT change any `log_odds`. The
  "evidence layer" the findings credit is disconnected from belief/abstain.
- **M3 — the deterministic layer is demotion-only (asymmetric).** It can demote a salient event but
  never *promote* "the recent change IS the cause." On `salient_is_cause=True` cases (case4, case8)
  nothing credits the true change-cause.
- **M4 — abstain gate is conf-only.** `abstain = conf <= tau_min`; it ignores low margin / a
  dispersed differential (several comparably-supported hypotheses), so a saturated-but-ambiguous
  state concludes confidently instead of abstaining.
- **M5 — VOI selection** (`voi.select`/`voi.py`) may under-select an expensive discriminating
  check, or `expected_discrimination` is mis-estimated (case7 needs the costly D6 check).

## The 8 cases (`src/dh/generator/cases.py`); your target is one of the 4 misses
- case4 `calibration_drift` (`salient_is_cause=True`): recent cal change IS the cause. acc 0.
- case5 `no_clean_cause` (`salient_is_cause=None`): correct answer is **abstain**. acc 0 (failed to
  abstain → `abstention_calibration=0`).
- case7 `tec_degradation_variant` (`salient_is_cause=False`): near-symmetric to a decoy; needs the
  expensive discriminating check. acc 0 but `abstention=1` → it concluded the WRONG cause.
- case8 `common_mode_power` (`salient_is_cause=True`): one cause looks like two faults; redundant
  channels agree but are wrong. acc 0 (all LLM solvers miss; only shortcut gets it).

## Confirm the failure is REAL before proposing a fix (mandatory)
A `0` may be a **scorer artifact**, not a real wrong answer (the react baseline once scored
all-zeros from a harness key-mismatch bug). Accuracy is `named ∈ _exact_cause_set(gt.root_cause)`
in `src/dh/eval/bespoke.py` with `_canon` canonicalization. Verify **structurally**: does the
gold `root_cause` node id, after `_canon`, actually fall in `_exact_cause_set`? Could the
controller name a correct node in a form the scorer drops? If the failure is a scorer/harness bug,
the fix is to the harness and #5 does not apply — say so. (A flawed split voids negatives too, not
just inflated positives — re-test, don't assume the negative is sound.)

## How to spike (deterministic, NO live LLM calls — the machine has a live eval running; do not add load)
Use `ScriptedBackend` exactly as `tests/test_controller_tec.py` does: real `LidarEnvironment(case)`
+ real `diagnose()`/`beliefs`/`voi`/scorer, with the LLM's seed/propose/interpret/synthesize
replies scripted to **representative, faithful** judgments for your case (construct them from the
case graph + the real check outputs — run the checks via the env to get real result payloads;
that is deterministic and free). Show: (1) the failure reproduces under scripted-but-faithful LLM
output, (2) your code fix flips it to the correct answer/abstain, (3) it does NOT break the passing
cases (case1/2/3/6 patterns). A scripted spike that drives the REAL deterministic machinery to the
right outcome is the proof; a final live confirmation is the orchestrator's job, serialized later.

Inspect a case's real evidence quickly:
`from dh.generator import generate; from dh.environment import LidarEnvironment`
`case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed); env = LidarEnvironment(case)`
then call `env.run_check(...)`, `env.read_logbook()`, `env.list_signals()`, inspect
`case.graph.nodes`, `case.ground_truth`.

## Deliverable (return value — main session keeps only this)
A markdown section for your shortcoming:
1. **Audit** — confirmed-real vs scorer-artifact (with the structural check); the exact failure
   mechanism mapped to file:line; which of M1–M5 (or new) it hits.
2. **Fix proposal** — the code change (file:line, concrete diff sketch), with the **#5
   justification** (why general, not case-tuned).
3. **Spike** — the ScriptedBackend test you wrote (path), what it asserts, and the before/after
   result (fails on current code, passes with the fix). Put tests in `investigation/spikes/`.
4. **Fix audit** — what the fix might break, regression risk on the 4 passing cases, residual gaps.
End with a `## Takeaways` block: decisions made, gotchas hit, lessons worth keeping.
