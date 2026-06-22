---
project: fathom
goal: Make case5 (abstain) and case8 (common-mode) succeed LIVE by fixing M1 (interpret
  over-crediting) and the case8 seeding/granularity bug — using the spike+audit pattern, #5-safe.
created: 2026-06-22
status: open
branch: investigate-controller (worktree /home/bolun/projects/fathom-investigate)
---

# Fathom controller — fix M1 + case8, drive case5 & case8 to live success

## Where we are (verified)
A prior investigation took the controller from a thesis-negative 4/8 to **6/8 live accuracy (n=1,
budget 8), 0 regressions** — see `investigation/RESULTS.md` (the full per-shortcoming audit/fix/
spike/fix-audit table) and `investigation/audits/*.md`. All fixes are integrated and committed on
branch `investigate-controller` (commits df91c89 → 9634c68 → d5c6db7). Full test suite: **179
passed, 1 skipped, 1 xfailed** (run with `PYTHONPATH=/home/bolun/projects/fathom-investigate/src
/home/bolun/projects/fathom/.venv/bin/python -m pytest tests/ investigation/spikes/ -q`).

Live results (n=1, budget 8), via `investigation/capture.py <caseN>`:
- PASS: case1,2,3,6 (no regression), **case4** (fixed), **case7** (fixed).
- **FAIL: case5** (concluded part.laser_module; gold=abstain) and **case8** (concluded
  part.detector; gold=sub.power). These two are this handoff's job.

Per-case live IG dumps are saved: `investigation/cap_case{1..8}.json` (hypotheses+log_odds, links,
evidence, ig_conflicts, trace, score, ground_truth).

## The two remaining failures — root cause (verified live, not inferred)

### case5 — M1: interpret over-credits nominal/at-spec checks → confident WRONG leader
Live IG (`cap_case5.json`): leader **H4 part.laser_module at +2.00** (8 positive links), runner-up
−1.00 → conf 0.881, margin 0.61. Every check on case5 is nominal/at-spec (no anomaly); the correct
answer is **abstain** (gold root_cause=None, trigger=log.reboot which the sweep demotes). The
margin-aware abstain gate (already integrated) **cannot** catch this: it's not a dispersed
differential, it's a confident DOMINANT wrong leader. The fix MUST be at the interpret layer: a
hypothesis must not accumulate strong POSITIVE log-odds from nominal/negative evidence. Nominal
evidence rules OUT, it does not rule IN.
- Code: `src/dh/controller/llm.py::interpret_result` (~L404-446) builds links; polarity/weight come
  from the LLM JSON, clamped to MAX_WEIGHT=2.0. The system prompt (llm.py L36-40) already SAYS
  "a nominal check argues AGAINST" — the LLM ignores it. A prompt-only fix is (a) unreliable and
  (b) risks #5 if tuned to these cases. Prefer a STRUCTURAL guard.
- The deterministic checks return structured verdict flags (read `src/dh/checks.py`): e.g.
  `at_limit`, `correlated`, `bias_drift`, `stuck`, `common_mode`, `localized`,
  `onset_predates_event`, and now `losing_setpoint`. A check result is "affirmative" (an anomaly
  was found) vs "nominal" (no anomaly). Candidate general fix: derive polarity/affirmativeness
  from the check's own verdict deterministically, OR require ≥1 affirmative finding linking to the
  leader before concluding (else abstain). Design must be check-agnostic / structural.

### case8 — seeding gap + node-ref granularity mismatch (NOT just M3)
Live IG (`cap_case8.json`): the LLM seeded 5 hypotheses at **part granularity**
(`part.detector`, `part.laser_module`, `part.tec`, `part.window`, `sub.calibration`) and **never
seeded `sub.power`** — the true cause is not in the differential at all. The integrated
`_promote_common_mode` (loop.py) DID fire (`ev.common_mode` was added) but attached **zero links**:
it matches hypotheses by `sub.*` node_ref (`target_subs={sub.power}`, `deg_subs={sub.detector,…}`)
while the hypotheses are `part.*`. So promotion was a no-op; decoy `part.detector` (M1-saturated to
+2.5) won. TWO bugs:
1. **Seeding coverage**: `seed_hypotheses` (llm.py L348) lets the LLM pick which candidates become
   hypotheses; it picks parts and omits the common upstream subsystem `sub.power`.
   `_seed_candidates` (loop.py L39) DOES return sub.power in the candidate menu — but the LLM
   doesn't instantiate it. Fix idea: deterministically ensure common upstream subsystems (or all
   `_seed_candidates`) are represented as hypotheses, OR seed a hypothesis for any subsystem a
   common-mode/promotion path could implicate.
2. **Granularity matching**: `_promote_common_mode` (and `_promote_change_cause`) match by exact
   `node_ref == subsystem_id`. A hypothesis at `part.X` that is `part_of sub.X` should be matchable
   to a `sub.X` promotion. Fix idea: match a promotion's subsystem to any hypothesis whose node_ref
   is the subsystem OR part_of/within it (use the graph's part_of topology). NB case4 worked only
   because the LLM happened to seed `sub.calibration` at subsystem granularity.

> Lesson that produced this handoff: the case8 spike HAND-SEEDED a `sub.power` hypothesis, so it
> passed deterministically while live fails. **Spikes must reflect the real LLM's seeding/polarity
> behavior, or they over-promise. Live (`capture.py`) is the only proof of a case.**

## How to work (the established pattern + hard constraints)
- **Worktree**: work in `/home/bolun/projects/fathom-investigate` (branch investigate-controller).
- **venv gotcha**: the venv's editable install points at the MAIN repo `/home/bolun/projects/
  fathom/src`. ALWAYS prefix `PYTHONPATH=/home/bolun/projects/fathom-investigate/src` with
  `/home/bolun/projects/fathom/.venv/bin/python`, or you silently run main-repo code.
- **Spike+audit per fix**: real `LidarEnvironment(case)` + real `diagnose()` + `ScriptedBackend`,
  exactly like `tests/test_controller_tec.py` and the existing `investigation/spikes/*.py`. BUT for
  these two, make the scripted seed/interpret FAITHFUL TO OBSERVED LIVE BEHAVIOR (part-granularity
  seeding; over-crediting nominal checks) — replay the captured `cap_case5.json`/`cap_case8.json`
  links if helpful. The spike must reproduce the LIVE failure, not an idealized one.
- **#5 (non-negotiable)**: fixes must be GENERAL mechanism changes, justified structurally (fire on
  a structural signature across all 8 cases, no case names/per-case constants). M1 especially:
  do NOT tune the interpret prompt to these 8 cases. A structural polarity/affirmativeness guard
  or an "affirmative-evidence-required-to-conclude" rule is defensible; case-keyed prompt text is
  not.
- **Live confirmation is the orchestrator's job, SERIALIZED**. Never run two live `claude -p` evals
  concurrently (subscription CLI collapses → ~20min/call). Check first:
  `pgrep -af "claude -p" | grep -v grep`. Do NOT kill the user's brain2 session
  (`/proc/<pid>/cwd` = …/brain2). Run `capture.py caseN --budget 8` one at a time.
- **Goal (definition of done)**: case5 abstains and case8 concludes sub.power **LIVE**
  (`capture.py` shows acc=1.0), with **no regression** on case1,2,3,4,6,7 live, and full suite
  green. n=1 is the working bar (variance is real; re-run a pass once to sanity-check if cheap).

## Key files
- `src/dh/controller/llm.py` — `interpret_result` (M1), `seed_hypotheses` (case8 seeding),
  `synthesize` (leader-anchored verdict, already integrated). System prompt at L33-44.
- `src/dh/controller/loop.py` — `_promote_common_mode`, `_promote_change_cause`,
  `_change_cause_subsystem`, `_finalize_conflicts`, `diagnose` (gate at the bottom).
- `src/dh/controller/beliefs.py` — `update_beliefs`, `leader`, MAX_LOG_ODDS=3.0.
- `src/dh/checks.py` — check verdict flags (the structural signals for an M1 fix).
- `src/dh/eval/bespoke.py` — scorer (`score`, `_exact_cause_set`, `_canon`); confirms real-vs-artifact.
- `src/dh/generator/cases.py` — the 8 CaseSpecs (salient_is_cause field).
- `config.yaml` — tau_dom=0.70, tau_margin=0.20, tau_min=0.55, budget=12 (runs use 8).
- `investigation/capture.py` — live capture/confirm harness. `investigation/BRIEFING.md` — pipeline map.
- `investigation/RESULTS.md` — the full prior findings table. `investigation/cap_case*.json` — live IGs.

## Open risk to watch
The **leader-anchored verdict** (synthesize names the belief leader when dominant) amplifies the
belief state both ways. An M1 fix that corrects belief polarity makes this safer; verify the M1 fix
doesn't make a previously-correct case's leader flip (live regression check on case1,2,3,4,6,7).
