CREATE DATABASE IF NOT EXISTS `monition`; USE `monition`; 
SET FOREIGN_KEY_CHECKS=0;
SET UNIQUE_CHECKS=0;
DROP TABLE IF EXISTS `decisions`;
CREATE TABLE `decisions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `takeaway_id` int NOT NULL,
  `session_id` varchar(64),
  `decided_at` datetime NOT NULL,
  `decision` enum('fire','suppress') NOT NULL,
  `evidence_count` int NOT NULL,
  `cold_start` tinyint(1) NOT NULL DEFAULT '0',
  `ev_score` decimal(5,4),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
INSERT INTO `decisions` (`id`,`takeaway_id`,`session_id`,`decided_at`,`decision`,`evidence_count`,`cold_start`,`ev_score`) VALUES (1,2,'e785c7f3-5a00-4e94-b251-16efc780bd77','2026-06-16 02:42:55','fire',0,1,NULL), (2,4,'e785c7f3-5a00-4e94-b251-16efc780bd77','2026-06-16 03:11:24','fire',0,1,NULL);
DROP TABLE IF EXISTS `firings`;
CREATE TABLE `firings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `takeaway_id` int NOT NULL,
  `fired_at` datetime NOT NULL,
  `session_id` varchar(64),
  `trigger_kind` varchar(32),
  `trigger_context` varchar(512),
  `outcome` enum('helpful','noise'),
  `git_sha` varchar(40),
  `git_dirty` tinyint(1),
  `model` varchar(64),
  `monition_version` varchar(32),
  `situation` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
INSERT INTO `firings` (`id`,`takeaway_id`,`fired_at`,`session_id`,`trigger_kind`,`trigger_context`,`outcome`,`git_sha`,`git_dirty`,`model`,`monition_version`,`situation`) VALUES (1,2,'2026-06-16 02:42:55','e785c7f3-5a00-4e94-b251-16efc780bd77','on_demand','/goal \"Begin Fathom Phase 1 / spike M0: scaffold pyproject.toml + config.yaml + src/dh/schemas.py from \n  spike_spec.md §3; gate on test_schemas.\" And then implement that phase until complete, you run',NULL,'295d284bebb614f26c3be74c9f612fd5785ebe80',0,NULL,'0.1.0','/goal \"Begin Fathom Phase 1 / spike M0: scaffold pyproject.toml + config.yaml + src/dh/schemas.py from \n  spike_spec.md §3; gate on test_schemas.\" And then implement that phase until complete, you run out of context, or you genuinely need to ask me for somsething'), (2,4,'2026-06-16 03:11:24','e785c7f3-5a00-4e94-b251-16efc780bd77','edit_path','src/dh/environment.py',NULL,'295d284bebb614f26c3be74c9f612fd5785ebe80',1,'claude-opus-4-8','0.1.0','\"\"\"The environment interface (spec §4) — the controller\'s only window on a case.\n\nOne `Environment` ABC fronts two worlds: `LidarEnvironment` (the generated SUT, full\ndiagnostic toolset) and `BenchmarkEnvironment` (a QA passage set, `symptom`+`search`\nonly). The controller is written once against this interface and degrades gracefully\nwhen a method is unavailable (it discovers capabilities via `capabilities()` or by\ncatching `NotSupported`).\n\n**Non-negotiable #1 (ground truth is eval-only):** `LidarEnvironment` holds the `Case`\nprivately and exposes *nothing* that returns `Case.ground_truth`. The eval reads ground\ntruth from the `Case` directly; it never travels through this boundary.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport re\nfrom abc import ABC, abstractmethod\n\nfrom dh import checks\nfrom dh.schemas import Artifact, Case, Node, TimeSeries\n\n_TOKEN = re.compile(r\"\\w+\")\n\n\nclass NotSupported(RuntimeError):\n    \"\"\"Raised when a method isn\'t available in this environment (e.g. lidar tools on QA).\"\"\"\n\n\ndef _tokenize(text: str) -> list[str]:\n    return _TOKEN.findall(text.lower())\n\n\ndef _in_window(ts: float | None, window: tuple[float, float] | None) -> bool:\n    if window is None:\n        return True\n    if ts is None:\n        return False\n    lo, hi = window\n    return lo <= ts <= hi\n\n\nclass Environment(ABC):\n    @abstractmethod\n    def symptom(self) -> str: ...\n\n    @abstractmethod\n    def search(self, query: str, k: int = 5) -> list[Artifact]: ...\n\n    def capabilities(self) -> set[str]:\n        \"\"\"Method names this environment supports (the controller probes this).\"\"\"\n        return {\"symptom\", \"search\"}\n\n    # --- lidar-only methods (BenchmarkEnvironment raises NotSupported) --------\n    def query_telemetry(self, signal: str, window=None, condition=None) -> TimeSeries:\n        raise NotSupported(\"query_telemetry\")\n\n    def run_check(self, name: str, args: dict) -> dict:\n        raise NotSupported(\"run_check\")\n\n    def read_logbook(self, window=None) -> list[Artifact]:\n        raise NotSupported(\"read_logbook\")\n\n    def read_errors(self, window=None) -> list[Artifact]:\n        raise NotSupported(\"read_errors\")\n\n    def read_diagnostic_actions(self) -> list[Artifact]:\n        raise NotSupported(\"read_diagnostic_actions\")\n\n    def traverse(self, node_id: str, edge_type: str, direction: str = \"out\") -> list[Node]:\n        raise NotSupported(\"traverse\")\n\n    def list_signals(self) -> list[str]:\n        raise NotSupported(\"list_signals\")\n\n\nclass LidarEnvironment(Environment):\n    \"\"\"Wraps one generated lidar `Case`. The full diagnostic toolset (spec §4).\"\"\"\n\n    _CHECKS = {\n        \"config_diff\", \"spatial_intensity_check\", \"temp_correlation_check\",\n        \"tec_load_check\", \"channel_sanity_check\", \"onset_vs_event_check\",\n    }\n\n    def __init__(self, case: Case):\n        self._case = case  # PRIVATE — ground truth must not leak past this boundary\n        self._telemetry = {s.signal: s for s in case.telemetry}\n        self._artifacts = {a.id: a for a in case.artifacts}\n        self._bm25 = None  # lazily built (rank_bm25)\n\n    # --- discovery -----------------------------------------------------------\n    def capabilities(self) -> set[str]:\n        return {\n            \"symptom\", \"search\", \"query_telemetry\", \"run_check\", \"read_logbook\",\n            \"read_errors\", \"read_diagnostic_actions\", \"traverse\", \"list_signals\",\n        }\n\n    def symptom(self) -> str:\n        for n in self._case.graph.nodes:\n            if n.type == \"KPI\" and \"symptom\" in n.props:\n                return n.props[\"symptom\"]\n        return \"A performance KPI has degraded. Diagnose the root cause.\"\n\n    # --- retrieval -----------------------------------------------------------\n    def search(self, query: str, k: int = 5) -> list[Artifact]:\n        from rank_bm25 import BM25Okapi\n\n        arts = self._case.artifacts\n        if not arts:\n            return []\n        if self._bm25 is None:\n            self._bm25 = BM25Okapi([_tokenize(f\"{a.kind} {a.text}\") fo');
DROP TABLE IF EXISTS `takeaways`;
CREATE TABLE `takeaways` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `kind` enum('gotcha','rule','preference') NOT NULL,
  `scope` varchar(255),
  `trigger_kind` enum('edit_path','session_start','on_demand') NOT NULL,
  `trigger_spec` varchar(255),
  `one_liner` varchar(500) NOT NULL,
  `full_content` text,
  `source` varchar(255),
  `status` enum('active','retired') NOT NULL DEFAULT '1',
  `mirror` enum('none','candidate','mirrored') NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
INSERT INTO `takeaways` (`id`,`created`,`kind`,`scope`,`trigger_kind`,`trigger_spec`,`one_liner`,`full_content`,`source`,`status`,`mirror`) VALUES (1,'2026-06-16 02:29:17','gotcha',NULL,'edit_path','.claude/*','Hook commands with relative paths (python3 tools/x.py) break when the session shell cwd drifts — anchor to $CLAUDE_PROJECT_DIR in settings.json hook commands.',NULL,NULL,'active','none'), (2,'2026-06-16 02:29:18','rule',NULL,'on_demand','handoff, resume, pick up','A handoff\'s State section is a snapshot, not ground truth — verify every \"not done yet\" claim against git log before executing; handoffs go stale within a day.',NULL,NULL,'active','none'), (3,'2026-06-16 02:29:18','gotcha',NULL,'on_demand','git --since, --until, commits since, approxidate, git log date','Computing a git log --since/--until boundary? A bare date fills its time-of-day from the current wall clock (git approxidate) — same-day commits drift in/out; pass an explicit datetime (<date> 00:00:00).','Approxidate fills a bare date\'s missing time from \"now,\" so --since <date> means \"<date> at the current time,\" not midnight. It passes unit tests written with arbitrary dates and only bites at the real same-day boundary — test there.',NULL,'active','none'), (4,'2026-06-16 02:29:18','rule',NULL,'edit_path','src/dh/controller/*, src/dh/environment.py, src/dh/baselines.py','Case.ground_truth is eval-only — it must never enter the controller\'s (or a baseline\'s) context; enforce at the environment boundary, which never exposes it.','The entire eval is invalid if ground truth leaks into reasoning. The environment is the typed boundary: it exposes symptom/search/checks/traverse but never Case.ground_truth — the controller and all baselines see only what the environment surfaces; only the eval reads ground truth. Audit any new environment method or prompt builder for accidental exposure. (spike_spec §0 item 1, §3.2; 00_README non-negotiable #1.)',NULL,'active','none');
