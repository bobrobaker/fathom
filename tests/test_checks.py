"""M2 gate (spec §4, §6.5, build plan M2).

Each deterministic check returns the expected structured result on the TEC case;
the environment fronts the case correctly and never leaks ground truth.
"""

import pytest

from dh.environment import BenchmarkEnvironment, Environment, LidarEnvironment, NotSupported
from dh.generator import generate
from dh.schemas import Artifact, Case


@pytest.fixture(scope="module")
def case() -> Case:
    return generate("tec_degradation", ["D1", "B5", "D5", "A2"], seed=0)


@pytest.fixture(scope="module")
def env(case) -> LidarEnvironment:
    return LidarEnvironment(case)


# --- the six checks (M2 done-when) -------------------------------------------

def test_temp_correlation_reports_r(env):
    r = env.run_check("temp_correlation_check")
    assert abs(r["r"]) >= 0.85 and r["correlated"]  # r≈0.9
    assert r["sign"] == "negative"  # intensity falls as diode temp rises


def test_onset_precedes_reboot(env):
    r = env.run_check("onset_vs_event_check")
    assert r["onset_predates_event"]
    assert r["onset_t"] < r["event_t"]
    assert abs(r["onset_t"] - 4.0) <= 1.0  # change-point recovers the true onset (~t-6d)


def test_channel_sanity_flags_detector_temp(env):
    assert env.run_check("channel_sanity_check", {"signal": "detector_temp_C"})["stuck"]
    # a live channel is not flagged
    assert not env.run_check("channel_sanity_check", {"signal": "ambient_temp_C"})["stuck"]


def test_tec_load_near_limit(env):
    r = env.run_check("tec_load_check")
    assert r["at_limit"] and 0.85 <= r["frac_of_limit"] <= 0.95


def test_config_diff_no_change(env):
    assert env.run_check("config_diff")["any_change"] is False


def test_spatial_intensity_uniform(env):
    assert env.run_check("spatial_intensity_check")["localized"] is False


def test_unknown_check_raises(env):
    with pytest.raises(ValueError):
        env.run_check("not_a_check")


def test_check_resolves_metric_node_ids(env):
    # checks accept metric node ids, not just raw signal names
    r = env.run_check("temp_correlation_check",
                      {"signal_a": "metric.intensity", "signal_b": "metric.diode_temp"})
    assert abs(r["r"]) >= 0.85


# --- environment interface ---------------------------------------------------

def test_symptom_and_capabilities(env):
    assert "range" in env.symptom().lower()
    caps = env.capabilities()
    assert {"run_check", "search", "traverse", "query_telemetry"} <= caps


def test_query_telemetry_window(env):
    full = env.query_telemetry("laser_diode_temp_C")
    sliced = env.query_telemetry("laser_diode_temp_C", window=(0.0, 2.0))
    assert len(sliced.t) < len(full.t) and all(0.0 <= t <= 2.0 for t in sliced.t)


def test_query_unknown_signal_raises(env):
    with pytest.raises(KeyError):
        env.query_telemetry("nope")


def test_read_logbook_errors_actions(env):
    assert any(a.id == "log.reboot" for a in env.read_logbook())
    assert any(a.id == "err.tec_load" for a in env.read_errors())
    actions = {a.id for a in env.read_diagnostic_actions()}
    assert {"act.window_clean", "act.swap_test"} <= actions


def test_traverse(env):
    parts = env.traverse("sub.thermal", "measured_by")
    assert "metric.diode_temp" in {n.id for n in parts}


def test_search_ranks_relevant_first(env):
    assert env.search("range degradation playbook differential", k=1)[0].id == "doc.playbook"
    assert env.search("TEC current thermal", k=1)[0].id == "report.prior_tec"


# --- ground-truth boundary (non-negotiable #1) -------------------------------

def test_environment_never_exposes_ground_truth(env, case):
    # no public attribute returns the GroundTruth object
    from dh.schemas import GroundTruth
    public = [getattr(env, n) for n in dir(env) if not n.startswith("_")]
    assert all(not isinstance(x, GroundTruth) for x in public)
    # and nothing the controller can call returns it
    assert not isinstance(env.symptom(), GroundTruth)
    for art in env.search("cause root", k=5) + env.read_logbook() + env.read_errors():
        assert "answer_type" not in (art.text or "")  # gt fields aren't serialized into text


# --- benchmark environment degrades gracefully -------------------------------

def test_benchmark_env_supports_only_qa():
    benv = BenchmarkEnvironment("Who founded the company?",
                                [Artifact(id="p0", kind="passage", text="Acme was founded by Ada.")])
    assert isinstance(benv, Environment)
    assert benv.capabilities() == {"symptom", "search"}
    assert benv.search("who founded Acme", k=1)[0].id == "p0"
    for call in (lambda: benv.run_check("config_diff", {}),
                 lambda: benv.query_telemetry("x"),
                 lambda: benv.traverse("a", "affects"),
                 lambda: benv.list_signals()):
        with pytest.raises(NotSupported):
            call()
