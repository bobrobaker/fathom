#!/usr/bin/env python3
"""Assemble the hostable Investigation-Graph showpiece (fathom_visualizer_spec.md §5).

Runs the controller live on a *curated* case set chosen to show range — the TEC cross-subsystem
case, the honest abstention, and a buried-evidence (navigation) case — exports each run's replay
bundle (stepped IG + per-step trace + the eval row), and writes the deployable static site to
`viewer_site/`. Replay-only: the site plays back these recorded runs, it makes no model calls.

    .venv/bin/python tools/build_viewer_site.py                 # default curated set
    .venv/bin/python tools/build_viewer_site.py --cases case1 case5 case6 --budget 8
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dh.controller.llm import MeteredBackend, get_backend  # noqa: E402
from dh.controller.loop import diagnose  # noqa: E402
from dh.environment import LidarEnvironment  # noqa: E402
from dh.eval.bespoke import score  # noqa: E402
from dh.generator import generate  # noqa: E402
from dh.generator.cases import CASES_BY_ID  # noqa: E402
from dh.viewer.export import build_site, case_bundle  # noqa: E402

CURATED = ["case1", "case5", "case6"]  # TEC showcase · honest abstention · buried evidence
TITLES = {
    "case1": "TEC degradation", "case5": "No clean cause (abstain)",
    "case6": "Detector bias (buried)", "case7": "TEC tie-breaker",
    "case8": "Common-mode power", "case2": "Laser aging", "case3": "Window contamination",
    "case4": "Calibration drift",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", nargs="+", default=CURATED)
    ap.add_argument("--budget", type=int, default=8)
    ap.add_argument("--out", default="viewer_site")
    args = ap.parse_args()

    base = get_backend()
    if base is None:
        sys.exit("no LLM backend (set ANTHROPIC_API_KEY or install the claude CLI)")

    bundles = []
    for cid in args.cases:
        spec = CASES_BY_ID[cid]
        case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
        meter = MeteredBackend(base)
        print(f"# running {cid} ({spec.fault}) ...", file=sys.stderr)
        ans = diagnose(LidarEnvironment(case), backend=meter, budget=args.budget)
        sc = score(ans, case, solver="controller", tokens=meter.cost_tokens)
        gt = case.ground_truth  # eval-side annotations for rendering only (never controller context)
        bundles.append(case_bundle(
            ans.final_graph, case_id=cid, title=TITLES.get(cid, cid), caption=spec.purpose,
            trigger=gt.trigger, root_cause=gt.root_cause,
            answer={"answer_type": ans.answer_type, "root_cause": ans.root_cause,
                    "cited_evidence": ans.cited_evidence, "conflicts": ans.conflicts},
            eval_row={"accuracy": sc.accuracy, "localization": sc.localization,
                      "trigger_discrimination": sc.trigger_discrimination,
                      "conflict_handling": sc.conflict_handling, "evidence_f1": round(sc.evidence_f1, 2),
                      "tokens": sc.tokens}))
        print(f"  {cid}: {ans.answer_type} root={ans.root_cause} acc={sc.accuracy:.0f} "
              f"trig={sc.trigger_discrimination:.0f} tok={sc.tokens}", file=sys.stderr)

    out = pathlib.Path(__file__).resolve().parent.parent / args.out
    index = build_site(bundles, out)
    print(f"\n# wrote {len(bundles)} bundles -> {index}", file=sys.stderr)


if __name__ == "__main__":
    main()
