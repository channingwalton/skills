# mikado

Run the Mikado Method (Ola Ellnestam and Daniel Brolund) with an agent on a
structural change whose dependencies you can't map up front. The agent tries the
goal the naive way, writes each break into a graph of prerequisites, reverts,
and then lands the change leaf-first, one green commit per leaf.

The habit it replaces is **fixing forward**: chasing compile errors and test
failures until the build goes green, ending with one snowballed diff that nobody
can review. In a Mikado experiment a break is information. It goes into the
graph, and the code is reverted.

## When to invoke

- "Use Mikado for this." / "Resume the Mikado graph for X."
- A change in progress has snowballed, and each fix reveals more breaks.
- A structural change crosses module or system boundaries through a dependency
  tangle you can't see in advance: carving out a module, swapping a framework,
  or a major platform upgrade.

For a change inside one module, however many call sites it touches, use your
usual development workflow instead.

## How a run goes

```mermaid
flowchart TD
    start["Start<br/>state the goal, clean tree,<br/>green baseline, branch and graph file"]
    pick["Pick a ready node<br/>goal first, then the deepest<br/>on the branch just worked"]
    exp["Experiment<br/>test first if new behaviour,<br/>make the change naively,<br/>compile and test"]
    red["Revert and record<br/>revert the code, add prerequisites<br/>to the graph, commit the graph"]
    green["Land the leaf<br/>full check,<br/>commit code and graph"]
    finish["Finish<br/>review and fix the branch,<br/>report"]

    start --> pick --> exp
    exp -- "breaks" --> red --> pick
    exp -- "green" --> green
    green -- "full check fails" --> red
    green -- "more nodes" --> pick
    green -- "goal done" --> finish
```

- **Start.** If you did not ask for Mikado, the agent proposes it and waits for
  your yes. The goal is one observable outcome, such as "Orders are priced
  through `PricingEngine`; `LegacyPricer` is deleted". The working tree must be
  clean, because every revert resets to `HEAD`. If you already have a snowballed
  attempt at the goal, it becomes the first experiment: the agent records what
  broke, stashes the attempt so you can recover it, and seeds the graph from it.
  The agent then runs the full check on the clean tree, and stops to ask if it
  is red. Last, it creates a `mikado/<slug>` branch and commits the graph file,
  which records the base.
- **Experiment.** The agent picks a ready node (not done, with every
  prerequisite done) and makes that change directly. For a node that adds
  behaviour, it writes a failing test first. For each break it asks: could this
  be changed first, on its own, leaving the build green? If so, it is a
  prerequisite. If not, it belongs to this node and is fixed within the
  experiment.
- **Revert and record.** The agent reverts the experiment first. Each
  prerequisite becomes a node under the one tried, phrased as a state that must
  hold ("`OrderService` receives `PaymentClient` by injection"), not as a
  symptom ("fix error at OrderService.ts:42"). A log line says what broke and
  where. Only the graph is committed, on a clean tree, so a pre-commit hook
  passes.
- **Land the leaf.** The agent runs the full check. If it passes, the agent
  marks the node done and commits the code and the graph together. If it fails,
  the node is red, and the agent reverts and records.
- **Finish.** Once the goal node is done, the agent reviews the whole branch,
  fixes what the review finds, and reports the final graph, the commits, the
  verification run, any decisions it settled, and any stash it made.

## When it stops to ask

The agent drives the experiments, but two things stop it and send you the
graph:

- **A design decision.** A node has materially different options, such as the
  name of a new concept, the shape of an interface, or how a dependency is
  passed. If you pre-authorised the work ("land this", "don't wait for me"), the
  agent takes the smallest reversible option instead, logs it as a decision, and
  lists it in the report.
- **Scope.** The graph outgrows the goal: prerequisites reach another service,
  a schema, or a contract consumed outside the repo, or the graph grows well
  past what the goal seemed to need. This stops the agent even when the work is
  pre-authorised, because it changes what you agreed to. Every commit so far is
  green, so stopping is safe.

## The graph file

The graph lives in `docs/mikado/<slug>.md` on the branch. It records the base
the branch started from, and holds a Mermaid graph, with edges running from a
node to its prerequisites and done nodes styled, plus a log that records why
each node exists. Each prerequisite label starts with its node ID, so the log
and the commit messages can cite it. A mid-run graph looks like this:

```mermaid
graph TD
  goal["Orders are priced through PricingEngine; LegacyPricer is deleted"]
  goal --> n1["n1 · OrderService receives PricingEngine by injection"]
  goal --> n2["n2 · Invoice takes its total from Order, not LegacyPricer"]
  n1 --> n3["n3 · PricingEngine builds without a database connection"]:::done
  n1 --> n4["n4 · Order carries its priced total"]
  n2 --> n4
  classDef done fill:#cfc,stroke:#393
```

Because the graph is committed, a run can span sessions. Ask the agent to resume
the Mikado graph and it finds the `mikado/` branch, reads the graph and the log,
and carries on. If an interrupted experiment left the tree dirty, the agent
shows you the changed files and asks before it reverts them.

Starting the skill authorises commits on the `mikado/` branch. It never pushes.
The graph file is still on the branch when the run finishes, so drop it before
merging if you don't want it in the history.

## Depends on

No other skills. The graph replaces three parts of your usual development
workflow: the planning step, the approval before each commit, and the review
after each task. The rest of that workflow applies to each leaf, and its code
review runs once, at Finish, whichever skills provide them.

## Install

Via [skills.sh](https://skills.sh) from the repo root:

```sh
npx skills@latest add channingwalton/skills
```

Or manually:

```sh
mkdir -p ~/.codex/skills
cp -R skills/mikado ~/.codex/skills/
```

If you don't use Codex, copy it to your agent's skill directory instead.

See [`SKILL.md`](./SKILL.md) for the full instructions the agent follows.
