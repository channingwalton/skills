# Skill Evaluation Harness

Use this to compare `origin/main` against a candidate skill edit with blind, repeatable prompts.

## Setup

```sh
git worktree add /tmp/skills-old origin/main
```

## Render prompts

```sh
./evals/render_case.sh software-development-plan /tmp/skills-old > /tmp/sd-plan-old.md
./evals/render_case.sh software-development-plan . > /tmp/sd-plan-new.md
```

For `fix-loop-critical-only`, copy the fixture first and provide its path:

```sh
cp -R evals/fixtures/fix-loop-critical-only /tmp/fix-loop-a
./evals/render_case.sh fix-loop-critical-only . /tmp/fix-loop-a > /tmp/fix-loop-a.md
```

For `mikado-pricing`, make the copied fixture a git repository with its pre-commit hook enabled:

```sh
cp -R evals/fixtures/mikado-pricing /tmp/mikado-a
git -C /tmp/mikado-a init -q -b main
git -C /tmp/mikado-a config core.hooksPath .githooks
git -C /tmp/mikado-a add -A
git -C /tmp/mikado-a commit -qm "Fixture baseline"
./evals/render_case.sh mikado-pricing . /tmp/mikado-a > /tmp/mikado-a.md
```

After the run, check that every commit on the branch is green:

```sh
for c in $(git -C /tmp/mikado-a rev-list --reverse main..mikado/<slug>); do
  git -C /tmp/mikado-a checkout -q "$c" && /tmp/mikado-a/bin/check > /dev/null 2>&1 || echo "red: $c"
done
```

Paste each rendered prompt into a fresh agent session. Do not tell the agent whether it has the old or new skill.

## Cases

- `software-development-plan` - CLARIFY/CONFIRM discipline without generic process bloat.
- `software-development-refactor` - refactor guardrails without per-step interruption.
- `fix-loop-critical-only` - fixes Critical findings only (fix-loop's Fixer contract).
- `chatter-start` - start-thread protocol and handoff wording.
- `mikado-pricing` - Mikado run: baseline, revert instead of fixing forward, graph-only commits through a pre-commit hook, green leaf commits.

Score outputs with [scorecard.md](scorecard.md).
