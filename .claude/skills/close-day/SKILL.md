---
name: close-day
description: "End-of-day synthesis — scan all documentation changes made today, extract key learnings, decisions, and patterns, produce a daily article in daily/YYYY-MM-DD.md. Use when user says '/close-day', 'close the day', 'end of day', 'wrap up', 'daily summary', or indicates they are done working for the day."
---

# /close-day — End-of-Day Synthesis

Synthesize all documentation changes from today into a single daily article. This replaces auto-flush background processing with a deliberate, high-quality, in-context synthesis.

## When to Use

- User says `/close-day` or "close the day" or "wrap up"
- User indicates they're done working for the day
- Last session of the day, user wants to capture everything

## Flow

### Step 1: Discover today's changes

```bash
# Files modified today
find .claude/memory projects/ context/ knowledge/ -name "*.md" -mtime 0 2>/dev/null

# Uncommitted changes
git diff --name-only

# Today's commits
git log --since="today 00:00" --name-only --format=""
```

### Step 2: Extract changes from each file

| File type | How to extract today's changes |
|-----------|-------------------------------|
| `MEMORY.md` | Grep for today's date tag `[YYYY-MM-DD]` |
| `knowledge/concepts/*.md` | Check `updated:` frontmatter — if today, read for new content |
| `context/next-session-prompt.md` | Read session summaries with today's date |
| `projects/*/BACKLOG.md` | Check git diff for task status changes |
| `.claude/rules/*.md` | Read full file if modified (rules change rarely) |

### Step 3: Synthesize daily article

Create `daily/YYYY-MM-DD.md`:

```markdown
# Daily: YYYY-MM-DD

## Projects Worked On
- **[project]** — [1-2 sentence summary]

## Key Decisions
- [Decision with rationale]

## Patterns Learned
- [New patterns added to MEMORY.md or knowledge/]

## Files Modified
- [Key files changed, grouped by project]

## Tomorrow
- [Pending work, blockers, first action]
```

### Step 4: Report

1. Show user a 3-5 line summary
2. Report file path and size
3. Flag any MEMORY.md entries without today's date tag

## Rules

1. **Synthesis, not extraction.** You have full context — write quality summaries.
2. **One article per day.** If file exists, APPEND new section with timestamp.
3. **Don't duplicate.** Daily = index + narrative. Details stay in source files.
4. **Date tags are the contract.** Every MEMORY.md entry must have `[YYYY-MM-DD]`.
5. **Skip if nothing happened.** Don't create empty articles.
