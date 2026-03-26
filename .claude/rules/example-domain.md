---
paths:
  - "projects/my-first-project/**/*"
---

# Example Domain Rules

> This file auto-loads when working on files matching the `paths` pattern above.
> Delete this file and create your own rules for your project's domains.

## How to write rules

Rules are behavioral instructions that change how the agent works. Good rules:

1. **Are stable** — they don't change every session (use JOURNAL for volatile data)
2. **Are scoped** — the `paths:` frontmatter controls when they load
3. **Are actionable** — each rule changes agent behavior

## Examples of good rules

```markdown
# Database Rules

- Always use parameterized queries, never string interpolation
- Connection string: postgres://localhost:5432/mydb
- After schema changes, run migrations: `npm run db:migrate`
```

```markdown
# API Rules

- Base URL: https://api.example.com/v2
- Auth: Bearer token from `$API_TOKEN` env var
- Rate limit: 100 req/min — add 600ms delay between batch calls
```

## Examples of bad rules (put these elsewhere)

- "We have 1,234 users" → volatile data, goes in JOURNAL
- "Yesterday we fixed bug X" → session context, goes in next-session-prompt
- "The codebase has 50 files" → changes constantly, not a rule
