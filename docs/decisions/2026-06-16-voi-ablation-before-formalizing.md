# Run a VOI ablation before building the formal entropy-reduction VOI

**Date:** 2026-06-16 · **Status:** accepted · **Milestones:** Phase B (full harness)

## Decision

Before building the formal entropy-reduction VOI named in `spike_spec.md` §6.3 /
`full_build_spec.md` §4, **run an ablation** measuring whether VOI scoring buys anything at
spike scale. Compare action-selection strategies: (1) the current **LLM-scalar**
`expected_discrimination`, (2) **entropy reduction over the LLM's predicted outcome
distributions** (no per-hypothesis simulator), (3) **random action order**, (4)
**playbook-fixed** order. Build the formal VOI only if the ablation shows scoring moves the
metrics.

## Why

- The current VOI is an **uncalibrated LLM scalar**: `ActionProposal.expected_discrimination`
  defaults to 0.5, LLM-estimated (`schemas.py:216`, `llm.py:294`); cost is a hardcoded type
  lookup (`config.yaml:voi_costs`); nothing in the eval scores VOI calibration.
- At spike scale (5 hypotheses, ~6 cheap checks) the optimal next action is often obvious —
  the playbook even names it — so the formal machinery may not move the numbers. The spec's
  "alongside, as an option" hedge was the right instinct: measure before building.
- If the ablation shows scoring matters, the **intermediate upgrade** is entropy reduction
  over predicted outcome distributions — not a per-hypothesis simulator.

## Next step

`tools/ablate_voi.py` (or a flag on `tools/run_eval.py`) implementing the four-way
comparison. Blocks the formal-VOI build decision (Phase B). See `docs/debt.md`.
