# The VERIFY ledger (APPLY step 8)

The ledger holds the `proposed, not applied` report section written at CONFIRM,
and three row types appended at APPLY. The next retro reads the rows at VERIFY
and PROPOSE.

## Applied-edit row

One per applied edit. The verbatim `after` text is VERIFY's presence anchor:

```
date (shell `date`) | file+section | actuator | targets-failure-class |
before→after (verbatim) | [optional: config-fingerprint] |
status: open
```

## Rejected row

One per proposal that did **not** land — declined by the user at CONFIRM, or
reverted at VERIFY as `ineffective` or `refuted-by-replay`:

```
REJECTED | date (shell `date`) | file+section | actuator |
targets-failure-class | proposed after-text (abridged) |
reason: <declined: … | ineffective | refuted-by-replay>
```

PROPOSE reads these rows so that it does not re-raise a settled decision. They
also record which actuators already failed against a failure class, which is
evidence when that class recurs.

## Summary row

One per retro run, even when the user approved no edits, because VERIFY's trend
check needs the headline:

```
SUMMARY | date (shell `date`) | window: <N sessions / range> |
corrections: <n> (<n per human turn>) | questions: <n per human turn> |
human~hours: <total> | accepted: <n> (<n per human hour>) | wasted~tok: <total> |
restarts: <n> | wrong-outcome: <n> |
edits to date: <confirmed>/<ineffective>/<untested> (replayed: <n> of confirmed+ineffective) |
rejected to date: <n>
```

## Writing rule

Write the ledger only at retro time. Do **not** add a hook that writes
observations on the fly; the transcript is already the complete on-the-fly
record.
