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
from dh.schemas import InvestigationGraph

_HTML = pathlib.Path(__file__).resolve().parent / "index.html"


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
    }


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
