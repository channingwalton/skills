#!/usr/bin/env python3
"""retro - MEASURE scripts for the retrospective skill.

    retro.py measure  --days N   corrections, questions and throughput
    retro.py context  --days N   where the window's tokens went
    retro.py restarts --days N   restart candidates: first and last text per session

Reads Claude Code's JSONL transcripts (default root ~/.claude/projects). Another
host's schema parses to near-zero totals rather than an error; see
references/context-audit.md. Stdlib only.
"""

from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime

CAP = 10 * 60  # seconds; a longer reply gap is mostly time away. Human hours only.
REMINDER = r'<system-reminder>.*?</system-reminder>'
NOT_HUMAN = ('<local-command-', '<task-notification>', '<bash-stdout>', '<bash-stderr>',
             '<bash-notification>', '<teammate-message', '[Usage limit', '[Earlier usage')
GIT_C = re.compile(r'git\s+-C\s+(\S+)')
ASK = ('AskUserQuestion',)
AUTO = re.compile(r'^vault backup:')
RECORD_ONLY = {'prompt_snapshot', 'hook_success'}  # stored in the transcript, never sent (trap 5)
DECLINED = "The user doesn't want to proceed"
OVERSIZE = 40_000
IMAGE_TOKENS = 1400


# ---------------------------------------------------------------- core

def stamp(o):
    return datetime.fromisoformat(o['timestamp'].replace('Z', '+00:00')).timestamp()


def blocks(c):
    if isinstance(c, list):
        return c
    return [{'type': 'text', 'text': c}] if isinstance(c, str) else []


@dataclass
class Session:
    counts: collections.Counter = field(default_factory=collections.Counter)
    spans: list = field(default_factory=list)  # (start, end) of human attention
    dirs: set = field(default_factory=set)     # every directory the session worked in
    has_agent: bool = False                    # a prompt-only transcript is not a session (trap 3)


def measure_session(events, start, ask=ASK, reminder=re.compile(REMINDER, re.DOTALL), cap=CAP):
    """Human turns, interrupts, declined calls, questions and attention spans of one transcript."""
    s = Session()
    last_out = None
    uses = {}
    for o in events:
        t = o.get('type')
        if t not in ('user', 'assistant') or o.get('isSidechain') or 'timestamp' not in o:
            continue
        now = stamp(o)
        if now < start:
            continue  # file time is not the window (trap 4)
        s.dirs.add(o.get('cwd', ''))
        bl = blocks(o.get('message', {}).get('content', []))
        if t == 'assistant':
            s.has_agent = True
            last_out = now
            for b in bl:
                if b.get('type') == 'tool_use':
                    uses[b.get('id')] = now
                    s.counts['asks'] += b.get('name') in ask
                    command = (b.get('input') or {}).get('command', '')
                    s.dirs.update(os.path.expanduser(d.strip('"\'')) for d in GIT_C.findall(command))
            continue
        results = [b for b in bl if b.get('type') == 'tool_result']
        for b in results:
            use = uses.get(b.get('tool_use_id'))
            text = '\n'.join(x.get('text', '') for x in blocks(b.get('content') or '') if isinstance(x, dict))
            if text.startswith(DECLINED):
                s.counts['declined'] += 1
                if use:
                    s.spans.append((max(use, now - cap), now))
        if results or o.get('isMeta') or o.get('isCompactSummary'):
            continue
        if (o.get('origin') or {}).get('kind', 'human') != 'human':
            continue
        text = reminder.sub('', ' '.join(b.get('text', '') for b in bl if b.get('type') == 'text')).strip()
        if not text or text.startswith(NOT_HUMAN):
            continue
        if text.startswith('[Request interrupted'):
            s.counts['interrupts'] += 1
            continue
        s.counts['turns'] += 1
        if last_out:
            s.spans.append((max(last_out, now - cap), now))
    return s


def union(spans):
    total = end = 0
    for a, b in sorted(spans):
        if b > end:
            total += b - max(a, end)
            end = b
    return total


def accepted_from_log(log, auto=AUTO):
    """Commits in `git log --format='%H %B%x00'` output, less timer commits, reverts and what they revert."""
    entries = [e.strip() for e in log.split('\0')]
    entries = [e for e in entries if e and not auto.match(e[41:])]
    hashes = {e.split()[0] for e in entries}
    gone = {h for e in entries for h in re.findall(r'This reverts commit ([0-9a-f]{40})', e)} & hashes
    return len(hashes) - 2 * len(gone)


@dataclass
class Audit:
    cat: collections.Counter = field(default_factory=collections.Counter)       # category -> chars
    tool_out: collections.Counter = field(default_factory=collections.Counter)  # tool -> result chars
    err: int = 0
    dup: int = 0
    oversize: int = 0
    images: int = 0
    hook_hash: collections.Counter = field(default_factory=collections.Counter)
    hook_size: dict = field(default_factory=dict)
    active: int = 0  # transcripts with an event inside the window

    def boilerplate(self):
        return sum(self.hook_size[h] * (n - 1) for h, n in self.hook_hash.items() if n > 1)


def audit(sessions, start, reminder=re.compile(REMINDER, re.DOTALL), record_only=RECORD_ONLY):
    """Context composition over (name, events) pairs."""
    a = Audit()
    for _, events in sessions:
        id2name, id2path, seen, active = {}, {}, set(), False
        for o in events:
            if 'timestamp' in o:
                if stamp(o) < start:
                    continue  # trap 4
                active = True
            t = o.get('type')
            if t == 'attachment':
                if o.get('attachment', {}).get('type') in record_only:
                    continue  # trap 5
                s = json.dumps(o.get('attachment', {}))
                h = hashlib.md5(s.encode()).hexdigest()
                a.hook_hash[h] += 1
                a.hook_size[h] = len(s)
                a.cat['hook/attachment'] += len(s)
                continue
            if t not in ('user', 'assistant'):
                continue
            role = o.get('message', {}).get('role', t)
            for b in blocks(o.get('message', {}).get('content', [])):
                bt = b.get('type')
                if bt == 'text':
                    txt = b.get('text', '')
                    if role == 'assistant':
                        a.cat['assistant_text'] += len(txt)
                    else:
                        rem = sum(len(m) for m in reminder.findall(txt))
                        a.cat['injected_reminder'] += rem
                        a.cat['user_text'] += len(txt) - rem
                elif bt == 'thinking':
                    a.cat['thinking'] += len(b.get('thinking', ''))
                elif bt == 'tool_use':
                    id2name[b.get('id')] = b.get('name')
                    if b.get('name') == 'Read':
                        i = b.get('input') or {}
                        id2path[b.get('id')] = (i.get('file_path'), i.get('offset'), i.get('limit'))
                    a.cat['tool_use_input'] += len(json.dumps(b.get('input', {})))
                elif bt == 'tool_result':
                    c = b.get('content', '')
                    if isinstance(c, str):
                        s = c
                    else:
                        # chars/4 overstates a base64 image ~30x, so images are counted apart.
                        parts = c if isinstance(c, list) else [c]
                        imgs = [x for x in parts if isinstance(x, dict) and x.get('type') == 'image']
                        a.images += len(imgs)
                        s = json.dumps([x for x in parts if x not in imgs])
                    a.cat['tool_result'] += len(s)
                    a.tool_out[id2name.get(b.get('tool_use_id'), '?')] += len(s)
                    if b.get('is_error'):
                        a.err += len(s)
                    if len(s) > OVERSIZE:
                        a.oversize += len(s)
                    p = id2path.get(b.get('tool_use_id'))
                    if p is not None:
                        if p in seen:
                            a.dup += len(s)  # the same slice read again in this session
                        else:
                            seen.add(p)
        a.active += active
    return a


def restart_row(events, start):
    """(end, first human prompt, last text) for a session that ended in the window, else None."""
    first = last = ''
    end = 0
    for o in events:
        if o.get('type') not in ('user', 'assistant'):
            continue
        for b in blocks(o.get('message', {}).get('content', [])):
            if b.get('type') != 'text' or not (b.get('text') or '').strip():
                continue
            t = ' '.join(b['text'].split())[:110]
            if not first and o['type'] == 'user' and not t.startswith('<'):
                first = t
            last = f"[{o['type']}] {t}"
            end = stamp(o) if 'timestamp' in o else end
    return (end, first, last) if end > start else None


# ---------------------------------------------------------------- adapters

def read(path):
    with open(path, errors='ignore') as f:
        for line in f:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if isinstance(o, dict):
                yield o


def is_sdk(path):
    """An application, not a person, may write an SDK session's prompts."""
    with open(path, errors='ignore') as f:
        for line in f:
            if '"entrypoint"' in line:
                try:
                    return json.loads(line).get('entrypoint', '').startswith('sdk')
                except (ValueError, AttributeError):
                    pass
    return False


def select(root, start, self_, skip_subagents):
    """Transcripts modified after start, less the retro's own run (trap 1) and SDK sessions."""
    found = glob.glob(os.path.join(os.path.expanduser(root), '**', '*.jsonl'), recursive=True)
    return [f for f in found
            if not (skip_subagents and '/subagents/' in f)
            and os.path.getmtime(f) > start
            and not (self_ and self_ in f)
            and not is_sdk(f)]


def git(repo, *args):
    return subprocess.run(['git', '-C', repo, *args], check=False, capture_output=True, text=True).stdout.strip()


def accepted(repo, start, auto=AUTO):
    """Commits that reached the default branch since start, less reverts and what they reverted."""
    base = git(repo, 'symbolic-ref', '--quiet', '--short', 'refs/remotes/origin/HEAD')
    base = base or next((b for b in ('main', 'master') if git(repo, 'rev-parse', '--verify', '--quiet', b)), 'HEAD')
    return accepted_from_log(git(repo, 'log', base, '--since', f'@{int(start)}', '--format=%H %B%x00'), auto)


def find_repos(dirs):
    repos = {}  # the shared git dir -> one worktree, so worktrees count once
    for d in dirs:
        if os.path.isabs(d) and os.path.isdir(d) and git(d, 'rev-parse', '--is-inside-work-tree') == 'true':
            repos.setdefault(os.path.realpath(os.path.join(d, git(d, 'rev-parse', '--git-common-dir'))), d)
    return repos


def tok(chars):
    return chars // 4


def run_measure(args, start):
    per, spans, dirs = {}, [], set()
    for f in select(args.root, start, args.self, skip_subagents=True):
        s = measure_session(read(f), start, tuple(args.ask), re.compile(args.reminder, re.DOTALL))
        spans += s.spans
        dirs |= s.dirs
        if s.has_agent:
            per[f] = s.counts
    hours = union(spans) / 3600
    auto = re.compile(args.auto)
    per_repo = {os.path.dirname(k): accepted(d, start, auto) for k, d in find_repos(dirs).items()}
    changes = sum(per_repo.values())
    tot = sum(per.values(), collections.Counter())
    turns = tot['turns'] or 1
    print(f"sessions={len(per)}  human turns={tot['turns']}  interrupts={tot['interrupts']}  "
          f"declined={tot['declined']}  questions={tot['asks']} ({tot['asks'] / turns:.3f} per human turn)")
    print(f"human~hours={hours:.1f}  repos={len(per_repo)}  accepted changes={changes}  "
          f"per human hour={changes / hours if hours else 0:.2f}")
    print("\naccepted changes by repo (check for a tool that commits on a timer):")
    for d, n in sorted(per_repo.items(), key=lambda kv: -kv[1]):
        if n:
            print(f"  {n:4}  {d}")
    print("\nsessions by human turns (top):")
    for f, s in sorted(per.items(), key=lambda kv: -kv[1]['turns'])[:15]:
        print(f"  turns={s['turns']:<4} int={s['interrupts']:<2} dec={s['declined']:<2} ask={s['asks']:<2} "
              f"{os.path.basename(os.path.dirname(f))[-50:]}/{os.path.basename(f)[:8]}")


def run_context(args, start):
    files = select(args.root, start, args.self, skip_subagents=False)
    a = audit(((f, read(f)) for f in files), start, re.compile(args.reminder, re.DOTALL))
    tot = sum(a.cat.values()) or 1
    print(f"files={a.active} total~tok={tok(tot):,}\n")
    for k, v in a.cat.most_common():
        print(f"{k:18}{tok(v):>10,}  {100 * v / tot:5.1f}%")
    print("\noutput by tool (top):")
    for k, v in a.tool_out.most_common(12):
        print(f"  {k:24}{tok(v):>9,}")
    print(f"\nerrors~tok={tok(a.err):,}  dup-reads~tok={tok(a.dup):,}  oversize>40k~tok={tok(a.oversize):,}  "
          f"repeated-boilerplate~tok={tok(a.boilerplate()):,}")
    print(f"images={a.images} (~{a.images * IMAGE_TOKENS:,} tok, excluded from the char counts above)")
    print("\nmost-repeated injected blocks:")
    for h, n in a.hook_hash.most_common(6):
        if n > 1:
            print(f"  x{n:<4}{a.hook_size[h]:>7,}c each")


def run_restarts(args, start):
    rows = []
    for f in select(args.root, start, args.self, skip_subagents=True):  # a subagent cannot restart
        row = restart_row(read(f), start)
        if row:
            rows.append((row[0], f, row[1], row[2]))
    for end, f, first, last in sorted(rows):
        print(f"{time.strftime('%m-%d %H:%M', time.localtime(end))}  {os.path.basename(os.path.dirname(f))[:36]}")
        print(f"   first: {first}\n   last:  {last}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = p.add_subparsers(dest='command', required=True)
    for name, run in (('measure', run_measure), ('context', run_context), ('restarts', run_restarts)):
        c = sub.add_parser(name)
        c.set_defaults(run=run)
        c.add_argument('--days', type=float, required=True, help='the review window, in days')
        c.add_argument('--root', default='~/.claude/projects', help='transcript root')
        c.add_argument('--self', default='', help="the retro's own project-dir substring (trap 1)")
        if name != 'restarts':
            c.add_argument('--reminder', default=REMINDER, help='regex for harness text injected into user messages')
        if name == 'measure':
            c.add_argument('--ask', nargs='+', default=list(ASK), help='tools that put a question to the user')
            c.add_argument('--auto', default=AUTO.pattern, help='subject regex of commits a tool makes on a timer')
    argv = list(sys.argv[1:] if argv is None else argv)
    for i, a in enumerate(argv[:-1]):
        if a == '--self':  # a Claude Code project dir starts with '-', which argparse reads as an option
            argv[i:i + 2] = [f'--self={argv[i + 1]}']
            break
    args = p.parse_args(argv)
    args.run(args, time.time() - args.days * 86400)


if __name__ == '__main__':
    main()
