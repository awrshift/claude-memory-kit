---
description: Run 7 structural health checks on the knowledge base + reference skills
---

# /memory-lint

Run 7 structural health checks (all free, no LLM calls):

1. **Broken links** — `[[wikilinks]]` pointing to non-existent articles
2. **Orphan pages** — Articles with zero inbound links
3. **Orphan sources** — Daily logs that haven't been compiled yet
4. **Missing backlinks** — A links to B but B doesn't link back
5. **Sparse articles** — Under 150 words
6. **Missing frontmatter** — Articles without YAML frontmatter
7. **Oversized reference skills** (new v4) — `.claude/skills/*-guidance/SKILL.md` over 500 lines (Anthropic's recommended SKILL.md ceiling). Flagged as candidates for split; use `/memory-audit` for agent-in-session clustering + actual split execution.

## Flags

- `--fix` — auto-add missing backlinks
- `--audit-sizes` — only run the oversized-reference-skill check (fast pre-step before `/memory-audit`)

## Execution

!python3 .claude/memory/scripts/lint.py $ARGUMENTS

## Related

- `/memory-audit` — semantic clustering + actual split execution for oversized reference skills
- `/memory-compile` — daily → knowledge/concepts/
- `/memory-query` — natural-language search across memory
