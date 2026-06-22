"""LLM plumbing (spec §6.6) — backends + structured controller calls.

One `complete(prompt, system) -> text` interface, three backends (see
`docs/decisions/2026-06-16-llm-backend-stripped-cli.md`):
  - `CLIBackend`  — headless `claude -p`, subscription auth, the default here.
  - `AnthropicBackend` — the SDK (needs `ANTHROPIC_API_KEY`); written, dormant.
  - `ScriptedBackend` — deterministic canned outputs for the test gates.

On top sit the four structured calls the loop makes — `seed_hypotheses`,
`propose_actions`, `interpret_result`, `synthesize` — each builds a tagged prompt,
parses JSON robustly (retry, then graceful degrade), and returns typed objects. The
system prompt is small and role-bounded; tool/check results come back as structured
observations the model interprets but never fabricates.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from typing import Literal, Protocol

from pydantic import BaseModel

from dh import config
from dh.schemas import Answer, EvidenceItem, EvidenceLink, Hypothesis, InvestigationGraph

log = logging.getLogger("dh.llm")

SYSTEM_PROMPT = (
    "You are a diagnostic controller. You maintain a hypothesis differential and propose "
    "the single most DISCRIMINATING next action — one that separates the leading hypotheses, "
    "not one that re-confirms a hypothesis already well-supported. Weigh evidence both ways: "
    "a nominal check argues AGAINST a hypothesis. A salient recent event (a reboot, a config "
    "change) is only the cause if the degradation onset aligns with it; if the onset predates "
    "it, the event is a non-causal trigger — note it, don't blame it. Distrust a channel with "
    "near-zero variance under changing load (a stuck/lying channel). Never assert a measurement "
    "you have not retrieved; cite evidence by id. Reply with ONLY the requested JSON object — "
    "no prose, no code fences."
)


# --- backends ----------------------------------------------------------------

class LLMBackend(Protocol):
    name: str

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024) -> str: ...


class AnthropicBackend:
    """Messages API. Written now, dormant until an ANTHROPIC_API_KEY exists."""
    name = "anthropic"

    def __init__(self, model: str):
        import anthropic

        self._client = anthropic.Anthropic()
        self._model = model

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024) -> str:
        kwargs = dict(model=self._model, max_tokens=max_tokens,
                      messages=[{"role": "user", "content": prompt}])
        if system:
            kwargs["system"] = system
        resp = self._client.messages.create(**kwargs)
        return " ".join(b.text for b in resp.content if getattr(b, "type", None) == "text")


class CLIBackend:
    """Headless `claude -p`: system prompt replaced, tools + project context excluded,
    subscription auth (no API key). The spike's default.

    A default `claude -p` call carries a ~21k-token system-prompt prefix (Claude Code harness +
    built-in tool definitions + global `~/.claude/CLAUDE.md`), even for a 3-token prompt. We
    delete it rather than cache it, with two flags (measured with `--output-format json`):
      - `--tools ""` removes the built-in tool *definitions* from context entirely (~14-17k).
        NOTE: `--allowed-tools ""` does NOT — it only removes tool *permissions*, leaving the
        definitions in the prompt. The controller has its own Python action system and never used
        Claude Code's tools, so this is pure dead weight; removing it is behaviour-neutral
        (verified: a full live diagnose still resolves correctly).
      - `--setting-sources project,local` excludes the `user` source → drops the global
        `~/.claude/CLAUDE.md` (~3.2k). With `--tools ""` alone, CLAUDE.md still loads (~3.5k).
    Together these take the per-call prefix from ~21k to ~150 tokens — there is essentially no
    scaffolding left, so per-call cost becomes the *actual prompt content* (uncached input +
    output), not a fixed overhead. This supersedes the earlier stable-cwd prompt-cache approach
    (which only made the 21k prefix a cheap cache_read); with the prefix gone there is nothing
    large enough to cache (<2048-token cacheable minimum), so caching is moot.

    Subscription auth survives both flags — credentials in `~/.claude/.credentials.json` are read
    independently of `--tools`/`--setting-sources` (no API key, no separate token). We do NOT pass
    `--bare` (forces an API key → metered, off subscription), `--strict-mcp-config`, or
    `--exclude-dynamic-system-prompt-sections`. The stable scratch cwd (below) is retained only to
    keep any project `CLAUDE.md` out of context, not for caching. See
    docs/decisions/2026-06-22-claude-cli-prompt-cache.md.

    `--output-format json` is used so the real per-call `usage` (input / cache_creation / read /
    output) is captured into `last_usage` for honest metering; the assistant text is the JSON
    `result` field."""
    name = "cli"

    # A stable scratch cwd under the system temp dir (not a repo) so no project CLAUDE.md leaks
    # into context. (No longer load-bearing for caching — the prefix is now ~150 tokens.)
    _SCRATCH = os.path.join(tempfile.gettempdir(), "fathom-cli-scratch")

    def __init__(self, model: str, exe: str | None = None, timeout_s: int = 180):
        self._exe = exe or os.environ.get("LLM_CLI", "claude")
        self._model = model
        self._timeout = int(os.environ.get("LLM_CLI_TIMEOUT", timeout_s))
        os.makedirs(self._SCRATCH, exist_ok=True)
        self.last_usage: dict | None = None

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024) -> str:
        argv = [self._exe, "-p", prompt, "--tools", "",
                "--setting-sources", "project,local",
                "--output-format", "json", "--model", self._model]
        if system:
            argv += ["--system-prompt", system]
        proc = subprocess.run(argv, cwd=self._SCRATCH, capture_output=True, text=True,
                              timeout=self._timeout)
        if proc.returncode != 0:
            raise RuntimeError(f"claude CLI failed ({proc.returncode}): {proc.stderr[:400]}")
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"claude CLI returned non-JSON: {proc.stdout[:400]}") from e
        if payload.get("is_error"):
            raise RuntimeError(f"claude CLI error result: {str(payload.get('result'))[:400]}")
        self.last_usage = payload.get("usage") or {}
        return (payload.get("result") or "").strip()


class ScriptedBackend:
    """Deterministic backend for tests. Maps a prompt's `TASK:<tag>` line to a canned
    reply; a list value is consumed in order across repeated calls of that tag."""
    name = "scripted"

    def __init__(self, replies: dict[str, str | list[str]]):
        self._replies = {k: (list(v) if isinstance(v, list) else v) for k, v in replies.items()}
        self.calls: list[str] = []

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024) -> str:
        tag = _read_tag(prompt)
        self.calls.append(tag)
        r = self._replies.get(tag, "{}")
        if isinstance(r, list):
            return r.pop(0) if r else "{}"
        return r


class MeteredBackend:
    """Wraps any backend to accumulate per-call token cost for the eval.

    When the inner backend exposes real per-call `usage` (CLIBackend does, via
    `--output-format json`), we record the true counts — uncached input, cache-creation,
    cache-read, and output tokens. This replaces the old chars/4 content estimate, which
    undercounted real input ~15x by ignoring the ~21k-token cached harness/tool prefix every
    call carries. Backends with no `last_usage` (ScriptedBackend in the test gates) fall back
    to chars/4 of the content we control.

    The ~21k prefix is identical across every solver, so it cancels in the cross-solver
    comparison; the per-call WIN of the stable-cwd cache fix (see CLIBackend) is a shift from
    `cache_creation` (~1.25-2x base price) to `cache_read` (~0.1x), NOT a drop in raw token count
    — raw input/call is ~21k either way. So a fair cost figure must price-weight the breakdown:
    `cost_tokens` does, and the raw components are exposed so a report can apply its own price
    model. `cached_tokens` tracks the reused prefix; `content_tokens` nets it out.

    Pricing multipliers are base-input-token equivalents for the pinned model **claude-sonnet-4-6**
    ($3 input / $15 output per 1M): output 5.0x; cache_read 0.1x; cache_creation 1.25x (5m TTL) /
    2.0x (1h TTL) — the 5m/1h split is read from `usage.cache_creation`, so the figure self-adjusts
    to whichever TTL the CLI used (observed: 1h). If the model pin changes (config.yaml), re-check
    OUTPUT_MULT against that model's output/input price ratio."""
    OUTPUT_MULT = 5.0          # claude-sonnet-4-6: $15 output / $3 input
    CACHE_READ_MULT = 0.1
    CACHE_WRITE_5M_MULT = 1.25
    CACHE_WRITE_1H_MULT = 2.0

    def __init__(self, inner: LLMBackend):
        self.inner = inner
        self.name = f"metered:{inner.name}"
        self.uncached_in_tokens = 0   # input_tokens — uncached new input (prompt + uncached prefix)
        self.created_5m_tokens = 0    # cache_creation written with a 5m TTL (~1.25x)
        self.created_1h_tokens = 0    # cache_creation written with a 1h TTL (~2.0x)
        self.cached_tokens = 0        # cache_read_input_tokens — the reused prefix (~0.1x)
        self.out_tokens = 0
        self.calls = 0

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024) -> str:
        self.calls += 1
        out = self.inner.complete(prompt, system=system, max_tokens=max_tokens)
        usage = getattr(self.inner, "last_usage", None)
        if usage:
            self.uncached_in_tokens += usage.get("input_tokens", 0)
            self.cached_tokens += usage.get("cache_read_input_tokens", 0)
            self.out_tokens += usage.get("output_tokens", 0)
            created = usage.get("cache_creation_input_tokens", 0)
            breakdown = usage.get("cache_creation") or {}
            self.created_5m_tokens += breakdown.get("ephemeral_5m_input_tokens", 0)
            # any creation not attributed to 5m is 1h (conservative when the breakdown is absent)
            self.created_1h_tokens += (breakdown.get("ephemeral_1h_input_tokens")
                                       if "ephemeral_1h_input_tokens" in breakdown
                                       else created - breakdown.get("ephemeral_5m_input_tokens", 0))
        else:  # no usage API (e.g. ScriptedBackend) — estimate from content we control
            self.uncached_in_tokens += (len(prompt) + len(system or "")) // 4
            self.out_tokens += len(out) // 4
        return out

    @property
    def created_tokens(self) -> int:
        """Total cache-creation input tokens (5m + 1h TTL)."""
        return self.created_5m_tokens + self.created_1h_tokens

    @property
    def in_tokens(self) -> int:
        """Raw input tokens processed (uncached + cache-creation + cache-read)."""
        return self.uncached_in_tokens + self.created_tokens + self.cached_tokens

    @property
    def total_tokens(self) -> int:
        return self.in_tokens + self.out_tokens

    @property
    def content_tokens(self) -> int:
        """Marginal tokens net of the reused cached prefix (cache_read), which is ~0.1x cost."""
        return self.total_tokens - self.cached_tokens

    @property
    def cost_tokens(self) -> int:
        """Price-weighted cost in base-input-token equivalents — the figure that reflects the
        cache fix. See class docstring for multipliers (pinned to claude-sonnet-4-6)."""
        return int(self.uncached_in_tokens
                   + self.created_5m_tokens * self.CACHE_WRITE_5M_MULT
                   + self.created_1h_tokens * self.CACHE_WRITE_1H_MULT
                   + self.cached_tokens * self.CACHE_READ_MULT
                   + self.out_tokens * self.OUTPUT_MULT)


def get_backend(model: str | None = None) -> LLMBackend | None:
    """Anthropic if keyed; else a headless CLI if available; else None (stub fallback).

    `DH_BACKEND=stub` forces None so the suite never shells out."""
    if os.environ.get("DH_BACKEND") == "stub":
        return None
    model = model or os.environ.get("DH_MODEL") or config.model_id()
    if os.environ.get("ANTHROPIC_API_KEY"):
        return AnthropicBackend(model)
    exe = os.environ.get("LLM_CLI", "claude")
    if shutil.which(exe):
        return CLIBackend(model, exe=exe)
    return None


# --- JSON parsing ------------------------------------------------------------

def extract_json(text: str) -> dict:
    """Pull the first JSON object from a completion (tolerates fences / prose)."""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    blob = fenced.group(1) if fenced else None
    if blob is None:
        start, end = text.find("{"), text.rfind("}")
        blob = text[start:end + 1] if start != -1 and end > start else ""
    try:
        out = json.loads(blob)
        return out if isinstance(out, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def _read_tag(prompt: str) -> str:
    m = re.search(r"^TASK:(\w+)", prompt, re.MULTILINE)
    return m.group(1) if m else ""


def _call_json(backend: LLMBackend, tag: str, body: str, *, retries: int = 2,
               max_tokens: int = 1024, system: str = SYSTEM_PROMPT) -> dict:
    """Call the backend for `tag`, parse JSON, retry on failure, then degrade to {}.

    `system` defaults to the controller's prompt; baselines pass their own so the controller's
    hypothesis-differential guidance never leaks into bare_llm / react (fairness, §7)."""
    prompt = f"TASK:{tag}\n{body}"
    for attempt in range(retries + 1):
        nudge = "" if attempt == 0 else "\n\nYour previous reply was not valid JSON. Return ONLY the JSON object."
        try:
            raw = backend.complete(prompt + nudge, system=system, max_tokens=max_tokens)
        except Exception as e:  # noqa: BLE001 — backend failures must degrade, not crash
            log.warning("backend error on %s (attempt %d): %s", tag, attempt + 1, e)
            continue
        data = extract_json(raw)
        if data:
            return data
        log.warning("unparseable %s output (attempt %d)", tag, attempt + 1)
    log.error("giving up on %s after %d attempts; degrading", tag, retries + 1)
    return {}


# --- controller-internal action type -----------------------------------------

class ActionProposal(BaseModel):
    type: Literal["run_check", "traverse", "search", "recommend_swap_test"]
    args: dict = {}
    rationale: str = ""
    expected_discrimination: float = 0.5  # 0–1, LLM-estimated (§6.3)
    target_hypotheses: list[str] = []


# --- prompt helpers ----------------------------------------------------------

# Cap |LLR| per evidence link at ≈2.0 (≈7× odds shift, e^2≈7.4) so one observation — which the
# LLM may over-weight — can't saturate a hypothesis. Sized against τ_dom=0.70 (logit≈0.85): one
# strong item clears it, but the §6.2 stop also needs margin>0.20 over the runner-up, so a clean
# conclusion still wants a second concordant item. The accumulated log-odds is clamped again in
# `beliefs` (MAX_LOG_ODDS) so confidence tops out near 0.95, leaving room to be pulled back down.
MAX_WEIGHT = 2.0


def _coerce_node_ref(node_ref, label, cand_ids: set[str], cand_names: dict[str, str]):
    """Snap an LLM-supplied node_ref to a real candidate id (models drift to free text)."""
    if node_ref in cand_ids:
        return node_ref
    text = f"{node_ref or ''} {label or ''}".lower()
    for cid in cand_ids:
        if cid.lower() in text:
            return cid
    text_toks = set(re.findall(r"\w+", text))
    best, best_overlap = node_ref, 0
    for cid, name in cand_names.items():
        overlap = len(set(re.findall(r"\w+", (name or "").lower())) & text_toks)
        if overlap > best_overlap:
            best, best_overlap = cid, overlap
    return best if best_overlap >= 1 else node_ref


def _ig_brief(ig: InvestigationGraph) -> str:
    hyps = "\n".join(
        f"  - {h.id} | {h.label} | log_odds={h.log_odds:.2f} | {h.status}"
        for h in ig.hypotheses
    ) or "  (none yet)"
    ev = "\n".join(f"  - {e.id}: {e.summary} (src={e.source})" for e in ig.evidence) or "  (none yet)"
    return f"symptom: {ig.symptom}\nhypotheses:\n{hyps}\nevidence:\n{ev}"


# --- the four structured calls -----------------------------------------------

def seed_hypotheses(backend: LLMBackend, symptom: str, candidates: list[dict],
                    playbook: str | None = None) -> list[Hypothesis]:
    """Seed the differential from the symptom + affects-neighbors + playbook (§6.1)."""
    body = (
        f"Symptom: {symptom}\n"
        f"Candidate subsystems/parts (id | name) reachable from the symptom:\n"
        + "\n".join(f"  - {c['id']} | {c['name']}" for c in candidates)
        + (f"\nPlaybook differential:\n{playbook}\n" if playbook else "\n")
        + 'Return {"hypotheses":[{"id","label","node_ref"}]} — one fault hypothesis per '
          "plausible cause, node_ref pointing at the implicated subsystem/part id."
    )
    data = _call_json(backend, "seed", body)
    cand_ids = {c["id"] for c in candidates}
    cand_names = {c["id"]: c.get("name", "") for c in candidates}
    hyps: list[Hypothesis] = []
    for h in data.get("hypotheses", []):
        try:
            node_ref = _coerce_node_ref(h.get("node_ref"), h.get("label"), cand_ids, cand_names)
            hyps.append(Hypothesis(id=h["id"], label=h.get("label", h["id"]), node_ref=node_ref))
        except (KeyError, TypeError):
            continue
    if not hyps:  # degrade: one hypothesis per candidate so the loop still runs
        log.warning("seed_hypotheses degraded to candidate fallback")
        hyps = [Hypothesis(id=f"h.{c['id']}", label=c["name"], node_ref=c["id"])
                for c in candidates]
    return hyps


def propose_actions(backend: LLMBackend, ig: InvestigationGraph, action_menu: list[str],
                    capabilities: set[str]) -> list[ActionProposal]:
    """Propose candidate next actions with an expected-discrimination estimate (§6.3)."""
    body = (
        f"{_ig_brief(ig)}\n"
        f"Available action types: {sorted(capabilities)}\n"
        f"Available checks/targets: {action_menu}\n"
        "Propose the next actions. Favour the ONE action that best discriminates between the "
        "current leading hypotheses — score expected_discrimination high only when the result "
        "would move them apart (raise one AND lower another), low for an action that merely "
        "re-confirms an already-supported hypothesis. If two hypotheses are both high, pick the "
        "action that tells them apart. If a salient recent event (reboot / config change) could "
        "be mistaken for the cause, propose onset_vs_event_check against it to order the onset.\n"
        'Return {"actions":[{"type","args","rationale","expected_discrimination",'
        '"target_hypotheses"}]} where type is one of run_check|traverse|search|'
        "recommend_swap_test, args carries its parameters (e.g. {\"name\":\"tec_load_check\"} "
        "for run_check), and expected_discrimination is 0..1."
    )
    data = _call_json(backend, "propose", body)
    actions: list[ActionProposal] = []
    for a in data.get("actions", []):
        try:
            actions.append(ActionProposal.model_validate(a))
        except Exception:  # noqa: BLE001 — skip malformed proposals
            continue
    return actions


def interpret_result(backend: LLMBackend, ig: InvestigationGraph, action: ActionProposal,
                     result: dict) -> tuple[EvidenceItem | None, list[EvidenceLink], list[str]]:
    """Turn a tool/check result into an EvidenceItem + polarity/weight links (§6.4)."""
    hyp_ids = [h.id for h in ig.hypotheses]
    body = (
        f"{_ig_brief(ig)}\n"
        f"Action just taken: {action.type} args={action.args}\n"
        f"Structured result:\n{json.dumps(result)}\n"
        f"Hypothesis ids: {hyp_ids}\n"
        "Interpret this result into evidence and links. Emit a link for EVERY hypothesis the "
        "result bears on — a NEGATIVE ('-') link to any hypothesis it argues against (e.g. a "
        "nominal/at-spec reading rules one out), not only a positive link to the favoured one. "
        "If the result demotes a salient recent event (its onset_predates_event is true, so the "
        "event is coincident not causal) or flags a stuck/unreliable channel, put that event's "
        "or channel's id (use the node id, e.g. log.reboot or metric.detector_temp) in "
        "conflicts.\n"
        'Return {"evidence":{"id","summary","source"},"links":[{"hypothesis_id",'
        '"polarity","weight"}],"conflicts":[node_or_signal_ids]} where polarity is "+" or '
        '"-" and weight≈|log-likelihood-ratio| (0..4). Link only to listed hypothesis ids.'
    )
    data = _call_json(backend, "interpret", body)
    ev_d = data.get("evidence") or {}
    evidence = None
    if ev_d.get("id"):
        try:
            evidence = EvidenceItem(id=ev_d["id"], summary=ev_d.get("summary", ""),
                                    source=ev_d.get("source", action.type),
                                    props=ev_d.get("props", {}))
        except (KeyError, TypeError):
            evidence = None
    links: list[EvidenceLink] = []
    if evidence:
        for ln in data.get("links", []):
            try:
                if ln["hypothesis_id"] in hyp_ids and ln["polarity"] in ("+", "-"):
                    weight = min(abs(float(ln["weight"])), MAX_WEIGHT)  # clamp |LLR|
                    links.append(EvidenceLink(evidence_id=evidence.id,
                                              hypothesis_id=ln["hypothesis_id"],
                                              polarity=ln["polarity"], weight=weight))
            except (KeyError, TypeError, ValueError):
                continue
    conflicts = [c for c in data.get("conflicts", []) if isinstance(c, str)]
    return evidence, links, conflicts


def synthesize(backend: LLMBackend, ig: InvestigationGraph,
               abstain: bool = False) -> Answer:
    """Produce the final Answer (cause+chain+citations, or abstain) from the IG (§6.1)."""
    body = (
        f"{_ig_brief(ig)}\n"
        f"conflicts flagged: {ig.conflicts}\n"
        f"{'The evidence does not support a confident single cause; ABSTAIN.' if abstain else ''}\n"
        'Return {"answer_type":"cause"|"abstain","root_cause":node_id_or_null,'
        '"causal_chain":[node_ids],"cited_evidence":[evidence_ids],"ruled_out":[node_ids],'
        '"conflicts":[ids],"recommended_action":str_or_null}. Cite only evidence ids that exist.'
    )
    data = _call_json(backend, "synthesize", body, max_tokens=1536)
    valid_ev = {e.id for e in ig.evidence}
    answer_type = data.get("answer_type")
    if answer_type not in ("cause", "abstain"):
        answer_type = "abstain" if abstain else "cause"
    # resolve root_cause: models often return the hypothesis id, not its node_ref
    hyp_node = {h.id: h.node_ref for h in ig.hypotheses}
    root_cause = data.get("root_cause")
    if root_cause in hyp_node and hyp_node[root_cause]:
        root_cause = hyp_node[root_cause]
    return Answer(
        answer_type=answer_type,
        root_cause=root_cause if answer_type == "cause" else None,
        causal_chain=[c for c in data.get("causal_chain", []) if isinstance(c, str)],
        cited_evidence=[c for c in data.get("cited_evidence", []) if c in valid_ev],
        ruled_out=[c for c in data.get("ruled_out", []) if isinstance(c, str)],
        conflicts=list(ig.conflicts),  # loop-accumulated & id-validated, not free-text
        recommended_action=data.get("recommended_action") or ig.recommended_action,
        final_graph=ig,
    )
