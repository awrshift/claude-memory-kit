---
description: Run 6 structural health checks on the knowledge base
---

# /memory-lint

Run 6 structural health checks on `.claude/memory/knowledge/`:

1. **Broken links** — `[[wikilinks]]` pointing to non-existent articles
2. **Orphan pages** — Articles with zero inbound links (not even from index.md)
3. **Orphan sources** — Daily logs that haven't been compiled yet
4. **Missing backlinks** — A links to B but B doesn't link back
5. **Sparse articles** — Under 150 words
6. **Missing frontmatter** — Articles without YAML frontmatter

All checks are free (no LLM calls).

## Auto-fix

Pass `--fix` to auto-add missing backlinks. Other issues require manual review.

## Execution

!python3 .claude/memory/scripts/lint.py $ARGUMENTS
