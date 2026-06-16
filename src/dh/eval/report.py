"""Uplift-table renderer (spec §8.1, build plan M6/M7).

Aggregates per-solver scores across runs (mean ± std for the ≥3-run variance, §9 S1)
and renders the bespoke report grouped into the two families — accuracy and capability —
reported separately, with the headline capability-family uplift of `controller` over
`bare_llm` and `shortcut`, accuracy reported honestly alongside, win or tie (§8.1).
"""

from __future__ import annotations

import statistics as st

from dh.eval.bespoke import ACCURACY_FAMILY, CAPABILITY_FAMILY, CaseScore

_SOLVER_ORDER = ["controller", "bare_llm", "react", "shortcut"]


def summarize(scores: list[CaseScore]) -> dict[str, tuple[float, float]]:
    """metric → (mean, stdev) across runs (stdev 0 for a single run)."""
    metrics = CAPABILITY_FAMILY + ACCURACY_FAMILY + ["tokens"]
    out: dict[str, tuple[float, float]] = {}
    for m in metrics:
        vals = [float(getattr(s, m)) for s in scores]
        mean = st.mean(vals) if vals else 0.0
        sd = st.pstdev(vals) if len(vals) > 1 else 0.0
        out[m] = (mean, sd)
    return out


def _cell(stat: tuple[float, float], is_tokens: bool = False) -> str:
    mean, sd = stat
    if is_tokens:
        base = f"{mean:.0f}"
        return base if sd == 0 else f"{base}±{sd:.0f}"
    base = f"{mean:.2f}"
    return base if sd == 0 else f"{base}±{sd:.2f}"


def _capability_mean(summary: dict[str, tuple[float, float]]) -> float:
    return st.mean([summary[m][0] for m in CAPABILITY_FAMILY])


def render(results: dict[str, list[CaseScore]], case_id: str = "") -> str:
    """Render the bespoke report (markdown) for one case across solvers/runs."""
    solvers = [s for s in _SOLVER_ORDER if s in results] + \
              [s for s in results if s not in _SOLVER_ORDER]
    summaries = {s: summarize(results[s]) for s in solvers}
    n_runs = max((len(v) for v in results.values()), default=0)

    def table(metrics: list[str], is_tokens: bool = False) -> list[str]:
        head = "| metric | " + " | ".join(solvers) + " |"
        sep = "|" + "---|" * (len(solvers) + 1)
        rows = [head, sep]
        for m in metrics:
            cells = " | ".join(_cell(summaries[s][m], is_tokens) for s in solvers)
            rows.append(f"| {m} | {cells} |")
        return rows

    out = [f"## Bespoke eval — {case_id or 'case'} (n={n_runs} run(s))", "",
           "### Accuracy family", *table(ACCURACY_FAMILY), "",
           "### Capability family", *table(CAPABILITY_FAMILY), "",
           "### Cost", *table(["tokens"], is_tokens=True), ""]

    cap = {s: _capability_mean(summaries[s]) for s in solvers}
    out.append("### Headline")
    if "controller" in cap:
        for baseline in ("bare_llm", "react", "shortcut"):
            if baseline in cap:
                delta = cap["controller"] - cap[baseline]
                sign = "+" if delta >= 0 else ""
                out.append(f"- capability-family mean: controller {cap['controller']:.2f} "
                           f"vs {baseline} {cap[baseline]:.2f} ({sign}{delta:.2f})")
    out.append("")
    return "\n".join(out)
