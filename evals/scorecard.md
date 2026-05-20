# Scorecard

Score each criterion 0-2:

- `0` missing or wrong.
- `1` present but weak, vague, or mixed with noise.
- `2` clear, specific, and useful.

Prefer the new skill only if it keeps recall while reducing generic output or bad dependencies.

## code-reviewer-review

- Finds the SQL-injection risk from interpolated search text.
- Finds the timezone/date-boundary risk in `active_on?`.
- Finds the missing index risk in the migration.
- Flags missing edge-case tests without invoking `bugmagnet`.
- Avoids generic style nits and focuses on behaviour/risk.
- Critical findings include concrete reproduction or trace.

## software-development-plan

- Does not jump into implementation.
- Asks targeted CLARIFY questions about actor, timing, failure, and definitions.
- Produces or requests a vertical first slice.
- Keeps CLARIFY/CONFIRM stops.
- Avoids generic XP/TDD exposition.

## software-development-refactor

- Preserves behaviour and public API unless a tested behaviour change is explicitly requested.
- Plans one transformation at a time.
- Mentions tests must be green before and after.
- Does not ask after every tiny refactor step.
- Refuses or redirects behaviour-changing cleanup back to DEVELOP.

## fixer-critical-only

- Fixes only Critical findings.
- Leaves Warning/Suggestion items untouched or reports them as not actioned.
- Runs narrow verification before broader tests.
- Reverts or marks unfixable if a fix breaks tests.
- Reports files modified and test status.
- `app/queries/member_search.rb` uses a bound parameter.
- `app/models/member.rb` remains unchanged.

## chatter-start

- Creates a new thread rather than asking the user to invite others first.
- Uses local timestamp slug format.
- Uses the helper script instead of hand-written files.
- Includes exactly: `Instruction for other agents: join chatter <slug>`.
- Enters or describes the wait loop after the opener.
- Uses safe content handling for shell metacharacters.
