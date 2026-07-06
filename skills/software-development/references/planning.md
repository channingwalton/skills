# Planning

## ❓ CLARIFY — Surface Hidden Premises

**Find the missing premises** — restate the requirement as "Given [premises], then [conclusion]" and ask what's been left unsaid:

- **Who** — which actor triggers this, and do different actors expect different things?
- **When** — at what point in the process? What state must already exist?
- **Boundaries** — what counts as valid input? Smallest/largest/emptiest case? For values that span a range (dates, versions, numeric intervals), what decides membership — start, end, full containment, or overlap?
- **Failure** — what happens when this *can't* work? Who finds out and how?
- **Definitions** — are we using the same words to mean the same things? Record any agreed term definitions where the project keeps them.
- **User-facing strings** — does this change error messages, UI copy, or notifications? Who reads them (operator, end-user, ops triage)? Does the change preserve diagnostic value?

**Context-specific premises** — check the ones that apply:

- **UI change** — pin the exact dialog/page by *role* (which user) and *app/bundle* before picking a component. A component name that matches the feature in two apps is a trap, not an answer; ask for a screenshot or navigation path.
- **No existing test seam** — adding a test dependency or an injection seam (an interface, a function parameter) is a scope decision the user owns. Name the options; don't silently defer.
- **Generated artefacts / codegen** — pin which command regenerates which file and whether it needs a live upstream service running. Regenerate by default; hand-edit generated output only when repo docs or user approval make that explicit.
- **Presenting the questions** — define any issue-specific term inside the question itself; don't assume the user shares the ticket's framing. For an unfamiliar design space, ask one decision at a time and expect questions back; a batched multiple-choice form suits settled trade-offs, not exploration.

## ✂️ SLICE — Break Into Tasks

Slice by visible behaviour, not implementation layer.

## 🧪 FALSIFY — Test Your Understanding

1. **State what you believe** — "We understand the feature to mean X"
2. **Seek disconfirmation** — "What scenario would prove this wrong?"
3. **Check for gaps** — "Is there a case this plan doesn't handle?"
4. **Check ordering** — "Does any task depend on something unplanned?"

**Discharge each falsifier with the cheapest evidence that can settle it:**

- **Fact about the current system** ("validation only runs client-side") → read the code, run it, or query the data — never ask the user what the repo can answer.
- **Fact about intent** ("does 'within the range' mean overlap or containment?") → ask the user; loop back to CLARIFY with a specific question.
- **Prediction about behaviour** ("the importer already trims whitespace") → execute something: the existing suite, a REPL snippet, a characterisation test. A prediction about *new* behaviour is not discharged at plan time — it becomes the first red test in DEVELOP.

If you can't think of anything that would prove your understanding wrong, that's a warning sign — not a green light.
