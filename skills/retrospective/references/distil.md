# DISTIL (step 1)

Read one transcript, isolate its genuine failures, and write one structured
note. This file is all that a distil subagent needs.

Use namespaced scratch paths (e.g. `/tmp/<session-id>-skel.txt`, never a shared
`/tmp/skel*.txt`): concurrent distil agents have clobbered each other's
extractions.

## Isolating genuine failures

**This is the judgement-heavy step.** A failure is output that took a wrong
path, missed a constraint, or declared done prematurely. Exclude normal
iteration:

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
- **corrections**: the user turns that corrected the agent because of this
  failure, each quoted verbatim. Tag each with one class:
  - `rejected-change` — the user read a change and rejected it;
  - `rework` — earlier work came back to the user;
  - `decision-twice` — the user restated a decision already made in standing
    guidance, a skill, or an earlier turn;
  - `redirect` — the user turned the agent off a wrong path;
  - `interrupt` — the user stopped the agent mid-work;
  - `declined-call` — the user declined a tool call.

  A new request, a refinement the agent could not have known, or an answer to
  the agent's own question is not a correction. Tag a turn `ambiguous` when you
  cannot tell; a high ambiguous rate is a finding. A failure that the agent
  recovered from without the user has zero corrections, however many calls it
  took. Also quote each decision the user states: only the retro's
  cross-session pass can see a decision made twice.
- **agent cost**: wasted calls and tokens (`chars / 4`). It ranks failures with
  equal corrections — a cosmetic self-correction and a ten-call misdirection are
  not equal units — and it points at the cause.
- **outcome severity, independent of cost**: did the mistake produce a wrong
  outcome — a wrong answer accepted, a premature "done", a bad edit left in
  place? A cheap mistake with a wrong outcome is a high-severity finding.
- the agent's own mid-session failure-recognitions, verbatim ("I made up…", "I
  see the architectural issue", "the test didn't actually run"). These are the
  highest-value signal. **Check first whether `thinking` blocks carry content.**
  Some hosts store them empty or as one-line summaries (Claude Code did in the
  2026-09-20 and 2026-10-21 windows); then the recognitions must come from
  assistant *text*. Say so in
  the note, and prefer `cant-tell` over `present-contradicted` wherever the
  distinction between "engaged with and overrode" and "never registered" rests
  on reasoning you cannot see — that boundary decides what counts as the floor.
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
