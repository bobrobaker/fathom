# Upstream candidates

Rules codified locally whose domain-stripped form would apply to *any* project —
queued for the upstream template's next sweep. Format: `YYYY-MM-DD | rule | origin`.

2026-06-16 | A name must not overclaim a formalism it lacks — e.g. don't call a confidence-weighted directed-edge graph "causal" (that implies do-calculus / structural equations) | fathom tools/lint.py:check_causal_terminology
2026-06-22 | Predicting a git merge conflict from `git diff --stat` divergence on both branches is nominal, not structural — only overlapping hunks conflict; dry-run (`git merge --no-commit --no-ff` / `git merge-tree`) before claiming one | fathom monition t110
