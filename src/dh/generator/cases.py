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


CASES: list[CaseSpec] = [
    CaseSpec("case1", "tec_degradation", ("D1", "B5", "D5", "A2"), 0,
             "worked example: cross-subsystem + decoy + lying channel + demoted trigger",
             authored=True),
    CaseSpec("case2", "laser_aging", ("D5", "A1"), 1,
             "decoy as a true cause (no temp correlation) — symmetry vs case1",
             authored=True),
    CaseSpec("case3", "window_contamination", ("C-spatial", "A3"), 2,
             "spatial-cluster signature; reasoning from absence", authored=True),
    CaseSpec("case4", "calibration_drift", ("B1", "C3"), 3,
             "post-release config; chained evidence (date -> release)"),
    CaseSpec("case5", "no_clean_cause", ("E1",), 4,
             "intermittent/coincidence -> correct answer is abstain", authored=True),
    CaseSpec("case6", "detector_bias_drift", ("C1", "C2"), 5,
             "buried evidence reachable only via graph traversal + intra-doc"),
    CaseSpec("case7", "tec_degradation_variant", ("D6",), 6,
             "near-symmetric to a decoy; needs the expensive discriminating check"),
    CaseSpec("case8", "common_mode_power", ("A4", "A5"), 7,
             "one cause looks like two faults; redundant channels agree but are wrong"),
]

CASES_BY_ID = {c.id: c for c in CASES}


def authored_cases() -> list[CaseSpec]:
    """Cases whose fault is implemented to depth (eval-ready)."""
    return [c for c in CASES if c.authored]
