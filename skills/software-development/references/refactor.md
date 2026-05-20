# Refactor

## Guardrails

- Refactoring preserves behaviour.
- Tests must be green before and after.
- Apply one transformation at a time.
- If the change alters behaviour or public API, return to DEVELOP and write a test first.
- State the test status; if tests were not run, say so.

## Code Smells to Watch For

Duplication, long methods, large classes, long parameter lists, feature envy, primitive obsession.

## Safety Checklist

Before: tests pass and you understand the code. After each change: tests still pass, behaviour is unchanged, and code is clearer rather than just different.
