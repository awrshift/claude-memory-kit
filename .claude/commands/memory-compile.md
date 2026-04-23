---
description: Compile daily/ logs into knowledge/ wiki articles
---

# /memory-compile

Manually trigger compilation of `daily/YYYY-MM-DD.md` logs into structured `knowledge/` wiki articles.

Runs `.claude/memory/scripts/compile.py` as a subprocess. Uses `claude -p` under the hood (subscription, zero incremental cost).

## When to use

- After `/close-day` has written today's `daily/YYYY-MM-DD.md` and you want it folded into the wiki
- When you want to force recompile everything: pass `--all`
- To preview what would be compiled: pass `--dry-run`
- To compile a specific file: pass `--file daily/2026-04-09.md`

## Manual by default

Recommended flow: `/close-day` → this command when you're ready. Deliberate, in-context, high quality.

## Execution

!python3 .claude/memory/scripts/compile.py $ARGUMENTS
