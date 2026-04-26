# daily/

Chronological session logs, one file per working day: `daily/YYYY-MM-DD.md`.

**The agent writes these, not you.** They are the output of `/close-day` — the end-of-day audit ritual where the agent synthesizes what was said into a structured log and proposes promotions (pattern → `.claude/skills/<role>-guidance/SKILL.md`).

Do not edit files here manually. If you want to add context or correct a log, say so in conversation — the agent will revise. Manual edits break the `/close-day` dedup check and the «user only talks» invariant.

These logs are searchable via `/memory-query` and compiled into topical articles in `knowledge/concepts/` via `/memory-compile`.
