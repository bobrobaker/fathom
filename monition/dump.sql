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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
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
