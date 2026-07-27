# DISTIL (step 1)

For each transcript in the window, in isolation: read it, isolate genuine
failures (not normal iteration), write a structured note. One transcript at a
time; do not load them all together.

This file is self-contained. When the retro fans out to parallel distil
subagents, give each subagent this file and the one transcript it is to distil —
it needs nothing else from `SKILL.md`.

## Working directory and fan-out

Create a tmp working dir once (`mktemp -d`). For each transcript: read one,
write one structured note, move on. When distilling via parallel subagents,
require each to use namespaced scratch paths (e.g. `/tmp/<session-id>-skel.txt`,
never a shared `/tmp/skel*.txt`) — concurrent agents have clobbered each
other's extractions and nearly mis-attributed content across transcripts.

Before distilling, look for surviving notes from an earlier aborted run (the tmp
dirs persist) and reuse them — distil only what is missing. Cap concurrent distil
subagents at ~12: a 40-agent fan-out exhausted the session limit mid-run and
abandoned an entire retro (~1.85M tokens, 12 of 40 notes never written), which
cost more than every failure that retro was studying.

## Isolating genuine failures

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

## What to capture per failure

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

## Note file

Save as `<tmpdir>/YYYY-MM-DD-HHMMSS-session.md`; get the timestamp from shell
`date`.
