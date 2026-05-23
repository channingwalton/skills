# retrospective

A cross-session improvement loop. Distils several session transcripts into structured notes, audits across them for recurring patterns, and turns those into concrete skill edits or follow-up notes.

See [`SKILL.md`](./SKILL.md) for the full process, sort table, output shape, and red flags.

## When to invoke

- Fortnightly / end of a milestone / "let's do a retro"
- "What's been recurring?" / "what did we learn?" / "review the last few sessions"

Not for single-session end-of-task review or mid-task check-ins. The unit of analysis is several sessions, not one.

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

## Persistence

The retro prints inline. The only files it writes are the per-session intermediate notes, into a throwaway tmp dir (`mktemp -d`). No configuration or env var needed.

Session transcripts (the input) live in different places per agent and host — the skill asks where they are if the location isn't obvious. To flag something for the next retro mid-session, just say "remember X for retro"; it lands in the transcript and the distil step picks it up.
