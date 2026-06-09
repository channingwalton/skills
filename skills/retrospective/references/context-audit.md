# Context audit (MEASURE step)

The MEASURE step has three outputs. This file covers all three; the first is
scriptable, the third partly so:

1. **Context waste** (scriptable) — quantify where a window's context tokens
   went, and trace the biggest noise to the skill / command / habit that
   produced it. Aggregate across all transcripts in the window — a totals pass,
   not a per-session note.
2. **Cost per failure** (manual) — tally the wasted calls/tokens each isolated
   failure cost, so the retro's headline is cost-weighted not count-based. This
   is a judgement tally over the DISTIL notes, not a script output — see "Cost
   per failure" below for why.
3. **Restarts** (script surfaces candidates, judgement confirms) — find
   abandoned-and-re-attempted sessions across the window. See "Restart
   detection" below.

Token estimate: `chars / 4`. Good enough for attribution; don't chase exactness.

## Inputs

Raw session transcripts as JSONL. Default location:
`~/.claude/projects/**/*.jsonl`. Each line is one event; `type` is `user` /
`assistant` / `attachment` / `system` / metadata. Message content is a list of
blocks: `text`, `thinking`, `tool_use` (has `name`, `input`, `id`),
`tool_result` (has `content`, `tool_use_id`, `is_error`). Map `tool_use.id` →
`name` to attribute each result to its tool.

Adjust the glob / window for the agent and host. If transcripts aren't JSONL,
skip MEASURE.

Format drift: hosts change what they store, so sanity-check two things before
trusting the composition output. If `thinking` reads 0, the host likely strips
thinking from stored transcripts — host behaviour, not zero thinking. And some
hosts inject harness context inside *user* messages rather than as attachments
(e.g. one host wraps it in `<system-reminder>` tags — the marker the script's
`REMINDER` pattern matches by default); adjust the pattern to your host's
marker, or `user_text` absorbs the injections and injection bloat is badly
undercounted.

## What to compute

1. **Composition** — total chars by category: `tool_result`, `tool_use_input`,
   `hook/attachment`, `assistant_text`, `user_text`, `thinking`, meta. The
   conversation (user+assistant text) is usually a small slice; tool I/O and
   injected hooks dominate.
2. **Output by tool** — sum `tool_result` chars per tool name. Two or three
   tools (typically `Read`, `Bash`) tend to own most of it.
3. **Noise buckets** (the "carried but unused" proxies):
   - **Errored / denied** results (`is_error`).
   - **Duplicate re-reads** — same `Read` path twice in one session.
   - **Oversized dumps** — single results over ~40k chars (often subagents
     reading whole generated files).
   - **Repeated boilerplate** — identical `attachment` blocks across sessions
     (hash them). Attribute by `attachment.type`: `skill_listing` and
     `deferred_tools_delta` scale with how many skills / MCP servers are
     installed (prune the install surface, not a file); `hook_additional_context`
     is a plugin's SessionStart injection (disable the plugin or edit upstream,
     never the cache). Note these are the **most expensive actuator class** in
     the SORT ordering — a standing per-session tax paid whether or not the
     installed thing is used. Pruning the install surface is a gate-vs-wallpaper
     call: it removes an always-on cost, so it often beats any in-file edit.

## Trace to source — the point of the step

A token number is only actionable once tied to what emits it:

- Recurring large `git diff` / verbose command output on a known trigger
  (e.g. every commit) → a slash-command / skill `!`-injection. Cap or scope it.
  *(This audit's origin: a commit-and-push command injected `git diff HEAD`
  uncapped on every invocation; fix was stat + capped diff.)*
- Oversized dumps in subagents → the dispatch prompt told them to read whole
  files; pass a `jq` slice or summary instead.
- Per-session boilerplate → installed-but-unused plugins / MCP servers, or a
  plugin's SessionStart hook.

Route each finding through the SORT table. The "Skill/command injects unused
context" row is the common landing spot.

## Script

Plain `python3`, stdlib only. Edit the glob and window.

```python
import json, os, glob, time, collections, hashlib, re

DAYS = 7
REMINDER = re.compile(r'<system-reminder>.*?</system-reminder>', re.S)  # adjust marker per host
files = [f for f in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True)
         if time.time() - os.path.getmtime(f) < DAYS*86400]

def blocks(c):
    return c if isinstance(c, list) else ([{'type':'text','text':c}] if isinstance(c, str) else [])

cat = collections.Counter()        # category -> chars
tool_out = collections.Counter()   # tool name -> tool_result chars
err = dup = oversize = 0
hook_hash = collections.Counter(); hook_size = {}

for f in files:
    id2name = {}; id2path = {}; seen_paths = set()
    for line in open(f, errors='ignore'):
        try: o = json.loads(line)
        except: continue
        t = o.get('type')
        if t == 'attachment':
            s = json.dumps(o.get('attachment', {}))
            h = hashlib.md5(s.encode()).hexdigest()
            hook_hash[h] += 1; hook_size[h] = len(s)
            cat['hook/attachment'] += len(s); continue
        if t not in ('user', 'assistant'): continue
        for b in blocks(o.get('message', {}).get('content', [])):
            bt = b.get('type'); role = o.get('message', {}).get('role', t)
            if bt == 'text':
                txt = b.get('text', '')
                if role == 'assistant':
                    cat['assistant_text'] += len(txt)
                else:
                    rem = sum(len(m) for m in REMINDER.findall(txt))
                    cat['injected_reminder'] += rem
                    cat['user_text'] += len(txt) - rem
            elif bt == 'thinking':
                cat['thinking'] += len(b.get('thinking', ''))
            elif bt == 'tool_use':
                id2name[b.get('id')] = b.get('name')
                if b.get('name') == 'Read':
                    id2path[b.get('id')] = (b.get('input') or {}).get('file_path')
                cat['tool_use_input'] += len(json.dumps(b.get('input', {})))
            elif bt == 'tool_result':
                c = b.get('content', ''); s = c if isinstance(c, str) else json.dumps(c)
                cat['tool_result'] += len(s)
                name = id2name.get(b.get('tool_use_id'), '?'); tool_out[name] += len(s)
                if b.get('is_error'): err += len(s)
                if len(s) > 40000: oversize += len(s)
                p = id2path.get(b.get('tool_use_id'))
                if p is not None:
                    if p in seen_paths: dup += len(s)   # same path Read again this session
                    else: seen_paths.add(p)

tok = lambda c: c // 4
tot = sum(cat.values())
print(f"files={len(files)} total~tok={tok(tot):,}\n")
for k, v in cat.most_common():
    print(f"{k:18}{tok(v):>10,}  {100*v/tot:5.1f}%")
print("\noutput by tool (top):")
for k, v in tool_out.most_common(12):
    print(f"  {k:24}{tok(v):>9,}")
dupe_boiler = sum(hook_size[h]*(n-1) for h, n in hook_hash.items() if n > 1)
print(f"\nerrors~tok={tok(err):,}  dup-reads~tok={tok(dup):,}  oversize>40k~tok={tok(oversize):,}  repeated-boilerplate~tok={tok(dupe_boiler):,}")
print("\nmost-repeated injected blocks:")
for h, n in hook_hash.most_common(6):
    if n > 1: print(f"  x{n:<4}{hook_size[h]:>7,}c each")
```

The `dup-reads` figure counts the result chars of any `Read` of a path already
read earlier in the same session — re-reading a file the model already had. It
attributes by `tool_use.id` → `input.file_path`. Limits worth knowing: it only
covers the `Read` tool (not `cat` via `Bash`, which can't be path-attributed
reliably), and a re-read after a genuine edit is not necessarily waste — treat a
high figure as a pointer to investigate, not a verdict.

## Restart detection

A session the user abandoned and re-prompted fresh is the most expensive
failure shape — the whole abandoned transcript is the cost — and per-transcript
DISTIL cannot see it: an abandoned session just looks like one that ended. This
is a cross-transcript pass.

The script lists each session's opening prompt and final event, in time order.
Adjacent sessions with near-duplicate openings, or an opening that re-states
the previous session's unfinished task, are restart candidates:

```python
import json, os, glob, time

DAYS = 7
files = sorted((f for f in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True)
                if time.time() - os.path.getmtime(f) < DAYS*86400), key=os.path.getmtime)

def texts(o):
    c = o.get('message', {}).get('content', [])
    c = c if isinstance(c, list) else [{'type': 'text', 'text': c}]
    return [b.get('text', '') for b in c if b.get('type') == 'text' and b.get('text', '').strip()]

for f in files:
    first = last = ''
    for line in open(f, errors='ignore'):
        try: o = json.loads(line)
        except: continue
        if o.get('type') not in ('user', 'assistant'): continue
        for t in texts(o):
            t = ' '.join(t.split())[:110]
            if not first and o['type'] == 'user' and not t.startswith('<'): first = t
            last = f"[{o['type']}] {t}"
    print(f"{time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(f)))}  {os.path.basename(os.path.dirname(f))[:36]}")
    print(f"   first: {first}\n   last:  {last}")
```

Confirming a candidate is judgement, not script: read the abandoned session's
tail. A last event that is an error, an unanswered question, or mid-task tool
output (rather than a wrap-up) confirms abandonment. The failure to fix is
whatever caused the abandonment — find it in the tail, cost it at the full
abandoned transcript, and route it through SORT like any other finding. A
session that ends cleanly and is followed by related new work is continuation,
not a restart — don't count it.

## Cost per failure (manual — not scripted)

The script above attributes *context* tokens to *tools*. It cannot attribute
*wasted* tokens to *failures*, and you should not extend it to try. Deciding
which calls belong to a given failure — from its first wrong turn to its
resolution — is the same judgement as isolating the failure in the first place
(DISTIL), and it does not separate mechanically from interleaved work: a
session rarely does one thing at a time, so "calls spent on this failure" is a
read, not a count. A script that claims it will produce confident nonsense.

Do it by hand over the DISTIL notes. For each isolated failure, an approximate
cost is fine: count the tool calls (and roughly their tokens, `chars/4`) between
the first wrong turn and the point the model recovered. Flag it as approximate;
do not present it as attribution the interleaving won't support. The number only
needs to be good enough to separate an expensive misdirection (e.g. ten calls
down a false hypothesis) from a cosmetic self-correction (one call, immediately
fixed) — that ranking is the point, not the precise figure.

This is what makes the retro headline cost-weighted: one expensive failure can
outweigh a tail of papercuts, and a count-based ratio would hide that. One
exception: wrong-outcome mistakes keep finding status regardless of cost —
cost ranks them, it does not gate them.

## Output

Feed the numbers into the retro's normal PROPOSE shape. One line per finding:
the token cost, the source, the concrete edit. Don't report a category total
without naming what to change.
