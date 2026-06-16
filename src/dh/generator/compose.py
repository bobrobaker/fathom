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

    # config store — all unchanged for case #1 (rules out calibration/firmware/setpoint)
    config = {
        "config.cal_table_version": ("cal_table_version", "v12"),
        "config.firmware_version": ("firmware_version", "3.4.1"),
        "config.tec_setpoint_C": ("tec_setpoint_C", 25.0),
        "config.scan_params": ("scan_params", "raster_default"),
    }
    for nid, (name, val) in config.items():
        nodes.append(Node(id=nid, type="config", name=name,
                          props={"value": val, "baseline": val}))

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


def _build_corpus(facts) -> tuple[list[Node], list[Edge], list[Artifact]]:
    """Shared range-degradation corpus (docs, prior reports, logbook, diagnostic actions);
    the error-log entry is fault-specific (only present when the fault injects one)."""
    # (id, node_type, name, artifact_kind, text, edges_out[(dst,type)], extra_artifact_kw)
    items = [
        ("doc.system_model", "domain_doc", "Lidar thermal-optical model", "doc",
         "System model: the Thermal -> Laser -> return-intensity -> effective-range chain. "
         "Rule: laser optical output falls as the diode temperature rises above its setpoint. "
         "Detector dark-count rises with detector temperature, lowering SNR.",
         [("sub.thermal", "references"), ("sub.laser", "references"),
          ("metric.intensity", "references")], {}),
        ("doc.playbook", "procedure", "Diagnosing range degradation", "procedure",
         "Playbook: when effective range degrades, work the differential "
         "{window contamination, detector drift, laser aging, thermal/TEC, calibration drift}. "
         "Cheap eliminations first: config_diff (calibration/firmware), spatial_intensity_check "
         "(window). Discriminate laser aging vs thermal with temp_correlation_check and "
         "tec_load_check. Check channel_sanity_check for stuck sensors and onset_vs_event_check "
         "to order onset against recent events.",
         [("kpi.effective_range", "references")], {}),
        ("report.prior_tec", "report", "Prior incident: TEC degradation", "report",
         "Six months ago a unit showed range loss with intensity tracking diode temperature "
         "and TEC current near its limit; root cause was a degraded TEC module. Same signature.",
         [("sub.thermal", "concluded"), ("part.tec", "references")], {}),
        ("report.prior_laser", "report", "Prior incident: laser power aging", "report",
         "A separate unit lost range from laser power aging: optical output fell but diode "
         "temperature stayed nominal and intensity did NOT correlate with temperature.",
         [("sub.laser", "concluded"), ("part.laser_module", "references")], {}),
        ("log.reboot", "logbook_entry", "Scheduled system reboot", "logbook_entry",
         "Scheduled system reboot performed (routine maintenance window).",
         [], {"timestamp": faults.REBOOT_T, "source": "scheduled"}),
        ("log.service", "logbook_entry", "Last thermal-subsystem service", "logbook_entry",
         "Last service of the thermal subsystem (TEC module inspected, no action).",
         [("sub.thermal", "references")], {"timestamp": faults.SERVICE_T}),
        ("act.window_clean", "diagnostic_action", "Window cleaned", "diagnostic_action",
         "Window cleaned during inspection; no improvement in return intensity afterwards "
         "(reinforces: not contamination).",
         [("sub.optics", "references")], {"timestamp": faults.WINDOW_CLEAN_T,
                                          "props_result": "no_improvement"}),
        ("act.swap_test", "diagnostic_action", "Laser-module swap-test (not tried)",
         "diagnostic_action",
         "Recommended-but-untried: swap the laser module to cleanly isolate laser aging from "
         "a thermal cause before ordering parts. High value of information.",
         [("sub.laser", "references"), ("sub.thermal", "references")], {"props_tried": False}),
    ]

    nodes: list[Node] = []
    edges: list[Edge] = []
    artifacts: list[Artifact] = []
    for nid, ntype, name, kind, text, out_edges, kw in items:
        props = {k.removeprefix("props_"): v for k, v in kw.items() if k.startswith("props_")}
        nodes.append(Node(id=nid, type=ntype, name=name, props=props))
        for dst, etype in out_edges:
            edges.append(Edge(src=nid, dst=dst, type=etype))
        artifacts.append(Artifact(
            id=nid, kind=kind, text=text,
            source=kw.get("source"), timestamp=kw.get("timestamp"),
            refs=[dst for dst, _ in out_edges],
        ))

    # the error-log entry is an artifact only (no "error" node type), reachable via read_errors
    if facts.error:
        eid, etext, erefs = facts.error
        artifacts.append(Artifact(id=eid, kind="error", text=etext,
                                  timestamp=faults.ONSET, refs=erefs))
    return nodes, edges, artifacts


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
    corpus_nodes, corpus_edges, artifacts = _build_corpus(fct)
    if fct.exclude_artifacts:  # drop corpus items whose conclusion would contradict this fault
        ex = set(fct.exclude_artifacts)
        corpus_nodes = [n for n in corpus_nodes if n.id not in ex]
        corpus_edges = [e for e in corpus_edges if e.src not in ex and e.dst not in ex]
        artifacts = [a for a in artifacts if a.id not in ex]

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
