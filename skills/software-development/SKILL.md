---
name: software-development
description: Software development workflow for implementation work that changes code or tests. Use when asked to implement, modify, or fix software behaviour; do not use for shell help, Git-only work, read-only investigation, configuration questions, or general explanation unless code changes are requested. Coordinates planning, TDD, review, and optional commit.
---

# Software Development

Use this skill for implementation work that changes code or tests. Do not use it for shell help, CLI usage, Git-only work, read-only investigation, configuration questions, or general technical explanation unless the user explicitly asks for code changes.

The workflow is:

1. 📋 PLAN - understand and slice the work.
2. 🔴 DEVELOP - red, green, refactor, review.
3. 💾 COMMIT - only when requested or confirmed.
4. 🔁 ITERATE - repeat until the agreed scope is done.
5. ✅ COMPLETE - disconfirm the result.

No task is done until the review step passes or an explicit low-risk exception is recorded.

## Related Skills

- `fix-loop` - use for the DEVELOP review step. It drives `code-reviewer` and repairs Critical findings itself; do not also run `code-reviewer` on the same diff.
- Language skill - use the relevant language skill for Red and Green when one is installed.

## 📋 PLAN

Plan before coding when the work is ambiguous, user-facing, multi-step, or risky. For small explicit fixes, use a compressed plan and move straight to the first test.

Sequence: DISCUSS -> CLARIFY -> SLICE -> FALSIFY -> CONFIRM. See [planning reference](references/planning.md) for detailed checklists and examples.

- DISCUSS: identify the real outcome and affected surface.
- CLARIFY: restate hidden premises as "Given [premises], then [conclusion]" and challenge missing or obvious assumptions.
- SLICE: create small vertical tasks ordered by dependency and value.
- FALSIFY: ask what scenario would prove the understanding wrong.
- CONFIRM: present the ordered tasks and get agreement on the first task before coding.

Use this task format when a visible plan is needed:

```markdown
## Tasks for [Feature]

1. [ ] [Task description] - [acceptance criteria] - DoD: new tests for new behaviour + affected-submodule tests green (whole project if no submodules) + fix-loop clean + for UI/runtime tasks, the changed behaviour exercised in the running app (browser **or** native app — drive it, or capture a screenshot; use your agent's run/verify skills if it has them); if it truly can't be run, report it unverified — "build/tests green" is not "done"

Assumptions surfaced: [key premises]
First task: [task 1]
```

## 🔴 DEVELOP

Each task runs this cycle.

### 🔴 Red

Write a failing test for the next behaviour. If the change threads through multiple call sites, write coverage for each relevant caller before going green; helper-only tests can miss broken wiring. See [development reference](references/development.md).

### 🟢 Green

Make only the failing test pass. Avoid drive-by edits to adjacent code, comments, or formatting.

If you change a public function signature, read every caller before declaring green. Compile-passing is not enough.

### 🔵 Refactor

Clean up while tests are green and the domain is fresh, one transformation at a time, keeping tests green after each. Ask only when choosing between materially different cleanup directions or expanding scope. If a cleanup alters behaviour or public API, return to DEVELOP and write a test first. State the test status; if tests were not run, say so.

Public signature rule still applies during refactor: after a signature change, read every caller.

After any out-of-band mutation (formatter, codegen, `sed`/script rewrite), re-read a file before editing it; for bulk renames prefer your edit tool's own replace-everywhere over a shell rewrite, and run the formatter at the gate, not between edit batches.

### 🔍 Review

Run `fix-loop` unless the change is pure non-code, or is one-line build/config wiring with no production logic. If using that targeted-verification exception, state the skip and name the command run in the final response.

Stop if critical findings or test regressions remain. The task is not done.

Treat new behaviour without new tests as critical, even if sibling code lacks tests. Precedent is not permission.

Edge cases flagged as critical by review must be covered before the task is done.

## 💾 COMMIT

Commit only when the user asks for it or confirms it.

Before committing:

1. Inspect `git status --short --branch` and the diff.
2. Run the project's canonical verification command from README, CONTRIBUTING, build scripts, package manager scripts, Makefile, or workspace instructions.
3. If broad checks include substantial pre-existing branch changes outside the task, say so and prefer targeted verification unless the user explicitly asks for the full check.
4. Summarise what will be committed and ask for confirmation.

No red commits. No pushes without a green check for the commit being pushed.

If review is deferred across a batch, record it as a task at the moment of deferral — an in-context promise does not survive a restart, and an unreviewed batch must not be pushed.

If the user, repository, or agent platform specifies a co-author trailer, include that exact trailer. Otherwise use the current agent's appropriate public attribution if known; do not hard-code another agent's identity.

## 🔁 ITERATE

Mark a task done only after DEVELOP review passes or the targeted-verification exception is recorded. Adjust remaining tasks when new facts change the plan.

## ✅ COMPLETE

Before reporting the scope done, disconfirm it — this is the FALSIFY step from PLAN, applied to the result instead of the understanding:

1. For each behaviour you are about to call done, name the single check that would prove that claim **false**, then run it. Apply the Grounding Checks below: a claim that something *works* or *changed* is grounded by inspecting the real artifact (the rendered element, the served response, the actual file) — not by re-reading the code or trusting a green suite.
2. A passing test counts only once you have confirmed it exercises the new behaviour — that it fails when the behaviour is removed, not merely that the suite is green.
3. The check must observe the claim's own signal on the real substrate. A claim about live/real behaviour is not grounded by a fake/mock gateway, a green suite, or a proxy (a DB row, a projection, a log stream with silent failure paths) — say what you observed and on what substrate. If the DoD names a rendered UI, observe the rendered surface, not the store/API behind it. A reported runtime bug is "fixed" only when the symptom is reproduced-then-gone or traced to the exact failing line — never fix-by-analogy.
4. If a check cannot be run, report that behaviour as **unverified**, not done — and do not commit a behavioural fix whose operative cause is unconfirmed.

When disconfirming by mutating a file, revert with `git checkout -- <file>` and verify with `git diff` — never a `cp` backup restore (an aliased `cp -i` declines silently and has left mutations in tracked files).

Then report the change and the verification you ran.

## Grounding Checks

Before relying on a claim, ground it:

| Claim | Grounding action |
|---|---|
| A note, ticket, memory, or comment says how code works | Open the source and confirm it still holds. |
| A test passed | Confirm it exercised the new behaviour, not only a happy path or name-filtered slice. |
| A tool said success | Inspect the real effect, output, or served UI when that is the user-facing contract. |
| A rename or move is done | Search the old name, path, and package across code, docs, and README. |

If you cannot ground a claim, say so rather than building on it.
