"""Export the Investigation Graph (+ per-step snapshots) for the viewer (spec §9 S4).

The IG is the single source of truth: the controller writes it, the eval reads it, and
this turns it into `ig_data.js` (+ `ig.json`) for the static `index.html`. Each snapshot
becomes one viewer "step", carrying hypotheses (with confidence = sigmoid(log-odds)),
evidence, polarity-signed links, and conflicts. `trigger`/`root_cause` are optional
eval-side annotations (NOT controller context) so the demoted trigger renders distinctly.
"""

from __future__ import annotations

import json
import pathlib
import shutil

from dh.controller.beliefs import sigmoid
from dh.schemas import Case, InvestigationGraph

_HTML = pathlib.Path(__file__).resolve().parent / "index.html"        # the spike viewer (S4)
_SITE_HTML = pathlib.Path(__file__).resolve().parent / "site.html"    # the polished showpiece
_D3 = pathlib.Path(__file__).resolve().parent / "d3.v7.min.js"        # vendored — site loads over file://

# Node types kept as drillable parts under a subsystem (mirrors loop.py::_seed_candidates: configs
# are excluded — they part_of a subsystem too but aren't the diagnostic parts the BFS surfaces).
_PART_TYPES = ("part_type", "part_version")
# Node types the backward-affects BFS records as candidate subsystems (loop.py::_seed_candidates).
_SUBSYSTEM_TYPES = ("subsystem", "part_type")
_BFS_DEPTH = 5  # depth bound, identical to _seed_candidates


def bfs_subgraph(case: Case, *, node_refs: tuple[str, ...] = ()) -> dict:
    """The KPI-rooted backward-causal subgraph the viewer renders (alignment spec "Enabling change").

    Mirrors `loop.py::_seed_candidates` — backward BFS over `affects` from the KPI to subsystems,
    drilled into part_types via `part_of` — but, unlike that helper (which flattens to a candidate
    list with no edges/depth), captures the **edges** (`affects`, `part_of`) and **depth-from-KPI**
    the layered DAG layout needs. Eval-side and LLM-free: reads `case.graph` directly (the export
    already consumes `case.ground_truth`), so it's deterministic for a given (fault, seed).

    `node_refs` (the recorded hypotheses' node_refs) are guaranteed present as nodes — a hypothesis
    anchored at part/config granularity the plain BFS skips (e.g. a config root cause) is pulled in
    along its real outgoing edge, so every bundle node_ref resolves to a rendered node.
    """
    g = case.graph
    by_id = {n.id: n for n in g.nodes}
    affects_in: dict[str, list[str]] = {}
    part_in: dict[str, list[str]] = {}
    for e in g.edges:
        if e.type == "affects":
            affects_in.setdefault(e.dst, []).append(e.src)
        elif e.type == "part_of":
            part_in.setdefault(e.dst, []).append(e.src)

    # The symptom anchors to a KPI (mirrors LidarEnvironment.symptom_node_id); any KPI is the fallback.
    root = next((n.id for n in g.nodes if n.type == "KPI" and "symptom" in n.props), None)
    if root is None:
        root = next((n.id for n in g.nodes if n.type == "KPI"), None)
    if root is None:
        raise KeyError("no KPI node to root the subgraph")

    depth = {root: 0}
    edges: dict[tuple[str, str, str], None] = {}  # ordered set
    frontier = [root]
    for d in range(1, _BFS_DEPTH + 1):  # backward-affects BFS
        nxt = []
        for nid in frontier:
            for src in affects_in.get(nid, []):
                edges[(src, nid, "affects")] = None
                if src not in depth:
                    depth[src] = d
                    nxt.append(src)
        frontier = nxt
        if not frontier:
            break

    # Drill each candidate subsystem into its parts (snapshot `depth` first so freshly-added parts,
    # which have no part_of children of their own, aren't themselves drilled).
    for sid in [i for i in list(depth) if by_id[i].type in _SUBSYSTEM_TYPES]:
        for pid in part_in.get(sid, []):
            if by_id.get(pid) and by_id[pid].type in _PART_TYPES:
                edges[(pid, sid, "part_of")] = None
                depth.setdefault(pid, depth[sid] + 1)

    for ref in node_refs:  # guarantee every recorded hypothesis anchor resolves to a node
        if not ref or ref in depth or ref not in by_id:
            continue
        attached = next(((e.dst, e.type) for e in g.edges
                         if e.src == ref and e.dst in depth and e.type in ("affects", "part_of")), None)
        if attached:
            dst, etype = attached
            edges[(ref, dst, etype)] = None
            depth[ref] = depth[dst] + 1
        else:
            depth[ref] = max(depth.values()) + 1

    return {
        "root": root,
        "nodes": [{"id": i, "type": by_id[i].type, "name": by_id[i].name, "depth": depth[i]}
                  for i in depth],
        "edges": [{"src": s, "dst": t, "type": ty} for (s, t, ty) in edges],
    }


def _step_dict(ig: InvestigationGraph) -> dict:
    return {
        "status": ig.status,
        "recommended_action": ig.recommended_action,
        "conflicts": list(ig.conflicts),
        "hypotheses": [
            {"id": h.id, "label": h.label, "node_ref": h.node_ref,
             "log_odds": round(h.log_odds, 3), "confidence": round(sigmoid(h.log_odds), 3),
             "status": h.status}
            for h in ig.hypotheses
        ],
        "evidence": [{"id": e.id, "summary": e.summary, "source": e.source} for e in ig.evidence],
        "links": [
            {"evidence_id": l.evidence_id, "hypothesis_id": l.hypothesis_id,
             "polarity": l.polarity, "weight": round(l.weight, 3)}
            for l in ig.links
        ],
    }


def ig_to_dict(ig: InvestigationGraph, trigger: str | None = None,
               root_cause: str | None = None) -> dict:
    """Serialize an IG and its snapshots into the viewer's step model."""
    steps = ig.snapshots if ig.snapshots else [ig]
    return {
        "symptom": ig.symptom,
        "trigger": trigger,
        "root_cause": root_cause,
        "final_status": ig.status,
        "steps": [_step_dict(s) for s in steps],
        "trace": list(ig.trace),  # per-step action / VOI / deltas, aligned with steps
    }


def case_bundle(ig: InvestigationGraph, *, case_id: str, title: str, caption: str,
                trigger: str | None = None, root_cause: str | None = None,
                answer: dict | None = None, eval_row: dict | None = None) -> dict:
    """The full replay bundle for one recorded run (fathom_visualizer_spec §2): the stepped IG +
    per-step trace, a ground-truth-free header, the final answer, and the case's eval row. The
    `trigger`/`root_cause` are eval-side annotations for rendering, never controller context."""
    d = ig_to_dict(ig, trigger=trigger, root_cause=root_cause)
    d.update({"case_id": case_id, "title": title, "caption": caption,
              "answer": answer or {}, "eval_row": eval_row or {}})
    return d


def build_site(bundles: list[dict], out_dir: str | pathlib.Path) -> pathlib.Path:
    """Assemble the hostable static site: one `<case_id>.json` per bundle, a `manifest.json`
    listing them, `bundles.js` (so it loads over file:// without a server), and `index.html`."""
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for b in bundles:
        (out / f"{b['case_id']}.json").write_text(json.dumps(b, indent=2))
        manifest.append({"case_id": b["case_id"], "title": b.get("title", b["case_id"]),
                         "caption": b.get("caption", ""),
                         "final_status": b.get("final_status", "")})
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (out / "bundles.js").write_text(
        "window.FATHOM_BUNDLES = " + json.dumps({b["case_id"]: b for b in bundles}, indent=2)
        + ";\nwindow.FATHOM_MANIFEST = " + json.dumps(manifest, indent=2) + ";\n")
    shutil.copyfile(_SITE_HTML, out / "index.html")
    shutil.copyfile(_D3, out / _D3.name)  # vendored D3 — keeps the site dependency-free over file://
    return out / "index.html"


def export_viewer(ig: InvestigationGraph, out_dir: str | pathlib.Path,
                  trigger: str | None = None, root_cause: str | None = None) -> pathlib.Path:
    """Write `ig.json`, `ig_data.js`, and a copy of `index.html` into `out_dir`.

    `ig_data.js` (a `window.IG_DATA = …` assignment) is what lets `index.html` load
    over `file://` without a server — fetch() of a sibling JSON is CORS-blocked there.
    """
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = ig_to_dict(ig, trigger=trigger, root_cause=root_cause)
    blob = json.dumps(data, indent=2)
    (out / "ig.json").write_text(blob)
    (out / "ig_data.js").write_text(f"window.IG_DATA = {blob};\n")
    shutil.copyfile(_HTML, out / "index.html")
    return out / "index.html"
