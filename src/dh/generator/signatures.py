"""Telemetry signature templates (spec §5.2). Deterministic given a seeded RNG.

Each builder returns a `TimeSeries` over a shared time grid. The templates —
flat, ramp, step, drift, and `derived` (a signal coupled to a driver, the
mechanism behind correlated pairs) — cover every static signature the spike
needs. `dynamic` is the single hook for the temporal/bifurcation fault (D4); it
is a stub here, not exercised by case #1.

Noise is drawn from the passed RNG so a fixed seed reproduces every series
exactly. Time is in days over the case window (0 = window start, `end` = now).
"""

from __future__ import annotations

import math
import random

from dh.schemas import TimeSeries


def time_grid(start: float, end: float, step: float) -> list[float]:
    """Inclusive grid [start, end] at `step` spacing (rounded to avoid fp drift)."""
    n = round((end - start) / step)
    return [round(start + i * step, 6) for i in range(n + 1)]


def _jitter(value: float, noise: float, rng: random.Random) -> float:
    return value + (rng.gauss(0.0, noise) if noise > 0 else 0.0)


def flat(
    signal: str, t: list[float], value: float, noise: float,
    rng: random.Random, spec: dict | None = None,
) -> TimeSeries:
    """Constant signal (noise=0 ⇒ exactly flat — the stuck/lying-channel case)."""
    v = [_jitter(value, noise, rng) for _ in t]
    return TimeSeries(signal=signal, t=list(t), v=v, spec=spec)


def ramp(
    signal: str, t: list[float], baseline: float, final: float, onset: float,
    noise: float, rng: random.Random, spec: dict | None = None,
) -> TimeSeries:
    """Flat at `baseline` until `onset`, then linear to `final` at the window end."""
    end = t[-1]
    span = end - onset
    v = []
    for ti in t:
        if ti < onset or span <= 0:
            base = baseline
        else:
            base = baseline + (final - baseline) * (ti - onset) / span
        v.append(_jitter(base, noise, rng))
    return TimeSeries(signal=signal, t=list(t), v=v, spec=spec)


def step(
    signal: str, t: list[float], baseline: float, final: float, step_time: float,
    noise: float, rng: random.Random, spec: dict | None = None,
) -> TimeSeries:
    """Baseline before `step_time`, `final` after — a discrete config-style change."""
    v = [_jitter(baseline if ti < step_time else final, noise, rng) for ti in t]
    return TimeSeries(signal=signal, t=list(t), v=v, spec=spec)


def drift(
    signal: str, t: list[float], baseline: float, rate: float,
    noise: float, rng: random.Random, spec: dict | None = None,
) -> TimeSeries:
    """Linear drift from `baseline` at `rate` per day across the whole window."""
    start = t[0]
    v = [_jitter(baseline + rate * (ti - start), noise, rng) for ti in t]
    return TimeSeries(signal=signal, t=list(t), v=v, spec=spec)


def derived(
    signal: str, driver: TimeSeries, base: float, slope: float, ref: float,
    noise: float, rng: random.Random, spec: dict | None = None,
) -> TimeSeries:
    """Couple a signal to a `driver`: v = base + slope·(driver − ref) + noise.

    This is how a correlated pair is built (e.g. intensity falling as diode
    temperature rises). The noise term controls the realised correlation: more
    noise ⇒ |r| further below 1.
    """
    v = [_jitter(base + slope * (dv - ref), noise, rng) for dv in driver.v]
    return TimeSeries(signal=signal, t=list(driver.t), v=v, spec=spec)


def dynamic(
    signal: str, t: list[float], rng: random.Random, spec: dict | None = None,
) -> TimeSeries:
    """Stub for the temporal/bifurcation generator (D4); flat until authored at M7+."""
    return flat(signal, t, 0.0, 0.0, rng, spec=spec)


def pearson_r(xs: list[float], ys: list[float]) -> float:
    """Pearson correlation of two equal-length series (0.0 if degenerate)."""
    n = len(xs)
    if n == 0 or n != len(ys):
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return 0.0
    return sxy / math.sqrt(sxx * syy)
