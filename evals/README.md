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

For `fixer-critical-only`, copy the fixture first and provide its path:

```sh
cp -R evals/fixtures/fixer-critical-only /tmp/fixer-a
./evals/render_case.sh fixer-critical-only . /tmp/fixer-a > /tmp/fixer-a.md
```

Paste each rendered prompt into a fresh agent session. Do not tell the agent whether it has the old or new skill.

## Cases

- `code-reviewer-review` - review recall, no `bugmagnet` dependency.
- `software-development-plan` - CLARIFY/CONFIRM discipline without generic process bloat.
- `software-development-refactor` - refactor guardrails without per-step interruption.
- `fixer-critical-only` - fixes Critical findings only.
- `chatter-start` - start-thread protocol and handoff wording.

Score outputs with [scorecard.md](scorecard.md).
