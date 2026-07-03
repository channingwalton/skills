---
name: fix-loop
description: Iterative review-fix cycle that runs code-reviewer then repairs Critical issues until none remain. Use when the user says "review and fix", "find and fix bugs", "clean up the code", "fix all issues", "review then fix", or otherwise asks to both find and repair problems.
---

# Fix Loop

Run a bounded review-fix cycle until all Critical issues are resolved, marked unfixable, or the iteration cap is hit.

Review uses the `code-reviewer` **Skill** — invoke it with the Skill tool. There is no `code-reviewer` subagent_type; `Task(subagent_type: "code-reviewer")` fails with "Agent type not found". Use `Skill(code-reviewer)`. Repairs follow the Fixer contract below.

Keep the reviewer and fixer roles separate even though one agent plays both: findings stand as written. Do not rationalise away findings because you are about to edit the code.

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
3. FIX - announce `Fix iteration N/3 - addressing X Critical issue(s)`; apply the Fixer contract below.
4. VERIFY - run the narrowest relevant tests plus the canonical command when practical. Compare with baseline.
5. NARROW - set next scope to modified files plus any newly touched files. If nothing changed because findings were unfixable, stop.

Warnings and suggestions are reported, not auto-fixed.

## Fixer Contract

Fix only Critical findings. Leave warnings and suggestions unactioned. Preserve user changes and avoid unrelated refactors.

For each finding:

1. READ - inspect the finding, surrounding code, and relevant tests.
2. FIX - apply the smallest change that resolves the finding.
3. VERIFY - run the narrowest tests that prove the fix.
4. TEST - run the project's canonical test command when practical.

If a fix breaks tests:

1. identify the failing fix
2. revert only that fix
3. mark the finding unfixable with the reason
4. re-run verification

A fix iteration is complete only when every Critical finding is fixed or marked unfixable, and verification status is clear.

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
