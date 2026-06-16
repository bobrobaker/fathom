---
name: codify
description: Turn a one-off correction or agreed convention into durable governance — a CLAUDE.md line, a doc rule, a prompt edit — so it sticks across sessions. Use when the user invokes /codify, says "make this a rule" / "remember this as a convention", or when a reusable rule or anti-pattern surfaces mid-conversation. Always proposes the change and gets explicit acceptance before writing.
---

# codify

You are turning a correction or convention into a durable rule. Codifying changes
future behavior, so the gate is absolute: **never write before explicit acceptance.**

1. Route the rule, in order — the first decisive test wins:
   - **Owning surface:** an artifact that already fires at the right moment (a
     skill that runs then, a hook on that event, a prompt for that task, a linter
     on those files, or one of the project's own governance surfaces named in
     CLAUDE.md §Map) gets the edit — it's already a trigger with a payload, and a
     parallel lesson would duplicate its trigger with worse precision. Procedure
     changes always land here. A destination with its own admission rules (caps,
     evidence gates, eval suites) keeps them — routing never bypasses the
     surface's own gate.
   - **Describable trigger, no owner:** a takeaway block in `lessons.md` (path
     footprint or session start; format documented in that file). Also the default
     when evidence is thin — blocks are reversible, prose is forever.
   - **Every session:** a CLAUDE.md line, only if it earns being paid for every
     session forever.
   - **File-local:** a one-line gotcha next to the code it protects.

   Then draft the **smallest durable edit** that captures the rule at that
   destination.
2. Show the proposed change verbatim — exact text, exact destination — and say what
   behavior it changes.
3. Only after the user accepts: apply it, keeping the *why* next to the rule in one
   line.
4. If the rule is mechanical (checkable by code), propose a linter check instead of or
   alongside the prose — each check's comment names the rule it shadows.
5. **Upstream-candidate test.** After the rule lands, strip this project's domain from
   it. If what survives would apply to *any* project, append one line to
   `handoffs/upstream-candidates.md` (`YYYY-MM-DD | rule | origin`) and tell the user
   it's queued for the upstream template's next sweep. Domain-specific rules stay
   local; never skip the append for a rule that passes — the queue is how lessons
   reach the template at all.
