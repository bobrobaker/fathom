<!-- monition-skill v0.2.0 sha256:a592104c14e84228d8dab53acb6aa87f88b7cbd57559763ee0e53200dada3b5c -->
---
name: mine-session
description: End-of-session mining pass — review this session for reusable lessons and house them in the Monition store with explicit triggers. Use when the user invokes /mine-session, says "mine this session" / "save the takeaways", or is wrapping up a session that hit gotchas worth keeping. NOT for mid-session one-offs the user wants codified immediately.
---

# mine-session

You are mining this session for takeaways. The store's semantics live in the
Monition store contract (`docs/contracts/takeaway-store.md` in the monition
repo) — read it before your first run in a session.

1. Review the session for lessons that are **reusable** (would recur) and
   **non-obvious** (a future session wouldn't rediscover them cheaply). Mistakes,
   gotchas, corrections, and confirmed preferences all qualify; routine work does not.
2. **Route each candidate before drafting** (routing v1 — from CMS
   `method/lesson-routing.md`; run in order, first decisive test wins; under
   uncertainty prefer the row — it is the only tier with an eval loop and it
   retires cleanly):
   - *Behavior test:* can't state it as "in situation S, do/avoid X" with a
     nameable S → not routable; leave it in session notes.
   - *Owning surface:* an artifact that already fires at S (a skill that runs
     then, a hook on that event, a prompt for that task, a linter on those files,
     or a governance surface named in this repo's CLAUDE.md) gets the edit
     directly — a parallel row duplicates its trigger with worse precision.
     Procedure changes always land here. Destinations with their own admission
     rules keep them.
   - *Describable trigger, no owner:* takeaway row (`monition add`) — also the
     default when evidence is thin.
   - *Every session:* a CLAUDE.md line, only if it earns being paid every
     session forever.
   - *Mechanical shadow:* checkable-and-unambiguous violations also get a linter
     check alongside whatever prose landed above; for semantic artifacts the
     host's eval suite plays that role — the lesson must pass it before consent
     closes.

   Every landing goes through the consent gate; the proposal names the deciding test.
3. For each candidate routed to a row, draft the full row: `kind`
   (gotcha/rule/preference), `trigger_kind` + `trigger_spec` (*when should this
   fire?* — the design decision; edit_path glob, session_start, or on_demand),
   `one_liner` (what gets injected — make it a trap-warning, not a description),
   `full_content` (the why + the workaround), `source` (session/commit).
4. **Show the proposed landings and get acceptance before applying** (consent gate).
5. Insert accepted rows (`monition add …`), then snapshot the store:
   `monition commit -m "mine: <session topic>"`.
6. If a takeaway is domain-free enough to apply beyond this repo, add it with
   `--mirror candidate` — the mirror-back sweep picks those up. It keeps firing
   locally while queued; mirror state never affects firing.
