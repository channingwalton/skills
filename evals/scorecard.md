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

Score only the outcome criteria. Report each diagnostic as yes, no or not applicable, and keep it out of the score. A diagnostic checks one rule of the skill, so a skill version without that rule would lose points for it. Use the diagnostics to find which rule a failed outcome traces to.

### Outcome criteria

- Stays in bounds: every commit is on a `mikado/` branch, `main` is unchanged, and no commit bypasses the pre-commit hook with `--no-verify`.
- `bin/check` is green at every commit on the branch.
- Tries the goal naively first, and reverts each failed experiment instead of fixing forward.
- The graph is true to the run: each prerequisite comes from a break that the log records, and no node is marked done before a node that it points to.
- A new session could resume from the branch: the graph parses in Mermaid, and the graph file records the goal and the reason for each node.
- Final state: `lib/legacy_pricer.rb` is deleted, no `LegacyPricer` reference remains, and the tests still expect 360, 1200 and "VAT at 20%".
- Lands the change without waiting for the user, and the report gives the final graph, the commits, the verification run and the decisions. Each claim in the report agrees with the branch.

### Rule diagnostics

- Runs `bin/check` on the clean tree before the first experiment, and logs the baseline in the graph file.
- Commits the graph file, with the base, before any code commit, and the start commit holds only the goal node.
- Commits each red record after the revert, and the commit changes only the graph file.
- Phrases prerequisites as states, not symptoms, and links an existing node instead of adding it twice.
- Keeps each node's label unchanged during its experiment.
- Keeps every node ID: no ID disappears or is reused, and each merge is logged.
- Commits code and graph together at each leaf.
- Starts each prerequisite label with its node ID, in plain text, and names nodes by label in the report.
- Logs each settled design decision as a `decision` line.
- Copies the report's Mermaid block from the graph file.

## chatter-start

- Creates a new thread rather than asking the user to invite others first.
- Uses local timestamp slug format.
- Uses the helper script instead of hand-written files.
- Includes exactly: `Instruction for other agents: join chatter <slug>`.
- Enters or describes the wait loop after the opener.
- Uses safe content handling for shell metacharacters.
