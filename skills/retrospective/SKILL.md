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
   small file the retro writes at APPLY and reads at the next retro; it can
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
3. VERIFY   — Read the ledger. For each open prior edit: was its failure mode
              EXERCISED in this window, and if so did its cost FALL? Close the
              loop before proposing anything new.
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

### 1. DISTIL

Create a tmp working dir once (`mktemp -d`). For each transcript: read one,
write one structured note, move on.

**Isolate genuine failures first — this is the judgement-heavy step.** A failure
is output that took a wrong path, missed a constraint, or declared done
prematurely. Exclude normal iteration:

- Expected red→green loops. A typechecker/compiler reporting a legitimate next
  constraint is the loop working, NOT a failure. Discriminator: did the error
  report a real next step (exclude), or the model's own fabrication / wrong
  choice (count)? *Example: Unison emitting `needs {Storage}` then `needs
  {Random}` is incremental ability discovery — exclude. Submitting a symbol that
  does not exist and getting "couldn't figure out what X refers to" is a failure
  — the model invented it.*
- Retries against genuinely unknowable-in-advance state where no prior tool
  could have surfaced the answer. Judge honestly — often one *could* have.

If isolating a failure is itself ambiguous, say so. A high ambiguous rate is a
finding: failures aren't cleanly separable from iteration in these transcripts.

For each isolated failure, capture:

- what went wrong and what would have prevented it
- **was the preventing information in-window at the failure turn?** Judge by the
  `tool_result` the model saw (not the full `toolUseResult`). Tag one of:
  - `present-not-consulted` — info was in-window/standing context, model acted
    before consulting it (often runs the right check correctly *elsewhere*).
    Harness-fixable: move guidance to a point-of-action actuator.
  - `present-contradicted` — info was surfaced and engaged with (read, even
    restated), model proceeded against it anyway. **The floor — not
    harness-fixable.** Do not propose an actuator fix; note and move on.
  - `absent-via-truncation` — info was fetched but capped out of the
    `tool_result`. Fix: the cap/summariser.
  - `absent-via-never-retrieved` — never fetched. Fix: retrieval/ordering, or a
    file never opened.
  - `absent-via-compaction` — present pre-compaction, failure post-compaction.
    Compaction dropped load-bearing signal — a finding, call it out.
  - `cant-tell` — cannot determine (compaction boundary; or info isn't
    tool-surfaceable). Abstain rather than force a label.
- **cost**: wasted calls and/or wasted wall-clock attributable to the failure.
  This is the weight that matters — a cosmetic self-correction and a ten-call
  misdirection are not equal units.
- **outcome severity, independent of cost**: did the mistake produce a wrong
  outcome — a wrong answer accepted, a premature "done", a bad edit left in
  place? A token-cheap mistake with a wrong outcome is a high-severity finding;
  cost ranks findings, it does not gate them.
- the agent's own mid-session failure-recognitions, verbatim ("I made up…", "I
  see the architectural issue", "the test didn't actually run"). These are the
  highest-value signal and they are already in the transcript — harvest them.
- context waste: large tool outputs that went unused; note the producing tool,
  command, or skill `!`-injection
- redundancy signals: skill text, rules, installed surfaces, or injected
  guidance that appear to add no behavioural delta. Record the evidence type:
  `duplicated-by-default`, `covered-by-other-skill`, `loaded-unused`,
  `exercised-no-delta`, or `low-value-token-tax`. Treat these as inferences, not
  proof; absence of visible use is weak evidence unless the relevant trigger was
  exercised.
- explicit "remember X for retro" markers, verbatim
- candidate findings

Save as `<tmpdir>/YYYY-MM-DD-HHMMSS-session.md`; get the timestamp from shell
`date`.

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

`references/context-audit.md` holds the script and the noise heuristics. Skip
this step only when transcripts aren't available as raw JSONL.

### 3. VERIFY

Close the loop on prior corrections before proposing new ones. Read the ledger.
For each edit still marked open:

1. **Excitation check first.** Did this window contain work that could trigger
   the targeted failure mode? If not, mark `untested-this-window`, carry it
   forward, **conclude nothing.** Absence of a failure on an un-exercised mode is
   not evidence the edit worked. Reverting on an unobserved mode injects noise.
2. **Presence check.** Look for the prior edit's recorded `after` text in the
   governed file now. The ledger already stores it (see APPLY), so this needs no
   snapshot of the original config — just confirm the edit is still literally in
   force.
   - Still present → the edit survives; proceed to the cost check.
   - Gone or overwritten → someone reverted or replaced it out-of-retro. That is
     itself the finding: the edit did not stick. Do not re-apply blindly; note
     it and treat as `untested-this-window` for cost purposes (you cannot
     attribute a cost change to an edit that wasn't in force).
     Optionally, a cheap whole-config fingerprint (a VCS revision id or content
     hash recorded at the last APPLY) that has changed flags that *something*
     moved between retros. Advisory only — detection, not attribution; the
     per-edit presence check above is the load-bearing one.
3. **If exercised and attributable:** did the targeted failure's cost fall?
   - Fell → `confirmed-effective`. Becomes a consolidation candidate in SORT.
   - Did not / regressed → `ineffective`. **Revise or revert — do not stack a
     second patch on top.** Stacking is integrator windup.
4. **Trend check (skill-level).** Read prior retros' SUMMARY rows (see APPLY).
   Compare this window's headline — wasted tokens, restarts, wrong-outcome
   mistakes, roughly normalised per session — against the trajectory, and read
   the cumulative edit hit-rate (confirmed-effective vs ineffective vs
   still-untested). Flat-or-rising waste across several retros despite
   confirmed-effective edits means the retro is fixing the wrong things; a high
   ineffective or perpetually-untested rate means diagnoses are poor or edits
   target modes too rare to matter. Either is a finding about the retro
   itself — report it in the Loop check. Directional only: task mix and model
   changes confound, and one window is never a trend.

Skip VERIFY only on the first-ever run (no ledger yet).

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

### 7. CONFIRM

Present the report (Output Shape below) and ask "apply these and record the
retro summary?". Do nothing without a yes.

### 8. APPLY

After CONFIRM only. Edit the canonical source, verify the loaded file changed,
report the landed path. Then record in the ledger, one row per applied edit:

```
date (shell `date`) | file+section | actuator | targets-failure-class |
before→after (verbatim — VERIFY's presence anchor) | [optional: config-fingerprint] |
status: open
```

Record the `after` text verbatim — VERIFY uses it as the presence anchor next
retro (step 2 above). The optional config fingerprint is the advisory
whole-config hint described there.

Then append **one SUMMARY row for the retro itself** — written every run after
CONFIRM, even when zero edits were approved, because VERIFY's trend check needs
the headline regardless:

```
SUMMARY | date (shell `date`) | window: <N sessions / range> |
wasted~tok: <total> | restarts: <n> | wrong-outcome: <n> |
edits to date: <confirmed-effective>/<ineffective>/<untested>
```

Write the ledger to the path resolved in Preconditions. It is read only at
retro time — do **not** add a hook that writes observations on the fly; the
transcript is already the complete on-the-fly record.

## Output Shape

Printed inline. Nothing is written to disk except tmp intermediate notes and, at
APPLY, the ledger.

```
## Loop check (VERIFY)
- <prior edit>: <confirmed-effective | ineffective | untested-this-window>
  (<edit still present? exercised this window? cost change?>)
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

- Generic advice ("test more", "plan better") — name a file and section or drop it.
- No anchor: proposed edit lacks a file path and section.
- Pure analysis: no proposed edit or follow-up note.
- Premature application: edits applied before user approval.
- Wrong actuator: fix placed higher in standing cost than needed (a CLAUDE.md line where a gate would do).
- Louder wallpaper: answering `present-not-consulted` with more standing context.
- Count over cost: a headline that weights a papercut equal to an expensive misdirection.
- Cost over outcome: dismissing a wrong-outcome mistake because it was token-cheap.
- Restart blindness: treating an abandoned-and-restarted session as a clean ending.
- Spending on the floor: proposing a fix for `present-contradicted`.
- Open loop: proposing new edits without VERIFYing prior ones against the ledger.
- Attribution without excitation: crediting a prior edit when its failure mode was never exercised.
- On-the-fly ledger: a hook writing observations mid-session.
- Layer mixing / portability leak: project facts, local paths, private tools, or personal workflow in a shared skill.
- One-window trend: reading a single retro's headline as a trajectory.
- Absence treated as evidence: no recurrence in this window does not prove a past issue is fixed.
