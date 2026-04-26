---
name: marketing-guidance
description: Role wisdom for the marketer — positioning one-liners, messaging pillars, audience-specific angles, competitive positioning, channel patterns, pitch construction. Use for positioning discussions, pitch decks, launches, campaign work, competitive analysis, or ICP-related decisions.
user-invocable: false
---

# Marketing guidance — role wisdom for the marketer

> **Empty template.** Agent captures via `/close-day`. Never edit manually.
>
> **Reference skill** (user-invocable: false). Auto-loads for marketing/positioning conversations.

## Typical entries

- Positioning one-liners (ICP + differentiator, tested against founder)
- Messaging pillars (3-5 core claims, ranked by salience to target segment)
- Audience-specific angles (same product, different framing per ICP segment)
- Competitive positioning notes (who we're against, how we differ, why that matters)
- Channel patterns (what works where — LinkedIn vs Twitter vs newsletter vs outbound)

## Pending observations

_Agent captures during marketing/pitch/copy sessions. Promoted via `/close-day`._

---

## Related layers

- `knowledge/concepts/` for factual reference (market data, competitor profiles, pricing benchmarks)
- `.claude/skills/founder-profile/` for founder's taste on marketing voice (always-on)
- If your project needs deep ICP or competitor profiles, consider spawning `.claude/skills/icp-<segment>/` or `.claude/skills/competitor-<name>/` as separate reference skills

## Promotion

Marketing wisdom rarely becomes a mechanical rule — it stays as judgment. But specific mechanical constraints (e.g., "every pitch deck must state pricing on slide 8") can promote to `.claude/rules/marketing-*.md`.
