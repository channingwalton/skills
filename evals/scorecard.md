# Scorecard

Score each criterion 0-2:

- `0` missing or wrong.
- `1` present but weak, vague, or mixed with noise.
- `2` clear, specific, and useful.

Prefer the new skill only if it keeps recall while reducing generic output or bad dependencies.

## software-development-plan

- Does not jump into implementation.
- Asks targeted CLARIFY questions about actor, timing, failure, and definitions.
- Surfaces the context-specific premises this feature actually raises — which page/role sees the banner, and how the expiry window decides which tokens qualify (measured from now, boundary inclusive/exclusive) — rather than assuming them.
- Produces or requests a vertical first slice.
- Keeps CLARIFY/CONFIRM stops.
- Avoids generic XP/TDD exposition.

## software-development-refactor

- Preserves behaviour and public API unless a tested behaviour change is explicitly requested.
- Plans one transformation at a time.
- Mentions tests must be green before and after.
- Does not ask after every tiny refactor step.
- Refuses or redirects behaviour-changing cleanup back to DEVELOP.

## fix-loop-critical-only

- Fixes only Critical findings.
- Leaves Warning/Suggestion items untouched or reports them as not actioned.
- Runs narrow verification before broader tests.
- Reverts or marks unfixable if a fix breaks tests.
- Reports files modified and test status.
- `app/queries/member_search.rb` uses a bound parameter.
- `app/models/member.rb` remains unchanged.

## mikado-pricing

- Runs `bin/check` on the clean tree before the first experiment, and logs the baseline in the graph file.
- Creates a `mikado/` branch and commits the graph file, with the base recorded, before any code commit.
- Tries the goal naively first, then reverts instead of fixing forward.
- Every red commit changes only the graph file, and passes the pre-commit hook without `--no-verify`.
- Phrases prerequisites as states, not symptoms, and links a shared prerequisite instead of adding it twice.
- Adds prerequisites only from breaks in experiments: the start commit holds only the goal node.
- Keeps each node's label unchanged during its experiment; a break that passes the prerequisite test becomes a new node.
- Draws edges from a node to its prerequisites: no node is marked done while a node it points to is not done.
- Keeps every node ID: no ID disappears or is reused, and each merge is logged.
- Every leaf commit changes code and graph together, and `bin/check` is green at every commit on the branch.
- Each prerequisite label starts with its node ID and is plain text, the graph parses in Mermaid, and the report names nodes by label.
- Settles design decisions without stopping, and logs each one as a `decision` line.
- Final state: `lib/legacy_pricer.rb` is deleted, no `LegacyPricer` reference remains, and the tests still expect 360, 1200 and "VAT at 20%".
- Reports the final graph, the commits, the verification run and the decisions. The report's Mermaid block is the same as the block in the graph file.

## chatter-start

- Creates a new thread rather than asking the user to invite others first.
- Uses local timestamp slug format.
- Uses the helper script instead of hand-written files.
- Includes exactly: `Instruction for other agents: join chatter <slug>`.
- Enters or describes the wait loop after the opener.
- Uses safe content handling for shell metacharacters.
