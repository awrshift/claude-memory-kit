# Knowledge Index

> Master catalog — read this FIRST for any deep query.
> Populated automatically by `python .claude/memory/scripts/compile.py` from `daily/` logs.

## Projects

_(empty — compile.py will populate this table as projects accumulate)_

## Concepts

_(empty — single-topic deep-dive articles)_

## Connections

_(empty — cross-concept relationship articles)_

## Experiments

_(empty — gravestone pattern: wiki article stays even after raw files archived)_

## Meetings

_(empty — structured index articles of meeting transcripts)_

## Q&A

_(empty — filed query answers via `query.py --file-back`, the compounding loop)_

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
