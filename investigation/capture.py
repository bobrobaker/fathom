#!/usr/bin/env python
"""Capture / confirm harness for the controller investigation.

Runs the REAL controller (live LLM backend) on one case and dumps the full Investigation
Graph (hypotheses+log_odds, links, conflicts, evidence, trace, snapshots), the Answer, the
score, and the ground truth to JSON. Two uses:
  - audit substrate: see exactly what the controller did on a failing case
  - per-fix confirmation: re-run after a fix; assert the case now scores correctly

LIVE backend — drives `claude -p`. Serialize these; do not run concurrently with another eval
(subscription CLI collapses under concurrency). Usage:
    .venv/bin/python investigation/capture.py case5 [--budget 12] [--out investigation/cap_case5.json]
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                    format="%(asctime)s %(name)s %(message)s", datefmt="%H:%M:%S")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dh.controller.llm import MeteredBackend, get_backend  # noqa: E402
from dh.controller.loop import diagnose  # noqa: E402
from dh.environment import LidarEnvironment  # noqa: E402
from dh.eval.bespoke import score  # noqa: E402
from dh.generator import generate  # noqa: E402
from dh.generator.cases import CASES_BY_ID  # noqa: E402


def capture(case_id: str, budget: int) -> dict:
    spec = CASES_BY_ID[case_id]
    base = get_backend()
    if base is None:
        sys.exit("no LLM backend (install the claude CLI or set ANTHROPIC_API_KEY)")
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    env = LidarEnvironment(case)
    meter = MeteredBackend(base)
    ans = diagnose(env, backend=meter, budget=budget)
    sc = score(ans, case, solver="controller", tokens=meter.cost_tokens)
    gt = case.ground_truth
    ig = ans.final_graph
    return {
        "case_id": case_id, "fault": spec.fault, "salient_is_cause": spec.salient_is_cause,
        "ground_truth": {"root_cause": gt.root_cause, "causal_chain": gt.causal_chain,
                         "trigger": gt.trigger, "conflicts": gt.conflicts,
                         "load_bearing_evidence": gt.load_bearing_evidence},
        "answer": {"answer_type": ans.answer_type, "root_cause": ans.root_cause,
                   "causal_chain": ans.causal_chain, "cited_evidence": ans.cited_evidence,
                   "conflicts": ans.conflicts, "recommended_action": ans.recommended_action},
        "score": {"accuracy": sc.accuracy, "localization": sc.localization,
                  "evidence_f1": round(sc.evidence_f1, 3),
                  "conflict_handling": round(sc.conflict_handling, 3),
                  "trigger_discrimination": round(sc.trigger_discrimination, 3),
                  "abstention_calibration": sc.abstention_calibration,
                  "cost_tokens": meter.cost_tokens},
        "hypotheses": [{"id": h.id, "label": h.label, "log_odds": round(h.log_odds, 3),
                        "status": h.status, "node_ref": h.node_ref} for h in ig.hypotheses],
        "links": [{"evidence_id": l.evidence_id, "hypothesis_id": l.hypothesis_id,
                   "polarity": l.polarity, "weight": l.weight} for l in ig.links],
        "evidence": [{"id": e.id, "summary": e.summary, "source": e.source} for e in ig.evidence],
        "ig_conflicts": ig.conflicts,
        "trace": ig.trace,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("case", help="case id, e.g. case5")
    ap.add_argument("--budget", type=int, default=12)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    data = capture(a.case, a.budget)
    out = a.out or f"investigation/cap_{a.case}.json"
    pathlib.Path(out).write_text(json.dumps(data, indent=2))
    s = data["score"]
    print(f"{a.case}: acc={s['accuracy']} loc={s['localization']} evF1={s['evidence_f1']} "
          f"abst={s['abstention_calibration']} answer={data['answer']['answer_type']} "
          f"root={data['answer']['root_cause']} gold={data['ground_truth']['root_cause']} "
          f"cost={s['cost_tokens']}  -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
