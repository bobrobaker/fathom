"""The spike case set (spec §5.3) as (fault, mechanisms, seed) tuples.

Case #1 (TEC degradation) is authored to depth at M1; cases #2–#8 are declared
here with their target mechanisms and are filled in at M7 (their faults become
real entries in `faults.FAULTS`). The eval's frozen slice draws from this list.
The anti-shortcut balance (≈0.5 correlation between salient-recent-event and
cause, §5.2) is enforced across the set as the cases are authored.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CaseSpec:
    id: str
    fault: str
    mechanisms: tuple[str, ...]
    seed: int
    purpose: str
    authored: bool = False  # True once the fault is implemented to depth
    # Anti-shortcut balance (§5.2): does the salient recent event equal the true cause?
    #   True  → the recent change/event IS the cause (a shortcut is right here)
    #   False → a salient recent event exists but is NOT the cause (trigger≠cause / coincidence)
    #   None  → no salient recent event (absent-cue) or no single cause (abstain)
    # Across the set the True-fraction over the not-None cases must sit ≈0.5 (B8), so that
    # "a recent event is present" carries ~no information about whether it is the cause.
    salient_is_cause: bool | None = None


CASES: list[CaseSpec] = [
    # `purpose` doubles as the viewer caption (reader-facing): keep it plain English, no internal
    # catalog/case references. The difficulty mechanisms live in the tuple; the design rationale in the
    # trailing comment + salient_is_cause.
    CaseSpec("case1", "tec_degradation", ("D1", "B5", "D5", "A2"), 0,
             "A cross-subsystem fault masked by a decoy part, a lying sensor channel, and a coincidental "
             "reboot that has to be demoted.",
             authored=True, salient_is_cause=False),       # reboot present, non-causal
    CaseSpec("case2", "laser_aging", ("D5", "A1"), 1,
             "An aging laser is the true cause, even though a tempting decoy part would normally show a "
             "temperature correlation and here doesn't.",
             authored=True, salient_is_cause=False),        # reboot present, non-causal
    CaseSpec("case3", "window_contamination", ("C-spatial", "A3"), 2,
             "A spatially-clustered intensity loss, pinned down by where it occurs and by an expected "
             "signal that never appears.",
             authored=True, salient_is_cause=False),        # reboot present, non-causal
    CaseSpec("case4", "calibration_drift", ("B1", "C3"), 3,
             "Here the recent config change really is the culprit — the salient event is the cause, not a "
             "red herring to rule out.",
             authored=True, salient_is_cause=True),         # cal-table change IS the cause
    CaseSpec("case5", "no_clean_cause", ("E1",), 4,
             "No single clean cause exists; the correct answer is to abstain rather than name a culprit.",
             authored=True, salient_is_cause=None),         # abstain — no single cause
    CaseSpec("case6", "detector_bias_drift", ("C1", "C2"), 5,
             "No obvious cue — the deciding evidence is reached only by traversing the graph to it and "
             "digging it out of a document.",
             authored=True, salient_is_cause=None),         # absent-cue — no recent event
    CaseSpec("case7", "tec_degradation_variant", ("D6",), 6,
             "Two near-identical suspects that only an expensive discriminating check can tell apart.",
             authored=True, salient_is_cause=False),        # reboot present, non-causal
    CaseSpec("case8", "common_mode_power", ("A4", "A5"), 7,
             "One upstream power fault that masquerades as two independent faults across redundant channels.",
             authored=True, salient_is_cause=True),         # power-mode change IS the cause
]

CASES_BY_ID = {c.id: c for c in CASES}


def authored_cases() -> list[CaseSpec]:
    """Cases whose fault is implemented to depth (eval-ready)."""
    return [c for c in CASES if c.authored]
