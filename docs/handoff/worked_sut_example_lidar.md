# Worked SUT example — lidar range-degradation diagnosis

**A design vertical slice.** This document makes the SUT / agent / eval conception concrete through *one fully-instantiated scenario*, end to end. It is the reference that the spike docs and the full-build docs will be written against. Nothing here is the spec yet — it is the worked example we agree on first.

**Scope of this slice:** one instrument; domain = lidar; ~6 subsystems (2 focal, the rest abstracted but carrying real propagation, all behind one interface); one fault traced fully, plus its decoy, a lying channel, and a trigger. The SUT is a **puzzle generator** — a forward causal model that emits internally-consistent evidence for a known injected fault — **not a digital twin**. No physics is solved; fidelity lives in the effects model.

---

## 0. The shape, in one paragraph

A synthetic lidar unit has a known injected fault. The **generator** emits a case: time-series telemetry, a config store, a maintenance logbook, an error log, and a small document corpus — all consistent with that fault's forward effects model, plus an overlapping **decoy**, one **lying channel**, and a salient but non-causal **trigger**. It also emits a hidden **ground truth**. The **agent** (a bounded, hypothesis-driven controller) triages the request, retrieves a diagnostic playbook, runs deterministic checks to discriminate among hypotheses, and produces an **Investigation Graph**: a root cause with a causal chain, per-node supporting/contradicting evidence, ruled-out branches, and flagged conflicts. The **eval** scores it against the ground truth on accuracy, evidence quality, conflict handling, trigger discrimination, and token cost — racing it against a shortcut baseline, a bare LLM, and a tool-equipped ReAct agent.

---

## 1. The SUT — subsystems and coupling topology

### 1.1 Subsystems

| Subsystem | Role here | Key observables | Faults it can host |
|---|---|---|---|
| **Thermal / TEC** | **focal** | `tec_current_A`, `laser_diode_temp_C`, `detector_temp_C`, `ambient_temp_C`, `tec_setpoint_C` (config) | TEC degradation, setpoint misconfig |
| **Laser emitter** | **focal** | `laser_power_mW`, `drive_current_A`, pulse energy | laser power aging, drive instability |
| **Receiver / detector** | abstracted (real propagation) | `detector_bias_V`, `dark_count_rate`, per-region return stats | gain drift, bias drift, dead pixels |
| **Optics / window** | abstracted | `window_transmission_est`, per-region intensity map | window contamination, misalignment |
| **Signal proc / calibration** | abstracted | `firmware_version`, `cal_table_version`, `range_bias_residual` | calibration drift, firmware regression |
| **Scanner / power** | stub | `scan_coverage`, `supply_ripple` | angle miscalibration, brownout |

**Performance KPIs (the "specs" a user notices declining):** `effective_max_range_m`, `range_noise_cm`, `point_density`, `mean_return_intensity`, intensity-by-region.

### 1.2 Coupling topology (edges = "affects", annotated with the propagated effect)

```
Thermal → Laser        (diode temp ↑ ⇒ optical output ↓, wavelength drift)
Thermal → Detector     (detector temp ↑ ⇒ dark-count ↑, gain drift)
Laser   → Returns      (optical output ↓ ⇒ mean return intensity ↓)
Optics  → Returns      (contamination ⇒ intensity ↓, spatially clustered)
Detector→ Returns      (gain/SNR ↓ ⇒ usable returns ↓)
Returns → KPI          (intensity ↓ / SNR ↓ ⇒ effective_max_range ↓)
Calib   → KPI          (table drift ⇒ range_bias)
Power   → all          (stub)
```

The discriminating point: **range degradation is a downstream KPI reachable from at least four subsystems.** That is what makes diagnosis non-trivial — the symptom is far from the cause, and several causes overlap on it.

### 1.3 The uniform subsystem interface (the wrapper contract)

Every subsystem — focal, abstracted, or future-detailed — implements the same contract. Abstraction is just a thinner implementation, swappable later for richer mocked machinery without changing the interface or the agent.

```
Subsystem:
  observables()            -> emits its signals / config / log events for a case
  respond(upstream_effects)-> how its observables shift given effects arriving via topology edges
  fault_hooks()            -> faults it can host + each fault's forward-effect signature
```

- **Focal** = rich implementation (many channels, detailed signatures).
- **Abstracted** = thin implementation (coarse channels, simple propagation) — still couples, can still carry a decoy.
- **Extended project** = swap a thin implementation for richer mocked machinery; interface unchanged.

A side benefit: the generator is a clean standalone engineering artifact (it produces labelled diagnostic cases) that stands on its own even if the AI layer is ignored.

---

## 2. The fault catalog (spike target: ~6)

1. **TEC degradation** ← *traced in full below*
2. Laser power aging ← *the decoy for #1*
3. Window contamination (spatially clustered)
4. Detector bias drift
5. Calibration-table drift (post-maintenance)
6. Scanner angle miscalibration (sparse region)

Each is one fault hook with a forward-effect signature. The catalog is built so **no single surface feature predicts the cause** (see §6).

---

## 3. The traced scenario — "effective range degraded"

### 3.1 Ground truth (hidden from the agent)

- **Root cause:** TEC degradation (Thermal). The cooler is losing capacity; it can no longer hold the laser diode at setpoint.
- **Causal chain:** TEC degradation → laser-diode over-temperature → laser optical output ↓ **and** detector over-temperature → (a) mean return intensity ↓ → effective range ↓; (b) dark-count ↑ → SNR ↓ → effective range ↓ (secondary).
- **Decoy (overlapping cause):** laser power aging — also drops optical output → intensity → range. Consistent with "intensity down, range down." **Discriminator:** aging shows *nominal* diode temp and *no* temperature correlation; TEC degradation shows elevated diode temp, elevated TEC current, and intensity that *correlates with diode temperature*.
- **Lying channel:** `detector_temp_C` is flatlined at 25.0 °C (a stuck sensor, unrelated to the fault). It falsely suggests "thermal is fine." A robust solver should notice ~zero variance under varying load and distrust it, leaning on `laser_diode_temp_C` + `tec_current_A`.
- **Trigger (non-causal):** a **system reboot 2 days ago** (logbook). Salient and recent — a shortcut solver blames it. But the degradation trend **began ~6 days ago, predating the reboot**, so the reboot is coincident, not causal. Correct answer: TEC degradation, with the reboot noted as a non-causal trigger.

**Evidence sets (used by the eval):**
- *Load-bearing:* `tec_current_A` at limit; `laser_diode_temp_C` above setpoint; intensity↔diode-temp correlation; onset predates reboot; intermittent `TEC_LOAD_HIGH`.
- *Decoy-overlap:* `laser_power_mW` ↓, `mean_return_intensity` ↓, `effective_max_range_m` ↓ (consistent with aging too).
- *Conflict/caveat:* `detector_temp_C` flatlined (unreliable); reboot 2d ago (trigger, not cause).

### 3.2 What the generator emits (the case artifacts)

**Telemetry** (illustrative synthetic values; degradation window ≈ 6 days):

| Signal | Baseline | Now | Note |
|---|---|---|---|
| `effective_max_range_m` | 120 | 110 | the symptom (−8%) |
| `mean_return_intensity` | 1.00 | 0.85 | −15%, **correlates with diode temp (r≈0.9)** |
| `laser_power_mW` | 48 | 42 | −12% (also consistent with aging) |
| `laser_diode_temp_C` | 25.2 | 31.5 ↑ | above 25.0 setpoint — **key** |
| `tec_current_A` | 1.2 | 2.3 | 92% of 2.5 A limit — **key** |
| `detector_temp_C` | 25.0 | 25.0 (flat) | **lying channel — stuck** |
| `dark_count_rate` | 1.00 | 1.20 | mildly elevated (secondary) |
| `ambient_temp_C` | 22 | 22 | nominal (rules out external heat) |
| intensity-by-region | uniform | uniform drop | **not localized — rules out window** |

**Config store:** `cal_table_version`, `firmware_version`, `tec_setpoint_C`, `scan_params` — **all unchanged** (rules out calibration / firmware).

**Logbook (excerpt):**
```
[t−2d]   system reboot (scheduled)            ← the trigger
[t−400d] last thermal-subsystem service
```

**Error / warning log:** `TEC_LOAD_HIGH` — intermittent, increasing frequency over the window (a strong clue the agent must still connect to the chain).

**Corpus (small):**
- system-model doc: the Thermal→Laser→Intensity→Range chain; the rule "optical output falls as diode temperature rises above setpoint."
- playbook: *Diagnosing range degradation* (the procedure that dispatches the checks in §4).
- prior cases: one past TEC-degradation incident (similar signature) and one past laser-aging incident (for contrast).

**Diagnostic actions (history):**
- prior: window cleaned 5 days ago → no improvement (reinforces: not contamination).
- not yet tried: laser-module swap-test — would cleanly isolate laser-vs-thermal; a high-VOI next action the agent can *recommend*.

> The full Corpus/Schema family — telemetry, tickets, reports (formerly RCAs), docs, design/test documentation, procedures, diagnostic actions — is defined in the separate schema doc.

### 3.3 The observable interface and deterministic checks the agent can call

- **Query telemetry** (signal, window) → series + summary stats.
- **Diff config** vs baseline → changed keys.
- **Read logbook / errors** (window) → events.
- **Search corpus** (hybrid) → doc spans, playbooks, prior cases.
- **Read diagnostic-action history** → what's been tried, and the result.
- Deterministic checks (code, cheap, auditable):
  - `config_diff` → "no relevant change."
  - `spatial_intensity_check` → "uniform, not localized."
  - `temp_correlation_check` → "intensity ↔ diode-temp r≈0.9." **(the discriminator)**
  - `tec_load_check` → "TEC current 92% of limit."
  - `channel_sanity_check` → "`detector_temp_C` variance ≈ 0 under load → unreliable."
  - `onset_vs_event_check` → "degradation onset ≈ t−6d; reboot at t−2d → onset predates trigger." **(demotes the trigger)**

---

## 4. The agent run (target trajectory)

1. **Triage.** Symptom = `effective_max_range_m` ↓. Metadata: in-house tool, fresh request, log streams available. The reboot 2d ago raises the prior on "recent-change" causes — but this is a prior, not a conclusion.
2. **Playbook retrieval.** Retrieves *Diagnosing range degradation*, which frames a differential: {window contamination, detector drift, laser aging, thermal/TEC, calibration drift} and prescribes the checks above.
3. **Cheap eliminations first.** `config_diff` → no change (clears calibration/firmware). `spatial_intensity_check` → uniform (clears window contamination).
4. **The discriminating move (VOI).** Laser aging vs TEC both predict intensity↓/range↓; the single most discriminating check is thermal. `temp_correlation_check` → intensity tracks diode temp; `tec_load_check` → TEC at limit; `laser_diode_temp` above setpoint. → TEC degradation dominates laser aging.
5. **Trigger demotion.** `onset_vs_event_check` → degradation predates the reboot → the reboot is a non-causal trigger, not the cause.
6. **Lying-channel handling.** `channel_sanity_check` flags `detector_temp_C` as stuck; the agent down-weights it and relies on diode temp + TEC current.
7. **Output — the Investigation Graph:**
   - **Root cause:** TEC degradation (Thermal) — high confidence.
   - **Causal chain:** as in §3.1.
   - **Supporting (per node):** TEC current 92% of limit; diode temp 31.5 °C vs 25 °C setpoint; intensity↔temp r≈0.9; intermittent `TEC_LOAD_HIGH`; onset predates reboot.
   - **Ruled out:** window contamination (uniform drop); calibration/firmware (no config change); laser aging (no temp elevation or correlation).
   - **Conflicts flagged:** `detector_temp_C` unreliable (not trusted); reboot 2d ago is a trigger, not the cause.
   - **Recommended next action (VOI):** a laser-module swap-test to confirm thermal-vs-laser before ordering a part; then inspect/replace the TEC module and service the `detector_temp` sensor.

This trajectory is the controller's serialized state — there is no separate animation layer; the **live view renders the actual state object** as it changes (nodes appear, recolor for/against, deepen on contested branches), and the eval reads the same object.

---

## 5. The eval for this case

| Dimension | What it measures | This case |
|---|---|---|
| **Accuracy** | top hypothesis == ground-truth cause | TEC degradation ✓ |
| **Evidence-F1** | precision/recall of cited evidence vs the load-bearing set; no hallucinated citations | cite TEC/diode-temp/correlation/onset; avoid inventing |
| **Conflict handling** | surfaced the lying channel + the trigger-vs-cause distinction | flag stuck `detector_temp`; demote reboot |
| **Trigger discrimination** | did NOT blame the salient recent event | reboot correctly demoted |
| **Cost** | tokens per resolved case vs baselines | curated checks vs dumping all data |

**Baselines on this exact case:**
- **Shortcut baseline** ("blame the most recent change/event") → blames the reboot → **wrong**. (If the agent only ties this, the case is leaky.)
- **Bare LLM, all data in context** → may reach TEC, but typically with thin/partly-hallucinated support and no explicit trigger demotion; pays for the full dump.
- **Tool-equipped ReAct** → can get there, but without enforced hypothesis bookkeeping it often stops early or skips the conflict flags.
- **Structured controller** → correct cause + grounded evidence + conflicts surfaced, at lower token cost. This is the uplift to demonstrate.

Eval ladder: **shortcut baseline < bare LLM < tool-equipped ReAct < structured controller.**

---

## 6. How this generalizes (the knobs)

- **New scenario family** = promote a different subsystem to focal and pick its fault hooks. The topology and interface are unchanged.
- **Breaking the shortcut (catalog-level):** sibling cases decorrelate surface features from cause —
  - a **coincidence case**: a real config change is present but is a red herring; the true cause is elsewhere;
  - an **absent-cue case**: a fault with no recent change/reboot;
  - **trigger ≠ cause** (this case): a salient event that the time-ordering check demotes.
  Target: correlation between "salient recent event" and "that event is the cause" ≈ 0.5, not ≈ 1.0.
- **Abstracted subsystems** carry real coarse propagation now; the extended project replaces a stub with mocked machinery behind the same interface.
- **Volume** (annoying-to-wade-through) is a generation knob: pad telemetry length, add benign log churn, and roughen artifacts with an LLM pass; it does not change the causal model.

---

## 7. Difficulty catalog (living)

The mechanisms that make a case hard. Each is defined on the live Investigation Graph, so it doubles as a **generation knob** and an **eval target**. A scenario picks a few; the list is extensible in production. Bracketed IDs (e.g., [B7]) cross-reference `failure_mode_archetypes.md`, whose "9 cross-cutting deception patterns" are the organizing spine. *Cost* = generation effort.

**A · How evidence combines on a hypothesis**
- **A1 Mixed evidence on one node** — supporting and contradicting evidence on the same hypothesis; confidence is the net. *Cheap.*
- **A2 Shared / diagnostic evidence** — one observation moves two hypotheses (raises one, lowers another). *Cheap.*
- **A3 Reasoning from absence** — the missing expected signal is the clue ("aging would have raised drive current; it didn't"). *Cheap.*
- **A4 Common-cause vs multiple-fault** — one upstream cause looks like several independent faults; includes the error-cascade from one trigger (e.g., wrong SW boot order). *Medium.*
- **A5 Common-mode defeats redundancy** [B6] — redundant channels agree, falsely reassuring, because one shared cause hits them all. *Medium.*

**B · How much a piece of evidence counts**
- **B1 Context-weighted evidence** — a ticket cites a config; weight = config-match × recency, flipping on whether its date falls before/after a major HW/SW release. *Medium; tickets are a high-leverage primitive.*
- **B2 Source credibility** — weight by reporter/source reliability (calibrated sensor vs vague ticket vs flaky channel). *Cheap.*
- **B3 Stale-doc / validity-window trap** — an outdated spec from before a HW revision misleads; check the validity window/provenance. *Medium.*
- **B4 Salience ≠ relevance** — a loud alarm or spike that's benign, pulling attention off the subtle cause. *Cheap.*
- **B5 Lying channel** [A8/A9/A10] — a channel reports plausible-but-wrong values; needs an independent reference. *Cheap.*
- **B6 Observability gap / masking** [B7 gray failure, B1] — the channel that would reveal the cause is absent or silent; a blind health path blinds you. Distinct from B5 (wrong values vs missing observability). *Medium.*

**C · Getting to the evidence (where the graph + RAG earn their keep)**
- **C1 Navigation-gated / buried evidence** — a relevant artifact isn't obviously relevant; you learn to open it only by traversing a relationship edge. The graph's navigation role. *Medium.*
- **C2 Intra-document enrichment** — the useful fact is buried inside a found artifact, surfaced by RAG within it. *Medium.*
- **C3 Chained / multi-hop evidence** — the fact needs a chain (log → ticket → config → date → release boundary); no single retrieval gets it. *Harder.*
- **C4 Knowledge-gap surfacing** — a log cites a metric the Project has no spec for; the correct move is to request the spec/reference, not guess. *Medium.*

**D · What you must do with it (temporal & quantitative reasoning)**
- **D1 Trigger vs cause** — demote a salient recent event by time-ordering (onset predates it). *Cheap.*
- **D2 Lagged cause / transport delay** [A12] — the true cause is temporally distant; instantaneous correlation misleads; needs history-with-lag. Inverse of D1. *Medium.*
- **D3 Intermittent / condition-dependent** — manifests only under a condition (duty cycle, cold start); a single snapshot misses it. *Medium.*
- **D4 Threshold / bifurcation, no warning trend** [B2 metastable, B3 coupled-loop, B4 resonance-corner] — appears only at an operating-point corner; sub-critical data don't extrapolate. The emergent class; warrants the small dynamic core. *Harder.*
- **D5 Compute-to-discriminate** — diagnostic only after a computation (correlation, rate, residual, threshold). Forces the deterministic check. *Cheap-ish.*
- **D6 Tie-breaker under budget** — near-symmetric hypotheses; only an expensive check breaks the tie, so spend or abstain. Tests VOI + abstention; this is the "two discriminating checks / deeper search" case. *Cheap.*

**E · When there may be no clean answer (uncertainty & abstention)**
- **E1 No-clean-cause / coincidence / self-resolved** — the honest answer is "intermittent, no single cause," "resolved without action," or "coincidence"; report uncertainty, don't confabulate. The anti-confabulation guard. *Cheap.*
- **E2 Self-erasing / No-Fault-Found** [B10, B11, B12] — the evidence destroys itself or won't reproduce on the bench; a passing test ≠ cleared. Interacts with diagnostic actions. *Medium.*

*This catalog is the direct input to the scenario generator: each scenario = one fault + a chosen subset of these mechanisms. New mechanisms get appended (including from production).*

---

## 8. Decisions locked

- **System = lidar** (precision-instrument framing; on-strategy for the AV/sensing adjacency).
- **SUT = puzzle generator** (forward causal model over a coupling graph), not a digital twin; small dynamic core only for the inherently-temporal faults (D4).
- **Numbers** will be calibrated against real automotive-lidar specs when artifacts are locked.
- **Difficulty** includes deeper / two-check cases (D6) and the full catalog above.
- **Catalog depth for the spike:** carry 2–3 faults fully + stub the rest as named fault-hooks.
- **Trace schema is first-class:** the Investigation Graph is the controller's live state object — the single source the reasoning writes, the eval reads, and the view renders.
- **Diagnostic actions** added as a Corpus type (history in + recommend-next, where recommend-next = the VOI choice).

---

*This is the worked example, not the spike spec. Next, on your go: the Corpus Schema turn, then the extensive spike docs (built against this), then the full-build docs.*
