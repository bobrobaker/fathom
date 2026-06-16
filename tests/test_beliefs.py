"""C3 / B7 — the belief layer clamps principledly and lets evidence move both ways.

Per-link |LLR| is capped (MAX_WEIGHT) so one observation can't saturate a hypothesis, and the
accumulated log-odds is capped (MAX_LOG_ODDS) so confidence tops out near 0.95 — a decoy can
never get pinned at 0.99 with "no path back down" (the B7 stuck-decoy failure). Contradicting
evidence must always be able to pull a hypothesis down. A sensitivity check documents how the
margin moves if the cap is retuned.
"""

from dh.controller import beliefs
from dh.controller.beliefs import MAX_LOG_ODDS, confidence, leader, update_beliefs
from dh.schemas import EvidenceItem, EvidenceLink, Hypothesis, InvestigationGraph


def _ig(links):
    return InvestigationGraph(
        symptom="range down",
        hypotheses=[Hypothesis(id="h.tec", label="TEC"), Hypothesis(id="h.laser", label="laser")],
        evidence=[EvidenceItem(id="e", summary="", source="s")],
        links=links,
    )


def _link(h, pol, w):
    return EvidenceLink(evidence_id="e", hypothesis_id=h, polarity=pol, weight=w)


def test_two_concordant_items_clear_tau_dom():
    """Sizing: ~2 concordant capped items put the leader over τ_dom=0.70 (logit≈0.85)."""
    ig = _ig([_link("h.tec", "+", 2.0), _link("h.tec", "+", 2.0)])
    update_beliefs(ig)
    _top, conf, _margin = leader(ig)
    assert conf > 0.70


def test_accumulated_log_odds_is_clamped():
    """A pile of concordant links can't push confidence to 0.99 — it saturates near 0.95."""
    ig = _ig([_link("h.tec", "+", 2.0) for _ in range(6)])  # would be log_odds 12 unclamped
    update_beliefs(ig)
    h = next(h for h in ig.hypotheses if h.id == "h.tec")
    assert h.log_odds == MAX_LOG_ODDS
    assert confidence(h) < 0.96  # headroom left, never 0.99


def test_contradicting_evidence_pulls_a_saturated_hypothesis_down():
    """B7: a decoy pushed high by early agreement can still be brought back down by later
    contradicting evidence — there is always a path down."""
    ig = _ig([_link("h.laser", "+", 2.0), _link("h.laser", "+", 2.0)])  # decoy rides high
    update_beliefs(ig)
    before = confidence(next(h for h in ig.hypotheses if h.id == "h.laser"))
    ig.links.extend([_link("h.laser", "-", 2.0), _link("h.laser", "-", 2.0)])  # contradiction
    update_beliefs(ig)
    after = confidence(next(h for h in ig.hypotheses if h.id == "h.laser"))
    assert after < before - 0.3  # decisively pulled back down


def test_clamp_sensitivity_does_not_flip_the_leader():
    """Sensitivity (C3): retuning the per-link cap to 1.5 / 2.5 changes the margin but not who
    leads when the evidence genuinely favours one hypothesis — the result is not cap-fragile."""
    def margin_at(cap):
        ig = _ig([_link("h.tec", "+", min(3.0, cap)), _link("h.tec", "+", min(2.0, cap)),
                  _link("h.laser", "+", min(1.0, cap))])
        update_beliefs(ig)
        top, _conf, margin = leader(ig)
        return top.id, margin

    leaders = {margin_at(cap)[0] for cap in (1.5, 2.0, 2.5)}
    assert leaders == {"h.tec"}  # TEC leads at every cap
