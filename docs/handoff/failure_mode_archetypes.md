# Failure-Mode Archetype Catalog
### For an AI-native, multi-source system-test / diagnostic harness on a complex precision tool

**Purpose.** A working catalog of failure-mode *archetypes* for a coupled multi-subsystem machine (optical column / autofocus, XY stage, thermal/chiller, vacuum, wafer handling, control software, power), biased toward the two under-served classes you care about: **emergent / cross-subsystem** failures and **process / organizational / verification-gap** failures. Each archetype is chosen because it tends to **defeat a single data source** — which is exactly what makes it a good test of a fuse-across-sources diagnostic agent and a good case for your leave-one-source-out ablation.

**The four data sources** (abbreviated in the table): **T** = Telemetry (continuous numeric time series), **I** = Issue tickets (short structured incident/defect records), **R** = RCA decks (long-form narrative post-mortems / meeting write-ups), **D** = Engineering docs (FMEA, specs, interface-control docs — the *model* of the system).

**How to read a record.** *Mechanism* (causal chain) · *Subsystems & couplings* (or the process/org dimension) · *Symptoms & where they surface* · *Why it's hard / what's deceptive* (incl. which single source fails) · *Sources to crack it* (your ablation signal) · *Real-world grounding* (cited) · *Build-around vs Hold-out* · *Sim note* (lumped-parameter mechanism needed for it to emerge).

**Build-around vs Hold-out.** *Build-around* = a mechanism you deliberately model and validate the simulator/harness against (the condition is imposed; you confirm the harness catches it). *Hold-out* = a failure you do **not** script, held back to test whether it *emerges unprompted* from the coupled mechanism model. As a rule of thumb in this catalog: most **process/org/verification-gap** archetypes are build-around (they are *conditions you impose*), and most **emergent/cross-subsystem** archetypes are hold-out (they should *fall out of interactions* you modeled for other reasons). Reliability-physics archetypes split: a degradation *state* you model is build-around; a stochastic, condition-coincident intermittent is hold-out.

**A note on grounding.** Real-world anchors are cited inline. Where the public anchor is an *analog from another domain* rather than a like-for-like metrology case (e.g., a footbridge resonance standing in for a stage-resonance), or where I'm relying on a *general literature finding* rather than a single incident, I say so explicitly in the record and again in the "Grounding caveats" section at the end.

---

## Summary table (29 archetypes)

Ordered within each group by how diagnostically interesting / source-hungry they are. "Sources to crack" lists the combination that works; "Single source that fails" is one illustrative ablation casualty (most of these fail under *several* single-source views).

| # | Archetype | Class | B/H | Sources to crack | A single source that fails | Real-world anchor |
|---|-----------|-------|-----|------------------|----------------------------|-------------------|
| A1 | Verification/calibration proves the wrong thing | Verification-gap | Build | D + R + T | T alone (looks in-spec) | Hubble null corrector |
| A2 | Interface-control mismatch (units/scale/convention) | Verification-gap | Build | D + T | T alone (values look valid) | Mars Climate Orbiter |
| A3 | Config not rolled back to green baseline | Process/state | Build | D + I + T | T alone (no anomaly to point at) | Prototype-config drift (analog) |
| A4 | Legacy reuse carried into a new operating envelope | Process/verification | Build | D + R + T | T alone (fine until the corner) | Ariane 5 Flight 501 |
| A5 | Environment / use-condition assumption violated | Process/design | Build | D + R + T | T alone (env not instrumented) | Ariane 5; 737 MAX pilot-time |
| A6 | Maintenance-induced regression / not-restored | Process/maintenance | Build | I + R + T + D | T alone (state, not event) | TMI block valves; 2003 blackout |
| A7 | Spec too generous — in-spec parts still fail | Spec/process | Build | D + I + T | I alone (each ticket looks unique) | Samsung Note 7 |
| A8 | Measurement system masquerades as the process | Metrology | Build | D + T + I | T alone (the gauge *is* the noise) | Gauge R&R / MSA |
| A9 | Degrading sensor reports plausible-but-wrong values | Deceptive signal | Build | T + D + R | T alone (the lie lives in T) | Mars Polar Lander |
| A10 | Indicator shows *command*, not actual state | Deceptive signal | Build | T + D | T alone (signal == "healthy") | Three Mile Island PORV |
| A11 | Single non-redundant sensor + automation amplifies it | Design/deceptive | Build | T + D + R | T alone (no cross-channel) | 737 MAX MCAS |
| A12 | Thermal drift -> optical/dimensional error with lag | Thermo-coupling | Build | T + D | T alone (cause/effect delayed) | Machine-tool thermal error |
| A13 | Virtual leak (outgassing) mimics a real vacuum leak | Look-alike | Build | T + D + R | T alone (curves identical) | Vacuum rate-of-rise diagnosis |
| A14 | Thermomechanical fatigue wear-out (joint cracking) | Reliability-physics | Build | T + I + R | T alone (intermittent, delayed) | Xbox 360 "RRoD" |
| A15 | Infant-mortality vs wear-out (bathtub) | Reliability-physics | Build | I + T + D | T alone (slow margin burn) | Reliability theory (general) |
| A16 | Electromigration / current-density wear-out | Reliability-physics | Build | T + D + R | T alone (drift looks like noise) | IC reliability (Black's eq.) |
| A17 | Precursor / near-miss never propagated | Org/process | Build | I + R + D | T alone (history isn't in T) | Davis-Besse -> TMI |
| B1 | Cascade with no single anomalous component | Emergent | Hold | T + D + R | T alone (everything "in range") | 2003 NE blackout; LHC 2008 |
| B2 | Metastable collapse — sustaining loop holds it down | Emergent | Hold | T + R + D | T alone (trigger already gone) | Distributed-systems metastable |
| B3 | Coupled control-loop instability (stable alone) | Emergent | Hold | T + D | T alone (which loop? need ICD) | Loop-interaction theory |
| B4 | Velocity x payload resonance only in an envelope corner | Emergent | Hold | T + D + R | T alone (threshold/bifurcation) | Millennium Bridge |
| B5 | Resource contention / priority inversion | Emergent | Hold | T + D + R | T alone (symptom far from cause) | Mars Pathfinder |
| B6 | Common-cause failure defeats redundancy | Emergent | Hold | D + R + T | T alone (redundancy "should" hold) | Eastern 855; Ariane common-mode |
| B7 | Gray failure / differential observability | Emergent | Hold | T + I + R | T(monitor) alone (says healthy) | Cloud "gray failure" |
| B8 | Environmental coupling / upconversion into the band | Emergent | Hold | T + D | T(main) alone (need aux channels) | LIGO seismic->strain |
| B9 | Sensor cross-sensitivity -> phantom correlation | Emergent | Hold | T + D | T alone (correlation misleads) | Instrumentation (general) |
| B10 | Self-erasing intermittent short (whisker-type) | Reliability-physics | Hold | I + R + T | T alone (evidence fuses open) | NASA tin whiskers; Cassini |
| B11 | No-Fault-Found — fails in field, passes on bench | Reliability-physics | Hold | I + R + T | T(bench) alone (won't reproduce) | Avionics NFF/CND literature |
| B12 | Path-/soak-dependent intermittent (accumulated state) | Emergent | Hold | T + R + I | T(snapshot) alone (needs history) | NFF + soak/aging (analog) |

---

# Part A — Build-around archetypes
*Mechanisms you deliberately model and validate the harness against. Heavily weighted toward process/org/verification-gap and deceptive-signal cases — failures that are **conditions you impose** rather than dynamics you hope to see emerge.*

---

### A1. Verification / calibration proves the wrong thing ("test-as-proxy")
**Tagline:** the acceptance test passes, but it measures a proxy, not the function — so a defective unit ships "verified."

- **Mechanism:** The verification instrument or procedure is itself wrong, or measures something correlated-but-not-identical to the property that matters. The product is then built/accepted *to the flawed test*, and contradictory evidence from a cruder, "less trusted" check is dismissed.
- **Subsystems / process dimension:** Verification & calibration process; the relationship between the *metrology of the test* and the *function under test*.
- **Symptoms & where they surface:** Everything reads nominal in manufacturing/qualification **(T, D say "pass")**; the failure only appears in long field use or end-to-end operation, often described narratively in a post-mortem **(R)**. The smoking gun is a *disagreement between two test methods* that was rationalized away.
- **Why it's hard / what's deceptive:** Telemetry and acceptance data actively *reassure* — the unit is "in spec" against the very test that is broken. No single in-line stream can catch it; you need the design intent (what the test was *supposed* to prove) plus the field-failure narrative.
- **Sources to crack it:** **D** (spec / verification requirement — what function the test should prove) **+ R** (field RCA showing the proxy gap) **+ T** (field telemetry showing the real defect). *Telemetry alone is the classic ablation casualty: it says "pass."*
- **Real-world grounding:** Hubble's primary mirror was ground to match a **reflective null corrector that was itself mis-spaced by 1.3 mm**; two cruder correctors flagged the aberration and were dismissed as "the crude device is wrong," and an independent end-to-end test was skipped on cost grounds ([NASA](https://science.nasa.gov/mission/hubble/observatory/design/optics/hubbles-mirror-flaw/); [IOP](https://spark.iop.org/hubbles-troublesome-mirror)). Same family: Eastern 855's post-maintenance 10-second engine run "passed" because a leak needed >=30 s to show ([NTSB](http://www.rvs.uni-bielefeld.de/publications/Incidents/DOCS/ComAndRep/Eastern/Ntsb8404.html)); Ariane 5 skipped hardware-in-the-loop simulation of the new trajectory ([inquiry report](https://ocw.mit.edu/courses/16-355j-software-engineering-concepts-fall-2005/91f1e550b30b00ad797293f430220f18_ari5fail_ful_rep.pdf)).
- **Build-around / Hold-out:** **Build-around.** It's a condition you impose (a calibration that verifies a proxy), and a flagship demonstration of why design-intent docs are non-redundant.
- **Sim note:** Model the *verification step* as a function of a proxy variable `p` that is only partially correlated (`r<1`) with the true functional variable `f`; pass/fail keys on `p`. Let field stress excite the residual `f-p`. The harness must reconcile "passed on `p`" (T/D) with "failed on `f`" (field T + R).

---

### A2. Interface-control mismatch (units / scaling / convention across a boundary)
**Tagline:** two subsystems each behave correctly; the *contract between them* is wrong, so valid-looking numbers mean different things on either side.

- **Mechanism:** A quantity crosses a subsystem boundary with a mismatched unit, scale factor, sign, frame, or endianness. Each side is internally consistent; the error is in the *interface*, not a component. The deviation is often small per event and compounds.
- **Subsystems / couplings:** Any A->B data/command interface (motion-controller -> metrology, host software -> stage, sensor -> control loop). The governing artifact is the interface-control document (ICD).
- **Symptoms & where they surface:** Slow drift of a derived quantity (position, dose, trajectory, overlay) in **T**; no component alarms; the mismatch is only legible against the **D** that defines the convention.
- **Why it's hard / what's deceptive:** The numbers are *plausible* — they're real readings in the wrong units/frame. Telemetry alone shows drift but not *why*; the ICD alone shows the spec but not the violation; you need both, joined.
- **Sources to crack it:** **D** (the ICD / spec stating the agreed unit/convention) **+ T** (the drifting derived quantity). *Telemetry alone is insufficient: the values look valid.*
- **Real-world grounding:** Mars Climate Orbiter — ground software emitted impulse in **pound-force-seconds while the navigation software expected newton-seconds** (factor 4.45); tiny per-burn errors compounded over months, undetectable until orbit insertion ([PEimpact](https://peimpact.com/mars-climate-orbiter-failure-may-2026/); [Wikipedia](https://en.wikipedia.org/wiki/Mars_Surveyor_%2798)).
- **Build-around / Hold-out:** **Build-around.** You impose a deliberate ICD violation; it's the canonical case for why engineering docs carry non-redundant signal.
- **Sim note:** Give two subsystem models a shared interface variable with a scale/offset parameter; introduce a mismatch (`k!=1` or wrong frame). A small constant bias integrates into a slowly diverging derived state. The harness must pull the agreed value from D to localize.

---

### A3. Config not rolled back to the green baseline
**Tagline:** a setting changed to support prototype hardware that's since been removed — physical reality and configuration now disagree.

- **Mechanism:** A parameter/firmware/limit/recipe is changed for a temporary purpose (prototype part, bring-up, debug). The temporary cause is removed but the change persists. The system runs a config that describes a machine that no longer exists.
- **Subsystems / process dimension:** Configuration management vs physical state; the gap between "as-configured" and "as-built."
- **Symptoms & where they surface:** Often *no overt anomaly* — behavior is subtly off-nominal (a loop tuned for a different mass, a limit set for a different sensor). The discrepancy lives in the diff between current config and the **D** baseline, and the *reason* may be buried in a change ticket **(I)**.
- **Why it's hard / what's deceptive:** There is no failing component to point at; telemetry may be within limits because the limits themselves were moved. You need the baseline (D), the change history (I/R), and current behavior (T) together.
- **Sources to crack it:** **D** (green baseline / config-of-record) **+ I** (the change request that was never reverted) **+ T** (current behavior vs expected). *Telemetry alone fails: nothing trips.*
- **Real-world grounding:** Your own seed; closest hardware analogs are partial — e.g., TMI's auxiliary-feedwater block valves left closed after a test two days prior ([Online Ethics](https://onlineethics.org/cases/three-mile-island-nuclear-accident)). (Flagged: a clean public single-incident "prototype config left in place" is rare in the literature; the *pattern* is ubiquitous in field service. Treat grounding as analogical.)
- **Build-around / Hold-out:** **Build-around.** A deliberately injected state-vs-config mismatch; excellent for proving D + I non-redundancy.
- **Sim note:** Carry an explicit `config` object distinct from `physical_state`. Allow a scenario to set a prototype value, "remove" the prototype hardware (revert `physical_state`) but leave `config` stale. The harness must detect the mismatch from D + I, not from a threshold.

---

### A4. Legacy reuse carried into a new operating envelope
**Tagline:** proven hardware/software/recipe is reused for cost/commonality; an unstated assumption about its operating range no longer holds.

- **Mechanism:** A module with an excellent track record is reused in a new platform whose operating envelope differs. An assumption baked into the legacy design (a range, a rate, a duration) is silently violated in the new context, often only at a corner.
- **Subsystems / couplings:** Any reused subsystem (inertial/metrology reference, control law, handling sequence) x the new platform's dynamics. Also a *documentation* failure — the assumption wasn't in the ICD.
- **Symptoms & where they surface:** Long clean history, then a sharp failure when the new envelope is first reached **(T)**; the "why" requires the legacy design rationale **(D, R)**.
- **Why it's hard / what's deceptive:** The component's pedigree argues *against* suspecting it. A function may even be running that serves no purpose in the new system (dead legacy behavior). Telemetry alone can't reveal a violated *assumption*.
- **Sources to crack it:** **D** (legacy assumptions / ranges) **+ R** (reuse decision history) **+ T** (the corner-triggered event). *Telemetry alone fails: fine until the corner.*
- **Real-world grounding:** Ariane 5 Flight 501 — an alignment routine inherited from Ariane 4, **needless after liftoff and left running**, overflowed a 16-bit value because Ariane 5's horizontal velocity built ~5x faster; both (identically programmed) inertial units shut down ([inquiry report](https://ocw.mit.edu/courses/16-355j-software-engineering-concepts-fall-2005/91f1e550b30b00ad797293f430220f18_ari5fail_ful_rep.pdf); [Wikipedia](https://en.wikipedia.org/wiki/Ariane_flight_V88)).
- **Build-around / Hold-out:** **Build-around.** You impose a reuse-with-stale-assumption scenario.
- **Sim note:** Parameterize a subsystem with an `assumed_range`; reuse it on a platform whose state can exceed that range only in a corner. Add an overflow/saturation that triggers a "safe" shutdown (see A10/B6 for the deceptive-data and common-mode follow-ons).

---

### A5. Environment / use-condition assumption violated
**Tagline:** the design assumed something about vibration, heat, handling, cleanliness, or human/operating conditions that turned out false.

- **Mechanism:** A design margin rests on an environmental or use assumption (ambient temp band, vibration floor, duty cycle, contamination, replacement interval, operator reaction time). Field conditions violate it; in-spec hardware then fails or a control assumption breaks.
- **Subsystems / process dimension:** The boundary between the system and its environment/use; assumptions that live in specs/FMEA but aren't enforced by sensing.
- **Symptoms & where they surface:** Site- or use-correlated failures **(I clusters by site/shift/recipe)**; telemetry may not even instrument the violated variable; the assumption is in **D/R**.
- **Why it's hard / what's deceptive:** The violated variable is often *not measured* (no sensor for floor vibration, room humidity, or handling shock). The machine looks healthy on every channel it has.
- **Sources to crack it:** **D** (the stated assumption) **+ R** (field narrative correlating to an unmeasured condition) **+ T** (proxy signatures, if any). *Telemetry alone fails: the offending variable isn't in T.*
- **Real-world grounding:** Ariane 5's velocity-range assumption (above); 737 MAX's certification assumption that **pilots would counter an unexpected activation within ~3 seconds** ([Seattle Times](https://www.seattletimes.com/seattle-news/times-watchdog/the-inside-story-of-mcas-how-boeings-737-max-system-gained-power-and-lost-safeguards/)). Also LIGO-class environmental sensitivity (B8) and tin-whisker incubation accelerated by environment ([review](https://www.sciencedirect.com/science/article/pii/S1000936123002376)).
- **Build-around / Hold-out:** **Build-around.** You impose a use-condition the design didn't cover.
- **Sim note:** Add an *uninstrumented* environment input (e.g., floor vibration `v_env(t)`) that couples into a subsystem but has no dedicated sensor. Failures correlate with `v_env` only via D/R context, forcing the harness off pure telemetry.

---

### A6. Maintenance-induced regression / state-not-restored after service
**Tagline:** a service action introduces a defect or leaves the machine in a non-baseline state — and the post-service check doesn't catch it.

- **Mechanism:** Preventive/corrective maintenance perturbs the system: a part reinstalled wrong, a seal omitted, a valve/monitor left in the wrong position, a setting not restored. The verification after service is too short or too coarse to reveal it (links to A1).
- **Subsystems / process dimension:** Maintenance process x physical state; the *timing* signal (failure right after a service event) is key.
- **Symptoms & where they surface:** Failure clusters *immediately after a maintenance event* — visible only if you correlate **I** (work orders) with **T** (onset time) and the **D** procedure. Often a step-change in behavior, not drift.
- **Why it's hard / what's deceptive:** The failure looks like a random component fault unless you align it to the service timeline. Telemetry shows the symptom; only the maintenance record explains the coincidence.
- **Sources to crack it:** **I** (work orders / service log) **+ R** (how the procedure can go wrong) **+ T** (onset aligned to service) **+ D** (the procedure of record). This archetype is a strong **four-source** case. *Telemetry alone fails: it sees a state, not the event that caused it.*
- **Real-world grounding:** TMI's block valves left closed after a test, and the 2003 NE blackout's monitoring tool a technician corrected but **forgot to restart** ([HubPages summary](https://discover.hubpages.com/technology/The-Great-Northeast-Blackout-of-2003); [Online Ethics](https://onlineethics.org/cases/three-mile-island-nuclear-accident)); Eastern 855's three engines all losing oil because chip-detector **O-rings were omitted during the same overnight service** ([NTSB](http://www.rvs.uni-bielefeld.de/publications/Incidents/DOCS/ComAndRep/Eastern/Ntsb8404.html)).
- **Build-around / Hold-out:** **Build-around.** You inject a service event with a perturbation/omission.
- **Sim note:** Emit discrete `maintenance_event` records into the ticket stream; let a fraction perturb `physical_state` (offset, missing seal, unrestored valve). The harness must align T-onset to the I-event — a leave-out-tickets test should collapse accuracy here.

---

### A7. Spec too generous — in-spec parts still fail
**Tagline:** every part is within spec, yet the assembly fails, because the spec doesn't control the thing that actually matters.

- **Mechanism:** A tolerance band is set without controlling a latent characteristic (a corner radius, an internal clearance, a packaging margin under integration). Parts pass incoming inspection; the uncontrolled variable plus an integration stress produces failure. Two suppliers can fail by *different* mechanisms while presenting the *same* symptom.
- **Subsystems / process dimension:** Specification capability x supplier variability x integration margin.
- **Symptoms & where they surface:** Part-to-part inconsistent failures **(I)** that resist single-cause RCA; specs/FMEA **(D)** look satisfied; only aggregate telemetry + lot tracing **(T)** reveals the pattern.
- **Why it's hard / what's deceptive:** Each incident ticket looks like a one-off; the spec says everyone's compliant; a "fix" that swaps suppliers can introduce a *new* failure mode (see A6). The non-redundant signal is the *cross-incident pattern* plus the spec-gap.
- **Sources to crack it:** **D** (the spec, to show what it fails to control) **+ I** (the population of incidents) **+ T** (per-unit signatures / lot correlation). *Issue tickets alone fail: each looks unique; you need the spec gap and aggregate telemetry.*
- **Real-world grounding:** Samsung Note 7 — **two different battery suppliers, two different defect mechanisms** (a too-tight cell pouch deflecting electrodes vs welding burrs/insufficient insulation), the same fire symptom, aggressive packaging that removed margin, and a replacement that introduced a *new* defect ([CBC](https://www.cbc.ca/news/science/samsung-galaxy-note-7-battery-fire-cause-design-1.3947604); [HazardEx](https://www.hazardexonthenet.net/article/131394/Samsung-Galaxy-Note-7-fires-caused-by-battery-design-flaws-and-manufacturing-defects.aspx)).
- **Build-around / Hold-out:** **Build-around.** You set a spec that fails to bound a latent variable.
- **Sim note:** Draw a hidden part characteristic from a distribution *wider* than the spec controls; failure fires when hidden-var x integration-stress exceeds a threshold. Optionally give two "suppliers" different hidden distributions -> identical symptom, different mechanism (tests RCA-vs-ticket fusion).

---

### A8. Measurement system masquerades as the process ("the gauge lies")
**Tagline:** observed variation is dominated by the *measurement system*, not the part — so you chase a process problem that isn't there (or ship bad parts).

- **Mechanism:** Gauge repeatability + reproducibility (operator/condition/instrument) consume a large fraction of observed variation. Calibration (accuracy vs a standard) passes, but *precision* is poor, so good parts get rejected (false reject) and bad parts pass (false accept).
- **Subsystems / process dimension:** Metrology chain itself — directly relevant when the tool *is* a measurement instrument.
- **Symptoms & where they surface:** Suspicious capability numbers, scrap spikes, irreproducible measurements **(T, I)**; the resolution gap is only visible against the spec/tolerance and an MSA study **(D)**.
- **Why it's hard / what's deceptive:** This is "telemetry lies" at the *calibration* level — the data are precise-looking digits whose noise is the instrument's, not the world's. Calibration certificates reassure. A team will hunt for process causes that don't exist.
- **Sources to crack it:** **D** (tolerance + MSA/gauge-R&R definition) **+ T** (the variation decomposition) **+ I** (false-reject/accept reports). *Telemetry alone fails: the variation it reports is partly the gauge.*
- **Real-world grounding:** Gauge R&R / Measurement System Analysis: measurement variation can **masquerade as process variation**, producing false rejects and false accepts; calibration alone is not enough ([Lean Six Sigma](https://www.leansixsigmadefinition.com/glossary/gage-rr/); [MSA guide](https://www.theleansuite.com/blogs/measurement-system-analysis-gauge-reliability-manufacturing)).
- **Build-around / Hold-out:** **Build-around.** Model an explicit gauge-noise term.
- **Sim note:** Make every telemetry read `observed = true + eps_repeatability + eps_reproducibility(operator/condition)`. Tune eps so it dominates true part variation. The harness must distinguish gauge variance from process variance — a metrology-aware diagnosis.

---

### A9. Degrading sensor reports plausible-but-wrong values ("telemetry lies")
**Tagline:** a sensor drifts, biases, or saturates *within a believable range* — the control loop and the diagnostician both trust it.

- **Mechanism:** A sensor degrades (drift, offset, gain change, stuck-at, saturation) but still emits in-band values. Downstream control acts on the wrong number; a failed sensor may emit a diagnostic/garbage pattern that looks like data.
- **Subsystems / couplings:** Sensor -> control loop -> actuator; the sensor's health is itself unobserved.
- **Symptoms & where they surface:** The *primary* telemetry looks fine while the controlled physical quantity diverges; cross-checks (redundant or model-based) disagree. The "lie" is entirely inside **T**; the truth needs **D** (the sensor model / expected relationships) and often **R** (prior similar events).
- **Why it's hard / what's deceptive:** You cannot detect it by staring at the lying channel; you need an independent reference — physics/model from docs, or a second modality. This is the core of your thesis.
- **Sources to crack it:** **T** (the suspect + corroborating channels) **+ D** (model of expected relationships / sensor spec) **+ R** (precedent). *Telemetry alone fails when the lie is self-consistent on the lying channel.*
- **Real-world grounding:** Mars Polar Lander — a **spurious leg-deployment signal was read as touchdown ~40 m up**, cutting the descent engine ([Wikipedia](https://en.wikipedia.org/wiki/Mars_Surveyor_%2798)). Ariane 5's shutdown sent a **diagnostic bit pattern the flight computer treated as valid attitude data** ([inquiry report](https://ocw.mit.edu/courses/16-355j-software-engineering-concepts-fall-2005/91f1e550b30b00ad797293f430220f18_ari5fail_ful_rep.pdf)).
- **Build-around / Hold-out:** **Build-around.** Add explicit sensor fault modes.
- **Sim note:** Wrap each sensor in a transfer function with switchable faults: bias, drift, gain, stuck-at, saturation, and "garbage-as-data." Couple the loop to the *reading*, not the true state. The harness must use model-based or cross-channel residuals (D + multi-T) to catch it.

---

### A10. Indicator shows commanded state, not actual state
**Tagline:** the readout reflects "we told it to do X," not "X happened" — and the absence of an alarm is read as health.

- **Mechanism:** A status indicator is driven by the *command signal* (or by power to a coil), not by an independent position/state sensor. When command != reality (stuck actuator, mechanical hang), the indicator confidently shows the commanded state. A design that treats "no signal" as "fine" compounds it.
- **Subsystems / couplings:** Actuator command path vs true state feedback; HMI/telemetry semantics.
- **Symptoms & where they surface:** Operators/diagnostician believe a subsystem is in state X; physical consequences accumulate elsewhere **(T on other channels)**; the deceptive indicator is in **T** and only the **D** (what the channel actually represents) reveals the trap.
- **Why it's hard / what's deceptive:** The channel is *working correctly* — it just measures command, not state. Especially lethal under alarm flood (B7-adjacent), where it forms a wrong mental model that filters all later evidence (confirmation bias).
- **Sources to crack it:** **T** (the consequence channels that contradict the indicator) **+ D** (the channel definition: command vs state). *Telemetry alone fails if you trust the indicator's semantics.*
- **Real-world grounding:** Three Mile Island — the PORV light reflected the **close *command*, not the valve's position**; the valve was stuck open, the light went out, operators misread a loss-of-coolant for ~hours; a volume-based pressurizer-level reading reinforced the error ([World Nuclear](https://world-nuclear.org/information-library/safety-and-security/safety-of-plants/three-mile-island-accident); [HF Designworks](https://hfdesignworks.com/blogpress/human-factors-three-mile-island)).
- **Build-around / Hold-out:** **Build-around.** Model a command-driven indicator decoupled from true state.
- **Sim note:** For an actuator, expose `indicator = commanded_state` while `true_state` can diverge (stuck/hung). Let `true_state` drive the physics. The harness must catch the divergence from consequence channels + the D note that the indicator is command-sourced.

---

### A11. Single non-redundant sensor + automation amplifies its fault
**Tagline:** one sensor feeds an automatic loop with authority; when that sensor is wrong, automation drives the fault — and the disambiguating second source exists but isn't consulted.

- **Mechanism:** An automatic function takes authority from a single input. A fault on that input is not just trusted (A9) but *amplified* by repeated actuation. A second sensor that would expose the fault exists but is unused (or the system disables itself on disagreement rather than diagnosing).
- **Subsystems / couplings:** Sensor -> high-authority automation -> actuator; redundancy that is present in hardware but not in logic.
- **Symptoms & where they surface:** Aggressive, repeated actuator action with no proportionate disturbance **(T)**; a *latent disagreement* between redundant sensors visible in **T** but unused; design rationale and severity classification in **D**; the surprise-to-operator dynamic in **R**.
- **Why it's hard / what's deceptive:** Operators/diagnostician see the *automation's* effect and may chase the actuator or the plant, not the upstream sensor. The cross-channel disagreement that solves it is sitting in telemetry, unqueried.
- **Sources to crack it:** **T** (actuator action + the unused cross-channel disagreement) **+ D** (authority/redundancy design, hazard class) **+ R** (operator-surprise narrative). *Telemetry alone fails if the agent doesn't think to compare the redundant channel.*
- **Real-world grounding:** 737 MAX MCAS — triggered by a **single angle-of-attack vane**; the two vanes disagreed by ~20 degrees even on the ground; MCAS repeatedly trimmed nose-down; severity was under-classified and the change in authority wasn't re-submitted ([Seattle Times inside story](https://www.seattletimes.com/seattle-news/times-watchdog/the-inside-story-of-mcas-how-boeings-737-max-system-gained-power-and-lost-safeguards/); [engineering-ethics review](https://pmc.ncbi.nlm.nih.gov/articles/PMC7351545/)).
- **Build-around / Hold-out:** **Build-around** (the single-source authority is a design condition) — though the *amplification dynamic* doubles as a hold-out check.
- **Sim note:** Drive an automatic correction from one of two redundant sensors; fault that sensor; let the loop re-actuate on a schedule. Keep the second sensor logging (disagreement present but unused). Reward the harness for consulting the idle channel.

---

### A12. Thermal drift -> optical / dimensional error with transport lag
**Tagline:** a heat source hundreds of seconds ago shows up now as a focus or positioning error — cause and effect are separated in time and space.

- **Mechanism:** Internal heat (motors, bearings, friction, electronics) or ambient change diffuses through structure, producing time-delayed, position-dependent thermal expansion that shifts the optical focal plane or stage geometry. The deformation lags the heat input (first/second-order thermal time constants) and the temperature sensors are rarely co-located with the deformation.
- **Subsystems / couplings:** Thermal/chiller x optical column/autofocus x stage geometry; control loops chasing a slowly moving setpoint.
- **Symptoms & where they surface:** Slow, history-dependent drift in focus/overlay/position **(T)**, correlated with prior duty cycle rather than instantaneous temperature; the coupling map lives in **D** (thermal/structural ICD).
- **Why it's hard / what's deceptive:** The error *now* correlates poorly with temperature *now*; it correlates with the integral of past heat. Sensor placement means the hottest measured point isn't where the distortion is. A single snapshot misleads.
- **Sources to crack it:** **T** (thermal history + the drifting metric, with lag) **+ D** (which heat sources couple to which geometry, and the expected time constants). *Telemetry alone struggles without the coupling model and an awareness of lag.*
- **Real-world grounding:** In precision machine tools, **thermal effects cause ~40-75% of geometric/workpiece error**, with strongly position- and time-dependent heat sources and transient gradients ([review (40-70%)](https://www.academia.edu/35329955/Error_compensation_in_machine_tools_a_review_Part_I_geometric_cutting_force_induced_and_fixture_dependent_errors); [transient modeling](https://www.sciencedirect.com/science/article/abs/pii/S0890695523000111)). (General-literature grounding, not a single incident.)
- **Build-around / Hold-out:** **Build-around** — but the *lag/history-dependence* makes it a good test of whether the harness reasons about dynamics rather than instantaneous correlation.
- **Sim note:** First-order thermal lag: `dT_struct/dt = (heat_in - k*(T_struct - T_amb))/C`; map `T_struct` to a focus/position offset via an expansion coefficient. Place the temperature sensor at a *different* node than the deformation. Drift then trails duty cycle by the time constant.

---

### A13. Virtual leak (outgassing / trapped volume) mimics a real vacuum leak
**Tagline:** the pump-down/rate-of-rise curve looks like a leak, but there's no external leak — gas is coming from inside, and the fix is completely different.

- **Mechanism:** Trapped gas (blind/unvented screw holes, weld voids, porous material, water/oil ingress from cooling channels) or surface outgassing releases slowly, raising chamber pressure and degrading base vacuum — producing a pressure signature indistinguishable from a real external leak on a standard gauge.
- **Subsystems / couplings:** Vacuum x (thermal during bake) x handling/contamination; often *introduced by manufacturing or a repair*.
- **Symptoms & where they surface:** Slow pump-down, elevated base pressure, pressure "spikes" on heating **(T)**; helium leak-check finds nothing external; the distinguishing evidence is gas *composition* (a different modality — RGA) and the construction/maintenance context **(D/R)**.
- **Why it's hard / what's deceptive:** There is no reliable way to tell real from virtual with a typical gauge — the time-series look-alike sends teams on fruitless external leak hunts. The diagnostic key is a *different sensor modality* (RGA) plus design/maintenance context.
- **Sources to crack it:** **T** (pressure curve + RGA species, if available) **+ D** (chamber construction / vented-design intent) **+ R** (recent build/repair that could trap gas). *Telemetry from the pressure gauge alone fails: the curves are identical to a real leak.*
- **Real-world grounding:** A virtual leak "looks like a real leak in a pump-down or pressure-rise curve" but shows no external signal and can't be located from outside; diagnosis uses RGA gas-composition (argon-venting) and curve shape, and these leaks often arise from an original manufacturing procedure or a repair ([CERN leak-detection](https://cds.cern.ch/record/1047068/files/p227.pdf); [rate-of-rise diagnosis](https://www.normandale.edu/academics/degrees-certificates/vacuum-and-thin-film-technology/articles/rate-of-rise-curves-as-a-diagnostic-tool.html); [real vs virtual](https://www.heattreattoday.com/how-to-find-both-real-and-virtual-vacuum-leaks/)).
- **Build-around / Hold-out:** **Build-around** — model two pressure-rise mechanisms with the same gauge signature.
- **Sim note:** Model base pressure as `dP/dt = (Q_real_leak + Q_outgas(t,T) - S*P)/V`. Give `Q_real_leak` (constant, conductance-limited) and `Q_outgas` (decaying, T-spiking) the *same* P-signature but different RGA species. Add an "RGA channel" only sometimes present (tests whether the harness asks for the disambiguating modality / D-R context).

---

### A14. Thermomechanical fatigue wear-out (joint/solder cracking under cycling)
**Tagline:** repeated heat/load cycles slowly crack a joint; failures start months in, are intermittent first, and the indicator only says "something's broken."

- **Mechanism:** Coefficient-of-thermal-expansion mismatch under thermal/power cycling fatigues a solder joint or bonded interface; microfractures grow until intermittent then permanent loss of continuity. Pre-existing mechanical stress (board flex, heavy heatsink, uneven mounting) and brittle (Pb-free) solder accelerate it.
- **Subsystems / couplings:** Power/electronics x thermal cycling x mechanical mounting; a wear *state* that accumulates.
- **Symptoms & where they surface:** Failures rising **after months of service** **(I trend over time/cycles)**; intermittent resets/dropouts first **(T)**; generic "hardware fault" indicators that don't localize; root cause in teardown **(R)**.
- **Why it's hard / what's deceptive:** Early failures are intermittent and load/temperature-dependent (overlaps NFF, B11); the symptom is a vague fault, far from the cracked joint; only the *population trend vs cycles* plus teardown RCA tells the story.
- **Sources to crack it:** **T** (intermittent dropouts vs thermal/load cycles) **+ I** (rising failures with age/cycles) **+ R** (teardown showing fatigue cracks). *Telemetry alone fails: it's intermittent and the symptom is generic.*
- **Real-world grounding:** Xbox 360 "Red Ring of Death" — thermal cycling cracked **lead-free BGA solder under the GPU**, aggravated by motherboard flex from uneven standoffs/X-clamp and a heavy heatsink, with insufficient long-term-stress testing; most failures appeared after months ([XBLAFans teardown](https://xblafans.com/red-rings-e74s-diagnoses-xbox-pathologist-67043.html); [summary](https://www.quora.com/Why-did-the-Xbox-360-have-so-many-issues-like-the-red-ring-of-death)).
- **Build-around / Hold-out:** **Build-around** — model an explicit fatigue-damage accumulator.
- **Sim note:** Accumulate Coffin-Manson-style damage `D += f(dT_cycle)` per thermal cycle; when `D` crosses a threshold, joint resistance becomes intermittent (temperature/load-gated), then open. Onset lands after many cycles -> delayed, condition-dependent symptom.

---

### A15. Infant-mortality vs wear-out (the bathtub curve)
**Tagline:** the same symptom means opposite things at different ages — a dead-on-arrival defect vs end-of-life wear — and gradual margin burn hides both until late.

- **Mechanism:** Failure rate is high early (manufacturing/infant mortality), low in mid-life, rising at end-of-life (wear-out). A part may degrade *gradually* (consuming slack/clearance) so the function is fine until accumulated wear crosses a threshold.
- **Subsystems / process dimension:** Component reliability over the fleet lifetime; the interaction of age with otherwise-identical symptoms.
- **Symptoms & where they surface:** Bimodal failure-vs-age distribution in the population **(I + lifetime/serial data)**; gradual drift in a margin metric **(T)**; expected-life context in **D** (FMEA, MTBF).
- **Why it's hard / what's deceptive:** A single failure is ambiguous without age/serial context: infant-mortality and wear-out present alike but demand opposite responses (screening vs preventive replacement). Telemetry of one unit can't separate them.
- **Sources to crack it:** **I** (failures with age/serial/lot) **+ T** (margin-consumption trend) **+ D** (expected-life model). *Telemetry of a single unit fails: you need the population's age structure.*
- **Real-world grounding:** Standard reliability theory (bathtub curve; infant mortality and wear-out regions). (Textbook/general — not a single incident; pairs with the cited wear mechanisms in A14/A16.)
- **Build-around / Hold-out:** **Build-around** — model a hazard rate with explicit early/mid/late regions.
- **Sim note:** Sample component life from a mixture (Weibull beta<1 for infant mortality + beta>1 for wear-out); track a margin variable that erodes with use. Identical symptom code fires for both modes -> the harness must use age/serial (I/D) to disambiguate.

---

### A16. Electromigration / current-density wear-out
**Tagline:** sustained high current density slowly moves metal atoms, raising resistance and drifting parameters before an eventual open — looks like noise until it doesn't.

- **Mechanism:** High current density (hot spots, undersized traces/vias, derating violated under a corner load) drives mass transport in conductors, forming voids/hillocks; resistance creeps up, timing/parametrics drift, then an open or short occurs. Accelerated by temperature (Black's-equation dependence on current density and temperature).
- **Subsystems / couplings:** Power delivery / electronics x thermal; another *latent wear state* that consumes margin invisibly.
- **Symptoms & where they surface:** Slow parametric drift / rising resistance / marginal-timing errors **(T)**, accelerating with temperature and load; failures concentrate where derating was tight **(D)**; mechanism confirmed in failure analysis **(R)**.
- **Why it's hard / what's deceptive:** The drift hides in normal parametric variation and is easy to attribute to "noise" or environment; it depends on the *history* of current x temperature, not the present value.
- **Sources to crack it:** **T** (parametric drift vs load/temperature history) **+ D** (current-density / derating spec to flag the at-risk node) **+ R** (FA precedent). *Telemetry alone fails: the drift looks like benign variation.*
- **Real-world grounding:** Electromigration is a well-established IC wear-out mechanism (mean-time-to-failure via Black's equation, strongly current-density- and temperature-dependent). (Textbook/reliability-physics grounding rather than a single public incident — flagged.)
- **Build-around / Hold-out:** **Build-around** — model an accumulated EM-damage term.
- **Sim note:** `MTTF ~ J^-n * exp(Ea/kT)`; accumulate damage from `J(t),T(t)` history; map damage to a slow resistance rise that perturbs a downstream parametric, then opens. Tests whether the harness reasons over *history* and consults derating docs.

---

### A17. Precursor / near-miss never propagated
**Tagline:** the failure already announced itself — in an old ticket, a sister tool, or a vendor advisory — but the weak signal was never connected to the present case.

- **Mechanism:** A relevant prior event exists (an earlier intermittent on the same subsystem, a near-miss on a sister machine, a known-issue advisory). It was closed as benign, never analyzed, or never disseminated. The current failure repeats it.
- **Subsystems / process dimension:** Organizational memory / FRACAS; the value of history rather than the live machine.
- **Symptoms & where they surface:** The present telemetry **(T)** looks novel, but a matching pattern exists in **I** (old/duplicate tickets), **R** (a prior RCA reached a partial conclusion), or **D** (a vendor advisory / known-issue list). The signal is *temporal and textual*, not in the live numbers.
- **Why it's hard / what's deceptive:** Telemetry has no memory; the disambiguating evidence is entirely historical/narrative. Without ticket+RCA recall, the agent re-derives from scratch and may miss the known answer.
- **Sources to crack it:** **I** (prior/duplicate incidents) **+ R** (earlier partial RCA) **+ D** (advisories/known-issues). *Telemetry alone fails: the precursor isn't in the current time series.*
- **Real-world grounding:** Davis-Besse experienced the **same stuck-open PORV + level-confusion 18 months before TMI** (same Babcock & Wilcox design) without the lesson propagating ([precursor account](http://www.tmia.com/old-website/tmisab.html)); Eastern's chip-detector O-ring failure had **recurred before** and tin-whisker advisories (NASA NA-044) existed for decades ([NTSB](http://www.rvs.uni-bielefeld.de/publications/Incidents/DOCS/ComAndRep/Eastern/Ntsb8404.html); [NASA tin-whisker history](https://nepp.nasa.gov/whisker/failures/)).
- **Build-around / Hold-out:** **Build-around** — seed the corpus with a matching precursor.
- **Sim note:** Generate a *prior* ticket/RCA describing a near-miss of the current failure (closed "no action"). The current event's telemetry is novel-looking; the harness should retrieve the precursor. A leave-out-tickets or leave-out-RCA ablation should bite hard here.

---

# Part B — Hold-out archetypes
*Failures you do **not** script — held back to test whether they emerge unprompted from the coupled mechanism model. Heavily weighted toward emergent/cross-subsystem dynamics and stochastic, condition-coincident reliability failures.*

---

### B1. Cascade with no single anomalous component (+ observability collapse)
**Tagline:** a manageable local fault propagates system-wide because a protection/monitoring path silently failed — and afterward no single component reads "bad."

- **Mechanism:** A small initiating event (a marginal joint, an overloaded line, a contended resource) propagates through couplings because the safety/observability layer that should have caught it is itself degraded or blind. Each component is within or near limits; the failure lives in the *interactions* and the *gap in monitoring*.
- **Subsystems / couplings:** Many — power, control, protection, monitoring; tight coupling + interactive complexity (normal-accident territory; see Perrow, and Leveson's STAMP, which holds that accidents arise from unsafe *interactions*, not just component failure — [MIT STAMP](http://sunnyday.mit.edu/STAMP-publications.html)).
- **Symptoms & where they surface:** A spreading sequence of trips/derates across subsystems **(T, all "in range" individually)**; the *absence* of expected alarms is itself the clue; the coupling topology and protection logic are in **D**; the propagation story in **R**.
- **Why it's hard / what's deceptive:** No component telemetry screams; the diagnosis is about *sequence and coupling*, not magnitude. A silent monitoring failure removes the very evidence you'd reach for first.
- **Sources to crack it:** **T** (multi-channel sequence/timing) **+ D** (coupling/protection topology) **+ R** (precedent cascades). *Telemetry alone fails: every channel is individually plausible; you need the structure.*
- **Real-world grounding:** 2003 NE blackout — a tree-contacted line plus a **silently failed alarm/state-estimator (race condition)** left operators blind; a local fault cascaded to 55M people ([IEEE Spectrum](https://spectrum.ieee.org/the-blackout-of-2003); [Wikibooks](https://en.wikibooks.org/wiki/Professionalism/Northeast_Blackout_of_2003)). LHC 2008 — one bad busbar joint at high current arced and **cascaded into ~50 damaged magnets** via secondary effects ([CERN](https://home.web.cern.ch/news/press-release/cern/cern-releases-analysis-lhc-incident)).
- **Build-around / Hold-out:** **Hold-out.** It should *emerge* from coupling + a degraded protection path, not be scripted.
- **Sim note:** Model inter-subsystem coupling edges + a protection/alarm layer with its own failure mode. Inject a small disturbance and let load/heat redistribute over couplings while the alarm path is (independently) disabled. A good model produces system-wide collapse with no single out-of-range component.

---

### B2. Metastable collapse — a sustaining loop holds the system down after the trigger is gone
**Tagline:** a transient overload tips the system into a low-throughput state that *sustains itself* via a feedback loop, so it won't recover even after the original cause disappears.

- **Mechanism:** Under a vulnerable (margin-thin) operating point, a trigger causes temporary overload; a common-case optimization (retry, caching, re-routing, rework) then amplifies work, forming a positive feedback loop that keeps the system in a degraded equilibrium. The root cause is the *loop*, not the trigger.
- **Subsystems / couplings:** Wafer handling/scheduling x throughput x any retry/rework/queue mechanism; software + physical flow.
- **Symptoms & where they surface:** Sustained low goodput / throughput collapse with high activity **(T)**; the trigger may be long past and untraceable; the loop mechanism is understood only narratively **(R)** and via design **(D)**.
- **Why it's hard / what's deceptive:** Looking for "what broke" fails — nothing is broken, and the trigger is gone. Many different triggers yield the same collapse, so trigger-hunting misleads; you must find the *sustaining loop*.
- **Sources to crack it:** **T** (throughput/queue dynamics) **+ R** (recognizing the self-sustaining pattern) **+ D** (where the amplifying optimization lives). *Telemetry alone fails: the cause isn't present anymore; the dynamics are.*
- **Real-world grounding:** Metastable failures in distributed systems — a trigger tips a vulnerable system into a state held by a **work-amplifying sustaining loop (e.g., retry storms)** that persists after the trigger clears; generalizes congestion collapse, death spirals, cascading failures ([Bronson et al., HotOS '21](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf); [USENIX ;login:](https://www.usenix.org/publications/loginonline/metastable-failures-wild)).
- **Build-around / Hold-out:** **Hold-out.** Maps directly to your "wafer-mix-dependent throughput-collapse cascade" candidate; it should emerge from a queue + retry/rework loop.
- **Sim note:** Open system with an uncontrolled arrival process, a server with finite capacity, and a *retry/rework* path that adds load on failure. Tune to a vulnerable point; a brief arrival spike triggers collapse; goodput stays low after the spike ends because retries sustain the overload.

---

### B3. Coupled control-loop instability (each loop stable alone)
**Tagline:** two well-tuned loops sharing a plant interact destabilizingly in some region — the oscillation belongs to neither loop by itself.

- **Mechanism:** Two control loops (e.g., autofocus and stage-settling) are individually stable but share a plant or sensing path; loop interaction (cross-coupling, or one loop's actuator disturbing the other's sensor), saturation/integrator-windup, or a region-dependent gain change creates a limit cycle or growing oscillation only when both are active and a condition is met.
- **Subsystems / couplings:** Autofocus loop x XY-stage loop (or any two loops sharing structure/sensing); multivariable interaction.
- **Symptoms & where they surface:** Oscillation/limit cycle / settling failure in **T** that doesn't appear when either loop runs alone; the *shared coupling* is only legible from **D** (which loops share a plant/sensor).
- **Why it's hard / what's deceptive:** Each loop tests fine in isolation; bench/single-loop verification passes (links A1). The instability is a property of the *pair*, gated by a region or gain, so it's intermittent and configuration-dependent.
- **Sources to crack it:** **T** (the oscillation signature + which loops are co-active) **+ D** (interconnection/ICD showing the shared plant/sensor). *Telemetry alone struggles to attribute "which loop" without the coupling map.*
- **Real-world grounding:** Loop-interaction instability is standard multivariable-control phenomenology (relative-gain-array / interaction analysis); a vivid public *analog* of human-machine loop-coupling instability is pilot-induced oscillation / aircraft-pilot coupling. (Grounding is by analogy/theory, not a single metrology incident — flagged.)
- **Build-around / Hold-out:** **Hold-out.** Model two independently-stable PID loops sharing a plant; instability should emerge in a corner without being scripted.
- **Sim note:** Two PID loops on a coupled 2-input/2-output plant (cross terms `g12,g21`). Make a cross-gain or delay grow with a state (payload, position). Below threshold both are stable; above it the closed-loop poles cross into instability -> limit cycle only when co-active.

---

### B4. Velocity x payload structural resonance only in an envelope corner
**Tagline:** below a critical speed/load everything's fine; cross the threshold and a positive-feedback resonance erupts — and past good performance is no guarantee.

- **Mechanism:** A structural mode sits near an excitation frequency that the system only reaches in a corner of the operating envelope (high velocity x heavy payload, specific scan pattern). Above a critical condition, energy feeds the mode faster than damping removes it (effective negative damping), and amplitude grows — a bifurcation, not a gradual trend.
- **Subsystems / couplings:** XY motion x structural dynamics x payload/wafer mass; possibly closed-loop interaction (B3).
- **Symptoms & where they surface:** Sudden vibration/position-error blow-up confined to specific velocity/payload/recipe combinations **(T)**; benign at all tested lower conditions; mode/structural data in **D**; prior corner events in **R**.
- **Why it's hard / what's deceptive:** It's a *threshold* phenomenon — linear extrapolation from sub-critical data predicts safety. It appears only in a rarely-exercised corner, so coverage misses it (links A1/B11). Past good performance under sub-critical loading does not predict the corner.
- **Sources to crack it:** **T** (vibration vs the velocity/payload corner) **+ D** (structural modes / natural frequencies) **+ R** (any prior corner incident). *Telemetry alone (especially from sub-critical operation) fails to predict the threshold.*
- **Real-world grounding:** London Millennium Bridge — above a **critical crowd (~160-165 people)**, random pedestrians acted as *negative damping*, an abrupt bifurcation into large lateral sway; engineers noted that **satisfactory past performance under sub-critical loading is no guide to behavior at the critical value** ([Nature Communications](https://www.nature.com/articles/s41467-021-27568-y); [Ingenia/Arup](https://www.ingenia.org.uk/articles/stabilising-the-london-millennium-bridge/)). (Cross-domain analog for a stage/structure resonance.)
- **Build-around / Hold-out:** **Hold-out.** Resonance should emerge from a structural mode + envelope-dependent excitation, unscripted.
- **Sim note:** Lumped mass-spring-damper with a mode at `f_n`; excitation frequency = f(velocity, scan pattern); effective damping = f(payload) and can go negative past a threshold. Below critical: bounded. Above: exponential amplitude growth (bifurcation).

---

### B5. Resource contention / priority inversion
**Tagline:** a shared resource (bus, mutex, buffer, pump, power budget) gets held by a low-priority task while a high-priority one starves — the system trips far from the real cause, only under specific load.

- **Mechanism:** Tasks/subsystems share a finite resource without correct arbitration. Under a particular load mix, a low-priority holder blocks a high-priority consumer (priority inversion), or contention causes a deadline miss; a watchdog/supervisor then forces a reset or safe-state, masking the underlying contention.
- **Subsystems / couplings:** Control software scheduling x shared bus/resource x any subsystem competing for it (handling, comms, compute, power).
- **Symptoms & where they surface:** Intermittent resets / deadline misses / stalls under specific concurrent activity **(T)**; the symptom (reset) is *far from* the cause (arbitration config); the shared-resource design is in **D**; reproduction requires tracing **(R / instrumentation)**.
- **Why it's hard / what's deceptive:** The watchdog "knows something's wrong but can't say what." It's load-/timing-dependent, hard to reproduce, and the symptom points away from the cause. Reproduced often only with full event tracing on a replica.
- **Sources to crack it:** **T** (event/timing traces correlating resets with concurrent load) **+ D** (scheduling/resource-sharing design, priority config) **+ R** (prior reproduction). *Telemetry alone fails: the cause is a transient timing relationship, not a level.*
- **Real-world grounding:** Mars Pathfinder — a **priority inversion** (low-priority task holding a mutex, a medium-priority task preempting it, blocking a high-priority bus task) tripped a watchdog reset; it was **load-dependent**, had occurred in pre-flight testing but was dismissed as a glitch, and was found only by tracing on a replica ([Cornell write-up](https://www.cs.cornell.edu/courses/cs614/1999sp/papers/pathfinder.html); [priority inversion](https://en.wikipedia.org/wiki/Priority_inversion)).
- **Build-around / Hold-out:** **Hold-out.** Should emerge from shared-resource arbitration under a load mix, not be scripted as "now invert priorities."
- **Sim note:** Model tasks with priorities sharing a mutex/bus with a configurable inheritance flag; a watchdog resets on missed deadlines. Under a specific co-arrival pattern, inversion -> deadline miss -> reset. Symptom (reset) is decoupled from cause (the flag) -> forces D-aware diagnosis.

---

### B6. Common-cause failure defeats redundancy
**Tagline:** redundant channels fail together because they share a cause — the same design flaw, the same maintenance hand, or the same environment — so "1-out-of-2 will save us" doesn't.

- **Mechanism:** Redundancy assumes independent failures. A shared dependency — identical software (common-mode), a common maintenance action, a shared power/cooling/environmental input — fails all redundant paths at once or near-simultaneously.
- **Subsystems / couplings:** Any redundant subsystem (dual sensors, dual controllers, dual power) x a shared upstream cause.
- **Symptoms & where they surface:** Simultaneous or near-simultaneous loss of redundant channels **(T)**; the *shared dependency* is only visible in **D** (architecture / FMEA common-cause analysis) and **R** (how the shared cause acted); tickets **(I)** may show both channels serviced together.
- **Why it's hard / what's deceptive:** Diagnosis is biased by the belief that "both can't fail at once," so the common cause is the last thing suspected. Telemetry shows two failures; only the dependency map explains the coincidence.
- **Sources to crack it:** **D** (shared-dependency / common-cause map) **+ R** (mechanism of the shared cause) **+ T** (the simultaneity). *Telemetry alone fails: it shows two failures but not their shared root.*
- **Real-world grounding:** Eastern 855 — the same maintenance step left **all three engines without O-rings** (maintenance common-cause defeating triple redundancy), and the post-service check couldn't reveal it ([NTSB](http://www.rvs.uni-bielefeld.de/publications/Incidents/DOCS/ComAndRep/Eastern/Ntsb8404.html)). Ariane 5 — **both inertial units ran identical software**, so the overflow took out both (common-mode) ([analysis](https://inria.hal.science/inria-00073613/document)).
- **Build-around / Hold-out:** **Hold-out.** Should emerge once you model a shared dependency among "independent" channels.
- **Sim note:** Give redundant channels a shared input (common power node, common software parameter, or a common `maintenance_event` that touches both). A single shared-cause perturbation drops all channels together -> the harness must trace to the shared node via D.

---

### B7. Gray failure / differential observability
**Tagline:** the health monitor says "healthy" while the function is actually degraded — different observers disagree, and the monitor is the one that's wrong.

- **Mechanism:** A subsystem enters a degraded mode that the *health detector* doesn't register (its probes don't capture what the function actually needs), even though downstream consumers feel the degradation. The pattern evolves: latent fault -> degraded-but-"healthy" -> eventual hard failure the monitor finally sees.
- **Subsystems / couplings:** Any subsystem with a health-monitor whose metrics != the consumer's experience (e.g., a chiller "in range" by its own sensor but not delivering effective cooling to the optic).
- **Symptoms & where they surface:** Downstream metrics degrade **(T on consumer channels)** while the health/status channel reports OK **(T on monitor channel)** — a *disagreement between channels*; consumer complaints in **I**; the observation-gap explained in **R**.
- **Why it's hard / what's deceptive:** The authoritative health signal actively says "fine." Trusting the monitor (the natural move) blinds you. The fix is to compare *different observers'* views — exactly the multi-source move.
- **Sources to crack it:** **T** (monitor channel vs consumer channels) **+ I** (downstream incident reports) **+ R** (recognizing differential observability). *The monitor's telemetry alone fails — that's the definition.*
- **Real-world grounding:** "Gray failure" in cloud-scale systems — a partial failure with **differential observability**: the system's failure detector sees health while afflicted apps don't; classic cycle latent -> degraded -> down ([Microsoft Research](https://www.microsoft.com/en-us/research/publication/gray-failure-achilles-heel-cloud-scale-systems/); [acolyer summary](https://blog.acolyer.org/2017/06/15/gray-failure-the-achilles-heel-of-cloud-scale-systems/)).
- **Build-around / Hold-out:** **Hold-out.** Emerges whenever a monitor's metric set is narrower than the function — don't script the disagreement, let the gap produce it.
- **Sim note:** Define a subsystem's *true effectiveness* separately from its *self-reported health* (health = subset of state). Let a degradation hit effectiveness but not the monitored subset. Downstream consumers degrade; monitor stays green -> harness must weight consumer channels over the monitor.

---

### B8. Environmental coupling / nonlinear upconversion into the measurement band
**Tagline:** an external disturbance (seismic, acoustic, EMI, thermal) couples into the precious measurement — sometimes nonlinearly upconverted in frequency — and looks like a real in-band signal.

- **Mechanism:** Environmental energy couples into the sensing path. It may appear directly, or be *upconverted* (a low-frequency disturbance producing higher-frequency noise in the measurement band) via a nonlinearity. The corrupted measurement mimics a genuine event.
- **Subsystems / couplings:** Optical/metrology sensing x facility environment (floor vibration, acoustics, EMI, temperature); the coupling is often through a specific structural/optical path.
- **Symptoms & where they surface:** Glitches / excess noise / phantom events in the primary measurement **(T main channel)**; the discriminator is *time-coincidence with auxiliary environmental/witness channels* **(T aux)**; the coupling path and which channels are "safe" vs "unsafe" are documented **(D)**.
- **Why it's hard / what's deceptive:** The main channel alone *cannot* tell a real event from an environmental artifact — they look the same. You must correlate with a *different modality* (environment/witness sensors). Nonlinear upconversion hides the causal frequency.
- **Sources to crack it:** **T(main) + T(auxiliary/environmental witnesses)** **+ D** (coupling model; which aux channels are safe to veto with). *The main measurement channel alone fails — by construction.*
- **Real-world grounding:** LIGO uses **~200,000+ auxiliary/environmental channels** to identify time-coincident glitches and veto non-astrophysical events; documented cases include **seismic ground motion upconverting into the gravitational-wave band** and scattered-light noise traced to specific vacuum-chamber motion ([Royal Society review](https://royalsocietypublishing.org/doi/10.1098/rsta.2017.0286); [environmental-influences study](https://repository.lsu.edu/cgi/viewcontent.cgi?article=2626&context=physics_astronomy_pubs)).
- **Build-around / Hold-out:** **Hold-out.** This is the purest "single source provably insufficient" emergent case — exactly your thesis. Let coupling + a nonlinearity generate look-alike glitches.
- **Sim note:** Add environment inputs (`seismic(t)`, `acoustic(t)`) with weak (possibly nonlinear, e.g., squared) coupling into the measurement. Provide separate "auxiliary" sensors for the environment. Real events and coupled artifacts look identical on the main channel; only aux-coincidence + D distinguishes.

---

### B9. Sensor cross-sensitivity -> phantom correlation
**Tagline:** a sensor responds to a variable it isn't supposed to measure, creating a correlation that points diagnosis at the wrong subsystem.

- **Mechanism:** A transducer has secondary sensitivity (a pressure or position sensor that also responds to temperature, a metrology channel that responds to humidity/EMI). When the unintended variable changes, the channel moves, manufacturing a spurious correlation between two unrelated subsystems.
- **Subsystems / couplings:** Sensor of subsystem A with cross-sensitivity to subsystem B's variable; an unmodeled coupling.
- **Symptoms & where they surface:** A persuasive correlation in **T** (A's reading tracks B's activity) that suggests a causal link that doesn't exist; the cross-sensitivity is a *known characteristic* in **D** (sensor datasheet/spec) if you look.
- **Why it's hard / what's deceptive:** The correlation is real and reproducible, so it's compelling — and wrong. Pure data-driven correlation mining gets fooled; you need the sensor's physical characteristics (docs) to know the channel is contaminated.
- **Sources to crack it:** **T** (the correlation + the unintended driver) **+ D** (sensor cross-sensitivity spec / physics). *Telemetry alone fails: it shows a true correlation with a false implied cause.*
- **Real-world grounding:** Cross-sensitivity (e.g., temperature effects on pressure/strain sensors; EMI on signal lines) is standard instrumentation phenomenology and a core reason measurement-system analysis exists (relates to A8). (General instrumentation grounding rather than a single incident — flagged.)
- **Build-around / Hold-out:** **Hold-out.** Add a cross-term to a sensor model; the misleading correlation should emerge during an unrelated event.
- **Sim note:** `reading_A = true_A + alpha*var_B + noise`. When `var_B` (e.g., temperature) changes, A's channel moves with B's activity. The harness must consult D (cross-sensitivity coefficient) to reject the phantom causal link.

---

### B10. Self-erasing intermittent short (whisker-type metallurgical fault)
**Tagline:** a spontaneously grown conductive filament causes a brief short that *fuses itself open* — the evidence destroys itself, and the cause has an unpredictable incubation of months to years.

- **Mechanism:** A metallurgical process (tin/zinc whisker growth, electrochemical migration) spontaneously forms a conductive filament over time. It can cause a transient short that vaporizes itself (fuses open), a stable short, or — in vacuum/high-power conditions — destructive metal-vapor arcing. Incubation is highly variable; there is no accepted test for propensity.
- **Subsystems / couplings:** Electronics/power x time x environment; often aggravated by Pb-free finishes (a process change for environmental compliance).
- **Symptoms & where they surface:** Rare, non-reproducible glitches/shorts **(T, often a single transient)** with no persistent fault; patterns only across the fleet over long time **(I)**; mechanism confirmed by destructive analysis **(R)**; finish/material risk in **D**.
- **Why it's hard / what's deceptive:** The transient short *fuses open*, so post-failure inspection finds nothing — the ultimate No-Fault-Found (links B11). The cause is stochastic in time and not provoked by any operating variable, so telemetry can't predict or reproduce it.
- **Sources to crack it:** **I** (fleet-wide rare-event pattern over long time) **+ R** (teardown / materials FA) **+ T** (the captured transient, if logged at high rate). *Telemetry alone fails: single self-erasing transient, no reproducible state.*
- **Real-world grounding:** NASA attributes multiple on-orbit and ground failures to tin whiskers — e.g., **Cassini's intermittent shorts over ~6 years** traced to whiskers on a plasma-spectrometer card, and the Galaxy IV satellite loss; incubation can be months-years and **no industry-accepted propensity test exists** ([NASA NESC/APPEL](https://appel.nasa.gov/2022/02/17/spotlight-on-lessons-learned-electrical-short-circuits-due-to-tin-whiskers); [NASA NEPP](https://nepp.nasa.gov/whisker/failures/)).
- **Build-around / Hold-out:** **Hold-out.** A stochastic incubation timer + a rare self-clearing fault — let it surprise the harness rather than scripting it.
- **Sim note:** Per-unit whisker incubation drawn from a long-tailed distribution; on "growth," fire a short transient that clears itself (channel returns to normal). No operating variable triggers it -> forces reliance on fleet I + materials-FA R rather than live T.

---

### B11. No-Fault-Found — fails in the field, passes on the bench
**Tagline:** the unit misbehaves in service but tests good in the shop, because the bench doesn't reproduce the field's vibration/thermal/load/timing conditions.

- **Mechanism:** An intermittent fault (cracked joint, fretting connector, marginal timing, thermal-gated defect) only manifests under field stress (vibration, temperature, load, specific sequences). Bench/built-in test re-runs in benign conditions and passes; the part is returned to service and fails again. False alarms from built-in test inflate the churn.
- **Subsystems / couplings:** Any subsystem with an intermittent, condition-gated fault; the *mismatch between field and test conditions*.
- **Symptoms & where they surface:** Repeated remove-and-replace cycles with "no fault found" dispositions **(I, with repeat serials)**; field telemetry **(T)** shows the symptom that the bench can't reproduce; the field-vs-bench condition gap is reasoned about in **R**.
- **Why it's hard / what's deceptive:** The bench test — the thing you trust to confirm the fault — actively says "good." NFF/CND can be a large fraction of avionics removals and the majority of maintenance cost. The signal is the *recurrence pattern* plus the field-condition context, not any single bench result.
- **Sources to crack it:** **I** (repeat removals on the same serial) **+ R** (field-vs-bench condition gap) **+ T** (field-condition signatures around the symptom). *Bench telemetry alone fails: it won't reproduce the fault.*
- **Real-world grounding:** No-Fault-Found / Cannot-Duplicate literature — intermittent faults that pass shop test; **NFF/CND can be ~20-50% of avionics removals and a majority of maintenance cost**, driven by intermittents the bench can't reproduce ([Ungar, Causes & Costs of NFF](https://smtnet.com/library/files/upload/Causes-and-Costs-of-NFF-Events.pdf); [intermittent-fault detection](https://www.aerospacemanufacturinganddesign.com/article/finding-a-cure-for-no-fault-found/)).
- **Build-around / Hold-out:** **Hold-out.** Emerges from a condition-gated intermittent + a benign "test mode."
- **Sim note:** Gate a fault on field-only conditions (`vibration>v0` AND `temp>t0`); provide a "bench" mode that sets those conditions benign. The fault fires in field telemetry but not in bench re-test -> harness must fuse I-recurrence + R-context.

---

### B12. Path-/soak-dependent intermittent (accumulated hidden state)
**Tagline:** the fault appears only after N hours of soak or a specific recipe sequence — it depends on the *history*, so any single snapshot looks innocent.

- **Mechanism:** A hidden state accumulates with operation: a buffer/leak slowly fills, a thermal gradient builds, a counter/log wraps, a contaminant deposits, a hysteretic element latches. The fault fires only past an accumulation threshold or after a particular ordering of operations.
- **Subsystems / couplings:** Any subsystem with memory/accumulation (thermal, contamination, software counters, mechanical wear/backlash) x the operating sequence.
- **Symptoms & where they surface:** Failure correlates with *elapsed soak time or recipe order*, not with any instantaneous reading **(T over a long window)**; reproduction requires replaying the sequence **(R)**; recurrence-by-recipe shows in **I**.
- **Why it's hard / what's deceptive:** A snapshot — or even a short trace — shows nothing wrong; the cause is the *trajectory*. Resetting the tool (clearing the hidden state) "fixes" it temporarily, hiding the accumulation.
- **Sources to crack it:** **T** (long-horizon history, not snapshots) **+ R** (recognizing the accumulation/sequence dependence) **+ I** (recurrence tied to recipe/soak). *A telemetry snapshot alone fails: you need the history.*
- **Real-world grounding:** Soak-/sequence-dependence is a recognized driver of intermittents and NFF (faults that need accumulated stress or specific sequences to appear); pairs with the NFF literature above ([Ungar](https://smtnet.com/library/files/upload/Causes-and-Costs-of-NFF-Events.pdf)). (Mechanism is well-established; the specific "N-hour soak / recipe-order" framing here is generalized — flagged.)
- **Build-around / Hold-out:** **Hold-out.** Your "appears only after N hours soak / specific recipe sequence" candidate; let it emerge from an accumulator + sequence logic.
- **Sim note:** Maintain a hidden accumulator (`fill`, `gradient`, `deposit`, or a wrapping counter) that integrates with operation and is reset on idle/reboot. Fire the fault past a threshold or after a specific op-ordering. Diagnosis requires history-aware telemetry + sequence context, defeating snapshot analysis.

---

## How this catalog feeds your leave-one-source-out ablation

A few design notes so the catalog earns its keep as an eval, not just a list.

- **Each archetype names a specific single-source casualty.** Telemetry-only is the most common one to break, but the table deliberately spreads the load: A17/B10/B11 punish *dropping tickets*; A1/B2/B5 punish *dropping RCA*; A2/A3/B3/B8 punish *dropping docs*. If you want the ablation to show all four sources carrying non-redundant value, stock the scenario set across the table rather than clustering on telemetry-heavy cases.
- **Several archetypes are genuine four-source cases** — A6 (maintenance regression) and A17 (precursor) in particular need T + I + R + D together. These are your strongest demonstrations that fusion beats any single stream, and the cleanest "accuracy falls when you drop *any* one" curves.
- **Watch for redundancy between sources, which weakens the ablation.** If the same fact appears in both a ticket and an RCA deck, dropping one won't hurt accuracy and the ablation will look flat. To get a crisp leave-one-out signal, make each source carry *distinct* evidence: telemetry has the dynamics, tickets have the recurrence/timing, RCA has the mechanism and the field-vs-bench reasoning, docs have the design intent / coupling map / spec. The "Sources to crack it" field is written to keep those roles separate.
- **Distinguish "cannot diagnose" from "diagnoses wrong."** The most valuable cases (A9, A10, B7, B9) don't just leave the agent short of evidence — they actively supply *misleading* evidence (a lying channel, a phantom correlation, a green monitor). A good harness should *reverse* a wrong single-source conclusion when a second source is added, not merely gain confidence. Consider scoring that reversal explicitly.
- **Hold-out validation is a different test from source ablation.** Source ablation asks "does each data source carry signal?"; hold-out asks "does the *simulator* produce failures it wasn't told to produce?" Keep them separate: validate the harness on the full (build-around) set, and validate the *simulator* by checking whether the Part B mechanisms emerge from the coupled model without being scripted.

## Cross-cutting deception patterns (the reasons single-source diagnosis fails)

Most of these archetypes are instances of a smaller set of recurring *diagnostic* traps. Naming them is useful both for the harness's reasoning and for organizing your eval:

1. **The channel lies but is self-consistent** (A9, A10, A8) — needs an independent reference (model/docs or a second modality).
2. **Masking / differential observability** (B7, B1, A10) — the health/alarm path is blind or absent; trusting it blinds you.
3. **Cause and effect separated in time** (A12, B12, A14, A16) — instantaneous correlation misleads; you need history.
4. **Cause and effect separated in space / symptom far from cause** (B5, B1, A14) — the symptom (reset, generic fault) points away from the cause.
5. **Threshold / bifurcation, not a trend** (B4, B2, B3) — sub-critical data don't predict the corner; linear extrapolation is unsafe.
6. **Intermittent / self-erasing / non-reproducible** (B10, B11, B12, A14) — the evidence isn't present when you look, or destroys itself.
7. **Look-alikes: two mechanisms, one signature** (A13, A7) — the same observable has different root causes (and different fixes); needs a disambiguating modality or the spec.
8. **Independence assumptions that don't hold** (B6, A4) — redundancy or reuse fails because of a shared cause or a carried-over assumption.
9. **The evidence is historical/textual, not in the live numbers** (A17, A3, A2) — tickets/RCA/docs carry the non-redundant signal.

## Foundational frameworks worth citing in the writeup

If you want a literature spine for the portfolio narrative, these recur across the catalog:

- **STAMP / STPA (Leveson).** Accidents in complex systems arise from *unsafe interactions* among components, not just component failure; safety as a control problem. The conceptual backbone for the whole emergent/cross-subsystem class ([MIT STAMP publications](http://sunnyday.mit.edu/STAMP-publications.html); [intro](https://www.ul.com/sis/blog/introduction-to-stamp-stpa-and-cast)).
- **Normal Accident Theory (Perrow).** Tight coupling + interactive complexity make certain cascade failures effectively inevitable — underpins B1. *(Cite Perrow, "Normal Accidents," 1984 — foundational text, not from this search.)*
- **Swiss-cheese / latent conditions (Reason).** Latent organizational conditions line up with active failures — underpins A1/A6/A17. *(Cite Reason, "Human Error," 1990 — foundational text, not from this search.)*
- **Gray failure / differential observability (Huang et al.).** Monitors disagree with reality — B7 ([Microsoft Research](https://www.microsoft.com/en-us/research/publication/gray-failure-achilles-heel-cloud-scale-systems/)).
- **Metastable failures (Bronson et al.).** Sustaining feedback loops hold a system in collapse after the trigger clears — B2 ([HotOS '21](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf)).
- **No-Fault-Found / Cannot-Duplicate taxonomy.** Intermittents that defeat bench test — B10/B11/B12 ([Ungar](https://smtnet.com/library/files/upload/Causes-and-Costs-of-NFF-Events.pdf)).
- **Measurement Systems Analysis / Gauge R&R (AIAG).** The measurement chain as a failure source — A8 ([MSA guide](https://www.theleansuite.com/blogs/measurement-system-analysis-gauge-reliability-manufacturing)).
- **Prognostics & Health Management (PHM)** and **FMEA/FMECA / FRACAS** are the practitioner frames for A14-A17 and the reliability-physics records (well-established; cite standard texts/handbooks).

## The two self-chosen research angles (and what they contributed)

Per your brief, beyond the listed domains I pursued two extra angles, both chosen to map tightly onto your tool's subsystem palette:

- **Large-scale precision scientific instruments** (accelerators, gravitational-wave detectors, space telescopes). Closest structural analog to a metrology-class machine — same UHV/cryo/optics/nm-motion/RF/control vocabulary, with unusually deep public anomaly reports. Contributed Hubble (A1), LHC 2008 (B1), and especially LIGO (B8) — the latter is arguably the single best public illustration of your "no single source suffices" thesis, since LIGO *operationally* fuses one precious channel with hundreds of thousands of auxiliary/environmental channels to tell real signals from artifacts.
- **Electronics & materials reliability physics** (tin whiskers, solder-joint thermal fatigue, electromigration, NFF/CND). The metallurgical/thermomechanical underbelly that produces the most *deceptive* delayed/intermittent/self-erasing failures. Contributed A14, A16, B10, B11, B12 — the cases that most directly defeat a snapshot-of-telemetry approach.

## Grounding caveats (where I'm relying on analogy or general literature)

Flagging these explicitly so you can calibrate how much weight each anchor bears:

- **A3 (config rollback):** a clean *single public incident* of "prototype config left in place" is rare; the *pattern* is ubiquitous in field service. TMI's unrestored block valves is an analog, not a like-for-like. Treat as pattern-grounded.
- **A12 (thermal lag), A15 (bathtub), A16 (electromigration), B9 (cross-sensitivity):** grounded in *general engineering/reliability literature*, not a single named incident. These are well-established mechanisms, not speculation — but the anchor is a body of work, not one report.
- **B3 (coupled-loop instability):** grounded by *analogy* (multivariable loop-interaction theory; pilot-induced oscillation) rather than a published metrology-tool incident. The physics is standard; the specific autofocus x stage instantiation is illustrative.
- **B4 (resonance):** the Millennium Bridge is a *cross-domain analog* (crowd-structure feedback) standing in for a stage/structure resonance. The transferable point — a critical-threshold bifurcation where sub-critical history doesn't predict the corner — is exact; the domain is not.
- **B12 (soak/sequence-dependent):** the *mechanism* (accumulated hidden state) is well-established in the NFF literature; the specific "N-hour soak / recipe-order" framing is my generalization to your tool.
- Cross-domain anchors generally (cloud gray failure, distributed-systems metastable, footbridge resonance, aviation/spacecraft incidents) transfer the *failure logic*, not the physics. That's deliberate — the catalog is about diagnostic structure, which is domain-portable — but worth stating plainly in a portfolio writeup so a reviewer doesn't read them as semiconductor-specific claims.

*All synthetic/IP-safe by design; no proprietary or company-specific machine data is used or implied.*
