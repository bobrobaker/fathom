window.FATHOM_BUNDLES = {
  "case1": {
    "symptom": "Effective maximum range has degraded ~8% over the past week (about 110 m vs a 120 m baseline). Diagnose the root cause.",
    "trigger": "log.reboot",
    "root_cause": "part.tec",
    "final_status": "concluded",
    "steps": [
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination reducing transmitted / received optical power",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Detector sensitivity drift (dark-current rise or responsivity loss)",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser aging / output power decline",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC fault causing elevated operating temperature that degrades SNR",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift (range-gate offset or gain table error)",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [],
        "links": []
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination reducing transmitted / received optical power",
            "node_ref": "part.window",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Detector sensitivity drift (dark-current rise or responsivity loss)",
            "node_ref": "part.detector",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser aging / output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC fault causing elevated operating temperature that degrades SNR",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift (range-gate offset or gain table error)",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser output has dropped 12.2% (42.4 mW vs 48.2 mW baseline). Critically, diode temperature is 30.96 \u00b0C \u2014 well above the 26.0 \u00b0C setpoint maximum \u2014 indicating a TEC or thermal-management fault is suppressing laser power, not intrinsic laser aging. A 12.2% optical power reduction is sufficient to account for the observed ~8% range degradation (range scales sub-linearly with transmitted power), making additional optical-path or detector-side causes less necessary to invoke.",
            "source": "laser_power_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination reducing transmitted / received optical power",
            "node_ref": "part.window",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Detector sensitivity drift (dark-current rise or responsivity loss)",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Laser aging / output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC fault causing elevated operating temperature that degrades SNR",
            "node_ref": "part.tec",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "leading"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift (range-gate offset or gain table error)",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 1.0,
            "confidence": 0.731,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser output has dropped 12.2% (42.4 mW vs 48.2 mW baseline). Critically, diode temperature is 30.96 \u00b0C \u2014 well above the 26.0 \u00b0C setpoint maximum \u2014 indicating a TEC or thermal-management fault is suppressing laser power, not intrinsic laser aging. A 12.2% optical power reduction is sufficient to account for the observed ~8% range degradation (range scales sub-linearly with transmitted power), making additional optical-path or detector-side causes less necessary to invoke.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.tec_load_01",
            "summary": "TEC current is 2.27 A \u2014 91% of the 2.5 A hardware limit \u2014 yet the diode is held at 30.96 \u00b0C, which is 4.96 \u00b0C above the 26.0 \u00b0C setpoint maximum, and the controller flag losing_setpoint=true confirms active thermal runaway. The TEC is saturating its drive capacity and still cannot recover the setpoint, pointing to a failing TEC or an increased thermal load the TEC cannot reject, not intrinsic laser aging. This is consistent with ev.laser_power_01: suppressed laser output is a downstream consequence of the elevated junction temperature forced by TEC loss-of-control.",
            "source": "tec_load_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination reducing transmitted / received optical power",
            "node_ref": "part.window",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Detector sensitivity drift (dark-current rise or responsivity loss)",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Laser aging / output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC fault causing elevated operating temperature that degrades SNR",
            "node_ref": "part.tec",
            "log_odds": 1.5,
            "confidence": 0.818,
            "status": "leading"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift (range-gate offset or gain table error)",
            "node_ref": "sub.calibration",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser output has dropped 12.2% (42.4 mW vs 48.2 mW baseline). Critically, diode temperature is 30.96 \u00b0C \u2014 well above the 26.0 \u00b0C setpoint maximum \u2014 indicating a TEC or thermal-management fault is suppressing laser power, not intrinsic laser aging. A 12.2% optical power reduction is sufficient to account for the observed ~8% range degradation (range scales sub-linearly with transmitted power), making additional optical-path or detector-side causes less necessary to invoke.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.tec_load_01",
            "summary": "TEC current is 2.27 A \u2014 91% of the 2.5 A hardware limit \u2014 yet the diode is held at 30.96 \u00b0C, which is 4.96 \u00b0C above the 26.0 \u00b0C setpoint maximum, and the controller flag losing_setpoint=true confirms active thermal runaway. The TEC is saturating its drive capacity and still cannot recover the setpoint, pointing to a failing TEC or an increased thermal load the TEC cannot reject, not intrinsic laser aging. This is consistent with ev.laser_power_01: suppressed laser output is a downstream consequence of the elevated junction temperature forced by TEC loss-of-control.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_01",
            "summary": "common_mode_check returned common_mode=false with 3 degraded channels and an onset spread of 4.25 days. The staggered, non-simultaneous multi-channel onset pattern is incompatible with a single shared upstream event (power rail, scanner drive) that would degrade all channels in lockstep. It modestly disfavours h4 in the multi-channel reading (a single TEC unit fault should not produce staggered onset across 3 channels) though h4 remains dominant via direct thermal evidence. Independent per-channel staggered onsets are marginally more consistent with independent per-channel processes (h2, h3). The lack of common mode further corroborates ruling out h1 (a contaminated window would be common-mode) and h5 (a gain-table or range-gate error would be system-wide).",
            "source": "common_mode_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot",
          "metric.detector_temp"
        ],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination reducing transmitted / received optical power",
            "node_ref": "part.window",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Detector sensitivity drift (dark-current rise or responsivity loss)",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Laser aging / output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC fault causing elevated operating temperature that degrades SNR",
            "node_ref": "part.tec",
            "log_odds": 1.5,
            "confidence": 0.818,
            "status": "leading"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift (range-gate offset or gain table error)",
            "node_ref": "sub.calibration",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser output has dropped 12.2% (42.4 mW vs 48.2 mW baseline). Critically, diode temperature is 30.96 \u00b0C \u2014 well above the 26.0 \u00b0C setpoint maximum \u2014 indicating a TEC or thermal-management fault is suppressing laser power, not intrinsic laser aging. A 12.2% optical power reduction is sufficient to account for the observed ~8% range degradation (range scales sub-linearly with transmitted power), making additional optical-path or detector-side causes less necessary to invoke.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.tec_load_01",
            "summary": "TEC current is 2.27 A \u2014 91% of the 2.5 A hardware limit \u2014 yet the diode is held at 30.96 \u00b0C, which is 4.96 \u00b0C above the 26.0 \u00b0C setpoint maximum, and the controller flag losing_setpoint=true confirms active thermal runaway. The TEC is saturating its drive capacity and still cannot recover the setpoint, pointing to a failing TEC or an increased thermal load the TEC cannot reject, not intrinsic laser aging. This is consistent with ev.laser_power_01: suppressed laser output is a downstream consequence of the elevated junction temperature forced by TEC loss-of-control.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_01",
            "summary": "common_mode_check returned common_mode=false with 3 degraded channels and an onset spread of 4.25 days. The staggered, non-simultaneous multi-channel onset pattern is incompatible with a single shared upstream event (power rail, scanner drive) that would degrade all channels in lockstep. It modestly disfavours h4 in the multi-channel reading (a single TEC unit fault should not produce staggered onset across 3 channels) though h4 remains dominant via direct thermal evidence. Independent per-channel staggered onsets are marginally more consistent with independent per-channel processes (h2, h3). The lack of common mode further corroborates ruling out h1 (a contaminated window would be common-mode) and h5 (a gain-table or range-gate error would be system-wide).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.stuck_detector_temp_C",
            "summary": "detector_temp_C is stuck (\u2248zero variance) \u2192 unreliable channel",
            "source": "channel_sanity_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "concluded",
        "recommended_action": "Inspect and replace the TEC assembly: ev.tec_load_01 shows TEC current saturated at 2.27 A (91% of 2.5 A limit) with losing_setpoint=true and diode held at 30.96 \u00b0C \u2014 4.96 \u00b0C above the 26.0 \u00b0C max setpoint \u2014 indicating the TEC can no longer reject heat. This thermal runaway is the proximate cause of the 12.2% laser power drop confirmed in ev.laser_power_01, which is sufficient to account for the 8% range degradation; intrinsic laser aging (h3) is not independently implicated. The staggered 4.25-day onset across 3 channels (ev.common_mode_01) suggests per-channel TEC degradation rather than a single shared unit \u2014 audit each channel's TEC drive current and thermal interface independently rather than assuming a single common failure. Do not use detector_temp_C readings for thermal baselining: the channel is stuck with near-zero variance and is unreliable per ev.stuck_detector_temp_C. The system reboot (ev.trigger_demoted) postdates degradation onset and is non-causal.",
        "conflicts": [
          "log.reboot",
          "metric.detector_temp"
        ],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination reducing transmitted / received optical power",
            "node_ref": "part.window",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Detector sensitivity drift (dark-current rise or responsivity loss)",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Laser aging / output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC fault causing elevated operating temperature that degrades SNR",
            "node_ref": "part.tec",
            "log_odds": 1.5,
            "confidence": 0.818,
            "status": "leading"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift (range-gate offset or gain table error)",
            "node_ref": "sub.calibration",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser output has dropped 12.2% (42.4 mW vs 48.2 mW baseline). Critically, diode temperature is 30.96 \u00b0C \u2014 well above the 26.0 \u00b0C setpoint maximum \u2014 indicating a TEC or thermal-management fault is suppressing laser power, not intrinsic laser aging. A 12.2% optical power reduction is sufficient to account for the observed ~8% range degradation (range scales sub-linearly with transmitted power), making additional optical-path or detector-side causes less necessary to invoke.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.tec_load_01",
            "summary": "TEC current is 2.27 A \u2014 91% of the 2.5 A hardware limit \u2014 yet the diode is held at 30.96 \u00b0C, which is 4.96 \u00b0C above the 26.0 \u00b0C setpoint maximum, and the controller flag losing_setpoint=true confirms active thermal runaway. The TEC is saturating its drive capacity and still cannot recover the setpoint, pointing to a failing TEC or an increased thermal load the TEC cannot reject, not intrinsic laser aging. This is consistent with ev.laser_power_01: suppressed laser output is a downstream consequence of the elevated junction temperature forced by TEC loss-of-control.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_01",
            "summary": "common_mode_check returned common_mode=false with 3 degraded channels and an onset spread of 4.25 days. The staggered, non-simultaneous multi-channel onset pattern is incompatible with a single shared upstream event (power rail, scanner drive) that would degrade all channels in lockstep. It modestly disfavours h4 in the multi-channel reading (a single TEC unit fault should not produce staggered onset across 3 channels) though h4 remains dominant via direct thermal evidence. Independent per-channel staggered onsets are marginally more consistent with independent per-channel processes (h2, h3). The lack of common mode further corroborates ruling out h1 (a contaminated window would be common-mode) and h5 (a gain-table or range-gate error would be system-wide).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.stuck_detector_temp_C",
            "summary": "detector_temp_C is stuck (\u2248zero variance) \u2192 unreliable channel",
            "source": "channel_sanity_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      }
    ],
    "trace": [
      {
        "action": "seed",
        "args": {},
        "rationale": "seed the differential from the symptom",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h1",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "h1": 0.5,
          "h2": 0.5,
          "h3": 0.5,
          "h4": 0.5,
          "h5": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "laser_power_check"
        },
        "rationale": "No evidence has been collected yet and all six hypotheses are at equal log_odds. Laser output power is the single measurement that best partitions the hypothesis space at this stage. A degraded reading raises h3 (laser aging) and makes h4 (thermal/TEC fault driving laser output down) jointly plausible, while simultaneously arguing against h1, h2, and h5. A nominal reading does the opposite: it rules out h3, partially argues against hyp.upstream_power (TX power branch), and shifts probability mass toward h1 (window \u2014 attenuates both TX and RX), h2 (detector sensitivity loss \u2014 RX-side only), h4 (thermal degrading SNR via detector dark current rather than laser power), and h5 (calibration/gain drift \u2014 no optical loss at all). No prior evidence exists to cite; this check produces the first discriminating data point and avoids re-confirming anything already known.",
        "voi": 0.8,
        "evidence_id": "ev.laser_power_01",
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "h1": 0.269,
          "h2": 0.269,
          "h3": 0.119,
          "h4": 0.5,
          "h5": 0.269,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "tec_load_check"
        },
        "rationale": "ev.laser_power_01 establishes that diode temperature is 4.96 \u00b0C above its 26.0 \u00b0C setpoint maximum, implicating a thermal/TEC failure (h4) as the proximate cause of the 12.2% laser power drop. However, hyp.upstream_power (shared upstream supply issue) is equally scored at log_odds=0.00 and could explain the same temperature elevation via under-voltage to the TEC driver rather than a TEC fault per se. tec_load_check will reveal TEC drive current, duty cycle, and supply rail health: (a) an overloaded or degraded TEC running at or near 100% duty cycle with rising junction temp confirms h4 directly; (b) a TEC operating within normal load parameters but receiving a sagging supply voltage points to hyp.upstream_power; (c) a TEC that is simply off or faulted (zero drive) also confirms h4. This result moves h4 and hyp.upstream_power in opposite directions \u2014 the single most discriminating split available given current evidence \u2014 while h1, h2, and h5 remain less necessary to invoke until the thermal/power root cause is resolved.",
        "voi": 0.87,
        "evidence_id": "ev.tec_load_01",
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.881,
        "margin": 0.15,
        "confidences": {
          "h1": 0.119,
          "h2": 0.119,
          "h3": 0.047,
          "h4": 0.881,
          "h5": 0.119,
          "hyp.upstream_power": 0.731
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "common_mode_check"
        },
        "rationale": "Both h4 (isolated TEC/thermal fault) and hyp.upstream_power (shared upstream cause) remain active. ev.laser_power_01 and ev.tec_load_01 confirm thermal runaway on this channel but cannot distinguish whether the TEC is failing in isolation or whether a shared power/thermal supply anomaly is starving the TEC of drive headroom across multiple channels. A common_mode_check is the single most discriminating action: if degradation is present on other channels simultaneously, it strongly supports hyp.upstream_power (shared upstream cause) and reframes h4 as a downstream symptom rather than root cause; if the effect is strictly isolated to this channel, hyp.upstream_power falls and h4 (component-level TEC failure) is confirmed as the root cause requiring a swap/repair on this unit alone. Running laser_power_check or tec_load_check again would only re-confirm already well-evidenced findings without moving the two hypotheses apart.",
        "voi": 0.87,
        "evidence_id": "ev.common_mode_01",
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.818,
        "margin": 0.549,
        "confidences": {
          "h1": 0.076,
          "h2": 0.119,
          "h3": 0.047,
          "h4": 0.818,
          "h5": 0.076,
          "hyp.upstream_power": 0.269
        }
      },
      {
        "action": "conflict_sweep",
        "args": {},
        "rationale": "order onset vs the salient recent event; sanity-check channels",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [
          "log.reboot",
          "metric.detector_temp"
        ],
        "leader": "h4",
        "leader_conf": 0.818,
        "margin": 0.549,
        "confidences": {
          "h1": 0.076,
          "h2": 0.119,
          "h3": 0.047,
          "h4": 0.818,
          "h5": 0.076,
          "hyp.upstream_power": 0.269
        }
      },
      {
        "action": "synthesize",
        "args": {
          "answer_type": "cause",
          "root_cause": "part.tec"
        },
        "rationale": "conclude or abstain from the differential",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.818,
        "margin": 0.549,
        "confidences": {
          "h1": 0.076,
          "h2": 0.119,
          "h3": 0.047,
          "h4": 0.818,
          "h5": 0.076,
          "hyp.upstream_power": 0.269
        }
      }
    ],
    "case_id": "case1",
    "title": "TEC degradation",
    "caption": "worked example: cross-subsystem + decoy + lying channel + demoted trigger",
    "answer": {
      "answer_type": "cause",
      "root_cause": "part.tec",
      "cited_evidence": [
        "ev.tec_load_01",
        "ev.laser_power_01",
        "ev.common_mode_01",
        "ev.trigger_demoted",
        "ev.stuck_detector_temp_C"
      ],
      "conflicts": [
        "log.reboot",
        "metric.detector_temp"
      ]
    },
    "eval_row": {
      "accuracy": 1.0,
      "localization": 1.0,
      "trigger_discrimination": 1.0,
      "conflict_handling": 1.0,
      "evidence_f1": 0.4,
      "tokens": 83683
    },
    "graph": {
      "root": "kpi.effective_range",
      "nodes": [
        {
          "id": "kpi.effective_range",
          "type": "KPI",
          "name": "effective_max_range_m",
          "depth": 0
        },
        {
          "id": "metric.intensity",
          "type": "metric",
          "name": "mean_return_intensity",
          "depth": 1
        },
        {
          "id": "sub.calibration",
          "type": "subsystem",
          "name": "Signal proc / calibration",
          "depth": 1
        },
        {
          "id": "sub.laser",
          "type": "subsystem",
          "name": "Laser emitter",
          "depth": 2
        },
        {
          "id": "sub.optics",
          "type": "subsystem",
          "name": "Optics / window",
          "depth": 2
        },
        {
          "id": "sub.detector",
          "type": "subsystem",
          "name": "Receiver / detector",
          "depth": 2
        },
        {
          "id": "sub.thermal",
          "type": "subsystem",
          "name": "Thermal / TEC",
          "depth": 3
        },
        {
          "id": "sub.power",
          "type": "subsystem",
          "name": "Scanner / power",
          "depth": 4
        },
        {
          "id": "part.laser_module",
          "type": "part_type",
          "name": "Laser module",
          "depth": 3
        },
        {
          "id": "part.window",
          "type": "part_type",
          "name": "Window",
          "depth": 3
        },
        {
          "id": "part.detector",
          "type": "part_type",
          "name": "Detector",
          "depth": 3
        },
        {
          "id": "part.tec",
          "type": "part_type",
          "name": "TEC module",
          "depth": 4
        }
      ],
      "edges": [
        {
          "src": "metric.intensity",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.calibration",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.laser",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.optics",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.detector",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.laser",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.detector",
          "type": "affects"
        },
        {
          "src": "sub.power",
          "dst": "sub.thermal",
          "type": "affects"
        },
        {
          "src": "part.laser_module",
          "dst": "sub.laser",
          "type": "part_of"
        },
        {
          "src": "part.window",
          "dst": "sub.optics",
          "type": "part_of"
        },
        {
          "src": "part.detector",
          "dst": "sub.detector",
          "type": "part_of"
        },
        {
          "src": "part.tec",
          "dst": "sub.thermal",
          "type": "part_of"
        }
      ]
    },
    "explainer": {
      "purpose": "worked example: cross-subsystem + decoy + lying channel + demoted trigger",
      "answer_type": "cause",
      "mechanisms": [
        {
          "id": "D1",
          "desc": "A recent, attention-grabbing event looks like the cause but isn't \u2014 the fault started before it, so it has to be ruled out by timing."
        },
        {
          "id": "B5",
          "desc": "A sensor channel reports plausible-but-wrong values, so its readings can't be trusted on their own and must be cross-checked against an independent source."
        },
        {
          "id": "D5",
          "desc": "You can't tell the suspects apart by eye \u2014 it takes an actual computation (a rate, residual, or threshold) to discriminate them."
        },
        {
          "id": "A2",
          "desc": "One reading moves two suspects at once \u2014 it raises one hypothesis while lowering another, so a single check has to be read in both directions."
        }
      ],
      "decoys": [
        "part.laser_module"
      ],
      "trigger": "log.reboot"
    }
  },
  "case2": {
    "symptom": "Effective maximum range has degraded ~8% over the past week (about 110 m vs a 120 m baseline). Diagnose the root cause.",
    "trigger": "log.reboot",
    "root_cause": "part.laser_module",
    "final_status": "concluded",
    "steps": [
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing and return beam",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift shifting range-gate or detection threshold",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h4",
            "label": "TEC degradation causing elevated detector/laser operating temperature and reduced SNR",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h5",
            "label": "Detector responsivity drift (dark-current rise or gain shift) reducing sensitivity",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [],
        "links": []
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing and return beam",
            "node_ref": "part.window",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift shifting range-gate or detection threshold",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "leading"
          },
          {
            "id": "h4",
            "label": "TEC degradation causing elevated detector/laser operating temperature and reduced SNR",
            "node_ref": "part.tec",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h5",
            "label": "Detector responsivity drift (dark-current rise or gain shift) reducing sensitivity",
            "node_ref": "part.detector",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check.20260622",
            "summary": "Laser output power has declined 11.2% from baseline (47.9 mW \u2192 42.5 mW). Diode temperature is 25.3 \u00b0C against a 26.0 \u00b0C setpoint max (diode_nominal=true), confirming the TEC is maintaining thermal control. Power loss is therefore intrinsic to the emitter, not thermally induced. The magnitude of power loss is consistent with the observed ~8% range degradation.",
            "source": "laser_power_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h3",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing and return beam",
            "node_ref": "part.window",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift shifting range-gate or detection threshold",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "leading"
          },
          {
            "id": "h4",
            "label": "TEC degradation causing elevated detector/laser operating temperature and reduced SNR",
            "node_ref": "part.tec",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h5",
            "label": "Detector responsivity drift (dark-current rise or gain shift) reducing sensitivity",
            "node_ref": "part.detector",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check.20260622",
            "summary": "Laser output power has declined 11.2% from baseline (47.9 mW \u2192 42.5 mW). Diode temperature is 25.3 \u00b0C against a 26.0 \u00b0C setpoint max (diode_nominal=true), confirming the TEC is maintaining thermal control. Power loss is therefore intrinsic to the emitter, not thermally induced. The magnitude of power loss is consistent with the observed ~8% range degradation.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h3",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "concluded",
        "recommended_action": "Replace the laser diode emitter. ev.laser_power_check.20260622 confirms an 11.2% intrinsic output-power loss (47.9 mW \u2192 42.5 mW) that fully and parsimoniously accounts for the observed 8% range degradation; no other hypothesis is needed to explain the residual. TEC thermal control is nominal (25.3 \u00b0C vs 26.0 \u00b0C setpoint), eliminating a thermal cause and ruling out h4. Because the power deficit is measured at the emitter itself, calibration drift (h2), detector gain/dark-current shift (h5), and shared upstream supply issues (hyp.upstream_power) are displaced as explanations. Window fouling (h1) has not been directly measured and cannot be formally ruled out, but contributes nothing to the root-cause chain since the emitter loss alone matches the degradation. After emitter swap, verify restored output \u226547.9 mW and confirm range returns to 120 m baseline; opportunistically clean and inspect the protective window at that time. The reboot event (log.reboot) is confirmed non-causal\u2014degradation onset predates it (ev.trigger_demoted).",
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing and return beam",
            "node_ref": "part.window",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift shifting range-gate or detection threshold",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "leading"
          },
          {
            "id": "h4",
            "label": "TEC degradation causing elevated detector/laser operating temperature and reduced SNR",
            "node_ref": "part.tec",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h5",
            "label": "Detector responsivity drift (dark-current rise or gain shift) reducing sensitivity",
            "node_ref": "part.detector",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check.20260622",
            "summary": "Laser output power has declined 11.2% from baseline (47.9 mW \u2192 42.5 mW). Diode temperature is 25.3 \u00b0C against a 26.0 \u00b0C setpoint max (diode_nominal=true), confirming the TEC is maintaining thermal control. Power loss is therefore intrinsic to the emitter, not thermally induced. The magnitude of power loss is consistent with the observed ~8% range degradation.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h3",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check.20260622",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      }
    ],
    "trace": [
      {
        "action": "seed",
        "args": {},
        "rationale": "seed the differential from the symptom",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h1",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "h1": 0.5,
          "h2": 0.5,
          "h3": 0.5,
          "h4": 0.5,
          "h5": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "laser_power_check"
        },
        "rationale": "No evidence has been collected yet, so all hypotheses sit at equal prior. Laser output power is the single most leveraged physical parameter for range performance: a ~8% range reduction maps to a meaningful optical-power deficit in most SNR-limited configurations. Measuring laser power at source (before the window) cleanly separates the hypothesis space: (A) if power is nominal, h3 (laser aging) and the laser leg of hyp.upstream_power are effectively ruled out, and the investigation pivots to h1 (window fouling), h2 (calibration/threshold drift), h4 (TEC \u2192 temperature-driven SNR loss), and h5 (detector responsivity); (B) if power is measurably reduced, h3 and/or hyp.upstream_power become the leading causes and the other hypotheses drop in relative weight. No prior measurement has been cited (evidence list is empty), so this is not re-confirming anything \u2014 it is the first discriminating cut.",
        "voi": 0.78,
        "evidence_id": "ev.laser_power_check.20260622",
        "conflicts_added": [],
        "leader": "h3",
        "leader_conf": 0.881,
        "margin": 0.612,
        "confidences": {
          "h1": 0.269,
          "h2": 0.269,
          "h3": 0.881,
          "h4": 0.119,
          "h5": 0.269,
          "hyp.upstream_power": 0.269
        }
      },
      {
        "action": "conflict_sweep",
        "args": {},
        "rationale": "order onset vs the salient recent event; sanity-check channels",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [
          "log.reboot"
        ],
        "leader": "h3",
        "leader_conf": 0.881,
        "margin": 0.612,
        "confidences": {
          "h1": 0.269,
          "h2": 0.269,
          "h3": 0.881,
          "h4": 0.119,
          "h5": 0.269,
          "hyp.upstream_power": 0.269
        }
      },
      {
        "action": "synthesize",
        "args": {
          "answer_type": "cause",
          "root_cause": "part.laser_module"
        },
        "rationale": "conclude or abstain from the differential",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h3",
        "leader_conf": 0.881,
        "margin": 0.612,
        "confidences": {
          "h1": 0.269,
          "h2": 0.269,
          "h3": 0.881,
          "h4": 0.119,
          "h5": 0.269,
          "hyp.upstream_power": 0.269
        }
      }
    ],
    "case_id": "case2",
    "title": "Laser aging",
    "caption": "decoy as a true cause (no temp correlation) \u2014 symmetry vs case1",
    "answer": {
      "answer_type": "cause",
      "root_cause": "part.laser_module",
      "cited_evidence": [
        "ev.laser_power_check.20260622",
        "ev.trigger_demoted"
      ],
      "conflicts": [
        "log.reboot"
      ]
    },
    "eval_row": {
      "accuracy": 1.0,
      "localization": 1.0,
      "trigger_discrimination": 1.0,
      "conflict_handling": 1.0,
      "evidence_f1": 0.33,
      "tokens": 36527
    },
    "graph": {
      "root": "kpi.effective_range",
      "nodes": [
        {
          "id": "kpi.effective_range",
          "type": "KPI",
          "name": "effective_max_range_m",
          "depth": 0
        },
        {
          "id": "metric.intensity",
          "type": "metric",
          "name": "mean_return_intensity",
          "depth": 1
        },
        {
          "id": "sub.calibration",
          "type": "subsystem",
          "name": "Signal proc / calibration",
          "depth": 1
        },
        {
          "id": "sub.laser",
          "type": "subsystem",
          "name": "Laser emitter",
          "depth": 2
        },
        {
          "id": "sub.optics",
          "type": "subsystem",
          "name": "Optics / window",
          "depth": 2
        },
        {
          "id": "sub.detector",
          "type": "subsystem",
          "name": "Receiver / detector",
          "depth": 2
        },
        {
          "id": "sub.thermal",
          "type": "subsystem",
          "name": "Thermal / TEC",
          "depth": 3
        },
        {
          "id": "sub.power",
          "type": "subsystem",
          "name": "Scanner / power",
          "depth": 4
        },
        {
          "id": "part.laser_module",
          "type": "part_type",
          "name": "Laser module",
          "depth": 3
        },
        {
          "id": "part.window",
          "type": "part_type",
          "name": "Window",
          "depth": 3
        },
        {
          "id": "part.detector",
          "type": "part_type",
          "name": "Detector",
          "depth": 3
        },
        {
          "id": "part.tec",
          "type": "part_type",
          "name": "TEC module",
          "depth": 4
        }
      ],
      "edges": [
        {
          "src": "metric.intensity",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.calibration",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.laser",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.optics",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.detector",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.laser",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.detector",
          "type": "affects"
        },
        {
          "src": "sub.power",
          "dst": "sub.thermal",
          "type": "affects"
        },
        {
          "src": "part.laser_module",
          "dst": "sub.laser",
          "type": "part_of"
        },
        {
          "src": "part.window",
          "dst": "sub.optics",
          "type": "part_of"
        },
        {
          "src": "part.detector",
          "dst": "sub.detector",
          "type": "part_of"
        },
        {
          "src": "part.tec",
          "dst": "sub.thermal",
          "type": "part_of"
        }
      ]
    },
    "explainer": {
      "purpose": "decoy as a true cause (no temp correlation) \u2014 symmetry vs case1",
      "answer_type": "cause",
      "mechanisms": [
        {
          "id": "D5",
          "desc": "You can't tell the suspects apart by eye \u2014 it takes an actual computation (a rate, residual, or threshold) to discriminate them."
        },
        {
          "id": "A1",
          "desc": "A1"
        }
      ],
      "decoys": [
        "part.tec"
      ],
      "trigger": "log.reboot"
    }
  },
  "case3": {
    "symptom": "Effective maximum range has degraded ~8% over the past week (about 110 m vs a 120 m baseline). Diagnose the root cause.",
    "trigger": "log.reboot",
    "root_cause": "part.window",
    "final_status": "concluded",
    "steps": [
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination reducing transmitted/received optical power",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration or firmware drift shifting range-detection thresholds",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser aging causing gradual output power decline",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H4",
            "label": "TEC/thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [],
        "links": []
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination reducing transmitted/received optical power",
            "node_ref": "part.window",
            "log_odds": -0.3,
            "confidence": 0.426,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration or firmware drift shifting range-detection thresholds",
            "node_ref": "sub.calibration",
            "log_odds": -0.2,
            "confidence": 0.45,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser aging causing gradual output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC/thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": -0.2,
            "confidence": 0.45,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_1",
            "summary": "Laser output power 47.96 mW vs baseline 47.91 mW (+0.1%, ratio 1.001) \u2014 no meaningful decline. Diode temperature 25.15 \u00b0C vs setpoint max 26.0 \u00b0C \u2014 TEC regulation nominal. Both 'declined' and 'low_power' flags are false.",
            "source": "laser_power_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.3
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination reducing transmitted/received optical power",
            "node_ref": "part.window",
            "log_odds": -0.3,
            "confidence": 0.426,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration or firmware drift shifting range-detection thresholds",
            "node_ref": "sub.calibration",
            "log_odds": -0.7,
            "confidence": 0.332,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser aging causing gradual output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC/thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -2.4,
            "confidence": 0.083,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": -2.1,
            "confidence": 0.109,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_1",
            "summary": "Laser output power 47.96 mW vs baseline 47.91 mW (+0.1%, ratio 1.001) \u2014 no meaningful decline. Diode temperature 25.15 \u00b0C vs setpoint max 26.0 \u00b0C \u2014 TEC regulation nominal. Both 'declined' and 'low_power' flags are false.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check_1",
            "summary": "Detector dark-count rise +0.85%, temperature rise +0.0 \u00b0C (live channel, detector_temp_live=true), bias_drift=false, affirmative=false \u2014 no isolated detector degradation or responsivity-drift signature. Channel is responsive and variance is normal.",
            "source": "detector_health_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.3
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 1.9
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 0.4
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination reducing transmitted/received optical power",
            "node_ref": "part.window",
            "log_odds": 1.7,
            "confidence": 0.846,
            "status": "leading"
          },
          {
            "id": "H2",
            "label": "Calibration or firmware drift shifting range-detection thresholds",
            "node_ref": "sub.calibration",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing gradual output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -2.8,
            "confidence": 0.057,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC/thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": -2.9,
            "confidence": 0.052,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_1",
            "summary": "Laser output power 47.96 mW vs baseline 47.91 mW (+0.1%, ratio 1.001) \u2014 no meaningful decline. Diode temperature 25.15 \u00b0C vs setpoint max 26.0 \u00b0C \u2014 TEC regulation nominal. Both 'declined' and 'low_power' flags are false.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check_1",
            "summary": "Detector dark-count rise +0.85%, temperature rise +0.0 \u00b0C (live channel, detector_temp_live=true), bias_drift=false, affirmative=false \u2014 no isolated detector degradation or responsivity-drift signature. Channel is responsive and variance is normal.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.spatial_intensity_check_1",
            "summary": "Spatial intensity check across 4 regions shows high spread (0.484) with a localized affirmative result, indicating the intensity drop is confined to a sub-region of the field rather than uniform across the aperture. This pattern is characteristic of a physical obstruction or contamination on the optical window/optics, not a system-wide electronic or firmware effect.",
            "source": "spatial_intensity_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.3
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 1.9
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 0.4
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H1",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination reducing transmitted/received optical power",
            "node_ref": "part.window",
            "log_odds": 1.7,
            "confidence": 0.846,
            "status": "leading"
          },
          {
            "id": "H2",
            "label": "Calibration or firmware drift shifting range-detection thresholds",
            "node_ref": "sub.calibration",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing gradual output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -2.8,
            "confidence": 0.057,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC/thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": -2.9,
            "confidence": 0.052,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_1",
            "summary": "Laser output power 47.96 mW vs baseline 47.91 mW (+0.1%, ratio 1.001) \u2014 no meaningful decline. Diode temperature 25.15 \u00b0C vs setpoint max 26.0 \u00b0C \u2014 TEC regulation nominal. Both 'declined' and 'low_power' flags are false.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check_1",
            "summary": "Detector dark-count rise +0.85%, temperature rise +0.0 \u00b0C (live channel, detector_temp_live=true), bias_drift=false, affirmative=false \u2014 no isolated detector degradation or responsivity-drift signature. Channel is responsive and variance is normal.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.spatial_intensity_check_1",
            "summary": "Spatial intensity check across 4 regions shows high spread (0.484) with a localized affirmative result, indicating the intensity drop is confined to a sub-region of the field rather than uniform across the aperture. This pattern is characteristic of a physical obstruction or contamination on the optical window/optics, not a system-wide electronic or firmware effect.",
            "source": "spatial_intensity_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.3
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 1.9
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 0.4
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H1",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "concluded",
        "recommended_action": "Physically inspect and clean the optical window, focusing on the sub-region flagged by the localized intensity drop in ev.spatial_intensity_check_1. After cleaning, re-run the spatial intensity check to confirm spread returns below threshold and intensity uniformity is restored across all 4 regions. Do not implicate the recent reboot \u2014 ev.trigger_demoted confirms degradation onset predates it, making it coincident and non-causal.",
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination reducing transmitted/received optical power",
            "node_ref": "part.window",
            "log_odds": 1.7,
            "confidence": 0.846,
            "status": "leading"
          },
          {
            "id": "H2",
            "label": "Calibration or firmware drift shifting range-detection thresholds",
            "node_ref": "sub.calibration",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing gradual output power decline",
            "node_ref": "part.laser_module",
            "log_odds": -2.8,
            "confidence": 0.057,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC/thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": -2.9,
            "confidence": 0.052,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_1",
            "summary": "Laser output power 47.96 mW vs baseline 47.91 mW (+0.1%, ratio 1.001) \u2014 no meaningful decline. Diode temperature 25.15 \u00b0C vs setpoint max 26.0 \u00b0C \u2014 TEC regulation nominal. Both 'declined' and 'low_power' flags are false.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check_1",
            "summary": "Detector dark-count rise +0.85%, temperature rise +0.0 \u00b0C (live channel, detector_temp_live=true), bias_drift=false, affirmative=false \u2014 no isolated detector degradation or responsivity-drift signature. Channel is responsive and variance is normal.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.spatial_intensity_check_1",
            "summary": "Spatial intensity check across 4 regions shows high spread (0.484) with a localized affirmative result, indicating the intensity drop is confined to a sub-region of the field rather than uniform across the aperture. This pattern is characteristic of a physical obstruction or contamination on the optical window/optics, not a system-wide electronic or firmware effect.",
            "source": "spatial_intensity_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.3
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 1.9
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 0.4
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H1",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.spatial_intensity_check_1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      }
    ],
    "trace": [
      {
        "action": "seed",
        "args": {},
        "rationale": "seed the differential from the symptom",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "H1": 0.5,
          "H2": 0.5,
          "H3": 0.5,
          "H4": 0.5,
          "H5": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "laser_power_check"
        },
        "rationale": "No evidence has been collected yet and all hypotheses sit at equal log-odds. Measuring actual laser output power is the single most bifurcating first step: (a) if power is nominal it argues strongly AGAINST H3 (laser aging) and the laser-side of H4 (TEC failure degrading laser junction), and against hyp.upstream_power, collapsing the differential onto H1/H2/H5 (optical-path, threshold, or detector causes); (b) if power is measurably degraded it raises H3, H4, and hyp.upstream_power while arguing against H1, H2, and H5. A single measurement therefore simultaneously raises one cluster of hypotheses and lowers another \u2014 the definition of high discrimination. Window contamination (H1) would not reduce internally-measured laser power, calibration drift (H2) would not, and detector drift (H5) would not, so a nominal reading cleanly exonerates the source side and redirects effort to the optical-path and signal-processing side.",
        "voi": 0.82,
        "evidence_id": "ev.laser_power_check_1",
        "conflicts_added": [],
        "leader": "H2",
        "leader_conf": 0.45,
        "margin": 0.0,
        "confidences": {
          "H1": 0.426,
          "H2": 0.45,
          "H3": 0.119,
          "H4": 0.119,
          "H5": 0.45,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "detector_health_check"
        },
        "rationale": "ev.laser_power_check_1 already confirms the TX path is healthy (laser output +0.1% vs baseline, TEC nominal), ruling out H3 and H4. The three remaining open hypotheses split into two camps: H5 (detector responsivity drift \u2014 a hardware RX-path degradation) vs H1/H2 (optical-window contamination or calibration/threshold drift, neither of which would show up as detector responsivity loss). A detector_health_check directly probes the detector's responsivity and dark-current characteristics. A degraded result raises H5 strongly and argues against H1 and H2 (neither affects detector physics); a nominal result rules H5 out and redirects investigation to the window (H1) and config/firmware (H2). No other single check provides this clean binary split between the RX-hardware hypothesis and the two non-detector hypotheses simultaneously.",
        "voi": 0.82,
        "evidence_id": "ev.detector_health_check_1",
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.426,
        "margin": 0.094,
        "confidences": {
          "H1": 0.426,
          "H2": 0.332,
          "H3": 0.119,
          "H4": 0.083,
          "H5": 0.109,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "spatial_intensity_check"
        },
        "rationale": "H1 (window contamination) and H2 (calibration/firmware drift) are the only open hypotheses. Laser output (ev.laser_power_check_1), TEC regulation, and detector responsivity (ev.detector_health_check_1) are all nominal, ruling out H3\u2013H5 and upstream power. The single best discriminator between H1 and H2 is the spatial distribution of return intensity across the field of view. Window contamination (H1) produces spatially non-uniform attenuation \u2014 localised dirty patches, streaks, or a sector-dependent intensity gradient \u2014 whereas a calibration or firmware threshold shift (H2) would degrade range estimation uniformly across all azimuth/elevation angles with no spatial intensity signature. A non-uniform spatial pattern strongly raises H1 and lowers H2; a spatially flat but globally reduced return raises H2 and lowers H1. No existing evidence speaks to spatial distribution, so this check adds maximum new information.",
        "voi": 0.87,
        "evidence_id": "ev.spatial_intensity_check_1",
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.846,
        "margin": 0.77,
        "confidences": {
          "H1": 0.846,
          "H2": 0.076,
          "H3": 0.057,
          "H4": 0.047,
          "H5": 0.052,
          "hyp.upstream_power": 0.076
        }
      },
      {
        "action": "conflict_sweep",
        "args": {},
        "rationale": "order onset vs the salient recent event; sanity-check channels",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [
          "log.reboot"
        ],
        "leader": "H1",
        "leader_conf": 0.846,
        "margin": 0.77,
        "confidences": {
          "H1": 0.846,
          "H2": 0.076,
          "H3": 0.057,
          "H4": 0.047,
          "H5": 0.052,
          "hyp.upstream_power": 0.076
        }
      },
      {
        "action": "synthesize",
        "args": {
          "answer_type": "cause",
          "root_cause": "part.window"
        },
        "rationale": "conclude or abstain from the differential",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.846,
        "margin": 0.77,
        "confidences": {
          "H1": 0.846,
          "H2": 0.076,
          "H3": 0.057,
          "H4": 0.047,
          "H5": 0.052,
          "hyp.upstream_power": 0.076
        }
      }
    ],
    "case_id": "case3",
    "title": "Window contamination",
    "caption": "spatial-cluster signature; reasoning from absence",
    "answer": {
      "answer_type": "cause",
      "root_cause": "part.window",
      "cited_evidence": [
        "ev.spatial_intensity_check_1",
        "ev.laser_power_check_1",
        "ev.detector_health_check_1",
        "ev.trigger_demoted"
      ],
      "conflicts": [
        "log.reboot"
      ]
    },
    "eval_row": {
      "accuracy": 1.0,
      "localization": 1.0,
      "trigger_discrimination": 1.0,
      "conflict_handling": 1.0,
      "evidence_f1": 0.29,
      "tokens": 69316
    },
    "graph": {
      "root": "kpi.effective_range",
      "nodes": [
        {
          "id": "kpi.effective_range",
          "type": "KPI",
          "name": "effective_max_range_m",
          "depth": 0
        },
        {
          "id": "metric.intensity",
          "type": "metric",
          "name": "mean_return_intensity",
          "depth": 1
        },
        {
          "id": "sub.calibration",
          "type": "subsystem",
          "name": "Signal proc / calibration",
          "depth": 1
        },
        {
          "id": "sub.laser",
          "type": "subsystem",
          "name": "Laser emitter",
          "depth": 2
        },
        {
          "id": "sub.optics",
          "type": "subsystem",
          "name": "Optics / window",
          "depth": 2
        },
        {
          "id": "sub.detector",
          "type": "subsystem",
          "name": "Receiver / detector",
          "depth": 2
        },
        {
          "id": "sub.thermal",
          "type": "subsystem",
          "name": "Thermal / TEC",
          "depth": 3
        },
        {
          "id": "sub.power",
          "type": "subsystem",
          "name": "Scanner / power",
          "depth": 4
        },
        {
          "id": "part.laser_module",
          "type": "part_type",
          "name": "Laser module",
          "depth": 3
        },
        {
          "id": "part.window",
          "type": "part_type",
          "name": "Window",
          "depth": 3
        },
        {
          "id": "part.detector",
          "type": "part_type",
          "name": "Detector",
          "depth": 3
        },
        {
          "id": "part.tec",
          "type": "part_type",
          "name": "TEC module",
          "depth": 4
        }
      ],
      "edges": [
        {
          "src": "metric.intensity",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.calibration",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.laser",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.optics",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.detector",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.laser",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.detector",
          "type": "affects"
        },
        {
          "src": "sub.power",
          "dst": "sub.thermal",
          "type": "affects"
        },
        {
          "src": "part.laser_module",
          "dst": "sub.laser",
          "type": "part_of"
        },
        {
          "src": "part.window",
          "dst": "sub.optics",
          "type": "part_of"
        },
        {
          "src": "part.detector",
          "dst": "sub.detector",
          "type": "part_of"
        },
        {
          "src": "part.tec",
          "dst": "sub.thermal",
          "type": "part_of"
        }
      ]
    },
    "explainer": {
      "purpose": "spatial-cluster signature; reasoning from absence",
      "answer_type": "cause",
      "mechanisms": [
        {
          "id": "C-spatial",
          "desc": "C-spatial"
        },
        {
          "id": "A3",
          "desc": "A3"
        }
      ],
      "decoys": [
        "part.tec",
        "part.laser_module"
      ],
      "trigger": "log.reboot"
    }
  },
  "case4": {
    "symptom": "Effective maximum range has degraded ~8% over the past week (about 110 m vs a 120 m baseline). Diagnose the root cause.",
    "trigger": null,
    "root_cause": "sub.calibration",
    "final_status": "concluded",
    "steps": [
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing or return signal",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift reducing effective sensitivity / range gate",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser output power aging or degradation reducing peak emitted intensity",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h4",
            "label": "Detector responsivity drift (dark current rise, gain loss) reducing SNR",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h5",
            "label": "TEC module under-performing, elevating detector or laser junction temperature and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [],
        "links": []
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing or return signal",
            "node_ref": "part.window",
            "log_odds": -0.2,
            "confidence": 0.45,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift reducing effective sensitivity / range gate",
            "node_ref": "sub.calibration",
            "log_odds": -0.2,
            "confidence": 0.45,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser output power aging or degradation reducing peak emitted intensity",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Detector responsivity drift (dark current rise, gain loss) reducing SNR",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h5",
            "label": "TEC module under-performing, elevating detector or laser junction temperature and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check.1",
            "summary": "Laser output power 48.0 mW vs baseline 47.9 mW (+0.1%); diode temperature 25.1 \u00b0C against a 26.0 \u00b0C setpoint ceiling. Both metrics fully nominal; no sustained power loss detected.",
            "source": "laser_power_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 0.2
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing or return signal",
            "node_ref": "part.window",
            "log_odds": -0.2,
            "confidence": 0.45,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift reducing effective sensitivity / range gate",
            "node_ref": "sub.calibration",
            "log_odds": -0.2,
            "confidence": 0.45,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Laser output power aging or degradation reducing peak emitted intensity",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Detector responsivity drift (dark current rise, gain loss) reducing SNR",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h5",
            "label": "TEC module under-performing, elevating detector or laser junction temperature and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -2.8,
            "confidence": 0.057,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check.1",
            "summary": "Laser output power 48.0 mW vs baseline 47.9 mW (+0.1%); diode temperature 25.1 \u00b0C against a 26.0 \u00b0C setpoint ceiling. Both metrics fully nominal; no sustained power loss detected.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check.1",
            "summary": "Detector health check fully nominal: dark-count rise \u22480% (\u22120.003, indistinguishable from zero), detector temperature rise \u22480 \u00b0C (\u22120.007 \u00b0C), bias drift absent, and temperature channel confirmed live (detector_temp_live=true). No detector degradation or bias signature of any kind detected.",
            "source": "detector_health_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_check.1",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.8
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing or return signal",
            "node_ref": "part.window",
            "log_odds": -1.2,
            "confidence": 0.231,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift reducing effective sensitivity / range gate",
            "node_ref": "sub.calibration",
            "log_odds": 1.8,
            "confidence": 0.858,
            "status": "leading"
          },
          {
            "id": "h3",
            "label": "Laser output power aging or degradation reducing peak emitted intensity",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Detector responsivity drift (dark current rise, gain loss) reducing SNR",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h5",
            "label": "TEC module under-performing, elevating detector or laser junction temperature and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -2.8,
            "confidence": 0.057,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check.1",
            "summary": "Laser output power 48.0 mW vs baseline 47.9 mW (+0.1%); diode temperature 25.1 \u00b0C against a 26.0 \u00b0C setpoint ceiling. Both metrics fully nominal; no sustained power loss detected.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check.1",
            "summary": "Detector health check fully nominal: dark-count rise \u22480% (\u22120.003, indistinguishable from zero), detector temperature rise \u22480 \u00b0C (\u22120.007 \u00b0C), bias drift absent, and temperature channel confirmed live (detector_temp_live=true). No detector degradation or bias signature of any kind detected.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.config_diff.1",
            "summary": "cal_table_version changed from v12 to v13; this is the only configuration change detected. A calibration-table update directly governs range-gate boundaries and sensitivity mapping, and the change falls within the one-week degradation window \u2014 making it a plausible primary cause of the ~8% effective-range reduction without requiring any hardware fault.",
            "source": "config_diff"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_check.1",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.config_diff.1",
            "hypothesis_id": "h2",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.config_diff.1",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing or return signal",
            "node_ref": "part.window",
            "log_odds": -1.2,
            "confidence": 0.231,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift reducing effective sensitivity / range gate",
            "node_ref": "sub.calibration",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          },
          {
            "id": "h3",
            "label": "Laser output power aging or degradation reducing peak emitted intensity",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Detector responsivity drift (dark current rise, gain loss) reducing SNR",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h5",
            "label": "TEC module under-performing, elevating detector or laser junction temperature and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -2.8,
            "confidence": 0.057,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check.1",
            "summary": "Laser output power 48.0 mW vs baseline 47.9 mW (+0.1%); diode temperature 25.1 \u00b0C against a 26.0 \u00b0C setpoint ceiling. Both metrics fully nominal; no sustained power loss detected.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check.1",
            "summary": "Detector health check fully nominal: dark-count rise \u22480% (\u22120.003, indistinguishable from zero), detector temperature rise \u22480 \u00b0C (\u22120.007 \u00b0C), bias drift absent, and temperature channel confirmed live (detector_temp_live=true). No detector degradation or bias signature of any kind detected.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.config_diff.1",
            "summary": "cal_table_version changed from v12 to v13; this is the only configuration change detected. A calibration-table update directly governs range-gate boundaries and sensitivity mapping, and the change falls within the one-week degradation window \u2014 making it a plausible primary cause of the ~8% effective-range reduction without requiring any hardware fault.",
            "source": "config_diff"
          },
          {
            "id": "ev.change_cause_log.cal_update",
            "summary": "log.cal_update: a recent config change to sub.calibration aligns with the degradation onset \u2192 the change is the cause",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_check.1",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.config_diff.1",
            "hypothesis_id": "h2",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.config_diff.1",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.change_cause_log.cal_update",
            "hypothesis_id": "h2",
            "polarity": "+",
            "weight": 1.5
          }
        ]
      },
      {
        "status": "concluded",
        "recommended_action": "Roll back cal_table_version from v13 to v12 and verify effective range returns to ~120 m baseline. If confirmed, audit the v13 cal table diff for mis-configured range-gate boundaries or sensitivity-mapping offsets before any re-deployment. Hardware checks (laser, detector, TEC, window) are all nominal and require no further action.",
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination / fouling attenuating outgoing or return signal",
            "node_ref": "part.window",
            "log_odds": -1.2,
            "confidence": 0.231,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Calibration or firmware drift reducing effective sensitivity / range gate",
            "node_ref": "sub.calibration",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          },
          {
            "id": "h3",
            "label": "Laser output power aging or degradation reducing peak emitted intensity",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Detector responsivity drift (dark current rise, gain loss) reducing SNR",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h5",
            "label": "TEC module under-performing, elevating detector or laser junction temperature and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -2.8,
            "confidence": 0.057,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check.1",
            "summary": "Laser output power 48.0 mW vs baseline 47.9 mW (+0.1%); diode temperature 25.1 \u00b0C against a 26.0 \u00b0C setpoint ceiling. Both metrics fully nominal; no sustained power loss detected.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check.1",
            "summary": "Detector health check fully nominal: dark-count rise \u22480% (\u22120.003, indistinguishable from zero), detector temperature rise \u22480 \u00b0C (\u22120.007 \u00b0C), bias drift absent, and temperature channel confirmed live (detector_temp_live=true). No detector degradation or bias signature of any kind detected.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.config_diff.1",
            "summary": "cal_table_version changed from v12 to v13; this is the only configuration change detected. A calibration-table update directly governs range-gate boundaries and sensitivity mapping, and the change falls within the one-week degradation window \u2014 making it a plausible primary cause of the ~8% effective-range reduction without requiring any hardware fault.",
            "source": "config_diff"
          },
          {
            "id": "ev.change_cause_log.cal_update",
            "summary": "log.cal_update: a recent config change to sub.calibration aligns with the degradation onset \u2192 the change is the cause",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.laser_power_check.1",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_check.1",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check.1",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.8
          },
          {
            "evidence_id": "ev.config_diff.1",
            "hypothesis_id": "h2",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.config_diff.1",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.change_cause_log.cal_update",
            "hypothesis_id": "h2",
            "polarity": "+",
            "weight": 1.5
          }
        ]
      }
    ],
    "trace": [
      {
        "action": "seed",
        "args": {},
        "rationale": "seed the differential from the symptom",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h1",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "h1": 0.5,
          "h2": 0.5,
          "h3": 0.5,
          "h4": 0.5,
          "h5": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "laser_power_check"
        },
        "rationale": "No evidence has been collected yet; all hypotheses sit at equal log-odds. Laser output power is the single most branching measurement in the signal chain: (a) if emitted power is at or near baseline, h3 (laser aging) and hyp.upstream_power are strongly disfavoured, collapsing the differential onto h1/h2/h4/h5; (b) if emitted power is depressed by ~15-30% (the range consistent with an 8% range loss under inverse-square / fourth-root scaling), h3 becomes the leading cause and hyp.upstream_power rises in parallel, directing hardware attention to the emitter rather than optics, detector, or calibration. This single measurement therefore raises one cluster of hypotheses while lowering the other \u2014 maximum discrimination with one action. TEC, detector, and window checks remain queued but are only meaningful once we know whether the loss is on the transmit or receive/optics side.",
        "voi": 0.8,
        "evidence_id": "ev.laser_power_check.1",
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.5,
        "margin": 0.05,
        "confidences": {
          "h1": 0.45,
          "h2": 0.45,
          "h3": 0.119,
          "h4": 0.5,
          "h5": 0.119,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "detector_health_check"
        },
        "rationale": "h4 (detector responsivity drift) currently holds the highest log_odds (0.00) among open hypotheses, yet no detector evidence has been collected. The laser is confirmed nominal (ev.laser_power_check.1), ruling out h3 and supporting that the ~8% range loss originates post-emission. detector_health_check will measure dark current, gain, and SNR margin directly: if any metric is degraded it confirms h4 and largely exonerates h1/h2; if all metrics are nominal it substantially lowers h4, making h1 (window fouling) and h2 (calibration/firmware drift) the co-leaders and directing the next action toward spatial_intensity_check or config_diff respectively. This is the highest-leverage single action because it tests the current front-runner while its negative result would cleanly redirect the differential.",
        "voi": 0.85,
        "evidence_id": "ev.detector_health_check.1",
        "conflicts_added": [],
        "leader": "h1",
        "leader_conf": 0.45,
        "margin": 0.0,
        "confidences": {
          "h1": 0.45,
          "h2": 0.45,
          "h3": 0.119,
          "h4": 0.119,
          "h5": 0.057,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "config_diff"
        },
        "rationale": "Only h1 (window contamination) and h2 (calibration/firmware drift) remain open, both at equal log-odds (-0.20). The laser power (ev.laser_power_check.1) and detector health (ev.detector_health_check.1) are fully nominal, ruling out signal-generation and signal-detection paths. The remaining fork is: (A) the optical path is attenuated externally (h1 \u2014 physical window fouling), or (B) a software/configuration parameter (range-gate threshold, sensitivity coefficient, firmware version) has drifted (h2). config_diff directly probes h2: a detected parameter change aligns with h2 and argues against h1 (no physical cause needed); a clean diff eliminates h2 and makes h1 the remaining candidate to pursue via spatial_intensity_check or physical inspection. No other available check separates these two hypotheses as cleanly in a single step.",
        "voi": 0.82,
        "evidence_id": "ev.config_diff.1",
        "conflicts_added": [],
        "leader": "h2",
        "leader_conf": 0.858,
        "margin": 0.627,
        "confidences": {
          "h1": 0.231,
          "h2": 0.858,
          "h3": 0.119,
          "h4": 0.119,
          "h5": 0.057,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "conflict_sweep",
        "args": {},
        "rationale": "order onset vs the salient recent event; sanity-check channels",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h2",
        "leader_conf": 0.953,
        "margin": 0.721,
        "confidences": {
          "h1": 0.231,
          "h2": 0.953,
          "h3": 0.119,
          "h4": 0.119,
          "h5": 0.057,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "synthesize",
        "args": {
          "answer_type": "cause",
          "root_cause": "sub.calibration"
        },
        "rationale": "conclude or abstain from the differential",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h2",
        "leader_conf": 0.953,
        "margin": 0.721,
        "confidences": {
          "h1": 0.231,
          "h2": 0.953,
          "h3": 0.119,
          "h4": 0.119,
          "h5": 0.057,
          "hyp.upstream_power": 0.182
        }
      }
    ],
    "case_id": "case4",
    "title": "Calibration drift",
    "caption": "post-release config; recent change IS the cause (anti-shortcut balance)",
    "answer": {
      "answer_type": "cause",
      "root_cause": "sub.calibration",
      "cited_evidence": [
        "ev.config_diff.1",
        "ev.change_cause_log.cal_update",
        "ev.laser_power_check.1",
        "ev.detector_health_check.1"
      ],
      "conflicts": []
    },
    "eval_row": {
      "accuracy": 1.0,
      "localization": 1.0,
      "trigger_discrimination": 1.0,
      "conflict_handling": 1.0,
      "evidence_f1": 0.0,
      "tokens": 63228
    },
    "graph": {
      "root": "kpi.effective_range",
      "nodes": [
        {
          "id": "kpi.effective_range",
          "type": "KPI",
          "name": "effective_max_range_m",
          "depth": 0
        },
        {
          "id": "metric.intensity",
          "type": "metric",
          "name": "mean_return_intensity",
          "depth": 1
        },
        {
          "id": "sub.calibration",
          "type": "subsystem",
          "name": "Signal proc / calibration",
          "depth": 1
        },
        {
          "id": "sub.laser",
          "type": "subsystem",
          "name": "Laser emitter",
          "depth": 2
        },
        {
          "id": "sub.optics",
          "type": "subsystem",
          "name": "Optics / window",
          "depth": 2
        },
        {
          "id": "sub.detector",
          "type": "subsystem",
          "name": "Receiver / detector",
          "depth": 2
        },
        {
          "id": "sub.thermal",
          "type": "subsystem",
          "name": "Thermal / TEC",
          "depth": 3
        },
        {
          "id": "sub.power",
          "type": "subsystem",
          "name": "Scanner / power",
          "depth": 4
        },
        {
          "id": "part.laser_module",
          "type": "part_type",
          "name": "Laser module",
          "depth": 3
        },
        {
          "id": "part.window",
          "type": "part_type",
          "name": "Window",
          "depth": 3
        },
        {
          "id": "part.detector",
          "type": "part_type",
          "name": "Detector",
          "depth": 3
        },
        {
          "id": "part.tec",
          "type": "part_type",
          "name": "TEC module",
          "depth": 4
        }
      ],
      "edges": [
        {
          "src": "metric.intensity",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.calibration",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.laser",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.optics",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.detector",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.laser",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.detector",
          "type": "affects"
        },
        {
          "src": "sub.power",
          "dst": "sub.thermal",
          "type": "affects"
        },
        {
          "src": "part.laser_module",
          "dst": "sub.laser",
          "type": "part_of"
        },
        {
          "src": "part.window",
          "dst": "sub.optics",
          "type": "part_of"
        },
        {
          "src": "part.detector",
          "dst": "sub.detector",
          "type": "part_of"
        },
        {
          "src": "part.tec",
          "dst": "sub.thermal",
          "type": "part_of"
        }
      ]
    },
    "explainer": {
      "purpose": "post-release config; recent change IS the cause (anti-shortcut balance)",
      "answer_type": "cause",
      "mechanisms": [
        {
          "id": "B1",
          "desc": "B1"
        },
        {
          "id": "C3",
          "desc": "C3"
        }
      ],
      "decoys": [
        "part.tec",
        "part.laser_module"
      ],
      "trigger": null
    }
  },
  "case5": {
    "symptom": "An intermittent range fluctuation was reported around the last maintenance. Determine the root cause, or whether there is a single clean cause at all.",
    "trigger": "log.reboot",
    "root_cause": null,
    "final_status": "abstained",
    "steps": [
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [],
        "links": []
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.laser_power_check",
            "summary": "Laser output 48.15 mW vs baseline 48.07 mW (+0.2%), ratio 1.0017 \u2014 no sustained decline. Diode temperature 25.28 \u00b0C nominal vs setpoint_max 26.0 \u00b0C, diode_nominal=true, low_power=false. A point-in-time snapshot; cannot exclude brief intermittent drops, but the trend shows no degradation from baseline.",
            "source": "laser_power_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.laser_power_check",
            "summary": "Laser output 48.15 mW vs baseline 48.07 mW (+0.2%), ratio 1.0017 \u2014 no sustained decline. Diode temperature 25.28 \u00b0C nominal vs setpoint_max 26.0 \u00b0C, diode_nominal=true, low_power=false. A point-in-time snapshot; cannot exclude brief intermittent drops, but the trend shows no degradation from baseline.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check",
            "summary": "Dark-count rise \u22480.003 (effectively 0%), detector temp rise \u22480.008 \u00b0C, bias_drift=false, detector_temp_live=true. No detector bias, responsivity, or thermal signature detected. Detector operating point is electrically and thermally stable at time of check; channel confirmed live (not stuck).",
            "source": "detector_health_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.laser_power_check",
            "summary": "Laser output 48.15 mW vs baseline 48.07 mW (+0.2%), ratio 1.0017 \u2014 no sustained decline. Diode temperature 25.28 \u00b0C nominal vs setpoint_max 26.0 \u00b0C, diode_nominal=true, low_power=false. A point-in-time snapshot; cannot exclude brief intermittent drops, but the trend shows no degradation from baseline.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check",
            "summary": "Dark-count rise \u22480.003 (effectively 0%), detector temp rise \u22480.008 \u00b0C, bias_drift=false, detector_temp_live=true. No detector bias, responsivity, or thermal signature detected. Detector operating point is electrically and thermally stable at time of check; channel confirmed live (not stuck).",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_check",
            "summary": "TEC current 1.19 A is 47% of the 2.5 A limit; diode temp 25.28 \u00b0C is well below setpoint_max 26.0 \u00b0C; losing_setpoint=false. The TEC has substantial headroom, is tracking its setpoint without strain, and shows no sign of thermal saturation, instability, or runaway. The laser diode thermal operating point is actively and stably controlled at time of check.",
            "source": "tec_load_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -1.7,
            "confidence": 0.154,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": -2.7,
            "confidence": 0.063,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.laser_power_check",
            "summary": "Laser output 48.15 mW vs baseline 48.07 mW (+0.2%), ratio 1.0017 \u2014 no sustained decline. Diode temperature 25.28 \u00b0C nominal vs setpoint_max 26.0 \u00b0C, diode_nominal=true, low_power=false. A point-in-time snapshot; cannot exclude brief intermittent drops, but the trend shows no degradation from baseline.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check",
            "summary": "Dark-count rise \u22480.003 (effectively 0%), detector temp rise \u22480.008 \u00b0C, bias_drift=false, detector_temp_live=true. No detector bias, responsivity, or thermal signature detected. Detector operating point is electrically and thermally stable at time of check; channel confirmed live (not stuck).",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_check",
            "summary": "TEC current 1.19 A is 47% of the 2.5 A limit; diode temp 25.28 \u00b0C is well below setpoint_max 26.0 \u00b0C; losing_setpoint=false. The TEC has substantial headroom, is tracking its setpoint without strain, and shows no sign of thermal saturation, instability, or runaway. The laser diode thermal operating point is actively and stably controlled at time of check.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_check",
            "summary": "Common-mode check found 0 degraded channels with onset spread 0.00 d \u2014 no shared degradation signature across channels. A shared upstream cause (power rail, firmware push, shared thermal infrastructure) would be expected to produce concurrent multi-channel onset; the complete absence of any such pattern argues strongly against hyp.upstream_power. It also mildly argues against H2 (firmware/calibration drift, which typically propagates system-wide) and H4 (a shared-path thermal instability scenario). Single-unit per-channel hypotheses (H1, H3, H5) are not meaningfully constrained by this result.",
            "source": "common_mode_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": -2.7,
            "confidence": 0.063,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.laser_power_check",
            "summary": "Laser output 48.15 mW vs baseline 48.07 mW (+0.2%), ratio 1.0017 \u2014 no sustained decline. Diode temperature 25.28 \u00b0C nominal vs setpoint_max 26.0 \u00b0C, diode_nominal=true, low_power=false. A point-in-time snapshot; cannot exclude brief intermittent drops, but the trend shows no degradation from baseline.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check",
            "summary": "Dark-count rise \u22480.003 (effectively 0%), detector temp rise \u22480.008 \u00b0C, bias_drift=false, detector_temp_live=true. No detector bias, responsivity, or thermal signature detected. Detector operating point is electrically and thermally stable at time of check; channel confirmed live (not stuck).",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_check",
            "summary": "TEC current 1.19 A is 47% of the 2.5 A limit; diode temp 25.28 \u00b0C is well below setpoint_max 26.0 \u00b0C; losing_setpoint=false. The TEC has substantial headroom, is tracking its setpoint without strain, and shows no sign of thermal saturation, instability, or runaway. The laser diode thermal operating point is actively and stably controlled at time of check.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_check",
            "summary": "Common-mode check found 0 degraded channels with onset spread 0.00 d \u2014 no shared degradation signature across channels. A shared upstream cause (power rail, firmware push, shared thermal infrastructure) would be expected to produce concurrent multi-channel onset; the complete absence of any such pattern argues strongly against hyp.upstream_power. It also mildly argues against H2 (firmware/calibration drift, which typically propagates system-wide) and H4 (a shared-path thermal instability scenario). Single-unit per-channel hypotheses (H1, H3, H5) are not meaningfully constrained by this result.",
            "source": "common_mode_check"
          },
          {
            "id": "ev.spatial_intensity_check",
            "summary": "Intensity drop is spatially uniform across all 4 sampled regions (spread=0.072, localized=false, affirmative=false). A contaminated window would produce a spatially non-uniform, regionally concentrated attenuation signature; the near-zero spread directly rules that out. Uniformity is instead consistent with any global beam-path or power mechanism \u2014 laser aging, thermal modulation, detector responsivity drift, or upstream power \u2014 all of which would affect all scan regions indiscriminately.",
            "source": "spatial_intensity_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.spatial_intensity_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 2.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.laser_power_check",
            "summary": "Laser output 48.15 mW vs baseline 48.07 mW (+0.2%), ratio 1.0017 \u2014 no sustained decline. Diode temperature 25.28 \u00b0C nominal vs setpoint_max 26.0 \u00b0C, diode_nominal=true, low_power=false. A point-in-time snapshot; cannot exclude brief intermittent drops, but the trend shows no degradation from baseline.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check",
            "summary": "Dark-count rise \u22480.003 (effectively 0%), detector temp rise \u22480.008 \u00b0C, bias_drift=false, detector_temp_live=true. No detector bias, responsivity, or thermal signature detected. Detector operating point is electrically and thermally stable at time of check; channel confirmed live (not stuck).",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_check",
            "summary": "TEC current 1.19 A is 47% of the 2.5 A limit; diode temp 25.28 \u00b0C is well below setpoint_max 26.0 \u00b0C; losing_setpoint=false. The TEC has substantial headroom, is tracking its setpoint without strain, and shows no sign of thermal saturation, instability, or runaway. The laser diode thermal operating point is actively and stably controlled at time of check.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_check",
            "summary": "Common-mode check found 0 degraded channels with onset spread 0.00 d \u2014 no shared degradation signature across channels. A shared upstream cause (power rail, firmware push, shared thermal infrastructure) would be expected to produce concurrent multi-channel onset; the complete absence of any such pattern argues strongly against hyp.upstream_power. It also mildly argues against H2 (firmware/calibration drift, which typically propagates system-wide) and H4 (a shared-path thermal instability scenario). Single-unit per-channel hypotheses (H1, H3, H5) are not meaningfully constrained by this result.",
            "source": "common_mode_check"
          },
          {
            "id": "ev.spatial_intensity_check",
            "summary": "Intensity drop is spatially uniform across all 4 sampled regions (spread=0.072, localized=false, affirmative=false). A contaminated window would produce a spatially non-uniform, regionally concentrated attenuation signature; the near-zero spread directly rules that out. Uniformity is instead consistent with any global beam-path or power mechanism \u2014 laser aging, thermal modulation, detector responsivity drift, or upstream power \u2014 all of which would affect all scan regions indiscriminately.",
            "source": "spatial_intensity_check"
          },
          {
            "id": "ev.temp_correlation_check",
            "summary": "mean_return_intensity vs laser_diode_temp_C yields r=-0.24 (correlated=false, affirmative=false). The correlation is below significance and the direction is weakly negative. If TEC/thermal instability were modulating the laser or detector operating point (H4), a materially stronger intensity-temperature relationship would be expected; the near-zero correlation directly undercuts that mechanism. It also mildly argues against any thermally-driven pathway in H3 (laser aging manifesting via thermal runaway) and H5 (detector responsivity drifting with diode temperature). H1, H2, and hyp.upstream_power are not substantially constrained by a thermal correlation test, but the absence of any thermal footprint provides marginal additional argument against each.",
            "source": "temp_correlation_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.spatial_intensity_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.2
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.laser_power_check",
            "summary": "Laser output 48.15 mW vs baseline 48.07 mW (+0.2%), ratio 1.0017 \u2014 no sustained decline. Diode temperature 25.28 \u00b0C nominal vs setpoint_max 26.0 \u00b0C, diode_nominal=true, low_power=false. A point-in-time snapshot; cannot exclude brief intermittent drops, but the trend shows no degradation from baseline.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check",
            "summary": "Dark-count rise \u22480.003 (effectively 0%), detector temp rise \u22480.008 \u00b0C, bias_drift=false, detector_temp_live=true. No detector bias, responsivity, or thermal signature detected. Detector operating point is electrically and thermally stable at time of check; channel confirmed live (not stuck).",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_check",
            "summary": "TEC current 1.19 A is 47% of the 2.5 A limit; diode temp 25.28 \u00b0C is well below setpoint_max 26.0 \u00b0C; losing_setpoint=false. The TEC has substantial headroom, is tracking its setpoint without strain, and shows no sign of thermal saturation, instability, or runaway. The laser diode thermal operating point is actively and stably controlled at time of check.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_check",
            "summary": "Common-mode check found 0 degraded channels with onset spread 0.00 d \u2014 no shared degradation signature across channels. A shared upstream cause (power rail, firmware push, shared thermal infrastructure) would be expected to produce concurrent multi-channel onset; the complete absence of any such pattern argues strongly against hyp.upstream_power. It also mildly argues against H2 (firmware/calibration drift, which typically propagates system-wide) and H4 (a shared-path thermal instability scenario). Single-unit per-channel hypotheses (H1, H3, H5) are not meaningfully constrained by this result.",
            "source": "common_mode_check"
          },
          {
            "id": "ev.spatial_intensity_check",
            "summary": "Intensity drop is spatially uniform across all 4 sampled regions (spread=0.072, localized=false, affirmative=false). A contaminated window would produce a spatially non-uniform, regionally concentrated attenuation signature; the near-zero spread directly rules that out. Uniformity is instead consistent with any global beam-path or power mechanism \u2014 laser aging, thermal modulation, detector responsivity drift, or upstream power \u2014 all of which would affect all scan regions indiscriminately.",
            "source": "spatial_intensity_check"
          },
          {
            "id": "ev.temp_correlation_check",
            "summary": "mean_return_intensity vs laser_diode_temp_C yields r=-0.24 (correlated=false, affirmative=false). The correlation is below significance and the direction is weakly negative. If TEC/thermal instability were modulating the laser or detector operating point (H4), a materially stronger intensity-temperature relationship would be expected; the near-zero correlation directly undercuts that mechanism. It also mildly argues against any thermally-driven pathway in H3 (laser aging manifesting via thermal runaway) and H5 (detector responsivity drifting with diode temperature). H1, H2, and hyp.upstream_power are not substantially constrained by a thermal correlation test, but the absence of any thermal footprint provides marginal additional argument against each.",
            "source": "temp_correlation_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.spatial_intensity_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.2
          }
        ]
      },
      {
        "status": "abstained",
        "recommended_action": "H3 (laser aging / intermittent output-power drop) is the sole surviving candidate: H1 is excluded by spatially uniform attenuation (ev.spatial_intensity_check); H4 is excluded by near-zero temp correlation and TEC headroom (ev.temp_correlation_check, ev.tec_load_check); H5 is excluded by stable detector operating point (ev.detector_health_check); hyp.upstream_power and H2 are excluded by zero co-degraded channels (ev.common_mode_check); the maintenance reboot is demoted as non-causal (ev.onset_vs_reboot). However, the laser power check (ev.laser_power_check) is a point-in-time snapshot confirming no sustained decline \u2014 it cannot exclude brief transient drops. To confirm or exclude H3, deploy synchronized high-frequency laser output power logging (\u22651 kHz) time-locked to range-measurement records and capture data across multiple fluctuation events; a confirmed transient power excursion co-incident with range drop would confirm H3 and warrant laser diode I-V characterization and aging assessment.",
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination attenuating return signal",
            "node_ref": "part.window",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H2",
            "label": "Calibration / firmware drift shifting range computation",
            "node_ref": "sub.calibration",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H3",
            "label": "Laser aging causing intermittent output-power drop",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "TEC / thermal instability modulating laser or detector operating point",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "H5",
            "label": "Detector responsivity drift producing range-measurement error",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.onset_vs_reboot",
            "summary": "Effective-max-range degradation onset at t\u22487.5 precedes log.reboot (maintenance) at t=8.0. The reboot is coincident, not causal. This demotes any hypothesis whose mechanism would have been initiated by the maintenance event and is consistent with pre-existing, gradual degradation.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.laser_power_check",
            "summary": "Laser output 48.15 mW vs baseline 48.07 mW (+0.2%), ratio 1.0017 \u2014 no sustained decline. Diode temperature 25.28 \u00b0C nominal vs setpoint_max 26.0 \u00b0C, diode_nominal=true, low_power=false. A point-in-time snapshot; cannot exclude brief intermittent drops, but the trend shows no degradation from baseline.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_check",
            "summary": "Dark-count rise \u22480.003 (effectively 0%), detector temp rise \u22480.008 \u00b0C, bias_drift=false, detector_temp_live=true. No detector bias, responsivity, or thermal signature detected. Detector operating point is electrically and thermally stable at time of check; channel confirmed live (not stuck).",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_check",
            "summary": "TEC current 1.19 A is 47% of the 2.5 A limit; diode temp 25.28 \u00b0C is well below setpoint_max 26.0 \u00b0C; losing_setpoint=false. The TEC has substantial headroom, is tracking its setpoint without strain, and shows no sign of thermal saturation, instability, or runaway. The laser diode thermal operating point is actively and stably controlled at time of check.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_check",
            "summary": "Common-mode check found 0 degraded channels with onset spread 0.00 d \u2014 no shared degradation signature across channels. A shared upstream cause (power rail, firmware push, shared thermal infrastructure) would be expected to produce concurrent multi-channel onset; the complete absence of any such pattern argues strongly against hyp.upstream_power. It also mildly argues against H2 (firmware/calibration drift, which typically propagates system-wide) and H4 (a shared-path thermal instability scenario). Single-unit per-channel hypotheses (H1, H3, H5) are not meaningfully constrained by this result.",
            "source": "common_mode_check"
          },
          {
            "id": "ev.spatial_intensity_check",
            "summary": "Intensity drop is spatially uniform across all 4 sampled regions (spread=0.072, localized=false, affirmative=false). A contaminated window would produce a spatially non-uniform, regionally concentrated attenuation signature; the near-zero spread directly rules that out. Uniformity is instead consistent with any global beam-path or power mechanism \u2014 laser aging, thermal modulation, detector responsivity drift, or upstream power \u2014 all of which would affect all scan regions indiscriminately.",
            "source": "spatial_intensity_check"
          },
          {
            "id": "ev.temp_correlation_check",
            "summary": "mean_return_intensity vs laser_diode_temp_C yields r=-0.24 (correlated=false, affirmative=false). The correlation is below significance and the direction is weakly negative. If TEC/thermal instability were modulating the laser or detector operating point (H4), a materially stronger intensity-temperature relationship would be expected; the near-zero correlation directly undercuts that mechanism. It also mildly argues against any thermally-driven pathway in H3 (laser aging manifesting via thermal runaway) and H5 (detector responsivity drifting with diode temperature). H1, H2, and hyp.upstream_power are not substantially constrained by a thermal correlation test, but the absence of any thermal footprint provides marginal additional argument against each.",
            "source": "temp_correlation_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_vs_reboot",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.common_mode_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.spatial_intensity_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H4",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.temp_correlation_check",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.2
          }
        ]
      }
    ],
    "trace": [
      {
        "action": "seed",
        "args": {},
        "rationale": "seed the differential from the symptom",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "H1": 0.5,
          "H2": 0.5,
          "H3": 0.5,
          "H4": 0.5,
          "H5": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "onset_vs_event_check",
          "event": "last_maintenance",
          "symptom": "intermittent_range_fluctuation"
        },
        "rationale": "The symptom was reported 'around the last maintenance', making maintenance the salient candidate event. Before drilling into any component hypothesis, we must establish whether the fluctuation onset predates, coincides with, or postdates the maintenance window. If onset predates maintenance, H1 (window contamination introduced by maintenance) and H2 (calibration/firmware change at maintenance) are substantially weakened as root causes \u2014 maintenance becomes a non-causal coincidence \u2014 and weight shifts toward chronic degradation hypotheses H3 (laser aging), H4 (TEC instability), H5 (detector drift). If onset aligns tightly with or follows maintenance, H1 and H2 rise sharply and H3/H5 (slow-drift processes) are relatively less likely. This single temporal ordering check is maximally discriminating at the current stage because it partitions the hypothesis space along the maintenance-causal vs. pre-existing-degradation axis before any component-level telemetry is pulled.",
        "voi": 0.88,
        "evidence_id": "ev.onset_vs_reboot",
        "conflicts_added": [
          "log.reboot"
        ],
        "leader": "H3",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "H1": 0.182,
          "H2": 0.119,
          "H3": 0.5,
          "H4": 0.5,
          "H5": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "laser_power_check"
        },
        "rationale": "All four remaining hypotheses (H3, H4, H5, hyp.upstream_power) sit at equal log_odds=0.00. The laser_power_check is the highest-leverage split: a nominal, stable laser-output trace argues AGAINST H3 (laser aging) and hyp.upstream_power simultaneously, concentrating posterior weight on H4/H5; an intermittent or trending power drop argues FOR H3 and hyp.upstream_power and against H4/H5. This is a 2-vs-2 partition \u2014 the maximum information gain available in one step. ev.onset_vs_reboot already tells us the degradation is gradual and pre-existing, which is consistent with laser aging or upstream supply drift, making this check the natural next discriminator. TEC and detector checks are better deferred until the transmit-side is cleared or implicated.",
        "voi": 0.85,
        "evidence_id": "ev.laser_power_check",
        "conflicts_added": [],
        "leader": "H5",
        "leader_conf": 0.5,
        "margin": 0.231,
        "confidences": {
          "H1": 0.182,
          "H2": 0.119,
          "H3": 0.119,
          "H4": 0.269,
          "H5": 0.5,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "detector_health_check"
        },
        "rationale": "H5 (detector responsivity drift, log_odds=0.00) is the current leader and remains directly untested. ev.laser_power_check already showed laser output and diode temperature nominal, which partially demotes H4 on its laser side \u2014 but H4 could still manifest as TEC-driven instability at the detector operating point. A detector_health_check now directly probes the detector channel: if responsivity drift or a declining signal channel is found, H5 is confirmed as the primary mechanism and H4 is demoted to a secondary/contributing role at most; if the detector is healthy with normal variance under load, H5 is strongly demoted and H4 (thermal modulation of the detector operating point, not yet checked on the detector side) rises to become the dominant remaining explanation. The result is expected to move H4 and H5 in strictly opposite directions, maximising discrimination between the only two open hypotheses.",
        "voi": 0.87,
        "evidence_id": "ev.detector_health_check",
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.182,
        "margin": 0.0,
        "confidences": {
          "H1": 0.182,
          "H2": 0.119,
          "H3": 0.119,
          "H4": 0.076,
          "H5": 0.119,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "tec_load_check"
        },
        "rationale": "All collected evidence (ev.laser_power_check, ev.detector_health_check) are nominal point-in-time snapshots; neither captures intermittent behaviour. ev.onset_vs_reboot confirms the degradation predates maintenance, ruling out any maintenance-triggered cause and indicating slow, pre-existing deterioration. H4 was tentatively ruled out on the basis that the detector temperature appears stable, but the detector health check only observed the equilibrium temperature \u2014 it did not assess TEC drive current or duty-cycle variance. A TEC that is working progressively harder to maintain setpoint (rising thermal resistance in the mount or cooler degradation) remains fully invisible to a static temperature reading yet would produce periodic brief thermal excursions on the laser or detector operating point that manifest as intermittent range fluctuations. Running tec_load_check will either (a) reveal elevated or variable TEC load, which reopens H4 and H3 as thermally coupled degradation modes and narrows the fault locus to the thermal subsystem, or (b) confirm TEC load is flat and nominal, more definitively closing the thermal family and redirecting effort toward undiscovered causes outside the current hypothesis set. No prior evidence addresses this dimension, so expected information gain is high.",
        "voi": 0.74,
        "evidence_id": "ev.tec_load_check",
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.182,
        "margin": 0.0,
        "confidences": {
          "H1": 0.182,
          "H2": 0.119,
          "H3": 0.047,
          "H4": 0.047,
          "H5": 0.076,
          "hyp.upstream_power": 0.182
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "common_mode_check"
        },
        "rationale": "Every hypothesis has been ruled out via point-in-time snapshot checks, yet the symptom\u2014intermittent range fluctuation with onset predating the maintenance reboot\u2014remains unexplained. The single most discriminating open question is whether the fluctuation is correlated across multiple channels simultaneously (shared/upstream infrastructure: power-supply ripple, clock jitter, chassis vibration, or environmental interference) or strictly isolated to one channel (intermittent local failure not captured in snapshots). A positive common-mode result would directly challenge the ruling-out of hyp.upstream_power and redirect investigation toward shared infrastructure. A negative result would confirm channel isolation and force re-examination of whether any local component (laser, detector, or optical path) produces an intermittent signature invisible to snapshot checks. No prior evidence (ev.laser_power_check, ev.detector_health_check, ev.tec_load_check) addresses cross-channel correlation; this action fills that gap cleanly.",
        "voi": 0.82,
        "evidence_id": "ev.common_mode_check",
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.154,
        "margin": 0.091,
        "confidences": {
          "H1": 0.154,
          "H2": 0.047,
          "H3": 0.047,
          "H4": 0.047,
          "H5": 0.063,
          "hyp.upstream_power": 0.047
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "spatial_intensity_check"
        },
        "rationale": "All established hypotheses are currently marked ruled_out, yet the symptom (intermittent range fluctuation with onset at t\u22487.5, pre-maintenance) persists unexplained. H1 (window contamination, log_odds=-1.70) is the least-negative surviving candidate, and its ruling-out was not directly supported by any spatial measurement in the evidence record \u2014 only by the absence of a common-mode pattern, which does not constrain a single-unit, spatially localised attenuation source. Intermittent or non-uniform contamination (e.g., moisture film, migrating particulate) would produce a spatially structured return-signal deficit invisible to the power snapshot (ev.laser_power_check measures emitted power, not received signal distribution) and to the detector point-check (ev.detector_health_check measures bias/dark-count, not spatial uniformity). A spatial_intensity_check directly probes the return-signal intensity map: a localised cold-spot or asymmetric attenuation would resurrect H1 or surface a beam-path anomaly (alignment/divergence drift) not yet hypothesised; a fully uniform nominal map would instead support a 'no single clean cause / multi-factor or transient' conclusion and allow closure. This is the one unrun check that splits these outcomes along an axis not yet sampled.",
        "voi": 0.75,
        "evidence_id": "ev.spatial_intensity_check",
        "conflicts_added": [],
        "leader": "H5",
        "leader_conf": 0.063,
        "margin": 0.016,
        "confidences": {
          "H1": 0.047,
          "H2": 0.047,
          "H3": 0.047,
          "H4": 0.047,
          "H5": 0.063,
          "hyp.upstream_power": 0.047
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "temp_correlation_check"
        },
        "rationale": "Every static point-in-time check has returned nominal: laser power, detector bias, TEC load, and common-mode are all clear. However, the symptom is explicitly *intermittent*, and ev.laser_power_check (src=laser_power_check) itself notes it 'cannot exclude brief intermittent drops.' The only remaining check not yet executed is temp_correlation_check, which operates over a time-series rather than a snapshot. A time-varying correlation between ambient or diode temperature and range-measurement error would revive H4 (TEC / thermal instability) \u2014 specifically an intermittent regime not captured by a static TEC headroom check \u2014 and could also implicate H3 (laser aging with thermally triggered dropouts). Absence of any correlation would instead argue that all thermal hypotheses are genuinely clear on a time-series basis as well, pushing the conclusion toward either a multi-factor compound cause or no single clean root cause (consistent with the task framing). The onset at t\u22487.5 predates the reboot (ev.onset_vs_reboot, src=onset_vs_event_check), so a slow-build thermal drift mechanism is plausible and pre-dates maintenance. This is the highest-discrimination action available: a positive result lifts H4 (and possibly H3) while a negative result materially collapses the remaining hypothesis space.",
        "voi": 0.72,
        "evidence_id": "ev.temp_correlation_check",
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.047,
        "margin": 0.0,
        "confidences": {
          "H1": 0.047,
          "H2": 0.047,
          "H3": 0.047,
          "H4": 0.047,
          "H5": 0.047,
          "hyp.upstream_power": 0.047
        }
      },
      {
        "action": "conflict_sweep",
        "args": {},
        "rationale": "order onset vs the salient recent event; sanity-check channels",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.047,
        "margin": 0.0,
        "confidences": {
          "H1": 0.047,
          "H2": 0.047,
          "H3": 0.047,
          "H4": 0.047,
          "H5": 0.047,
          "hyp.upstream_power": 0.047
        }
      },
      {
        "action": "synthesize",
        "args": {
          "answer_type": "abstain",
          "root_cause": null
        },
        "rationale": "conclude or abstain from the differential",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.047,
        "margin": 0.0,
        "confidences": {
          "H1": 0.047,
          "H2": 0.047,
          "H3": 0.047,
          "H4": 0.047,
          "H5": 0.047,
          "hyp.upstream_power": 0.047
        }
      }
    ],
    "case_id": "case5",
    "title": "No clean cause (abstain)",
    "caption": "intermittent/coincidence -> correct answer is abstain",
    "answer": {
      "answer_type": "abstain",
      "root_cause": null,
      "cited_evidence": [
        "ev.onset_vs_reboot",
        "ev.laser_power_check",
        "ev.detector_health_check",
        "ev.tec_load_check",
        "ev.common_mode_check",
        "ev.spatial_intensity_check",
        "ev.temp_correlation_check"
      ],
      "conflicts": [
        "log.reboot"
      ]
    },
    "eval_row": {
      "accuracy": 1.0,
      "localization": 1.0,
      "trigger_discrimination": 1.0,
      "conflict_handling": 1.0,
      "evidence_f1": 0.0,
      "tokens": 186581
    },
    "graph": {
      "root": "kpi.effective_range",
      "nodes": [
        {
          "id": "kpi.effective_range",
          "type": "KPI",
          "name": "effective_max_range_m",
          "depth": 0
        },
        {
          "id": "metric.intensity",
          "type": "metric",
          "name": "mean_return_intensity",
          "depth": 1
        },
        {
          "id": "sub.calibration",
          "type": "subsystem",
          "name": "Signal proc / calibration",
          "depth": 1
        },
        {
          "id": "sub.laser",
          "type": "subsystem",
          "name": "Laser emitter",
          "depth": 2
        },
        {
          "id": "sub.optics",
          "type": "subsystem",
          "name": "Optics / window",
          "depth": 2
        },
        {
          "id": "sub.detector",
          "type": "subsystem",
          "name": "Receiver / detector",
          "depth": 2
        },
        {
          "id": "sub.thermal",
          "type": "subsystem",
          "name": "Thermal / TEC",
          "depth": 3
        },
        {
          "id": "sub.power",
          "type": "subsystem",
          "name": "Scanner / power",
          "depth": 4
        },
        {
          "id": "part.laser_module",
          "type": "part_type",
          "name": "Laser module",
          "depth": 3
        },
        {
          "id": "part.window",
          "type": "part_type",
          "name": "Window",
          "depth": 3
        },
        {
          "id": "part.detector",
          "type": "part_type",
          "name": "Detector",
          "depth": 3
        },
        {
          "id": "part.tec",
          "type": "part_type",
          "name": "TEC module",
          "depth": 4
        }
      ],
      "edges": [
        {
          "src": "metric.intensity",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.calibration",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.laser",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.optics",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.detector",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.laser",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.detector",
          "type": "affects"
        },
        {
          "src": "sub.power",
          "dst": "sub.thermal",
          "type": "affects"
        },
        {
          "src": "part.laser_module",
          "dst": "sub.laser",
          "type": "part_of"
        },
        {
          "src": "part.window",
          "dst": "sub.optics",
          "type": "part_of"
        },
        {
          "src": "part.detector",
          "dst": "sub.detector",
          "type": "part_of"
        },
        {
          "src": "part.tec",
          "dst": "sub.thermal",
          "type": "part_of"
        }
      ]
    },
    "explainer": {
      "purpose": "intermittent/coincidence -> correct answer is abstain",
      "answer_type": "abstain",
      "mechanisms": [
        {
          "id": "E1",
          "desc": "There is no single clean cause \u2014 the honest answer is that it's intermittent or coincidental, so the system should abstain rather than invent a culprit."
        }
      ],
      "decoys": [],
      "trigger": "log.reboot"
    }
  },
  "case6": {
    "symptom": "Effective maximum range has degraded ~8% over the past week (about 110 m vs a 120 m baseline). Diagnose the root cause.",
    "trigger": null,
    "root_cause": "part.detector",
    "final_status": "concluded",
    "steps": [
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination / fouling attenuating outgoing beam and return signal",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration / signal-processing drift skewing range calculation or sensitivity threshold",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser emitter aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H4",
            "label": "Detector responsivity drift (dark-current rise, gain shift) reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H5",
            "label": "TEC / thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [],
        "links": []
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination / fouling attenuating outgoing beam and return signal",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration / signal-processing drift skewing range calculation or sensitivity threshold",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser emitter aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "Detector responsivity drift (dark-current rise, gain shift) reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "H5",
            "label": "TEC / thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser emitter output 47.9 mW vs 48.0 mW baseline (\u22120.3%); diode junction temp 25.2 \u00b0C within 26.0 \u00b0C max setpoint; diode_nominal=true, low_power=false, declined=false. No sustained emitter power loss detected.",
            "source": "laser_power_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination / fouling attenuating outgoing beam and return signal",
            "node_ref": "part.window",
            "log_odds": -0.5,
            "confidence": 0.378,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration / signal-processing drift skewing range calculation or sensitivity threshold",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser emitter aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "Detector responsivity drift (dark-current rise, gain shift) reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "leading"
          },
          {
            "id": "H5",
            "label": "TEC / thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser emitter output 47.9 mW vs 48.0 mW baseline (\u22120.3%); diode junction temp 25.2 \u00b0C within 26.0 \u00b0C max setpoint; diode_nominal=true, low_power=false, declined=false. No sustained emitter power loss detected.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_01",
            "summary": "Dark-count rate elevated +56% while detector junction temperature rose only +0.026 \u00b0C (live channel, not stuck); bias_drift=true. The large dark-count rise with a negligible thermal footprint isolates a non-thermal bias/gain drift in the detector as the mechanism elevating the noise floor and degrading SNR at long range. Affirmative = true.",
            "source": "detector_health_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination / fouling attenuating outgoing beam and return signal",
            "node_ref": "part.window",
            "log_odds": -0.5,
            "confidence": 0.378,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration / signal-processing drift skewing range calculation or sensitivity threshold",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser emitter aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "Detector responsivity drift (dark-current rise, gain shift) reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "leading"
          },
          {
            "id": "H5",
            "label": "TEC / thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser emitter output 47.9 mW vs 48.0 mW baseline (\u22120.3%); diode junction temp 25.2 \u00b0C within 26.0 \u00b0C max setpoint; diode_nominal=true, low_power=false, declined=false. No sustained emitter power loss detected.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_01",
            "summary": "Dark-count rate elevated +56% while detector junction temperature rose only +0.026 \u00b0C (live channel, not stuck); bias_drift=true. The large dark-count rise with a negligible thermal footprint isolates a non-thermal bias/gain drift in the detector as the mechanism elevating the noise floor and degrading SNR at long range. Affirmative = true.",
            "source": "detector_health_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "concluded",
        "recommended_action": "Trim or recalibrate detector bias voltage to restore nominal dark-count rate: ev.detector_health_01 shows +56% dark-count elevation with only +0.026 \u00b0C junction temperature rise, isolating a non-thermal bias/gain drift as the SNR-degrading mechanism. If bias adjustment cannot return dark-count rate to within \u00b15% of baseline, schedule detector module replacement. Secondarily, perform a physical window inspection and wipe-down to close H1, which remains open with no direct discriminating evidence; this is low-cost and prevents a latent compounding attenuation path. H3/H5/hyp.upstream_power remain ruled out: ev.laser_power_01 confirms emitter output within 0.3% of baseline and junction temperature within setpoint.",
        "conflicts": [],
        "hypotheses": [
          {
            "id": "H1",
            "label": "Window contamination / fouling attenuating outgoing beam and return signal",
            "node_ref": "part.window",
            "log_odds": -0.5,
            "confidence": 0.378,
            "status": "open"
          },
          {
            "id": "H2",
            "label": "Calibration / signal-processing drift skewing range calculation or sensitivity threshold",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "H3",
            "label": "Laser emitter aging reducing peak output power",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "H4",
            "label": "Detector responsivity drift (dark-current rise, gain shift) reducing SNR at long range",
            "node_ref": "part.detector",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "leading"
          },
          {
            "id": "H5",
            "label": "TEC / thermal regulation failure elevating laser or detector junction temperature and degrading performance",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "Laser emitter output 47.9 mW vs 48.0 mW baseline (\u22120.3%); diode junction temp 25.2 \u00b0C within 26.0 \u00b0C max setpoint; diode_nominal=true, low_power=false, declined=false. No sustained emitter power loss detected.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_01",
            "summary": "Dark-count rate elevated +56% while detector junction temperature rose only +0.026 \u00b0C (live channel, not stuck); bias_drift=true. The large dark-count rise with a negligible thermal footprint isolates a non-thermal bias/gain drift in the detector as the mechanism elevating the noise floor and degrading SNR at long range. Affirmative = true.",
            "source": "detector_health_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "H3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H5",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "H1",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      }
    ],
    "trace": [
      {
        "action": "seed",
        "args": {},
        "rationale": "seed the differential from the symptom",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "H1": 0.5,
          "H2": 0.5,
          "H3": 0.5,
          "H4": 0.5,
          "H5": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "laser_power_check"
        },
        "rationale": "With all six hypotheses at equal prior and zero evidence in hand, the single most discriminating first measurement is emitter output power. A nominal result simultaneously argues AGAINST H3 (laser aging) and AGAINST H5 (TEC-driven junction heating reducing output), collapsing the field to H1/H2/H4/hyp.upstream_power. A degraded result does the opposite \u2014 strongly supporting H3 and flagging H5 as a contributor \u2014 while leaving H1/H2/H4 less likely. No other available check produces this clean a split across this many hypotheses in one step; tec_load_check only addresses H5, detector_health_check only H4, and neither touches laser output.",
        "voi": 0.8,
        "evidence_id": "ev.laser_power_01",
        "conflicts_added": [],
        "leader": "H1",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "H1": 0.5,
          "H2": 0.5,
          "H3": 0.119,
          "H4": 0.5,
          "H5": 0.119,
          "hyp.upstream_power": 0.119
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "detector_health_check"
        },
        "rationale": "ev.laser_power_01 has already eliminated H3 and hyp.upstream_power and strongly argues against H5 (junction temp nominal, emitter output \u22120.3%). The three remaining open hypotheses \u2014 H1 (window fouling), H2 (calibration/processing drift), and H4 (detector responsivity drift) \u2014 are all at equal log_odds=0.00. detector_health_check directly probes the one mechanism (dark-current rise, gain shift) that is wholly distinct from window attenuation and signal-processing error. If dark current and gain are nominal the check argues against H4 and redirects focus to H1/H2; if degraded it sharply raises H4 and argues against H1 and H2 as primary causes. No currently retrieved evidence touches detector parameters, so this is not re-confirming anything already measured.",
        "voi": 0.82,
        "evidence_id": "ev.detector_health_01",
        "conflicts_added": [],
        "leader": "H4",
        "leader_conf": 0.881,
        "margin": 0.503,
        "confidences": {
          "H1": 0.378,
          "H2": 0.269,
          "H3": 0.119,
          "H4": 0.881,
          "H5": 0.047,
          "hyp.upstream_power": 0.119
        }
      },
      {
        "action": "conflict_sweep",
        "args": {},
        "rationale": "order onset vs the salient recent event; sanity-check channels",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "H4",
        "leader_conf": 0.881,
        "margin": 0.503,
        "confidences": {
          "H1": 0.378,
          "H2": 0.269,
          "H3": 0.119,
          "H4": 0.881,
          "H5": 0.047,
          "hyp.upstream_power": 0.119
        }
      },
      {
        "action": "synthesize",
        "args": {
          "answer_type": "cause",
          "root_cause": "part.detector"
        },
        "rationale": "conclude or abstain from the differential",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "H4",
        "leader_conf": 0.881,
        "margin": 0.503,
        "confidences": {
          "H1": 0.378,
          "H2": 0.269,
          "H3": 0.119,
          "H4": 0.881,
          "H5": 0.047,
          "hyp.upstream_power": 0.119
        }
      }
    ],
    "case_id": "case6",
    "title": "Detector bias (buried)",
    "caption": "absent-cue; buried evidence reachable via graph traversal + intra-doc",
    "answer": {
      "answer_type": "cause",
      "root_cause": "part.detector",
      "cited_evidence": [
        "ev.detector_health_01",
        "ev.laser_power_01"
      ],
      "conflicts": []
    },
    "eval_row": {
      "accuracy": 1.0,
      "localization": 1.0,
      "trigger_discrimination": 1.0,
      "conflict_handling": 1.0,
      "evidence_f1": 0.33,
      "tokens": 47348
    },
    "graph": {
      "root": "kpi.effective_range",
      "nodes": [
        {
          "id": "kpi.effective_range",
          "type": "KPI",
          "name": "effective_max_range_m",
          "depth": 0
        },
        {
          "id": "metric.intensity",
          "type": "metric",
          "name": "mean_return_intensity",
          "depth": 1
        },
        {
          "id": "sub.calibration",
          "type": "subsystem",
          "name": "Signal proc / calibration",
          "depth": 1
        },
        {
          "id": "sub.laser",
          "type": "subsystem",
          "name": "Laser emitter",
          "depth": 2
        },
        {
          "id": "sub.optics",
          "type": "subsystem",
          "name": "Optics / window",
          "depth": 2
        },
        {
          "id": "sub.detector",
          "type": "subsystem",
          "name": "Receiver / detector",
          "depth": 2
        },
        {
          "id": "sub.thermal",
          "type": "subsystem",
          "name": "Thermal / TEC",
          "depth": 3
        },
        {
          "id": "sub.power",
          "type": "subsystem",
          "name": "Scanner / power",
          "depth": 4
        },
        {
          "id": "part.laser_module",
          "type": "part_type",
          "name": "Laser module",
          "depth": 3
        },
        {
          "id": "part.window",
          "type": "part_type",
          "name": "Window",
          "depth": 3
        },
        {
          "id": "part.detector",
          "type": "part_type",
          "name": "Detector",
          "depth": 3
        },
        {
          "id": "part.tec",
          "type": "part_type",
          "name": "TEC module",
          "depth": 4
        }
      ],
      "edges": [
        {
          "src": "metric.intensity",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.calibration",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.laser",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.optics",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.detector",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.laser",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.detector",
          "type": "affects"
        },
        {
          "src": "sub.power",
          "dst": "sub.thermal",
          "type": "affects"
        },
        {
          "src": "part.laser_module",
          "dst": "sub.laser",
          "type": "part_of"
        },
        {
          "src": "part.window",
          "dst": "sub.optics",
          "type": "part_of"
        },
        {
          "src": "part.detector",
          "dst": "sub.detector",
          "type": "part_of"
        },
        {
          "src": "part.tec",
          "dst": "sub.thermal",
          "type": "part_of"
        }
      ]
    },
    "explainer": {
      "purpose": "absent-cue; buried evidence reachable via graph traversal + intra-doc",
      "answer_type": "cause",
      "mechanisms": [
        {
          "id": "C1",
          "desc": "The decisive evidence isn't obviously relevant; you only reach it by following a relationship link through the graph to it."
        },
        {
          "id": "C2",
          "desc": "The key fact is buried inside a document you've already found, and has to be dug out of its text."
        }
      ],
      "decoys": [
        "part.tec",
        "part.laser_module",
        "part.window"
      ],
      "trigger": null
    }
  },
  "case7": {
    "symptom": "Effective maximum range has degraded ~8% over the past week (about 110 m vs a 120 m baseline). Diagnose the root cause.",
    "trigger": "log.reboot",
    "root_cause": "part.tec",
    "final_status": "concluded",
    "steps": [
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination (optical loss reducing return signal strength)",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Laser aging / output power decline reducing emitted pulse energy",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h3",
            "label": "Detector drift / sensitivity degradation reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC failure causing temperature-dependent efficiency loss",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift biasing range threshold",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [],
        "links": []
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination (optical loss reducing return signal strength)",
            "node_ref": "part.window",
            "log_odds": -0.5,
            "confidence": 0.378,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Laser aging / output power decline reducing emitted pulse energy",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Detector drift / sensitivity degradation reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -0.5,
            "confidence": 0.378,
            "status": "open"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC failure causing temperature-dependent efficiency loss",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift biasing range threshold",
            "node_ref": "sub.calibration",
            "log_odds": -0.5,
            "confidence": 0.378,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "laser_power_check shows emitted power at 45.4 mW vs 48.1 mW baseline (\u22125.5%). Diode temperature is 28.2 \u00b0C, exceeding TEC setpoint max of 26.0 \u00b0C (diode_nominal=false). System attributes the power decline to thermal excursion, not laser aging. A 5.5% power reduction accounts for only ~1\u20133% of range loss depending on range-power relationship, leaving a gap versus the observed ~8% degradation.",
            "source": "laser_power_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination (optical loss reducing return signal strength)",
            "node_ref": "part.window",
            "log_odds": -0.7,
            "confidence": 0.332,
            "status": "open"
          },
          {
            "id": "h2",
            "label": "Laser aging / output power decline reducing emitted pulse energy",
            "node_ref": "part.laser_module",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Detector drift / sensitivity degradation reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC failure causing temperature-dependent efficiency loss",
            "node_ref": "part.tec",
            "log_odds": -0.5,
            "confidence": 0.378,
            "status": "open"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift biasing range threshold",
            "node_ref": "sub.calibration",
            "log_odds": -0.7,
            "confidence": 0.332,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -0.2,
            "confidence": 0.45,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "laser_power_check shows emitted power at 45.4 mW vs 48.1 mW baseline (\u22125.5%). Diode temperature is 28.2 \u00b0C, exceeding TEC setpoint max of 26.0 \u00b0C (diode_nominal=false). System attributes the power decline to thermal excursion, not laser aging. A 5.5% power reduction accounts for only ~1\u20133% of range loss depending on range-power relationship, leaving a gap versus the observed ~8% degradation.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_01",
            "summary": "detector_health_check returned affirmative=false: dark-count change \u22121% (near-zero), detector temperature rise \u22120.04 \u00b0C (channel live, not stuck), bias_drift=false. No isolated detector degradation or sensitivity-loss signature is present. The detector subsystem appears nominally healthy.",
            "source": "detector_health_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.2
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination (optical loss reducing return signal strength)",
            "node_ref": "part.window",
            "log_odds": -1.2,
            "confidence": 0.231,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Laser aging / output power decline reducing emitted pulse energy",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Detector drift / sensitivity degradation reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC failure causing temperature-dependent efficiency loss",
            "node_ref": "part.tec",
            "log_odds": 1.5,
            "confidence": 0.818,
            "status": "leading"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift biasing range threshold",
            "node_ref": "sub.calibration",
            "log_odds": -1.2,
            "confidence": 0.231,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 1.3,
            "confidence": 0.786,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "laser_power_check shows emitted power at 45.4 mW vs 48.1 mW baseline (\u22125.5%). Diode temperature is 28.2 \u00b0C, exceeding TEC setpoint max of 26.0 \u00b0C (diode_nominal=false). System attributes the power decline to thermal excursion, not laser aging. A 5.5% power reduction accounts for only ~1\u20133% of range loss depending on range-power relationship, leaving a gap versus the observed ~8% degradation.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_01",
            "summary": "detector_health_check returned affirmative=false: dark-count change \u22121% (near-zero), detector temperature rise \u22120.04 \u00b0C (channel live, not stuck), bias_drift=false. No isolated detector degradation or sensitivity-loss signature is present. The detector subsystem appears nominally healthy.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_01",
            "summary": "TEC current is 2.04 A (81.6% of 2.5 A limit) \u2014 elevated but not at hard limit \u2014 yet diode temperature is 28.2 \u00b0C, still 2.2 \u00b0C above the 26.0 \u00b0C setpoint maximum (losing_setpoint=true). The TEC is working hard and cannot hold the diode at setpoint, confirming TEC-side thermal control failure as the proximate cause of diode over-temperature and the associated 5.5% laser power decline recorded in ev.laser_power_01. Because the TEC is undershooting setpoint while drawing substantial current, the fault is thermal management degradation (TEC efficiency loss or heat-load increase), not intrinsic laser aging.",
            "source": "tec_load_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination (optical loss reducing return signal strength)",
            "node_ref": "part.window",
            "log_odds": -2.2,
            "confidence": 0.1,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Laser aging / output power decline reducing emitted pulse energy",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Detector drift / sensitivity degradation reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC failure causing temperature-dependent efficiency loss",
            "node_ref": "part.tec",
            "log_odds": 1.0,
            "confidence": 0.731,
            "status": "leading"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift biasing range threshold",
            "node_ref": "sub.calibration",
            "log_odds": -2.2,
            "confidence": 0.1,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -0.7,
            "confidence": 0.332,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "laser_power_check shows emitted power at 45.4 mW vs 48.1 mW baseline (\u22125.5%). Diode temperature is 28.2 \u00b0C, exceeding TEC setpoint max of 26.0 \u00b0C (diode_nominal=false). System attributes the power decline to thermal excursion, not laser aging. A 5.5% power reduction accounts for only ~1\u20133% of range loss depending on range-power relationship, leaving a gap versus the observed ~8% degradation.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_01",
            "summary": "detector_health_check returned affirmative=false: dark-count change \u22121% (near-zero), detector temperature rise \u22120.04 \u00b0C (channel live, not stuck), bias_drift=false. No isolated detector degradation or sensitivity-loss signature is present. The detector subsystem appears nominally healthy.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_01",
            "summary": "TEC current is 2.04 A (81.6% of 2.5 A limit) \u2014 elevated but not at hard limit \u2014 yet diode temperature is 28.2 \u00b0C, still 2.2 \u00b0C above the 26.0 \u00b0C setpoint maximum (losing_setpoint=true). The TEC is working hard and cannot hold the diode at setpoint, confirming TEC-side thermal control failure as the proximate cause of diode over-temperature and the associated 5.5% laser power decline recorded in ev.laser_power_01. Because the TEC is undershooting setpoint while drawing substantial current, the fault is thermal management degradation (TEC efficiency loss or heat-load increase), not intrinsic laser aging.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_01",
            "summary": "common_mode_check found 2 degraded channels with a 4-day onset spread and returned common_mode=false. Staggered onset rules out any single simultaneous shared-upstream failure (power bus, scanner) that would hit all channels at once, and equally disfavours single-emitter or common-optical causes (laser aging, window contamination) and shared signal-processing drift which would all produce coincident, common-mode degradation. The sequential per-channel pattern is weakly consistent with independent per-channel degradation such as individual detector drift, but is not consistent with the single monolithic upstream cause hypothesis.",
            "source": "common_mode_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination (optical loss reducing return signal strength)",
            "node_ref": "part.window",
            "log_odds": -2.2,
            "confidence": 0.1,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Laser aging / output power decline reducing emitted pulse energy",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Detector drift / sensitivity degradation reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC failure causing temperature-dependent efficiency loss",
            "node_ref": "part.tec",
            "log_odds": 1.0,
            "confidence": 0.731,
            "status": "leading"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift biasing range threshold",
            "node_ref": "sub.calibration",
            "log_odds": -2.2,
            "confidence": 0.1,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -0.7,
            "confidence": 0.332,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "laser_power_check shows emitted power at 45.4 mW vs 48.1 mW baseline (\u22125.5%). Diode temperature is 28.2 \u00b0C, exceeding TEC setpoint max of 26.0 \u00b0C (diode_nominal=false). System attributes the power decline to thermal excursion, not laser aging. A 5.5% power reduction accounts for only ~1\u20133% of range loss depending on range-power relationship, leaving a gap versus the observed ~8% degradation.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_01",
            "summary": "detector_health_check returned affirmative=false: dark-count change \u22121% (near-zero), detector temperature rise \u22120.04 \u00b0C (channel live, not stuck), bias_drift=false. No isolated detector degradation or sensitivity-loss signature is present. The detector subsystem appears nominally healthy.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_01",
            "summary": "TEC current is 2.04 A (81.6% of 2.5 A limit) \u2014 elevated but not at hard limit \u2014 yet diode temperature is 28.2 \u00b0C, still 2.2 \u00b0C above the 26.0 \u00b0C setpoint maximum (losing_setpoint=true). The TEC is working hard and cannot hold the diode at setpoint, confirming TEC-side thermal control failure as the proximate cause of diode over-temperature and the associated 5.5% laser power decline recorded in ev.laser_power_01. Because the TEC is undershooting setpoint while drawing substantial current, the fault is thermal management degradation (TEC efficiency loss or heat-load increase), not intrinsic laser aging.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_01",
            "summary": "common_mode_check found 2 degraded channels with a 4-day onset spread and returned common_mode=false. Staggered onset rules out any single simultaneous shared-upstream failure (power bus, scanner) that would hit all channels at once, and equally disfavours single-emitter or common-optical causes (laser aging, window contamination) and shared signal-processing drift which would all produce coincident, common-mode degradation. The sequential per-channel pattern is weakly consistent with independent per-channel degradation such as individual detector drift, but is not consistent with the single monolithic upstream cause hypothesis.",
            "source": "common_mode_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "concluded",
        "recommended_action": "Service or replace the TEC unit on the affected channel(s). ev.tec_load_01 confirms the TEC is drawing 81.6% of rated current yet cannot hold the diode below the 26.0 \u00b0C setpoint maximum (actual 28.2 \u00b0C), indicating TEC efficiency degradation or increased thermal load \u2014 not intrinsic laser aging (h2 ruled out). This thermal excursion produces the 5.5% emitted-power decline documented in ev.laser_power_01, which is the proximate driver of range reduction. Inspect thermal interface material, heat-sink fouling, and TEC element integrity. After remediation, verify diode temperature returns to \u226426.0 \u00b0C under representative load and that emitted power recovers toward the 48.1 mW baseline. Additionally, the 5.5% power decline accounts for only ~1\u20133% of the observed ~8% range loss; the residual gap, combined with the 4-day staggered per-channel onset in ev.common_mode_01, suggests a second affected channel with independent thermal degradation \u2014 inspect and test both channels individually. A single shared-upstream power or scanner fault (hyp.upstream_power) is ruled out by the staggered, non-coincident onset pattern in ev.common_mode_01. The system reboot (ev.trigger_demoted) is confirmed non-causal as degradation onset predates it.",
        "conflicts": [
          "log.reboot"
        ],
        "hypotheses": [
          {
            "id": "h1",
            "label": "Window contamination (optical loss reducing return signal strength)",
            "node_ref": "part.window",
            "log_odds": -2.2,
            "confidence": 0.1,
            "status": "ruled_out"
          },
          {
            "id": "h2",
            "label": "Laser aging / output power decline reducing emitted pulse energy",
            "node_ref": "part.laser_module",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h3",
            "label": "Detector drift / sensitivity degradation reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "h4",
            "label": "Thermal / TEC failure causing temperature-dependent efficiency loss",
            "node_ref": "part.tec",
            "log_odds": 1.0,
            "confidence": 0.731,
            "status": "leading"
          },
          {
            "id": "h5",
            "label": "Calibration / signal-processing drift biasing range threshold",
            "node_ref": "sub.calibration",
            "log_odds": -2.2,
            "confidence": 0.1,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": -0.7,
            "confidence": 0.332,
            "status": "open"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_01",
            "summary": "laser_power_check shows emitted power at 45.4 mW vs 48.1 mW baseline (\u22125.5%). Diode temperature is 28.2 \u00b0C, exceeding TEC setpoint max of 26.0 \u00b0C (diode_nominal=false). System attributes the power decline to thermal excursion, not laser aging. A 5.5% power reduction accounts for only ~1\u20133% of range loss depending on range-power relationship, leaving a gap versus the observed ~8% degradation.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.detector_health_01",
            "summary": "detector_health_check returned affirmative=false: dark-count change \u22121% (near-zero), detector temperature rise \u22120.04 \u00b0C (channel live, not stuck), bias_drift=false. No isolated detector degradation or sensitivity-loss signature is present. The detector subsystem appears nominally healthy.",
            "source": "detector_health_check"
          },
          {
            "id": "ev.tec_load_01",
            "summary": "TEC current is 2.04 A (81.6% of 2.5 A limit) \u2014 elevated but not at hard limit \u2014 yet diode temperature is 28.2 \u00b0C, still 2.2 \u00b0C above the 26.0 \u00b0C setpoint maximum (losing_setpoint=true). The TEC is working hard and cannot hold the diode at setpoint, confirming TEC-side thermal control failure as the proximate cause of diode over-temperature and the associated 5.5% laser power decline recorded in ev.laser_power_01. Because the TEC is undershooting setpoint while drawing substantial current, the fault is thermal management degradation (TEC efficiency loss or heat-load increase), not intrinsic laser aging.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.common_mode_01",
            "summary": "common_mode_check found 2 degraded channels with a 4-day onset spread and returned common_mode=false. Staggered onset rules out any single simultaneous shared-upstream failure (power bus, scanner) that would hit all channels at once, and equally disfavours single-emitter or common-optical causes (laser aging, window contamination) and shared signal-processing drift which would all produce coincident, common-mode degradation. The sequential per-channel pattern is weakly consistent with independent per-channel degradation such as individual detector drift, but is not consistent with the single monolithic upstream cause hypothesis.",
            "source": "common_mode_check"
          },
          {
            "id": "ev.trigger_demoted",
            "summary": "log.reboot: degradation onset predates it \u2192 coincident, not causal",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.laser_power_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.detector_health_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.2
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h4",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.tec_load_01",
            "hypothesis_id": "h3",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h1",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h2",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h5",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_01",
            "hypothesis_id": "h4",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      }
    ],
    "trace": [
      {
        "action": "seed",
        "args": {},
        "rationale": "seed the differential from the symptom",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h1",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "h1": 0.5,
          "h2": 0.5,
          "h3": 0.5,
          "h4": 0.5,
          "h5": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "laser_power_check"
        },
        "rationale": "No evidence has been collected yet; all hypotheses sit at identical prior odds. Under a standard lidar link budget, an 8 % range reduction maps to roughly a 15 % reduction in peak return power (range \u221d P^0.25 under shot-noise-limited SNR, so \u0394P/P \u2248 4\u00d7\u0394R/R \u2248 32 % in emitted energy, or ~15 % if the exponent is closer to 2 in the near-saturation regime \u2014 either way, a measurable transmitter-side drop). Laser output power is the first node in the signal chain and the single quantity that simultaneously discriminates h2 (laser aging), hyp.upstream_power (supply/scanner shared source), and h4 (TEC failure indirectly reducing laser efficiency via junction temperature). Result branches: (A) power DEGRADED \u226510 % \u2192 strongly raises h2 and hyp.upstream_power, prompts tec_load_check to distinguish intrinsic aging from thermally-driven decline, and weakens h1/h3/h5; (B) power NOMINAL \u2192 eliminates h2 and hyp.upstream_power with high confidence, narrows the differential to receiver-side (h3 detector drift), optical path (h1 window contamination), or processing (h5 calibration drift), and makes detector_health_check and temp_correlation_check the natural next steps. No other single check achieves this two-branch split across three hypotheses simultaneously.",
        "voi": 0.82,
        "evidence_id": "ev.laser_power_01",
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "h1": 0.378,
          "h2": 0.119,
          "h3": 0.378,
          "h4": 0.5,
          "h5": 0.378,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "detector_health_check"
        },
        "rationale": "TEC overtemperature is already confirmed by ev.laser_power_01 (diode at 28.2 \u00b0C vs 26.0 \u00b0C setpoint; diode_nominal=false), so h4 is partially supported. However, the 5.5% emitted-power reduction maps to only ~1\u20133% range loss, leaving ~5\u20136% of the observed 8% degradation unexplained. The leading competing explanations for the residual gap are h3 (detector sensitivity degradation \u2014 possibly thermally induced via the same TEC fault, since a warm detector raises dark current and lowers SNR) vs. h1 (window contamination, independent optical loss) vs. h5 (calibration/threshold drift). detector_health_check directly measures detector responsivity, dark current, and noise floor. If the detector is degraded and the degradation tracks temperature, h4 becomes the unified root cause (TEC failure depressing both emission AND detection arms). If the detector is nominal, h3 is effectively ruled out, the residual gap must come from h1 or h5, and h4 is bounded to the laser-power pathway only. This action therefore simultaneously probes h3 and limits or extends h4 \u2014 neither of which is yet constrained by existing evidence.",
        "voi": 0.82,
        "evidence_id": "ev.detector_health_01",
        "conflicts_added": [],
        "leader": "hyp.upstream_power",
        "leader_conf": 0.45,
        "margin": 0.073,
        "confidences": {
          "h1": 0.332,
          "h2": 0.119,
          "h3": 0.076,
          "h4": 0.378,
          "h5": 0.332,
          "hyp.upstream_power": 0.45
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "tec_load_check"
        },
        "rationale": "ev.laser_power_01 already confirms a thermal excursion (diode at 28.2 \u00b0C vs TEC setpoint max 26.0 \u00b0C) that explains only ~1\u20133% of the observed ~8% range loss. The critical unresolved question is WHY the TEC is failing to hold setpoint: (a) the TEC stage itself is degrading or saturated (\u2192 h4 confirmed, hyp.upstream_power deprioritised), or (b) the TEC is being starved of drive current/voltage by an upstream power rail fault (\u2192 hyp.upstream_power confirmed, h4 deprioritised). tec_load_check directly probes TEC drive current, voltage compliance, \u0394T achieved vs demanded, and duty cycle \u2014 exactly the discriminating measurement. h1 and h5 cannot be meaningfully separated until the thermal/power causal chain is resolved, because a larger-than-expected range deficit could be a compounding artefact of uncorrected thermal gain shift (h5) driven by the same TEC fault. Running this check now prevents chasing window or calibration artefacts while the primary thermal fault remains uncharacterised.",
        "voi": 0.82,
        "evidence_id": "ev.tec_load_01",
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.818,
        "margin": 0.032,
        "confidences": {
          "h1": 0.231,
          "h2": 0.047,
          "h3": 0.047,
          "h4": 0.818,
          "h5": 0.231,
          "hyp.upstream_power": 0.786
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "common_mode_check"
        },
        "rationale": "The two leading hypotheses \u2014 h4 (isolated TEC/thermal failure in the diode thermal loop, log_odds=1.50) and hyp.upstream_power (shared upstream power or scanner degradation, log_odds=1.30) \u2014 have nearly equal posterior weight and are not yet separated by existing evidence. A critical unexplained gap persists: ev.laser_power_01 confirms a 5.5% emitted-power drop driven by the TEC over-temperature documented in ev.tec_load_01, yet a 5.5% power reduction translates to only ~1\u20133% range loss (depending on the range-power exponent), leaving ~5\u20137% of the observed 8% degradation unaccounted for by h4 alone. If hyp.upstream_power is correct \u2014 e.g., a sagging shared power rail \u2014 it would simultaneously cause the TEC to draw elevated current (consistent with ev.tec_load_01) AND reduce supply voltage to other subsystems (detector bias, scanner drive), producing a common-mode degradation signature across multiple channels or subsystems correlated in time. If h4 is a purely isolated TEC efficiency or heat-load failure, only the diode thermal channel is affected; all other subsystems remain nominal, and no common-mode pattern exists. A common_mode_check directly discriminates: common-mode present \u2192 strongly raises hyp.upstream_power and demotes h4 to a downstream symptom of a shared-supply fault; common-mode absent \u2192 confirms h4 as an isolated fault and forces a search for a separate mechanism to explain the residual ~5\u20137% range loss. This is the highest-leverage single action available \u2014 neither re-confirming already-supported evidence (ev.tec_load_01 already confirms TEC is losing setpoint) nor redundant with ruled-out hypotheses.",
        "voi": 0.85,
        "evidence_id": "ev.common_mode_01",
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.731,
        "margin": 0.399,
        "confidences": {
          "h1": 0.1,
          "h2": 0.047,
          "h3": 0.047,
          "h4": 0.731,
          "h5": 0.1,
          "hyp.upstream_power": 0.332
        }
      },
      {
        "action": "conflict_sweep",
        "args": {},
        "rationale": "order onset vs the salient recent event; sanity-check channels",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [
          "log.reboot"
        ],
        "leader": "h4",
        "leader_conf": 0.731,
        "margin": 0.399,
        "confidences": {
          "h1": 0.1,
          "h2": 0.047,
          "h3": 0.047,
          "h4": 0.731,
          "h5": 0.1,
          "hyp.upstream_power": 0.332
        }
      },
      {
        "action": "synthesize",
        "args": {
          "answer_type": "cause",
          "root_cause": "part.tec"
        },
        "rationale": "conclude or abstain from the differential",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "h4",
        "leader_conf": 0.731,
        "margin": 0.399,
        "confidences": {
          "h1": 0.1,
          "h2": 0.047,
          "h3": 0.047,
          "h4": 0.731,
          "h5": 0.1,
          "hyp.upstream_power": 0.332
        }
      }
    ],
    "case_id": "case7",
    "title": "TEC tie-breaker",
    "caption": "near-symmetric to a decoy; needs the expensive discriminating check",
    "answer": {
      "answer_type": "cause",
      "root_cause": "part.tec",
      "cited_evidence": [
        "ev.tec_load_01",
        "ev.laser_power_01",
        "ev.detector_health_01",
        "ev.common_mode_01",
        "ev.trigger_demoted"
      ],
      "conflicts": [
        "log.reboot"
      ]
    },
    "eval_row": {
      "accuracy": 1.0,
      "localization": 1.0,
      "trigger_discrimination": 1.0,
      "conflict_handling": 1.0,
      "evidence_f1": 0.44,
      "tokens": 128121
    },
    "graph": {
      "root": "kpi.effective_range",
      "nodes": [
        {
          "id": "kpi.effective_range",
          "type": "KPI",
          "name": "effective_max_range_m",
          "depth": 0
        },
        {
          "id": "metric.intensity",
          "type": "metric",
          "name": "mean_return_intensity",
          "depth": 1
        },
        {
          "id": "sub.calibration",
          "type": "subsystem",
          "name": "Signal proc / calibration",
          "depth": 1
        },
        {
          "id": "sub.laser",
          "type": "subsystem",
          "name": "Laser emitter",
          "depth": 2
        },
        {
          "id": "sub.optics",
          "type": "subsystem",
          "name": "Optics / window",
          "depth": 2
        },
        {
          "id": "sub.detector",
          "type": "subsystem",
          "name": "Receiver / detector",
          "depth": 2
        },
        {
          "id": "sub.thermal",
          "type": "subsystem",
          "name": "Thermal / TEC",
          "depth": 3
        },
        {
          "id": "sub.power",
          "type": "subsystem",
          "name": "Scanner / power",
          "depth": 4
        },
        {
          "id": "part.laser_module",
          "type": "part_type",
          "name": "Laser module",
          "depth": 3
        },
        {
          "id": "part.window",
          "type": "part_type",
          "name": "Window",
          "depth": 3
        },
        {
          "id": "part.detector",
          "type": "part_type",
          "name": "Detector",
          "depth": 3
        },
        {
          "id": "part.tec",
          "type": "part_type",
          "name": "TEC module",
          "depth": 4
        }
      ],
      "edges": [
        {
          "src": "metric.intensity",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.calibration",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.laser",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.optics",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.detector",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.laser",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.detector",
          "type": "affects"
        },
        {
          "src": "sub.power",
          "dst": "sub.thermal",
          "type": "affects"
        },
        {
          "src": "part.laser_module",
          "dst": "sub.laser",
          "type": "part_of"
        },
        {
          "src": "part.window",
          "dst": "sub.optics",
          "type": "part_of"
        },
        {
          "src": "part.detector",
          "dst": "sub.detector",
          "type": "part_of"
        },
        {
          "src": "part.tec",
          "dst": "sub.thermal",
          "type": "part_of"
        }
      ]
    },
    "explainer": {
      "purpose": "near-symmetric to a decoy; needs the expensive discriminating check",
      "answer_type": "cause",
      "mechanisms": [
        {
          "id": "D6",
          "desc": "D6"
        }
      ],
      "decoys": [
        "part.laser_module"
      ],
      "trigger": "log.reboot"
    }
  },
  "case8": {
    "symptom": "Effective maximum range has degraded ~8% over the past week (about 110 m vs a 120 m baseline). Diagnose the root cause.",
    "trigger": null,
    "root_cause": "sub.power",
    "final_status": "concluded",
    "steps": [
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          }
        ],
        "evidence": [],
        "links": []
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "leading"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 1.0,
            "confidence": 0.731,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.common_mode_check_001",
            "summary": "Common-mode check confirms 3 channels degraded with an onset spread of only 1.25 days, indicating a single shared upstream failure rather than independent per-channel faults. This eliminates independent multi-channel drift as an explanation and strongly implicates a component that sits upstream of all affected channels (laser drive, optical path, or shared signal processing).",
            "source": "common_mode_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": null,
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.5,
            "confidence": 0.622,
            "status": "supported"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": -1.5,
            "confidence": 0.182,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 2.5,
            "confidence": 0.924,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.common_mode_check_001",
            "summary": "Common-mode check confirms 3 channels degraded with an onset spread of only 1.25 days, indicating a single shared upstream failure rather than independent per-channel faults. This eliminates independent multi-channel drift as an explanation and strongly implicates a component that sits upstream of all affected channels (laser drive, optical path, or shared signal processing).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.onset_event_check_001",
            "summary": "onset_vs_event_check returned no logged reboot or timed configuration-change event (log.reboot absent). No discrete system event exists that could align with the degradation onset, eliminating event-triggered calibration coefficient shifts or post-reboot mis-initialisation as a cause. The absence is consistent with gradual, non-event-driven mechanisms such as progressive emitter aging or slow optical-path contamination.",
            "source": "onset_vs_event_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": "Recommended-but-untried: swap the laser module to cleanly isolate laser aging from a thermal cause before ordering parts. High value of information.",
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 2.0,
            "confidence": 0.881,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.common_mode_check_001",
            "summary": "Common-mode check confirms 3 channels degraded with an onset spread of only 1.25 days, indicating a single shared upstream failure rather than independent per-channel faults. This eliminates independent multi-channel drift as an explanation and strongly implicates a component that sits upstream of all affected channels (laser drive, optical path, or shared signal processing).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.onset_event_check_001",
            "summary": "onset_vs_event_check returned no logged reboot or timed configuration-change event (log.reboot absent). No discrete system event exists that could align with the degradation onset, eliminating event-triggered calibration coefficient shifts or post-reboot mis-initialisation as a cause. The absence is consistent with gradual, non-event-driven mechanisms such as progressive emitter aging or slow optical-path contamination.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.swap_rec_001",
            "summary": "Swap test of the laser emitter module recommended but not yet executed. The recommendation identifies the laser emitter module as the single most discriminating component to isolate next, framing the test as separating intrinsic emitter aging from any residual thermal cause (the latter already largely ruled out by ev.laser_power_check_001). No empirical outcome exists yet; evidential weight is modest and prospective. Critically, the recommendation prioritises the emitter module over optical-path inspection (window cleaning) and over upstream drive-circuit investigation, implicitly deprioritising both hyp.window_contamination and hyp.upstream_power as primary root causes at this stage.",
            "source": "recommend_swap_test"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 0.5
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": "Recommended-but-untried: swap the laser module to cleanly isolate laser aging from a thermal cause before ordering parts. High value of information.",
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.common_mode_check_001",
            "summary": "Common-mode check confirms 3 channels degraded with an onset spread of only 1.25 days, indicating a single shared upstream failure rather than independent per-channel faults. This eliminates independent multi-channel drift as an explanation and strongly implicates a component that sits upstream of all affected channels (laser drive, optical path, or shared signal processing).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.onset_event_check_001",
            "summary": "onset_vs_event_check returned no logged reboot or timed configuration-change event (log.reboot absent). No discrete system event exists that could align with the degradation onset, eliminating event-triggered calibration coefficient shifts or post-reboot mis-initialisation as a cause. The absence is consistent with gradual, non-event-driven mechanisms such as progressive emitter aging or slow optical-path contamination.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.swap_rec_001",
            "summary": "Swap test of the laser emitter module recommended but not yet executed. The recommendation identifies the laser emitter module as the single most discriminating component to isolate next, framing the test as separating intrinsic emitter aging from any residual thermal cause (the latter already largely ruled out by ev.laser_power_check_001). No empirical outcome exists yet; evidential weight is modest and prospective. Critically, the recommendation prioritises the emitter module over optical-path inspection (window cleaning) and over upstream drive-circuit investigation, implicitly deprioritising both hyp.window_contamination and hyp.upstream_power as primary root causes at this stage.",
            "source": "recommend_swap_test"
          },
          {
            "id": "ev.config_diff_001",
            "summary": "config_diff shows scan_params changed from 'raster_default' to 'high_power_v2'. No timestamp accompanies this record, so onset alignment with the ~1-week degradation cannot be confirmed; without that confirmation the change must be treated as coincident rather than causal. The shift to a 'high_power_v2' scan profile implies an upstream alteration to scanner or laser-drive operating parameters, consistent with a shared upstream configuration cause affecting all channels simultaneously. The finding conflicts with ev.onset_event_check_001, which asserted no configuration-change event existed in the event log; the discrepancy indicates this mutation occurred outside the formal event-logging system. The existence of an alternative upstream configuration explanation marginally undercuts hyp.laser_aging as a purely intrinsic mechanism for the observed power deficit.",
            "source": "config_diff"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": "Recommended-but-untried: swap the laser module to cleanly isolate laser aging from a thermal cause before ordering parts. High value of information.",
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": -1.0,
            "confidence": 0.269,
            "status": "open"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.common_mode_check_001",
            "summary": "Common-mode check confirms 3 channels degraded with an onset spread of only 1.25 days, indicating a single shared upstream failure rather than independent per-channel faults. This eliminates independent multi-channel drift as an explanation and strongly implicates a component that sits upstream of all affected channels (laser drive, optical path, or shared signal processing).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.onset_event_check_001",
            "summary": "onset_vs_event_check returned no logged reboot or timed configuration-change event (log.reboot absent). No discrete system event exists that could align with the degradation onset, eliminating event-triggered calibration coefficient shifts or post-reboot mis-initialisation as a cause. The absence is consistent with gradual, non-event-driven mechanisms such as progressive emitter aging or slow optical-path contamination.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.swap_rec_001",
            "summary": "Swap test of the laser emitter module recommended but not yet executed. The recommendation identifies the laser emitter module as the single most discriminating component to isolate next, framing the test as separating intrinsic emitter aging from any residual thermal cause (the latter already largely ruled out by ev.laser_power_check_001). No empirical outcome exists yet; evidential weight is modest and prospective. Critically, the recommendation prioritises the emitter module over optical-path inspection (window cleaning) and over upstream drive-circuit investigation, implicitly deprioritising both hyp.window_contamination and hyp.upstream_power as primary root causes at this stage.",
            "source": "recommend_swap_test"
          },
          {
            "id": "ev.config_diff_001",
            "summary": "config_diff shows scan_params changed from 'raster_default' to 'high_power_v2'. No timestamp accompanies this record, so onset alignment with the ~1-week degradation cannot be confirmed; without that confirmation the change must be treated as coincident rather than causal. The shift to a 'high_power_v2' scan profile implies an upstream alteration to scanner or laser-drive operating parameters, consistent with a shared upstream configuration cause affecting all channels simultaneously. The finding conflicts with ev.onset_event_check_001, which asserted no configuration-change event existed in the event log; the discrepancy indicates this mutation occurred outside the formal event-logging system. The existence of an alternative upstream configuration explanation marginally undercuts hyp.laser_aging as a purely intrinsic mechanism for the observed power deficit.",
            "source": "config_diff"
          },
          {
            "id": "ev.tec_load_check_001",
            "summary": "TEC current is 1.98 A \u2014 79% of the 2.5 A limit \u2014 and is not at limit. Diode junction temperature is 25.21 \u00b0C against a 26.0 \u00b0C setpoint maximum; losing_setpoint is false. The TEC is operating comfortably within capacity and maintaining full thermal control. This independently corroborates ev.laser_power_check_001's finding that the laser power deficit is not thermally driven, and eliminates TEC underperformance as a contributing mechanism to the observed range degradation.",
            "source": "tec_load_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": "Recommended-but-untried: swap the laser module to cleanly isolate laser aging from a thermal cause before ordering parts. High value of information.",
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "supported"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.common_mode_check_001",
            "summary": "Common-mode check confirms 3 channels degraded with an onset spread of only 1.25 days, indicating a single shared upstream failure rather than independent per-channel faults. This eliminates independent multi-channel drift as an explanation and strongly implicates a component that sits upstream of all affected channels (laser drive, optical path, or shared signal processing).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.onset_event_check_001",
            "summary": "onset_vs_event_check returned no logged reboot or timed configuration-change event (log.reboot absent). No discrete system event exists that could align with the degradation onset, eliminating event-triggered calibration coefficient shifts or post-reboot mis-initialisation as a cause. The absence is consistent with gradual, non-event-driven mechanisms such as progressive emitter aging or slow optical-path contamination.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.swap_rec_001",
            "summary": "Swap test of the laser emitter module recommended but not yet executed. The recommendation identifies the laser emitter module as the single most discriminating component to isolate next, framing the test as separating intrinsic emitter aging from any residual thermal cause (the latter already largely ruled out by ev.laser_power_check_001). No empirical outcome exists yet; evidential weight is modest and prospective. Critically, the recommendation prioritises the emitter module over optical-path inspection (window cleaning) and over upstream drive-circuit investigation, implicitly deprioritising both hyp.window_contamination and hyp.upstream_power as primary root causes at this stage.",
            "source": "recommend_swap_test"
          },
          {
            "id": "ev.config_diff_001",
            "summary": "config_diff shows scan_params changed from 'raster_default' to 'high_power_v2'. No timestamp accompanies this record, so onset alignment with the ~1-week degradation cannot be confirmed; without that confirmation the change must be treated as coincident rather than causal. The shift to a 'high_power_v2' scan profile implies an upstream alteration to scanner or laser-drive operating parameters, consistent with a shared upstream configuration cause affecting all channels simultaneously. The finding conflicts with ev.onset_event_check_001, which asserted no configuration-change event existed in the event log; the discrepancy indicates this mutation occurred outside the formal event-logging system. The existence of an alternative upstream configuration explanation marginally undercuts hyp.laser_aging as a purely intrinsic mechanism for the observed power deficit.",
            "source": "config_diff"
          },
          {
            "id": "ev.tec_load_check_001",
            "summary": "TEC current is 1.98 A \u2014 79% of the 2.5 A limit \u2014 and is not at limit. Diode junction temperature is 25.21 \u00b0C against a 26.0 \u00b0C setpoint maximum; losing_setpoint is false. The TEC is operating comfortably within capacity and maintaining full thermal control. This independently corroborates ev.laser_power_check_001's finding that the laser power deficit is not thermally driven, and eliminates TEC underperformance as a contributing mechanism to the observed range degradation.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.traverse_config_001",
            "summary": "Traversal of config record 'scan_params:high_power_v2' requesting fields [timestamp_applied, drive_current_setpoint_mA, param_delta_vs_raster_default, applied_by] returned a key error ('node_id'). No data was retrieved. Consequently: (1) the timestamp of the high_power_v2 profile application remains unknown, so onset alignment with the ~1-week degradation still cannot be confirmed or denied; (2) whether this profile altered laser drive-current setpoints \u2014 which could explain the 13% power deficit extrinsically \u2014 cannot be established from this path. The config change evidenced in ev.config_diff_001 is real but its detailed record is not traversable as a structured node, deepening the discrepancy with ev.onset_event_check_001. The failure to retrieve drive-current delta leaves hyp.upstream_power mechanistically unsubstantiated and marginally favours hyp.laser_aging as the primary remaining explanation.",
            "source": "traverse:config_record:scan_params:high_power_v2"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.0
          }
        ]
      },
      {
        "status": "in_progress",
        "recommended_action": "Recommended-but-untried: swap the laser module to cleanly isolate laser aging from a thermal cause before ordering parts. High value of information.",
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.common_mode_check_001",
            "summary": "Common-mode check confirms 3 channels degraded with an onset spread of only 1.25 days, indicating a single shared upstream failure rather than independent per-channel faults. This eliminates independent multi-channel drift as an explanation and strongly implicates a component that sits upstream of all affected channels (laser drive, optical path, or shared signal processing).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.onset_event_check_001",
            "summary": "onset_vs_event_check returned no logged reboot or timed configuration-change event (log.reboot absent). No discrete system event exists that could align with the degradation onset, eliminating event-triggered calibration coefficient shifts or post-reboot mis-initialisation as a cause. The absence is consistent with gradual, non-event-driven mechanisms such as progressive emitter aging or slow optical-path contamination.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.swap_rec_001",
            "summary": "Swap test of the laser emitter module recommended but not yet executed. The recommendation identifies the laser emitter module as the single most discriminating component to isolate next, framing the test as separating intrinsic emitter aging from any residual thermal cause (the latter already largely ruled out by ev.laser_power_check_001). No empirical outcome exists yet; evidential weight is modest and prospective. Critically, the recommendation prioritises the emitter module over optical-path inspection (window cleaning) and over upstream drive-circuit investigation, implicitly deprioritising both hyp.window_contamination and hyp.upstream_power as primary root causes at this stage.",
            "source": "recommend_swap_test"
          },
          {
            "id": "ev.config_diff_001",
            "summary": "config_diff shows scan_params changed from 'raster_default' to 'high_power_v2'. No timestamp accompanies this record, so onset alignment with the ~1-week degradation cannot be confirmed; without that confirmation the change must be treated as coincident rather than causal. The shift to a 'high_power_v2' scan profile implies an upstream alteration to scanner or laser-drive operating parameters, consistent with a shared upstream configuration cause affecting all channels simultaneously. The finding conflicts with ev.onset_event_check_001, which asserted no configuration-change event existed in the event log; the discrepancy indicates this mutation occurred outside the formal event-logging system. The existence of an alternative upstream configuration explanation marginally undercuts hyp.laser_aging as a purely intrinsic mechanism for the observed power deficit.",
            "source": "config_diff"
          },
          {
            "id": "ev.tec_load_check_001",
            "summary": "TEC current is 1.98 A \u2014 79% of the 2.5 A limit \u2014 and is not at limit. Diode junction temperature is 25.21 \u00b0C against a 26.0 \u00b0C setpoint maximum; losing_setpoint is false. The TEC is operating comfortably within capacity and maintaining full thermal control. This independently corroborates ev.laser_power_check_001's finding that the laser power deficit is not thermally driven, and eliminates TEC underperformance as a contributing mechanism to the observed range degradation.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.traverse_config_001",
            "summary": "Traversal of config record 'scan_params:high_power_v2' requesting fields [timestamp_applied, drive_current_setpoint_mA, param_delta_vs_raster_default, applied_by] returned a key error ('node_id'). No data was retrieved. Consequently: (1) the timestamp of the high_power_v2 profile application remains unknown, so onset alignment with the ~1-week degradation still cannot be confirmed or denied; (2) whether this profile altered laser drive-current setpoints \u2014 which could explain the 13% power deficit extrinsically \u2014 cannot be established from this path. The config change evidenced in ev.config_diff_001 is real but its detailed record is not traversable as a structured node, deepening the discrepancy with ev.onset_event_check_001. The failure to retrieve drive-current delta leaves hyp.upstream_power mechanistically unsubstantiated and marginally favours hyp.laser_aging as the primary remaining explanation.",
            "source": "traverse:config_record:scan_params:high_power_v2"
          },
          {
            "id": "ev.change_cause_log.power_mode",
            "summary": "log.power_mode: a recent config change to sub.power aligns with the degradation onset \u2192 the change is the cause",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.common_mode",
            "summary": "3 degraded channel(s), onset spread 1.25d \u2192 common-mode (one upstream cause, not independent faults)",
            "source": "common_mode_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.0
          },
          {
            "evidence_id": "ev.change_cause_log.power_mode",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 1.5
          }
        ]
      },
      {
        "status": "concluded",
        "recommended_action": "Access the high_power_v2 config record via an alternative path (e.g., flat config dump or direct filesystem read, not the failed structured-node traversal) to retrieve drive_current_setpoint_mA and diff it against raster_default. ev.laser_power_check_001 shows a 13% emitter power deficit that is not thermally driven (ev.tec_load_check_001 confirms TEC healthy); the most parsimonious extrinsic explanation is a reduced drive-current setpoint introduced by the unlogged sub.power / scan_params change to high_power_v2 (ev.change_cause_log.power_mode, ev.config_diff_001). If the drive-current setpoint is confirmed lower, revert scan_params to raster_default and verify range recovery to the 120 m baseline. If drive-current is unchanged in the config, escalate to physical emitter inspection; only then does intrinsic laser aging become the primary candidate.",
        "conflicts": [],
        "hypotheses": [
          {
            "id": "hyp.window_contamination",
            "label": "Window contamination attenuating TX/RX optical path",
            "node_ref": "part.window",
            "log_odds": 0.0,
            "confidence": 0.5,
            "status": "open"
          },
          {
            "id": "hyp.laser_aging",
            "label": "Laser emitter output power degraded due to aging or drive-current shift",
            "node_ref": "part.laser_module",
            "log_odds": -2.5,
            "confidence": 0.076,
            "status": "ruled_out"
          },
          {
            "id": "hyp.detector_drift",
            "label": "Receiver/detector sensitivity drift reducing SNR at range",
            "node_ref": "part.detector",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.thermal_tec",
            "label": "TEC module underperforming, elevating detector/laser junction temp and degrading efficiency",
            "node_ref": "part.tec",
            "log_odds": -3.0,
            "confidence": 0.047,
            "status": "ruled_out"
          },
          {
            "id": "hyp.calibration_drift",
            "label": "Signal processing / calibration coefficients drifted, causing systematic range underreporting or sensitivity reduction",
            "node_ref": "sub.calibration",
            "log_odds": -2.0,
            "confidence": 0.119,
            "status": "ruled_out"
          },
          {
            "id": "hyp.upstream_power",
            "label": "Scanner / power (shared upstream cause)",
            "node_ref": "sub.power",
            "log_odds": 3.0,
            "confidence": 0.953,
            "status": "leading"
          }
        ],
        "evidence": [
          {
            "id": "ev.laser_power_check_001",
            "summary": "Laser emitter output 41.8 mW vs 48.0 mW baseline (\u221213.0%) \u2014 a sustained decline exceeding the observed 8% range loss. Diode junction temperature 25.2 \u00b0C is within the 26.0 \u00b0C setpoint, confirming TEC is maintaining thermal control; the power loss is therefore intrinsic to the emitter, not thermally driven.",
            "source": "laser_power_check"
          },
          {
            "id": "ev.common_mode_check_001",
            "summary": "Common-mode check confirms 3 channels degraded with an onset spread of only 1.25 days, indicating a single shared upstream failure rather than independent per-channel faults. This eliminates independent multi-channel drift as an explanation and strongly implicates a component that sits upstream of all affected channels (laser drive, optical path, or shared signal processing).",
            "source": "common_mode_check"
          },
          {
            "id": "ev.onset_event_check_001",
            "summary": "onset_vs_event_check returned no logged reboot or timed configuration-change event (log.reboot absent). No discrete system event exists that could align with the degradation onset, eliminating event-triggered calibration coefficient shifts or post-reboot mis-initialisation as a cause. The absence is consistent with gradual, non-event-driven mechanisms such as progressive emitter aging or slow optical-path contamination.",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.swap_rec_001",
            "summary": "Swap test of the laser emitter module recommended but not yet executed. The recommendation identifies the laser emitter module as the single most discriminating component to isolate next, framing the test as separating intrinsic emitter aging from any residual thermal cause (the latter already largely ruled out by ev.laser_power_check_001). No empirical outcome exists yet; evidential weight is modest and prospective. Critically, the recommendation prioritises the emitter module over optical-path inspection (window cleaning) and over upstream drive-circuit investigation, implicitly deprioritising both hyp.window_contamination and hyp.upstream_power as primary root causes at this stage.",
            "source": "recommend_swap_test"
          },
          {
            "id": "ev.config_diff_001",
            "summary": "config_diff shows scan_params changed from 'raster_default' to 'high_power_v2'. No timestamp accompanies this record, so onset alignment with the ~1-week degradation cannot be confirmed; without that confirmation the change must be treated as coincident rather than causal. The shift to a 'high_power_v2' scan profile implies an upstream alteration to scanner or laser-drive operating parameters, consistent with a shared upstream configuration cause affecting all channels simultaneously. The finding conflicts with ev.onset_event_check_001, which asserted no configuration-change event existed in the event log; the discrepancy indicates this mutation occurred outside the formal event-logging system. The existence of an alternative upstream configuration explanation marginally undercuts hyp.laser_aging as a purely intrinsic mechanism for the observed power deficit.",
            "source": "config_diff"
          },
          {
            "id": "ev.tec_load_check_001",
            "summary": "TEC current is 1.98 A \u2014 79% of the 2.5 A limit \u2014 and is not at limit. Diode junction temperature is 25.21 \u00b0C against a 26.0 \u00b0C setpoint maximum; losing_setpoint is false. The TEC is operating comfortably within capacity and maintaining full thermal control. This independently corroborates ev.laser_power_check_001's finding that the laser power deficit is not thermally driven, and eliminates TEC underperformance as a contributing mechanism to the observed range degradation.",
            "source": "tec_load_check"
          },
          {
            "id": "ev.traverse_config_001",
            "summary": "Traversal of config record 'scan_params:high_power_v2' requesting fields [timestamp_applied, drive_current_setpoint_mA, param_delta_vs_raster_default, applied_by] returned a key error ('node_id'). No data was retrieved. Consequently: (1) the timestamp of the high_power_v2 profile application remains unknown, so onset alignment with the ~1-week degradation still cannot be confirmed or denied; (2) whether this profile altered laser drive-current setpoints \u2014 which could explain the 13% power deficit extrinsically \u2014 cannot be established from this path. The config change evidenced in ev.config_diff_001 is real but its detailed record is not traversable as a structured node, deepening the discrepancy with ev.onset_event_check_001. The failure to retrieve drive-current delta leaves hyp.upstream_power mechanistically unsubstantiated and marginally favours hyp.laser_aging as the primary remaining explanation.",
            "source": "traverse:config_record:scan_params:high_power_v2"
          },
          {
            "id": "ev.change_cause_log.power_mode",
            "summary": "log.power_mode: a recent config change to sub.power aligns with the degradation onset \u2192 the change is the cause",
            "source": "onset_vs_event_check"
          },
          {
            "id": "ev.common_mode",
            "summary": "3 degraded channel(s), onset spread 1.25d \u2192 common-mode (one upstream cause, not independent faults)",
            "source": "common_mode_check"
          }
        ],
        "links": [
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.laser_power_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.common_mode_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "+",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.onset_event_check_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.swap_rec_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 0.5
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "+",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.config_diff_001",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.tec_load_check_001",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 2.0
          },
          {
            "evidence_id": "ev.tec_load_check_001",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.calibration_drift",
            "polarity": "-",
            "weight": 1.0
          },
          {
            "evidence_id": "ev.traverse_config_001",
            "hypothesis_id": "hyp.window_contamination",
            "polarity": "-",
            "weight": 0.0
          },
          {
            "evidence_id": "ev.change_cause_log.power_mode",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode",
            "hypothesis_id": "hyp.upstream_power",
            "polarity": "+",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode",
            "hypothesis_id": "hyp.laser_aging",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode",
            "hypothesis_id": "hyp.detector_drift",
            "polarity": "-",
            "weight": 1.5
          },
          {
            "evidence_id": "ev.common_mode",
            "hypothesis_id": "hyp.thermal_tec",
            "polarity": "-",
            "weight": 1.5
          }
        ]
      }
    ],
    "trace": [
      {
        "action": "seed",
        "args": {},
        "rationale": "seed the differential from the symptom",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "hyp.window_contamination",
        "leader_conf": 0.5,
        "margin": 0.0,
        "confidences": {
          "hyp.window_contamination": 0.5,
          "hyp.laser_aging": 0.5,
          "hyp.detector_drift": 0.5,
          "hyp.thermal_tec": 0.5,
          "hyp.calibration_drift": 0.5,
          "hyp.upstream_power": 0.5
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "laser_power_check"
        },
        "rationale": "With all six hypotheses at equal prior and no evidence collected, the single most discriminating measurement is transmitted optical power at the emitter. An 8% range loss is physically consistent with a TX-power drop (range \u221d P^0.5 in SNR-limited systems, so ~8% range reduction \u2248 ~15% power drop). Result interpretation: (A) Power is nominal \u2192 strongly argues AGAINST hyp.laser_aging and hyp.upstream_power, and partially against hyp.thermal_tec; redirects suspicion to RX path (hyp.detector_drift), optical path (hyp.window_contamination), or processing (hyp.calibration_drift). (B) Power is reduced \u2192 strongly supports hyp.laser_aging and/or hyp.upstream_power, and raises hyp.thermal_tec as a contributing cause (elevated junction temp reduces wall-plug efficiency). This single check cleanly splits the six hypotheses into two camps \u2014 TX-side vs. RX/calibration-side \u2014 giving the maximum evidence gain per action at this stage.",
        "voi": 0.82,
        "evidence_id": "ev.laser_power_check_001",
        "conflicts_added": [],
        "leader": "hyp.laser_aging",
        "leader_conf": 0.881,
        "margin": 0.15,
        "confidences": {
          "hyp.window_contamination": 0.269,
          "hyp.laser_aging": 0.881,
          "hyp.detector_drift": 0.269,
          "hyp.thermal_tec": 0.119,
          "hyp.calibration_drift": 0.269,
          "hyp.upstream_power": 0.731
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "common_mode_check"
        },
        "rationale": "ev.laser_power_check_001 confirms laser output is \u221213% but cannot distinguish whether that loss is intrinsic to the emitter diode (hyp.laser_aging) or is a consequence of a shifted drive current / upstream power rail (hyp.upstream_power). A common_mode_check tests correlation across all channels sharing the same supply and driver bus: if the output drop is isolated to this single emitter while peer emitters remain nominal, it argues strongly FOR hyp.laser_aging and AGAINST hyp.upstream_power; if peer emitters or downstream subsystems on the same rail show a proportional decline, the shared upstream cause is implicated and hyp.upstream_power rises while hyp.laser_aging falls. This is the only available action that can move these two leading hypotheses in opposite directions from a single result. hyp.thermal_tec is already ruled out by ev.laser_power_check_001; hyp.detector_drift and hyp.calibration_drift remain secondary \u2014 the 13% TX loss already accounts for the observed 8% range degradation, so discriminating the TX-side root cause is the highest-value step before revisiting RX-side hypotheses.",
        "voi": 0.88,
        "evidence_id": "ev.common_mode_check_001",
        "conflicts_added": [],
        "leader": "hyp.laser_aging",
        "leader_conf": 0.953,
        "margin": 0.0,
        "confidences": {
          "hyp.window_contamination": 0.5,
          "hyp.laser_aging": 0.953,
          "hyp.detector_drift": 0.047,
          "hyp.thermal_tec": 0.076,
          "hyp.calibration_drift": 0.5,
          "hyp.upstream_power": 0.953
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "onset_vs_event_check"
        },
        "rationale": "Both hyp.laser_aging and hyp.upstream_power are co-leading at log_odds=3.00 and must be separated. ev.common_mode_check_001 revealed a tight 1.25-day co-onset across 3 channels. True laser aging (hyp.laser_aging) is a slow, continuous, per-emitter process \u2014 it does not produce a near-simultaneous step degradation across multiple channels within 1.25 days. A shared upstream discrete event (drive-current config push, firmware flash, power-supply swap) does. onset_vs_event_check will determine whether any logged event (reboot, config change, firmware update, hardware swap) temporally aligns with the degradation onset. A confirmed alignment strongly raises hyp.upstream_power and hyp.calibration_drift while materially lowering hyp.laser_aging; no alignment reverses those odds and forces an intrinsic emitter explanation for the rapid multi-channel co-onset \u2014 an unusual profile for natural aging that would itself need accounting for. hyp.window_contamination is also implicitly tested: contamination would be gradual and optically uniform, inconsistent with a sharp event-aligned onset.",
        "voi": 0.88,
        "evidence_id": "ev.onset_event_check_001",
        "conflicts_added": [],
        "leader": "hyp.laser_aging",
        "leader_conf": 0.953,
        "margin": 0.028,
        "confidences": {
          "hyp.window_contamination": 0.622,
          "hyp.laser_aging": 0.953,
          "hyp.detector_drift": 0.047,
          "hyp.thermal_tec": 0.076,
          "hyp.calibration_drift": 0.182,
          "hyp.upstream_power": 0.924
        }
      },
      {
        "action": "recommend_swap_test",
        "args": {
          "component": "laser_emitter_module"
        },
        "rationale": "ev.laser_power_check_001 confirms \u221213% optical output with junction temperature at 25.2 \u00b0C (within the 26 \u00b0C TEC setpoint), ruling out a thermally driven cause and isolating the loss to either intrinsic emitter degradation (hyp.laser_aging) or a reduced upstream drive current feeding the emitter (hyp.upstream_power). ev.common_mode_check_001 shows 3 channels co-degrading within a 1.25-day window, consistent with a shared upstream component \u2014 which could be the laser assembly itself or its drive/power supply. These two hypotheses currently sit only 0.5 log-odds apart and no available telemetry check measures drive current directly to separate them. Substituting a known-good laser emitter module is the single most discriminating action available: (a) if optical output and effective range recover to baseline with the replacement emitter, the fault is intrinsic to the diode \u2014 hyp.laser_aging confirmed, hyp.upstream_power substantially lowered; (b) if degradation persists with a fresh emitter under the same drive circuitry, the upstream drive or power rail is the root cause \u2014 hyp.upstream_power confirmed, hyp.laser_aging substantially lowered. Either outcome cleanly separates the two leading hypotheses in a single intervention.",
        "voi": 0.3,
        "evidence_id": "ev.swap_rec_001",
        "conflicts_added": [],
        "leader": "hyp.laser_aging",
        "leader_conf": 0.953,
        "margin": 0.072,
        "confidences": {
          "hyp.window_contamination": 0.5,
          "hyp.laser_aging": 0.953,
          "hyp.detector_drift": 0.047,
          "hyp.thermal_tec": 0.047,
          "hyp.calibration_drift": 0.119,
          "hyp.upstream_power": 0.881
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "config_diff"
        },
        "rationale": "ev.laser_power_check_001 confirms emitter output is \u221213% below baseline and thermal causes are ruled out (TEC nominal). The remaining fork is whether the drive circuit/upstream supply has reduced delivered current to the laser (hyp.upstream_power, log_odds=2.00) or whether the emitter itself has intrinsically degraded at unchanged drive current (hyp.laser_aging, log_odds=3.00). config_diff directly exposes any drift or change in laser drive-current setpoints, bias registers, or supply-voltage parameters. Result is strongly bifurcating: (a) if drive-current or supply parameters have shifted from baseline, this raises upstream_power and materially lowers laser_aging as the sole explanation; (b) if configuration is fully nominal and unchanged, this eliminates the upstream-drive path and consolidates the evidence for intrinsic laser aging, justifying the pending emitter swap. No prior check has yet interrogated drive-current configuration, so this is non-redundant with existing evidence. hyp.window_contamination (log_odds=0.00) is not yet ruled out but is lower priority than resolving the gap between the two leading hypotheses; its spatial signature can be tested by spatial_intensity_check in a subsequent step.",
        "voi": 0.82,
        "evidence_id": "ev.config_diff_001",
        "conflicts_added": [],
        "leader": "hyp.laser_aging",
        "leader_conf": 0.953,
        "margin": 0.0,
        "confidences": {
          "hyp.window_contamination": 0.5,
          "hyp.laser_aging": 0.953,
          "hyp.detector_drift": 0.047,
          "hyp.thermal_tec": 0.047,
          "hyp.calibration_drift": 0.269,
          "hyp.upstream_power": 0.953
        }
      },
      {
        "action": "run_check",
        "args": {
          "name": "tec_load_check"
        },
        "rationale": "The two co-leading hypotheses \u2014 hyp.laser_aging (log_odds=3.00) and hyp.upstream_power (log_odds=3.00) \u2014 are not yet discriminated from each other. ev.config_diff_001 revealed a scan_params change to 'high_power_v2' with no timestamp, which could mean the laser driver is supplying a different (potentially higher) drive current \u2014 an upstream mechanism. ev.laser_power_check_001 confirmed the TEC is successfully holding junction temperature at 25.2 \u00b0C against the 26 \u00b0C setpoint, but did NOT measure TEC duty cycle or thermal load. If tec_load_check returns an elevated TEC load, it implies the laser is generating more waste heat than at baseline, consistent with a higher drive-current set by 'high_power_v2' depressing wall-plug efficiency \u2014 this would raise hyp.upstream_power and weaken the purely-intrinsic-aging reading of hyp.laser_aging. If TEC load is nominal (no increase in heat to reject), the drive conditions are effectively unchanged and the \u221213% optical power deficit (ev.laser_power_check_001) is intrinsic to the emitter, raising hyp.laser_aging and weakening hyp.upstream_power. This check has not been run; ev.laser_power_check_001 and ev.common_mode_check_001 are already in evidence and do not answer this question. The action raises one leading hypothesis while lowering the other depending on outcome, satisfying the discrimination criterion.",
        "voi": 0.72,
        "evidence_id": "ev.tec_load_check_001",
        "conflicts_added": [],
        "leader": "hyp.laser_aging",
        "leader_conf": 0.953,
        "margin": 0.0,
        "confidences": {
          "hyp.window_contamination": 0.5,
          "hyp.laser_aging": 0.953,
          "hyp.detector_drift": 0.047,
          "hyp.thermal_tec": 0.047,
          "hyp.calibration_drift": 0.269,
          "hyp.upstream_power": 0.953
        }
      },
      {
        "action": "traverse",
        "args": {
          "target": "config_record",
          "ref": "scan_params:high_power_v2",
          "fields": [
            "timestamp_applied",
            "drive_current_setpoint_mA",
            "param_delta_vs_raster_default",
            "applied_by"
          ]
        },
        "rationale": "The two co-leading hypotheses \u2014 hyp.laser_aging (log_odds=3.00) and hyp.upstream_power (log_odds=3.00) \u2014 both fit ev.laser_power_check_001's \u221213% output deficit but predict different mechanisms. hyp.laser_aging requires that laser drive current is at its nominal setpoint yet emitter output has intrinsically declined; hyp.upstream_power requires that the 'high_power_v2' config change (ev.config_diff_001) altered drive-current or scan-drive parameters, making the output drop an externally imposed reduction rather than emitter degradation. ev.config_diff_001 is the critical fork: it found a scan_params mutation outside the formal event log with NO timestamp, so onset alignment is unconfirmed and causal attribution is suspended. Traversing the config record directly resolves both discriminating sub-questions: (1) the timestamp determines whether the change aligns with the ~1-week onset \u2014 if aligned, hyp.upstream_power rises and hyp.laser_aging falls as the primary intrinsic mechanism; if misaligned, the reverse; (2) the param delta reveals whether drive-current setpoint changed \u2014 a reduced setpoint fully explains the deficit without invoking aging, while an unchanged setpoint leaves intrinsic emitter degradation as the only remaining explanation. No currently retrieved evidence (ev.laser_power_check_001, ev.tec_load_check_001, ev.common_mode_check_001) directly measures drive-current setpoint or dates the config change, so this action opens new evidential territory rather than re-confirming already-supported findings.",
        "voi": 0.88,
        "evidence_id": "ev.traverse_config_001",
        "conflicts_added": [],
        "leader": "hyp.laser_aging",
        "leader_conf": 0.953,
        "margin": 0.0,
        "confidences": {
          "hyp.window_contamination": 0.5,
          "hyp.laser_aging": 0.953,
          "hyp.detector_drift": 0.047,
          "hyp.thermal_tec": 0.047,
          "hyp.calibration_drift": 0.119,
          "hyp.upstream_power": 0.953
        }
      },
      {
        "action": "conflict_sweep",
        "args": {},
        "rationale": "order onset vs the salient recent event; sanity-check channels",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "hyp.upstream_power",
        "leader_conf": 0.953,
        "margin": 0.453,
        "confidences": {
          "hyp.window_contamination": 0.5,
          "hyp.laser_aging": 0.076,
          "hyp.detector_drift": 0.047,
          "hyp.thermal_tec": 0.047,
          "hyp.calibration_drift": 0.119,
          "hyp.upstream_power": 0.953
        }
      },
      {
        "action": "synthesize",
        "args": {
          "answer_type": "cause",
          "root_cause": "sub.power"
        },
        "rationale": "conclude or abstain from the differential",
        "voi": 0.0,
        "evidence_id": null,
        "conflicts_added": [],
        "leader": "hyp.upstream_power",
        "leader_conf": 0.953,
        "margin": 0.453,
        "confidences": {
          "hyp.window_contamination": 0.5,
          "hyp.laser_aging": 0.076,
          "hyp.detector_drift": 0.047,
          "hyp.thermal_tec": 0.047,
          "hyp.calibration_drift": 0.119,
          "hyp.upstream_power": 0.953
        }
      }
    ],
    "case_id": "case8",
    "title": "Common-mode power",
    "caption": "one cause looks like two faults; redundant channels agree but are wrong",
    "answer": {
      "answer_type": "cause",
      "root_cause": "sub.power",
      "cited_evidence": [
        "ev.change_cause_log.power_mode",
        "ev.common_mode",
        "ev.common_mode_check_001",
        "ev.config_diff_001",
        "ev.laser_power_check_001",
        "ev.tec_load_check_001",
        "ev.traverse_config_001"
      ],
      "conflicts": []
    },
    "eval_row": {
      "accuracy": 1.0,
      "localization": 1.0,
      "trigger_discrimination": 1.0,
      "conflict_handling": 1.0,
      "evidence_f1": 0.22,
      "tokens": 295256
    },
    "graph": {
      "root": "kpi.effective_range",
      "nodes": [
        {
          "id": "kpi.effective_range",
          "type": "KPI",
          "name": "effective_max_range_m",
          "depth": 0
        },
        {
          "id": "metric.intensity",
          "type": "metric",
          "name": "mean_return_intensity",
          "depth": 1
        },
        {
          "id": "sub.calibration",
          "type": "subsystem",
          "name": "Signal proc / calibration",
          "depth": 1
        },
        {
          "id": "sub.laser",
          "type": "subsystem",
          "name": "Laser emitter",
          "depth": 2
        },
        {
          "id": "sub.optics",
          "type": "subsystem",
          "name": "Optics / window",
          "depth": 2
        },
        {
          "id": "sub.detector",
          "type": "subsystem",
          "name": "Receiver / detector",
          "depth": 2
        },
        {
          "id": "sub.thermal",
          "type": "subsystem",
          "name": "Thermal / TEC",
          "depth": 3
        },
        {
          "id": "sub.power",
          "type": "subsystem",
          "name": "Scanner / power",
          "depth": 4
        },
        {
          "id": "part.laser_module",
          "type": "part_type",
          "name": "Laser module",
          "depth": 3
        },
        {
          "id": "part.window",
          "type": "part_type",
          "name": "Window",
          "depth": 3
        },
        {
          "id": "part.detector",
          "type": "part_type",
          "name": "Detector",
          "depth": 3
        },
        {
          "id": "part.tec",
          "type": "part_type",
          "name": "TEC module",
          "depth": 4
        }
      ],
      "edges": [
        {
          "src": "metric.intensity",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.calibration",
          "dst": "kpi.effective_range",
          "type": "affects"
        },
        {
          "src": "sub.laser",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.optics",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.detector",
          "dst": "metric.intensity",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.laser",
          "type": "affects"
        },
        {
          "src": "sub.thermal",
          "dst": "sub.detector",
          "type": "affects"
        },
        {
          "src": "sub.power",
          "dst": "sub.thermal",
          "type": "affects"
        },
        {
          "src": "part.laser_module",
          "dst": "sub.laser",
          "type": "part_of"
        },
        {
          "src": "part.window",
          "dst": "sub.optics",
          "type": "part_of"
        },
        {
          "src": "part.detector",
          "dst": "sub.detector",
          "type": "part_of"
        },
        {
          "src": "part.tec",
          "dst": "sub.thermal",
          "type": "part_of"
        }
      ]
    },
    "explainer": {
      "purpose": "one cause looks like two faults; redundant channels agree but are wrong",
      "answer_type": "cause",
      "mechanisms": [
        {
          "id": "A4",
          "desc": "A4"
        },
        {
          "id": "A5",
          "desc": "A5"
        }
      ],
      "decoys": [
        "part.laser_module",
        "part.detector"
      ],
      "trigger": null
    }
  }
};
window.FATHOM_MANIFEST = [
  {
    "case_id": "case1",
    "title": "TEC degradation",
    "caption": "worked example: cross-subsystem + decoy + lying channel + demoted trigger",
    "final_status": "concluded"
  },
  {
    "case_id": "case2",
    "title": "Laser aging",
    "caption": "decoy as a true cause (no temp correlation) \u2014 symmetry vs case1",
    "final_status": "concluded"
  },
  {
    "case_id": "case3",
    "title": "Window contamination",
    "caption": "spatial-cluster signature; reasoning from absence",
    "final_status": "concluded"
  },
  {
    "case_id": "case4",
    "title": "Calibration drift",
    "caption": "post-release config; recent change IS the cause (anti-shortcut balance)",
    "final_status": "concluded"
  },
  {
    "case_id": "case5",
    "title": "No clean cause (abstain)",
    "caption": "intermittent/coincidence -> correct answer is abstain",
    "final_status": "abstained"
  },
  {
    "case_id": "case6",
    "title": "Detector bias (buried)",
    "caption": "absent-cue; buried evidence reachable via graph traversal + intra-doc",
    "final_status": "concluded"
  },
  {
    "case_id": "case7",
    "title": "TEC tie-breaker",
    "caption": "near-symmetric to a decoy; needs the expensive discriminating check",
    "final_status": "concluded"
  },
  {
    "case_id": "case8",
    "title": "Common-mode power",
    "caption": "one cause looks like two faults; redundant channels agree but are wrong",
    "final_status": "concluded"
  }
];
