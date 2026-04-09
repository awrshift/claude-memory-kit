---
description: Compile daily/ logs into knowledge/ wiki articles
---

# /memory-compile

Manually trigger compilation of `daily/YYYY-MM-DD.md` logs into structured `knowledge/` wiki articles.

Runs `.claude/memory/scripts/compile.py` as a subprocess. Uses `claude -p` under the hood (subscription, zero incremental cost).

## When to use

- After an important session, before end-of-day auto-trigger fires
- When you want to force recompile everything: pass `--all`
- To preview what would be compiled: pass `--dry-run`
- To compile a specific file: pass `--file daily/2026-04-09.md`

## Auto-compile vs manual

By default, `flush.py` auto-triggers compile after 18:00 local time (end-of-day) if today's daily log has changed since its last compile. This slash command is the manual override for explicit control.

Configurable via `CMK_COMPILE_AFTER_HOUR` env var.

## Execution

!python3 .claude/memory/scripts/compile.py $ARGUMENTS
