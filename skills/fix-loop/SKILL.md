---
name: fix-loop
description: Iterative review-fix cycle that runs the host's native code review, adds house checks, then repairs Critical issues until none remain. Use when the user asks to both find and fix problems, such as "review and fix".
---

# Fix Loop

Run a bounded review-fix cycle until all Critical issues are resolved, marked unfixable, or the iteration cap is hit.

Review uses your host's native reviewer plus the House checks below. Repairs follow the Fixer contract below. This loop owns repairs, so the reviewer only reports.

Keep the reviewer and fixer roles separate even though one agent plays both: findings stand as written. Do not rationalise away findings because you are about to edit the code.

## Review

Run the row for your host:

| Host | Invocation | Scope |
| --- | --- | --- |
| Claude Code | `code-review` skill with an explicit level and target: `code-review high <target>` on iteration 1, `code-review medium <target>` after. A bare call reuses the user's last level. Pass no `--fix`, `--comment`, or `ultra`. | Target is the Input or NARROW scope: paths, a branch, or a PR. |
| Codex | Shell out to `codex review` with a scope flag: `--uncommitted`, `--base <branch>`, or `--commit <sha>`. The `/review` slash command is user-only. | Diff only; a scope flag takes no prompt argument. Later iterations re-run `--uncommitted`, which covers the fixes because this loop never commits. |
| Other | Run the House checks as the whole review. | Input scope. |

Normalise findings before TRIAGE:

| Claude `code-review` | Codex `review` | Triage as |
| --- | --- | --- |
| CONFIRMED correctness finding | `[P0]`, `[P1]` | Critical |
| PLAUSIBLE | `[P2]` | Settle with one command: proven → Critical, not ruled out → Warning |
| `simplification`, `efficiency`, `reuse` category | `[P3]` | Suggestion |

### House checks

Run these after the native review on every host; native reviewers miss them.

- **Test gaps** - new behaviour without a test is Critical. Report untested edge cases.
- **Landing surface** - open the surface the change lands on, not only the diff. A diff can be entirely correct and still ship a defect visible one file away. For a change that adds data to a handler, read that handler's authorisation guard, because a diff-only review does not show who can reach the endpoint. For a fix that matches or joins on an id, read the code that *writes* that id — a green disconfirmation run proves the test is load-bearing, not that the fixture is producible. For a change to a response payload or public contract, probe the generated artefact rather than reasoning about the source. For data added to any output (errors, logs, emails, API responses), name who can observe it — surfacing existing data to a new audience is an exposure.
- **Changed strings and signatures** - search the whole repo for other usages and test assertions of the old values.
- **First run** - a migration that can fail on existing production data is Critical unless the diff proves a safe backfill/default. For a change that re-enables a disabled path (CI trigger, feature flag, cron, scheduled job), check what it does on its first run in the first environment the merge reaches; read the CI branch triggers.
- **Repro** - every Critical finding carries a failing test, REPL snippet, or trace with concrete input values. Without one, it is a Warning.

## Input

Use the supplied files/directories when present. With no explicit scope:

1. uncommitted changes: `git diff --name-only` plus `git diff --name-only --staged`
2. otherwise recent work: `git log -3 --name-only --format=`
3. otherwise ask what to review

## Baseline

Before fixing, run the project's canonical verification command if discoverable from README, CONTRIBUTING, build scripts, package manager scripts, Makefile, or workspace instructions. Record pass/fail/unavailable so later failures can be separated from regressions.

## Loop

Maximum 5 fix iterations, and the loop always ends on a review. After the fifth FIX and VERIFY, announce `Final review` and run REVIEW once more on the narrowed scope; report its Critical findings under Remaining Critical, unfixed. A fix no review has seen is never reported as reviewed.

For each iteration:

1. REVIEW - announce `Review iteration N/5`; run the Review section against the current scope, then normalise its findings.
2. TRIAGE - extract Critical findings:
   - A Warning that names a concrete correctness defect introduced by the change under review is triaged as Critical unless the user explicitly defers it.
   - Every finding the reviewer raised goes in the report under exactly one heading, in the reviewer's words. A finding triaged only in your reasoning is a dropped finding.
   - *Noted* holds only Suggestions, Warnings that name no correctness defect, findings on code that predates this session, and findings a check ruled out (name the check). A correctness finding on code this session wrote is Resolved, Remaining Critical, or *Deferred by user* with the user's quoted words. "Commit it", "looks good", "handing this to task 2" and a list inside a collapsed section the user never opened are not deferrals; a finding in such a list ships as a known defect.
   - **Settle severity with a check, not by reasoning about it: a finding you cannot rule out in one command is not a Suggestion — run the command, or file it as a Warning.** A reasoned downgrade can hide a defect that blocks the release, and the probe takes one command.
   - If nothing remains to fix, stop.
3. FIX - announce `Fix iteration N/5 - addressing X Critical issue(s)`; apply the Fixer contract below.
4. VERIFY - run the narrowest relevant tests, then the canonical command when practical. Compare with baseline.
5. NARROW - set next scope to modified files plus any newly touched files. If nothing changed because findings were unfixable, stop.

## Fixer Contract

Fix only Critical findings. Report Warnings and Suggestions without fixing them. Preserve user changes and avoid unrelated refactors.

For each finding:

1. READ - inspect the finding, surrounding code, and relevant tests.
2. FIX - apply the smallest change that resolves the finding.
3. VERIFY - run the narrowest tests that prove the fix.

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
N/5 fix iterations; final review: [clean | N Critical, listed under Remaining Critical]

## Resolved
- [file:line] [issue] - fixed in iteration N

## Remaining Critical
- [file:line] [issue] - [reason]

## Deferred by user
- [file:line] [issue] - "[the user's words deferring it]"

## Noted
- [file:line] [Suggestion, non-correctness Warning, finding on pre-session code, or ruled out by: check] - not actioned

## Test Status
[baseline vs final, including unavailable checks]
```

Do not commit. Callers decide when to commit.
