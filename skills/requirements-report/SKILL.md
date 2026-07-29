---
name: requirements-report
description: >-
  Link Markdown requirements to tests and render pass, fail, or untested
  traceability from JUnit XML. Use before writing tests whenever requirements or
  a specification drive implementation, and for living requirements, acceptance
  criteria tied to tests, finding untested requirements, or mapping a failure to
  its requirement. Works with any test runner that emits JUnit XML; test names
  must carry requirement IDs.
---

# Requirements report

Treat the rendered report as the requirements document: preserve all marked and unmarked
Markdown in order, add status to marked lines, roll status up through headings, and disclose
test source and failures beneath each requirement.

A requirement is a Markdown line containing `` `#id` ``. Link a test through that ID in its
JUnit test name. Read:

- [conventions.md](references/conventions.md) before adding markers or naming tests; it
  defines document structure, IDs, identifier-based names, tables, and parameterisation.
- [junit-xml.md](references/junit-xml.md) when configuring the project's test runner.

## Use the bundled renderer

Use `reqreport.py` beside this file. It is stdlib-only Python 3. Never reimplement it per
project.

```
python3 reqreport.py --requirements requirements/ \
                     --junit build/test-results/test/ \
                     --sources src/test/ \
                     --out target/requirements/
```

Exit codes are 0 for clean, 1 for requirement problems, and 2 for bad input. Options may
live in `.reqreport.json` (`requirements`, `junit`, `sources`, `out`, `root`); `--no-gate`
writes the report without failing.

Set `--root` from the project root known to the build tool. It defaults to the working
directory. Never derive it from Git: repository and project roots differ in monorepos.

## Rules

- Put `#the-id` in free-text names. For identifier names such as Rust and Go, use
  `req_the_id`; Go needs `Test_req_the_id`, not `TestReqTheId`.
- Descriptive suffixes are allowed because IDs resolve longest-first against the document.
  An unknown ID is an orphan and fails the build.
- Allow only one test per requirement ID. Multiple tests naming one ID are fatal: merge
  assertions of one behaviour or split distinct behaviours into separately identified
  requirements.
- Use the name suffix to describe what the test checks, not to repeat the requirement.
- Link an existing test only when its coverage is clear. Leave uncertain tests unlinked and
  tell the user; a false link reports coverage that does not exist.

## Writing requirements

Draft from the user's requirements, existing specifications, ADRs, tickets, or README. Never
invent behaviour:

- Put every unresolved choice in an `Undecided` list, even when an inference feels obvious.
- Offer concrete alternative behaviours instead of open questions.
- Ask early about expensive-to-reverse semantics: observable behaviour, time granularity
  and zones, ordering, and whether assumed editing or deletion exists.

## Workflow

1. Make the test runner emit JUnit XML using [junit-xml.md](references/junit-xml.md). Run it
   and inspect the output directory and test names.
2. Find or create `requirements/`. Draft only from user-approved or existing sources; ask
   when behaviour is missing.
3. Add markers and name tests using [conventions.md](references/conventions.md).
4. Wire tests then `reqreport.py` into the build.
5. Run the build and show the user the generated index. Expect untested requirements on the
   first run; they show the setup is working.

## Wiring

- Delete the JUnit XML directory before every run; stale XML produces a plausible old
  report.
- Force tests before the report in parallel task graphs; for example, use `Def.sequential`
  in sbt rather than two `.value` calls.
- Let failed tests continue to the report, then let the report gate the build. Otherwise a
  test failure prevents its requirement report from being produced.

## Gates

| Check | Fails when |
|---|---|
| Failure | a test naming a requirement failed |
| Roll-up | any descendant of a requirement failed |
| No test | no test names a requirement — nothing demonstrates it works |
| Orphan | a test names an id no document defines |
| Duplicate | the same `#id` is defined twice — fatal, it double-counts coverage |
| Shared id | two tests name the same `#id` — fatal, the second assertion is an unwritten requirement |

Tests with no id are listed but are **not** errors. Unit tests need not map to requirements.

## Review control

No mechanical check detects a test that names one requirement but tests another. Review the
requirement prose beside the disclosed test source; that adjacency is the control. Keep
source requirements free of code, while allowing the rendered report to disclose test code
and stack traces.
