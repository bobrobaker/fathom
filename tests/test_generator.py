"""M1 gate (spec §5, build plan M1).

The TEC case generates deterministically and matches the worked example's
signatures; its ground truth is well-formed; and it round-trips through the golden
fixture `fixtures/tec_case.json`.

Regenerate the fixture after an intentional generator change:
    .venv/bin/python -c "from dh.generator import generate; import pathlib; \
      pathlib.Path('fixtures/tec_case.json').write_text(\
      generate('tec_degradation',['D1','B5','D5','A2'],0).model_dump_json(indent=2))"
"""

import json
import statistics as st
from pathlib import Path

import pytest

from dh.generator import faults, generate
from dh.generator.signatures import pearson_r
from dh.schemas import Case

MECHS = ["D1", "B5", "D5", "A2"]
FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "tec_case.json"


@pytest.fixture(scope="module")
def case() -> Case:
    return generate("tec_degradation", MECHS, seed=0)


def _sig(case: Case) -> dict:
    return {s.signal: s for s in case.telemetry}


def _recent(series, k=5) -> float:
    return st.mean(series.v[-k:])


def _baseline(series, k=8) -> float:
    return st.mean(series.v[:k])


# --- determinism (spec §5.1) -------------------------------------------------

def test_deterministic_per_seed():
    a = generate("tec_degradation", MECHS, seed=0)
    b = generate("tec_degradation", MECHS, seed=0)
    assert a.model_dump() == b.model_dump()


def test_different_seed_differs():
    a = generate("tec_degradation", MECHS, seed=0)
    c = generate("tec_degradation", MECHS, seed=1)
    assert a.model_dump() != c.model_dump()


def test_unknown_fault_raises():
    with pytest.raises(ValueError):
        generate("not_a_fault", [], seed=0)


# --- signatures match the worked example (§3.2) ------------------------------

def test_intensity_drop_and_temp_correlation(case):
    s = _sig(case)
    intensity, diode = s["mean_return_intensity"], s["laser_diode_temp_C"]
    drop = (_baseline(intensity) - _recent(intensity)) / _baseline(intensity)
    assert 0.10 <= drop <= 0.20  # ~-15%
    r = pearson_r(intensity.v, diode.v)
    assert r < 0 and abs(r) >= 0.85  # intensity falls as diode temp rises, |r|≈0.9


def test_tec_near_limit(case):
    s = _sig(case)
    tec, limit = s["tec_current_A"], faults.TEC_LIMIT_A
    assert 0.85 <= tec.v[-1] / limit <= 0.95  # ~92% of limit


def test_diode_above_setpoint(case):
    s = _sig(case)
    assert _recent(s["laser_diode_temp_C"]) > faults.SETPOINT_C + 3  # well above 25.0


def test_detector_temp_flatlined_but_ambient_lives(case):
    s = _sig(case)
    assert st.pvariance(s["detector_temp_C"].v) == 0.0  # lying channel: stuck
    assert st.pvariance(s["ambient_temp_C"].v) > 0.0    # a normal channel still varies


def test_intensity_by_region_uniform(case):
    s = _sig(case)
    finals = [s[f"region_intensity_{i}"].v[-1] for i in range(faults._N_REGIONS)]
    spread = max(finals) - min(finals)
    assert spread < 0.15  # uniform drop — not a localized (window) signature


def test_onset_predates_reboot_timing(case):
    # injected timing facts: onset 6d before now, reboot 2d before now
    assert faults.ONSET == faults.NOW - 6
    assert faults.REBOOT_T == faults.NOW - 2
    assert faults.ONSET < faults.REBOOT_T  # onset predates the trigger (D1)
    s = _sig(case)
    rng = s["effective_max_range_m"]
    pre = [v for ti, v in zip(rng.t, rng.v) if ti < faults.ONSET]
    post = [v for ti, v in zip(rng.t, rng.v) if ti >= faults.REBOOT_T]
    assert st.mean(post) < st.mean(pre) - 5  # degradation is well underway by the reboot
    reboot = next(a for a in case.artifacts if a.id == "log.reboot")
    assert reboot.timestamp == faults.REBOOT_T


# --- ground-truth well-formedness (§3.2) -------------------------------------

def test_ground_truth_well_formed(case):
    gt = case.ground_truth
    node_ids = {n.id for n in case.graph.nodes}
    assert gt.answer_type == "cause"
    assert gt.root_cause == "part.tec" and gt.root_cause in node_ids
    assert gt.causal_chain and all(nid in node_ids for nid in gt.causal_chain)
    assert gt.load_bearing_evidence  # non-empty
    assert gt.trigger == "log.reboot"
    assert set(gt.conflicts) == {"metric.detector_temp", "log.reboot"}
    assert "part.laser_module" in gt.decoys  # the laser-aging decoy
    assert gt.mechanisms == MECHS


def test_conflict_nodes_exist(case):
    node_ids = {n.id for n in case.graph.nodes}
    for nid in case.ground_truth.conflicts:
        assert nid in node_ids
    lying = next(n for n in case.graph.nodes if n.id == "metric.detector_temp")
    assert lying.props["signal"] == "detector_temp_C"  # resolves to the stuck channel


# --- structural integrity ----------------------------------------------------

def test_artifact_refs_and_ids(case):
    node_ids = {n.id for n in case.graph.nodes}
    ids = [a.id for a in case.artifacts]
    assert len(ids) == len(set(ids))  # unique
    for a in case.artifacts:
        for ref in a.refs:
            assert ref in node_ids  # every reference resolves to a node


def test_metric_signals_resolve(case):
    signals = {s.signal for s in case.telemetry}
    for n in case.graph.nodes:
        if n.type in ("metric", "KPI"):
            assert n.props["signal"] in signals


def test_bom_part_of(case):
    bom = case.bom
    part_of = {(e.src, e.dst) for e in bom.edges if e.type == "part_of"}
    assert ("part.tec", "sub.thermal") in part_of
    assert bom.neighbors("part.tec", edge_type="part_of") [0].id == "sub.thermal"


# --- golden fixture (build plan M1 deliverable) ------------------------------

def test_fixture_matches_generator(case):
    assert FIXTURE.exists(), "run the regen command in this file's docstring"
    loaded = Case.model_validate_json(FIXTURE.read_text())
    assert loaded.model_dump() == case.model_dump()


def test_fixture_hides_nothing_extra(case):
    # the fixture is the full case including ground truth (eval-only); sanity-check shape
    data = json.loads(FIXTURE.read_text())
    assert set(data) == {"id", "graph", "telemetry", "artifacts", "bom", "ground_truth"}
