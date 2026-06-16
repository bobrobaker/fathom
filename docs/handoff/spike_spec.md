# Spike specification — diagnostic harness (lidar SUT + benchmark)

**Status:** executable spec for the thin vertical spike. Companion: `spike_build_plan.md` (order of work). Reference docs (do not duplicate — read them): `worked_sut_example_lidar.md` (SUT, fault catalog, difficulty catalog, the worked TEC case), `ontology_typed_links.md` (node/link types, edge confidence, abstraction patterns).

---

## 0. Objective & definition of done

The spike proves the thesis: **one abductive controller, run against two environments, beats baselines** on diagnostic accuracy, evidence quality, token cost, and calibrated abstention — and is transparent (the Investigation Graph). "Done" =

1. The **controller** solves the lidar cases end-to-end and emits a faithful **Investigation Graph** (IG) per case.
2. **Bespoke eval:** the controller beats the `shortcut`, `bare_llm`, and `react` baselines on the rubric (§8.1), with the largest margins on **trigger-discrimination** and **abstention-calibration**.
3. **Benchmark eval:** the controller's *shared retrieval/reasoning core* scores competitively on a MuSiQue subset vs a `bare_llm` baseline at comparable-or-lower token cost (§8.2).
4. The **viewer** renders an IG for ≥1 case as an evidence-colored, step-advancing graph.

**What counts as success (read with §9).** The spike's deliverable is a *clean, defensible finding*, not a guaranteed win. Success = a well-formed eval, strong and fair baselines, and an honest measurement with the capability story visible — **whether or not the controller beats the baselines on accuracy**. The uplift in items 2–3 is the *hypothesis under test*, not the pass condition; the structure is expected to win on the **capability** metrics (trigger-discrimination, abstention, action/compute-bound cases) even if raw accuracy ties a strong long-context baseline. A null or negative result, reported cleanly, is a valid and credible outcome — the modest story.

Hard acceptance thresholds: §9.

---

## 1. Scope

**In:** the controller; the lidar generator producing ≥8 cases (§5.3); the `LidarEnvironment` + `BenchmarkEnvironment`; three baselines; both evals; a minimal IG viewer.

**Out (deferred to full-build):** the full 6-fault catalog at depth (spike carries 2–3 fully, stubs the rest); large/realistic corpus volume; polished UI; multi-tool MCP integrations; the generator's dynamic core beyond the one temporal fault; calibration of numbers against real lidar specs beyond plausibility.

---

## 2. Architecture

Two orthogonal separations, both load-bearing:

**(a) Reasoning vs evidence.** The **controller** (LLM) does judgment — triage, hypothesis generation, action proposal, evidence interpretation, synthesis. The **evidence/tool layer** (deterministic code) does retrieval, telemetry checks, and graph traversal. Determinism lives in the tools; the LLM never fabricates a measurement.

**(b) Controller vs environment.** The controller talks only to an `Environment` interface (§4). `LidarEnvironment` wraps a generated `Case`; `BenchmarkEnvironment` wraps a benchmark item. The controller code is identical across both; only the environment differs. The lidar-specific telemetry checks are plugins on the lidar side and are simply absent on the benchmark side.

```
            ┌─────────────── Controller (LLM reasoning) ───────────────┐
            │  triage → seed hypotheses → [VOI select → act → update    │
            │  Investigation Graph → stop?] → synthesize / abstain      │
            └───────────────┬───────────────────────────┬──────────────┘
                            │ Environment interface (§4) │
              ┌─────────────┴─────────┐       ┌───────────┴───────────┐
              │   LidarEnvironment    │       │  BenchmarkEnvironment  │
              │  (Case: graph,        │       │  (passages + retrieve) │
              │   telemetry, artifacts│       │                        │
              │   + deterministic     │       │   search() only        │
              │   checks/traversal)   │       │                        │
              └───────────┬───────────┘       └────────────────────────┘
                          │ produced by
                   ┌──────┴───────┐
                   │  Generator   │  {fault × mechanisms × seed} → Case
                   └──────────────┘
```

---

## 3. Data model (contracts)

Use **pydantic v2**. These are the authoritative shapes; everything else is implementation detail.

### 3.1 The typed graph

```python
class Node(BaseModel):
    id: str
    type: Literal["KPI","metric","subsystem","part_type","part_version",
                  "config","ticket","report","diagnostic_action",
                  "logbook_entry","doc","domain_doc","design_test_doc",
                  "procedure","person","meeting","chat"]
    name: str
    props: dict = {}                 # type-specific fields + free attrs

class Edge(BaseModel):
    src: str; dst: str
    type: Literal["affects","measured_by","references","version_of",
                  "part_of","specced_in","documented_in","concluded",
                  "variant_for","authored_by","owns","precedes",
                  "supersedes","discussed_in"]
    confidence: float = 1.0          # coupling strength / match degree (§ontology 3)
    props: dict = {}

class TypedGraph(BaseModel):
    nodes: list[Node]; edges: list[Edge]
    # helpers: neighbors(node_id, edge_type, direction) -> list[Node]
```

The graph is small and authored by the generator. It is the navigation structure (Tier-A links carry the weight) — not a retrieval index.

### 3.2 A case

```python
class TimeSeries(BaseModel):
    signal: str; t: list[float]; v: list[float]
    spec: dict | None                 # {min,max,units}; None ⇒ no spec (C4 gap trigger)

class Artifact(BaseModel):            # ticket | report | logbook_entry | doc | ... 
    id: str; kind: str; text: str
    source: str | None                # person id ⇒ credibility (B2)
    timestamp: float | None
    valid_from: float | None; valid_to: float | None   # validity window (B3)
    refs: list[str] = []              # node ids this artifact references (C1/C3)

class GroundTruth(BaseModel):
    answer_type: Literal["cause","abstain"]
    root_cause: str | None            # node id (subsystem/part) when answer_type=="cause"
    causal_chain: list[str]           # ordered node ids
    load_bearing_evidence: list[str]  # the evidence ids that should be cited
    decoys: list[str]                 # competing hypotheses (node ids)
    conflicts: list[str]              # e.g. lying-channel signal id, trigger event id
    trigger: str | None               # salient-but-noncausal event id, if any
    mechanisms: list[str]             # difficulty-catalog IDs present (e.g. ["D1","B5"])

class Case(BaseModel):
    id: str
    graph: TypedGraph
    telemetry: list[TimeSeries]
    artifacts: list[Artifact]
    bom: TypedGraph                   # part_of/version_of/variant_for subgraph (may share nodes)
    ground_truth: GroundTruth         # HIDDEN from controller; eval-only
```

### 3.3 The Investigation Graph (the controller's live state — the spine)

```python
class Hypothesis(BaseModel):
    id: str; label: str               # e.g. "TEC degradation"
    node_ref: str | None              # the graph node it corresponds to
    log_odds: float = 0.0             # prior + Σ evidence LLRs (§6.4)
    status: Literal["open","supported","ruled_out","leading"] = "open"

class EvidenceItem(BaseModel):
    id: str; summary: str
    source: str                       # which tool/artifact produced it (provenance)
    # n-ary by design (§ontology 4.2): condition/time live in props
    props: dict = {}

class EvidenceLink(BaseModel):
    evidence_id: str; hypothesis_id: str
    polarity: Literal["+","-"]
    weight: float                     # ~ |log-likelihood-ratio|, LLM-assigned

class InvestigationGraph(BaseModel):
    symptom: str
    hypotheses: list[Hypothesis]
    evidence: list[EvidenceItem]
    links: list[EvidenceLink]
    conflicts: list[str] = []         # flagged unreliable channels / demoted triggers
    recommended_action: str | None = None     # next diagnostic action (VOI), incl. swap-test
    status: Literal["in_progress","concluded","abstained"] = "in_progress"
    # snapshots[]: list[InvestigationGraph]  ← optional per-step copies for the viewer
```

The IG is the single source of truth: the controller writes it, the eval reads it, the viewer renders it. **Per-step snapshots** are how the "live view of the actual state" is produced — append a deep copy after each loop iteration.

### 3.4 The answer (what the controller returns)

```python
class Answer(BaseModel):
    answer_type: Literal["cause","abstain"]
    root_cause: str | None
    causal_chain: list[str] = []
    cited_evidence: list[str] = []    # evidence ids
    ruled_out: list[str] = []
    conflicts: list[str] = []
    recommended_action: str | None = None
    final_graph: InvestigationGraph
```

---

## 4. The environment interface

```python
class Environment(ABC):
    @abstractmethod
    def symptom(self) -> str: ...
    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[Artifact]: ...   # hybrid BM25(+embed)
    # lidar-only (BenchmarkEnvironment raises NotSupported):
    def query_telemetry(self, signal: str, window=None, condition=None) -> TimeSeries: ...
    def run_check(self, name: str, args: dict) -> dict: ...           # deterministic checks (§6.5)
    def read_logbook(self, window=None) -> list[Artifact]: ...
    def read_errors(self, window=None) -> list[Artifact]: ...
    def read_diagnostic_actions(self) -> list[Artifact]: ...
    def traverse(self, node_id: str, edge_type: str, direction="out") -> list[Node]: ...
    def list_signals(self) -> list[str]: ...                          # for C4 gap detection
```

`BenchmarkEnvironment` implements `symptom()` (the question) and `search()` (over the benchmark's passage set) only. The controller must degrade gracefully when diagnostic methods are unavailable (it discovers capabilities by attempting them or via a `capabilities()` flag).

---

## 5. The generator (lidar)

### 5.1 Contract
`generate(fault: str, mechanisms: list[str], seed: int) -> Case`. Deterministic given a seed. Implements the **forward-effects model** from `worked_sut_example_lidar.md`: a fault → parameterized signatures across telemetry/config/log + the corpus artifacts + the hidden ground truth, plus injected decoys, lying channel, and trigger per the requested `mechanisms`.

### 5.2 Mechanics
- **Signatures** are templated (ramp, step, drift, correlated-pair, flatline). One small **dynamic generator** for the temporal fault (D4); everything else static.
- **Coupling:** effects propagate along `affects` edges (focal subsystems detailed; abstracted ones carry coarse real propagation).
- **Anti-shortcut balancing** (§eval) is enforced *here*: across the case set, the correlation between "salient recent event present" and "that event is the cause" must sit ≈0.5 (mix of coincidence, absent-cue, and trigger≠cause cases).
- **Difficulty must be capability-bound** (the lesson from the prior attempt, where the questions were too easy): each case should be solvable *only* via something a context-dump cannot do — running a check (D5), querying a specific window/condition (D3/D4), traversing to buried evidence (C1), recommending an action, or abstaining (E1). If a case can be solved by reading the whole corpus once, it does not belong in the eval. At least one case is authored at a corpus volume that **exceeds a single context window**, so retrieval is mandatory.
- Optional **LLM roughening pass** on artifact text (logbook inconsistency, ticket phrasing) — off by default for reproducibility, on as a knob.

### 5.3 Spike case set (≥8; the eval's frozen slice draws from these)

| # | Fault | Mechanisms (IDs) | Purpose |
|---|---|---|---|
| 1 | TEC degradation | D1, B5, D5, A2 | the worked example (cross-subsystem + decoy + lying channel + demoted trigger) |
| 2 | Laser aging | D5, A1 | the decoy as a *true* cause (no temp correlation) — symmetry vs #1 |
| 3 | Window contamination | C-spatial, A3 | spatial-cluster signature; reasoning from absence |
| 4 | Calibration drift | B1, C3 | post-release config; chained evidence (date→release) |
| 5 | *No clean cause* | E1 | intermittent/coincidence → correct answer is **abstain** |
| 6 | Detector bias drift | C1, C2 | buried evidence reachable only via graph traversal + intra-doc |
| 7 | TEC degradation (variant) | D6 | near-symmetric to a decoy; needs the expensive discriminating check (tie-breaker) |
| 8 | Common-mode (power) | A4, A5 | one cause looks like two faults; redundant channels agree but are wrong |

(Stub faults — scanner miscalibration, etc. — exist as fault-hooks but aren't authored to depth in the spike.)

---

## 6. The controller (abductive loop)

### 6.1 Loop (pseudocode)

```
def diagnose(env, budget=12) -> Answer:
    ig = InvestigationGraph(symptom=env.symptom(), ...)
    seed_hypotheses(ig, env)                      # LLM: from symptom + affects-neighbors + playbook
    for step in range(budget):
        actions = propose_actions(ig, env)        # LLM proposes candidate next actions
        best = argmax(actions, key=voi)           # VOI = expected_discrimination / cost  (§6.3)
        result = execute(best, env)               # deterministic tool/retrieval/traversal
        update_graph(ig, result)                  # LLM interprets → EvidenceItem + links(+weights)
        ig.snapshots.append(deepcopy(ig))         # for the viewer
        if stop(ig): break                        # §6.2
    return synthesize(ig)                          # LLM: cause+chain+citations, or abstain
```

### 6.2 Stop / abstain conditions (defaults; tunable)
- **Conclude** if `max(confidence) > τ_dom (0.70)` **and** `margin over runner-up > τ_margin (0.20)`.
- **Budget exhausted** → conclude with the leader **iff** `max(confidence) > τ_min (0.55)`, else **abstain**.
- **Abstain** if after budget no hypothesis exceeds `τ_min`, or if the evidence is mutually contradictory beyond a set threshold (this is how E1/abstention cases must resolve).

### 6.3 VOI
Per candidate action the LLM estimates **expected discrimination** (how much it would move the hypothesis distribution; a 0–1 score) and the action carries a **fixed cost** by type (`run_check`=1, `traverse`=1, `search`=2, `recommend_swap_test`=3). Pick `argmax(expected_discrimination / cost)`. (A formal entropy-reduction VOI is a full-build option; LLM-scored is the spike's tractable version.)

### 6.4 Belief update (deterministic aggregation, LLM judgment)
The LLM assigns each new `EvidenceLink` a polarity and a `weight ≈ |log-likelihood-ratio|`. The deterministic layer sets `hypothesis.log_odds = prior + Σ (sign · weight)` and `confidence = sigmoid(log_odds)`. This makes A1 (mixed evidence) and A2 (shared evidence) fall out mechanically and keeps the aggregation auditable.

### 6.5 Deterministic checks (lidar; from the worked example)
`config_diff`, `spatial_intensity_check`, `temp_correlation_check`, `tec_load_check`, `channel_sanity_check`, `onset_vs_event_check`. Each is pure code over telemetry/config, returns a structured `dict`, and is logged. New checks are added per fault as the case set grows.

### 6.6 Prompts
Keep the system prompt small and role-bounded: "you maintain a hypothesis differential; propose the single most discriminating next action; never assert a measurement you have not retrieved; cite evidence by id." Tool/action results are returned as structured observations. (Detailed prompt text is an implementation artifact, iterated against case #1.)

---

## 7. Baselines (must be implemented *strong and fair* — see audit)

- **`shortcut`** — blames the most recent change/event. The rig-detector: the controller must beat it, or the cases are leaky.
- **`bare_llm`** — the entire case (all telemetry summaries + all artifacts) dumped into context, asked for the root cause + evidence. A genuinely strong long-context prompt, not a strawman.
- **`react`** — the same tools as the controller in a plain ReAct loop, but **without** the hypothesis-differential / IG bookkeeping and VOI selection. Isolates the value of the structure.
- **`controller`** — the system under test.

All four return an `Answer` (the baselines fill `final_graph` minimally) so the eval scores them identically.

---

## 8. Evals

### 8.1 Bespoke rubric (per case, vs ground truth)
| Metric | Definition |
|---|---|
| **accuracy** | `answer.root_cause == gt.root_cause` (or both abstain) |
| **evidence-F1** | F1 of `cited_evidence` vs `gt.load_bearing_evidence`; hallucinated citations (ids not in case) → precision penalty |
| **conflict-handling** | fraction of `gt.conflicts` surfaced in `answer.conflicts` |
| **trigger-discrimination** | 1 if a `gt.trigger` exists and was *not* named as cause (and was noted), else 0 |
| **abstention-calibration** | correct on the abstain/cause decision (scored across the set: false-abstain and false-conclude both penalized) |
| **cost** | total tokens per resolved case |

Report a table, **grouped into two families reported separately:** *accuracy* (root-cause correctness) and *capability* (trigger-discrimination, abstention-calibration, conflict-handling, and performance on the action/compute-bound cases). The **capability family is where the structure should win even if a strong `bare_llm` ties on accuracy** — so the headline is the capability-family uplift of `controller` over `bare_llm` and `shortcut`, with the accuracy comparison reported honestly alongside, win or tie.

### 8.2 Benchmark eval
Run the **shared core only** (controller minus lidar checks; `search`-driven iterative retrieval + hypothesis-style answer selection) on a **MuSiQue** dev subset (start n=100). Report **answer-EM/F1** and **tokens/question** for `controller-core` vs `bare_llm` and a `static_rag` baseline. HotpotQA optional alongside (same harness). Frame this as *agentic retrieval generalization*, not diagnosis (see audit concern #2).

---

## 9. Acceptance criteria

**The spike *succeeds* (ships as a portfolio finding) when:**
- S1. The eval is well-formed and reproducible — ≥9 cases, capability-bound (§5.2), anti-shortcut-balanced, scored across the four solvers over ≥3 runs with variance reported.
- S2. The baselines are strong and fair — a best-honest `bare_llm`, a real `react`; `shortcut` gets the trigger cases wrong as designed.
- S3. The result is reported cleanly, accuracy and capability families separately (§8.1), **whatever the outcome**.
- S4. The viewer renders case #1's IG across its steps, nodes colored by confidence sign, the demoted trigger visibly distinct.

**The thesis is *confirmed* (the hoped-for result) when, additionally:**
- T1. `controller` strictly beats `shortcut` on accuracy and ties-or-beats `bare_llm`.
- T2. `controller` strictly exceeds `bare_llm` and `react` on the **capability family** — the signature win.
- T3. `controller` evidence-F1 ≥ `bare_llm`'s at ≤ its token cost.
- T4. On MuSiQue, `controller-core` lands in a defensible band vs a published agentic-retrieval baseline at comparable-or-lower tokens — **or**, per the early floor check (build plan M4.5), is scoped down to report-only rather than showcased.

Success (S1–S4) does not depend on confirmation (T1–T4). A clean negative on the thesis is a valid, credible finding — the modest story we accepted.

---

## 10. Tech stack

Python 3.11; `anthropic` SDK (model = a current Claude; pin in config); `pydantic` v2; `networkx` (the small typed graph — no graph DB at this scale); `rank_bm25` (+ optional `sentence-transformers` for hybrid search); `pytest` (eval harness); the MuSiQue dataset via its standard release; viewer = a single static `index.html` (D3 or vis-network) that loads exported IG JSON. No browser storage; no external services beyond the Anthropic API and the dataset download.

---

## 11. Non-goals restated

The spike is a *finding*, not a product. It is small on purpose. The generator-at-scale, the full corpus, the polished UI, and the remaining faults are the full-build set's job. The spike's only burden is to make the uplift (or its honest absence) measurable and the reasoning visible.
