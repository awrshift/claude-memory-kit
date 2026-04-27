---
description: Run 6 structural health checks on the knowledge base
---

# /memory-lint

Run 6 structural health checks (all free, no LLM calls):

1. **Broken links** — `[[wikilinks]]` pointing to non-existent articles
2. **Orphan pages** — Articles with zero inbound links
3. **Orphan sources** — Daily logs that haven't been compiled yet
4. **Missing backlinks** — A links to B but B doesn't link back
5. **Sparse articles** — Under 150 words
6. **Missing frontmatter** — Articles without YAML frontmatter

## Flags

- `--fix` — auto-add missing backlinks

## Execution

!python3 .claude/memory/scripts/lint.py $ARGUMENTS

## Related

- `/memory-compile` — daily → knowledge/concepts/
- `/memory-query` — natural-language search across memory
