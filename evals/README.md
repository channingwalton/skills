# Skill Evaluation Harness

Use this to compare `origin/main` against a candidate skill edit with blind, repeatable prompts.

## Setup

```sh
git worktree add /tmp/skills-old origin/main
```

## Render prompts

```sh
./evals/render_case.sh code-reviewer-review /tmp/skills-old > /tmp/code-reviewer-old.md
./evals/render_case.sh code-reviewer-review . > /tmp/code-reviewer-new.md
```

For `fix-loop-critical-only`, copy the fixture first and provide its path:

```sh
cp -R evals/fixtures/fix-loop-critical-only /tmp/fix-loop-a
./evals/render_case.sh fix-loop-critical-only . /tmp/fix-loop-a > /tmp/fix-loop-a.md
```

Paste each rendered prompt into a fresh agent session. Do not tell the agent whether it has the old or new skill.

## Cases

- `code-reviewer-review` - review recall, no `bugmagnet` dependency.
- `software-development-plan` - CLARIFY/CONFIRM discipline without generic process bloat.
- `software-development-refactor` - refactor guardrails without per-step interruption.
- `fix-loop-critical-only` - fixes Critical findings only (fix-loop's Fixer contract).
- `chatter-start` - start-thread protocol and handoff wording.

Score outputs with [scorecard.md](scorecard.md).
