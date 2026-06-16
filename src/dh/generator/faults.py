"""Per-fault forward-effects models (spec §5.1–5.2).

A fault hook maps an injected fault to its telemetry signature plus the diagnostic
*facts* (root cause, causal chain, decoy, lying channel, trigger, load-bearing
evidence) that `compose` turns into a case and its hidden ground truth. Case #1
(TEC degradation) is authored to depth here; the rest are named hooks filled in at
M7. Everything is deterministic given the passed RNG.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dh.generator import signatures as sig
from dh.schemas import TimeSeries

# --- shared case-window timing (days; 0 = window start, NOW = now) ------------
WINDOW_START = 0.0
WINDOW_END = 10.0
NOW = 10.0
STEP = 0.25
ONSET = 4.0            # degradation begins 6 days before now
REBOOT_T = 8.0         # scheduled reboot 2 days before now (the trigger)
SERVICE_T = -390.0     # last thermal service ~400 days ago (outside the window)
WINDOW_CLEAN_T = 5.0   # window cleaned 5 days ago (a tried diagnostic action)

# --- TEC degradation forward model (the worked example, §3.2) -----------------
SETPOINT_C = 25.0
TEC_LIMIT_A = 2.5

# (baseline, now) targets straight from the worked-example telemetry table.
_DIODE = (25.2, 31.5)   # above setpoint — key
_INTENS = (1.00, 0.85)  # -15%, correlates with diode temp
_TEC = (1.2, 2.3)       # 92% of the 2.5 A limit — key
_POWER = (48.0, 42.0)   # -12% (also consistent with aging)
_DARK = (1.00, 1.20)    # mildly elevated (secondary)
_RANGE = (120.0, 110.0) # the symptom (-8%)
_AMBIENT = 22.0         # nominal (rules out external heat)
_DET_TEMP_STUCK = 25.0  # flatlined lying channel
_N_REGIONS = 4

# Noise levels tuned so intensity↔diode-temp lands at |r| ≈ 0.9 (see test_generator).
_NOISE = {
    "diode": 0.12, "intensity": 0.030, "tec": 0.03, "power": 0.35,
    "dark": 0.012, "range": 0.6, "ambient": 0.12, "region": 0.02,
}


@dataclass
class FaultFacts:
    """The hidden diagnostic truth a fault injects (consumed by `compose`)."""
    root_cause: str | None
    causal_chain: list[str]
    answer_type: str = "cause"
    decoys: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    trigger: str | None = None
    load_bearing_evidence: list[str] = field(default_factory=list)
    lying_channel_signal: str | None = None  # which signal is the stuck channel
    symptom: str | None = None               # KPI symptom text (None ⇒ compose default)
    error: tuple[str, str, list[str]] | None = None  # (id, text, refs) for the error log
    exclude_artifacts: list[str] = field(default_factory=list)  # corpus items this fault drops
                                             # (e.g. a diagnostic action whose conclusion would
                                             # contradict this fault — keeps the case consistent)


def _slope(pair: tuple[float, float]) -> float:
    """Per-°C coupling slope from a (baseline, now) target, referenced to diode swing."""
    base, now = pair
    return (now - base) / (_DIODE[1] - _DIODE[0])


def tec_degradation(seed_rng) -> tuple[list[TimeSeries], FaultFacts]:
    """TEC losing capacity → diode over-temp → optical output ↓ → intensity ↓ → range ↓.

    Diode temperature is the physical driver; intensity / tec_current / power /
    dark_count / range are derived from it (a correlated family), which is what
    makes `temp_correlation_check` discriminate TEC from laser aging. detector_temp
    is flatlined (the lying channel); ambient and config are nominal.
    """
    t = sig.time_grid(WINDOW_START, WINDOW_END, STEP)
    rng = seed_rng

    diode = sig.ramp("laser_diode_temp_C", t, _DIODE[0], _DIODE[1], ONSET,
                     _NOISE["diode"], rng, spec={"min": 24.0, "max": 26.0, "units": "C"})
    intensity = sig.derived("mean_return_intensity", diode, _INTENS[0], _slope(_INTENS),
                            _DIODE[0], _NOISE["intensity"], rng,
                            spec={"min": 0.90, "max": 1.10, "units": "norm"})
    tec_current = sig.derived("tec_current_A", diode, _TEC[0], _slope(_TEC), _DIODE[0],
                              _NOISE["tec"], rng, spec={"min": 0.0, "max": TEC_LIMIT_A, "units": "A"})
    power = sig.derived("laser_power_mW", diode, _POWER[0], _slope(_POWER), _DIODE[0],
                        _NOISE["power"], rng, spec={"min": 45.0, "max": 52.0, "units": "mW"})
    dark = sig.derived("dark_count_rate", diode, _DARK[0], _slope(_DARK), _DIODE[0],
                       _NOISE["dark"], rng, spec={"min": 0.5, "max": 1.5, "units": "norm"})
    rng_m = sig.derived("effective_max_range_m", diode, _RANGE[0], _slope(_RANGE), _DIODE[0],
                        _NOISE["range"], rng, spec={"min": 115.0, "max": 130.0, "units": "m"})
    detector_temp = sig.flat("detector_temp_C", t, _DET_TEMP_STUCK, 0.0, rng,
                             spec={"min": 20.0, "max": 30.0, "units": "C"})  # stuck, var≈0
    ambient = sig.flat("ambient_temp_C", t, _AMBIENT, _NOISE["ambient"], rng,
                       spec={"min": 15.0, "max": 30.0, "units": "C"})

    telemetry = [rng_m, intensity, power, diode, tec_current, detector_temp, dark, ambient]

    # intensity-by-region: a uniform drop (rules out window contamination, §3.2).
    for i in range(_N_REGIONS):
        telemetry.append(
            sig.derived(f"region_intensity_{i}", diode, _INTENS[0], _slope(_INTENS),
                        _DIODE[0], _NOISE["region"], rng, spec={"units": "norm"})
        )

    facts = FaultFacts(
        root_cause="part.tec",
        causal_chain=["part.tec", "metric.diode_temp", "metric.laser_power",
                      "metric.intensity", "kpi.effective_range"],
        decoys=["part.laser_module"],
        conflicts=["metric.detector_temp", "log.reboot"],
        trigger="log.reboot",
        load_bearing_evidence=["tec_load_check", "temp_correlation_check",
                               "metric.diode_temp", "onset_vs_event_check", "err.tec_load"],
        lying_channel_signal="detector_temp_C",
        error=("err.tec_load",
               "TEC_LOAD_HIGH: intermittent, increasing in frequency over the window.",
               ["sub.thermal", "part.tec"]),
    )
    return telemetry, facts


def _regions(driver, base, slope, ref, rng):
    return [sig.derived(f"region_intensity_{i}", driver, base, slope, ref,
                        _NOISE["region"], rng, spec={"units": "norm"}) for i in range(_N_REGIONS)]


def laser_aging(seed_rng) -> tuple[list[TimeSeries], FaultFacts]:
    """Laser power aging (#2): output power decays with NO thermal signature — the
    symmetry case to TEC. Diode temp and TEC current stay nominal, so intensity does
    NOT correlate with temperature; the discriminator is the *absence* of thermal signs.
    """
    t = sig.time_grid(WINDOW_START, WINDOW_END, STEP)
    rng = seed_rng
    power = sig.ramp("laser_power_mW", t, _POWER[0], _POWER[1], ONSET, _NOISE["power"], rng,
                     spec={"min": 45.0, "max": 52.0, "units": "mW"})
    # intensity tracks POWER (not temperature) — the key difference from TEC
    intensity = sig.derived("mean_return_intensity", power, _INTENS[0],
                            (_INTENS[1] - _INTENS[0]) / (_POWER[1] - _POWER[0]), _POWER[0],
                            _NOISE["intensity"], rng, spec={"min": 0.90, "max": 1.10, "units": "norm"})
    rng_m = sig.derived("effective_max_range_m", power, _RANGE[0],
                        (_RANGE[1] - _RANGE[0]) / (_POWER[1] - _POWER[0]), _POWER[0],
                        _NOISE["range"], rng, spec={"min": 115.0, "max": 130.0, "units": "m"})
    diode = sig.flat("laser_diode_temp_C", t, _DIODE[0], _NOISE["diode"], rng,
                     spec={"min": 24.0, "max": 26.0, "units": "C"})         # nominal
    tec_current = sig.flat("tec_current_A", t, _TEC[0], _NOISE["tec"], rng,
                           spec={"min": 0.0, "max": TEC_LIMIT_A, "units": "A"})  # nominal
    detector_temp = sig.flat("detector_temp_C", t, 25.0, 0.08, rng,
                             spec={"min": 20.0, "max": 30.0, "units": "C"})  # live, not stuck
    dark = sig.flat("dark_count_rate", t, _DARK[0], _NOISE["dark"], rng,
                    spec={"min": 0.5, "max": 1.5, "units": "norm"})
    ambient = sig.flat("ambient_temp_C", t, _AMBIENT, _NOISE["ambient"], rng,
                       spec={"min": 15.0, "max": 30.0, "units": "C"})
    telemetry = [rng_m, intensity, power, diode, tec_current, detector_temp, dark, ambient]
    telemetry += _regions(power, _INTENS[0], (_INTENS[1] - _INTENS[0]) / (_POWER[1] - _POWER[0]),
                          _POWER[0], rng)
    facts = FaultFacts(
        root_cause="part.laser_module",
        causal_chain=["part.laser_module", "metric.laser_power", "metric.intensity",
                      "kpi.effective_range"],
        decoys=["part.tec"],                       # TEC looks similar but is ruled out
        conflicts=["log.reboot"], trigger="log.reboot",
        load_bearing_evidence=["temp_correlation_check", "tec_load_check",
                               "metric.laser_power", "onset_vs_event_check"],
    )
    return telemetry, facts


def no_clean_cause(seed_rng) -> tuple[list[TimeSeries], FaultFacts]:
    """No clean cause (#5, E1): an intermittent dip that self-resolves, every channel
    nominal. The honest answer is ABSTAIN — nothing crosses threshold, the reboot is a
    coincidence, not a cause. The anti-confabulation guard.
    """
    t = sig.time_grid(WINDOW_START, WINDOW_END, STEP)
    rng = seed_rng
    # a brief transient dip around the reboot that recovers (self-resolved)
    def transient(base, dip):
        return [base - dip if REBOOT_T - 0.5 <= ti <= REBOOT_T + 0.5 else base for ti in t]
    rng_m = TimeSeries(signal="effective_max_range_m", t=list(t),
                       v=[v + rng.gauss(0, 0.8) for v in transient(120.0, 2.0)],
                       spec={"min": 115.0, "max": 130.0, "units": "m"})
    intensity = TimeSeries(signal="mean_return_intensity", t=list(t),
                           v=[v + rng.gauss(0, 0.02) for v in transient(1.0, 0.03)],
                           spec={"min": 0.90, "max": 1.10, "units": "norm"})
    diode = sig.flat("laser_diode_temp_C", t, _DIODE[0], _NOISE["diode"], rng,
                     spec={"min": 24.0, "max": 26.0, "units": "C"})
    tec_current = sig.flat("tec_current_A", t, _TEC[0], _NOISE["tec"], rng,
                           spec={"min": 0.0, "max": TEC_LIMIT_A, "units": "A"})
    power = sig.flat("laser_power_mW", t, _POWER[0], _NOISE["power"], rng,
                     spec={"min": 45.0, "max": 52.0, "units": "mW"})
    detector_temp = sig.flat("detector_temp_C", t, 25.0, 0.08, rng,
                             spec={"min": 20.0, "max": 30.0, "units": "C"})
    dark = sig.flat("dark_count_rate", t, _DARK[0], _NOISE["dark"], rng,
                    spec={"min": 0.5, "max": 1.5, "units": "norm"})
    ambient = sig.flat("ambient_temp_C", t, _AMBIENT, _NOISE["ambient"], rng,
                       spec={"min": 15.0, "max": 30.0, "units": "C"})
    telemetry = [rng_m, intensity, power, diode, tec_current, detector_temp, dark, ambient]
    telemetry += _regions(intensity, 1.0, 0.0, 1.0, rng)  # flat, uniform
    facts = FaultFacts(
        root_cause=None, answer_type="abstain", causal_chain=[],
        conflicts=["log.reboot"], trigger="log.reboot", load_bearing_evidence=[],
        symptom="An intermittent range fluctuation was reported around the last maintenance. "
                "Determine the root cause, or whether there is a single clean cause at all.",
    )
    return telemetry, facts


def window_contamination(seed_rng) -> tuple[list[TimeSeries], FaultFacts]:
    """Window contamination (#3): a spatially-clustered intensity loss — one region dims
    sharply while the rest stay nominal, and there is NO thermal/laser signature. The
    discriminator is `spatial_intensity_check` (localized); reasoning from absence (A3)
    rules out the thermal/laser decoys.
    """
    t = sig.time_grid(WINDOW_START, WINDOW_END, STEP)
    rng = seed_rng
    diode = sig.flat("laser_diode_temp_C", t, _DIODE[0], _NOISE["diode"], rng,
                     spec={"min": 24.0, "max": 26.0, "units": "C"})       # nominal
    tec_current = sig.flat("tec_current_A", t, _TEC[0], _NOISE["tec"], rng,
                           spec={"min": 0.0, "max": TEC_LIMIT_A, "units": "A"})  # nominal
    power = sig.flat("laser_power_mW", t, _POWER[0], _NOISE["power"], rng,
                     spec={"min": 45.0, "max": 52.0, "units": "mW"})       # nominal
    detector_temp = sig.flat("detector_temp_C", t, 25.0, 0.08, rng,
                             spec={"min": 20.0, "max": 30.0, "units": "C"})
    dark = sig.flat("dark_count_rate", t, _DARK[0], _NOISE["dark"], rng,
                    spec={"min": 0.5, "max": 1.5, "units": "norm"})
    ambient = sig.flat("ambient_temp_C", t, _AMBIENT, _NOISE["ambient"], rng,
                       spec={"min": 15.0, "max": 30.0, "units": "C"})
    # mean intensity & range drop modestly (one bad region pulls the average down)
    intensity = sig.ramp("mean_return_intensity", t, 1.00, 0.92, ONSET, _NOISE["intensity"], rng,
                         spec={"min": 0.90, "max": 1.10, "units": "norm"})
    rng_m = sig.ramp("effective_max_range_m", t, 120.0, 114.0, ONSET, _NOISE["range"], rng,
                     spec={"min": 115.0, "max": 130.0, "units": "m"})
    telemetry = [rng_m, intensity, power, diode, tec_current, detector_temp, dark, ambient]
    # region 0 dims sharply (the contaminated patch); the rest stay near nominal
    telemetry.append(sig.ramp("region_intensity_0", t, 1.0, 0.55, ONSET, _NOISE["region"], rng,
                              spec={"units": "norm"}))
    for i in range(1, _N_REGIONS):
        telemetry.append(sig.flat(f"region_intensity_{i}", t, 1.0, _NOISE["region"], rng,
                                  spec={"units": "norm"}))
    facts = FaultFacts(
        root_cause="part.window",
        causal_chain=["part.window", "metric.intensity", "kpi.effective_range"],
        decoys=["part.tec", "part.laser_module"],   # thermal/laser look plausible, ruled out
        conflicts=["log.reboot"], trigger="log.reboot",
        load_bearing_evidence=["spatial_intensity_check", "temp_correlation_check",
                               "tec_load_check"],
        # the "window cleaned, no improvement" action would contradict a window cause
        exclude_artifacts=["act.window_clean"],
    )
    return telemetry, facts


# Registry: fault name → forward model. Stub faults are named hooks (filled at M7).
FAULTS = {
    "tec_degradation": tec_degradation,
    "laser_aging": laser_aging,
    "window_contamination": window_contamination,
    "no_clean_cause": no_clean_cause,
}
