# Response — Fathom spike-completion-audit handoff (2026-06-16)

Replies to `handoffs/2026-06-16-spike-completion-audit.md`. Each item below carries the decision/instruction for the next session. Items originally flagged for Bolun's call (⚠) have been **decided** — the resolved calls are recorded in **Resolved direction calls** at the bottom and folded into the relevant items. An **Independent audit** sits between. Companion deliverable: `fathom_visualizer_spec.md` (the hostable showpiece — build *after* the finding; see **Build order** at the bottom).

> **Critical path to *ship a finding*:** A1 → A2 → A3 → A4, with **B4 + B5 done** (a credible `bare_llm` and per-case capability-binding). Everything else — A5 benchmark, A6 prompts, the fairness audits — is necessary but **time-boxed** and must not block shipping. B4 and B5 are the credibility linchpin: get them right *before* any final numbers.

---

## Part A

**A1 — per-fault corpus-delta refactor.** Do it, first, as you specced. Make only diagnostic-action *results* and prior-report *conclusions* fault-aware (a per-fault delta on `FaultFacts`); keep structure (telemetry shapes, graph, BOM, generic templates) shared. Replace the `exclude_artifacts` stopgap with the delta. The line on "how much" is in **C1**.

**A2 — author #4/#6/#7/#8 → ≥9.** Yes, with two hard constraints: (a) each **capability-bound on its scored axis** — add the per-case assertion from B5; (b) the *set* hits ≈0.5 anti-shortcut by making **#4 (calibration drift after a config change) the case where the recent change IS the true cause** (so `shortcut` is *right* there) — this fixes B8. Keep #6/#7/#8 with the trigger-as-coincidence pattern. Fold the `query_telemetry(condition=)` wiring (A9) in here — #5/#7 need it.

**A3 — ≥3-run variance eval.** Yes (S1). Report mean ± spread per metric per solver. Run after A2 on the **CLI backend** (the only path the current plan supports), with the cost-calibration in B10. Hold the model fixed across all four solvers per run (see A8).

**A4 — findings doc.** Yes — this is *the* deliverable; nothing ships without it. Write it **after** A2/A3 so it reports real numbers. Structure as you proposed; **lead with the eval design** (the hiring signal), then the per-case table with variance, then the honest cost section (B3), the viewer, and the clean outcome. Keep the modest-story framing.

**A5 — benchmark. (decided: build it.)** Build `tools/load_musique.py` and run the M4.5 fail-fast on **real MuSiQue**, n=20 — *not* the synthetic smoke (B9: it signals nothing). Decide from n=20: competitive → n=100, keep; not → scope to report-only with one honest line ("purpose-built for diagnosis, not generic QA"). Never ship a synthetic-smoke number. **[Superseded 2026-06-16:** the *competitiveness* framing here is replaced by a *structural* one — MuSiQue can't validate the differential regardless of score; footnote it, FEVER for generalization. See `docs/decisions/2026-06-16-benchmark-tests-retrieval-not-differential.md`.**]**

**A6 — prompt iteration.** Yes, to fix B7: the `interpret` prompt must (i) when two hypotheses are both high, prefer a *discriminating* action over re-confirming both, and (ii) always run the onset check on a salient recent event and record it in `conflicts` when demoted. Then **re-measure**; do not touch cases/scoring (#5). **Time-box** (2–3 iterations) — polish, not a ship-blocker.

**A7 — scoring id-space symmetry.** Yes. Add a test asserting the canonicalization (action-key→check, signal↔metric, evidence→source) is applied identically to all four solvers, and that a baseline's raw citation for the same evidence canonicalizes to the same id as the controller's. (Ties to C5/B6.)

**A8 — model pin. (decided: test Opus.)** During A6, test the controller's reasoning calls on **Opus** — B7's under-discrimination may be model capability, not just prompt. Pin whichever gives acceptable capability at acceptable cost, report which, decide before A4. **Like-to-like invariant:** for any one comparison the model is held fixed across *all* LLM-based solvers (Opus-`controller` vs Opus-`bare_llm` vs Opus-`react`, or the same trio on Sonnet) — never mix models within a comparison, or the model confounds the structure. Produce one self-consistent result set per model. `shortcut` is LLM-free → constant across both.

**A9 — deferred items.** Re-triage: `query_telemetry(condition=)` is **not** deferrable (→ fold into A2). BM25→hybrid only matters for the corpus-exceeds-context case → do it when that case is authored. Snapshot deepcopy → quick verify, keep.

---

## Part B

**B1 — headline on 1 case.** Resolved by A2 (≥9) + A3 (variance). Until then the finding is explicitly "n=1, illustrative" and A4's claims must not be written off case #1.

**B2 — n=1 / wobble.** The ≥3-run variance (A3) is the test. Report the capability number as mean ± spread; if it's within noise, **say so** — that's the honest finding. A6 should reduce the wobble; re-measure after.

**B3 — cost 6×. (decided: report as an honest tradeoff.)** ~6× is normal — even modest — for a bounded agentic loop (~15–20 calls with growing context vs one); it's architecture-driven, not a CLI artifact. So: (1) keep the honest number in A4 — don't hide it; (2) a *modest* reduction pass (budget already 8; tighten prompts, kill redundant per-step LLM calls) and report the post-reduction premium; (3) frame it as "the structure buys capability `bare_llm` structurally lacks — conflict-surfacing, trigger-demotion, calibrated abstention — at a quantified token premium," and note the count is ~model-agnostic (shared tokenizer), so a cheap-model-harness lands near a frontier one-shot in *dollar* terms. Label it a CLI-derived estimate (B10). T3 (≤cost) is a *confirmation* criterion, not a *success* gate; a clean miss, reported, is fine.

**B4 — is `bare_llm` "best honest"? (linchpin).** Current version (summaries + 5 fixed-query artifacts) is **too thin.** Strengthen it: give it the **maximal raw data a context-dump would contain** — full (or richly-summarized-with-statistics) telemetry series, the full artifact set (or a strong retrieval, not 5 fixed queries), and the raw config — **but not the check verdicts** (those are the controller's tooling; handing them over rigs it the other way). Principle: *all the data, none of the computed discriminators.* Re-run. If it still can't surface trigger/conflict, the gap is real; if it can, the case fails B5. Do this **before** any final numbers (non-negotiable #3).

**B5 — capability-bound per case.** Add a gate: the strengthened `bare_llm` (B4) must **fail** on each case's scored axis. If it passes, re-author or cut the case. Make it a test, per case. B4+B5 are what make the finding credible.

**B6 — do relaxations favor the controller?** Adversarial fairness pass: for each relaxation, a test that it helps a baseline as much as the controller (symmetry). Tighten accuracy per **C6**. For canonicalization, the A7 symmetry test. Any relaxation that can't be shown symmetric → remove it.

**B7 — capability quality shaky.** Fix via A6 (prompts) **and** investigate the **C3 clamp interaction** — a decoy stuck at 0.99 is likely saturated by early clamped links with no path back down. Ensure contradicting evidence can pull a hypothesis *down*, and consider clamping cumulative log-odds, not just per-link. Re-measure; report the averaged number even if it shrinks.

**B8 — anti-shortcut skew.** Fixed by making **#4 the "recent change IS the cause" case** (A2). Add a test asserting the set's salient-event↔cause correlation ≈0.5 (not ~0).

**B9 — benchmark unvalidated.** Same as A5: real MuSiQue n=20 decides; synthetic smoke proves nothing. Drop or report-only if not competitive — honest either way.

**B10 — reproducibility. (decided: CLI now, build the swappable backend.)** The current plan doesn't support API, so the final numbers come from the CLI backend. Make the estimate honest: measure the CLI's *fixed per-call overhead* (a near-empty prompt → the baseline char count it adds), subtract it to get an **API-equivalent estimate**, and label every cost figure "CLI-derived estimate, net of ~N tokens/call scaffolding" — applied **symmetrically to all four solvers**. Variance reporting (A3) covers residual nondeterminism. **Build a swappable LLM-backend interface (CLI ↔ API), default CLI**, so precise counts (and a validation of the calibration ratio) are available the moment API access exists.

---

## Part C

**C1 — the corpus-delta line.** The line: **facts *about the fault* vary per-fault (legitimate); difficulty/answer tuning does not (forbidden, #5).** A diagnostic-action result or a prior-report conclusion is a fact about the specific fault — vary it. Bespoke per-case wording chosen to move difficulty/score is tuning — cut it. Test: *if the variation would change with the ground-truth fault even with difficulty held constant, it's a fact (OK); if it exists only to move difficulty/score, it's tuning (cut).* The generator stays a generator — it composes shared structure + templates and takes per-fault *facts* as input, which is what a forward-causal model does.

**C2 — `bare_llm`'s digest.** Per B4 — strengthen to max raw data (full series / all artifacts / raw config), no check verdicts. The 5-fixed-query retrieval is the weakest part; replace with all-artifacts-in-context (if they fit) or a strong retrieval matching what a careful human would search.

**C3 — weight clamp 2.0.** Clamping is the right *mechanism* (bounded per-evidence LLR is standard robustness). Make 2.0 *principled*: state it as "≈7× odds shift per evidence, chosen so ~2–3 concordant items reach τ_dom=0.70." Sensitivity-check at 1.5/2.5; if the result moves materially, report that fragility. Investigate the B7 interaction (stuck decoy).

**C4 — abstain logic.** For the spike the low-confidence path is **probably enough** *if* case #5 is authored so no hypothesis gets strong support (intermittent/coincidence → all weak → leader ≤ τ_min → abstain). Don't build the contradiction-trigger path now — defer to full build. **But:** author #5, run it, and confirm it abstains via the low-confidence path; if it wrongly concludes, weaken #5's evidence or build the contradiction path. Test-driven.

**C5 — evidence-F1 canonicalization.** Keep it; the A7 symmetry test is mandatory — a baseline's raw citation and the controller's structured id for the same evidence must canonicalize identically, and canonicalization must never turn a wrong citation into a right one.

**C6 — accuracy granularity.** **Too lenient** as a correctness credit. Don't let "thermal" (subsystem) score full accuracy for a "tec" (part) fault. Recommend: accuracy = exact part match for part-level faults; report subsystem-correctness as a **separate "localization" metric** (partial credit), not folded into accuracy. This removes the B6 worry on accuracy and stops a vague answer scoring as correct.

---

## Independent audit (not in the handoff)

**1. (Critical) The repo / project knowledge is polluted with the superseded RCA project.** Searchable project knowledge contains **both** briefs at once: two `CLAUDE.md` (Fathom vs "RCA — Cross-source root-cause AI"), two `docs/road.md` (Fathom Phase-1 vs RCA Phase 0–6), and a full old `docs/handoff/` packet (`00_INDEX`, `01`–`07`, `02_design_constraints` C1–C10, `03_build_plan`, `05_scenario_contract`, `07_rag_and_agentic_harness`) sitting beside the new spike docs. The two projects have **different theses** (RCA = leave-one-source-out ablation; Fathom = abductive controller vs baselines), **different code** (`simkit/`+`harness/` vs `src/dh/`), and **different domains** (metrology A02/A09/B03 vs lidar TEC/laser). Your `CLAUDE.md` *mandates* searching project knowledge — so the next agent **will** pull RCA content and risk conflating it with Fathom. **Do:** (a) verify the live repo root `CLAUDE.md`/`docs/road.md` are the Fathom versions and purge the old RCA files from `docs/handoff/` into `docs/archive/` (or delete); (b) clean this project's knowledge so it indexes only the current Fathom repo (drop the old RCA snapshot, VVsim notes, brain2-vault notes, and the `monition/dump.sql` content); (c) add to `00_README`/`CLAUDE.md`: *"Ignore any RCA / ablation / simkit / four-source / scenario-contract content — superseded prior project; authoritative thesis = abductive controller vs baselines, code in `src/dh/`."* This is the single highest-leverage cleanup before the next session.

**2. Scope-creep vs the thin slice.** Nine A-items + fairness audits + benchmark + prompt iteration is drifting from "thin slice + one finding." Protect shipping: the ship-bar is A1→A2→A3→A4 with B4/B5; time-box A5 and A6 (both can be report-only / good-enough). Don't gold-plate.

**3. The trajectory points at a genuinely modest result.** Once `bare_llm` is strengthened (B4), variance is measured (B2/B3), and the cost premium is in the open, the net story may be "modest capability gain, accuracy parity, large cost premium, some variance." That's a valid finding by our prior agreement — but it *is* modest. Do the cheap strengthening (B4 done right, A6 prompts, a modest cost cut, the A8 model test) so it's the *best honest* version, then accept and frame it. Don't over-invest chasing a dominant win the spike can't prove.

**4. The showpiece (live IG viewer) is under-attended for an "impressive"-goal project.** S4 ("renders case #1") is a low bar, and the handoff gives the viewer one line — yet the demo is what a reviewer sees in 60 seconds. A small explicit pass to make the live state-evolution genuinely legible (recoloring, the demoted trigger, the abstention case) is disproportionately high-impact for the portfolio.

**5. (Minor) The salient-but-noncausal event is always a reboot.** Beyond B8's correlation fix, vary its *kind* (config change, part swap, neighboring-tool incident) so the controller isn't pattern-matching "reboot = trigger." Cheap diversity that strengthens the capability claim.

---

## Resolved direction calls (Bolun, this session)

- **B3 — cost premium:** report it as an honest capability-vs-cost tradeoff (CLI-derived estimate); modest reduction pass; no chasing a cost win.
- **A5/B9 — benchmark:** build `tools/load_musique.py`, take the real n=20 read, decide keep-vs-report-only from it. **[Superseded 2026-06-16 → footnote (structural, not competitiveness); FEVER for generalization — `docs/decisions/2026-06-16-benchmark-tests-retrieval-not-differential.md`.]**
- **B10 — reproducibility:** CLI estimates with the per-call-overhead calibration (above); build the swappable CLI↔API backend, default CLI.
- **A8 — model:** test Opus on the controller, like-to-like (model held fixed across all solvers per comparison); pin the winner before final numbers.

## Build order

1. **The finding first — this doc's critical path:** A1 → A2 → A3 → A4, with B4 + B5. This produces the shippable deliverable *and* the recorded runs.
2. **Then the showpiece — `fathom_visualizer_spec.md`:** the polished viewer is *replay-only*, so it needs the authored cases and a completed eval to replay. Build it after A4. (The minimal case-#1 viewer, S4, already exists in the interim.)

Authoritative spec for *what* to build stays the existing brief (`00_README_for_coding_agent.md` → `spike_spec.md` → `spike_build_plan.md`); this doc is the decision record layered on top.
