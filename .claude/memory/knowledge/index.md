# Knowledge Index

> Master catalog — read this FIRST for any deep query.
> Populated automatically by `python .claude/memory/scripts/compile.py` from `daily/` logs.
> Also injected into every Claude Code session via the SessionStart hook (`additionalContext`).

## Concepts

_(empty — single-topic deep-dive articles)_

## Connections

_(empty — cross-concept relationship articles)_

## Meetings

_(empty — structured index articles of meeting transcripts)_

---

## Article Format

All articles use YAML frontmatter + wikilinks:

```markdown
---
title: "Topic Name"
tags: [tag1, tag2]
project: project-name-or-global
sources:
  - "daily/YYYY-MM-DD.md"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Topic Name

## Key Points
- Bullet summary

## Details
Prose explanation.

## Related Concepts
- [[concepts/other-topic]] — how they connect

## Sources
- [[daily/YYYY-MM-DD]]
```

Wikilinks use `[[subdir/slug]]` format (no `.md` extension — Obsidian-compatible, works in any markdown editor).

## Wiki Structure

Memory Kit v3 uses 3 subdirectories (collapsed from 6 in v2):

| Subdir | Purpose |
|---|---|
| `concepts/` | Single-topic deep-dive articles — one concept per file |
| `connections/` | Cross-concept synthesis — links 2+ concepts |
| `meetings/` | Structured meeting index articles |

Previous subdirs (`qa/`, `projects/`, `experiments/`) were removed in v3. Rationale:
- `qa/` was empty in practice (compounding loop rarely fired manually)
- `projects/` duplicated root-level `projects/X/BACKLOG.md`
- `experiments/` duplicated root-level `experiments/NNN/EXPERIMENT.md`
