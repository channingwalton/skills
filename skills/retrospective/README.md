# retrospective

A cross-session improvement loop for harness configuration. Distils several
session transcripts into structured notes, measures **token-weighted wasted
effort**, proposes config edits placed at the **cheapest-to-run actuator** that
prevents each failure, and **verifies** that prior retros' edits actually reduced
the cost they targeted before proposing more.

It is a closed control loop: sessions are the only sensor; the actuators are the
things you can change (gates/hooks, skills, commands, agents, config, tool
surface, standing context like CLAUDE.md / AGENTS.md). Two things are explicitly
not actuators and never the proposed fix: the model itself, and the task
distribution.

See [`SKILL.md`](./SKILL.md) for the full process, actuator ordering, sort table,
output shape, and red flags. The MEASURE step's context-audit script and the
manual cost-per-failure method are in
[`references/context-audit.md`](./references/context-audit.md).

## When to invoke

- Fortnightly / end of a milestone / "let's do a retro"
- "What's been recurring?" / "what did we learn?" / "review the last few sessions"
- "How well have the skills been working lately?"

Not for single-session end-of-task review or mid-task check-ins. The unit of
analysis is several sessions, not one.

## What it does differently from a plain retro

- **Cost-weighted, not count-based.** One expensive misdirection outweighs a
  tail of papercuts; the headline is wasted effort, not a failure count.
- **Actuator placement.** Each fix goes to the latest-costing actuator that
  prevents it (a gate that costs nothing until it fires beats a CLAUDE.md line
  that taxes every session). It resists answering failures with more standing
  context.
- **Closed loop.** It keeps a small ledger of the edits it applies and checks,
  next time, whether each edit stuck and whether the failure it targeted got
  cheaper — so corrections are verified, not assumed.

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

The retro prints inline. It writes only two things to disk:

1. **Per-session intermediate notes** — into a throwaway tmp dir (`mktemp -d`).
   Discarded after the run.
2. **The VERIFY ledger** — a small durable file the retro writes to itself at
   APPLY and reads at the next retro. One row per applied edit: what changed,
   which actuator, the failure class it targets, the edit's `after` text
   verbatim (used next time to check the edit is still in force), and
   optionally a config fingerprint. It must persist across sessions and live
   somewhere read only at retro time — never injected into a working session's
   context. The skill does not prescribe a location or storage format; it asks
   where to keep it on first run, and works the same whether or not the files it
   edits are version-controlled (it uses the stored `after` text, not a VCS, to
   verify an edit survived).

On the **first run** (no ledger yet) VERIFY is skipped and the ledger is created
at APPLY in a location you confirm.

There is deliberately **no on-the-fly hook** writing observations during
sessions: the transcript is already the complete on-the-fly record, and an
in-session writer would spend live tokens in the very sessions the retro exists
to make cheaper. To flag something for the next retro mid-session, just say
"remember X for retro" — it lands in the transcript and DISTIL picks it up. The
agent's own in-session "that was wrong" recognitions are harvested the same way.

Session transcripts (the input) live in different places per agent and host —
the skill asks where they are if the location isn't obvious. If they aren't
available as raw JSONL, the MEASURE step's context-audit script is skipped (the
rest still runs).
