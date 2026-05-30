---
name: retrospective
description: Use on a fortnightly or post-milestone cadence, or when the user says "retrospective" / "retro" / "what's been recurring" / "what did we learn" / "review the last few sessions". Reads multiple session transcripts, distils each, and proposes targeted skill edits for patterns that recur across them. Not for single-session end-of-task review.
---

# Retrospective

Run across several sessions, not one. Distil each transcript separately, audit
the notes for recurring patterns, then propose concrete changes to the files
that guide future agent behaviour: skill files, repo instruction files such as
`AGENTS.md` or `CLAUDE.md`, README/process docs, or explicit follow-up notes.

Every useful finding must produce an exact proposed edit or follow-up note.
Single-session findings are noted but only escalated if high-severity.

## When to Use

Triggers:

- Fortnightly / end of a milestone / "let's do a retro"
- "What's been recurring?" / "what did we learn?" / "review the last few sessions"
- "How well have the skills been working lately?"

**Not for** single-session end-of-task review, mid-task check-ins, or routine
status reports. The unit of analysis is *several sessions*, not one.

## Preconditions

1. Session transcripts must be readable. Locations vary by agent and host; if
   not known, ask. If transcripts are unavailable, stop.
2. The review window must be defined: last fortnight, last N sessions, since
   last retro, or a supplied file list. If unspecified, ask.

## The Process

```
1. DISTIL   — For each transcript in the window, in isolation: read it, write
              a structured intermediate note to a tmp dir. One transcript at a
              time; do not load them all into context together.
2. MEASURE  — One aggregate pass over the whole window: where did context
              tokens go (per-tool output, hook/injection bloat, unused dumps)?
              See `references/context-audit.md`. Skip only if transcripts are
              unavailable as raw JSONL.
3. AUDIT    — Read the intermediate notes. Two lists: recurring worked /
              recurring didn't, with note references per item.
4. SORT     — Prioritise: consolidate > promote > procedure > one-line edit.
5. PROPOSE  — Write exact edits (before/after).
6. CONFIRM  — Ask "apply these?" — do nothing without a yes.
7. APPLY    — Edit the canonical source, verify the loaded file changed, and
              report the landed path. Follow symlinks; never edit versioned
              plugin/cache copies that will be overwritten.
```

### 1. DISTIL

Create a tmp working dir once (`mktemp -d`). For each transcript: read one,
write one structured note, move on. Do not load all transcripts together.

Each note should capture:

- nominal goal and what actually happened
- wrong paths pursued and why
- late-discovered failures or edge cases
- test-quality observations
- context waste: large tool outputs that went unused; note the producing tool, command, or skill `!`-injection
- rules invoked, skipped, or missing
- explicit "remember X for retro" markers, verbatim
- candidate findings

Save as `<tmpdir>/YYYY-MM-DD-HHMMSS-session.md`; get the timestamp from shell
`date`.

### 2. MEASURE

One aggregate pass over the raw transcript JSONL for the window — not per
session. Quantify where context went: tool-result output by tool, hook /
injection bloat, and content that was never used (errors, duplicate re-reads,
oversized dumps, repeated boilerplate). Trace the biggest noise back to its
source — a skill or slash-command `!`-injection, a verbose command, a full-file
read — so the finding routes to a concrete edit.

`references/context-audit.md` holds the script and the noise heuristics. Skip
this step only when the transcripts aren't available as raw JSONL.

### 3. AUDIT

Read the notes back. Build **recurring worked** and **recurring didn't** lists,
with note references per item. Do not escalate single-session findings unless
high-severity. Fold MEASURE findings in: a token-heavy injection or dump is a
recurring finding if it spans multiple sessions.

### 4. SORT

Prioritise: consolidate duplicate rules; promote repeated one-line rules into
new skills or sections; extract recurring multi-step recipes; otherwise propose
one-line edits.

Use this table to decide where each finding lands:

| Finding | Goes to |
|---------|---------|
| Rule that applies to any project | Skill file edit |
| Skill/command injects unused context (e.g. `!`-injected full diff) | Skill/command edit: cap or scope the injection |
| Discipline slipped (knew rule, skipped it) | Skill edit plus a Red Flags entry naming the rationalisation |
| Codebase-specific tripwire | Proposed project note, issue comment, or documentation update |
| Recurring project tripwire | Repo guidance such as `AGENTS.md`, `CLAUDE.md`, `README.md`, or process docs |
| User/team preference | Preference note, if durable memory exists |
| Project/team fact | Proposed project documentation or issue update |
| Domain term | Proposed definition in the project's documentation |
| Multi-step recipe that worked and is reusable | Procedure candidate |

Shared-skill portability: do not encode machine-local paths, private project
names, private tools, or one user's personal workflow into a shared skill unless
the user explicitly asks for a local fork. Put local/project-specific findings
in repo guidance, project docs, issue comments, or follow-up notes instead.

Rule of thumb: if a developer on another project would benefit, propose a skill
edit. Otherwise use the smallest durable project/local destination.

### 5. PROPOSE

```
File: <path>
Section: <heading>
Before: <existing line(s) or "new subsection">
After: <proposed line(s)>
Why: <one-sentence rationale>
```

One rule per paragraph, one example max. Cap proposals at the top 3-5 by
recurrence. Put the rest in "Noted but not actioned".

## Output Shape

Printed inline. Nothing is written to disk except the tmp intermediate notes.

```
## Recurring — worked
- <item with note references>

## Recurring — didn't work
- <item with note references>

## Proposed skill edits   (top 3–5 by recurrence)
1. File: <path>
   Section: <heading>
   Change: <old → new>
   Why: <one sentence>

## Proposed follow-up notes
- <destination or type>: <entry>

## Proposed procedure candidates
1. Name: <short verb-led title>
   Trigger: <when to invoke>
   Steps:
     1. <step>
   Destination: <new skill file path> or <existing skill + section>
   Why a procedure, not a rule: <one sentence>

## Proposed skill promotions
1. Pattern: <one-line description>
   Recurrence evidence: <which notes / sessions>
   Destination: <new skill file path + proposed name>
   Why promote: <one sentence>

## Noted but not actioned
- <single-session or lower-priority findings>

Apply these?
```

Nothing is written except tmp intermediate notes until the user approves.

## Red Flags

- Generic advice: "test more", "plan better"; name a file and section or drop it.
- No anchor: proposed edit lacks file path and section.
- Pure analysis: no proposed edit or follow-up note.
- Premature application: edits applied before user approval.
- Layer mixing: project facts placed in shared skills.
- Portability leak: local paths, private tools, or personal workflow placed in a shared skill.
- Absence treated as evidence: no recurrence in this window does not prove a past issue is fixed.
