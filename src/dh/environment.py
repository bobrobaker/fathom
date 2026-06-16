"""The environment interface (spec §4) — the controller's only window on a case.

One `Environment` ABC fronts two worlds: `LidarEnvironment` (the generated SUT, full
diagnostic toolset) and `BenchmarkEnvironment` (a QA passage set, `symptom`+`search`
only). The controller is written once against this interface and degrades gracefully
when a method is unavailable (it discovers capabilities via `capabilities()` or by
catching `NotSupported`).

**Non-negotiable #1 (ground truth is eval-only):** `LidarEnvironment` holds the `Case`
privately and exposes *nothing* that returns `Case.ground_truth`. The eval reads ground
truth from the `Case` directly; it never travels through this boundary.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from dh import checks
from dh.schemas import Artifact, Case, Node, TimeSeries

_TOKEN = re.compile(r"\w+")


class NotSupported(RuntimeError):
    """Raised when a method isn't available in this environment (e.g. lidar tools on QA)."""


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def _bm25_rank(query: str, k: int, items: list, toks: list[list[str]], bm25) -> list:
    """Top-k items by BM25, gated on sharing ≥1 query token.

    The overlap gate (not a score>0 threshold) is what keeps this robust to tiny
    corpora, where BM25's IDF turns negative because every term is in every doc.
    """
    q = _tokenize(query)
    qset = set(q)
    scores = bm25.get_scores(q)
    cand = [(scores[i], i) for i in range(len(items)) if qset & set(toks[i])]
    cand.sort(key=lambda x: (-x[0], x[1]))
    return [items[i] for _, i in cand[:k]]


def _in_window(ts: float | None, window: tuple[float, float] | None) -> bool:
    if window is None:
        return True
    if ts is None:
        return False
    lo, hi = window
    return lo <= ts <= hi


class Environment(ABC):
    @abstractmethod
    def symptom(self) -> str: ...

    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[Artifact]: ...

    def capabilities(self) -> set[str]:
        """Method names this environment supports (the controller probes this)."""
        return {"symptom", "search"}

    # --- lidar-only methods (BenchmarkEnvironment raises NotSupported) --------
    def query_telemetry(self, signal: str, window=None, condition=None) -> TimeSeries:
        raise NotSupported("query_telemetry")

    def run_check(self, name: str, args: dict) -> dict:
        raise NotSupported("run_check")

    def read_logbook(self, window=None) -> list[Artifact]:
        raise NotSupported("read_logbook")

    def read_errors(self, window=None) -> list[Artifact]:
        raise NotSupported("read_errors")

    def read_diagnostic_actions(self) -> list[Artifact]:
        raise NotSupported("read_diagnostic_actions")

    def traverse(self, node_id: str, edge_type: str, direction: str = "out") -> list[Node]:
        raise NotSupported("traverse")

    def list_signals(self) -> list[str]:
        raise NotSupported("list_signals")


class LidarEnvironment(Environment):
    """Wraps one generated lidar `Case`. The full diagnostic toolset (spec §4)."""

    _CHECKS = {
        "config_diff", "spatial_intensity_check", "temp_correlation_check",
        "tec_load_check", "channel_sanity_check", "onset_vs_event_check",
        "detector_health_check", "common_mode_check",
    }

    def __init__(self, case: Case):
        self._case = case  # PRIVATE — ground truth must not leak past this boundary
        self._telemetry = {s.signal: s for s in case.telemetry}
        self._artifacts = {a.id: a for a in case.artifacts}
        self._bm25 = None  # lazily built (rank_bm25)
        self._art_toks: list[list[str]] = []

    # --- discovery -----------------------------------------------------------
    def capabilities(self) -> set[str]:
        return {
            "symptom", "search", "query_telemetry", "run_check", "read_logbook",
            "read_errors", "read_diagnostic_actions", "traverse", "list_signals",
        }

    def symptom(self) -> str:
        for n in self._case.graph.nodes:
            if n.type == "KPI" and "symptom" in n.props:
                return n.props["symptom"]
        return "A performance KPI has degraded. Diagnose the root cause."

    def list_checks(self) -> list[str]:
        """Deterministic checks the controller may request via run_check (§6.5)."""
        return sorted(self._CHECKS)

    def node_ids(self) -> set[str]:
        """All graph node ids + telemetry signal names — the vocabulary the controller
        may legitimately reference (used to filter hallucinated conflict ids). Not a
        ground-truth leak: this is observable topology, already reachable via traverse."""
        return {n.id for n in self._case.graph.nodes} | set(self._telemetry)

    def symptom_node_id(self) -> str:
        """The graph node the symptom attaches to — the controller's traversal entry point."""
        for n in self._case.graph.nodes:
            if n.type == "KPI" and "symptom" in n.props:
                return n.id
        for n in self._case.graph.nodes:
            if n.type == "KPI":
                return n.id
        raise KeyError("no KPI node to anchor the symptom")

    # --- retrieval -----------------------------------------------------------
    def all_artifacts(self) -> list[Artifact]:
        """The full observable corpus — what a 'dump everything' long-context baseline reads
        (spec §7). Observable evidence only; `Case.ground_truth` never travels through here."""
        return list(self._case.artifacts)

    def config_store(self) -> list[Node]:
        """The raw config nodes (current + baseline values) — observable, not a computed diff."""
        return [n for n in self._case.graph.nodes if n.type == "config"]

    def search(self, query: str, k: int = 5) -> list[Artifact]:
        from rank_bm25 import BM25Okapi

        arts = self._case.artifacts
        if not arts:
            return []
        if self._bm25 is None:
            self._art_toks = [_tokenize(f"{a.kind} {a.text}") for a in arts]
            self._bm25 = BM25Okapi(self._art_toks)
        return _bm25_rank(query, k, arts, self._art_toks, self._bm25)

    # --- telemetry -----------------------------------------------------------
    def list_signals(self) -> list[str]:
        return list(self._telemetry)

    def query_telemetry(self, signal: str, window=None, condition=None) -> TimeSeries:
        """Return a signal, optionally sliced by a time `window` and/or a `condition`.

        A condition-dependent signal (D3/D4) carries a parallel tag list in
        `props["conditions"]`; `condition=` keeps only the samples whose tag matches, so an
        intermittent fault visible only under one operating point can be isolated. Signals
        without condition tags ignore the filter (no spike case populates them yet — the
        full-build D3/D4 cases do; the wiring is here so the controller can request it)."""
        if signal not in self._telemetry:
            raise KeyError(f"unknown signal {signal!r}")
        s = self._telemetry[signal]
        tags = (s.spec or {}).get("conditions") if condition is not None else None
        pts = list(zip(s.t, s.v, tags or [None] * len(s.t)))
        if window is not None:
            lo, hi = window
            pts = [p for p in pts if lo <= p[0] <= hi]
        if condition is not None and tags is not None:
            pts = [p for p in pts if p[2] == condition]
        if window is None and condition is None:
            return s.model_copy(deep=True)
        return TimeSeries(signal=s.signal, t=[p[0] for p in pts],
                          v=[p[1] for p in pts], spec=s.spec)

    # --- logs & actions ------------------------------------------------------
    def read_logbook(self, window=None) -> list[Artifact]:
        return [a for a in self._case.artifacts
                if a.kind == "logbook_entry" and _in_window(a.timestamp, window)]

    def read_errors(self, window=None) -> list[Artifact]:
        return [a for a in self._case.artifacts
                if a.kind == "error" and _in_window(a.timestamp, window)]

    def read_diagnostic_actions(self) -> list[Artifact]:
        return [a for a in self._case.artifacts if a.kind == "diagnostic_action"]

    # --- graph navigation ----------------------------------------------------
    def traverse(self, node_id: str, edge_type: str, direction: str = "out") -> list[Node]:
        return self._case.graph.neighbors(node_id, edge_type=edge_type, direction=direction)

    # --- deterministic checks (§6.5) -----------------------------------------
    def run_check(self, name: str, args: dict | None = None) -> dict:
        args = args or {}
        if name not in self._CHECKS:
            raise ValueError(f"unknown check {name!r}; known: {sorted(self._CHECKS)}")
        return getattr(self, f"_run_{name}")(args)

    def _metric_signal(self, ref: str) -> str:
        """Resolve a metric/KPI node id or a raw signal name to a telemetry signal."""
        if ref in self._telemetry:
            return ref
        for n in self._case.graph.nodes:
            if n.id == ref and "signal" in n.props:
                return n.props["signal"]
        raise KeyError(f"cannot resolve signal for {ref!r}")

    def _run_config_diff(self, args: dict) -> dict:
        config_nodes = [n for n in self._case.graph.nodes if n.type == "config"]
        return checks.config_diff(config_nodes)

    def _run_spatial_intensity_check(self, args: dict) -> dict:
        regions = [s for sig, s in self._telemetry.items() if sig.startswith("region_intensity_")]
        return checks.spatial_intensity_check(regions)

    def _run_temp_correlation_check(self, args: dict) -> dict:
        a = self._metric_signal(args.get("signal_a", "mean_return_intensity"))
        b = self._metric_signal(args.get("signal_b", "laser_diode_temp_C"))
        return checks.temp_correlation_check(self._telemetry[a], self._telemetry[b])

    def _run_tec_load_check(self, args: dict) -> dict:
        sig = self._telemetry["tec_current_A"]
        limit = args.get("limit") or (sig.spec or {}).get("max")
        return checks.tec_load_check(sig, limit)

    def _run_channel_sanity_check(self, args: dict) -> dict:
        signal = self._metric_signal(args.get("signal", "detector_temp_C"))
        return checks.channel_sanity_check(self._telemetry[signal])

    def _run_onset_vs_event_check(self, args: dict) -> dict:
        signal = self._metric_signal(args.get("signal", "effective_max_range_m"))
        event_id = args.get("event_id", "log.reboot")
        event = self._artifacts.get(event_id)
        if event is None or event.timestamp is None:
            raise KeyError(f"no timed event {event_id!r}")
        return checks.onset_vs_event_check(self._telemetry[signal], event.timestamp,
                                           event_label=event.id)

    def _run_detector_health_check(self, args: dict) -> dict:
        dark = self._metric_signal(args.get("dark_signal", "dark_count_rate"))
        temp = self._metric_signal(args.get("temp_signal", "detector_temp_C"))
        return checks.detector_health_check(self._telemetry[dark], self._telemetry[temp])

    def _run_common_mode_check(self, args: dict) -> dict:
        names = args.get("signals") or ["laser_power_mW", "dark_count_rate",
                                        "mean_return_intensity"]
        series = [self._telemetry[self._metric_signal(n)] for n in names
                  if self._metric_signal(n) in self._telemetry]
        return checks.common_mode_check(series)


class BenchmarkEnvironment(Environment):
    """A QA benchmark item: the question (`symptom`) and a passage set (`search`).

    Lidar diagnostic methods raise `NotSupported`, exercising the controller's
    graceful-degradation path (the basis of M4.5 / M8 controller-core).
    """

    def __init__(self, question: str, passages: list[Artifact]):
        self._question = question
        self._passages = passages
        self._bm25 = None
        self._psg_toks: list[list[str]] = []

    def symptom(self) -> str:
        return self._question

    def search(self, query: str, k: int = 5) -> list[Artifact]:
        from rank_bm25 import BM25Okapi

        if not self._passages:
            return []
        if self._bm25 is None:
            self._psg_toks = [_tokenize(p.text) for p in self._passages]
            self._bm25 = BM25Okapi(self._psg_toks)
        return _bm25_rank(query, k, self._passages, self._psg_toks, self._bm25)
