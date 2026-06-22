#!/usr/bin/env python3
"""Run the bespoke eval live and render the uplift report (spec §8.1, build plan M6/M7).

Runs `controller` + the three baselines on one or more authored cases over N runs
(variance, §9 S1), scores each with the rubric, and writes the two-family report.

    .venv/bin/python tools/run_eval.py --runs 3 --budget 8 --case case1
    .venv/bin/python tools/run_eval.py --all            # every authored case

Uses the live LLM backend (CLI by default; Anthropic if keyed). `shortcut` is
deterministic and run once. Token cost is metered from the CLI's real `usage` per solver.

RUN PROTOCOL (read before an n=3 run — the settings are correct automatically, the *procedure*
is what bites):
  - **Backend flags are baked into `CLIBackend` (src/dh/controller/llm.py): `--tools ""`
    (deletes the ~14-17k built-in tool defs) + `--setting-sources project,local` (drops the
    global ~/.claude/CLAUDE.md), on subscription auth, no API key.** Nothing to configure here;
    `get_backend()` returns that backend. See docs/decisions/2026-06-22-claude-cli-prompt-cache.md.
  - **Close other interactive `claude` sessions first.** The subscription `claude -p` backend
    serializes under concurrent `claude` sessions — a controller run that takes seconds on a
    clear machine takes many minutes alongside a live session (monition t61).
  - **Run per-case, sequentially, with `--out`** so a mid-run failure doesn't lose prior cases
    and doesn't clobber the n=1 deliverable (`reports/bespoke.md`):
        for c in case1 case2 ... case8; do
          .venv/bin/python tools/run_eval.py --runs 3 --case $c --out reports/n3_$c.md
        done
  - Per-call cost is now scaffolding-free (~hundreds of input tokens/call); `cost_tokens` is
    output-dominated. n=3 over 8 cases is affordable but still ~hours of wall-clock if a live
    session is competing — prefer an idle window.
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
from dh.viewer.export import case_bundle  # noqa: E402

# captured during the run so the showpiece reuses real runs (no extra live calls)
_VIEWER_BUNDLES: list[dict] = []
_VIEWER_TITLES = {"case1": "TEC degradation", "case5": "No clean cause (abstain)",
                  "case6": "Detector bias (buried)", "case7": "TEC tie-breaker",
                  "case8": "Common-mode power", "case2": "Laser aging",
                  "case3": "Window contamination", "case4": "Calibration drift"}


def _run_case(spec, runs: int, budget: int) -> dict[str, list]:
    base = get_backend()
    if base is None:
        sys.exit("no LLM backend (set ANTHROPIC_API_KEY or install the claude CLI)")
    case = generate(spec.fault, list(spec.mechanisms), seed=spec.seed)
    results: dict[str, list] = {s: [] for s in ("controller", "bare_llm", "react", "shortcut")}

    # deterministic baseline — run once (no per-run loop, so trace it here for visibility)
    sc_short = score(baselines.shortcut(LidarEnvironment(case)),
                     case, solver="shortcut", tokens=0)
    results["shortcut"].append(sc_short)
    print(f"  {spec.id} shortcut (det.): acc={sc_short.accuracy} loc={sc_short.localization} "
          f"trig={sc_short.trigger_discrimination} conf={sc_short.conflict_handling} "
          f"evF1={sc_short.evidence_f1:.2f} tok=0", file=sys.stderr)

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
            sc = score(ans, case, solver=name, tokens=meter.cost_tokens)
            results[name].append(sc)
            print(f"  {spec.id} {name} run {r}: acc={sc.accuracy} loc={sc.localization} "
                  f"trig={sc.trigger_discrimination} conf={sc.conflict_handling} "
                  f"evF1={sc.evidence_f1:.2f} cost_tok={meter.cost_tokens} "
                  f"(raw {meter.total_tokens}, cached {meter.cached_tokens})", file=sys.stderr)
            if name == "controller" and r == 0:  # first controller run → showpiece bundle
                gt = case.ground_truth
                _VIEWER_BUNDLES.append(case_bundle(
                    ans.final_graph, case_id=spec.id, title=_VIEWER_TITLES.get(spec.id, spec.id),
                    caption=spec.purpose, trigger=gt.trigger, root_cause=gt.root_cause,
                    answer={"answer_type": ans.answer_type, "root_cause": ans.root_cause,
                            "cited_evidence": ans.cited_evidence, "conflicts": ans.conflicts},
                    eval_row={"accuracy": sc.accuracy, "localization": sc.localization,
                              "trigger_discrimination": sc.trigger_discrimination,
                              "conflict_handling": sc.conflict_handling,
                              "evidence_f1": round(sc.evidence_f1, 2), "tokens": sc.tokens}))
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

    # assemble the showpiece from the controller runs we just recorded (curated subset, or all)
    if _VIEWER_BUNDLES:
        from dh.viewer.export import build_site
        curated = [b for b in _VIEWER_BUNDLES if b["case_id"] in ("case1", "case5", "case6")] \
            or _VIEWER_BUNDLES
        site = pathlib.Path(__file__).resolve().parent.parent / "viewer_site"
        build_site(curated, site)
        print(f"# wrote showpiece ({len(curated)} cases) -> {site / 'index.html'}", file=sys.stderr)


if __name__ == "__main__":
    main()
