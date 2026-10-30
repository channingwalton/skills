# Context audit (MEASURE step)

## Contents

- Five traps the retro's own MEASURE keeps hitting
- Inputs
- What to compute
- Trace to source — the point of the step
- Script
- Restart detection
- Output

This file covers two of the MEASURE outputs. Corrections and throughput are in
`references/corrections.md`.

1. **Context waste** (scriptable) — quantify where a window's context tokens
   went, and trace the biggest noise to the skill / command / habit that
   produced it. Aggregate across all transcripts in the window — a totals pass,
   not a per-session note. Tokens are a diagnosis here, not the cost: a finding
   earns an edit when it explains a failure that the user corrected.
2. **Restarts** (script surfaces candidates, judgement confirms) — find
   abandoned-and-re-attempted sessions across the window. See "Restart
   detection" below.

Token estimate: `chars / 4`. Good enough for attribution; don't chase exactness.

**Except for images.** `chars/4` is wrong by ~30x on a base64 image block — a screenshot is
~250k chars but costs roughly `(w x h)/750` ≈ 1.4k tokens. Left in, 11 screenshots read as
470k phantom tokens and top the oversize ranking, which is a fabricated finding pointing at
a real habit. The script below counts them separately; never fold an image back into a char
total, and treat any "oversize dump" that turns out to be a Read of a `.png`/`.jpg` as ~1.4k.

## Five traps the retro's own MEASURE keeps hitting

Each has fired at least once — the MEASURE step reporting a measurement
artefact as a finding. Guard against all five before trusting a number:

1. **Exclude the retro's own run.** The distil fleet runs *during* MEASURE, so its
   subagent transcripts fall inside the mtime window and dominate the noise
   buckets — one run measured 585k `dup-read` tok and 526k `oversize` tok that
   were 73k and 84k once the fleet was excluded (8x and 6x inflation, each
   pointing at a fabricated top-finding). Set `SELF` to the retro's own project
   dir substring and drop it from every glob (both scripts below do this, and so
   does the script in `references/corrections.md`).

2. **Re-ground and date the evidence before reporting a defect.** A raw `grep`
   count over transcripts is not an event count — it sweeps subagent quotes and
   assistant prose. An error appearing *in* the window is not proof it is still
   live. Before banking any measurement- or grep-derived "standing defect", read
   the current config/source and date the actual events: two retros reported a
   dead hook ("99 occurrences") and an "unfixed" bug that both dissolved on
   checking current state. This is the same `assert-before-check` class the
   run's own gate targets, committed by the run reporting it.

3. **Drop prompt-only transcripts before counting sessions.** Eval harnesses
   such as skill-creator's trigger runs launch hundreds of `claude -p` sessions
   that are killed after the first decision, leaving a transcript with a user
   prompt and no assistant turn. On 2026-10-07 one run left 498 of them, which
   would have quadrupled the window's session count. Count a transcript as a
   session only if it has an assistant turn; report the eval run itself once,
   by its parent session.

4. **Window by event time, not file time.** A transcript file's modification
   time is not the time of its events. On 2026-10-30 a 14-day window selected
   2,638 files by modification time, but only 207 had an assistant turn inside
   the window, and 10,913 of 14,037 human-attention spans in those files were
   older than the window. Use modification time only as a pre-filter, then drop
   each event whose `timestamp` is before the window. The scripts here and in
   `references/corrections.md` do both.

5. **Drop attachments that only the transcript keeps.** Some attachments are
   records, not context: `prompt_snapshot` stores the system prompt and tool
   definitions, and `hook_success` stores each hook's command line and exit
   code. On 2026-10-30 they were 6.7M of the window's 9.7M attachment tokens,
   which read as attachment bloat. The script below skips the types in
   `RECORD_ONLY`; check a new large attachment type's fields before you count it.

## Inputs

Raw session transcripts as JSONL. Default location:
`~/.claude/projects/**/*.jsonl`. Each line is one event; `type` is `user` /
`assistant` / `attachment` / `system` / metadata. Message content is a list of
blocks: `text`, `thinking`, `tool_use` (has `name`, `input`, `id`),
`tool_result` (has `content`, `tool_use_id`, `is_error`). Map `tool_use.id` →
`name` to attribute each result to its tool.

**The scripts below are written against Claude Code's transcript schema** (the
glob, the event `type` values, the content-block shape above). Other hosts store
sessions differently — Codex, for one, writes its own JSONL with a different
event shape — so changing the glob is usually *not* enough. A schema mismatch
does not raise: the scripts run happily and report near-zero, which reads as "no
waste" when it means "parsed nothing". Before trusting any output, sanity-check
that `total~tok` is the right order of magnitude for the window; if it isn't,
port the block-extraction to your host's shape or skip MEASURE. If transcripts
aren't JSONL at all, skip MEASURE.

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
from datetime import datetime

DAYS = 7
START = time.time() - DAYS*86400
REMINDER = re.compile(r'<system-reminder>.*?</system-reminder>', re.S)  # adjust marker per host
RECORD_ONLY = {'prompt_snapshot', 'hook_success'}  # stored in the transcript, never sent (trap 5)
SELF = ''  # this retro's own project-dir substring, e.g. '-Users-you-dev-skills'; its distil
           # fleet runs NOW and floats to the top of dup-read/oversize/tool-output if left in.

def via_sdk(f):  # an application, not a person, may write the prompts; see corrections.md
    for line in open(f, errors='ignore'):
        if '"entrypoint"' in line:
            try: return json.loads(line).get('entrypoint', '').startswith('sdk')
            except: pass
    return False

files = [f for f in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True)
         if os.path.getmtime(f) > START and (not SELF or SELF not in f) and not via_sdk(f)]

def stamp(o):
    return datetime.fromisoformat(o['timestamp'].replace('Z', '+00:00')).timestamp()

def blocks(c):
    return c if isinstance(c, list) else ([{'type':'text','text':c}] if isinstance(c, str) else [])

cat = collections.Counter()        # category -> chars
tool_out = collections.Counter()   # tool name -> tool_result chars
err = dup = oversize = img_n = 0
hook_hash = collections.Counter(); hook_size = {}
active = set()                     # files with an event inside the window

for f in files:
    id2name = {}; id2path = {}; seen_paths = set()
    for line in open(f, errors='ignore'):
        try: o = json.loads(line)
        except: continue
        if 'timestamp' in o:
            if stamp(o) < START: continue  # mtime is not the window (trap 4)
            active.add(f)
        t = o.get('type')
        if t == 'attachment':
            if o.get('attachment', {}).get('type') in RECORD_ONLY: continue  # trap 5
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
                    i = b.get('input') or {}
                    id2path[b.get('id')] = (i.get('file_path'), i.get('offset'), i.get('limit'))
                cat['tool_use_input'] += len(json.dumps(b.get('input', {})))
            elif bt == 'tool_result':
                c = b.get('content', '')
                if isinstance(c, str):
                    s = c
                else:
                    # Split image blocks out before measuring. A base64 PNG is ~250k chars
                    # but costs ~(w*h)/750 ≈ 1.4k tokens, so chars/4 overstates it ~30x and
                    # floats screenshots to the top of the oversize ranking.
                    parts = c if isinstance(c, list) else [c]
                    imgs = [x for x in parts if isinstance(x, dict) and x.get('type') == 'image']
                    img_n += len(imgs)
                    s = json.dumps([x for x in parts if x not in imgs])
                cat['tool_result'] += len(s)
                name = id2name.get(b.get('tool_use_id'), '?'); tool_out[name] += len(s)
                if b.get('is_error'): err += len(s)
                if len(s) > 40000: oversize += len(s)
                p = id2path.get(b.get('tool_use_id'))
                if p is not None:
                    if p in seen_paths: dup += len(s)   # same slice Read again this session
                    else: seen_paths.add(p)

tok = lambda c: c // 4
tot = sum(cat.values())
print(f"files={len(active)} total~tok={tok(tot):,}\n")
for k, v in cat.most_common():
    print(f"{k:18}{tok(v):>10,}  {100*v/tot:5.1f}%")
print("\noutput by tool (top):")
for k, v in tool_out.most_common(12):
    print(f"  {k:24}{tok(v):>9,}")
dupe_boiler = sum(hook_size[h]*(n-1) for h, n in hook_hash.items() if n > 1)
print(f"\nerrors~tok={tok(err):,}  dup-reads~tok={tok(dup):,}  oversize>40k~tok={tok(oversize):,}  repeated-boilerplate~tok={tok(dupe_boiler):,}")
print(f"images={img_n} (~{img_n*1400:,} tok, excluded from the char counts above)")
print("\nmost-repeated injected blocks:")
for h, n in hook_hash.most_common(6):
    if n > 1: print(f"  x{n:<4}{hook_size[h]:>7,}c each")
```

The `dup-reads` figure counts the result chars of any `Read` of a slice already
read earlier in the same session — re-reading text the model already had. It
attributes by `tool_use.id` → `(file_path, offset, limit)`, so chunked reads of
one large file are not counted as re-reads (keyed on path alone, they once made
26k of a session's 64k "dup-read" tokens). Limits worth knowing: it only
covers the `Read` tool (not `cat` via `Bash`, which can't be path-attributed
reliably), and a re-read after a genuine edit is not necessarily waste — treat a
high figure as a pointer to investigate, not a verdict.

## Restart detection

A session the user abandoned and re-prompted fresh is the most expensive
failure shape — the user discarded the whole session, which makes it the
strongest correction — and per-transcript
DISTIL cannot see it: an abandoned session just looks like one that ended. This
is a cross-transcript pass.

The script lists each session's opening prompt and final event, in time order.
Adjacent sessions with near-duplicate openings, or an opening that re-states
the previous session's unfinished task, are restart candidates:

```python
import json, os, glob, time
from datetime import datetime

DAYS = 7
START = time.time() - DAYS*86400
SELF = ''  # this retro's own project-dir substring (trap 1)

def via_sdk(f):  # an application, not a person, may write the prompts; see corrections.md
    for line in open(f, errors='ignore'):
        if '"entrypoint"' in line:
            try: return json.loads(line).get('entrypoint', '').startswith('sdk')
            except: pass
    return False

files = [f for f in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True)
         if '/subagents/' not in f  # a subagent transcript cannot be a restart
         and os.path.getmtime(f) > START and (not SELF or SELF not in f) and not via_sdk(f)]

def stamp(o):
    return datetime.fromisoformat(o['timestamp'].replace('Z', '+00:00')).timestamp()

def texts(o):
    c = o.get('message', {}).get('content', [])
    c = c if isinstance(c, list) else [{'type': 'text', 'text': c}]
    return [b.get('text', '') for b in c if b.get('type') == 'text' and b.get('text', '').strip()]

rows = []
for f in files:
    first = last = ''; end = 0
    for line in open(f, errors='ignore'):
        try: o = json.loads(line)
        except: continue
        if o.get('type') not in ('user', 'assistant'): continue
        for t in texts(o):
            t = ' '.join(t.split())[:110]
            if not first and o['type'] == 'user' and not t.startswith('<'): first = t
            last = f"[{o['type']}] {t}"; end = stamp(o) if 'timestamp' in o else end
    if end > START:  # the session ended in the window; mtime is not the window (trap 4)
        rows.append((end, f, first, last))

for end, f, first, last in sorted(rows):
    print(f"{time.strftime('%m-%d %H:%M', time.localtime(end))}  {os.path.basename(os.path.dirname(f))[:36]}")
    print(f"   first: {first}\n   last:  {last}")
```

Confirming a candidate is judgement, not script: read the abandoned session's
tail. A last event that is an error, an unanswered question, or mid-task tool
output (rather than a wrap-up) confirms abandonment. The failure to fix is
whatever caused the abandonment — find it in the tail, rank it as the
strongest correction, and route it through SORT like any other finding. A session that ends cleanly and is followed by related new work is
continuation, not a restart — don't count it.

## Output

Feed the numbers into the retro's normal PROPOSE shape. One line per finding:
the corrected failure that it explains, the token cost, the source, the
concrete edit. Don't report a category total without naming what to change.
