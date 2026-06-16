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
CHANGE_T = 6.0         # a config / power-mode change 4 days before now (recent; the cause in #4/#8)

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
class CorpusItem:
    """A fault-specific corpus artifact (+ optional graph node): a diagnostic-action
    *result*, a fault-injected ticket / config-change / buried doc, or an error-log line.

    This is the per-fault corpus **delta** (spec §5; replaces the old `exclude_artifacts`
    stopgap and the special-cased `error` tuple). Diagnostic-action results and report
    conclusions are *facts about the specific fault* — they belong here, not in the shared
    structural corpus that every case carries. `node_type is None` ⇒ artifact only, no graph
    node (e.g. an error-log line, reachable via `read_errors` but not `traverse`).
    """
    id: str
    kind: str
    text: str
    node_type: str | None = None
    name: str | None = None
    refs: list[tuple[str, str]] = field(default_factory=list)  # (dst_node_id, edge_type)
    timestamp: float | None = None
    source: str | None = None
    props: dict = field(default_factory=dict)


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
    corpus: list[CorpusItem] = field(default_factory=list)  # the per-fault corpus delta:
                                             # this fault's diagnostic-action results, error
                                             # log, fault-injected tickets/docs/config changes.
    config_changes: dict[str, object] = field(default_factory=dict)  # config key id → new value
                                             # (a real post-release change; shifts config_diff)


# --- shared corpus builders (fault-conditioned facts, not difficulty knobs) ---
# These emit a diagnostic-history fact whose truth depends on the injected fault — a
# legitimate per-fault variation (C1): the same action yields a different *result* under a
# different ground-truth cause. A fault includes the builder when the fact holds for it.

def window_clean_tried() -> CorpusItem:
    """The window was cleaned with no improvement — true for any fault whose cause is NOT
    the window (cleaning a clean window does nothing). Omitted from window-contamination,
    where cleaning would have helped (so it was never logged as a no-op)."""
    return CorpusItem(
        id="act.window_clean", kind="diagnostic_action", node_type="diagnostic_action",
        name="Window cleaned",
        text="Window cleaned during inspection; no improvement in return intensity afterwards "
             "(reinforces: not contamination).",
        refs=[("sub.optics", "references")], timestamp=WINDOW_CLEAN_T,
        props={"result": "no_improvement"},
    )


def error_entry(eid: str, text: str, refs: list[str], timestamp: float = ONSET) -> CorpusItem:
    """A fault-specific error/warning-log line (artifact only, kind='error')."""
    return CorpusItem(id=eid, kind="error", text=text, timestamp=timestamp,
                      refs=[(r, "references") for r in refs])


def reboot_event() -> CorpusItem:
    """A scheduled reboot 2 days ago — the salient recent event a shortcut solver blames.
    Whether one happened in the window is a per-case fact: present as a non-causal trigger
    in most faults, omitted from the absent-cue case (#6), where there is no recent event."""
    return CorpusItem(
        id="log.reboot", kind="logbook_entry", node_type="logbook_entry",
        name="Scheduled system reboot",
        text="Scheduled system reboot performed (routine maintenance window).",
        timestamp=REBOOT_T, source="scheduled",
    )


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
        corpus=[
            error_entry("err.tec_load",
                        "TEC_LOAD_HIGH: intermittent, increasing in frequency over the window.",
                        ["sub.thermal", "part.tec"]),
            window_clean_tried(),  # window cleaned, no improvement → rules out optics
            reboot_event(),        # the salient-but-non-causal trigger (onset predates it)
        ],
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
        corpus=[window_clean_tried(), reboot_event()],  # optics ruled out; reboot non-causal
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
        corpus=[window_clean_tried(), reboot_event()],  # window ruled out; reboot is coincidence
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
        # no window_clean_tried(): cleaning a contaminated window WOULD improve return
        # intensity, so a "no improvement" log would contradict the cause. The honest history
        # is the window has not been cleaned (which is why it is still the active fault).
        corpus=[reboot_event()],                   # reboot present but non-causal
    )
    return telemetry, facts


def calibration_drift(seed_rng) -> tuple[list[TimeSeries], FaultFacts]:
    """Calibration-table drift (#4, B1/C3): a cal-table update (v12→v13) introduced a range
    bias. Range steps down at the update while every PHYSICAL channel stays nominal (no
    thermal, laser, or optics signature) — the tell that the fault lives in the calibration,
    not the hardware. **The anti-shortcut-balance case:** the salient recent change IS the
    cause, so a shortcut that blames the recent change is *right* here. The controller must
    still chain log→ticket→config→release notes to confirm v13 is the bad table (cite the
    evidence, not guess)."""
    t = sig.time_grid(WINDOW_START, WINDOW_END, STEP)
    rng = seed_rng
    rng_m = sig.step("effective_max_range_m", t, 120.0, 112.0, CHANGE_T, _NOISE["range"], rng,
                     spec={"min": 115.0, "max": 130.0, "units": "m"})  # steps at the cal update
    intensity = sig.flat("mean_return_intensity", t, _INTENS[0], _NOISE["intensity"], rng,
                         spec={"min": 0.90, "max": 1.10, "units": "norm"})  # returns are FINE
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
    telemetry += _regions(intensity, 1.0, 0.0, 1.0, rng)  # uniform, nominal
    facts = FaultFacts(
        root_cause="sub.calibration",
        causal_chain=["config.cal_table_version", "sub.calibration", "kpi.effective_range"],
        decoys=["part.tec", "part.laser_module"],  # a physical fault is plausible, ruled out
        conflicts=[], trigger=None,                # the recent change IS the cause — no trigger
        load_bearing_evidence=["config.cal_table_version", "ticket.cal_regression",
                               "doc.release_v13"],
        config_changes={"config.cal_table_version": "v13"},
        corpus=[
            CorpusItem("log.cal_update", "logbook_entry", node_type="logbook_entry",
                       name="Calibration table updated",
                       text="Calibration table updated v12 -> v13 (routine recalibration).",
                       timestamp=CHANGE_T, refs=[("config.cal_table_version", "references")]),
            CorpusItem("ticket.cal_regression", "ticket", node_type="ticket",
                       name="Range bias after cal v13",
                       text="Range readings biased low since the v13 cal-table rollout; suspected "
                            "calibration regression. Cites cal_table_version.",
                       refs=[("config.cal_table_version", "references"),
                             ("sub.calibration", "references")], timestamp=CHANGE_T + 0.5),
            CorpusItem("doc.release_v13", "doc", node_type="design_test_doc",
                       name="Cal-table v13 release notes",
                       text="Cal-table v13 release notes: a known range_bias regression vs v12 under "
                            "nominal optics; fix scheduled for v14. Shipped into this unit's window.",
                       refs=[("config.cal_table_version", "references")]),
        ],
    )
    return telemetry, facts


def detector_bias_drift(seed_rng) -> tuple[list[TimeSeries], FaultFacts]:
    """Detector bias drift (#6, C1/C2): the detector bias drifts, raising the dark-count and
    eroding SNR → range falls. **Absent-cue:** NO recent event, so a shortcut has nothing to
    blame; no thermal/laser/optics signature either. The discriminator is detector_health_check
    (dark-count up while detector temp stays flat → bias, not heat); the DARK_COUNT_HIGH error
    points at the detector, and the explaining note is navigation-gated — reachable by
    traversing from the receiver subsystem, not by searching the range-degradation terms."""
    t = sig.time_grid(WINDOW_START, WINDOW_END, STEP)
    rng = seed_rng
    dark = sig.ramp("dark_count_rate", t, 1.00, 1.60, ONSET, _NOISE["dark"], rng,
                    spec={"min": 0.5, "max": 1.5, "units": "norm"})       # rises past spec
    intensity = sig.ramp("mean_return_intensity", t, 1.00, 0.93, ONSET, _NOISE["intensity"], rng,
                         spec={"min": 0.90, "max": 1.10, "units": "norm"})  # modest SNR loss
    rng_m = sig.ramp("effective_max_range_m", t, 120.0, 113.0, ONSET, _NOISE["range"], rng,
                     spec={"min": 115.0, "max": 130.0, "units": "m"})
    diode = sig.flat("laser_diode_temp_C", t, _DIODE[0], _NOISE["diode"], rng,
                     spec={"min": 24.0, "max": 26.0, "units": "C"})         # nominal
    tec_current = sig.flat("tec_current_A", t, _TEC[0], _NOISE["tec"], rng,
                           spec={"min": 0.0, "max": TEC_LIMIT_A, "units": "A"})  # nominal
    power = sig.flat("laser_power_mW", t, _POWER[0], _NOISE["power"], rng,
                     spec={"min": 45.0, "max": 52.0, "units": "mW"})        # nominal
    detector_temp = sig.flat("detector_temp_C", t, 25.0, 0.08, rng,
                             spec={"min": 20.0, "max": 30.0, "units": "C"})  # live AND nominal
    ambient = sig.flat("ambient_temp_C", t, _AMBIENT, _NOISE["ambient"], rng,
                       spec={"min": 15.0, "max": 30.0, "units": "C"})
    telemetry = [rng_m, intensity, power, diode, tec_current, detector_temp, dark, ambient]
    telemetry += _regions(intensity, 1.0, 0.0, 1.0, rng)  # uniform (rules out window)
    facts = FaultFacts(
        root_cause="part.detector",
        causal_chain=["part.detector", "metric.dark_count", "metric.intensity",
                      "kpi.effective_range"],
        decoys=["part.tec", "part.laser_module", "part.window"],
        conflicts=[], trigger=None,                # absent-cue: no recent salient event at all
        load_bearing_evidence=["detector_health_check", "doc.detector_bias", "err.dark_count",
                               "metric.dark_count"],
        corpus=[
            window_clean_tried(),
            error_entry("err.dark_count",
                        "DARK_COUNT_HIGH: detector noise floor rising steadily over the window.",
                        ["sub.detector", "part.detector"]),
            CorpusItem("doc.detector_bias", "doc", node_type="domain_doc",
                       name="Detector bias-drift field note",
                       text="Field note: a slow detector bias drift raises the dark-count and noise "
                            "floor independent of detector temperature; confirm with a bias-voltage "
                            "sweep, then replace the detector. Filed under the receiver subsystem.",
                       refs=[("sub.detector", "documented_in"), ("part.detector", "references")]),
        ],
    )
    return telemetry, facts


def tec_degradation_variant(seed_rng) -> tuple[list[TimeSeries], FaultFacts]:
    """TEC degradation, near-symmetric variant (#7, D6): the same TEC fault as #1 but the cheap
    discriminators are AMBIGUOUS — the diode is only mildly above setpoint, the intensity↔diode
    correlation is borderline, and TEC current sits just *under* its limit. Neither
    temp_correlation_check nor tec_load_check fires cleanly, so resolving TEC vs the laser-aging
    decoy needs the expensive swap-test recommendation (cost 3): the tie-breaker-under-budget /
    VOI case. A reboot is present but non-causal (onset predates it)."""
    t = sig.time_grid(WINDOW_START, WINDOW_END, STEP)
    rng = seed_rng
    diode = sig.ramp("laser_diode_temp_C", t, _DIODE[0], 28.5, ONSET, _NOISE["diode"], rng,
                     spec={"min": 24.0, "max": 26.0, "units": "C"})   # clearly above setpoint
    intensity = sig.derived("mean_return_intensity", diode, _INTENS[0], _slope(_INTENS),
                            _DIODE[0], 0.034, rng,   # extra noise → |r| sub-threshold (not clean)
                            spec={"min": 0.90, "max": 1.10, "units": "norm"})
    tec_current = sig.derived("tec_current_A", diode, _TEC[0], (2.05 - _TEC[0]) / (28.5 - _DIODE[0]),
                              _DIODE[0], _NOISE["tec"], rng,
                              spec={"min": 0.0, "max": TEC_LIMIT_A, "units": "A"})  # ~82% (sub-threshold)
    power = sig.derived("laser_power_mW", diode, _POWER[0], _slope(_POWER), _DIODE[0],
                        _NOISE["power"], rng, spec={"min": 45.0, "max": 52.0, "units": "mW"})
    rng_m = sig.derived("effective_max_range_m", diode, _RANGE[0], _slope(_RANGE), _DIODE[0],
                        _NOISE["range"], rng, spec={"min": 115.0, "max": 130.0, "units": "m"})
    detector_temp = sig.flat("detector_temp_C", t, 25.0, 0.08, rng,
                             spec={"min": 20.0, "max": 30.0, "units": "C"})
    dark = sig.flat("dark_count_rate", t, _DARK[0], _NOISE["dark"], rng,
                    spec={"min": 0.5, "max": 1.5, "units": "norm"})
    ambient = sig.flat("ambient_temp_C", t, _AMBIENT, _NOISE["ambient"], rng,
                       spec={"min": 15.0, "max": 30.0, "units": "C"})
    telemetry = [rng_m, intensity, power, diode, tec_current, detector_temp, dark, ambient]
    telemetry += _regions(diode, _INTENS[0], _slope(_INTENS), _DIODE[0], rng)
    facts = FaultFacts(
        root_cause="part.tec",
        causal_chain=["part.tec", "metric.diode_temp", "metric.intensity", "kpi.effective_range"],
        decoys=["part.laser_module"],
        conflicts=["log.reboot"], trigger="log.reboot",
        load_bearing_evidence=["recommend_swap_test", "temp_correlation_check", "tec_load_check",
                               "onset_vs_event_check"],
        corpus=[window_clean_tried(), reboot_event()],
    )
    return telemetry, facts


def common_mode_power(seed_rng) -> tuple[list[TimeSeries], FaultFacts]:
    """Common-mode power fault (#8, A4/A5): a power-mode change overloaded the supply, so several
    nominally-independent channels degrade *together* — laser power down, dark-count up, TEC
    current up — looking like two or three separate faults. Redundant channels agreeing is the
    trap (A5); the tell is a COMMON ONSET across them (common_mode_check) tracing to one upstream
    power cause. **The second anti-shortcut-balance case:** the recent power-mode change IS the
    cause, so a shortcut blaming the recent config change is right here too."""
    t = sig.time_grid(WINDOW_START, WINDOW_END, STEP)
    rng = seed_rng
    power = sig.ramp("laser_power_mW", t, _POWER[0], 41.0, CHANGE_T, _NOISE["power"], rng,
                     spec={"min": 45.0, "max": 52.0, "units": "mW"})
    dark = sig.ramp("dark_count_rate", t, 1.00, 1.50, CHANGE_T, _NOISE["dark"], rng,
                    spec={"min": 0.5, "max": 1.5, "units": "norm"})
    tec_current = sig.ramp("tec_current_A", t, _TEC[0], 1.95, CHANGE_T, _NOISE["tec"], rng,
                           spec={"min": 0.0, "max": TEC_LIMIT_A, "units": "A"})  # ~78% (sub-threshold)
    diode = sig.flat("laser_diode_temp_C", t, _DIODE[0], _NOISE["diode"], rng,
                     spec={"min": 24.0, "max": 26.0, "units": "C"})    # flat → not a thermal primary
    intensity = sig.ramp("mean_return_intensity", t, 1.00, 0.88, CHANGE_T, _NOISE["intensity"], rng,
                         spec={"min": 0.90, "max": 1.10, "units": "norm"})
    rng_m = sig.ramp("effective_max_range_m", t, 120.0, 110.0, CHANGE_T, _NOISE["range"], rng,
                     spec={"min": 115.0, "max": 130.0, "units": "m"})
    detector_temp = sig.flat("detector_temp_C", t, 25.0, 0.08, rng,
                             spec={"min": 20.0, "max": 30.0, "units": "C"})
    ambient = sig.flat("ambient_temp_C", t, _AMBIENT, _NOISE["ambient"], rng,
                       spec={"min": 15.0, "max": 30.0, "units": "C"})
    telemetry = [rng_m, intensity, power, diode, tec_current, detector_temp, dark, ambient]
    telemetry += _regions(intensity, 1.0, 0.0, 1.0, rng)
    facts = FaultFacts(
        root_cause="sub.power",
        causal_chain=["sub.power", "sub.thermal", "metric.laser_power", "kpi.effective_range"],
        decoys=["part.laser_module", "part.detector"],  # the two surface faults it mimics
        conflicts=[], trigger=None,                      # the recent power-mode change IS the cause
        load_bearing_evidence=["common_mode_check", "config.scan_params", "log.power_mode"],
        config_changes={"config.scan_params": "high_power_v2"},
        corpus=[
            window_clean_tried(),
            CorpusItem("log.power_mode", "logbook_entry", node_type="logbook_entry",
                       name="Scan power-mode change",
                       text="Scan parameters switched to high_power_v2 (operator change).",
                       timestamp=CHANGE_T, refs=[("config.scan_params", "references")]),
            error_entry("err.supply",
                        "SUPPLY_RIPPLE: supply ripple elevated since the power-mode change.",
                        ["sub.power"], timestamp=CHANGE_T),
        ],
    )
    return telemetry, facts


# Registry: fault name → forward model.
FAULTS = {
    "tec_degradation": tec_degradation,
    "laser_aging": laser_aging,
    "window_contamination": window_contamination,
    "no_clean_cause": no_clean_cause,
    "calibration_drift": calibration_drift,
    "detector_bias_drift": detector_bias_drift,
    "tec_degradation_variant": tec_degradation_variant,
    "common_mode_power": common_mode_power,
}
