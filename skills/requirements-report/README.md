# requirements-report

Turn Markdown requirements into a living HTML traceability report showing which
requirements pass, fail, or have no test.

The skill helps an agent:

- write requirements without inventing unspecified behaviour;
- give each requirement a stable ID;
- link each ID to a test through its JUnit test name;
- configure the test runner and build;
- render the original Markdown with rolled-up status, test source, and failures;
- fail the build for failed, untested, orphaned, duplicate, or ambiguously linked
  requirements.

It works with any test runner that emits JUnit XML. The bundled renderer is
stdlib-only Python 3.

## Install

From the repository root:

```sh
npx skills@latest add channingwalton/skills
```

Or copy the skill manually to your agent's skill directory.

[`reqreport.py`](./reqreport.py) is bundled with the skill; there is no
separate download. In this repository it is at
`skills/requirements-report/reqreport.py`. After installation it is at
`<agent-skill-directory>/requirements-report/reqreport.py`, beside `SKILL.md`.

## Invoke the skill

Ask the agent to use `requirements-report` whenever requirements or a
specification drive implementation. For example:

> Use requirements-report for this feature. Draft requirements from
> `docs/specification.md`, link them to acceptance tests, wire the report into the build,
> and show me the generated index.

The skill also triggers for living requirements, acceptance criteria tied to
tests, finding untested requirements, and tracing a failed test back to its
requirement.

## Quick start

Mark each requirement with a unique ID in backticks:

```markdown
# Health endpoints

- The service answers `/health` with 200 while running `#health-live`
- The response body is `OK` `#health-body`
```

Include the ID in the corresponding test name (which your AI can do):

```javascript
test("#health-live returns 200 while the service is running", () => {
  // ...
})
```

For identifier-based test names, use `req_`, with underscores in place of
hyphens:

```rust
#[test]
fn req_health_live() {
    // ...
}
```

Configure the test runner to emit JUnit XML, run the tests, then render the
report:

```sh
python3 /path/to/installed/requirements-report/reqreport.py \
  --requirements requirements/ \
  --junit build/test-results/test/ \
  --sources src/test/ \
  --out target/requirements/ \
  --root .
```

Open `target/requirements/index.html`. The report contains one page per
requirements document and preserves its headings, prose, lists, and tables.

Options can instead live in `.reqreport.json`:

```json
{
  "requirements": "requirements",
  "junit": "build/test-results/test",
  "sources": ["src/test"],
  "out": "target/requirements",
  "root": "."
}
```

Run the renderer without arguments to use that file. Use `--no-gate` to write
the report without failing the command.

## Build rules

- Delete old JUnit XML before each run.
- Run tests before the renderer, including when the build task graph is
  parallel.
- Let failed tests continue to report generation so their failures appear in
  the report.
- Use only one test per requirement ID. Split distinct behaviours into distinct
  requirements.
- Leave tests unlinked when they do not clearly demonstrate a requirement.

The renderer exits `0` when clean, `1` for requirement problems, and `2` for
invalid input.

See [`SKILL.md`](./SKILL.md) for the agent workflow,
[`references/conventions.md`](./references/conventions.md) for requirement and
test naming, and
[`references/junit-xml.md`](./references/junit-xml.md) for test-runner setup.
