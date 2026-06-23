# Builder brief — recruiter-driven viewer polish

You are the **Fathom builder**, implementing a set of viewer GUI changes agreed in a two-round
"confer" where a skeptical recruiter (~45s of attention) critiqued the showpiece. Goal: make the
first 5 seconds land — *easy to understand, looks interesting, signals a transferable skill* —
**without ever breaching the honesty boundary**.

**Read first:** `docs/viewer_dev.md` (standing context — what the viewer is, the honesty boundary,
the dev loop, the gotchas). The whole viewer is one file: `src/dh/viewer/site.html` (HTML+CSS+D3).

## Hard constraints (non-negotiable)
- **Static / offline / replay-only. Zero LLM calls, zero new data.** Every change is to copy,
  layout, CSS, or replay-driving JS over the *already-recorded* runs.
- **Honesty boundary (load-bearing).** Never fabricate state. Narrative mode re-times *real* state;
  that's sanctioned. The `8/8` accuracy is **n=1, indicative, an n=3 variance pass is owed** — any
  promotion of it must carry that caveat at equal visual weight.
- **Do NOT alter the in-code source-of-truth caveat** — the `BASELINES` comment block at
  `site.html:~201-203` (`INDICATIVE ONLY: n=1 ...`). Rendered honesty and code honesty are separate
  obligations; reframing the rendered headline does not license softening that comment.
- **Do NOT run `tools/build_viewer_site.py`** (it re-rolls the hard-won 8/8 capture live). After any
  `site.html` change, propagate with the **offline** re-export (command below).

## The changes (agreed; implement all six)

**P0 — Lead with the *behavior*, not the number.** Add an above-the-fold headline whose claim is
*structural* (true at n=1), so it reads as strength with nothing to hedge:
> **The agent knows when it can't answer — and says so instead of guessing.**
Then accuracy becomes *supporting* evidence with the caveat riding on it, e.g.:
> In a controlled 8-case eval it localized the right root cause in every case (8/8 vs 6/8 for a bare
> LLM) — an indicative single-pass result; an n=3 variance pass is owed before that number is
> load-bearing.
Place this compact result strip directly under the `#intro` (above `#bar`/the graph), so a 45s skim
hits it. You may mirror the top line of `#baselines-sec`; leave the full baselines table where it is.

**P1 — Default to "Faithful (literal)" mode AND autoplay the first case on load.**
- Change the default `MODE` from `"narrative"` to the faithful/literal mode. Rationale: faithful
  seeds all hypotheses at triage (step 0), so the first frame is already *populated* — no empty-KPI
  cold-open — and it matches the plain description, so it's less confusing as a default.
- On load, **autoplay the first case** (drive the existing play/step replay) so the hero frame is a
  live, populated, animating graph — not a static first step. Guard the autoplay loop with the
  existing lifecycle tokens (`introTimer`, `pulseId`) so you don't leak a transition loop (see the
  dev-guide gotcha on `.on("end", loop)` surviving `.remove()`).
- Keep narrative mode fully available via the toggle; this is a *default* change, not a removal.

**P3 — Intro rewrite, plain-English-first hook (drive value).** The `#intro .tag` currently opens with
"abductive diagnostic reasoner / value-of-information–guided hypothesis differential over a typed
causal graph." Lead instead with a plain-English sentence that states the *job and why it matters*;
demote the precise vocabulary to the *second* sentence (keep it — it's the real differentiating claim
on the second read). Keep the `<details>` deep-dive as-is.

**P4 — One "why this transfers" bridge sentence.** Near the intro, name the transferable shape —
*structured agentic reasoning + calibrated abstention + a controlled evaluation against real
baselines* — and say *why lidar*: the domain is hard enough (decoys, a salient red-herring trigger to
demote, an abstain case) to *require* the structure; an easy domain would let a bare LLM win and
invalidate the result. **Do not de-domain.** One sentence, not a paragraph.

**P5 — Relabel the view modes.** In the modebar: "Narrative reveal" → **"Discovery order"**;
"Faithful (literal)" → **"All at once"**. The word "Faithful" implies the other mode lies — a self-own
in the copy. Update the `mhint` disambiguator to state *both replay the same real run; "discovery
order" reveals hypotheses as the agent surfaced them*. Label/copy change only — do not touch the
honesty behavior. (Note: with P1, "All at once" is now the default.)

**P6 — Author/provenance footer seam (one line, not a résumé).** Add a single unobtrusive footer:
> Built by Bolun · github.com/bobrobaker/fathom
Link to the repo (`https://github.com/bobrobaker/fathom`). This attaches authorship and survives the
artifact traveling (screenshots/hotlinks). **Keep out** any human-vs-LLM-contribution breakdown or
skills list — that's the README/portfolio's job, which the footer links to. (Confirm the display name
"Bolun" with the recruiter/owner if unsure.)

## Dev loop (port 8778 — 8777 is already taken by another server)
```bash
cd /home/bolun/projects/fathom-viewer-polish
VENV=/home/bolun/projects/fathom/.venv/bin/python
PYTHONPATH=src $VENV tools/reexport_viewer_graphs.py     # offline refresh — propagate site.html → viewer_site/
PYTHONPATH=src $VENV tools/gui_smoke.py                  # smoke + screenshots → /tmp/fathom_gui/
PYTHONPATH=src $VENV -m pytest tests/test_viewer.py -q   # unit gate
cd viewer_site && python3 -m http.server 8778            # preview at http://127.0.0.1:8778/
```

## Working rule — iterate visually
**Visual verification is the multiplier.** After each change, re-export, drive Playwright headless
against `viewer_site/index.html`, screenshot, and *read the image* — confirm it actually looks right,
not just "no console errors." `tools/gui_smoke.py` is the pattern to copy. Show the recruiter
before/after screenshots at each checkpoint.

Implement P3/P4/P0 (the cheap copy trio) first, then P1 (default+autoplay, the lifecycle-sensitive
one), then P5/P6. Commit when a coherent chunk is done and verified.
