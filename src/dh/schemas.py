"""Data contracts (spec §3) — the authoritative shapes for the whole spike.

This module is the single source of truth: the generator writes these, the
environment passes them, the controller reasons over the Investigation Graph,
and the eval reads ground truth. Anything that disagrees with a model here is a
bug. Pydantic v2. Traversal logic for `TypedGraph` lives in `dh.graph` and is
exposed here as thin `neighbors()` / `traverse()` methods (spec §3.1, build plan).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

# --- §3.1 The typed graph ----------------------------------------------------

NodeType = Literal[
    "KPI", "metric", "subsystem", "part_type", "part_version",
    "config", "ticket", "report", "diagnostic_action",
    "logbook_entry", "doc", "domain_doc", "design_test_doc",
    "procedure", "person", "meeting", "chat",
]

EdgeType = Literal[
    "affects", "measured_by", "references", "version_of",
    "part_of", "specced_in", "documented_in", "concluded",
    "variant_for", "authored_by", "owns", "precedes",
    "supersedes", "discussed_in",
]

Direction = Literal["out", "in"]


class Node(BaseModel):
    id: str
    type: NodeType
    name: str
    props: dict = {}  # type-specific fields + free attrs


class Edge(BaseModel):
    src: str
    dst: str
    type: EdgeType
    confidence: float = 1.0  # coupling strength / match degree (ontology §3)
    props: dict = {}


class TypedGraph(BaseModel):
    nodes: list[Node] = []
    edges: list[Edge] = []

    def neighbors(
        self,
        node_id: str,
        edge_type: EdgeType | None = None,
        direction: Direction = "out",
    ) -> list[Node]:
        """Direct neighbors of `node_id` along `edge_type` (any type if None)."""
        from dh import graph

        return graph.neighbors(self, node_id, edge_type, direction)

    def traverse(
        self,
        node_id: str,
        edge_type: EdgeType,
        direction: Direction = "out",
        max_depth: int | None = None,
    ) -> list[Node]:
        """Multi-hop reachability from `node_id` following `edge_type`."""
        from dh import graph

        return graph.traverse(self, node_id, edge_type, direction, max_depth)


# --- §3.2 A case -------------------------------------------------------------

class TimeSeries(BaseModel):
    signal: str
    t: list[float]
    v: list[float]
    spec: dict | None = None  # {min,max,units}; None => no spec (C4 gap trigger)


class Artifact(BaseModel):  # ticket | report | logbook_entry | doc | ...
    id: str
    kind: str
    text: str
    source: str | None = None  # person id => credibility (B2)
    timestamp: float | None = None
    valid_from: float | None = None  # validity window (B3)
    valid_to: float | None = None
    refs: list[str] = []  # node ids this artifact references (C1/C3)


class GroundTruth(BaseModel):
    answer_type: Literal["cause", "abstain"]
    root_cause: str | None = None  # node id (subsystem/part) when answer_type=="cause"
    causal_chain: list[str] = []  # ordered node ids
    load_bearing_evidence: list[str] = []  # evidence ids that should be cited
    decoys: list[str] = []  # competing hypotheses (node ids)
    conflicts: list[str] = []  # e.g. lying-channel signal id, trigger event id
    trigger: str | None = None  # salient-but-noncausal event id, if any
    mechanisms: list[str] = []  # difficulty-catalog IDs present (e.g. ["D1","B5"])


class Case(BaseModel):
    id: str
    graph: TypedGraph
    telemetry: list[TimeSeries] = []
    artifacts: list[Artifact] = []
    bom: TypedGraph = TypedGraph()  # part_of/version_of/variant_for subgraph (may share nodes)
    ground_truth: GroundTruth  # HIDDEN from controller; eval-only


# --- §3.3 The Investigation Graph (controller's live state — the spine) -------

class Hypothesis(BaseModel):
    id: str
    label: str  # e.g. "TEC degradation"
    node_ref: str | None = None  # the graph node it corresponds to
    log_odds: float = 0.0  # prior + Σ evidence LLRs (§6.4)
    status: Literal["open", "supported", "ruled_out", "leading"] = "open"


class EvidenceItem(BaseModel):
    id: str
    summary: str
    source: str  # which tool/artifact produced it (provenance)
    # n-ary by design (ontology §4.2): condition/time live in props
    props: dict = {}


class EvidenceLink(BaseModel):
    evidence_id: str
    hypothesis_id: str
    polarity: Literal["+", "-"]
    weight: float  # ~ |log-likelihood-ratio|, LLM-assigned


class InvestigationGraph(BaseModel):
    symptom: str
    hypotheses: list[Hypothesis] = []
    evidence: list[EvidenceItem] = []
    links: list[EvidenceLink] = []
    conflicts: list[str] = []  # flagged unreliable channels / demoted triggers
    recommended_action: str | None = None  # next diagnostic action (VOI), incl. swap-test
    status: Literal["in_progress", "concluded", "abstained"] = "in_progress"
    snapshots: list["InvestigationGraph"] = []  # per-step copies for the viewer (§3.3)


# --- §3.4 The answer (what the controller returns) ---------------------------

class Answer(BaseModel):
    answer_type: Literal["cause", "abstain"]
    root_cause: str | None = None
    causal_chain: list[str] = []
    cited_evidence: list[str] = []  # evidence ids
    ruled_out: list[str] = []
    conflicts: list[str] = []
    recommended_action: str | None = None
    final_graph: InvestigationGraph


# Resolve the self-reference in InvestigationGraph.snapshots.
InvestigationGraph.model_rebuild()
