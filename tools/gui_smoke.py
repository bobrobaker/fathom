#!/usr/bin/env python3
"""Headless GUI smoke test for the viewer showpiece.

Loads `viewer_site/index.html` over file://, exercises each curated case, and asserts the D3 render
actually produced a graph (nodes/edges/labels in the DOM) with no console errors. Screenshots land in
`/tmp/fathom_gui/` for eyeballing. Not a pytest unit — it needs a browser; run on demand.

    PYTHONPATH=src python tools/gui_smoke.py
"""

from __future__ import annotations

import pathlib
import sys

from playwright.sync_api import sync_playwright

SITE = pathlib.Path(__file__).resolve().parent.parent / "viewer_site" / "index.html"
OUT = pathlib.Path("/tmp/fathom_gui")
# (case_id, expects_leader_ring) — the abstain case must render NO winner; the cause cases must.
CASES = [("case1", True), ("case5", False), ("case6", True)]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 760})
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(SITE.as_uri())
        page.wait_for_timeout(2600)  # let the intro choreography settle

        # Stress the async lifecycle: switch cases mid-intro and scrub fast — a leaked pulse loop or an
        # uncancelled intro timeout would surface here as a console error or a stomped view.
        for cid, _ in CASES:
            page.evaluate(f"selectCase('{cid}')")
            page.wait_for_timeout(300)  # well inside the ~1.5s intro window
            page.evaluate("go(cur.steps.length - 1)")
        page.wait_for_timeout(800)
        if errors:
            failures.append(f"rapid-switch stress: console errors {errors[:3]}")

        for cid, expects_leader in CASES:
            errors.clear()
            page.evaluate(f"selectCase('{cid}')")
            page.wait_for_timeout(2600)
            n_nodes = page.eval_on_selector_all(".node", "els => els.length")
            n_edges = page.eval_on_selector_all(".edge", "els => els.length")
            n_labels = page.eval_on_selector_all(".nodeLabel", "els => els.length")
            # jump to the final step (full evidence + leader/abstain settled), screenshot
            page.evaluate("go(cur.steps.length - 1)")
            page.wait_for_timeout(1500)
            # the leader ring is a thick stroke; D3 interpolates #fff to an rgb() string, so key on width
            leaders = page.eval_on_selector_all(
                ".node circle", "els => els.filter(c => +c.getAttribute('stroke-width') >= 3).length")
            page.screenshot(path=str(OUT / f"{cid}.png"))
            status = "OK"
            if n_nodes == 0 or n_edges == 0 or n_labels == 0:
                failures.append(f"{cid}: empty render (nodes={n_nodes} edges={n_edges} labels={n_labels})")
                status = "FAIL-empty"
            if errors:
                failures.append(f"{cid}: console errors {errors[:3]}")
                status = "FAIL-console"
            if expects_leader and leaders == 0:
                failures.append(f"{cid}: expected a leader ring, found none")
                status = "FAIL-no-leader"
            if not expects_leader and leaders != 0:
                failures.append(f"{cid}: abstain case must show no winner, found {leaders} leader ring(s)")
                status = "FAIL-false-winner"
            print(f"  {cid}: {status} — {n_nodes} nodes, {n_edges} edges, {n_labels} labels, "
                  f"leader-rings={leaders} (expect-leader={expects_leader})", file=sys.stderr)
        browser.close()

    if failures:
        print("\nGUI SMOKE FAILURES:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"\n# GUI smoke OK — screenshots in {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
