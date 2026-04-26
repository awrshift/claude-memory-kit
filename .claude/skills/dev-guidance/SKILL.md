---
name: dev-guidance
description: Role wisdom for the software engineer — architecture judgment, refactor scope, performance tradeoffs, code-review gotchas (grep audits, framework silent-drops, React/TanStack pitfalls, SSR/crawler discipline). Use for any code task — feature implementation, bug fix, refactor, architecture choice, optimization, or code review.
user-invocable: false
---

# Dev guidance — role wisdom for the software engineer

> **Empty template.** Agent captures patterns during code sessions and proposes additions via `/close-day`. Confirm verbally; agent writes. Never edit manually — talk to the agent.
>
> **Reference skill** (user-invocable: false). Claude auto-loads when conversation matches the description.

## How entries look

### [Pattern name]

[Stated preference in one line]

**Why:** [Past incident or reasoning]

**How to apply:** [When this kicks in]

**Cross-refs:** [other skills, concepts, rules]

---

## Pending observations

_Agent notes candidates here during work. Promoted via `/close-day` after repetition._

---

## Typical entries for this skill

- Framework-specific gotchas (React 19, TanStack, Tailwind v4 silent class drops)
- Refactor scope heuristics (when to bundle, when to split)
- grep-audit patterns that saved us from shipping regressions
- SSR / crawler-compat rules for content pages
- Testing discipline (unit vs integration cost/value)

## Promotion to rule

Stable entries (6+ months) get proposed for `.claude/rules/dev-*.md` with `paths:` scoping to `src/**`. Agent surfaces on `/close-day`.
