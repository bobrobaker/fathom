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
    "A1": "Supporting and contradicting evidence pile up on the same suspect, so its standing is the net "
          "of the two — you can't just tally the readings that point at it.",
    "A2": "One reading moves two suspects at once — it raises one hypothesis while lowering another, "
          "so a single check has to be read in both directions.",
    "A3": "The decisive clue is a signal that should be present but isn't (aging would have driven the "
          "laser current up; it didn't) — so you reason from the absence, not from what's there.",
    "A4": "One upstream cause shows up as several independent-looking faults at once; the trap is to chase "
          "each symptom on its own instead of finding the single shared root behind them.",
    "A5": "Several redundant channels all agree, which feels reassuring — but one shared cause is skewing "
          "them together, so their agreement points to a common-mode fault, not to health.",
    "B1": "A maintenance ticket points at a config, but how much it counts depends on context: whether its "
          "date falls before or after a major hardware/software release flips it from damning to irrelevant.",
    "B5": "A sensor channel reports plausible-but-wrong values, so its readings can't be trusted on their "
          "own and must be cross-checked against an independent source.",
    "B6": "The channel that would reveal the cause is absent or silent — a blind spot you have to work around.",
    "C1": "The decisive evidence isn't obviously relevant; you only reach it by following a relationship "
          "link through the graph to it.",
    "C2": "The key fact is buried inside a document you've already found, and has to be dug out of its text.",
    "C3": "No single lookup gets the answer — the fact has to be chained across several hops "
          "(log → ticket → config → date → release boundary) before it means anything.",
    "C-spatial": "The fault has a spatial fingerprint — the intensity loss is clustered in one region of the "
          "field rather than spread evenly — so it's identified by where the degradation sits, not just how much.",
    "D1": "A recent, attention-grabbing event looks like the cause but isn't — the fault started before it, "
          "so it has to be ruled out by timing.",
    "D2": "The true cause happened earlier in time; lining things up instant-by-instant is misleading.",
    "D5": "You can't tell the suspects apart by eye — it takes an actual computation (a rate, residual, or "
          "threshold) to discriminate them.",
    "D6": "Two suspects are nearly symmetric and only one expensive check can break the tie, so the agent "
          "must weigh whether that discrimination is worth the cost — or abstain rather than overspend.",
    "E1": "There is no single clean cause — the honest answer is that it's intermittent or coincidental, so "
          "the system should abstain rather than invent a culprit.",
}


# Reasoning-challenge label per case — this is the TAB label now, so the strip reads as "8 kinds of hard
# reasoning" rather than "8 lidar faults". The lidar fault name (the domain content) is preserved in the
# "what this example shows" header. (case2's label is ours — the owner's list named the other seven.)
PATTERNS = {
    "case1": "Red-herring demotion",
    "case2": "Decoy fails to correlate",
    "case3": "Reason from absence",
    "case4": "Salient event is cause",
    "case5": "Abstain",
    "case6": "Buried evidence",
    "case7": "Tie-breaker",
    "case8": "Common-mode",
}

# Authored "what this example shows" body per case: a concrete elaboration (detail) + why it matters.
# The header/title (spec.purpose) STATES the point; these ELABORATE it without repeating — details,
# examples, and the stakes. (Abstention messaging is folded into the cases where it's relevant: case5 and
# the spend-or-abstain tie-breaker case7.)
CONTENT = {
    "case1": {
        "detail": "The range started slipping before the reboot, so timing alone clears the eye-catching "
                  "event. One sensor reads plausibly but wrongly and only counts once it's cross-checked, "
                  "and the remaining suspects look alike until a computed rate separates them.",
        "why": "Resisting the obvious recent event and the confident-but-wrong channel is what separates "
               "evidence-driven diagnosis from pattern-matching on recency.",
    },
    "case2": {
        "detail": "A thermal cause would track temperature, so the agent computes the correlation, finds "
                  "none, and uses that absence to rule the tempting decoy out. The laser itself carries "
                  "both supporting and contradicting evidence that has to be read as a net, not a tally.",
        "why": "Treating a missing-but-expected signal as real evidence is exactly the move shallow "
               "reasoning skips.",
    },
    "case3": {
        "detail": "Because the intensity loss is concentrated in one region rather than spread evenly, the "
                  "discriminator is where it occurs, not how much was lost. Causes like aging would have "
                  "moved other signals; their silence is what rules them out.",
        "why": "A clean spatial signature plus reasoning from what's absent is far harder than reading a "
               "single threshold.",
    },
    "case4": {
        "detail": "A maintenance ticket fingers a config edit, and its weight depends on whether its date "
                  "falls after a release boundary — a fact assembled across log → ticket → config → date. "
                  "Here, unlike the trigger cases, demoting the recent change would be the mistake.",
        "why": "It proves the agent weighs recent events on the evidence instead of reflexively dismissing "
               "them, so a genuine recent cause still gets caught.",
    },
    "case5": {
        "detail": "The symptom looks like a fault, but the readings are intermittent and never converge — "
                  "no hypothesis clears the confidence bar. When the evidence doesn't single out one cause, "
                  "the agent says so instead of guessing.",
        "why": "A confident wrong diagnosis is worse than an honest “no clean cause,” and "
               "calibrated abstention is what makes the confident answers trustworthy.",
    },
    "case6": {
        "detail": "Nothing on the surface implicates the detector; the agent follows a relationship link to "
                  "an artifact that doesn't look relevant, then extracts the deciding fact buried inside "
                  "its text.",
        "why": "Much of real diagnosis is retrieval — the answer exists but has to be navigated to, not "
               "recalled from what's already in view.",
    },
    "case7": {
        "detail": "Cheaper evidence leaves the two suspects balanced, so the agent has to judge whether the "
                  "costly discriminating check is worth it — and abstain rather than overspend or guess "
                  "when it isn't.",
        "why": "Deciding when one more measurement pays for itself, and when to stop, is the "
               "value-of-information call at the heart of the system.",
    },
    "case8": {
        "detail": "Several channels sag together, reading either as multiple independent faults or as "
                  "reassuring agreement — but a single shared supply is driving them all. The tell is a "
                  "common onset across channels, traced upstream instead of debugged one at a time.",
        "why": "Shared-cause failures defeat redundancy and fool naive monitoring, so finding the one root "
               "behind many symptoms is the whole point of structured causal reasoning.",
    },
}


def _node_refs(bundle: dict) -> tuple[str, ...]:
    """Every hypothesis node_ref across all recorded steps (the BFS must surface them all)."""
    refs = {h.get("node_ref") for step in bundle.get("steps", []) for h in step.get("hypotheses", [])}
    return tuple(sorted(r for r in refs if r))


def _explainer(spec, case) -> dict:
    """Eval-side 'what this example shows' metadata for the viewer panel: the difficulty mechanisms
    present (with descriptions), the case's purpose, and what makes it hard (decoys / demoted trigger)."""
    gt = case.ground_truth
    # The viewer must NEVER render a bare internal catalog id (A4/A5/C-spatial …) in "what this example
    # shows" — those are doc-internal references. Fail loud if a mechanism has no plain-English description.
    missing = [m for m in gt.mechanisms if m not in MECHANISMS]
    if missing:
        raise ValueError(
            f"{spec.id}: difficulty mechanism(s) {missing} have no plain-English description in MECHANISMS "
            f"(tools/reexport_viewer_graphs.py). Add one before re-export — the viewer must not show a raw "
            f"catalog id to a reader.")
    if spec.id not in PATTERNS:
        raise ValueError(
            f"{spec.id}: no reasoning-challenge label in PATTERNS (tools/reexport_viewer_graphs.py). Add "
            f"one — it is the tab label.")
    if spec.id not in CONTENT:
        raise ValueError(
            f"{spec.id}: no authored 'what this example shows' body in CONTENT "
            f"(tools/reexport_viewer_graphs.py). Add a {{detail, why}} pair.")
    return {
        "purpose": spec.purpose,
        "answer_type": gt.answer_type,
        "pattern": PATTERNS[spec.id],
        "detail": CONTENT[spec.id]["detail"],
        "why": CONTENT[spec.id]["why"],
        "mechanisms": [{"id": m, "desc": MECHANISMS[m]} for m in gt.mechanisms],
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
