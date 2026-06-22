# Per-call `claude -p` overhead: delete the scaffolding (`--tools ""`), don't cache it

**Date:** 2026-06-22 · **Status:** accepted · **Supersedes the cost-fix hypothesis in**
`2026-06-21-eval-fairness-and-scoring-audit.md` / `docs/debt.md` (2026-06-21 block)

## Decision

`CLIBackend` invokes `claude -p` with **`--tools ""`** (removes the ~14-17k of built-in tool
*definitions* from context) **+ `--setting-sources project,local`** (drops the ~3.2k global
`~/.claude/CLAUDE.md`), from a stable scratch cwd, reading usage via `--output-format json`.
Together these take the per-call system-prompt prefix from **~21k tokens to ~150** — the
scaffolding is essentially gone, so per-call cost is now the *actual prompt content* (uncached
input + output), not a fixed overhead. `MeteredBackend` records the real per-call `usage`
breakdown (uncached input / cache-creation-5m / cache-creation-1h / cache-read / output) and
exposes a price-weighted `cost_tokens`. We do **not** pass `--allowed-tools ""` (does not strip
tool *definitions*, only permissions), `--exclude-dynamic-system-prompt-sections`,
`--strict-mcp-config`, or `--bare`.

> **This supersedes the original thesis of this doc** (preserved below as the reasoning trail):
> we first made the 21k prefix a cheap prompt-cache `cache_read` via a stable cwd (~7x), then
> discovered `--tools ""` deletes the prefix outright. With the prefix at ~150 tokens (below the
> 2048-token cacheable minimum) caching is moot; the stable cwd is retained only to keep project
> `CLAUDE.md` out of context. All on subscription, no API key.

## Why — measured, not inherited

The 2026-06-21 audit diagnosed "~22.6k tokens of scaffolding per call" and hypothesised the fix
was to *strip* the global `~/.claude/CLAUDE.md` + dynamic sections (via
`--exclude-dynamic-system-prompt-sections`, `--setting-sources`, scratch `$HOME`, or `--bare`).
Measuring each lever with `--output-format json` (3-token prompt, `claude-sonnet-4-6`) showed
that hypothesis was wrong on both ends:

| Config (from a stable cwd)                         | cache_creation (steady) | cache_read |
|----------------------------------------------------|------------------------:|-----------:|
| baseline flags, **fresh temp cwd per call** (old)  |        21,149  |          0 |
| `--allowed-tools ""` only                          |     no change vs default (27.5k) — **tool defs are NOT stripped** |
| `--exclude-dynamic-system-prompt-sections`         |         ~6,546 |    ~14,603 |
| `--strict-mcp-config`                              |         ~6,449 |    ~14,603 |
| **plain flags, stable cwd**                        | ~6,546 (varying prompts) → **0** (byte-identical) | ~14,618 |
| **stable cwd, `--setting-sources project,local`**  | **~2,270** | ~14,616 |
| **`--tools "" --setting-sources project,local`** (FINAL) | **0** | **0** — prefix is ~150 uncached tokens, below the 2048 cache minimum |

Findings:
1. **The cache-buster was the cwd, not CLAUDE.md.** The cwd path appears in the system prompt's
   "working directory" section, so a fresh temp dir per call changed the cacheable prefix every
   call → full `cache_creation` (~2x base price, 1h TTL) every call, `cache_read` never hit.
2. **`--allowed-tools ""` removes tool *permissions*, not tool *definitions*** — the defs stay
   in context (D=F=27.5k). The 2026-06-16 "tools stripped" claim was false; harmless because the
   defs are now cached, but the doc is corrected.
3. **`--exclude-dynamic-system-prompt-sections` and `--strict-mcp-config` HURT** here — both
   deviate from the warm common prefix and force ~6.5k re-creation per call instead of reading it.
   The opposite of the 2026-06-21 recommendation. (Hence: measure levers, don't infer them.)
4. **`--setting-sources project,local` HELPS** — excluding the `user` source drops the
   auto-discovered global `~/.claude/CLAUDE.md` (~3.2k tokens incl. its memory wrapper) from the
   re-created tail: steady-state `cache_creation` 6,546 → ~2,270/call. Subscription auth survives
   (it reads `~/.claude/.credentials.json`, independent of setting sources — no API key, no
   separate token). This is the residual that 2026-06-21 wanted but mis-prescribed (it called for
   a scratch `$HOME` + a long-lived `CLAUDE_CODE_OAUTH_TOKEN`; neither is needed — `--setting-sources`
   alone does it on the existing token).
5. **`--tools ""` is the real fix — it DELETES the prefix, not caches it** (found via web research,
   then measured). `--allowed-tools ""` removes tool *permissions* but leaves the ~14-17k of tool
   *definitions* in context; **`--tools ""` (or bare-name `--disallowedTools "*"`) removes the
   definitions themselves.** With it, the per-call prefix collapses to ~150 uncached tokens
   (`create=0 read=0`). Combined with `--setting-sources` (CLAUDE.md gone too), there is no
   scaffolding left to cache or pay for — cost becomes actual content (input + output). Auth
   unaffected. The controller uses its own Python action system and never invokes Claude Code's
   built-in tools, so removing their definitions is expected to be behaviour-neutral; live
   diagnoses run end-to-end and emit valid structured output. NOT proven equivalent across runs:
   case1's root-cause result varies run-to-run on its own (observed both `part.tec` and the wrong
   `part.detector` — the documented thesis-negative variance, n=1 uncharacterized), so `--tools ""`
   is not *shown* to change accuracy, but a controlled before/after across ≥3 runs is the proper
   check and has not been done. This is why caching (findings 1-4) is now moot — there's nothing
   big enough to cache.
6. **`--bare` was rejected** — it forces `ANTHROPIC_API_KEY`/`apiKeyHelper`, switching off the
   subscription onto the metered API (and it ignores `CLAUDE_CODE_OAUTH_TOKEN`, so there is no
   subscription path through it). No key is available and the spike runs on subscription.

## The honest size of the win

Per-call **input-cost** in base-input-token equivalents (uncached 1.0x, cache_creation 2.0x @1h,
cache_read 0.1x), 3-token probe prompt:

| State | uncached | created (1h) | read | input-cost units | vs original |
|---|---:|---:|---:|---:|---:|
| original (fresh temp cwd) | 3 | 21,149 | 0 | 42,301 | 1.0x |
| stable cwd (cache the prefix) | 3 | ~6,546 | ~14,618 | ~14,557 | 2.9x |
| stable cwd + `--setting-sources` | 3 | ~2,270 | ~14,616 | ~6,005 | 7.0x |
| **`--tools "" --setting-sources`** (FINAL) | ~150 | 0 | 0 | **~150** | **~280x** |

The stable-cwd/caching path got to ~7x by making the 21k prefix a cheap `cache_read`. `--tools ""`
makes that path moot: it removes the prefix, so input cost drops to the actual content (~150
tokens of system+user prompt for a small call) — **~280x cheaper than the original broken state**,
all on subscription, no API key, no extra token.

With scaffolding gone, **per-call cost is now dominated by output** (the controller's own JSON
reasoning), which is irreducible real work. A full live `diagnose` on case1 (8 calls, budget 4):
uncached-in ≈4.2k total (~530/call), output ≈12.3k — so `cost_tokens` is ~85% output (5.0x weight)
and ~15% input. There is no scaffolding left to optimise; further input savings would mean
shortening the controller's own prompts/IG-brief, a separate concern. `cost_tokens` (in
`MeteredBackend`) weights output 5.0x and the 5m/1h cache split from `usage.cache_creation`, so the
reported figure reflects this.

## Measurement reproducer

`(cd /tmp/scratch && claude -p "<prompt>" --tools "" --setting-sources project,local
--output-format json --model claude-sonnet-4-6 --system-prompt "<sys>")` → parse
`.usage.{input_tokens,cache_creation_input_tokens,cache_read_input_tokens,output_tokens}`. Expect
`input_tokens ≈ 150, create=0, read=0`. Auth works with no API key (subscription credentials are
read regardless of `--tools`/`--setting-sources`). Swap `--tools ""` → `--allowed-tools ""` to see
the ~17k tool definitions reappear (the distinction that matters).
