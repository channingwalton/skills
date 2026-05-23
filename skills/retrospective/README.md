# retrospective

A post-session improvement loop. Inspects what worked, what failed, and turns useful lessons into concrete skill edits or memory entries.

See [`SKILL.md`](./SKILL.md) for the full process, sort table, output shape, and red flags.

## When to invoke

- "How did that go?" / "retro" / "what did we learn"
- End of a feature or task, after commit, before moving on

Not for mid-task check-ins.

## Install

Via [skills.sh](https://skills.sh) from the repo root:

```sh
npx skills@latest add channingwalton/skills
```

Or manually:

```sh
mkdir -p ~/.codex/skills
cp -R skills/retrospective ~/.codex/skills/
```

Substitute your agent's skill directory if not Codex.

## Configuration

By default, retros print inline and write nothing to disk.

To enable cross-session persistence (e.g. for a future meta-retro that aggregates findings), set:

```sh
export RETROSPECTIVE_DIR=~/path/to/retros
```

When set, each retro is written to `$RETROSPECTIVE_DIR/YYYY-MM-DD-HHMMSS.md`. If unset, the skill never touches the filesystem.
