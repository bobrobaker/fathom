# Viewer / web front-end — dev guide

**Read this first for any work on the web viewer.** It pins the standing facts (architecture, data
contract, dev loop, gotchas) so a session doesn't re-derive them. The viewer is the portfolio showpiece:
a static, replay-only site that plays back recorded controller runs as an animated KPI-rooted causal graph.

## What the viewer is

- **Static + offline + replay-only.** It makes **zero LLM calls**. Everything it renders is a *recorded*
  run plus a deterministically-regenerated case graph. Hostable over `file://` or any static server.
- **Two view modes** (bottom toggle):
  - **Narrative reveal** (default) — progressive: only the KPI shows first; hypotheses appear as the run
    "discovers" them, the revealed subset re-balances its layout, edges tint with belief flowing to the KPI.
  - **Faithful (literal)** — every hypothesis seeded at triage (step 0), exactly as the controller runs it.
- **Honesty boundary (load-bearing).** Narrative mode *re-times real state* — it never fabricates a
  hypothesis, belief, or evidence the run didn't produce. Faking the *choreography* is sanctioned
  (alignment spec Q3); fabricating *state* is not. Keep that line bright in any reveal/animation change.

## Files

- `src/dh/viewer/site.html` — the entire viewer: HTML + CSS + D3 render JS in one file. This is the
  showpiece; `index.html` (in `src/dh/viewer/`) is the older thin spike viewer, not this.
- `src/dh/viewer/d3.v7.min.js` — vendored D3 (v7.9.0). Vendored, not CDN, so the site stays
  dependency-free over `file://`. `build_site` copies it into the output dir.
- `src/dh/viewer/export.py` — `bfs_subgraph(case)` (the KPI-rooted causal subgraph extractor),
  `case_bundle`, `build_site`, `ig_to_dict`. Eval-side, LLM-free.
- `tools/reexport_viewer_graphs.py` — **the offline refresh**: reads each frozen `viewer_site/case*.json`,
  regenerates only the case *graph* + `explainer` block, merges them in, rewrites the static site. No model
  calls. Run this after any `site.html` / `export.py` change to propagate into `viewer_site/`.
- `tools/gui_smoke.py` — headless Playwright smoke test + screenshot harness (regression gate).
- `viewer_site/` — the built, hostable site (tracked). `case{1..8}.json`, `bundles.js`, `manifest.json`,
  `index.html` (copied from `site.html`), `d3.v7.min.js`.

## Data contract (one bundle = one recorded run)

```
{ case_id, title, caption, symptom, trigger, root_cause, final_status, answer, eval_row,
  steps: [ { status, recommended_action, conflicts,
             hypotheses: [{id, label, node_ref, log_odds, confidence, status}],
             evidence:   [{id, summary, source}],
             links:      [{evidence_id, hypothesis_id, polarity, weight}] } ],
  trace: [ {action, args, voi, rationale, confidences:{hyp_id:conf}, leader, ...} ],   # aligned with steps
  graph:     { root, nodes:[{id,type,name,depth}], edges:[{src,dst,type}] },           # added by re-export
  explainer: { purpose, answer_type, mechanisms:[{id,desc}], decoys, trigger } }       # added by re-export
```

- Hypotheses anchor to graph nodes via `node_ref`. The viewer badges them `H1…H6` (`dispId`) so the
  rationale's hypothesis ids resolve visually.
- `graph` depth = backward-BFS distance from the KPI (drives the left→right layered layout).

## Dev loop

The `.venv` lives in the **main repo** (`/home/bolun/projects/fathom/.venv`), *not* the worktree
(gitignored). Run everything with the worktree's `src` on the path:

```bash
cd <worktree>
PYTHONPATH=src /home/bolun/projects/fathom/.venv/bin/python tools/reexport_viewer_graphs.py   # refresh
PYTHONPATH=src /home/bolun/projects/fathom/.venv/bin/python tools/gui_smoke.py                 # smoke + screenshots → /tmp/fathom_gui/
PYTHONPATH=src /home/bolun/projects/fathom/.venv/bin/python -m pytest tests/test_viewer.py -q  # unit gate
cd viewer_site && python3 -m http.server 8777                                                 # view at http://127.0.0.1:8777/
```

**Visual verification is the multiplier.** Drive Playwright headless against `viewer_site/index.html`,
screenshot, and read the image — that's how to confirm a render change actually looks right (not just
"no console errors"). `gui_smoke.py` is the pattern to copy; it also asserts the leader/abstain
distinction (case1/6 → 1 leader ring; case5 abstain → 0) and zero console errors.

## Gotchas (the ones that bit us)

- **NEVER run `tools/build_viewer_site.py` to "refresh."** It runs `diagnose()` LIVE and re-rolls the
  nondeterministic, hard-won 8/8 capture in `viewer_site/`. Use `reexport_viewer_graphs.py` (offline) instead.
- **D3 `.remove()` does NOT cancel in-flight transitions.** A `.on("end", loop)` recursion survives removal
  and leaks forever. Guard animation loops with a generation token (`pulseId`) and cancel queued timeouts
  (`introTimer`) on case/step/mode change.
- **Two transitions on the same selection cancel each other** unless *named*. The render uses
  `svg.transition("move")` (positions/opacity) and `svg.transition("color")` (fills/strokes); they must
  stay attribute-disjoint.
- **`pos` is rebuilt per render** (`pos={}`) holding only *visible* nodes in narrative mode. Every
  `pos[id]` deref must be guarded; node radius is type-based (`radius()`), never read from `pos`.
- **`buildReveal` connectivity invariant:** an ancestor's reveal step is the `min` over its descendants —
  this is what guarantees no floating nodes / no edges to pos-less nodes. Don't change `min` to first-write.
- **One subscription session limit** governs any live `claude -p` work; the viewer spike itself makes no
  LLM calls, so this only matters if you touch the live builder. Don't fan out agent fleets alongside a live eval.

## Per-session recipe

> Read `docs/viewer_dev.md`. Goal: <what you want>. Iterate visually (render + screenshot loop).

For mid-task pauses, `/handoff` on top captures in-flight state; this doc is the *standing* context.
