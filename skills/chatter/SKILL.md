---
name: chatter
description: Start, join or continue a local multi-agent chat through Markdown files in a shared thread directory.
disable-model-invocation: true
---

# chatter

Filesystem-based multi-agent chat. Messages are markdown files (YAML frontmatter + body) in a shared thread directory. No network.

Core behaviour: read new messages -> reply if useful -> wait -> repeat -> exit when resolved or silent.

## The helper

All filesystem mechanics live in the bundled `chatter` script next to `SKILL.md`; use it for every post and read, never hand-written JSON or filenames. Resolve its absolute path once and invoke that path as the first command token. Examples below use `chatter` for readability.

```sh
chatter post <slug> <agent-id> <content> [--in-reply-to ID]   # prints filename
chatter read <slug> [--since FILENAME] [--wait-create SEC]    # JSON messages
chatter wait <slug> [--timeout SEC] [--wait-create SEC]       # 0 on event, non-zero on timeout/error
chatter loop <slug> <agent-id> [--timeout SEC] [--silences N] [--since FILENAME]
# stateful read/wait loop; prints next non-self message batch as JSON
```

Pass content that contains backticks, `$`, `!`, `\`, or similar shell metacharacters on stdin, never as a double-quoted argument:

```sh
chatter post <slug> <you> - --in-reply-to <id> <<'EOF'
Use `Array.prototype.flat()` not $foo.
EOF
```

## Root and Time

Root resolution: `--root <path>`, then `$CHATTER_ROOT`, then `./agent-chatter`. Run from the project working directory unless all agents agree on another root.

Requires `python3`. `wait` uses `fswatch`, `inotifywait`, or polling. Filename order is protocol order; `created_at` is diagnostic. Slug timestamps and message timestamps use local time; generate slugs with plain `date`, not UTC.

## Agent identity

Pick a stable `agent-id` for this conversation, in order, and post only under it:

1. User-specified (e.g. "join as `codex-reviewer`").
2. Host name alone: `claude-code`, `codex`, `opencode`. If the thread already has a message from that host (different session), ask the user for a discriminator (e.g. `claude-code-2`).
3. Ask the user if genuinely unknown.

## Start vs join

| Action | Steps |
|---|---|
| **Start** | slug = `{yyyyMMdd-HHmm}-{kebab-topic}`; `chatter post <slug> <you> -` creates the thread; tell the user `Instruction for other agents: join chatter <slug>`; enter `loop` immediately. The user brings the other agents in, so start without asking about invitations. |
| **Join** | `chatter loop <slug> <you> --wait-create 300`, which waits for the other agent's first post; reply if useful; call `loop` again. Ask the user only if the thread never appears. |

## Replying

Set `--in-reply-to <id>` on every post that responds to another message. The id is the target message's filename without `.md` (e.g. `0003-claude-code`) — usually the message you're directly addressing, not necessarily the latest. Only the opening post of a thread omits the flag.

## The loop

`chatter loop` persists cursor state in `.chatter-state/<agent>.json`, filters self-authored messages, and keeps long wait defaults (`--timeout 300`, `--silences 2`). Each call returns when the next non-self message batch arrives, or after `--silences` consecutive timeouts:

```sh
chatter loop <slug> <you> [--wait-create 300]   # join: catch up + wait
# exit 0 with status:messages -> reply if useful
chatter post <slug> <you> - --in-reply-to <target.id>
chatter loop <slug> <you>                        # rejoin: wait for next batch
# exit 1 with status:silent -> conversation done
```

Exit codes: `0` new messages, `1` silent, `2` iteration cap. On `messages`, reply only when adding information, disagreement, a clarifying question, or a next step. Acks do not need replies. On `silent`, resolution, or explicit sign-off, exit.

If the thread circles, call that out and propose a conclusion. For protocol debugging, use `read` and `wait` directly; after `wait`, always re-run `read` because the wake may be from a temp file or your own write.

## Report to user

- **Before loop:** thread slug, path, your agent-id, and for a new thread the instruction line from Start.
- **After exit:** why (resolution / silence / iteration cap), brief outcome, thread path for review.
