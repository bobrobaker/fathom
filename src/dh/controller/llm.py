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
    """Headless `claude -p`: tools stripped, system prompt replaced, project context
    excluded (scratch cwd). Subscription auth, no API key. The spike's default."""
    name = "cli"

    def __init__(self, model: str, exe: str | None = None, timeout_s: int = 180):
        self._exe = exe or os.environ.get("LLM_CLI", "claude")
        self._model = model
        self._timeout = int(os.environ.get("LLM_CLI_TIMEOUT", timeout_s))

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024) -> str:
        argv = [self._exe, "-p", prompt, "--allowed-tools", "",
                "--output-format", "text", "--model", self._model]
        if system:
            argv += ["--system-prompt", system]
        with tempfile.TemporaryDirectory() as cwd:
            proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                                  timeout=self._timeout)
        if proc.returncode != 0:
            raise RuntimeError(f"claude CLI failed ({proc.returncode}): {proc.stderr[:400]}")
        return proc.stdout.strip()


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
    """Wraps any backend to accumulate approximate token cost (chars/4) for the eval.

    A *CLI-derived estimate* by design — the headless CLI exposes no usage API, so we count
    chars/4 of the content we control (the user prompt + the system prompt we pass). Because the
    CLI is invoked with tools stripped and its default system prompt replaced (see CLIBackend),
    little hidden scaffolding remains, so this approximates API *input* tokens. The system-prompt
    portion — the fixed per-call overhead — is tracked separately (`scaffold_tokens`) so a report
    can subtract it for a content-only, API-equivalent estimate and show it is small and constant
    across solvers (B10). The same meter wraps every solver, so any residual overhead cancels in
    the cross-solver comparison. Counts are ~model-agnostic (chars/4), not billing-accurate."""
    def __init__(self, inner: LLMBackend):
        self.inner = inner
        self.name = f"metered:{inner.name}"
        self.in_tokens = 0
        self.out_tokens = 0
        self.scaffold_tokens = 0   # system-prompt tokens — the fixed per-call CLI scaffolding
        self.calls = 0

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024) -> str:
        self.in_tokens += (len(prompt) + len(system or "")) // 4
        self.scaffold_tokens += len(system or "") // 4
        self.calls += 1
        out = self.inner.complete(prompt, system=system, max_tokens=max_tokens)
        self.out_tokens += len(out) // 4
        return out

    @property
    def total_tokens(self) -> int:
        return self.in_tokens + self.out_tokens

    @property
    def content_tokens(self) -> int:
        """API-equivalent estimate: total net of the fixed system-prompt scaffolding (B10)."""
        return self.total_tokens - self.scaffold_tokens


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
