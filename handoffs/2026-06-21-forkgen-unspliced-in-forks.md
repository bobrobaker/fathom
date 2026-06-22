# Handoff — `bootstrap.sh --update` leaves forkgen sentinels unspliced in forks

**Date:** 2026-06-21 · **Origin:** fathom `/eos` mine (session 70d6c319) · **Fix belongs in:** CMS (machinery bug, not a fathom bug)

## The finding

Running `/eos` → `mine-session` in fathom, the loaded skill was the **CMS-canonical**
`mine-session/SKILL.md` (re-vendored into fathom earlier this session by
`./bootstrap.sh --update`). It still contained CMS's `<!-- forkgen:strip -->` /
`<!-- forkgen:swap step6 -->` sentinels **and CMS's upstream-only step 6** ("CMS is the
upstream, so promote, don't queue"), plus the copied `mine-session.fork-overrides.md`.

Nothing ran the **fork-side splice**. So a fork's `mine-session` carries CMS's step 6
verbatim instead of the fork variant ("queue domain-free lessons to
`upstream-candidates.md`"). The forkgen regen that does the strip/swap lives in
**monition's `tools/regen_from_cms.py`** (per CMS decision
`2026-06-21-generate-monition-mine-session-from-cms.md`) — it is NOT invoked by
`bootstrap.sh --update`, which just `cp -R`s `.claude/skills/` wholesale.

## Why it matters

A fork that mines a transferable lesson will be told to **promote it directly** (CMS's
behavior) rather than **queue it to `upstream-candidates.md`** (the correct fork→upstream
direction). Domain-free lessons get mis-routed — exactly the queue mechanism explained to
the user this session. Silent: the skill loads and reads fine; the wrong branch only bites
at step 6 of a mine.

## Options to fix (CMS-side, decide when consumed)

1. **Splice on re-vendor:** `bootstrap.sh --update` (and initial bootstrap) runs the
   forkgen strip/swap when copying `.claude/skills/`, using the copied
   `*.fork-overrides.md` — so a fork gets the spliced fork variant, not the raw CMS body.
2. **Ship pre-spliced:** `--update` lays down a fork-tailored skill rather than the raw
   canonical one (the canonical-with-sentinels stays CMS-internal).
3. **At minimum:** have `--update` strip the `forkgen:*` sentinels + drop the CMS-only
   step 6 block in forks, even if it can't do the full swap.

Mechanically mirrors the same managed/fork-local seam the craft_reminder confer just
resolved — the re-vendor needs a fork-aware transform step, not a verbatim copy.

## Pointers
- Resolved craft_reminder confer (related seam reasoning):
  `~/projects/brain2/handoffs/archive/2026-06-21-confer-craft-reminder-seam-rules-merge.md`
- CMS regen decision: CMS `docs/decisions/2026-06-21-generate-monition-mine-session-from-cms.md`
- Symptom file in fathom: `.claude/skills/mine-session/SKILL.md` (has the unspliced sentinels)
