"""Deterministic lidar checks (spec §6.5) — pure code over telemetry/config.

Each check is cheap, auditable, and returns a structured `dict` (never prose-only):
the controller calls them through `Environment.run_check`, the result is logged, and
the LLM interprets it into evidence. The six checks are the discriminators from the
worked example (§3.3); new checks are added per fault as the case set grows.

Functions here take already-fetched data (a signal's `TimeSeries`, the config nodes,
an event time) so they stay pure and unit-testable; `LidarEnvironment.run_check`
is the thin data-access layer that feeds them.
"""

from __future__ import annotations

import statistics as st

from dh.generator.signatures import pearson_r
from dh.schemas import Node, TimeSeries


def _recent(series: TimeSeries, k: int = 5) -> float:
    return st.mean(series.v[-k:])


def _baseline(series: TimeSeries, k: int = 8) -> float:
    return st.mean(series.v[:k])


def config_diff(config_nodes: list[Node]) -> dict:
    """Changed config keys vs baseline (§3.3 → "no relevant change" for case #1)."""
    changed = []
    for n in config_nodes:
        cur, base = n.props.get("value"), n.props.get("baseline")
        if cur != base:
            changed.append({"key": n.name, "from": base, "to": cur})
    return {
        "check": "config_diff",
        "changed": changed,
        "any_change": bool(changed),
        "summary": "no relevant config change" if not changed
        else f"{len(changed)} config key(s) changed: {[c['key'] for c in changed]}",
    }


def spatial_intensity_check(region_series: list[TimeSeries]) -> dict:
    """Spread of per-region intensity now → localized (window) vs uniform (§3.3)."""
    finals = [s.v[-1] for s in region_series]
    spread = (max(finals) - min(finals)) if finals else 0.0
    localized = spread > 0.15  # a single dim region stands out
    return {
        "check": "spatial_intensity_check",
        "spread": spread,
        "n_regions": len(finals),
        "localized": localized,
        "summary": "intensity drop is localized (suggests window/optics)" if localized
        else "intensity drop is uniform across regions (rules out window contamination)",
    }


def temp_correlation_check(
    signal_a: TimeSeries, signal_b: TimeSeries, threshold: float = 0.7,
) -> dict:
    """Pearson r between two signals — the laser-aging vs TEC discriminator (§3.3).

    For TEC degradation, intensity falls as diode temperature rises ⇒ strong
    negative r. `correlated` keys on |r|; `sign` carries the direction.
    """
    r = pearson_r(signal_a.v, signal_b.v)
    return {
        "check": "temp_correlation_check",
        "signal_a": signal_a.signal,
        "signal_b": signal_b.signal,
        "r": r,
        "abs_r": abs(r),
        "sign": "negative" if r < 0 else "positive",
        "correlated": abs(r) >= threshold,
        "summary": f"{signal_a.signal} vs {signal_b.signal}: r={r:.2f} "
        f"({'correlated' if abs(r) >= threshold else 'no correlation'})",
    }


def tec_load_check(tec_current: TimeSeries, limit: float) -> dict:
    """Current TEC load vs its limit (§3.3 → "92% of limit" for case #1)."""
    current = tec_current.v[-1]
    frac = current / limit if limit else 0.0
    return {
        "check": "tec_load_check",
        "current": current,
        "limit": limit,
        "frac_of_limit": frac,
        "at_limit": frac >= 0.85,
        "summary": f"TEC current {current:.2f} A is {frac * 100:.0f}% of the {limit} A limit",
    }


def channel_sanity_check(series: TimeSeries, min_var: float = 1e-6) -> dict:
    """Flag a stuck/lying channel: ~zero variance under varying load (§3.3, B5)."""
    var = st.pvariance(series.v) if len(series.v) > 1 else 0.0
    stuck = var <= min_var
    return {
        "check": "channel_sanity_check",
        "signal": series.signal,
        "variance": var,
        "stuck": stuck,
        "summary": f"{series.signal} variance≈{var:.2e} → "
        f"{'unreliable (stuck channel)' if stuck else 'looks live'}",
    }


def _onset_changepoint(series: TimeSeries) -> float:
    """Estimate degradation onset: the split minimizing a flat-pre / linear-post fit.

    Models v[:s] as a constant and v[s:] as a line; the breakpoint that minimises
    total squared error is where a gentle ramp departs the flat baseline, recovering
    the true onset better than a fixed-threshold first-crossing.
    """
    t, v = series.t, series.v
    n = len(v)
    if n < 6:
        return t[0]
    best_t, best_sse = t[0], float("inf")
    for s in range(3, n - 2):  # need ≥3 pre points and ≥3 post points
        pre = v[:s]
        pre_mean = sum(pre) / len(pre)
        sse = sum((x - pre_mean) ** 2 for x in pre)
        # linear LSQ on the post segment
        ts, vs = t[s:], v[s:]
        m = len(ts)
        mt, mv = sum(ts) / m, sum(vs) / m
        denom = sum((ti - mt) ** 2 for ti in ts)
        if denom > 0:
            slope = sum((ti - mt) * (vi - mv) for ti, vi in zip(ts, vs)) / denom
            intercept = mv - slope * mt
            sse += sum((vi - (slope * ti + intercept)) ** 2 for ti, vi in zip(ts, vs))
        else:
            sse += sum((vi - mv) ** 2 for vi in vs)
        if sse < best_sse:
            best_sse, best_t = sse, t[s]
    return best_t


def onset_vs_event_check(series: TimeSeries, event_t: float, event_label: str = "event") -> dict:
    """Order degradation onset against a salient event → demote a trigger (§3.3, D1)."""
    onset_t = _onset_changepoint(series)
    predates = onset_t < event_t
    return {
        "check": "onset_vs_event_check",
        "signal": series.signal,
        "onset_t": onset_t,
        "event_t": event_t,
        "event_label": event_label,
        "onset_predates_event": predates,
        "summary": f"degradation onset≈t={onset_t:g} "
        f"{'precedes' if predates else 'follows'} {event_label} at t={event_t:g}"
        + (f" → {event_label} is coincident, not causal" if predates else ""),
    }
