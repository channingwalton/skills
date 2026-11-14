---
name: retrospective
description: Retrospective over several sessions — measure the user's corrections, check that earlier retro edits worked, and propose config edits at the lowest standing-cost actuator. Run fortnightly or after a milestone.
disable-model-invocation: true
---

# Retrospective

Run across several sessions, not one. The job is to reduce **mistakes, wasted
human attention, and restarts** in future sessions by improving the skills and
config they run under.

The user's attention is the **bottleneck**; agent tokens are cheap. The headline
metric is **corrections**: user turns that correct the agent — a rejected
change, rework, a decision made twice, a redirect, an interrupt, a declined tool
call. Report them per human turn. A restart is the strongest correction. A
failure that the agent recovered from alone has no corrections and ranks low. A
**wrong outcome** (a wrong answer accepted, a premature "done") keeps finding
status regardless of cost, because nobody corrected it inside the window.

Two more measures go beside it. The **guard** is questions to the user per human
turn, because an edit can turn corrections into questions. **Throughput** is
accepted changes per human hour, and it is directional only. Tokens are a
diagnosis, not the objective: trace token waste when truncation, compaction or a
session limit explains a failure.

This is a closed control loop. Sessions are the only sensor. The actuators (the
things you can change) are ordered by **standing cost** — how much they cost to
keep in place over many sessions, whether or not they ever fire. User turns rank
first, tokens second:

| Actuator | User turns | Token cost |
|----------|------------|------------|
| Gate / hook that blocks and tells the agent | None | Only when the guarded action fires |
| Skill / command | None, unless the user must invoke it or answer it | Only when invoked |
| Agent / config / tool surface | None | Structurally, per session frame |
| CLAUDE.md / AGENTS.md standing context | None | Every session, relevant or not |
| Gate / hook that asks the user | One, every time it fires | Only when the guarded action fires |

The model itself and the task distribution are not actuators; never propose
them as the fix. Every useful finding ends as an exact proposed edit or a
follow-up note.

## Preconditions

1. Session transcripts must be readable. Locations vary by agent and host; if
   not known, ask. If transcripts are unavailable, stop.
2. The review window must be defined: last fortnight, last N sessions, since
   last retro, or a supplied file list. If unspecified, ask.
3. Locate the ledger: `$RETROSPECTIVE_LEDGER` if set, otherwise ask the user
   and suggest that they export the variable. It can live anywhere durable. If
   the file does not exist, this is the first run: skip VERIFY, and create the
   ledger at CONFIRM.

## The Process

Read each reference at its step, not before.

```
1. DISTIL   — one structured note per transcript, each read in isolation.
              → references/distil.md
2. MEASURE  — one aggregate pass: corrections, throughput, restarts, context
              waste, redundancy.
              → references/corrections.md; references/context-audit.md
                when transcripts are raw JSONL
3. VERIFY   — close the loop on prior edits before proposing anything new.
              → references/verify.md, except on the first run
4. AUDIT    — recurring worked / recurring didn't, with note references.
5. SORT     — place each fix at the lowest standing-cost actuator that
              prevents it.
6. PROPOSE  — exact edits, before and after.
7. CONFIRM  — write the report to the ledger, then ask "apply these?".
8. APPLY    — edit the canonical source, then append the ledger rows.
              → references/ledger.md
```

### 1. DISTIL

Read `references/distil.md` first. It is self-contained: give each distil
subagent that file and its one transcript, and nothing else.

- Create one working directory with `mktemp -d`. Before you distil, reuse the
  notes that an earlier aborted run left, and distil only what is missing.
- Spawn at most ~12 distil subagents per retro session. The cap counts every
  spawn, not only concurrent ones, because a larger fan-out can reach the
  session limit. Distil the remainder yourself, and state in the report how many
  sessions the subagents examined and how many you examined.

### 2. MEASURE

One aggregate pass over the window, not per session. Use the bundled
`retro.py` beside this file (`measure`, `context` and `restarts`); never
reimplement it. It reads Claude Code's JSONL transcript schema. On another
schema it reports near-zero totals instead of an error, so check the caveat in
`context-audit.md` first. When the transcripts are not raw JSONL, or a port
costs more than it saves, cost the failures from the DISTIL notes alone.

Five outputs:

1. **Corrections**: tally each failure's corrections from the DISTIL notes, and
   take human turns, interrupts, declined calls and questions from the script.
   Report the correction rate and the question rate per human turn. Weigh each
   failure by its corrections, not by count: one failure that the user
   corrected four times can outweigh the whole tail. Distrust a clean percentage
   on a small sample of papercuts.
2. **Throughput**: accepted changes per human hour, from the same script.
3. **Restarts**: abandoned-and-re-attempted work across transcripts, which
   DISTIL cannot see. Read the abandoned session's tail, and treat whatever
   caused the abandonment as the failure.
4. **Context waste**: where the tokens went, traced to the skill, command or
   habit that produced them. Propose an edit only when the waste explains a
   corrected failure; otherwise note it.
5. **Redundancy**: skill sections or installed surfaces that cost tokens with no
   observed behavioural change, overlap another active skill, or repeat default
   behaviour. Require evidence that the rule's trigger occurred, or clear
   overlap; one window with no use is not enough.

### 3. VERIFY

Skip this step on the first run. Otherwise read the ledger, and work
`references/verify.md` for each edit that is still open. Each open edit ends
with one verdict: `confirmed-by-replay`, `refuted-by-replay`,
`confirmed-effective`, `ineffective`, or `untested-this-window`.

### 4. AUDIT

Read the notes back. Build **recurring worked** and **recurring didn't** lists,
with note references per item. Escalate a single-session finding only when it is
high-severity. These are recurring by definition:

- a token-heavy injection or dump that spans several sessions;
- a restart, even from one instance, because it is high-severity;
- a **decision made twice**: a user correction or decision that appears in two
  sessions;
- an `ineffective` prior edit.

A **harness-shaped** failure (tool loading, gating, polling, path handling) is
general by construction and needs no cross-paradigm recurrence test. A paradigm
contrast does not establish generality, because the work mix seldom gives
comparable populations.

### 5. SORT

Place each fix at the **lowest standing-cost actuator that prevents it**. A new
CLAUDE.md rule, or a gate that asks the user, is the expensive actuator; reach
for it last.

- A `present-not-consulted` failure means that standing guidance did not reach
  the point of action. Move the guidance to a gate or an on-demand skill that
  fires when the action is imminent. Louder standing guidance feeds the
  blindness and taxes every session.
- A `present-contradicted` failure is the floor. No actuator fixes it; note it.
- The prevention must cost less, over the expected sessions, than the failure
  it prevents. Weigh corrections first, then tokens.
- Consolidate `confirmed-effective` edits (merge and lock — integral reset).
  Revise or revert an `ineffective` edit with a different actuator; never stack
  a second patch on it (integrator windup).

| Finding | Goes to |
|---------|---------|
| Preventable at the point of action | Blocking gate/hook in config |
| Needs context at a specific moment | Skill/command edit (on-demand) |
| Topology / delegation / tool availability | Agent, config, or tool-surface edit |
| Needs the user's judgement, and nothing else | Gate/hook that asks the user |
| Skill/command injects unused context | Skill/command edit: cap or scope the injection |
| Skill/rule appears redundant after excitation or overlap check | Skill/command edit: trim, merge, demote to reference, or drop |
| Discipline slipped (knew rule, skipped it) | Prefer a blocking gate; CLAUDE.md + Red Flags entry only if no gate is possible |
| Rule that genuinely must be always-on and applies to any project | Skill file or CLAUDE.md (last resort) |
| Codebase-specific tripwire | Project note, issue comment, or repo guidance |
| Recurring project tripwire | Repo guidance (`AGENTS.md`, `CLAUDE.md`, `README.md`, process docs) |
| User/team preference | Preference note, if durable memory exists |
| Domain term | Definition in project documentation |
| Multi-step recipe that worked and is reusable | Procedure candidate |

Keep shared skills portable: put machine-local paths, private project names,
private tools and one user's workflow in repo guidance, project docs or notes,
unless the user asks for a local fork. If a developer on another project would
benefit, propose a skill edit; otherwise use the smallest durable local
destination.

### 6. PROPOSE

```
File: <path>
Actuator: <gate | skill | command | agent | config | tool | CLAUDE.md>
Section: <heading>
Targets failure class: <stable id, for the ledger>
Before: <existing line(s) or "new subsection">
After: <proposed line(s)>
Cost traded: <corrections (then tokens) this prevents vs standing cost of the fix>
Why this actuator, not a lower- or higher-standing-cost one: <one sentence>
```

One rule per paragraph, one example max. Cap proposals at the top 3-5 by
**cost-weighted** recurrence, and put the rest in "Noted but not actioned". An
edit that cannot name the failure class it targets is a note, not a proposal.

Check the ledger's REJECTED rows first. If a proposal targets a failure class
with a rejected row, drop it, or state what is different this time: a new
actuator, new evidence, or a changed cost. A repeated proposal spends the user's
attention on a decision they already made.

### 7. CONFIRM

**Write the report to the ledger as a `proposed, not applied` section before you
ask.** Then an unanswered question loses only the edits, not the run.

Then present the report (Output Shape below) and ask with **AskUserQuestion, not
prose**. Do nothing further without a yes. Record which proposals the user
declines, and the reason if one is given; they become REJECTED rows at APPLY.

### 8. APPLY

After CONFIRM only. Edit the canonical source, verify that the loaded file
changed, and report the landed path. Follow symlinks; never edit versioned
plugin or cache copies that an update will overwrite.

A gate edit is not applied until its matcher has been replayed against the real
in-window command forms, including forms that the standing rules mandate (e.g.
`git -C <path>`). A matcher defect otherwise shows only after APPLY.

Then read `references/ledger.md`. Change the `proposed, not applied` section to
its final state, and append one row per applied edit, one REJECTED row per
proposal that did not land, and one SUMMARY row, even when the user approved
nothing.

## Output Shape

Printed inline, and written to the ledger as the `proposed, not applied` section
at CONFIRM.

```
## Loop check (VERIFY)
- <prior edit>: <verdict>
  (<edit still present? replayed or observed? exercised this window? cost change?>)
- Trend: <this window's headline vs prior SUMMARY rows; cumulative edit
  hit-rate> (directional only)

## Cost summary
- Corrections, the correction rate per human turn, and the few failures that
  caused most of them.
- Questions to the user per human turn (the guard), against prior SUMMARY rows.
- Throughput: accepted changes per human hour, against prior SUMMARY rows.
- Restarts, with the cause of each abandonment.
- Wrong-outcome mistakes, listed regardless of cost.
- Token waste that caused a failure above; the window's token total for the
  trend only.

## Recurring — worked
- <item with note references>

## Recurring — didn't work
- <item with note references, cost-weighted>

## Proposed edits   (top 3–5, each in the PROPOSE format)

## Floor (not actionable)
- <present-contradicted failures>

## Proposed follow-up notes
- <destination or type>: <entry>

## Proposed procedure candidates
1. Name / Trigger / Steps / Destination / Why a procedure not a rule

## Proposed skill promotions
1. Pattern / Recurrence evidence / Destination / Why promote

## Noted but not actioned
- <single-session, low-cost, or floor findings>
```

## Red Flags

Check the finished report for these five. Each one happens while the step that
forbids it is followed:

- **Pure analysis** — a finding with no proposed edit or note, or an edit with
  no file path and section. Generic advice ("test more") is this failure.
- **Wrong actuator** — the fix sits higher in standing cost than the failure
  warrants: louder standing context for `present-not-consulted`, or corrections
  turned into questions to the user.
- **Count over cost, cost over outcome** — a papercut weighted equal to an
  expensive misdirection, an uncorrected failure ranked high on tokens, or a
  cheap wrong outcome dropped. Both dimensions rank; neither gates the other.
- **Absence read as evidence** — no recurrence proves nothing when the failure
  mode was never exercised, a one-sided replay is not causal, and one window is
  not a trend.
- **Premature application** — edits applied before the user says yes at CONFIRM.
