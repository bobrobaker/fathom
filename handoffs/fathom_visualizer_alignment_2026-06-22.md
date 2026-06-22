# Fathom visualizer — aligned model (2026-06-22)

**Status:** alignment artifact from a `/grill-me` pass. Refines `handoffs/fathom_visualizer_spec.md`
§3–§4 — replaces the flat *symptom → hypotheses → evidence* columns with a **KPI-rooted causal-graph**
view. Pending sign-off → fold the load-bearing bits into the spec + drop a `docs/decisions/` record.

## Task as understood

Re-render the Investigation Graph viewer so it shows the controller's actual reasoning substrate:
the **backward-BFS causal subgraph rooted at the KPI**, fault hypotheses anchored to their real graph
nodes, evidence attached where it bears, support/refutation **flowing through the structure**, and a
staged reveal that makes the diagnosis feel like it unfolds. **Viewer + export only; controller untouched.**

## Grounding — how the controller actually works (verified in code)

- Symptom/KPI → `_seed_candidates` (`loop.py`): **backward BFS over `affects` edges** from the KPI
  → subsystems, drilled into `part_type`s via `part_of`.
- `seed_hypotheses` (`llm.py`): the LLM selects fault hypotheses from that candidate set; each
  `node_ref`'s the implicated subsystem/part.
- All hypotheses are seeded at **triage (step 0)**; the action loop then gathers evidence and updates beliefs.
- ⇒ The KPI → subsystem → cause hierarchy is **real graph topology**, not authored for the viz. The
  viewer simply wasn't rendering it, and `export.py` doesn't emit it yet.

## Goals

- The **causal map** (BFS subgraph) is the backbone.
- Hypotheses are graph **nodes lit up**; the rest of the candidate map is **dim context** (so "other
  possible hypotheses" are visibly present).
- Evidence **attaches to its node**; lines flow through the graph.
- Belief **flows visibly up the headline causal path** to the KPI.
- Evidence lines are **pruned and strength-weighted** (dominant + relevant opposing).
- Staged reveal animation.

## Non-goals

- No controller behavior change (no genuine progressive hypothesis generation — it's faked in the viewer).
- Not every edge animates flow — **headline path only**.
- Not all 8 cases in the reel — **curated 3**.
- No live LLM in browser — replay-only stays.

## Decisions (firm)

| # | Decision |
|---|----------|
| Q1 | Viewer + export only; controller untouched (protects the verified 8/8). |
| Q2 | Evidence attaches to the node it bears on (not a separate column). |
| Q3 | Faking controller choreography in the viewer is allowed. |
| Q4 | Evidence lines: dominant association **+ relevant opposing side**; opacity/width **∝ \|weight\|**; below-relevance dropped. |
| Q5 | Edge flow: **(b) animated propagation** on the headline path (implicated node → KPI); **(a) static** elsewhere. |
| Q6 | Draw the **full BFS map**; hypothesis nodes are colored/live, non-hypothesis candidates dim. |
| Q7 | *(tentative)* Choreography: KPI → BFS expands depth-by-depth → hypotheses take initial color → per step: action → evidence attaches → lines draw after a beat → recolor + flow-pulse up the headline path. |

## Defaults adopted (tentative unless noted)

- **Layout:** layered DAG, KPI-rooted, depth = BFS distance (left → right).
- **Graph lib:** D3 — render-layer rewrite; max control for bespoke layered animation. *(firm — chosen earlier.)*
- **Curated reel:** case1 (TEC), case5 (abstain), case6 (buried). *(firm.)*
- **Trigger** node rendered distinctly; **abstention** rendered honestly (no false winner).

## Open — deferred to implementation / post-first-look

- **Q7 timing is tentative** — expect iteration after the first case1 render.
- **Decluttering large subgraphs** (case8-scale, ~many nodes) — dim/collapse strategy TBD.
- Whether dim candidate nodes need labels or just shapes.

## Enabling change (required first) — re-export, NOT re-run

The viewer needs the **BFS subgraph** — nodes (`id`, `type`, `name`, depth-from-KPI), the `affects`
+ `part_of` edges among candidates, and the `hypothesis → node_ref` map — which the current bundles
don't carry. **This data is deterministic and LLM-free** (`generate(case, seed=…)` + `_seed_candidates`),
so we do **not** re-run the controller. Instead, export **reads the already-recorded run** (frozen
hypotheses / evidence / beliefs / snapshots / trace — the verified 8/8) and **merges** the
freshly-regenerated case graph into it.

Rationale: the runs are nondeterministic; re-running risks losing the clean 8/8 capture (e.g. case5's
hard-won abstain). Freeze the runs; enrich only the visuals. **Net effect: after the viewer work, a
refresh is a sub-second offline re-export, not a ~15-min live build.**

## What's reasonable for the spike (proposed scope)

**Tier 1 — MUST (the new model's core; the differentiators):**
1. Export the BFS subgraph (enabling change).
2. Render the KPI-rooted layered causal graph; hypotheses anchored to real nodes; non-hypothesis
   candidates dim (Q6).
3. Evidence attached to its node (Q2).
4. Pruned, strength-weighted evidence lines, opposing side shown (Q4).
5. Reuse the existing step/scrub controls, reasoning side-panel, case selector, header.

**Tier 2 — SHOULD (high polish payoff, moderate cost):**
6. Q7 staged choreography (BFS-expand → per-step evidence).
7. Q5 flow-pulse on the headline path only.

**Tier 3 — DEFER (cost > spike payoff):**
- Flow animation on all edges (scoped out — headline only).
- Progressive hypothesis *generation* feel during the step phase (keep all-at-map-draw for now).
- Mobile graceful-degradation polish; full transition interpolation everywhere.
- Expanding the reel beyond the curated 3.

**Build order (spine-first):** vertical slice on **case1 (TEC)** end-to-end (Tier 1 + 2) → react →
generalize to case5 (abstain) + case6 (buried). The main cost is the **D3 render-layer rewrite**; the
CSS shell, controls, and side-panel largely survive.

**Risk flags:** (i) layered layout of a KPI-rooted DAG that animates predictably — lean layered,
left→right by depth; (ii) some subgraphs are large (case8 ran 295k tokens / many nodes) — needs the
declutter strategy before those cases enter the reel; (iii) Q7 timing is a guess until seen.
