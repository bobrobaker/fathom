# road.md tracks the brief; the brief is authoritative

**Date:** 2026-06-16
**Status:** accepted

## Context

Fathom was instantiated from a complete external build-brief packet (the eight docs now
in `docs/handoff/`), not from an interview. The packet is internally cross-referenced
and authoritative: `00_README_for_coding_agent.md` fixes a read-order and the
non-negotiable rules, `spike_spec.md` is the executable spec (contracts, components,
acceptance), `spike_build_plan.md` fixes milestone order, and `full_build_spec.md` is
the spike-conditioned destination. The incubator's full profile also ships a
`docs/road.md`. Two documents could plausibly own "the plan."

## Decision

1. **`docs/road.md` is a thin phase *tracker*, not a plan.** It records phase status and
   a milestone checklist and *points at* the governing brief sections. It must not
   duplicate the brief's contracts, milestones, or acceptance criteria.
2. **The brief in `docs/handoff/` is authoritative.** On any conflict, `spike_spec.md`
   wins (per `00_README` authority order), then `spike_build_plan.md` for order.
3. **The data contract lives in the brief and becomes code, not a third copy.** The
   pydantic schemas in `spike_spec.md` §3 are the data contract; they land as
   `src/dh/schemas.py` — the single source of truth (build plan M0). We deliberately do
   **not** mirror them into `docs/contracts/`: the spec already houses them
   authoritatively and `schemas.py` is the runtime single-source, so a markdown copy
   would only drift.

## Why

The usual instantiation reflex is to absorb a plan into `road.md`. When the user hands a
complete, cross-referenced packet, copying it in creates two sources that drift — and
the brief, being the thing the user authored and will keep editing, must stay the one
that wins. Tracking-plus-pointing keeps a single source while still giving sessions the
phase/status/next-work view the roadmap is for. (Pattern carried from the CMS
`/instantiate` feedback log, 2026-06-15: when the user hands a full plan, confirm the
mapping and generate; road.md becomes a tracker over the brief.)

## Consequences

- A session edits the brief to change the plan; `road.md` only to move phase/milestone
  status. The `craft_reminder` hook reinforces this on edits under `docs/`.
- If the spike's findings revise the full build (expected, by the brief's own terms),
  that revision lands in `full_build_spec.md`; `road.md`'s sketched Phases 2–4 are
  refreshed to match, not treated as the source.
