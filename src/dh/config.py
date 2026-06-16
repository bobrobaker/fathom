"""Load `config.yaml` (model pin, thresholds, seeds, VOI costs) — spec §6.2/§6.3/§10.

A thin typed-ish accessor so the controller, eval, and llm layers read one source of
truth for tunables instead of hard-coding them.
"""

from __future__ import annotations

import functools
import pathlib

import yaml

_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_DEFAULT = _ROOT / "config.yaml"


@functools.lru_cache(maxsize=8)
def load_config(path: str | None = None) -> dict:
    p = pathlib.Path(path) if path else _DEFAULT
    return yaml.safe_load(p.read_text())


def model_id(path: str | None = None) -> str:
    return load_config(path)["model"]["id"]


def thresholds(path: str | None = None) -> dict:
    return load_config(path)["thresholds"]


def budget(path: str | None = None) -> int:
    return load_config(path)["controller"]["budget"]


def voi_costs(path: str | None = None) -> dict:
    return load_config(path)["voi_costs"]
