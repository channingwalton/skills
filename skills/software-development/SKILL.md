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
5. ✅ COMPLETE - suggest retrospective when useful.

No task is done until the review step passes or an explicit low-risk exception is recorded.

## Related Skills

- `fix-loop` - use for the DEVELOP review step. It drives `code-reviewer` and `fixer`; do not also run `code-reviewer` on the same diff.
- `retrospective` - suggest at COMPLETE when the work exposed repeated workflow gaps.
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

1. [ ] [Task description] - [acceptance criteria] - DoD: new tests for new behaviour + affected-submodule tests green (whole project if no submodules) + fix-loop clean + for UI tasks, feature exercised in a browser

Assumptions surfaced: [key premises]
First task: [task 1]
```

## 🔴 DEVELOP

Each task runs this cycle.

### 🔴 Red

Write a failing test for the next behaviour. If the change threads through multiple call sites, write coverage for each relevant caller before going green; helper-only tests can miss broken wiring. See [development reference](references/development.md).

### 🟢 Green

Make only the failing test pass. Match existing style. Avoid drive-by edits to adjacent code, comments, or formatting.

If you change a public function signature, read every caller before declaring green. Compile-passing is not enough.

### 🔵 Refactor

Clean up while tests are green and the domain is fresh. Keep refactoring while behaviour stays green; ask only when choosing between materially different cleanup directions or expanding scope. See [refactor reference](references/refactor.md).

Public signature rule still applies during refactor: after a signature change, read every caller.

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

If the user, repository, or agent platform specifies a co-author trailer, include that exact trailer. Otherwise use the current agent's appropriate public attribution if known; do not hard-code another agent's identity.

## 🔁 ITERATE

Mark a task done only after DEVELOP review passes or the targeted-verification exception is recorded. Adjust remaining tasks when new facts change the plan.

## ✅ COMPLETE

When the agreed scope is done, report the change and verification. Suggest `retrospective` only when the work exposed repeated friction or workflow gaps.

## Grounding Checks

Before relying on a claim, ground it:

| Claim | Grounding action |
|---|---|
| A note, ticket, memory, or comment says how code works | Open the source and confirm it still holds. |
| A test passed | Confirm it exercised the new behaviour, not only a happy path or name-filtered slice. |
| A tool said success | Inspect the real effect, output, or served UI when that is the user-facing contract. |
| A rename or move is done | Search the old name, path, and package across code, docs, and README. |

If you cannot ground a claim, say so rather than building on it.
