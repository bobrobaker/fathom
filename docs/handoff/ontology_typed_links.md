# Typed-link ontology for the diagnostic knowledge graph

**Purpose.** Define the node and link types of the Project's knowledge graph — the typed, hand-built **system-model graph** the generator lays scenarios on and the agent navigates for evidence. Links are **graded and ranked by the one criterion that matters: does the agent *use* the link to improve a project goal** — diagnostic accuracy, evidence quality, token cost, transparency, or calibrated abstention? A link that earns no agent-use is cut.

**Grounding (how others build this — see §6).** This follows current practice rather than inventing:
- a **compact, bounded schema** ⟨entity types, condensed relations, attribute types⟩ — the schema-bounded approach now standard in agentic GraphRAG — rather than open-ended relations;
- a **property-graph** model (Neo4j-style) so links carry attributes (confidence, weights) natively;
- the **RCA-knowledge-graph** pattern of locating faults to physical entities (devices, signals) over causal/dependency edges, which is what makes the result interpretable.

> Scope note: at our corpus scale this graph is **small and authored**, used for *navigation and reasoning* — not LLM-extracted at scale, not a bulk retrieval index. GraphRAG-the-retrieval-stack stays deferred; this is the system-model/navigation graph.

---

## 1. Node types

**System structure**
- `KPI` — a performance spec the user cares about (effective range, range noise).
- `metric` / `signal` — a measurable quantity (return intensity, TEC current).
- `subsystem` — thermal, laser, detector, optics, …
- `part_type` — a part as a *class* (the detector). [abstraction — see §4]
- `part_version` — a specific revision/instance (detector rev C).
- `config` / `variant` — a customer/module configuration.

**Evidence & corpus**
- `ticket`, `report` (formerly RCA), `diagnostic_action`, `logbook_entry`
- `doc` (system-model/reference), `domain_doc` (specialized vocabulary/science, often new-hire training material), `design_test_doc`, `procedure`

**People & comms** *(new)*
- `person` — owns systems/parts, authors records, attends meetings.
- `meeting` — especially recurring ones (a `meeting_series` *class* with `meeting` occurrences — see §4); a temporal backbone and soft-evidence source.
- `chat` — informal conversational record (logbook-like, low consistency).

---

## 2. Link types — graded & ranked

**Grade = agent-use** (primary). *Cost* = authoring effort. *Goal* = the project goal it serves.

### Tier A — load-bearing (used constantly; cut one and the project breaks)

| Link | Connects | How the agent uses it | Goal | Cost |
|---|---|---|---|---|
| **affects** | subsystem/metric/KPI → metric/KPI | defines the hypothesis & propagation space; the causal spine of the Investigation Graph | accuracy, transparency | med |
| **measured_by** | metric → part/sensor | maps a symptom-metric to the parts that could cause it; underlies "the gauge lies" | accuracy, evidence | cheap |
| **references** | ticket/report/action/chat/meeting → any artifact | primary navigation edge from structure to the human records discussing it (C1) | evidence, transparency | cheap |
| **version_of** | part_version → part_type | the relevance key: is a historical report about *my* version? (B1/B3 confidence) | evidence, abstention | cheap |

### Tier B — frequently useful (clear agent-use; keep)

| Link | Connects | How the agent uses it | Goal | Cost |
|---|---|---|---|---|
| **part_of** | subassembly → assembly | localize/scope a fault up the hierarchy | accuracy | cheap |
| **specced_in** / **documented_in** | metric/part → doc/procedure | find "what's normal"/the spec; the *absence* of this edge is a C4 knowledge-gap | accuracy, abstention | cheap |
| **concluded** | report/action → root-cause/result | prior verdicts become priors for a matching signature | accuracy | cheap |
| **variant_for** | config → customer | gate relevance of customer-config-specific evidence | evidence | cheap |
| **authored_by** / **reported_by** | record → person | source-credibility weighting (B2) | evidence | cheap |
| **owns** / **responsible_for** | person → subsystem/part | escalation routing, "who to ask," credibility | action, transparency | cheap |

### Tier C — situational (keep only where a scenario uses it)

| Link | Connects | How the agent uses it | Goal | Cost |
|---|---|---|---|---|
| **precedes** / **occurred_at** | event → event/time | explicit time-ordering for trigger-vs-cause (D1/D2) — often a timestamp *property*, not an edge | accuracy | cheap |
| **supersedes** | report/doc/config → prior | validity/staleness (B3) | evidence | cheap |
| **discussed_in** / **attended** | artifact/person → meeting/chat | reach soft evidence; recurring-meeting timeline | evidence | cheap |

**Cut rule.** If a proposed link has no honest answer in "how the agent uses it," it doesn't enter the schema. This is also the test for any *new* link proposed later.

---

## 3. Should links carry confidence? — yes, and mostly on the links, not the nodes

Confidence belongs on **relations**, because a hypothesis node's confidence is *derived* — it is the net of its weighted evidence edges (mechanism A1). Two kinds:

- **System-model edges** (`affects`, `version_of`) carry a static **coupling strength** or **match degree** — how strongly A affects B, how closely a version matches — feeding propagation priors and B1 relevance weighting.
- **Investigation-Graph edges** (evidence → hypothesis) carry a dynamic **confidence / likelihood-ratio** that updates as evidence arrives (supports/contradicts, with weight). This is where A1/A2 live.

Mechanically: in a **property-graph** model this is simply an edge property — clean and cheap. The standard reason to go further and **reify** a relation into its own node is precisely when you must attach *certainty/strength/relevance* to it, or relate **more than two** things — which the W3C n-ary-relations pattern names as its motivating cases, and which leads directly to §4.

---

## 4. Abstractions & grouping — three named patterns (this is well-trodden)

Your "part type" intuition is a formal, named distinction, and "connect a bunch of nodes with a quality to a node" is a second one. There are **three** patterns; the skill is choosing which applies. The existence of an abstraction does *not* always mean "just add a node" — it means add a node **of a specific kind**, and the kind matters.

### (1) Class / instance — the universal vs the particular
(T-box vs A-box.) `part_type` is a *class*; each `part_version` is an instance, linked by `version_of`. The class node is where you attach what's true of *all* instances. Other instances of this same phenomenon in our domain:
- `fault_type` vs `fault_occurrence` (our catalog vs a scenario instance)
- `tool_model` vs `tool_unit` (lidar model X vs serial #1234)
- `metric` (a concept) vs a `reading` (a specific time-series)
- `procedure` vs `procedure_execution` (the calibration vs the one done Tuesday)
- `meeting_series` vs a `meeting` occurrence

### (2) Reified n-ary relation — a relationship that has its own attributes or connects >2 nodes
Make the *relationship* a node. This is the standard fix for "a quality connecting several nodes." Examples we already have or want:
- an **evidence/observation event**: *metric M, under condition C, at time T, supports hypothesis H with weight W* — a 5-way relation, reified. This **is** the Investigation Graph's evidence node.
- a **diagnostic_action**: *person P swapped part A onto tool B on date D → result R* — already a reified n-ary relation.
- a **measurement**: *sensor S read metric M = V at T under C*.
- a **release**: *HW rev X + SW ver Y, effective date D* — a context node others reference for validity windows.

*When to reify (the truthmaker test):* reify the entity responsible for the statement's truth. If a relation needs a qualifier, a timestamp, a confidence, or a third participant — it is a node, not an edge.

### (3) Collection / grouping by a shared quality — set membership, not a kind
A `supplier_lot`, a `site`, a `customer_fleet`: a node the members link to, so the agent can reason over the group ("all parts from lot L," "all units at site S"). Use this when the abstraction *only* groups — no instance-of semantics, no relationship attributes.

### Decision rule
- groups *particulars under a universal* → **class** node (+ `instance_of` / `version_of`)
- carries *attributes of a relationship* or *arity > 2* → **reified relation** node
- only *bundles members by a property* → **collection** node
- a plain *binary fact* → just a typed **edge** (give it an attribute if it needs a weight)

---

## 5. How the agent uses the graph (operational)

- **Navigate to non-obvious evidence (C1/C3):** follow typed edges from the symptom outward — `KPI –affects→ metric –measured_by→ part –version_of→ … –references→ ticket` — where the *edge type* justifies why the destination is relevant. Route to graph-traversal when the answer is a *relationship*, not a passage.
- **Gate historical evidence (B1/B3):** use `version_of` / `variant_for` / `supersedes` to weight a prior report by how well its version, config, and date match the tool in front of you — the calibrated-confidence step that makes a closed report trustworthy or not.
- **Scaffold hypotheses:** the `affects` subgraph *is* the hypothesis-and-propagation space; the Investigation Graph is its evidence-annotated traversal (reified evidence nodes per §4(2), with edge confidence per §3).
- **Detect knowledge gaps (C4):** a metric or term with no `specced_in` / `documented_in` edge is a gap → surface a request rather than guess.
- **Route & credit (people):** `owns` / `authored_by` drive source-credibility weighting and "who to ask" recommendations.

Keep the schema **compact and bounded**, **property-graph** (edges hold attributes), and **small/authored** — the agent's leverage is the *typed traversal*, not graph scale.

---

## 6. References

*RCA knowledge graphs (relations, causal edges, fault localization to physical entities)*
- KGroot — *Enhancing Root Cause Analysis through Knowledge Graphs and GCNs*, arXiv:2402.13264. https://arxiv.org/abs/2402.13264
- *A Causality Mining and Knowledge Graph Based Method of Root Cause Diagnosis* (cloud), Appl. Sci. 2020. https://www.mdpi.com/2076-3417/10/6/2166
- *A Comprehensive Survey on Root Cause Analysis in (Micro)Services*, arXiv:2408.00803. https://arxiv.org/html/2408.00803v1
- Root-KGD — *Root Cause Diagnosis Based on Knowledge Graph and Industrial Data*, arXiv:2406.13664. https://arxiv.org/html/2406.13664v1

*Ontology design patterns (n-ary relations, reification, class/instance)*
- Noy & Rector, *Defining N-ary Relations on the Semantic Web*, W3C Working Group Note, 2006 — the canonical pattern for attaching certainty/strength/relevance to a relation. https://www.w3.org/TR/swbp-n-aryRelations/
- *The Semantics of Reifying n-ary Relationships as Classes* (truthmaker view of when to reify). https://www.researchgate.net/publication/220711168
- *A Multi-dimensional Comparison of Ontology Design Patterns for Representing n-ary Relations*. https://www.researchgate.net/publication/295091901
- PROV-O Qualification Pattern (reification in practice), via *Mapping PROV to BFO*, arXiv:2408.03866. https://arxiv.org/pdf/2408.03866

*Agentic GraphRAG / current practice (schema-bounded, property-graph, route-to-graph)*
- Youtu-GraphRAG — schema-bounded extraction ⟨entity types, relations, attributes⟩, arXiv:2508.19855. https://arxiv.org/pdf/2508.19855
- Neo4j NODES AI 2026 — *Agentic GraphRAG* (schema inference; route vector vs graph traversal; property graph). https://neo4j.com/videos/nodes-ai-2026-agentic-graphrag-autonomous-knowledge-graph-construction-and-adaptive-retrieval-2/
- *GraphRAG in 2026: A Practical Buyer's Guide* — "the answer is a relationship, not a paragraph"; multi-hop + traceability. https://medium.com/@tongbing00/graphrag-in-2026-a-practical-buyers-guide-to-knowledge-graph-augmented-rag-43e5e72d522d
- Graph-R1 — agentic, iterative graph retrieval, arXiv:2507.21892. https://arxiv.org/pdf/2507.21892
- Awesome-GraphRAG / GraphRAG Benchmark (ICLR'26). https://github.com/DEEP-PolyU/Awesome-GraphRAG

*Compiled 2026-06-15. Vendor/market claims re-verified before any external-facing use.*

---

## 7. Open choices

- The node/link sets above — additions or cuts? (the **cut rule** is the test.)
- Reified evidence nodes in the Investigation Graph from the start (richer, matches §4(2)), or start with weighted edges and reify later?
- Time as a universal timestamp **property** vs explicit `precedes` **edges** — I lean property, with a few explicit `precedes` edges where ordering is the point.
