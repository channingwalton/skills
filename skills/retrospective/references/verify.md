# VERIFY (step 3)

Close the loop on prior corrections before proposing new ones. Read the ledger.
For each edit still marked open, work the five checks below.

Skip this step — and this file — only on the first-ever run (no ledger yet).

## 1. Excitation check first

Did this window contain work that could trigger the targeted failure mode? If
not, mark `untested-this-window`, carry it forward, **conclude nothing.** Absence
of a failure on an un-exercised mode is not evidence the edit worked. Reverting
on an unobserved mode injects noise. A replay (check 3) manufactures its own
excitation — a replayable edit need not wait for the task mix to come round
again.

## 2. Presence check

Look for the prior edit's recorded `after` text in the governed file now. The
ledger already stores it (see `references/ledger.md`), so this needs no snapshot
of the original config — just confirm the edit is still literally in force.

- Still present → the edit survives; proceed to the cost check.
- Gone or overwritten → someone reverted or replaced it out-of-retro. That is
  itself the finding: the edit did not stick. Do not re-apply blindly; note
  it and treat as `untested-this-window` for cost purposes (you cannot
  attribute a cost change to an edit that wasn't in force).
  Optionally, a cheap whole-config fingerprint (a VCS revision id or content
  hash recorded at the last APPLY) that has changed flags that *something*
  moved between retros. Advisory only — detection, not attribution; the
  per-edit presence check above is the load-bearing one.

## 3. Replay, where the failure is replayable

The cost check below is *observational* — a later window with a different task
mix — which is weak attribution. Where the failure has a mechanically checkable
signal, re-run it and get an answer now instead of waiting a window.

Replayable means all three:

- the trigger is reconstructable from the transcript (the prompt, command, or
  file state that led to the wrong turn);
- success is decidable without judgement — a tool loaded or it didn't, a path
  resolved or it didn't, a gate fired or it didn't, a check ran or it didn't;
- re-running has no side effects: read-only, or confined to a throwaway dir.
  **Never replay work that writes to real files, commits, pushes, sends, or
  mutates remote state.** In doubt, don't replay.

Most work fails the test — investigations, design calls, anything scored by
judgement. Harness-shaped failures (tool loading, gating, path handling,
delegation) usually pass it, and they are also the ones an actuator can fix,
so the overlap is worth exploiting.

Run the trigger in a fresh session with the edit in force:

- Failure recurs → `refuted-by-replay`. Definitive. The edit does not prevent
  it; revise or revert, do not stack.
- Failure absent → `confirmed-by-replay`, and note that this is **one-sided**:
  it shows the failure is absent under the edit, not that the edit caused the
  absence. For the causal claim, re-run once with the edit removed and check
  the failure returns — only when removal is cheap and reversible (a skill
  file, not a live hook), and put it back immediately.

Cap replays at a handful per retro; each costs roughly a session. Spend them
on the most expensive failure classes. Where replay isn't possible or isn't
worth its cost, fall back to the observational check below and say which was
used — a replayed verdict and an observed one are not the same strength of
evidence.

## 4. Cost check, if exercised and attributable

Did the targeted failure's cost fall?

- Fell → `confirmed-effective`. Becomes a consolidation candidate in SORT.
- Did not / regressed → `ineffective`. **Revise or revert — do not stack a
  second patch on top.** Stacking is integrator windup.

## 5. Trend check (skill-level)

Read prior retros' SUMMARY rows (see `references/ledger.md`). Compare this
window's headline — wasted tokens, restarts, wrong-outcome mistakes, roughly
normalised per session — against the trajectory, and read the cumulative edit
hit-rate (confirmed vs ineffective vs still-untested — replay verdicts count in
the confirmed and ineffective buckets, flagged as replayed since they are
stronger evidence). Flat-or-rising waste across several retros despite
confirmed-effective edits means the retro is fixing the wrong things; a high
ineffective or perpetually-untested rate means diagnoses are poor or edits
target modes too rare to matter. Either is a finding about the retro
itself — report it in the Loop check. Directional only: task mix and model
changes confound, and one window is never a trend.
