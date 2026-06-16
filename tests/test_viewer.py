"""M9 gate (spec §9 S4, build plan M9).

The exporter turns an IG with snapshots into the viewer's step model and writes the
static bundle; steps grow and recolor; the demoted trigger is annotated distinctly.
"""

import json

from dh.controller.beliefs import sigmoid
from dh.schemas import EvidenceItem, EvidenceLink, Hypothesis, InvestigationGraph
from dh.viewer.export import export_viewer, ig_to_dict


def _ig_with_snapshots() -> InvestigationGraph:
    h_tec = Hypothesis(id="h.tec", label="TEC degradation", node_ref="part.tec", log_odds=1.2)
    h_laser = Hypothesis(id="h.laser", label="laser aging", node_ref="part.laser_module",
                         log_odds=-0.4)
    s0 = InvestigationGraph(symptom="range down", hypotheses=[h_tec, h_laser])
    s1 = InvestigationGraph(symptom="range down", hypotheses=[h_tec, h_laser],
                            evidence=[EvidenceItem(id="ev.tec", summary="TEC 91%",
                                                   source="tec_load_check")],
                            links=[EvidenceLink(evidence_id="ev.tec", hypothesis_id="h.tec",
                                                polarity="+", weight=1.2)],
                            conflicts=["log.reboot"], status="concluded")
    return InvestigationGraph(symptom="range down", hypotheses=[h_tec, h_laser],
                              evidence=s1.evidence, links=s1.links, conflicts=["log.reboot"],
                              status="concluded", snapshots=[s0, s1])


def test_ig_to_dict_structure():
    data = ig_to_dict(_ig_with_snapshots(), trigger="log.reboot", root_cause="part.tec")
    assert data["symptom"] == "range down"
    assert data["trigger"] == "log.reboot" and data["root_cause"] == "part.tec"
    assert len(data["steps"]) == 2
    # confidence is sigmoid(log_odds) and within [0,1]
    h = data["steps"][1]["hypotheses"][0]
    assert h["confidence"] == round(sigmoid(1.2), 3)  # exported at 3 dp
    assert all(0.0 <= hp["confidence"] <= 1.0 for s in data["steps"] for hp in s["hypotheses"])


def test_steps_grow():
    data = ig_to_dict(_ig_with_snapshots())
    ev_counts = [len(s["evidence"]) for s in data["steps"]]
    assert ev_counts == [0, 1]  # the graph grows across steps


def test_export_writes_static_bundle(tmp_path):
    out = export_viewer(_ig_with_snapshots(), tmp_path, trigger="log.reboot")
    assert out.name == "index.html" and out.exists()
    assert (tmp_path / "ig.json").exists()
    js = (tmp_path / "ig_data.js").read_text()
    assert js.startswith("window.IG_DATA =")
    # the js payload is valid JSON after stripping the assignment
    payload = js[len("window.IG_DATA ="):].rstrip().rstrip(";")
    assert json.loads(payload)["trigger"] == "log.reboot"
    html = (tmp_path / "index.html").read_text()
    assert "IG_DATA" in html and "<svg" in html  # self-contained, no CDN
    assert "http://" not in html.replace('"http://www.w3.org/2000/svg"', "")  # no external deps
