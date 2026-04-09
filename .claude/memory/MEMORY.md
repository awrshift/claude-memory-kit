# Project Memory
Last updated: [DATE] (Session: #1)
Architecture: Hot cache (< 200 lines, auto-loaded) + knowledge wiki (on-demand)

---

## Verified Patterns

> One line per pattern. Every entry MUST have a date tag [YYYY-MM].
> Format: **Pattern name** [YYYY-MM] — description
> Superseded: ~~**Old pattern** [YYYY-MM → YYYY-MM]~~ — reason

## User Preferences

> Workflow preferences, communication style, tool choices confirmed by the user.

## Architecture Decisions

> Key technical decisions that affect future work.

## Lessons Learned

| Pattern | Evidence | Confidence |
|---------|----------|------------|
| [Example: "Always run tests before commit"] | [Where you learned this] | VERIFIED / PROBABLE |

## Failed Approaches

| Approach | Why Failed | Lesson |
|----------|-----------|--------|
| [Example: "Used raw SQL"] | [SQL injection in user input] | [Always use parameterized queries] |

## Knowledge Wiki (read on-demand + injected at session start)

> Deep knowledge lives in `.claude/memory/knowledge/`, not here.
> MEMORY.md stays under 200 lines (Anthropic auto-load cap).
> The wiki `index.md` is injected automatically into every session via `session-start.py` (v3 additionalContext pattern). Individual articles are read on-demand when relevant.

**Wiki entry point:** `.claude/memory/knowledge/index.md`

**Subdirectories (v3 — 3 only):**
- `concepts/` — single-topic deep dives
- `connections/` — cross-concept relationships
- `meetings/` — structured meeting index articles

> **How to grow the wiki:**
> 1. When a theme in MEMORY.md grows beyond 5-10 entries on the same topic, move details to `.claude/memory/knowledge/concepts/{slug}.md`
> 2. Keep a one-line summary here with a pointer: `- **Theme name** [YYYY-MM] — see `knowledge/concepts/{slug}`
> 3. Or let the session-end hook + `compile.py` do it automatically from `daily/` logs
