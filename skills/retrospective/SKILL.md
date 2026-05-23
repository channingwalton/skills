---
name: retrospective
description: Use at the end of a session when the user asks how it went, what could be improved, how well the skill worked, or says "retrospective" / "retro" / "what did we learn". Surfaces gaps in the skill under examination and proposes targeted edits to fix them.
---

# Retrospective

## Overview

Run **after** a session. Reflect honestly on what worked and what didn't, then feed process-level learnings back into the skills used so next session is better.

**Core principle:** A retrospective is worthless without a concrete change. Every useful finding produces either a skill-file edit or an explicit follow-up note/update. Anything else is venting.

## When to Use

Triggers:

- "How well did [the skill / that / it] work?" / "How did that go?"
- "What could we improve?" / "retro" / "what did we learn"
- End of a feature/task, after commit, before moving on

**Not for** mid-task check-ins or routine status reports.

## The Process

```
1. AUDIT    — Scan full session transcript. Two lists: worked / didn't. Cite concrete turn/action per item.
2. SORT     — Each "didn't" item: skill gap or work lesson?
3. LOCATE   — For skill gaps: name the file and section.
4. PROPOSE  — Write the exact edit (before/after).
5. CONFIRM  — Ask "apply these?" — do nothing without a yes.
6. APPLY    — Edit skill files once approved.
```

### Sort: skill gap vs. work lesson

| Finding | Goes to |
|---------|---------|
| Rule that applies to any project | Skill file edit |
| Discipline slipped (knew rule, skipped it) | Skill edit **and** a one-line entry in the target skill's Red Flags list (create one if absent) naming the rationalisation that led to the slip |
| Codebase-specific tripwire | Proposed project note, issue comment, or documentation update |
| How user likes to work | Proposed user-preference note, if the agent has a durable memory system |
| Project/team fact | Proposed project documentation or issue update |
| Domain term | Proposed glossary or documentation entry |
| Same finding recurs (user notes "we've hit this before" or memory shows prior entries) | Promote: propose a new skill file — a one-line rule clearly isn't holding it |
| Multi-step recipe that worked and is reusable | Procedure candidate (see Output Shape) — a rule-line wouldn't carry the sequence |

Rule of thumb: *would a developer on another project benefit?* Yes → skill. No → propose the smallest durable place to record it. If no such place exists, keep it in the retrospective output as a follow-up note.

### Propose format

```
File: <path>
Section: <heading>
Before: <existing line(s) or "new subsection">
After: <proposed line(s)>
Why: <one-sentence rationale>
```

One rule per paragraph, one example max. Skills bloat when every retro adds three paragraphs.

## Output Shape

```
## Worked
- <concrete item with why>

## Didn't work
- <concrete item with why>

## Proposed skill edits
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
     2. <step>
   Destination: <new skill file path> or <existing skill + section>
   Why a procedure, not a rule: <one sentence>

## Proposed skill promotions
1. Pattern: <one-line description>
   Recurrence evidence: <prior sessions / memory entries / user statement>
   Destination: <new skill file path + proposed name>
   Why promote: <one sentence — why a line-edit isn't enough>

Apply these?
```

## Red Flags — stop and restart

- **Sycophancy.** Praising what the user just praised. "CLARIFY worked well" is empty — what premise did it *miss*?
- **Empty phrases.** "Overall it went well" / "a few small things". Be concrete or drop it.
- **Generic advice.** "Test more" / "plan better" — not an edit. Name a file and section or drop it.
- **No anchor.** Proposing an edit without a file path + section heading.
- **Pure analysis.** Paragraphs of reflection with no concrete change attached.
- **Premature application.** Applying edits before the user says yes.
- **Layer mixing.** A project fact bundled into a skill-rule finding. Project facts → follow-up notes/project docs; skill rules → skill files.
- **Sprawl.** A finding that needs 30 lines is a rewrite, not a retro — *unless* it's a genuine multi-step procedure, in which case route it to Proposed procedure candidates rather than collapsing it to a one-liner.

If any fire, stop. Restart with the sections above.

## Persistence (opt-in)

This skill does **not** write retro outputs to disk by default. Persisting retros only makes sense when paired with a meta-retro that aggregates them — silent file creation in shared use is a footgun.

Persist only if the environment variable `RETROSPECTIVE_DIR` is set (check via shell). If unset, print the retro inline and stop. Do not propose creating directories or files.

When `RETROSPECTIVE_DIR` is set:

- Write one file per retro: `$RETROSPECTIVE_DIR/YYYY-MM-DD-HHMMSS.md`, timestamp from shell `date`.
- File contents = the rendered Output Shape, unchanged.
- Confirm the resolved path with the user once before the first write of a session; write subsequent retros in that session without re-confirming.

## Meta mode (cross-session)

When the user asks for a retro across many sessions ("monthly retro", "meta retro", "what's been recurring", "review the retros"), run the same process — audit → sort → propose → confirm → apply — but over the persisted retro files rather than a single session transcript.

**Preconditions:**

- `RETROSPECTIVE_DIR` must be set and contain prior retro files. If unset or empty, stop and say so.
- Establish the window: ask which retros to include if the user didn't specify (e.g. last month, last 10 retros, all).

**What changes in the process:**

1. AUDIT — Read every retro file in the window. Build two lists: themes that recur across multiple retros (worked / didn't), each with the file references that contributed.
2. SORT — Reorder the sort table by priority:
   1. **Consolidate** — multiple existing rules saying nearly the same thing. Propose merging.
   2. **Promote** — same finding surfaced in N sessions but still living as a one-line rule. Propose a new skill file.
   3. **Procedure candidate** — recurring multi-step recipe still buried in prose. Propose extraction.
   4. **One-line edits** — only if a recurring finding doesn't fit the above.
3. PROPOSE / CONFIRM / APPLY — unchanged.

**Bias to design against:** sprawl. A monthly retro that suggests 10 changes will overwhelm. Cap proposals at the top 3-5 by recurrence count; surface the rest as a "noted but not actioned" appendix.

## Meta

This skill is itself subject to retrospection. If a retro using this skill surfaces a gap in *this* skill, edit `SKILL.md` here. Same loop.
