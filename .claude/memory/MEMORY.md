# Project Memory
Last updated: [DATE] (Session: #1)
Architecture: Index (< 200 lines, auto-loaded) + topic files (on-demand)

---

## Verified Patterns

> Add patterns here as you confirm them across multiple sessions.
> Keep this section SHORT — one line per pattern. Details go in topic files.
>
> Format: **Pattern name** — description. [Source: session/decision]

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

## Topic Files (read on-demand)

> As your project grows, move detailed knowledge into topic files.
> MEMORY.md stays under 200 lines. Topics have no size limit.
> Claude reads topic files when working on that area — not every session.

| Topic | File | When to read |
|-------|------|-------------|
| [Example: API patterns] | `.claude/memory/topics/api.md` | Working on API endpoints |
| [Example: Database] | `.claude/memory/topics/database.md` | Schema changes, queries |
| [Example: Deployment] | `.claude/memory/topics/deployment.md` | CI/CD, hosting, env config |

> **How to create a topic file:**
> 1. When a section above grows beyond 5-10 entries on the same theme
> 2. Create `.claude/memory/topics/{topic-name}.md`
> 3. Move detailed entries there, keep one-line summary here
> 4. Add to the table above
