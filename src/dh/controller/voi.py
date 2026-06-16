"""Value-of-information action scoring (spec §6.3).

Each candidate action carries an LLM-estimated *expected discrimination* (0–1: how
much it would move the hypothesis distribution) and a *fixed cost* by type. The
controller picks argmax(expected_discrimination / cost). A formal entropy-reduction
VOI is a full-build option; this LLM-scored ratio is the spike's tractable version.
"""

from __future__ import annotations

from dh import config
from dh.controller.llm import ActionProposal

_DEFAULT_COSTS = {"run_check": 1, "traverse": 1, "search": 2, "recommend_swap_test": 3}


def costs() -> dict:
    try:
        return {**_DEFAULT_COSTS, **config.voi_costs()}
    except Exception:  # noqa: BLE001 — config optional; fall back to spec defaults
        return dict(_DEFAULT_COSTS)


def voi(action: ActionProposal, cost_table: dict | None = None) -> float:
    cost_table = cost_table or costs()
    cost = max(cost_table.get(action.type, 1), 1)
    return action.expected_discrimination / cost


def select(actions: list[ActionProposal], cost_table: dict | None = None) -> ActionProposal | None:
    """The single highest-VOI action (None if there are no candidates)."""
    if not actions:
        return None
    cost_table = cost_table or costs()
    return max(actions, key=lambda a: voi(a, cost_table))
