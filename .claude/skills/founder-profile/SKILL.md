---
name: founder-profile
description: Reference profile of the founder — observed preferences, red lines, decision style, signals to watch, taste markers. Consulted on every non-trivial decision regardless of role. Use on any design, marketing, copy, feature, architecture, pricing, or launch decision where founder taste matters.
user-invocable: false
---

# Founder profile — always consulted

> **The most important reference skill in this kit.** Captures how the founder/user thinks, what they prefer, what their red lines are. Claude auto-loads this on every non-trivial decision regardless of role — the description is broad on purpose.
>
> **Empty template.** Agent captures via conversation + `/close-day` audit. Never edit manually — talk to the agent.
>
> **Reference skill** (user-invocable: false).

## Structure

### Observed preferences

Patterns from conversation the agent has noticed and confirmed with you at `/close-day`:

_Examples of what might land here: "prefers warm over cold aesthetics", "rejects copy with «seamlessly»", "avoids over-engineering", "wants explicit tradeoff analysis before non-trivial changes"._

### Red lines (things never to do)

Hard constraints. If the agent is considering an approach that crosses one of these, it stops and asks.

_Examples: "never edit user's files without explicit confirmation", "never hand-wave a complex tradeoff — always name it", "never push to a shared upstream without per-PR verbal approval"._

### Decision style

How you make calls when there's ambiguity.

_Examples: "prefers one bundled PR over many small", "pushes back on premature abstraction", "ships fast on marketing pages, slow on product pages"._

### Signals to watch

Early indicators that you're about to reject something. Agent monitors conversation for these.

_Examples: "when user says «не тот вайб» — agent has usually chosen a cool/generic aesthetic", "when user says «это AI-slop» — copy has em-dashes or rule-of-three padding"._

---

## Pending observations

_Agent captures candidates here during sessions. Promoted via `/close-day`._

---

## Why this skill is special

Other reference skills load on role-matching triggers. This one loads on a much broader trigger (any non-trivial decision) because founder taste is cross-cutting. The description is deliberately broad so Claude keeps it in context whenever stakes are meaningful.

Promotion: entries here don't promote to rules the same way. A red line might eventually become a `.claude/rules/*.md` entry with hard enforcement, but observed preferences stay here indefinitely as judgment signals.
