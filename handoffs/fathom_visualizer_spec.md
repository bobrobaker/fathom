# Fathom visualizer — spec (the showpiece)

**Status:** spec for the polished, hostable Investigation-Graph viewer. The spike's S4 viewer (renders case #1 across steps) is the minimal-viable version; this is the portfolio-grade target. Builds on the IG snapshot contract (`spike_spec.md` §3.3); expands `full_build_spec.md` §6.

## 0. What it is

A **static, hostable web frontend** that replays recorded diagnostic runs as a live-evolving Investigation Graph — what a visitor to your portfolio site watches to *see the harness think*. It is **replay-only**: it plays back exported IG snapshots from real runs, **not** live LLM calls (a public static site can't make authenticated model calls or expose keys). The "live view of the actual state" stays faithful — it replays the controller's actual recorded state evolution, just not generated in the browser.

## 1. Hosting constraints (the reason for the shape)

- **Static** — plain HTML/CSS/JS, deployable to GitHub Pages / Netlify / your own site. No backend, no API keys, no server.
- **Self-contained** — one small bundle; data baked in or fetched from local JSON. No build step, or a trivial one.
- **Replay, not live** — recorded runs only. Live diagnosis stays in the eval harness (which holds the key); the site shows its outputs.
- No browser storage; fast first paint; works offline once loaded.

## 2. Data contract (what it reads)

Per recorded case, a JSON containing: the IG `snapshots[]` (each an `InvestigationGraph`, §3.3); a per-step `trace` (the action taken, the VOI pick, the evidence interpreted, the confidence deltas); the case header (symptom — **ground-truth-free**); the final `Answer`; and the case's eval row (accuracy + capability families). A `manifest.json` lists the cases. `viewer/export.py` already emits the snapshots — extend it to emit this bundle.

## 3. The view

- **The graph (center).** Symptom → hypotheses → evidence (a mutated fishbone / layered graph). Encoding:
  - hypothesis nodes colored by **status** (open / supported / ruled-out / leading) with **confidence** as intensity;
  - **evidence edges** carry polarity (+/−) and weight (thickness);
  - the **trigger** node visually distinct (a context/trigger style, not a hypothesis);
  - the **abstention** outcome rendered honestly — no false winner, the differential left open with the "no clean cause" note.
- **Step/play controls.** Scrub the snapshots; play/pause; step ±; speed. As it plays, nodes appear, recolor for/against, branches deepen on contested hypotheses while settled ones freeze — the search visibly deepening.
- **Reasoning side-panel.** For the current step: the **action taken** (and the VOI reason for it), the **evidence interpreted** (weight, polarity, source), and the **confidence deltas**. This is the harness's thinking made legible — the differentiator, not decoration.
- **Case selector.** Switch among recorded cases to show range: the TEC cross-subsystem case, the abstention case, a buried-evidence (navigation) case. 2–4 cases.
- **Header.** Symptom, final answer (or abstention), and the case's accuracy + capability row.

## 4. Design direction (slick)

- Restrained, modern palette; one accent for "leading," green/red for supported/ruled-out, neutral for open, a distinct hue for the trigger. High contrast, legible.
- **Smooth transitions** between snapshots — nodes fade/scale in, edges draw, colors interpolate. The diagnosis should feel like it *unfolds*, not cuts between frames.
- Clean typography; a compact legend; a one-line caption per case.
- Desktop-first; degrade gracefully to a static final-state on mobile.
- Lightweight: one graph lib + vanilla JS, no heavy framework; fast first paint.

## 5. The pipeline (how the artifact is produced)

- `tools/build_viewer_site.py`: run the eval on a **curated case set**, export each run's bundle (§2), assemble the static site → `viewer_site/` (the deployable folder). A `make viewer-site` target.
- Curated cases = the 2–4 that best show range (TEC showcase, abstention, buried-evidence).
- Output is committable and deployable as-is.

## 6. Scope & sequencing

- **Minimal (ships with the spike, = S4):** single case (TEC), step-through, basic coloring — proves the contract.
- **Polished (this spec, portfolio-layer):** multi-case selector, the reasoning side-panel, smooth transitions, the hostable static bundle. Build *after* the finding (A4) exists, since it replays real runs.
- Shares the data contract with the spike viewer — the polish is additive, not a rewrite.

## 7. Open choices

- **Layout:** fishbone vs radial vs layered DAG — pick by what reads cleanest as it grows. Lean: layered (symptom-left → hypotheses → evidence-right), which animates predictably.
- **Graph lib:** D3 (max control, more work) vs cytoscape.js / vis-network (faster, less bespoke). Lean: cytoscape.js unless the bespoke look needs D3.
- **Abstention case in the headline reel:** lean yes — honest uncertainty is a strength to show a test-architect audience.
