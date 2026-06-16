"""Compose a fault's telemetry into a full `Case` (spec §5).

Builds the constant lidar topology (subsystems, parts, metrics, KPI, config), then
layers on the fault-specific corpus (logbook, error log, docs, diagnostic actions),
the BOM, and the hidden ground truth. Corpus items are emitted twice — as graph
`Node`s (for traversal) and as `Artifact`s (for search/read) sharing one id, which
is the join key between the navigation graph and the retrievable text.
"""

from __future__ import annotations

import random

from dh.generator import faults
from dh.generator.faults import CorpusItem
from dh.schemas import (
    Artifact,
    Case,
    Edge,
    GroundTruth,
    Node,
    TypedGraph,
)

# Metric node id → the telemetry signal it reads (props.signal join, §3.1).
_METRICS = {
    "metric.intensity": "mean_return_intensity",
    "metric.diode_temp": "laser_diode_temp_C",
    "metric.tec_current": "tec_current_A",
    "metric.detector_temp": "detector_temp_C",
    "metric.laser_power": "laser_power_mW",
    "metric.dark_count": "dark_count_rate",
    "metric.ambient": "ambient_temp_C",
}

_SUBSYSTEMS = {
    "sub.thermal": "Thermal / TEC",
    "sub.laser": "Laser emitter",
    "sub.detector": "Receiver / detector",
    "sub.optics": "Optics / window",
    "sub.calibration": "Signal proc / calibration",
    "sub.power": "Scanner / power",
}

_PARTS = {  # part_type → its subsystem (part_of, BOM)
    "part.tec": ("TEC module", "sub.thermal"),
    "part.laser_module": ("Laser module", "sub.laser"),
    "part.detector": ("Detector", "sub.detector"),
    "part.window": ("Window", "sub.optics"),
}


def _base_topology() -> tuple[list[Node], list[Edge]]:
    """The constant lidar SUT graph: subsystems, parts, metrics, KPI, config."""
    nodes: list[Node] = []
    edges: list[Edge] = []

    for nid, name in _SUBSYSTEMS.items():
        nodes.append(Node(id=nid, type="subsystem", name=name))
    for nid, (name, sub) in _PARTS.items():
        nodes.append(Node(id=nid, type="part_type", name=name))
        edges.append(Edge(src=nid, dst=sub, type="part_of"))
    # one part_version to exercise version_of (BOM)
    nodes.append(Node(id="part.tec.revB", type="part_version", name="TEC module rev B"))
    edges.append(Edge(src="part.tec.revB", dst="part.tec", type="version_of"))

    for nid, signal in _METRICS.items():
        nodes.append(Node(id=nid, type="metric", name=signal, props={"signal": signal}))
    nodes.append(Node(id="kpi.effective_range", type="KPI", name="effective_max_range_m",
                      props={"signal": "effective_max_range_m",
                             "symptom": "Effective maximum range has degraded ~8% over the "
                                        "past week (about 110 m vs a 120 m baseline). "
                                        "Diagnose the root cause."}))

    # config store — baseline values (a fault may diverge one via FaultFacts.config_changes).
    # Each config item part_of its owning subsystem: a config change then falls inside that
    # subsystem's cause-equivalence family (eval §8.1), so blaming the changed key counts as
    # localizing the subsystem fault — the calibration case (#4) leans on this.
    config = {  # id: (name, baseline_value, owning_subsystem)
        "config.cal_table_version": ("cal_table_version", "v12", "sub.calibration"),
        "config.firmware_version": ("firmware_version", "3.4.1", "sub.calibration"),
        "config.tec_setpoint_C": ("tec_setpoint_C", 25.0, "sub.thermal"),
        "config.scan_params": ("scan_params", "raster_default", "sub.power"),
    }
    for nid, (name, val, sub) in config.items():
        nodes.append(Node(id=nid, type="config", name=name,
                          props={"value": val, "baseline": val}))
        edges.append(Edge(src=nid, dst=sub, type="part_of"))

    # measured_by: subsystem/KPI ← metric
    measured = [
        ("sub.thermal", "metric.diode_temp"), ("sub.thermal", "metric.tec_current"),
        ("sub.laser", "metric.laser_power"), ("sub.detector", "metric.detector_temp"),
        ("sub.detector", "metric.dark_count"),
    ]
    for sub, metric in measured:
        edges.append(Edge(src=sub, dst=metric, type="measured_by"))

    # affects: the coupling topology (§1.2) — range is reachable from ≥4 subsystems
    affects = [
        ("sub.thermal", "sub.laser"), ("sub.thermal", "sub.detector"),
        ("sub.laser", "metric.intensity"), ("sub.optics", "metric.intensity"),
        ("sub.detector", "metric.intensity"), ("metric.intensity", "kpi.effective_range"),
        ("sub.calibration", "kpi.effective_range"), ("sub.power", "sub.thermal"),
    ]
    for src, dst in affects:
        edges.append(Edge(src=src, dst=dst, type="affects"))

    return nodes, edges


def _shared_corpus() -> list[CorpusItem]:
    """The structural range-degradation corpus carried by *every* case: domain docs, the
    playbook, prior-incident reports (case-based anchors about *other* units, so they never
    contradict the current fault), generic logbook, and the recommended swap-test. Anything
    whose truth depends on the injected fault is a per-fault `FaultFacts.corpus` item, not here."""
    return [
        CorpusItem("doc.system_model", "doc", node_type="domain_doc",
                   name="Lidar thermal-optical model",
                   text="System model: the Thermal -> Laser -> return-intensity -> effective-range "
                        "chain. Rule: laser optical output falls as the diode temperature rises above "
                        "its setpoint. Detector dark-count rises with detector temperature, lowering SNR.",
                   refs=[("sub.thermal", "references"), ("sub.laser", "references"),
                         ("metric.intensity", "references")]),
        CorpusItem("doc.playbook", "procedure", node_type="procedure",
                   name="Diagnosing range degradation",
                   text="Playbook: when effective range degrades, work the differential "
                        "{window contamination, detector drift, laser aging, thermal/TEC, calibration "
                        "drift}. Cheap eliminations first: config_diff (calibration/firmware), "
                        "spatial_intensity_check (window). Discriminate laser aging vs thermal with "
                        "temp_correlation_check and tec_load_check. Check channel_sanity_check for stuck "
                        "sensors and onset_vs_event_check to order onset against recent events.",
                   refs=[("kpi.effective_range", "references")]),
        CorpusItem("report.prior_tec", "report", node_type="report",
                   name="Prior incident: TEC degradation",
                   text="Six months ago a unit showed range loss with intensity tracking diode "
                        "temperature and TEC current near its limit; root cause was a degraded TEC "
                        "module. Same signature.",
                   refs=[("sub.thermal", "concluded"), ("part.tec", "references")]),
        CorpusItem("report.prior_laser", "report", node_type="report",
                   name="Prior incident: laser power aging",
                   text="A separate unit lost range from laser power aging: optical output fell but "
                        "diode temperature stayed nominal and intensity did NOT correlate with temperature.",
                   refs=[("sub.laser", "concluded"), ("part.laser_module", "references")]),
        CorpusItem("log.service", "logbook_entry", node_type="logbook_entry",
                   name="Last thermal-subsystem service",
                   text="Last service of the thermal subsystem (TEC module inspected, no action).",
                   refs=[("sub.thermal", "references")], timestamp=faults.SERVICE_T),
        CorpusItem("act.swap_test", "diagnostic_action", node_type="diagnostic_action",
                   name="Laser-module swap-test (not tried)",
                   text="Recommended-but-untried: swap the laser module to cleanly isolate laser aging "
                        "from a thermal cause before ordering parts. High value of information.",
                   refs=[("sub.laser", "references"), ("sub.thermal", "references")],
                   props={"tried": False}),
    ]


def _emit_corpus(items: list[CorpusItem]) -> tuple[list[Node], list[Edge], list[Artifact]]:
    """Emit each corpus item twice — a graph `Node` (if `node_type`) + an `Artifact` sharing
    its id, the join key between navigation and retrieval. `node_type is None` ⇒ artifact only."""
    nodes: list[Node] = []
    edges: list[Edge] = []
    artifacts: list[Artifact] = []
    for it in items:
        if it.node_type is not None:
            nodes.append(Node(id=it.id, type=it.node_type, name=it.name or it.id, props=it.props))
            for dst, etype in it.refs:
                edges.append(Edge(src=it.id, dst=dst, type=etype))
        artifacts.append(Artifact(id=it.id, kind=it.kind, text=it.text, source=it.source,
                                  timestamp=it.timestamp, refs=[dst for dst, _ in it.refs]))
    return nodes, edges, artifacts


def _build_corpus(facts) -> tuple[list[Node], list[Edge], list[Artifact]]:
    """Shared structural corpus + this fault's per-fault delta (`facts.corpus`, spec §5)."""
    return _emit_corpus(_shared_corpus() + facts.corpus)


def _build_bom() -> TypedGraph:
    """The part_of / version_of subgraph (shares node ids with the main graph)."""
    nodes = [Node(id="part.tec.revB", type="part_version", name="TEC module rev B")]
    edges = [Edge(src="part.tec.revB", dst="part.tec", type="version_of")]
    for nid, (name, sub) in _PARTS.items():
        nodes.append(Node(id=nid, type="part_type", name=name))
        nodes.append(Node(id=sub, type="subsystem", name=_SUBSYSTEMS[sub]))
        edges.append(Edge(src=nid, dst=sub, type="part_of"))
    # de-dup subsystem nodes (a subsystem hosts several parts)
    seen: set[str] = set()
    uniq = [n for n in nodes if not (n.id in seen or seen.add(n.id))]
    return TypedGraph(nodes=uniq, edges=edges)


def build_case(fault: str, mechanisms: list[str], seed: int = 0) -> Case:
    """Deterministically assemble a labelled `Case` for `fault` (spec §5.1)."""
    if fault not in faults.FAULTS:
        raise ValueError(f"unknown fault {fault!r}; known: {sorted(faults.FAULTS)}")
    rng = random.Random(seed)

    telemetry, fct = faults.FAULTS[fault](rng)
    base_nodes, base_edges = _base_topology()
    if fct.symptom:  # fault-specific symptom overrides the default range-degradation text
        for n in base_nodes:
            if n.type == "KPI":
                n.props["symptom"] = fct.symptom
    if fct.config_changes:  # a real post-release config change (value diverges from baseline)
        for n in base_nodes:
            if n.id in fct.config_changes:
                n.props["value"] = fct.config_changes[n.id]
    corpus_nodes, corpus_edges, artifacts = _build_corpus(fct)

    graph = TypedGraph(nodes=base_nodes + corpus_nodes, edges=base_edges + corpus_edges)
    ground_truth = GroundTruth(
        answer_type=fct.answer_type,
        root_cause=fct.root_cause,
        causal_chain=fct.causal_chain,
        load_bearing_evidence=fct.load_bearing_evidence,
        decoys=fct.decoys,
        conflicts=fct.conflicts,
        trigger=fct.trigger,
        mechanisms=list(mechanisms),
    )
    return Case(
        id=f"case.{fault}",
        graph=graph,
        telemetry=telemetry,
        artifacts=artifacts,
        bom=_build_bom(),
        ground_truth=ground_truth,
    )
