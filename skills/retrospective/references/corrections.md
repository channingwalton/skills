# Corrections and throughput (MEASURE step)

`retro.py measure` (see Script below) gives the window's human turns (the denominator of the
correction rate), its interrupts and declined tool calls, the agent's questions
to the user (the guard), and accepted changes per human hour. The cost of each
failure comes from the DISTIL notes, by hand (last section).

Before you trust a number, apply the five traps in
`references/context-audit.md`. The script excludes the retro's own run,
prompt-only transcripts and SDK sessions, and it filters events by timestamp.

## Corrections

The **correction rate** is corrections per human turn: of everything the user
said, the share that fixed the agent. It does not depend on session length.

A correction is a count, not a time, on purpose. To estimate the time a
correction took, you must first find the correction, and then add a weight
(the reply gap) that also holds reading, typing and idle time. The weight adds
error to each event, and a ranking of failures needs low error on each event.

Only interrupts and declined tool calls carry a mechanical marker. In a 14-day
test, 21 of 899 human turns had one. DISTIL classifies every other
correction from its text, so the correction rate is as good as DISTIL's
judgement. Read the ambiguous rate in the DISTIL notes with it.

**Guard: questions to the user.** An edit that makes the agent ask before it
acts can lower corrections and move the same cost into questions. The script
counts calls to the tools named by `--ask` per human turn. If an edit lowers
corrections and raises questions, it moved the cost; it did not remove it.
Questions in plain text are not counted.

## Human hours and throughput

**Human hours** exist only as the denominator of throughput. Each human turn
spans the gap from the agent's last output to the user's message, capped at 10
minutes, because a longer gap is mostly time away. A declined tool call spans
the gap from the call to the decline. The window total is the union of the
spans across all sessions, so time in two sessions at once counts once.

A single span is a poor estimate, but the total is good enough for a trend. It
adds up thousands of spans, so random error in each span has less effect, and
the cap introduces the same bias in every window.

An **accepted change** is a commit that reached the default branch in the
window and was not reverted. A squash-merged pull request is one commit on the
default branch, so it counts once. A commit on an unmerged branch is work in
progress, not yet accepted.

The script finds the repositories from the sessions' working directories and
their `git -C` paths, then reads each default branch. It excludes:

- a revert, and the commit that it reverts;
- commits that a tool makes on a timer, such as a notes vault backup. Pass
  their subject pattern as `--auto`. The per-repository output exists so that
  you can find a new one.

Commits that the user made outside any session count too, because the script
reads the branch, not the transcript. Read throughput as directional only: task
mix and task size move it more than any edit does.

## SDK sessions

An application that drives the agent through an SDK writes its prompts as user
turns. In the 14-day test, one such application wrote 2,340 of 3,350 "human
turns", which would have cut the correction rate to about a third of its true
value.

The transcript records how a prompt arrived, not who wrote it, so the script
excludes every session whose `entrypoint` starts with `sdk`. The command line
and the desktop app stay. The cost: a person who types into a chat panel that
uses the SDK is excluded too — 115 human turns in 18 sessions in the same test.

## Script

Run `retro.py measure` from the skill directory (Python 3, stdlib only):

```sh
python3 <skill-dir>/retro.py measure --days <window> --self <this retro's project-dir substring>
```

Other options: `--ask` names the tools that put a question to the user (default
`AskUserQuestion`), `--auto` is the subject regex of timer commits (default
`^vault backup:`), `--root` is the transcript root (default
`~/.claude/projects`), and `--reminder` matches harness text in user messages.

The human-turn filter matches Claude Code's markers for text that the harness
writes into user messages: command output, task notifications, agent-team
messages, usage-limit notices. Another host needs its own markers, or every injected message reads
as a human turn. The per-session list shows where the user's turns went; use it
to confirm restarts and to choose which transcripts to distil first.

## Cost per failure (manual — not scripted)

The script counts turns per *session*. It cannot attribute corrections to
*failures*, and you should not extend it to try. Deciding which user turns a
failure caused is the same judgement as isolating the failure in the first
place (DISTIL), and it does not separate mechanically from interleaved work: a
correction often also adds a new request. A script that claims it will produce
confident nonsense.

Do it by hand over the DISTIL notes. Each note gives, per failure, the
corrections it caused and the class of each. Rank failures by their number of
corrections, so a failure that took four corrections ranks above one that took
one. Rank failures with equal counts by class: a rejected change or rework
above a redirect or an interrupt.

The agent cost in each note is the third weight. It ranks failures with equal
corrections and class, and it points at the cause. Count it as the tool calls
(and roughly their tokens, `chars/4`) between the first wrong turn and the
point the model recovered.
