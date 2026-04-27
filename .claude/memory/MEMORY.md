# Memory — Hot cache

Date-tagged patterns that have been noticed 2+ times. Loaded on every session start as part of agent context.

**Agent writes this.** If you want to add a note, say it in conversation — the agent captures and writes. Manual edits will be overwritten by `/close-day` dedup pass.

## Why dates matter (load-bearing)

Every entry is `[YYYY-MM-DD]`-prefixed. This is what lets `/close-day` audit work — agent greps for "this pattern across 3+ distinct dates" and proposes promotion to a rule or concept. Without dates, every entry is timestamp-less noise and the audit ritual collapses. **An entry without a date tag is a bug, not a stylistic choice.**

## Format

Every entry is a single line prefixed with `[YYYY-MM-DD]`. Short. Scannable. No headings inside entries.

```
- [2026-04-24] user prefers plain prose for status updates, not dense tables
- [2026-04-24] screenshot discipline: prefer browser_evaluate + browser_snapshot over browser_take_screenshot; reserve screenshots for final aesthetic checks only
- [2026-04-23] for pricing tiers, highlighted plan must use scale-[1.02] + border-2 + badge (conversion +22%)
```

Group loosely by theme with empty lines if the file grows, but don't build a heavy hierarchy — this is a hot cache, not a wiki.

---

## Entries

<!-- Agent appends date-tagged patterns here. When the same pattern gets reinforced 3+ times across different dates, agent surfaces it at `/close-day` as a promotion candidate to a `knowledge/concepts/<topic>.md` article or a `.claude/rules/<name>.md` constraint. -->

(empty — start talking; agent will begin capturing)

---

## What NOT to put here

- Full session transcripts (those live in `daily/YYYY-MM-DD.md`)
- Rationale essays longer than one line (those belong in `knowledge/concepts/*.md`)
- Mechanical always/never constraints (those promote to `.claude/rules/*.md`)
- Project-specific tasks (those live in `projects/<name>/BACKLOG.md`)
- Experiment progress notes (those live in `experiments/<name>-YYYYMMDD/EXPERIMENT.md`)

## Size target

Keep this file short. When it exceeds ~200 lines, agent surfaces candidates for promotion on `/close-day` and prunes entries that have already been absorbed into `knowledge/concepts/` or `.claude/rules/`.
