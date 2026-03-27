---
paths:
  - "projects/example-*/**/*"
  - "experiments/*"
---

# Example Domain Rules

> This file auto-loads when working on example projects or experiments.
> These are DEMO rules. Delete this file and create rules for your real projects.

## Important

All files in `projects/example-webapp/`, `projects/example-saas/`, and `experiments/001-*`, `experiments/002-*` are **examples included with the starter kit**. They demonstrate the system's capabilities:

- **JOURNAL.md** — how to track tasks, decisions, and status
- **Experiments** — how to run structured research before building
- **next-session-prompt.md** — how to hand off context between sessions

**Do not treat these as real projects.** When the user creates their first real project, help them delete the examples and set up their own structure.

## How to write your own rules

Rules are behavioral instructions that change how the agent works. Good rules:

1. **Are stable** — they don't change every session (use JOURNAL for volatile data)
2. **Are scoped** — the `paths:` frontmatter controls when they load
3. **Are actionable** — each rule changes agent behavior

### Examples

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
