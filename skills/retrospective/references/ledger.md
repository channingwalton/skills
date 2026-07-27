# The VERIFY ledger (APPLY step 8)

Three row types, all appended at APPLY, all read at the next retro's VERIFY and
PROPOSE steps. Write to the ledger path resolved in Preconditions.

## Applied-edit row

One per applied edit:

```
date (shell `date`) | file+section | actuator | targets-failure-class |
before→after (verbatim — VERIFY's presence anchor) | [optional: config-fingerprint] |
status: open
```

Record the `after` text verbatim — VERIFY uses it as the presence anchor next
retro (its presence check). The optional config fingerprint is the advisory
whole-config hint described there.

## Rejected row

One per proposal that did **not** land — declined by the user at CONFIRM, or
reverted at VERIFY as `ineffective` or `refuted-by-replay`:

```
REJECTED | date (shell `date`) | file+section | actuator |
targets-failure-class | proposed after-text (abridged) |
reason: <declined: … | ineffective | refuted-by-replay>
```

This is the rejected-edit buffer. PROPOSE reads it to avoid re-raising a
decision the user already made, and it keeps a record of which actuators have
been tried against a failure class and failed — which is itself evidence when
that class recurs.

## Summary row

One per retro run — written every run after CONFIRM, even when zero edits were
approved, because VERIFY's trend check needs the headline regardless:

```
SUMMARY | date (shell `date`) | window: <N sessions / range> |
wasted~tok: <total> | restarts: <n> | wrong-outcome: <n> |
edits to date: <confirmed>/<ineffective>/<untested> (replayed: <n> of confirmed+ineffective) |
rejected to date: <n>
```

## Writing rule

The ledger is read only at retro time — do **not** add a hook that writes
observations on the fly; the transcript is already the complete on-the-fly
record.
