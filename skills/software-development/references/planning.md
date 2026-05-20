# Planning

## ❓ CLARIFY — Surface Hidden Premises

**Find the missing premises** — restate the requirement as "Given [premises], then [conclusion]" and ask what's been left unsaid:

- **Who** — which actor triggers this, and do different actors expect different things?
- **When** — at what point in the process? What state must already exist?
- **Boundaries** — what counts as valid input? Smallest/largest/emptiest case?
- **Failure** — what happens when this *can't* work? Who finds out and how?
- **Definitions** — are we using the same words to mean the same things? (→ `glossary` skill)
- **User-facing strings** — does this change error messages, UI copy, or notifications? Who reads them (operator, end-user, ops triage)? Does the change preserve diagnostic value?

## ✂️ SLICE — Break Into Tasks

Slice by visible behaviour, not implementation layer.

## 🧪 FALSIFY — Test Your Understanding

1. **State what you believe** — "We understand the feature to mean X"
2. **Seek disconfirmation** — "What scenario would prove this wrong?"
3. **Check for gaps** — "Is there a case this plan doesn't handle?"
4. **Check ordering** — "Does any task depend on something unplanned?"

If you can't think of anything that would prove your understanding wrong, that's a warning sign — not a green light.
