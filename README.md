# Fathom

A diagnostic harness: one abductive LLM controller, run against a generated lidar
system-under-test and a QA benchmark through a single environment interface, measured
against strong baselines on diagnostic accuracy, evidence quality, token cost, and
calibrated abstention — with the controller's reasoning made visible as an Investigation
Graph. A portfolio piece on AI-native test architecture.

## Orientation

- **The build brief is authoritative.** Start at
  [`docs/handoff/00_README_for_coding_agent.md`](docs/handoff/00_README_for_coding_agent.md)
  for read-order and the non-negotiable rules; `docs/handoff/spike_spec.md` is the
  authoritative spec (it wins on any conflict) and `docs/handoff/spike_build_plan.md`
  sets milestone order.
- **Phase tracker:** [`docs/road.md`](docs/road.md) — a tracker over the brief, not a spec.
- **Design calls:** [`docs/decisions/`](docs/decisions/). **Deferred work:**
  [`docs/debt.md`](docs/debt.md).

## Working here

- Validation: `.venv/bin/pytest`
- Arm the pre-commit linter once on a fresh clone: `git config core.hooksPath .githooks`

Built from the CMS incubator (full profile). The repo is self-contained — nothing in it
depends on the incubator being reachable.

Takeaway capture/disclosure via [Monition](https://github.com/bolun/monition): `uv tool install --editable ~/projects/monition` (hooks fail open if absent).
