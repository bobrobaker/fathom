# Benchmark tests retrieval/abstention/grounding — not the differential; MuSiQue footnoted, FEVER deferred

**Date:** 2026-06-16 · **Status:** accepted · **Milestones:** M4.5, M8 · **Refines:** [2026-06-16-benchmark-scoped-harness-first.md](2026-06-16-benchmark-scoped-harness-first.md) · **Supersedes:** the *competitiveness* framing in `handoffs/2026-06-16-spike-audit-response.md` A5/B9

## Decision

Scope the MuSiQue benchmark to a **footnote**: report it as a check on (a) iterative,
informativeness-gated **retrieval**, (b) **calibrated abstention** on unanswerable items,
and (c) **citation grounding** — and report **abstention + grounding, not EM alone**. Do
**not** present it as evidence that the controller's *differential structure* generalizes.
A differential-shaped second domain (FEVER-style claim verification: supports / refutes /
not-enough-info) is the **full-build** path to a real generalization claim — deferred, now
on the roadmap (Phase 4) and `full_build_spec.md` §5/§10.

## Why

- **MuSiQue is a compositional chain, not a differential.** Multi-hop QA decomposes →
  retrieves the bridge fact → the hop is settled. There is no rival-hypothesis
  adjudication, so the hypothesis differential / VOI / log-odds machinery is *carried
  along, not exercised*. A strong score proves "iterative agentic retrieval works" (a known
  result), not "the differential generalizes."
- **QA has no deterministic evidence layer.** The harness's signature is reasoning (LLM)
  over *deterministic* evidence (checks). In QA, relevance is itself a judgment — the belief
  weights have nothing computed underneath. (Cross-verified across two design chats.)
- **This corrects the audit's framing.** `spike-audit-response.md` A5/B9 treated the
  benchmark as a *competitiveness* question ("run n=20, keep if competitive") and inherited
  the spec's "shared core" claim without checking it — which the load-bearing-claim lesson
  (`handoffs/2026-06-16-lesson-unverified-load-bearing-claims.md`) showed is false in code
  (`agentic_rag` shares only LLM plumbing, not the differential). The structural reframe
  supersedes the competitiveness one.
- **FEVER is the right generalization domain** because it exercises VOI + log-odds +
  abstention the way diagnosis does (conflicting evidence, supports/refutes/NEI), where
  multi-hop QA's loop collapses to one chain.

## Conditions / caveats

- Before leaning on (b), **verify MuSiQue actually ships usable unanswerable contrast
  items**; if not, scope the footnote to (a) + (c).
- The lidar finding (the portfolio core) stands independently of this track.
