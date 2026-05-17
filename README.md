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

The published install surface contains six skills.

### [`chatter`](skills/chatter/SKILL.md)

Filesystem-based multi-agent chat.

Use it when you want agents to start, join, or continue a local conversation through markdown files in a shared thread directory. It includes a `chatter` helper script for posting, reading, waiting, and looping without hand-rolling the protocol.

### [`software-development`](skills/software-development/SKILL.md)

An Extreme Programming workflow for agent-assisted software development.

It pushes agents through planning, TDD, refactoring, review, commit verification, and retrospective instead of jumping straight to edits.

### [`fix-loop`](skills/fix-loop/SKILL.md)

An iterative review-fix cycle for critical issues.

Use it when you want an agent to review a change, fix critical findings, and repeat until the critical issues are resolved or need human judgement.

### [`code-reviewer`](skills/code-reviewer/SKILL.md)

An autonomous code review role.

Use it to inspect diffs, files, or directories for correctness, security, performance, maintainability, and missing tests.

### [`fixer`](skills/fixer/SKILL.md)

A targeted repair role used by `fix-loop`.

It is published for workflow completeness, but it is normally invoked by `fix-loop` rather than used as a standalone entrypoint.

### [`retrospective`](skills/retrospective/SKILL.md)

A post-session improvement loop.

Use it when you want to inspect what worked, what failed, and turn useful lessons into concrete skill edits or memory entries.

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
  fixer/
    SKILL.md
  software-development/
    SKILL.md
    references/
  retrospective/
    SKILL.md
```

Each skill is self-contained. `SKILL.md` is the entrypoint; extra scripts or references live beside it.

## Design Principles

- Small skills beat big agent frameworks.
- Process should make the agent easier to steer, not harder.
- Verification belongs in the workflow, not as an optional afterthought.
- User control matters: agents should ask when direction changes, not silently rewrite the plan.
- Skills should be easy to copy, edit, and throw away.

## Licence

MIT.
