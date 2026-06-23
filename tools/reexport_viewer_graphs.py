#!/usr/bin/env python3
"""Offline re-export: enrich the frozen viewer bundles with the KPI-rooted causal subgraph.

The recorded runs in `viewer_site/case*.json` are a hard-won, nondeterministic capture (the verified
8/8 — e.g. case5's abstain). We must NOT re-run the controller to refresh them. This tool instead
**reads** each frozen bundle, deterministically regenerates only the case *graph* (`generate(fault,
mechanisms, seed)` + `bfs_subgraph` — both LLM-free), merges a `graph` block into the bundle, and
rewrites the static site (`case*.json` / `bundles.js` / `manifest.json` / `index.html`). Sub-second,
no model calls, frozen run data preserved.

    PYTHONPATH=src python tools/reexport_viewer_graphs.py            # all viewer_site/case*.json
    PYTHONPATH=src python tools/reexport_viewer_graphs.py --out viewer_site

Distinct from `build_viewer_site.py`, which runs `diagnose()` LIVE and would destroy the frozen 8/8.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dh.generator import generate  # noqa: E402
from dh.generator.cases import CASES_BY_ID  # noqa: E402
from dh.viewer.export import bfs_subgraph, build_site  # noqa: E402

# Difficulty-catalog one-liners — sourced from docs/handoff/worked_sut_example_lidar.md §"difficulty
# catalog" (markdown-only; no importable constant). Used to make the viewer's "what this shows" legible.
MECHANISMS = {
    "A2": "One reading moves two suspects at once — it raises one hypothesis while lowering another, "
          "so a single check has to be read in both directions.",
    "B5": "A sensor channel reports plausible-but-wrong values, so its readings can't be trusted on their "
          "own and must be cross-checked against an independent source.",
    "B6": "The channel that would reveal the cause is absent or silent — a blind spot you have to work around.",
    "C1": "The decisive evidence isn't obviously relevant; you only reach it by following a relationship "
          "link through the graph to it.",
    "C2": "The key fact is buried inside a document you've already found, and has to be dug out of its text.",
    "D1": "A recent, attention-grabbing event looks like the cause but isn't — the fault started before it, "
          "so it has to be ruled out by timing.",
    "D2": "The true cause happened earlier in time; lining things up instant-by-instant is misleading.",
    "D5": "You can't tell the suspects apart by eye — it takes an actual computation (a rate, residual, or "
          "threshold) to discriminate them.",
    "E1": "There is no single clean cause — the honest answer is that it's intermittent or coincidental, so "
          "the system should abstain rather than invent a culprit.",
}


def _node_refs(bundle: dict) -> tuple[str, ...]:
    """Every hypothesis node_ref across all recorded steps (the BFS must surface them all)."""
    refs = {h.get("node_ref") for step in bundle.get("steps", []) for h in step.get("hypotheses", [])}
    return tuple(sorted(r for r in refs if r))


def _explainer(spec, case) -> dict:
    """Eval-side 'what this example shows' metadata for the viewer panel: the difficulty mechanisms
    present (with descriptions), the case's purpose, and what makes it hard (decoys / demoted trigger)."""
    gt = case.ground_truth
    return {
        "purpose": spec.purpose,
        "answer_type": gt.answer_type,
        "mechanisms": [{"id": m, "desc": MECHANISMS.get(m, m)} for m in gt.mechanisms],
        "decoys": list(gt.decoys),
        "trigger": gt.trigger,
    }


def reexport(out_dir: pathlib.Path) -> list[dict]:
    bundles = []
    for path in sorted(out_dir.glob("case*.json")):
        bundle = json.loads(path.read_text())
        cid = bundle["case_id"]
        spec = CASES_BY_ID[cid]
        case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
        refs = _node_refs(bundle)
        graph = bfs_subgraph(case, node_refs=refs)

        ids = {n["id"] for n in graph["nodes"]}
        missing = [r for r in refs if r not in ids]
        if missing:  # fail loud — a node_ref with no node is a broken render
            sys.exit(f"{cid}: hypothesis node_refs not in emitted subgraph: {missing}")
        print(f"  {cid}: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges, "
              f"{len(refs)} hypothesis anchors all resolved", file=sys.stderr)

        bundle["graph"] = graph
        bundle["explainer"] = _explainer(spec, case)
        bundles.append(bundle)
    return bundles


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="viewer_site")
    args = ap.parse_args()
    out = pathlib.Path(__file__).resolve().parent.parent / args.out
    if not out.exists():
        sys.exit(f"no such dir: {out}")
    bundles = reexport(out)
    if not bundles:
        sys.exit(f"no case*.json found in {out}")
    index = build_site(bundles, out)
    print(f"\n# re-exported {len(bundles)} bundles (graph merged) -> {index}", file=sys.stderr)


if __name__ == "__main__":
    main()
