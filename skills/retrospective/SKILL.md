---
name: retrospective
description: Use on a fortnightly or post-milestone cadence, or when the user says "retrospective" / "retro" / "what's been recurring" / "what did we learn" / "review the last few sessions". Reads multiple session transcripts, distils each, and proposes targeted skill edits for patterns that recur across them. Not for single-session end-of-task review.
---

# Retrospective

## Overview

Run across **multiple sessions** — a fortnight of work, or since the last
retro. Distil each session transcript into a structured note, audit across
those notes for patterns, then feed recurring process-level learnings back
into the skills used.

**Core principle:** A retrospective is worthless without a concrete change.
Every useful finding produces either a skill-file edit or an explicit
follow-up note. Anything else is venting.

**Cadence principle:** A single session is too small a sample. A pattern is
worth acting on when it recurs across sessions — that is what this skill
looks for. Single-session findings are noted but only escalated if
high-severity.

## When to Use

Triggers:

- Fortnightly / end of a milestone / "let's do a retro"
- "What's been recurring?" / "what did we learn?" / "review the last few sessions"
- "How well have the skills been working lately?"

**Not for** single-session end-of-task review, mid-task check-ins, or routine
status reports. The unit of analysis is *several sessions*, not one.

## Preconditions

1. **Transcripts must be readable.** Session transcripts live in different
   places depending on the agent (Claude Code, Codex, Gemini, etc.) and the
   host. There is no fixed path. If the location isn't already known or
   obvious from context, **ask the user where this window's transcripts are
   before starting.** If transcripts aren't saved anywhere readable, stop and
   say so — that's the one piece of infrastructure this skill needs.

2. **The window must be defined.** The user specifies it (last fortnight,
   last N sessions, since the last retro, a list of files). If unspecified,
   ask before starting.

## The Process

```
1. DISTIL   — For each transcript in the window, in isolation: read it, write
              a structured intermediate note to a tmp dir. One transcript at a
              time; do not load them all into context together.
2. AUDIT    — Read the intermediate notes. Two lists: recurring worked /
              recurring didn't, with note references per item.
3. SORT     — Prioritise: consolidate > promote > procedure > one-line edit.
4. PROPOSE  — Write exact edits (before/after).
5. CONFIRM  — Ask "apply these?" — do nothing without a yes.
6. APPLY    — Edit the *canonical source* of each skill, then verify it
              landed. Resolve which file the loading agent actually reads:
              follow symlinks to the real file; never edit a version-pinned
              plugin cache (e.g. `.../plugins/.../5.1.0/...`) — those wipe on
              update. If a skill lives in more than one tree, edit the
              canonical source. After editing, confirm the change is present
              in the file the agent loads and report the *landed* path —
              "approved" is not "landed".
```

### 1. DISTIL

Create a tmp working dir once at the start (e.g. `mktemp -d`). Then, treating
**each transcript as its own task** — read one, write its note, move on; never
hold all transcripts in context at once — produce a note containing:

- What the session was nominally about
- What actually happened (short narrative, including rework)
- Wrong paths pursued, and why
- Corner cases / failures discovered late — and at what point they surfaced
- Test-quality observations: tests that passed but didn't cover the risk;
  tests that caught something the implementation missed
- Skill rules invoked, skipped, or that would have helped if they existed
- Any explicit **"remember X for retro"** markers the user dropped during the
  session — these are deliberate signals; capture them verbatim
- Candidate findings — flagged generously. False positives are cheap here;
  the AUDIT step filters them.

Save each as `<tmpdir>/YYYY-MM-DD-HHMMSS-session.md` (timestamp from shell
`date`).

### 2. AUDIT

Read the notes back. Build two lists — **recurring worked** and **recurring
didn't** — each item citing the notes it came from. A finding that appears in
one note only is noted but not escalated unless it's high-severity.

### 3. SORT

Prioritise proposals in this order:

1. **Consolidate** — multiple existing rules saying nearly the same thing.
   Propose merging them.
2. **Promote** — the same finding recurring across N sessions but still living
   as a one-line rule. Propose a new skill file; a line clearly isn't holding it.
3. **Procedure candidate** — a recurring multi-step recipe still buried in
   prose. Propose extracting it (a rule-line can't carry a sequence).
4. **One-line edit** — only if a recurring finding fits none of the above.

Within that, use the gap-vs-lesson table to decide *where* each finding lands:

| Finding | Goes to |
|---------|---------|
| Rule that applies to any project | Skill file edit |
| Discipline slipped (knew rule, skipped it) | Skill edit **and** a one-line entry in the target skill's Red Flags list (create one if absent) naming the rationalisation that led to the slip |
| Codebase-specific tripwire | Proposed project note, issue comment, or documentation update |
| Project tripwire that has already recurred | Promote into the repo's own docs (AGENTS.md / CLAUDE.md / README) — agents read repo docs, not your memory. Only if verified, project-owned, non-sensitive, and the user has approved the exact text |
| How the user likes to work | Proposed user-preference note, if the agent has a durable memory system |
| Project/team fact | Proposed project documentation or issue update |
| Domain term | Proposed definition in the project's documentation |
| Multi-step recipe that worked and is reusable | Procedure candidate |

Rule of thumb: *would a developer on another project benefit?* Yes → skill.
No → the smallest durable place to record it. If no such place exists, keep it
as a follow-up note in the output.

### Propose format

```
File: <path>
Section: <heading>
Before: <existing line(s) or "new subsection">
After: <proposed line(s)>
Why: <one-sentence rationale>
```

One rule per paragraph, one example max. Skills bloat when every retro adds
three paragraphs.

**Cap proposals at the top 3–5 by recurrence.** The rest go in a "Noted but
not actioned" appendix.

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

## Red Flags — stop and restart

- **Sycophancy.** Praising what the user just praised. "CLARIFY worked well"
  is empty — what premise did it *miss*?
- **Empty phrases.** "Overall it went well" / "a few small things". Concrete or drop it.
- **Generic advice.** "Test more" / "plan better" — not an edit. Name a file
  and section or drop it.
- **No anchor.** Proposing an edit without a file path + section heading.
- **Pure analysis.** Paragraphs of reflection with no concrete change attached.
- **Premature application.** Applying edits before the user says yes.
- **Layer mixing.** A project fact bundled into a skill-rule finding. Project
  facts → follow-up notes/project docs; skill rules → skill files.
- **Sprawl.** A finding that needs 30 lines is a rewrite, not a retro —
  *unless* it's a genuine multi-step procedure, in which case route it to
  procedure candidates.
- **Absence is not evidence.** A pattern not appearing in this window doesn't
  mean a previous edit fixed it — the situations that would surface it may not
  have come up. When judging whether a past pattern has diminished, distinguish
  "diminished" from "can't tell".

If any fire, stop. Restart with the sections above.
