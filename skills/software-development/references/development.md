# Development

## Rules Worth Loading

Any failing test blocks — do not proceed.

**New behaviour requires a new test, even when similar existing code lacks one.** Precedent is not permission. Missing twin coverage is a gap to note, not a licence to skip.

**When mirroring a precedent, test what makes this not the precedent.** Copying a sibling's tests proves the shape matches, not the contract. Ask "what is the one case where this differs from what I'm copying?" — write that.

**Public signature changes require eyeballing every caller.** Compile-passing is weak evidence. Some languages coerce between function types — Kotlin accepts `() -> X` where `() -> Unit` is expected (return value dropped); TypeScript's structural typing accepts fewer parameters than the target signature declares — so stale callers stay stale and compile + tests both stay green. After any change to a public function's name, parameter list, or return type: `grep` the old shape, open each hit, confirm the new contract holds at every call site.

**Check the test script before running tests in a non-interactive or background context.** JS monorepos frequently alias `test` → watch mode (`jest --watch`, `vitest`). A test runner with no stdout after 30s is almost always watch mode, not a slow build. Prefer `test:run` / `test:ci`; if pnpm's `--` arg forwarding drops flags, invoke the runner binary directly (e.g. `../../node_modules/.bin/jest <args>` from a package dir).

**Probe local services before invoking tools that depend on them.** Codegen hitting a GraphQL endpoint, migrations hitting a DB, auth flows hitting Keycloak — a one-line port check (`lsof -iTCP:<port> -sTCP:LISTEN`) beats an `ECONNREFUSED` round-trip. Cached schema / fixture files often make the live service optional; prefer those if they exist.

## Red Flags

- "I'll mirror the existing X exactly" — mirroring copies shape, not contract. Find the case where this isn't X, and test that.
