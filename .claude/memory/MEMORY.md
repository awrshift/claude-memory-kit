# Memory — Hot cache

Date-tagged patterns that have been noticed 2+ times. Loaded on every session start as part of agent context.

**Agent writes this.** If you want to add a note, say it in conversation — the agent captures and writes. Manual edits will be overwritten by `/close-day` dedup pass.

---

## Format

Every entry is a single line prefixed with `[YYYY-MM-DD]` date tag. Short. Scannable. No headings inside entries.

```
- [2026-04-24] user prefers plain prose for status updates, not dense tables
- [2026-04-24] screenshot discipline: prefer browser_evaluate + browser_snapshot over browser_take_screenshot; reserve screenshots for final aesthetic checks only
- [2026-04-23] for pricing tiers, highlighted plan must use scale-[1.02] + border-2 + badge (conversion +22%)
```

Group loosely by theme with empty lines if the file grows, but don't build a heavy hierarchy — this is a hot cache, not a wiki.

---

## Entries

<!-- Agent appends date-tagged patterns here. When the same pattern gets reinforced 3+ times across different sessions, agent surfaces it at `/close-day` as a promotion candidate to a `knowledge/concepts/<topic>.md` article or a `.claude/rules/<name>.md` constraint. -->

(empty — start talking; agent will begin capturing)

---

## What NOT to put here

- Full session transcripts (those live in `daily/YYYY-MM-DD.md`)
- Rationale essays longer than one line (those belong in `knowledge/concepts/*.md`)
- Mechanical always/never constraints (those promote to `.claude/rules/*.md`)
- Project-specific tasks (those live in `projects/<name>/BACKLOG.md`)

## Size target

Keep this file short. When it exceeds ~200 lines, agent surfaces candidates for promotion on `/close-day` and prunes entries that have already been absorbed into `knowledge/concepts/` or `.claude/rules/`.
