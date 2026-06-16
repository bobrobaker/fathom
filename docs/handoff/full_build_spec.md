# Full-build specification — diagnostic harness (MVP)

**Status: provisional, spike-conditioned.** This extends the validated spike to a complete, showable MVP and portfolio piece. It is expected to be **revised by the spike's findings** — if the controller's uplift, the benchmark fit, or the difficulty calibration come back differently than hoped, the relevant sections change. Build the spike first (`spike_build_plan.md`); treat this as the destination, not the next keystroke.

Builds on: `spike_spec.md` (contracts — extended, not replaced), `spike_build_plan.md`, `worked_sut_example_lidar.md` (SUT, faults, difficulty catalog), `ontology_typed_links.md` (schema, links).

---

## 0. What the spike decides (and this doc inherits)

- Whether the controller's win is on accuracy or only on the **capability family** → sets the **headline claim**.
- Whether the benchmark core is competitive (M4.5/M8) → whether the benchmark is a **showcase or a scoped footnote**.
- Which difficulty mechanisms actually separate the controller from the baselines → **which to scale**.
- Whether reified evidence nodes and which links earned their place (the ontology was provisional, to be re-evaluated post-spike) → **the final schema**.

If the spike's finding is modest, this doc's claims shrink to match it — by prior agreement.

---

## 1. The full SUT

All six faults authored to depth (TEC degradation, laser aging, window contamination, detector bias drift, calibration drift, scanner miscalibration), with the abstracted-subsystem stubs promoted as needed. Full coupling topology. The small **dynamic core** for the inherently-temporal faults (the D4 class — metastable, coupled-loop, resonance-corner). Numbers **calibrated against real automotive-lidar specs** (the easy grounding pass). The uniform subsystem wrapper interface throughout, with the "swap a stub for richer mocked machinery" path realized for ≥1 previously-abstracted subsystem — demonstrating the extensibility claim concretely.

## 2. The corpus + generator at scale

The generator produces realistic-volume cases across **all** schema types: telemetry (queryable-by-condition + the utility/check layer), tickets, reports, logbooks (**LLM-roughening on by default** — the messy human record), docs, **domain_docs** (the specialized-vocabulary layer, with deliberately out-of-model terms that force retrieval or C4 gap-surfacing), design/test docs, procedures, diagnostic_actions (history-in + recommend-next), **BOM** (hierarchy + versions + customer configs), and **people / meetings / chats** (ownership, the recurring-meeting timeline, informal records). The typed graph at full scale. Volume tuned so retrieval and navigation are mandatory, not optional. The generator is also a clean **standalone engineering artifact** — it produces labelled diagnostic cases even if the AI layer is ignored.

## 3. The full difficulty catalog, instantiated

The complete ~20-mechanism catalog (worked example §7) realized across a larger case set, **capability-bound throughout** (the prior-attempt lesson), and anti-shortcut-balanced at scale. The catalog is the generator's input vocabulary; new mechanisms — including ones observed in real production triage — get appended. The emergent/hardest class (observability gap, threshold/bifurcation, self-erasing/NFF, common-mode, lagged cause) is authored using the dynamic core.

## 4. The full harness

The polished controller: the abductive loop with a **formal VOI** option (entropy reduction over the hypothesis distribution) alongside the spike's LLM-scored version; richer tool/retrieval interfaces (optionally via MCP for real integrations); the controller/environment separation preserved, leaving room for more environment adapters. The **Investigation Graph remains the single live state object** the reasoning writes, the eval reads, and the viewer renders.

## 5. The full eval suite

The bespoke eval at scale (many cases, the two metric families from spike §8.1, variance over runs); **multiple benchmarks** (MuSiQue + HotpotQA + optionally a newer set — scope set by the spike's benchmark finding); the full baseline ladder; and a **reproducibility harness** (seeds, pinned model, reported variance) so every number in the writeup is defensible.

## 6. The showpiece — the live Investigation Graph viewer

The polished, impressive artifact (the explicit "seeming impressive" goal): a **live view of the controller's actual state object** as it runs — hypotheses appearing, recoloring for/against, branches deepening, the trigger demoted, the abstention case showing honest uncertainty. This is the demo that leads the portfolio. It reads the same IG state object the controller writes and the eval scores; there is **no separate animation layer**.

## 7. The portfolio layer (the point of the exercise)

- A **writeup that leads with the designed eval** — the difficulty catalog, the metric families, the baseline ladder — because eval literacy is the hiring signal. Then the harness, then the finding.
- The **finding framed modestly and honestly** (carried from the spike): what the structure bought, where it tied, where it didn't — a test-architect's report, credible whether or not the controller dominates.
- A **README** that opens with the eval and the headline number(s), the live IG demo, and a one-paragraph "why this matters for AI-native test architecture."
- **Lidar framing kept legible** for AV/sensing recruiters.

## 8. Engineering at scale

Repo grown from the spike layout; **CI** running the eval on every change; the reproducibility harness; config-driven thresholds and seeds.

## 9. Sequencing (spike → MVP, in phases)

- **Phase A (gated on spike findings):** scale the case set + difficulty catalog; calibrate numbers; lock the schema to what the spike actually traversed.
- **Phase B:** the full harness (formal VOI, richer tools) + the polished viewer.
- **Phase C:** the full eval suite + reproducibility + the writeup/README/demo.

Each phase is shippable; the portfolio piece is presentable after **Phase A + the viewer**.

## 10. Spike-conditioned open decisions

- Headline claim (accuracy vs capability) — set by the spike.
- Benchmark scope (showcase vs footnote) — set by M4.5 + M8.
- Final schema (which links/nodes/reification survived) — set by spike traversal data.
- Whether to add environments/domains beyond lidar — a stretch, only if it strengthens the story.

*This doc is the destination. The spike is the next step, and its results may revise much of the above — by design.*
