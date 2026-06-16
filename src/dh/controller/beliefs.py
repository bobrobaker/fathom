"""Belief update — deterministic aggregation, LLM judgment (spec §6.4).

The LLM assigns each evidence→hypothesis link a polarity and a weight ≈
|log-likelihood-ratio|. This layer does the arithmetic: a hypothesis's log-odds is
its prior plus Σ(sign·weight) over its links, and confidence = sigmoid(log-odds).
Keeping aggregation here (not in the model) makes mixed evidence (A1) and shared
evidence (A2) fall out mechanically and keeps the result auditable.
"""

from __future__ import annotations

import math

from dh.schemas import InvestigationGraph, Hypothesis

RULED_OUT_CONF = 0.25   # below this a hypothesis is considered ruled out
SUPPORTED_CONF = 0.60   # a corroborated (but not necessarily leading) hypothesis


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def confidence(h: Hypothesis) -> float:
    return sigmoid(h.log_odds)


def update_beliefs(ig: InvestigationGraph, prior: float = 0.0) -> InvestigationGraph:
    """Recompute every hypothesis's log-odds from the current links, then set status."""
    totals = {h.id: prior for h in ig.hypotheses}
    for ln in ig.links:
        if ln.hypothesis_id in totals:
            totals[ln.hypothesis_id] += (1.0 if ln.polarity == "+" else -1.0) * ln.weight
    for h in ig.hypotheses:
        h.log_odds = totals[h.id]

    ranked = sorted(ig.hypotheses, key=lambda h: h.log_odds, reverse=True)
    for i, h in enumerate(ranked):
        c = sigmoid(h.log_odds)
        if c < RULED_OUT_CONF:
            h.status = "ruled_out"
        elif i == 0 and c > 0.5:
            h.status = "leading"
        elif c >= SUPPORTED_CONF:
            h.status = "supported"
        else:
            h.status = "open"
    return ig


def leader(ig: InvestigationGraph) -> tuple[Hypothesis | None, float, float]:
    """Return (top hypothesis, its confidence, margin over the runner-up)."""
    if not ig.hypotheses:
        return None, 0.0, 0.0
    ranked = sorted(ig.hypotheses, key=lambda h: h.log_odds, reverse=True)
    top = ranked[0]
    top_c = sigmoid(top.log_odds)
    runner_c = sigmoid(ranked[1].log_odds) if len(ranked) > 1 else 0.0
    return top, top_c, top_c - runner_c
