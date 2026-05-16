# AI Skills

Small, opinionated skills for AI coding agents.

These are the skills I use to keep agent work grounded: clear process, tight feedback loops, explicit decisions, and less conversational sludge.

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

### `chatter`

Filesystem-based multi-agent chat.

Use it when you want agents to start, join, or continue a local conversation through markdown files in a shared thread directory. It includes a `chatter` helper script for posting, reading, waiting, and looping without hand-rolling the protocol.

### `software-development`

An Extreme Programming workflow for agent-assisted software development.

It pushes agents through planning, TDD, refactoring, review, commit verification, and retrospective instead of jumping straight to edits.

### `retrospective`

A post-session improvement loop.

Use it when you want to inspect what worked, what failed, and turn useful lessons into concrete skill edits or memory entries.

## Structure

```text
skills/
  chatter/
    SKILL.md
    chatter
    test_chatter.py
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
