# AI Skills

[![skills.sh](https://skills.sh/b/channingwalton/skills)](https://skills.sh/channingwalton/skills)

A few useful skills I use daily, written as agent agnostic as possible.

## Quick start

Install with `skills.sh`:

```sh
npx skills@latest add channingwalton/skills
```

Then pick the skills you want to add to your agent.

Manual install:

```sh
mkdir -p ~/.codex/skills
cp -R skills/<skill-name> ~/.codex/skills/
```

## Skills

The published install surface contains six skills.

### [`chatter`](skills/chatter/SKILL.md)

Filesystem-based multi-agent chat.

Use it when you want agents to start, join, or continue a local conversation through markdown files in a shared thread directory. It includes a `chatter` helper script for posting, reading, waiting, and looping without hand-rolling the protocol.

Depends on: no other skills.

### [`software-development`](skills/software-development/SKILL.md)

An Extreme Programming workflow for agent-assisted software development.

It pushes agents through planning, TDD, refactoring, review, commit verification, and retrospective instead of jumping straight to edits.

Depends on: [`fix-loop`](skills/fix-loop/SKILL.md) (review step) and [`retrospective`](skills/retrospective/SKILL.md) (complete step). It also delegates to a language-specific skill when one is installed (e.g. `scala-developer`, `unison-development`); these are not published here.

### [`fix-loop`](skills/fix-loop/SKILL.md)

An iterative review-fix cycle for critical issues.

Use it when you want an agent to review a change, fix critical findings, and repeat until the critical issues are resolved or need human judgement.

Depends on: the host's native code review (Claude Code's `code-review` skill or `codex review`), plus built-in house checks. On other hosts the house checks are the whole review. The repair phase is built in (the Fixer contract).

### [`retrospective`](skills/retrospective/SKILL.md)

A post-session improvement loop.

Use it when you want to inspect what worked, what failed, and turn useful lessons into concrete skill edits or follow-up notes. See the [skill README](skills/retrospective/README.md) for details.

Depends on: no other skills.

### [`requirements-report`](skills/requirements-report/SKILL.md)

Requirements-to-tests traceability.

Use it when requirements or a specification drive implementation: link Markdown requirements to tests by ID, then render pass, fail, or untested status from JUnit XML. See the [skill README](skills/requirements-report/README.md) for details.

Depends on: no other skills. Needs a test runner that emits JUnit XML.

### [`pair-programming`](skills/pair-programming/SKILL.md)

Pair with an agent on a change you build yourself.

Use it when you want help thinking through a feature, its design options, and the code changes, while you keep the design and the keyboard. It protects your theory of the system (in Peter Naur's sense) so you can explain and extend the code afterwards. See the [skill README](skills/pair-programming/README.md) for details.

Depends on: no other skills.

## Structure

```text
skills/
  chatter/
    SKILL.md
    chatter
    test_chatter.py
  fix-loop/
    SKILL.md
  software-development/
    SKILL.md
    references/
  retrospective/
    SKILL.md
    README.md
  requirements-report/
    SKILL.md
    README.md
    reqreport.py
    test_reqreport.py
    references/
  pair-programming/
    SKILL.md
    README.md
```

Each skill is self-contained. `SKILL.md` is the entrypoint; extra scripts or references live beside it.

## Evaluation

Use `evals/` to compare candidate skill edits against `origin/main` with blind prompts and scorecards.

## Licence

MIT.
