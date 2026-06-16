# Agent architectures for a hypothesis-driven diagnostic harness — 2026 landscape

**Purpose.** A reference map of recent (≈ last 6 months, as of mid-2026) agentic-AI architectures relevant to *a bounded, hypothesis-driven diagnostic agent* that retrieves context, runs deterministic checks, reasons over evidence, and produces an evidence-linked rationale over a simulated engineered system-under-test — and that must measurably beat a bare LLM call (with the same data) on answer quality, evidence quality, and token cost.

**Honesty note on "recency."** The foundations predate 2026 — ReAct (2022), HyDE (2022), Self-RAG (2023), GraphRAG (2024), MCP (2024). What is genuinely *recent* is (a) their convergence into named, productized patterns and (b) a few new additions (programmatic tool calling, the "Investigation Graph" diagnostic framing, deterministic causal-graph RCA, small-model evaluators). Entries are tagged **[standard]** (mature / widely adopted) or **[emerging]** (recent / leading-edge). Source authority: arXiv papers and vendor *engineering* posts (Anthropic, Google) are primary; "2026 RAG/agent" listicles are directional market signal and treated as such.

---

## 1. The diagnostic loop itself is now a named pattern
*The most on-point finding: the architecture under design has converged into recognized patterns and shipping products.*

### Investigation-Graph diagnostic ensemble — [emerging]
An ensemble of specialized agents — a hypothesis-generator, an evidence-retriever (logs, configs, metrics, live queries), and an evidence-evaluator — running an investigative loop whose primary output is an **"Investigation Graph": a directed graph of hypothesis / evidence / conclusion nodes that branches as new hypotheses appear and converges as evidence narrows the field.** It is the formalized version of a fishbone-with-evidence and of confidence-weighted differential diagnosis.
- *Why it fits:* almost exactly the loop under design; the Investigation Graph is the transparency artifact (the reasoning trail + the ruled-out branches) made first-class.
- *Source:* ODSC, "Why Cross-Domain Root-Cause Analysis is Still Unsolved — and How Agentic AI Changes That," Medium (Mar 2026).

### AI SRE — the productized version — [standard / productized 2025–26]
Site Reliability Engineering vendors now ship diagnostic agents that **generate and test hypotheses against live telemetry, topology, and incident history; follow existing runbooks rather than a fixed rule library; gate actions behind human approval; and learn to generate new playbooks** (Datadog Bits AI SRE; PagerDuty SRE Agent; Dynatrace causal AI + Azure SRE Agent).
- *Why it fits:* the same shape, in IT-ops — validating playbook-driven, hypothesis-testing diagnosis with approval gates. A hardware/metrology version is a differentiated domain on a proven architecture. The "follow a runbook" agent is also a natural eval baseline.
- *Source:* Augment Code, "AI SRE: The 2026 Guide to AI-Powered Site Reliability Engineering" (~May 2026).

### AgentTrace — deterministic causal-graph RCA — [emerging]
A causal-tracing framework that reconstructs causal graphs from logs, traces backward from the error, and ranks candidate root causes from interpretable structural signals **with no LLM inference at debug time — and outperforms both heuristic and LLM-based baselines on accuracy and sub-second latency.**
- *Why it fits:* the strongest external evidence for keeping the evidence layer deterministic — deterministic checks can beat an LLM on accuracy *and* cost. (Built to diagnose multi-agent systems, but the principle transfers.)
- *Source:* Wang, "AgentTrace: Causal Graph Tracing for Root Cause Analysis in Deployed Multi-Agent Systems," arXiv:2603.14688 (Mar 2026; ICLR 2026 AIWILD workshop).

---

## 2. Control spine — stateful-graph orchestration
*The substrate for a bounded controller with explicit state, conditional transitions, and stop/abstain.*

### LangGraph — [standard]
A stateful, cyclic-graph orchestration framework: directed cyclic graph with conditional branching, persistent checkpoints, and interruptible human-in-the-loop points. The de-facto substrate for controllable agentic-RAG loops.
- *Why it fits:* the abductive loop (hypothesis state → value-of-information-gated transitions → deterministic nodes → stop/abstain) expressed as an inspectable graph.
- *Sources:* monday.com, "AI agent frameworks that actually work…" (Apr 2026); Rane, "Next-Generation Agentic RAG with LangGraph (2026 Edition)," Medium (Mar 2026).

### Claude Agent SDK — [emerging / Anthropic-native standard]
Anthropic's agent SDK (the architecture behind Claude Code): primitives for tool use, hooks, MCP, **skills**, and subagents; the fastest-growing Anthropic-native framework into 2026.
- *Why it fits:* "skills" map onto playbooks; hooks give deterministic control points; native extended thinking for the reasoning step.
- *Source:* Alice Labs, "Best AI Agent Frameworks 2026" (~May 2026).

### Model Context Protocol (MCP) — [standard]
An open standard for agent-to-tool communication, now broadly adopted across editors and platforms.
- *Why it fits:* the natural interface for exposing the deterministic checks / data sources as tools if this is productized.
- *Source:* gurusup, "Best Multi-Agent Frameworks 2026" (May 2026).

> **Spike note:** none of these is required for a first slice. A hand-rolled controller is more legible and matches the "the pipeline owns the loop" thesis; reach for a framework only when scaling.

---

## 3. Retrieval — RAG as a "knowledge runtime"
*Retrieval has shifted from a one-shot step to a governed, stateful subsystem.*

### Agentic RAG — [standard / converged 2026]
RAG where autonomous agents plan, retrieve, reason, critique, and reflect in loops until confident or out of budget — subsuming reflection (Self-RAG), query rewriting, and selective retrieval as components.
- *Why it fits:* this *is* the retrieve-to-discriminate loop; Self-RAG / HyDE / RRF (already specced) are sub-components.
- *Sources:* Rane, Medium (Mar 2026); "Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG," arXiv:2501.09136 (Jan 2026) — a taxonomy by agent cardinality, control structure, autonomy, and knowledge representation.

### GraphRAG / Agentic Graph RAG — [standard for relational corpora]
Build a knowledge graph (entities + relationships) from the corpus, then combine graph traversal with vector search; enables the multi-hop, cross-system reasoning that vector-only retrieval misses. Microsoft open-sourced GraphRAG, accelerating adoption.
- *Why it fits:* the diagnostic corpus is relational (config ↔ subsystem ↔ event ↔ spec ↔ prior case); this is the productized version of the "temporal knowledge graph" instinct from the failure-memory note.
- *Sources:* TIMEWELL, "RAG Complete Guide 2026" (Jan 2026); techment, "10 RAG Architectures in 2026" (May 2026); Google Cloud, "Multimodal GraphRAG resource orchestration" (Apr 2026).

### Adaptive RAG / Self-RAG — [standard]
Dynamically decide *whether* to retrieve and how hard, routed by query difficulty — optimizing cost, latency, and reliability.
- *Why it fits:* the cost-aware sibling of triage / cheap early-exit.
- *Source:* techment, "10 RAG Architectures in 2026" (May 2026).

### "Knowledge runtime" framing — [emerging framing]
The 2026 framing that retrieval now integrates retrieval + verification + reasoning + access control + audit trails into one always-on system — governed, explainable, adaptive — rather than a bolt-on document search.
- *Why it fits:* matches the transparency / provenance / audit requirement directly.
- *Source:* TIMEWELL, "RAG Complete Guide 2026" (Jan 2026).

---

## 4. Context engineering — cost & transparency
*The discipline behind "beat the bare call that has all the data dumped in."*

### Context engineering (Anthropic, formalized late 2025) — [standard]
Curate the smallest set of high-signal tokens at each step; more tokens actively degrade behavior (attention scales quadratically; "lost-in-the-middle"). Practices: retrieval budgeting, compaction, memory tiering, tool-result pruning.
- *Why it fits:* the conceptual backing for the uplift hypothesis — a curated retrieve-to-discriminate loop should beat a stuffed context on accuracy *and* cost.
- *Sources:* Anthropic, "Effective context engineering for AI agents" (2025); digitalapplied, "Context Engineering: Agent Reliability Playbook 2026" (~May 2026); morphllm, "Context Engineering: Why More Tokens Makes Agents Worse" (Feb 2026).

### Programmatic tool calling — [emerging]
The model orchestrates tools by **executing code**; the code consumes intermediate tool outputs and returns only the final processed result to the context window — so most tool I/O never enters context.
- *Why it fits:* the precise mechanism for cheap deterministic checks — the linter-like checks run as code; only their verdict costs tokens.
- *Source:* "LOCA-bench: Benchmarking Language Agents Under Controllable and Extreme Context Growth," arXiv:2602.07962 (describes Anthropic's programmatic tool calling, context editing, context awareness, and memory tools).

### Just-in-time retrieval — [standard]
Keep lightweight identifiers (paths, stored queries, links) and load data on demand at runtime, rather than pre-loading everything (the Claude Code model).
- *Why it fits:* "retrieve only what discriminates" is just-in-time retrieval.
- *Source:* Anthropic, "Effective context engineering for AI agents" (2025).

---

## 5. Evaluation
### Small-model (SLM) evaluators — [emerging]
Small-model evaluators reported at 10–100× lower cost than LLM-as-judge, enabling high-frequency scoring.
- *Why it fits:* cheap automated scoring for the eval ladder and for high-frequency checks.
- *Source:* Galileo, "8 Best AI Agent Debugging & Root Cause Analysis Tools" (Mar 2026).

### Trajectory tracing / agent observability — [standard]
Capture and reconstruct every decision in an agent's (non-deterministic) execution path.
- *Why it fits:* the controller's trajectory is both the transparency artifact and the eval substrate.
- *Source:* Galileo (Mar 2026).

---

## How this maps to the build (what to reach for in a first slice)
- **Controller:** hand-rolled, legible (owns the loop) — not a framework yet.
- **Checks:** deterministic, run via **programmatic tool calling** (the cost mechanism).
- **Evidence object:** an **Investigation-Graph**-style structure (transparency + the fishbone + ruled-out branches).
- **Retrieval (optional in the spike):** **GraphRAG** over the typed corpus.
- **Baselines to beat:** (1) a bare LLM with all data in context; (2) a runbook-following ReAct agent (the AI-SRE shape).
- **Headline metric:** evidence precision/recall (evidence-F1) and tokens-per-resolved-case, on a held-out case set.

---

## Sources
*Primary (arXiv / vendor engineering) vs directional (market listicles) noted inline above.*

**Diagnostic patterns**
- ODSC, "Why Cross-Domain Root-Cause Analysis is Still Unsolved — and How Agentic AI Changes That," Medium, Mar 2026. https://odsc.medium.com/why-cross-domain-root-cause-analysis-is-still-unsolved-and-how-agentic-ai-changes-that-08644daecb11
- Balasubramanian, "From Signals to Root Cause: A Systems Architecture for Agentic AI in Observability," IJISAE 14(1s), 2026. https://ijisae.org/index.php/IJISAE/article/view/8336
- Augment Code, "AI SRE: The 2026 Guide to AI-Powered Site Reliability Engineering," ~May 2026. https://www.augmentcode.com/guides/ai-sre-ai-powered-site-reliability-engineering
- Wang, "AgentTrace: Causal Graph Tracing for Root Cause Analysis in Deployed Multi-Agent Systems," arXiv:2603.14688, Mar 2026 (ICLR 2026 AIWILD workshop). https://arxiv.org/abs/2603.14688
- Galileo, "8 Best AI Agent Debugging & Root Cause Analysis Tools," Mar 2026. https://galileo.ai/blog/best-ai-agent-debugging-root-cause-analysis-tools

**Frameworks / control**
- monday.com, "AI agent frameworks that actually work for cross-functional teams in 2026," Apr 2026. https://monday.com/blog/ai-agents/ai-agent-frameworks/
- Alice Labs, "Best AI Agent Frameworks 2026: 7 Production-Tested Rankings," ~May 2026. https://alicelabs.ai/en/insights/best-ai-agent-frameworks-2026
- DataCamp, "The Best AI Agents in 2026," ~May 2026. https://www.datacamp.com/blog/best-ai-agents
- gurusup, "Best Multi-Agent Frameworks 2026," May 2026. https://gurusup.com/blog/best-multi-agent-frameworks-2026

**Retrieval**
- Rane, "Next-Generation Agentic RAG with LangGraph (2026 Edition)," Medium, Mar 2026. https://medium.com/@vinodkrane/next-generation-agentic-rag-with-langgraph-2026-edition-d1c4c068d2b8
- "Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG," arXiv:2501.09136, Jan 2026. https://arxiv.org/abs/2501.09136
- TIMEWELL, "RAG Complete Guide 2026: GraphRAG, Agentic Memory, Knowledge Runtime, and Enterprise AI Data Architecture," Jan 2026. https://timewell.jp/en/columns/ai-rag-agi
- techment, "10 RAG Architectures in 2026: Enterprise Use Cases & Strategy," May 2026. https://www.techment.com/blogs/rag-architectures-enterprise-use-cases-2026/
- Google Cloud, "Agentic AI use case: Multimodal GraphRAG resource orchestration," Apr 2026. https://docs.cloud.google.com/architecture/agentic-ai-multimodal-graph-rag-resource-orchestration

**Context engineering / cost**
- Anthropic, "Effective context engineering for AI agents," 2025. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- digitalapplied, "Context Engineering: Agent Reliability Playbook 2026," ~May 2026. https://www.digitalapplied.com/blog/context-engineering-agent-reliability-playbook-2026
- morphllm, "Context Engineering: Why More Tokens Makes Agents Worse," Feb 2026. https://www.morphllm.com/context-engineering
- "LOCA-bench: Benchmarking Language Agents Under Controllable and Extreme Context Growth," arXiv:2602.07962. https://arxiv.org/abs/2602.07962
- Atlan, "Context Architecture for AI Agents: A Complete 2026 Guide," Apr 2026. https://atlan.com/know/context-architecture-for-ai-agents/

*Compiled 2026-06-15. Market figures and "fastest-growing/standard" claims are vendor-reported — re-verify before any external-facing use.*
