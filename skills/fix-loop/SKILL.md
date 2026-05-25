---
name: fix-loop
description: Iterative review-fix cycle that orchestrates code-reviewer and fixer to eliminate Critical issues. Use when the user says "review and fix", "find and fix bugs", "clean up the code", "fix all issues", "review then fix", or otherwise asks to both find and repair problems.
---

# Fix Loop

Run a bounded review-fix cycle until all Critical issues are resolved, marked unfixable, or the iteration cap is hit.

`fix-loop` orchestrates:

- `code-reviewer` for read-only, disconfirming review
- `fixer` for minimal targeted repairs

Keep those roles separate. Do not rationalise away findings because you are about to edit the code.

## Input

Use the supplied files/directories when present. With no explicit scope:

1. uncommitted changes: `git diff --name-only` plus `git diff --name-only --staged`
2. otherwise recent work: `git diff --name-only HEAD~3`
3. otherwise ask what to review

## Baseline

Before fixing, run the project's canonical verification command if discoverable from README, CONTRIBUTING, build scripts, package manager scripts, Makefile, or workspace instructions. Record pass/fail/unavailable so later failures can be separated from regressions.

## Loop

Maximum 3 iterations.

For each iteration:

1. REVIEW - announce `Review iteration N/3`; use `code-reviewer` against the current scope. If the user explicitly asks for subagents, a bounded read-only reviewer can be separate from the fixing agent.
2. TRIAGE - extract only Critical findings. If none remain, stop.
3. FIX - announce `Fix iteration N/3 - addressing X Critical issue(s)`; use `fixer` when available. Fix only Critical findings. Preserve user changes and avoid unrelated refactors.
4. VERIFY - run the narrowest relevant tests plus the canonical command when practical. Compare with baseline.
5. NARROW - set next scope to modified files plus any newly touched files. If nothing changed because findings were unfixable, stop.

Warnings and suggestions are reported, not auto-fixed.

## Final Report

```markdown
# Fix Loop Report

## Iterations
N/3

## Resolved
- [file:line] [issue] - fixed in iteration N

## Remaining Critical
- [file:line] [issue] - [reason]

## Noted
- [file:line] [Warning/Suggestion] - not actioned

## Test Status
[baseline vs final, including unavailable checks]
```

Do not commit. Callers decide when to commit.
