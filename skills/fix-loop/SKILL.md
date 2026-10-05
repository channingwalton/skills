---
name: fix-loop
description: Iterative review-fix cycle that runs the host's native code review, adds house checks, then repairs Critical issues until none remain, with baseline and regression control. Use when the user says "review and fix", "find and fix bugs", "clean up the code", "fix all issues", "review then fix", or otherwise asks to both find and repair problems.
---

# Fix Loop

Run a bounded review-fix cycle until all Critical issues are resolved, marked unfixable, or the iteration cap is hit.

Review uses your host's native reviewer plus the House checks below. Repairs follow the Fixer contract below. This loop owns repairs, so the reviewer only reports.

Keep the reviewer and fixer roles separate even though one agent plays both: findings stand as written. Do not rationalise away findings because you are about to edit the code.

## Review

Run the row for your host:

| Host | Invocation | Scope |
|---|---|---|
| Claude Code | `code-review` skill with an explicit level and target: `code-review high <target>` on iteration 1, `code-review medium <target>` after. A bare call reuses the user's last level. Pass no `--fix`, `--comment`, or `ultra`. | Target is the Input or NARROW scope: paths, a branch, or a PR. |
| Codex | Shell out to `codex review` with a scope flag: `--uncommitted`, `--base <branch>`, or `--commit <sha>`. The `/review` slash command is user-only. | Diff only; a scope flag takes no prompt argument. Later iterations re-run `--uncommitted`, which covers the fixes because this loop never commits. |
| Other | Run the House checks as the whole review. | Input scope. |

Normalise findings before TRIAGE:

| Claude `code-review` | Codex `review` | Triage as |
|---|---|---|
| CONFIRMED correctness finding | `[P0]`, `[P1]` | Critical |
| PLAUSIBLE | `[P2]` | Settle with one command: proven → Critical, not ruled out → Warning |
| `simplification`, `efficiency`, `reuse` category | `[P3]` | Suggestion |

### House checks

Run these after the native review on every host; native reviewers miss them.

- **Test gaps** - new behaviour without a test is Critical. Report untested edge cases.
- **Landing surface** - open the surface the change lands on, not only the diff. A diff can be entirely correct and still ship a defect visible one file away. For a change that adds data to a handler, read that handler's authorisation guard (a worker-reachable endpoint leaked cross-worker data through three review passes). For a fix that matches or joins on an id, read the code that *writes* that id — a green disconfirmation run proves the test is load-bearing, not that the fixture is producible (a fix that matched nothing in production was committed, pushed, and defended to reviewers as intentional). For a change to a response payload or public contract, probe the generated artefact rather than reasoning about the source. For data added to any output (errors, logs, emails, API responses), name who can observe it — surfacing existing data to a new audience is an exposure.
- **Changed strings and signatures** - search the whole repo for other usages and test assertions of the old values.
- **First run** - a migration that can fail on existing production data is Critical unless the diff proves a safe backfill/default. For a change that re-enables a disabled path (CI trigger, feature flag, cron, scheduled job), check what it does on its first run in the first environment the merge reaches; read the CI branch triggers.
- **Repro** - every Critical finding carries a failing test, REPL snippet, or trace with concrete input values. Without one, it is a Warning.

## Input

Use the supplied files/directories when present. With no explicit scope:

1. uncommitted changes: `git diff --name-only` plus `git diff --name-only --staged`
2. otherwise recent work: `git diff --name-only HEAD~3`. That revision does not exist in a repo with fewer than four commits — check `git rev-list --count HEAD` first, diff from the root commit when it is shorter, and with a single commit review the files it added (`git show --name-only --format= HEAD`)
3. otherwise ask what to review

## Baseline

Before fixing, run the project's canonical verification command if discoverable from README, CONTRIBUTING, build scripts, package manager scripts, Makefile, or workspace instructions. Record pass/fail/unavailable so later failures can be separated from regressions.

## Loop

Maximum 3 iterations.

For each iteration:

1. REVIEW - announce `Review iteration N/3`; run the Review section against the current scope, then normalise its findings.
2. TRIAGE - extract Critical findings:
   - A Warning that names a concrete correctness defect introduced by the change under review is triaged as Critical unless the user explicitly defers it.
   - Quote that deferral under *Deferred by user* in the report; without a quotable deferral it stays Remaining Critical ("commit it" and "looks good" are not deferrals, and there is no "left for you to decide" list: one such list shipped three known defects in a notarised release).
   - Do not park your own true findings as carry-forwards; twice this class shipped to the edge of "done" and was only fixed when an external review re-raised it.
   - **Settle severity with a check, not by reasoning about it: a finding you cannot rule out in one command is not a Suggestion — run the command, or file it as a Warning.** Reasoned downgrades have twice buried a shipping-blocker under cosmetic framing ("I filed this as a suggestion because I reasoned about the sample as documentation. I did not run the probe that would have shown it, and the probe took one command").
   - A finding on code introduced in this session is fixed or handed off explicitly — never dropped — before the loop reports done.
   - If nothing remains to fix, stop.
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

## Deferred by user
- [file:line] [issue] - "[the user's words deferring it]"

## Noted
- [file:line] [Warning/Suggestion] - not actioned

## Test Status
[baseline vs final, including unavailable checks]
```

Do not commit. Callers decide when to commit.
