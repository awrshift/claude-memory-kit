---
name: design-guidance
description: Role wisdom for the designer — aesthetic judgment, warm-vs-cold palette decisions, typography weight tension, interaction-pattern choices, layout tradeoffs. Use whenever making an aesthetic decision, critiquing UI, choosing fonts or colors, evaluating visual quality, reviewing a new page design, or discussing brand voice.
user-invocable: false
---

# Design guidance — role wisdom for the designer

> **This skill starts empty.** As you work, the agent notices patterns during sessions and proposes additions via `/close-day`. You confirm verbally; agent writes entries here. **Never edit this file manually** — talk to the agent instead.
>
> This is a **reference skill** (user-invocable: false). Claude auto-loads it when the conversation matches the description above. It is NOT a task to `/invoke`.

## How entries look (example — remove when first real entry lands)

### Warm palette default for editorial pages

Warm tones (sand, burgundy, sage) read "editorial publication". Cool tones (cobalt, cool grey) read "SaaS product".

**Why:** Past session where cool palette got rejected with "это выглядит как Linear". Warmed palette passed.

**How to apply:** For any new editorial page (blog, about, manifesto), start with warm tones. Cool tones only when target audience is explicitly dev/product (docs, dashboard).

**Cross-refs:** `knowledge/concepts/color-system.md` (if you have one with token details), `.claude/rules/` (if a mechanical version later emerges).

---

## Pending observations

_Agent notes candidates here during work. Promoted to numbered entries via `/close-day` audit after repetition across sessions._

---

## Authorship discipline (agent, not user)

When writing new entries:
- Lead with the rule/preference in one line
- Add **Why:** — the reason (often a past incident or founder preference)
- Add **How to apply:** — when/where this kicks in
- Cite the session if it came from a specific moment
- Never fabricate — if evidence is thin, note «TBD, observe in future sessions»

## When a design entry matures into a rule

After 6+ months of stable application without contradiction AND landmark impact, an entry can be promoted to `.claude/rules/design-*.md` (with `paths:` frontmatter to scope to design files). Agent proposes this on `/close-day`; user confirms verbally.
