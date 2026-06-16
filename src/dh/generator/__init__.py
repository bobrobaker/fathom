"""Lidar case generator (spec §5).

`generate(fault, mechanisms, seed) -> Case` is deterministic given a seed: it runs
a fault's forward-effects model into telemetry, then composes the corpus, BOM, and
hidden ground truth around it. The generator is a clean standalone artifact — it
produces labelled diagnostic cases independent of the AI layer.
"""

from __future__ import annotations

from dh.generator.compose import build_case
from dh.schemas import Case


def generate(fault: str, mechanisms: list[str], seed: int = 0) -> Case:
    """Build one labelled case for `fault` with the requested difficulty `mechanisms`."""
    return build_case(fault, mechanisms, seed)


__all__ = ["generate", "build_case"]
