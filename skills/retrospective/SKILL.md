---
name: retrospective
description: >-
  Use on a fortnightly or post-milestone cadence, or when the user says
  "retrospective" / "retro" / "what's been recurring" / "what did we learn" /
  "review the last few sessions". Reads multiple session transcripts, distils
  each, measures token-weighted wasted effort (including abandoned-and-restarted
  sessions), and proposes targeted config edits — placed at the lowest standing-cost actuator that prevents the failure
  — then verifies that prior retros' edits actually reduced the cost they
  targeted. Not for single-session end-of-task review.
disable-model-invocation: true
---

# Retrospective

Run across several sessions, not one. The job is to reduce **mistakes, wasted
tokens, and restarts** in future sessions by improving the skills and config
they run under. The headline metric is **token-weighted wasted effort** — calls
and tokens spent on wrong paths, misdirections, revisions, and incorrect tool
use that a correctly-applied actuator would have avoided — with two findings
that keep standing regardless of token cost: wrong-outcome mistakes (a wrong
answer accepted, a premature "done") and abandoned-and-restarted sessions.

This is a closed control loop. Sessions are the only sensor. The actuators (the
things you can change) are, ordered by **standing cost** — how much they cost to
keep in place over many sessions, whether or not they ever fire:

| Actuator | When it costs tokens | Prefer for |
|----------|---------------------|------------|
| Gate / hook (config) | Only when the guarded action fires | Failures preventable at the point of action |
| Skill / command | Only when invoked | Failures needing context at a specific moment |
| Agent / config / tool surface | Structurally, per session frame | Failures from topology, delegation, tool availability |
| CLAUDE.md / AGENTS.md standing context | Every session, relevant or not | Last resort — always-on token tax |

Two things are **not** actuators and must never be the proposed fix: the model
itself (see `present-contradicted` below), and the task distribution.

Every useful finding must produce an exact proposed edit or follow-up note,
placed at the **lowest standing-cost actuator that can prevent it**. Single-session
findings are noted but only escalated if high-severity.

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
3. The VERIFY ledger must be locatable: `$RETROSPECTIVE_LEDGER` if set,
   otherwise ask the user (and suggest exporting it for future runs). It is a
   small file the retro writes at APPLY and reads at the next retro, holding
   applied edits, rejected proposals, and one summary row per run; it can
   live anywhere durable across sessions. If the file does not exist yet, this
   is the first run — VERIFY is skipped and the ledger is created at APPLY.

## The Process

```
1. DISTIL   — For each transcript in the window, in isolation: read it, isolate
              genuine failures (not normal iteration), write a structured note.
              One transcript at a time; do not load them all together.
2. MEASURE  — One aggregate pass: where did tokens go (per-tool output, hook/
              injection bloat, unused dumps), what did each failure COST in
              wasted calls/tokens, AND which sessions were abandoned and
              restarted. See `references/context-audit.md`.
3. VERIFY   — Read the ledger. For each open prior edit: is it still IN FORCE,
              was its failure mode EXERCISED this window (or can it be
              REPLAYED), and did its cost FALL? Close the loop before proposing
              anything new.
4. AUDIT    — Recurring worked / recurring didn't, with note references.
5. SORT     — Place each fix at the lowest standing-cost actuator that prevents it;
              cap by recurrence, weight by cost.
6. PROPOSE  — Exact edits (before/after).
7. CONFIRM  — Ask "apply these?" — do nothing without a yes.
8. APPLY    — Edit canonical source, verify the loaded file changed, record the
              edit in the ledger, recording its `after` text verbatim as the
              presence anchor. Follow symlinks; never edit
              versioned plugin/cache copies that will be overwritten.
```

### Step detail lives in `references/`

Read each file at its step, not before. Two of the four are often not opened at
all: VERIFY is skipped on a first run, and the ledger formats are needed only
after the user approves.

| File | Read it |
|---|---|
| `references/distil.md` | At DISTIL — and hand it to each distil subagent |
| `references/context-audit.md` | At MEASURE, when transcripts are raw JSONL |
| `references/verify.md` | At VERIFY, unless this is the first-ever run |
| `references/ledger.md` | At APPLY, after the user says yes at CONFIRM |

### 1. DISTIL

**Read `references/distil.md` before starting.** It holds the failure-isolation
test, the in-window availability tags, and the per-failure capture list, and it
is written to be self-contained — when fanning out, give each distil subagent
that file plus its one transcript and nothing else.

Orchestration rules, needed here rather than in the reference:

- One tmp working dir (`mktemp -d`), one transcript at a time, one structured
  note each. Do not load them all together.
- Reuse surviving notes from an earlier aborted run before distilling afresh.
- Cap concurrent distil subagents at ~12, each with a namespaced scratch path.
  A 40-agent fan-out exhausted the session limit mid-run and abandoned an entire
  retro (~1.85M tokens), and shared scratch paths have caused agents to clobber
  each other's extractions.

Each note carries three fields the later steps sort on: an in-window
availability tag (`present-not-consulted`, `present-contradicted`,
`absent-via-truncation`, `absent-via-never-retrieved`, `absent-via-compaction`,
`cant-tell`), a **cost**, and an **outcome severity** independent of that cost.

### 2. MEASURE

One aggregate pass over the raw transcript JSONL for the window — not per
session. Four outputs:

1. **Context waste**: tool-result output by tool, hook/injection bloat, content
   never used (errors, duplicate re-reads, oversized dumps, boilerplate). Trace
   the biggest noise to its source — a skill/command `!`-injection, a verbose
   command, a full-file read — so the finding routes to a concrete edit.
2. **Cost per failure**: from the DISTIL notes, tally wasted calls/tokens per
   isolated failure. The retro's headline is **cost-weighted, not count-based.**
   A clean-looking percentage on a small sample of mostly-papercut failures is
   the result to distrust — one expensive ungated failure can outweigh the
   entire tail. One exception: wrong-outcome mistakes (flagged in DISTIL) keep
   finding status regardless of token cost.
3. **Restarts** (cross-transcript): scan the window for abandoned-and-re-attempted
   work — near-duplicate opening prompts, the same task resumed in a fresh
   session, sessions ending mid-task with no wrap-up. Per-transcript DISTIL
   cannot see these: an abandoned session just looks like one that ended. A
   restart's cost is the **entire abandoned transcript**, which usually puts it
   at the top of the cost ranking; read the abandoned session's tail to find
   what caused the abandonment, and treat that as the failure to fix.
4. **Redundancy inference**: combine context waste with the DISTIL notes. Flag
   skill sections or installed surfaces that repeatedly cost tokens without an
   observed behavioural delta, overlap another active skill, or duplicate
   default model/harness behaviour. Do not delete or trim purely because a rule
   was not used in this window; require either relevant excitation or clear
   overlap evidence.

`references/context-audit.md` holds the script and the noise heuristics. The
script is written against Claude Code's transcript schema and fails silently
(near-zero totals) on a host that stores a different shape — check the caveat
there before trusting its numbers. Skip this step when transcripts aren't
available as raw JSONL, or when porting the script to your host's schema costs
more than the step is worth.

### 3. VERIFY

**Skip this step, and `references/verify.md` with it, only on the first-ever run
(no ledger yet).** Otherwise close the loop on prior corrections before proposing
new ones: read the ledger, then work `references/verify.md` for each edit still
marked open — the excitation check, the presence check, replay where the failure
is replayable, the cost check, and the skill-level trend check.

Two rules govern the rest, and they are what the step exists to enforce:

- **Absence of a failure on an un-exercised mode is not evidence the edit
  worked.** Mark it `untested-this-window` and conclude nothing.
- **An edit that did not reduce its target's cost is revised or reverted, never
  supplemented.** Stacking a second patch on a failed one is integrator windup.

Each open edit ends the step with one verdict: `confirmed-by-replay`,
`refuted-by-replay`, `confirmed-effective`, `ineffective`, or
`untested-this-window`.

### 4. AUDIT

Read the notes back. Build **recurring worked** and **recurring didn't** lists,
with note references per item. Do not escalate single-session findings unless
high-severity. Fold MEASURE in: a token-heavy injection or dump is recurring if
it spans multiple sessions, and a restart is automatically high-severity —
whatever caused the abandonment gets recurring-level standing even from one
instance. Fold VERIFY in: an `ineffective` prior edit is a recurring finding
that needs a *different* actuator, not a louder same one.

Note on generality: failures that are **harness/tooling-shaped** (tool loading,
gating, polling, path handling) are general by construction — they do not depend
on language or paradigm, so they need no cross-paradigm recurrence test to
promote. Do not rely on a paradigm contrast to establish generality; your work
mix may not provide comparable populations (e.g. implementation on one side,
investigation-only on the other).

### 5. SORT

Place each fix at the **lowest standing-cost actuator that prevents it** (gate <
skill/command < structural < CLAUDE.md). The instinct to add a CLAUDE.md rule is
reaching for the most expensive actuator first — resist it.

- A `present-not-consulted` failure is standing guidance that didn't get
  consulted at the point of action. The fix is almost never *louder standing
  guidance* (that feeds the blindness and taxes every session) — it is moving
  the guidance to a gate or an on-demand skill that fires when the action is
  imminent. Gated guidance fails cheap; wallpaper guidance fails expensive.
- A `present-contradicted` failure is the floor. No actuator fixes it. Note it,
  do not spend tokens on it.
- Weight by cost: do not add an always-on token tax (CLAUDE.md) to prevent a
  papercut. The prevention must cost less, over expected sessions, than the
  failure it prevents.
- Consolidate `confirmed-effective` edits (merge and lock — integral reset).
  Revise `ineffective` ones rather than supplementing.

Use this table for destination:

| Finding | Goes to |
|---------|---------|
| Preventable at the point of action | Gate/hook in config |
| Needs context at a specific moment | Skill/command edit (on-demand) |
| Topology / delegation / tool availability | Agent, config, or tool-surface edit |
| Skill/command injects unused context | Skill/command edit: cap or scope the injection |
| Skill/rule appears redundant after excitation or overlap check | Skill/command edit: trim, merge, demote to reference, or drop |
| Discipline slipped (knew rule, skipped it) | Prefer a gate; CLAUDE.md + Red Flags entry only if no gate is possible |
| Rule that genuinely must be always-on and applies to any project | Skill file or CLAUDE.md (last resort) |
| Codebase-specific tripwire | Project note, issue comment, or repo guidance |
| Recurring project tripwire | Repo guidance (`AGENTS.md`, `CLAUDE.md`, `README.md`, process docs) |
| User/team preference | Preference note, if durable memory exists |
| Domain term | Definition in project documentation |
| Multi-step recipe that worked and is reusable | Procedure candidate |

Shared-skill portability: do not encode machine-local paths, private project
names, private tools, or one user's personal workflow into a shared skill unless
the user explicitly asks for a local fork. Put local/project-specific findings
in repo guidance, project docs, issue comments, or follow-up notes.

Rule of thumb: if a developer on another project would benefit, propose a skill
edit. Otherwise use the smallest durable project/local destination.

### 6. PROPOSE

```
File: <path>
Actuator: <gate | skill | command | agent | config | tool | CLAUDE.md>
Section: <heading>
Targets failure class: <stable id, for the ledger>
Before: <existing line(s) or "new subsection">
After: <proposed line(s)>
Cost traded: <tokens/calls this prevents vs standing cost of the fix>
Why this actuator, not a lower- or higher-standing-cost one: <one sentence>
```

One rule per paragraph, one example max. Cap proposals at the top 3-5 by
**cost-weighted** recurrence. Put the rest in "Noted but not actioned". An edit
that cannot name the failure class it targets is not a controller action —
demote it to a note.

**Check the ledger's REJECTED rows before proposing.** If a proposal targets a
failure class that already has a rejected row, either drop it or state in the
proposal what is different this time — a new actuator, new evidence, a changed
cost. Re-proposing the same edit for the same reason a retro later is churn, and
it wastes the user's attention on a decision they already made.

### 7. CONFIRM

Present the report (Output Shape below) and ask "apply these and record the
retro summary?". Do nothing without a yes. Note which proposals the user
declines, and the reason if one is given; those become REJECTED rows at APPLY.

### 8. APPLY

After CONFIRM only. Edit the canonical source, verify the loaded file changed,
report the landed path.

Then read `references/ledger.md` and append three kinds of row to the ledger at
the path resolved in Preconditions:

- **one per applied edit**, carrying its `after` text verbatim — that is the
  anchor VERIFY uses next retro to check the edit is still in force;
- **one REJECTED row per proposal that did not land**, declined at CONFIRM or
  reverted at VERIFY, so PROPOSE does not re-raise a settled decision;
- **one SUMMARY row for the retro itself**, written every run even when zero
  edits were approved, because VERIFY's trend check needs the headline
  regardless.

## Output Shape

Printed inline. Nothing is written to disk except tmp intermediate notes and, at
APPLY, the ledger.

```
## Loop check (VERIFY)
- <prior edit>: <confirmed-by-replay | refuted-by-replay | confirmed-effective |
  ineffective | untested-this-window>
  (<edit still present? replayed or observed? exercised this window? cost change?>)
- Trend: <this window's headline vs prior SUMMARY rows; cumulative edit
  hit-rate> (directional only)

## Cost summary
- Total token-weighted wasted effort this window, and the few failures that
  dominate it. (Headline is cost, not count.)
- Restarts: abandoned-and-re-attempted sessions, each costed at its abandoned
  transcript, with the cause of abandonment.
- Wrong-outcome mistakes, listed regardless of token cost.

## Recurring — worked
- <item with note references>

## Recurring — didn't work
- <item with note references, cost-weighted>

## Proposed edits   (top 3–5 by cost-weighted recurrence)
1. File: <path>   Actuator: <…>   Targets: <failure class>
   Change: <old → new>
   Cost traded: <prevents X vs standing cost Y>
   Why this actuator: <one sentence>

## Floor (not actionable)
- <present-contradicted failures — info was available and ignored; no actuator fixes these>

## Proposed follow-up notes
- <destination or type>: <entry>

## Proposed procedure candidates
1. Name / Trigger / Steps / Destination / Why a procedure not a rule

## Proposed skill promotions
1. Pattern / Recurrence evidence / Destination / Why promote

## Noted but not actioned
- <single-session, low-cost, or floor findings>

Apply these?
```

Nothing is written (beyond tmp notes) until the user approves.

## Red Flags

The rules are in the steps above; these five are the ones that get violated while the
step is being followed, so check them against the finished report:

- **Pure analysis** — a finding with no proposed edit or follow-up note, or an edit with no
  file path and section. Generic advice ("test more", "plan better") is this failure wearing
  a conclusion.
- **Wrong actuator** — the fix sits higher in standing cost than the failure warrants. The
  usual form is answering `present-not-consulted` with louder standing context, which feeds
  the blindness *and* taxes every session.
- **Count over cost, cost over outcome** — a headline that weights a papercut equal to an
  expensive misdirection, or that drops a wrong-outcome mistake because it was token-cheap.
  Both dimensions rank; neither gates the other.
- **Absence read as evidence** — no recurrence proves nothing when the failure mode was
  never exercised, a one-sided replay pass is not causal, and one window is not a trend.
- **Premature application** — edits applied before the user says yes at CONFIRM.
