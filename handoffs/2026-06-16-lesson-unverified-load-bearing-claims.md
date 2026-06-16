# Lesson — unverified load-bearing claims (spec↔code referential drift)

**Date:** 2026-06-16 · **For:** coding-agent intake (read before the next spike session) ·
**Status:** active lesson + 3 repo actions + 1 gated decision.
**Proposed home:** this entry in `docs/lessons.md`; the actions land in `CLAUDE.md`, the audit
template, and `tests/`.

## TL;DR (the rule)

A spec claim is not true because it is written down, named after the thing it claims, or read
past by a reviewer. Before relying on any **"shared / reused / same as / X minus Y / subset /
core / identical"** statement, **verify it structurally against the code** — shared symbols,
shared call paths — never **nominally** (matching names or comments). When the cleanest correct
implementation must diverge from what the spec literally says, **stop and surface the
divergence**; do not reconcile it silently by building a parallel thing and naming it to match
the doc.

## What happened (worked example — self-contained)

`spike_spec.md` (§0, §8.2) describes the benchmark track as running the controller's *"shared
retrieval/reasoning core"* — *"controller minus lidar checks."* **The code does not do this.**
`src/dh/eval/benchmark.py::controller_core` is a **separate ~20-line function** that shares only
LLM plumbing (`_call_json`, `get_backend`) with the real controller
`src/dh/controller/loop.py::diagnose`. It has **no hypothesis differential, no VOI selection, no
log-odds belief update, no Investigation Graph, and no abstention** (it forces an answer after 3
rounds). So a benchmark number cannot speak to whether the harness's *structure* generalizes —
the structure is not running. The differential / VOI / calibrated-stop machinery that the
project's thesis is *about* is exactly what `controller_core` dropped.

This survived a full completion audit (`handoffs/2026-06-16-spike-audit-response.md`), which
handled the benchmark only as a *competitiveness* question (A5/B9: "is it competitive at QA — run
n=20 or scope to report-only?") and accepted "shared core" without checking it against the code.

## Why it is hard to catch

- **Locally consistent, globally false.** The spec reads fine alone; `controller_core` reads fine
  alone. The defect lives only in the correspondence between them — invisible to artifact-at-a-time
  review.
- **Self-camouflaging.** The function is *named* `controller_core`. The name corroborates the
  claim, so a reader (or a `grep` for "core") confirms the very thing they should be testing. A
  name is a claim, not evidence.
- **Propagates by inheritance.** Spec author → auditor → next agent each took the prior framing as
  ground truth. A claim you have accepted as the frame is invisible to you.

## Why "surface your concerns" does not catch it

"Concern" is an affective trigger — it fires on what *looks* risky (arbitrary constants, smells,
gaps) and is blind to a clean, confident claim that is simply false. A tidy falsehood produces no
discomfort; it reads as one of the true sentences around it. The needed operation is **verify**,
not **worry**, and verification must be cross-artifact (claim ↔ referent) — which "surface
concerns" never directs.

## The fix, in reliability order

1. **By construction (strongest).** Make the claim un-driftable: one `diagnose()` parameterized
   over a hypothesis-space provider + evidence interpreter, called by both the lidar track and the
   QA track. Then "shared core" is tautological and there is no parallel function to misname.
2. **Executable claim (fires 100%).** Encode each load-bearing claim as a test (Action 3). A test
   asserting the two paths share their reasoning functions would have failed the moment
   `controller_core` was written separately.
3. **Prose governance (probabilistic backstop).** The `CLAUDE.md` rule in Action 1. Fires ~60–80%
   (instruct, not enforce) — a norm-setter, not the net.

## Actions (execute on intake)

**Action 1 — add to `CLAUDE.md` (implementer rule):**

> When implementing from a spec: if the cleanest correct implementation must diverge from what the
> spec literally says — different structure, can't be the "subset"/"shared"/"core" thing it is
> described as, a claim that won't hold — STOP and surface the divergence before writing code. Do
> not reconcile it silently by building a parallel thing and naming it to match the doc. "I had to
> depart from the spec to make this work" is a required, surfaced event. A name that asserts a
> property does not establish it; verify "shared/reused/same/subset" claims structurally (shared
> symbols, shared call paths), never nominally.

**Action 2 — replace "surface your concerns" in the audit template with:**

> Verify the claims; don't just report what concerns you.
> 1. Inventory the load-bearing claims (every statement the thesis or architecture's validity rests
>    on). For each, cite the code that makes it true — quote the claim, cite the function/lines. If
>    you can't, mark **UNVERIFIED**. Clean and confident is not evidence of true.
> 2. Treat every "shared / reused / same as / X minus Y / subset / core / identical" as a claim
>    about the call graph; verify shared symbols / call paths. A matching name or comment is not
>    verification.
> 3. Read adversarially: assume each claim is a comforting fiction until the code disproves it; ask
>    "if this were false, what would the code look like?" and check for that shape.
> 4. Report **UNVERIFIED** and **FALSE** claims as a ranked list, separate from and above
>    "concerns."

**Action 3 — add claim-tests (`tests/`):**

- A test asserting the benchmark and controller reasoning paths share — or, after the decision
  below, explicitly do **not** share — their core functions, so the spec's "shared core" language
  is executable rather than asserted.
- A test pinning the controller's IG read-path (propose/score reads the current
  `InvestigationGraph`), so that load-bearing behavior is also tripwired.

## Gated decision (needs Bolun)

The benchmark's "shared core" claim is currently false in code. Two ways to make spec and code
agree:

- **(a) Rescope now (recommended for the spike).** Rewrite §0/§8.2 to drop "shared core"; state
  plainly that the benchmark is a generic agentic-retrieval sanity check sharing only plumbing with
  the diagnostic controller, and is report-only (T4 permits) — or cut it. Cheap; removes a
  credibility landmine on a test-architecture portfolio.
- **(b) Refactor (full-build).** Parameterize `diagnose()` so the same loop runs both domains; the
  claim becomes true by construction and the benchmark validly tests generalization. Stronger
  story, real work — roadmap, not spike.

**▶ Reply:**

## General intake

This is not only about the benchmark. Apply the same claim-verification discipline to every
"shared / reused / identical / minus / subset" statement anywhere in the repo and its docs — each
is a claim about the call graph until proven against it.
