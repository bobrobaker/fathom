"""M0 gate (spec §3, build plan M0).

Every model round-trips through dict and JSON; `TypedGraph.neighbors()` and
`traverse()` work on a hand-built 4-node graph.
"""

import pytest

from dh.schemas import (
    Answer,
    Artifact,
    Case,
    Edge,
    EvidenceItem,
    EvidenceLink,
    GroundTruth,
    Hypothesis,
    InvestigationGraph,
    Node,
    TimeSeries,
    TypedGraph,
)


def _sample_typed_graph() -> TypedGraph:
    """4-node lidar-flavored graph: KPI <-measured_by- metric, KPI <-affects- subsystem,
    subsystem -part_of-> part_type."""
    return TypedGraph(
        nodes=[
            Node(id="kpi.range", type="KPI", name="effective range"),
            Node(id="metric.intensity", type="metric", name="return intensity"),
            Node(id="sub.detector", type="subsystem", name="detector"),
            Node(id="part.tec", type="part_type", name="TEC"),
        ],
        edges=[
            Edge(src="metric.intensity", dst="kpi.range", type="measured_by"),
            Edge(src="sub.detector", dst="kpi.range", type="affects", confidence=0.9),
            Edge(src="part.tec", dst="sub.detector", type="part_of"),
        ],
    )


# --- model instances exercising defaults + every field -----------------------

def _model_instances():
    g = _sample_typed_graph()
    node = g.nodes[0]
    edge = g.edges[0]
    ts = TimeSeries(signal="intensity", t=[0.0, 1.0], v=[1.0, 0.85],
                    spec={"min": 0.0, "max": 1.0, "units": "norm"})
    art = Artifact(id="tk.1", kind="ticket", text="range dropped",
                   source="alice", timestamp=10.0, valid_from=0.0, valid_to=20.0,
                   refs=["sub.detector"])
    gt = GroundTruth(
        answer_type="cause", root_cause="part.tec",
        causal_chain=["part.tec", "sub.detector", "kpi.range"],
        load_bearing_evidence=["ev.1"], decoys=["sub.laser"],
        conflicts=["sig.detector_temp"], trigger="ev.reboot",
        mechanisms=["D1", "B5"],
    )
    case = Case(id="case.tec", graph=g, telemetry=[ts], artifacts=[art],
                bom=_sample_typed_graph(), ground_truth=gt)
    hyp = Hypothesis(id="h.tec", label="TEC degradation", node_ref="part.tec",
                     log_odds=1.2, status="leading")
    ev = EvidenceItem(id="ev.1", summary="intensity tracks temp", source="temp_correlation_check",
                      props={"r": 0.9})
    link = EvidenceLink(evidence_id="ev.1", hypothesis_id="h.tec", polarity="+", weight=1.4)
    inner_ig = InvestigationGraph(symptom="range down 15%")
    ig = InvestigationGraph(
        symptom="range down 15%", hypotheses=[hyp], evidence=[ev], links=[link],
        conflicts=["sig.detector_temp"], recommended_action="swap-test TEC",
        status="concluded", snapshots=[inner_ig],
    )
    ans = Answer(
        answer_type="cause", root_cause="part.tec",
        causal_chain=["part.tec", "sub.detector", "kpi.range"],
        cited_evidence=["ev.1"], ruled_out=["sub.laser"], conflicts=["sig.detector_temp"],
        recommended_action="swap-test TEC", final_graph=ig,
    )
    return [node, edge, g, ts, art, gt, case, hyp, ev, link, ig, ans]


@pytest.mark.parametrize("model", _model_instances(), ids=lambda m: type(m).__name__)
def test_dict_round_trip(model):
    cls = type(model)
    assert cls.model_validate(model.model_dump()) == model


@pytest.mark.parametrize("model", _model_instances(), ids=lambda m: type(m).__name__)
def test_json_round_trip(model):
    cls = type(model)
    assert cls.model_validate_json(model.model_dump_json()) == model


def test_every_section3_model_covered():
    """Guard: if a model is added to §3, it must appear in the round-trip set."""
    covered = {type(m).__name__ for m in _model_instances()}
    expected = {
        "Node", "Edge", "TypedGraph", "TimeSeries", "Artifact", "GroundTruth",
        "Case", "Hypothesis", "EvidenceItem", "EvidenceLink",
        "InvestigationGraph", "Answer",
    }
    assert covered == expected


# --- graph helpers (M0 done-when) --------------------------------------------

def test_neighbors_out_any_type():
    g = _sample_typed_graph()
    nb = g.neighbors("sub.detector")  # default direction="out"
    assert [n.id for n in nb] == ["kpi.range"]


def test_neighbors_in_by_type():
    g = _sample_typed_graph()
    nb = g.neighbors("kpi.range", edge_type="measured_by", direction="in")
    assert [n.id for n in nb] == ["metric.intensity"]
    # affects edge into kpi.range is filtered out by edge_type
    nb_affects = g.neighbors("kpi.range", edge_type="affects", direction="in")
    assert [n.id for n in nb_affects] == ["sub.detector"]


def test_neighbors_empty_and_bad_direction():
    g = _sample_typed_graph()
    assert g.neighbors("part.tec", direction="in") == []  # nothing points at the TEC
    with pytest.raises(ValueError):
        g.neighbors("part.tec", direction="sideways")  # type: ignore[arg-type]


def test_traverse_multi_hop():
    g = _sample_typed_graph()
    # part.tec -part_of-> sub.detector, then no further part_of edges out of detector
    reached = g.traverse("part.tec", edge_type="part_of", direction="out")
    assert [n.id for n in reached] == ["sub.detector"]
    # reverse traversal of part_of from the KPI reaches nothing (no part_of into kpi)
    assert g.traverse("kpi.range", edge_type="part_of", direction="in") == []
