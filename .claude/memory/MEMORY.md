# Project Memory
Last updated: [DATE] (Session: #1)
Architecture: Hot cache (< 200 lines, auto-loaded) + knowledge wiki (on-demand)

---

## Verified Patterns

> One line per pattern. Every entry MUST have a date tag [YYYY-MM-DD].
> Format: **Pattern name** [YYYY-MM-DD] — description
> Superseded: ~~**Old pattern** [YYYY-MM-DD → YYYY-MM-DD]~~ — reason
> Day-granularity is required for `/close-day` synthesis (v3.2.0).

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

> Deep knowledge lives in `knowledge/` at the project root (moved out of `.claude/` in v3.1.0 — see CHANGELOG).
> MEMORY.md targets ~200 lines — SSOT discipline over hard count (see Rotation Rule in CLAUDE.md).
> The wiki `index.md` is injected automatically into every session via `session-start.py` (v3 additionalContext pattern). Individual articles are read on-demand when relevant.

**Wiki entry point:** `knowledge/index.md`

**Subdirectories (v3 — 3 only):**
- `concepts/` — single-topic deep dives
- `connections/` — cross-concept relationships
- `meetings/` — structured meeting index articles

> **How to grow the wiki:**
> 1. When a theme in MEMORY.md grows beyond 5-10 entries on the same topic, move details to `knowledge/concepts/{slug}.md`
> 2. Keep a one-line summary here with a pointer: `- **Theme name** [YYYY-MM-DD] — see `knowledge/concepts/{slug}`
> 3. At end-of-day, run `/close-day` to synthesize today's changes into `daily/YYYY-MM-DD.md`, then `/memory-compile` when ready to fold daily logs into wiki articles
