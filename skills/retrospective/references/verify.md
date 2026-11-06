# VERIFY (step 3)

For each ledger edit that is still open, work the five checks below in order.

## 1. Excitation check first

Did this window contain work that could trigger the targeted failure mode? If
not, mark `untested-this-window`, carry it forward, and **conclude nothing.**
Absence of a failure on an un-exercised mode is not evidence that the edit
worked, and a revert on an unobserved mode injects noise. A replay (check 3)
manufactures its own excitation, so a replayable edit need not wait for the
task mix to come round again.

## 2. Presence check

Look for the edit's recorded `after` text in the governed file now.

- Still present → the edit survives; proceed.
- Gone or overwritten → someone reverted or replaced it out-of-retro. That is
  the finding: the edit did not stick. Do not re-apply it blindly. Treat it as
  `untested-this-window` for cost purposes, because a cost change cannot be
  attributed to an edit that was not in force.

A whole-config fingerprint (a VCS revision or content hash recorded at the last
APPLY) that has changed shows that *something* moved between retros. It is
advisory: detection, not attribution.

## 3. Replay, where the failure is replayable

The cost check below is *observational* — a later window with a different task
mix — which is weak attribution. Where the failure has a mechanically checkable
signal, re-run it and get an answer now.

Replayable means all three:

- the trigger is reconstructable from the transcript (the prompt, command, or
  file state that led to the wrong turn);
- success is decidable without judgement — a tool loaded or it didn't, a path
  resolved or it didn't, a gate fired or it didn't;
- re-running has no side effects: read-only, or confined to a throwaway dir.
  **Never replay work that writes to real files, commits, pushes, sends, or
  mutates remote state.** In doubt, don't replay.

Most work fails the test — investigations, design calls, anything scored by
judgement. Harness-shaped failures (tool loading, gating, path handling,
delegation) usually pass it, and an actuator can fix them too.

Run the trigger in a fresh session with the edit in force:

- Failure recurs → `refuted-by-replay`. Definitive: revise or revert.
- Failure absent → `confirmed-by-replay`. This is **one-sided**: it shows that
  the failure is absent under the edit, not that the edit caused the absence.
  For the causal claim, re-run once with the edit removed and check that the
  failure returns. Do this only when removal is cheap and reversible (a skill
  file, not a live hook), and put the edit back immediately.

Cap replays at a handful per retro, because each costs roughly a session. Spend
them on the most expensive failure classes. Otherwise use the cost check, and
say which check produced the verdict: a replayed verdict is stronger evidence
than an observed one.

## 4. Cost check, if exercised and attributable

Did the targeted cost fall: corrections, wrong outcomes, or tokens for an edit
applied before the retro counted corrections? An edit that lowered corrections
and raised questions to the user only moved the cost; mark it `ineffective`.

- Fell → `confirmed-effective`, a consolidation candidate in SORT.
- Did not, or regressed → `ineffective`. **Revise or revert; do not stack a
  second patch on top** (integrator windup).

## 5. Trend check (skill-level)

Compare this window's headline with prior SUMMARY rows: the correction rate, the
question rate, accepted changes per human hour, restarts and wrong outcomes,
roughly normalised per session. Compare each measure only with rows that carry
it; older rows carry wasted tokens and no corrections. Read the cumulative edit
hit-rate too: confirmed vs ineffective vs still untested, with replayed verdicts
flagged inside the first two buckets.

Report in the Loop check:

- flat or rising cost across several retros despite confirmed-effective edits
  means that the retro fixes the wrong things;
- a high ineffective or perpetually-untested rate means poor diagnoses, or edits
  that target modes too rare to matter.

Directional only: task mix and model changes confound, and one window is never
a trend.
