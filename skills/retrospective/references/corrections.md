# Corrections and throughput (MEASURE step)

## Contents

- Corrections
- Human hours and throughput
- SDK sessions
- Script
- Cost per failure (manual — not scripted)

The user's attention is the **bottleneck**. Agent tokens are cheap and
plentiful; the user's attention is not. The retro measures what failures take
from it as **corrections**: user turns that correct the agent. This file covers
two MEASURE outputs:

1. **Corrections** — the headline. The cost of each failure comes from the
   DISTIL notes, by hand. The script gives the window's human turns (the
   denominator of the correction rate), its interrupts and declined tool calls,
   and the agent's questions to the user (the guard).
2. **Throughput** — the script counts accepted changes and divides them by
   human hours.

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
counts calls to the tools in `ASK` per human turn. If an edit lowers
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
- commits that a tool makes on a timer, such as a notes vault backup. Set
  `AUTO` to their subject pattern. The per-repository output exists so that
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

Plain `python3`, stdlib only. Edit the window, `SELF`, `ASK` and `AUTO`.

```python
import json, os, glob, time, re, subprocess, collections
from datetime import datetime

DAYS = 14
CAP = 10 * 60  # seconds; a longer reply gap is mostly time away. Human hours only.
SELF = ''      # this retro's own project-dir substring; see context-audit.md, trap 1.
REMINDER = re.compile(r'<system-reminder>.*?</system-reminder>', re.S)
NOT_HUMAN = ('<local-command-', '<task-notification>', '<bash-stdout>', '<bash-stderr>',
             '<bash-notification>', '[Usage limit', '[Earlier usage')
GIT_C = re.compile(r'git\s+-C\s+(\S+)')
ASK = ('AskUserQuestion',)  # tools that put a question to the user; adjust per host
AUTO = re.compile(r'^vault backup:')  # subjects of commits that a tool makes on a timer; adjust per host

def via_sdk(f):  # an application, not a person, may write the prompts; see "SDK sessions"
    for line in open(f, errors='ignore'):
        if '"entrypoint"' in line:
            try: return json.loads(line).get('entrypoint', '').startswith('sdk')
            except: pass
    return False

START = time.time() - DAYS * 86400
files = [f for f in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True)
         if '/subagents/' not in f and os.path.getmtime(f) > START and (not SELF or SELF not in f)
         and not via_sdk(f)]

def stamp(o):
    return datetime.fromisoformat(o['timestamp'].replace('Z', '+00:00')).timestamp()

def blocks(c):
    return c if isinstance(c, list) else [{'type': 'text', 'text': c}]

spans = []                      # (start, end) of human attention, all sessions; for human hours
per = {}                        # session -> Counter
dirs = set()                    # every directory a session worked in
for f in files:
    s = collections.Counter(); last_out = None; uses = {}; agent = False
    for line in open(f, errors='ignore'):
        try: o = json.loads(line)
        except: continue
        t = o.get('type')
        if t not in ('user', 'assistant') or o.get('isSidechain') or 'timestamp' not in o: continue
        now = stamp(o)
        if now < START: continue    # mtime is not the window: a file can hold months of events
        dirs.add(o.get('cwd', ''))
        bl = blocks(o.get('message', {}).get('content', []))
        if t == 'assistant':
            agent = True; last_out = now
            for b in bl:
                if b.get('type') == 'tool_use':
                    uses[b.get('id')] = now
                    s['asks'] += b.get('name') in ASK
                    dirs.update(os.path.expanduser(d.strip('"\'')) for d in GIT_C.findall((b.get('input') or {}).get('command', '')))
            continue
        results = [b for b in bl if b.get('type') == 'tool_result']
        for b in results:
            use = uses.get(b.get('tool_use_id'))
            text = '\n'.join(x.get('text', '') for x in blocks(b.get('content') or '') if isinstance(x, dict))
            if text.startswith("The user doesn't want to proceed"):
                s['declined'] += 1
                if use: spans.append((max(use, now - CAP), now))
        if results or o.get('isMeta') or o.get('isCompactSummary'): continue
        if (o.get('origin') or {}).get('kind', 'human') != 'human': continue
        text = REMINDER.sub('', ' '.join(b.get('text', '') for b in bl if b.get('type') == 'text')).strip()
        if not text or text.startswith(NOT_HUMAN): continue
        if text.startswith('[Request interrupted'):
            s['interrupts'] += 1; continue
        s['turns'] += 1
        if last_out: spans.append((max(last_out, now - CAP), now))
    if agent: per[f] = s        # a prompt-only transcript is not a session; see context-audit.md, trap 3.

def union(spans):
    total = 0; end = 0
    for a, b in sorted(spans):
        if b > end: total += b - max(a, end); end = b
    return total

def git(repo, *args):
    return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True).stdout.strip()

def accepted(repo):
    """Commits that reached the default branch in the window, less reverts and what they reverted."""
    base = git(repo, 'symbolic-ref', '--quiet', '--short', 'refs/remotes/origin/HEAD')
    base = base or next((b for b in ('main', 'master') if git(repo, 'rev-parse', '--verify', '--quiet', b)), 'HEAD')
    log = [e.strip() for e in git(repo, 'log', base, '--since', f'@{int(START)}', '--format=%H %B%x00').split('\0')]
    log = [e for e in log if e and not AUTO.match(e[41:])]
    hashes = {e.split()[0] for e in log}
    gone = {h for e in log for h in re.findall(r'This reverts commit ([0-9a-f]{40})', e)} & hashes
    return len(hashes) - 2 * len(gone)

repos = {}                      # the shared git dir -> one worktree, so worktrees count once
for d in dirs:
    if os.path.isabs(d) and os.path.isdir(d) and git(d, 'rev-parse', '--is-inside-work-tree') == 'true':
        repos.setdefault(os.path.realpath(os.path.join(d, git(d, 'rev-parse', '--git-common-dir'))), d)

hours = union(spans) / 3600
per_repo = {os.path.dirname(k): accepted(d) for k, d in repos.items()}
changes = sum(per_repo.values())
tot = sum(per.values(), collections.Counter())
turns = tot['turns'] or 1
print(f"sessions={len(per)}  human turns={tot['turns']}  interrupts={tot['interrupts']}  "
      f"declined={tot['declined']}  questions={tot['asks']} ({tot['asks'] / turns:.3f} per human turn)")
print(f"human~hours={hours:.1f}  repos={len(repos)}  accepted changes={changes}  "
      f"per human hour={changes / hours if hours else 0:.2f}")
print("\naccepted changes by repo (check for a tool that commits on a timer):")
for d, n in sorted(per_repo.items(), key=lambda kv: -kv[1]):
    if n: print(f"  {n:4}  {d}")
print("\nsessions by human turns (top):")
for f, s in sorted(per.items(), key=lambda kv: -kv[1]['turns'])[:15]:
    print(f"  turns={s['turns']:<4} int={s['interrupts']:<2} dec={s['declined']:<2} ask={s['asks']:<2} "
          f"{os.path.basename(os.path.dirname(f))[-50:]}/{os.path.basename(f)[:8]}")
```

The human-turn filter matches Claude Code's markers for text that the harness
writes into user messages: command output, task notifications, usage-limit
notices. Another host needs its own markers, or every injected message reads
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

This is what makes the retro headline cost-weighted: one failure that the user
corrected four times can outweigh a tail of papercuts that the agent fixed
alone, and a count of failures would hide that. One exception: wrong-outcome
mistakes keep finding status regardless of cost, because nobody corrected them
inside the window.
