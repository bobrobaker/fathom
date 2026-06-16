# Diagnostic harness — document index & instructions for the coding agent

You are an LLM coding agent. Your job is to **build the spike** described in this doc set (and, later, the full build). Read the docs in the order below *before* writing any code.

---

## The documents (read in this order)

1. **`00_README_for_coding_agent.md`** — *this file.* Orientation, authority, and rules.
2. **`worked_sut_example_lidar.md`** — the concrete domain example. Read for intuition: what the lidar SUT is, the fault catalog, the difficulty catalog (mechanisms by ID — A1, B5, D1, …), and the fully-traced TEC case. **The TEC case is your golden fixture** → `fixtures/tec_case.json`.
3. **`ontology_typed_links.md`** — the data model: node and link types (graded by agent-use), edge confidence, and the three abstraction patterns (class/instance, reified n-ary relation, collection). Read for the corpus/graph schema. *Note: the ontology is provisional and will be re-evaluated after the spike — implement it as specced, but expect revision.*
4. **`spike_spec.md`** — **the authoritative specification.** Contracts (pydantic schemas), the environment interface, the controller loop, the baselines, the evals, and the acceptance criteria. When anything conflicts, this wins for the spike.
5. **`spike_build_plan.md`** — **the execution order.** Build in milestone order (M0 → M9); each milestone has a *done-when* gate that must pass before the next.
6. **`full_build_spec.md`** — the *next phase* after the spike. Read for where this is heading, but **do not build it yet** — the spike must produce its finding first, and that finding may revise the full build.
7. *(optional)* **`agent_architectures_2026.md`** — background on the 2026 agent landscape and why the design is shaped this way.
8. *(reference)* **`failure_mode_archetypes.md`** — the source of the difficulty-catalog archetype IDs (e.g., B7, A12). Consult when you need the meaning of a referenced archetype.

---

## Authority & priority

- **`spike_spec.md` is authoritative for *what* to build** (contracts, components, acceptance).
- **`spike_build_plan.md` is authoritative for *order*.**
- `worked_sut_example_lidar.md` and `ontology_typed_links.md` are the **design references** (intuition + schema).
- If a reference and the spec disagree, **follow the spec** and note the discrepancy.

---

## Non-negotiable rules

1. **Ground truth is eval-only.** `Case.ground_truth` must never enter the controller's context. Enforce it at the environment boundary — the environment never exposes it.
2. **Determinism.** Seed the generator; pin the model; low temperature. Re-runs reproduce numbers modulo LLM nondeterminism, which is **reported as variance over ≥3 runs**.
3. **Baselines must be strong and fair.** A weak `bare_llm` invalidates the result. Iterate its prompt until it is the best honest version.
4. **Capability-bound difficulty.** Every eval case must require something a context-dump cannot do — a check, a conditional query, a traversal, an action, or abstention. If reading the whole corpus once solves it, cut it. (`spike_spec.md` §5.2.)
5. **Success = the finding, not the win.** The spike ships if the eval is well-formed, the baselines fair, and the result reported cleanly — *whether or not the controller beats the baselines* (`spike_spec.md` §0, §9). **Never tune cases or baselines to manufacture a win.**
6. **Build the spine first.** M1 (the TEC case) and M4 (controller solves it) before anything else. Do not author the full case set before the controller solves case #1. Run the benchmark fit smoke-test (M4.5) early.

---

## What you deliver (spike)

A runnable repo per `spike_build_plan.md` producing:
- the **bespoke eval report** — accuracy and capability families, `controller` vs the three baselines, with variance;
- the **early benchmark read** (M4.5) and, if competitive, the **MuSiQue result** (M8);
- the **Investigation Graph viewer** rendering case #1 across its steps.

`spike_spec.md` §9 defines **success** (S1–S4) and **confirmation** (T1–T4) separately. Aim for both; ship on success.
