# Context audit (MEASURE step)

This file covers two MEASURE outputs: **context waste**, where the window's
tokens went and what produced them; and **restarts**, where the script finds
candidates and judgement confirms them.

Token estimate: `chars / 4`. Good enough for attribution; don't chase exactness.

**Except for images.** `chars/4` overstates a base64 image ~30x: a screenshot is
~250k chars but costs roughly `(w x h)/750` ≈ 1.4k tokens, and 11 screenshots
once read as 470k phantom tokens at the top of the oversize ranking. The script
counts images separately. Never fold an image back into a char total, and count
an "oversize dump" that is a Read of a `.png`/`.jpg` as ~1.4k.

## Five traps the retro's own MEASURE keeps hitting

Each has fired at least once — the MEASURE step reporting a measurement
artefact as a finding. Guard against all five before trusting a number:

1. **Exclude the retro's own run.** The distil fleet runs *during* MEASURE, so its
   subagent transcripts fall inside the mtime window and dominate the noise
   buckets — one run measured 585k `dup-read` tok and 526k `oversize` tok that
   were 73k and 84k once the fleet was excluded (8x and 6x inflation, each
   pointing at a fabricated top-finding). Pass the retro's own project-dir
   substring as `--self` to every `retro.py` command.

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
   each event whose `timestamp` is before the window. `retro.py` does both.

5. **Drop attachments that only the transcript keeps.** Some attachments are
   records, not context: `prompt_snapshot` stores the system prompt and tool
   definitions, and `hook_success` stores each hook's command line and exit
   code. On 2026-10-30 they were 6.7M of the window's 9.7M attachment tokens,
   which read as attachment bloat. `retro.py` skips the types in its
   `RECORD_ONLY` set; check a new large attachment type's fields before you count it.

## Inputs

Raw session transcripts as JSONL. Default location:
`~/.claude/projects/**/*.jsonl`. Each line is one event; `type` is `user` /
`assistant` / `attachment` / `system` / metadata. Message content is a list of
blocks: `text`, `thinking`, `tool_use` (has `name`, `input`, `id`),
`tool_result` (has `content`, `tool_use_id`, `is_error`). Map `tool_use.id` →
`name` to attribute each result to its tool.

**`retro.py` reads Claude Code's transcript schema** (the glob, the event
`type` values, the content-block shape above). Other hosts store sessions
differently — Codex, for one, writes its own JSONL with a different event shape —
so a new `--root` is usually *not* enough. A schema mismatch does not raise: the
script runs happily and reports near-zero, which reads as "no waste" when it
means "parsed nothing". Before trusting any output, sanity-check that
`total~tok` is the right order of magnitude for the window; if it isn't, port
the parsing in `retro.py` to your host's shape or skip MEASURE. If transcripts
aren't JSONL at all, skip MEASURE.

Format drift: hosts change what they store, so sanity-check two things before
trusting the composition output. If `thinking` reads 0, the host likely strips
thinking from stored transcripts — host behaviour, not zero thinking. And some
hosts inject harness context inside *user* messages rather than as attachments
(e.g. one host wraps it in `<system-reminder>` tags — the marker that
`--reminder` matches by default); pass your host's marker as `--reminder`, or
`user_text` absorbs the injections and injection bloat is badly undercounted.

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

```sh
python3 <skill-dir>/retro.py context --days <window> --self <this retro's project-dir substring>
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

Per-transcript DISTIL cannot see a restart: an abandoned session looks like one
that ended. This is a cross-transcript pass.

`retro.py restarts --days <window> --self <substring>` lists each session's
opening prompt and final text, in time order, and leaves out subagent
transcripts. Adjacent sessions with near-duplicate openings, or an opening that
re-states the previous session's unfinished task, are restart candidates.

Confirming a candidate is judgement, not script: read the abandoned session's
tail. A last event that is an error, an unanswered question, or mid-task tool
output (rather than a wrap-up) confirms abandonment. Find the cause in the tail,
and route it through SORT like any other finding. A session that ends cleanly
and is followed by related new work is continuation, not a restart.

## Output

Feed the numbers into the retro's normal PROPOSE shape. One line per finding:
the corrected failure that it explains, the token cost, the source, the
concrete edit. Don't report a category total without naming what to change.
