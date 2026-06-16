#!/usr/bin/env python3
"""Run the bespoke eval live and render the uplift report (spec §8.1, build plan M6/M7).

Runs `controller` + the three baselines on one or more authored cases over N runs
(variance, §9 S1), scores each with the rubric, and writes the two-family report.

    .venv/bin/python tools/run_eval.py --runs 3 --budget 8 --case case1
    .venv/bin/python tools/run_eval.py --all            # every authored case

Uses the live LLM backend (CLI by default; Anthropic if keyed). `shortcut` is
deterministic and run once. Token cost is metered (approx) per solver.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dh import baselines  # noqa: E402
from dh.controller.llm import MeteredBackend, get_backend  # noqa: E402
from dh.controller.loop import diagnose  # noqa: E402
from dh.environment import LidarEnvironment  # noqa: E402
from dh.eval import report  # noqa: E402
from dh.eval.bespoke import score  # noqa: E402
from dh.generator import generate  # noqa: E402
from dh.generator.cases import CASES_BY_ID, authored_cases  # noqa: E402


def _run_case(spec, runs: int, budget: int) -> dict[str, list]:
    base = get_backend()
    if base is None:
        sys.exit("no LLM backend (set ANTHROPIC_API_KEY or install the claude CLI)")
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    results: dict[str, list] = {s: [] for s in ("controller", "bare_llm", "react", "shortcut")}

    # deterministic baseline — run once
    results["shortcut"].append(score(baselines.shortcut(LidarEnvironment(case)),
                                     case, solver="shortcut", tokens=0))

    for r in range(runs):
        for name, fn in (("controller", None), ("bare_llm", baselines.bare_llm),
                         ("react", baselines.react)):
            env = LidarEnvironment(case)
            meter = MeteredBackend(base)
            try:
                ans = diagnose(env, backend=meter, budget=budget) if fn is None \
                    else fn(env, backend=meter)
            except Exception as e:  # noqa: BLE001 — a solver failure shouldn't kill the eval
                print(f"  ! {name} run {r} failed: {e}", file=sys.stderr)
                continue
            results[name].append(score(ans, case, solver=name, tokens=meter.total_tokens))
            print(f"  {spec.id} {name} run {r}: acc={results[name][-1].accuracy} "
                  f"trig={results[name][-1].trigger_discrimination} "
                  f"conf={results[name][-1].conflict_handling} tok={meter.total_tokens}",
                  file=sys.stderr)
    return case.id, results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--budget", type=int, default=8)
    ap.add_argument("--case", default="case1")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    specs = authored_cases() if args.all else [CASES_BY_ID[args.case]]
    out_dir = pathlib.Path(__file__).resolve().parent.parent / "reports"
    out_dir.mkdir(exist_ok=True)

    docs = []
    for spec in specs:
        print(f"# running {spec.id} ({spec.fault}) ...", file=sys.stderr)
        case_id, results = _run_case(spec, args.runs, args.budget)
        md = report.render(results, case_id=case_id)
        docs.append(md)
        print("\n" + md)

    out = pathlib.Path(args.out) if args.out else out_dir / "bespoke.md"
    out.write_text("\n\n".join(docs))
    print(f"\n# wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
