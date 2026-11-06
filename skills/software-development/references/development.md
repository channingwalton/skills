# Development

**Precedent is not permission.** New behaviour needs a new test even when similar existing code has none; note the missing twin coverage as a gap. When you mirror a precedent, test the one case where this code differs from it: copied tests prove that the shape matches, not the contract.

**After a public signature change, check every caller by hand.** Some languages coerce between function types — Kotlin accepts `() -> X` where `() -> Unit` is expected (return value dropped); TypeScript's structural typing accepts fewer parameters than the target signature declares — so stale callers stay stale while compile and tests both stay green. `grep` the old shape, open each hit, and confirm the new contract holds at every call site.

**Check the test script before running tests in a non-interactive or background context.** JS monorepos frequently alias `test` → watch mode (`jest --watch`, `vitest`). A test runner with no stdout after 30s is almost always watch mode, not a slow build. Prefer `test:run` / `test:ci`; if pnpm's `--` arg forwarding drops flags, invoke the runner binary directly (e.g. `../../node_modules/.bin/jest <args>` from a package dir).

**Probe local services before invoking tools that depend on them.** Codegen hitting a GraphQL endpoint, migrations hitting a DB, auth flows hitting Keycloak — a one-line port check (`lsof -iTCP:<port> -sTCP:LISTEN`) beats an `ECONNREFUSED` round-trip. Cached schema / fixture files often make the live service optional; prefer those if they exist.

**Manage the clock in tests that use dates** (e.g. `travel_to(...)` in Ruby); a hardcoded date starts failing when it passes.
