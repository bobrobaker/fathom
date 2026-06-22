# LLM backend: prompt/tool-stripped `claude` CLI, with a dormant SDK path

**Date:** 2026-06-16 · **Status:** accepted · **Milestone:** M3

> **CLIBackend argv superseded (2026-06-22).** The `--allowed-tools "" --output-format text` invocation
> shown below is stale: the current backend uses **`--tools "" --setting-sources project,local
> --output-format json`** (and parses real `usage`). `--allowed-tools ""` strips tool *permissions*,
> not *definitions* — `--tools ""` deletes the ~21k scaffolding prefix outright. Authoritative:
> `docs/decisions/2026-06-22-claude-cli-prompt-cache.md` + the `CLIBackend`/`MeteredBackend` docstrings.
> The rest of this record (three-backend structure, dormant SDK path, scratch cwd, subscription auth)
> still holds.

## Decision

The controller and baselines reach the model through one `complete(prompt, system) -> text`
interface (`src/dh/controller/llm.py`) with three backends, selected by `get_backend()`:

1. **`AnthropicBackend`** — the Messages API via the `anthropic` SDK. Used only when
   `ANTHROPIC_API_KEY` is set. Written now, **dormant** (no key in this environment yet).
2. **`CLIBackend`** — a headless `claude -p <prompt> --system-prompt <role>
   --allowed-tools "" --output-format text --model <id>` subprocess, run from a scratch
   temp cwd. This is the **default** path and what the spike actually runs on.
3. **`None` (stub)** — when neither is available, callers fall back to a deterministic
   scripted backend. `DH_BACKEND=stub` forces this so the test suite never shells out.

## Why

- **No API key is available**, but a logged-in `claude` CLI is. The CLI carries the
  subscription **auth token**, so it can complete prompts without a key.
- **Prompt-replaced, not bare.** `--allowed-tools ""` removes tool *permissions* (note: it does
  NOT strip the tool *definitions* from context — measured 2026-06-22); `--system-prompt`
  *replaces* Claude Code's default system prompt with our small role-bounded prompt (spec §6.6);
  running from a scratch cwd keeps the project's `CLAUDE.md`/context out. A "bare" mode that also
  strips auth would defeat the purpose — we deliberately keep auth. **The scratch cwd must be a
  single STABLE path reused across calls, not a fresh temp dir per call** — see
  `2026-06-22-claude-cli-prompt-cache.md` (a fresh cwd busts the prompt cache, ~2.7x cost).
- **Determinism for the gate.** `test_controller_tec` and `test_llm` drive a
  `ScriptedBackend` (canned structured outputs), so the loop logic is verified
  reproducibly. Live-model quality is measured separately by the eval (M6+), where
  nondeterminism is reported as variance over ≥3 runs (spec §9 S1).
- **One swap to go live with a key.** When a key appears, `get_backend()` prefers
  `AnthropicBackend` automatically; nothing else changes.

Verified working: headless `claude -p ... --allowed-tools "" --output-format json` returns
clean parseable JSON in ~3–4 s on subscription auth, including with `--system-prompt`. (Switched
text→json on 2026-06-22 to capture real `usage` for honest metering.)

## Reference

Pattern adapted from `~/projects/RCA/harness/llm.py` (same two-backend + stub shape).
