# AI Skills

[![skills.sh](https://skills.sh/b/channingwalton/skills)](https://skills.sh/channingwalton/skills)

A few useful skills I use daily.

## Quickstart

Install with `skills.sh`:

```sh
npx skills@latest add channingwalton/skills
```

Then pick the skills you want to add to your agent.

Manual install:

```sh
mkdir -p ~/.codex/skills
cp -R skills/<skill-name> ~/.codex/skills/
```

## Skills

The published install surface contains five skills.

### [`chatter`](skills/chatter/SKILL.md)

Filesystem-based multi-agent chat.

Use it when you want agents to start, join, or continue a local conversation through markdown files in a shared thread directory. It includes a `chatter` helper script for posting, reading, waiting, and looping without hand-rolling the protocol.

Depends on: no other skills.

### [`software-development`](skills/software-development/SKILL.md)

An Extreme Programming workflow for agent-assisted software development.

It pushes agents through planning, TDD, refactoring, review, commit verification, and retrospective instead of jumping straight to edits.

Depends on: [`fix-loop`](skills/fix-loop/SKILL.md) (review step) and [`retrospective`](skills/retrospective/SKILL.md) (complete step). Through `fix-loop` it also pulls in [`code-reviewer`](skills/code-reviewer/SKILL.md). It also delegates to a language-specific skill when one is installed (e.g. `scala-developer`, `unison-development`); these are not published here.

### [`fix-loop`](skills/fix-loop/SKILL.md)

An iterative review-fix cycle for critical issues.

Use it when you want an agent to review a change, fix critical findings, and repeat until the critical issues are resolved or need human judgement.

Depends on: [`code-reviewer`](skills/code-reviewer/SKILL.md) (review phase). Falls back to embedded rules if it is unavailable. The repair phase is built in (the Fixer contract).

### [`code-reviewer`](skills/code-reviewer/SKILL.md)

An autonomous code review role.

Use it to inspect diffs, files, or directories for correctness, security, performance, maintainability, and missing tests.

Depends on: no other skills.

### [`retrospective`](skills/retrospective/SKILL.md)

A post-session improvement loop.

Use it when you want to inspect what worked, what failed, and turn useful lessons into concrete skill edits or follow-up notes. See the [skill README](skills/retrospective/README.md) for details.

Depends on: no other skills.

## Structure

```text
skills/
  chatter/
    SKILL.md
    chatter
    test_chatter.py
  code-reviewer/
    SKILL.md
  fix-loop/
    SKILL.md
  software-development/
    SKILL.md
    references/
  retrospective/
    SKILL.md
    README.md
```

Each skill is self-contained. `SKILL.md` is the entrypoint; extra scripts or references live beside it.

## Evaluation

Use `evals/` to compare candidate skill edits against `origin/main` with blind prompts and scorecards.

## Licence

MIT.
