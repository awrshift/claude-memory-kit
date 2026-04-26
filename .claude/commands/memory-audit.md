---
description: Structural audit for oversized reference skills — size check + semantic clustering + split proposals
---

# /memory-audit

Invoke the `memory-audit` skill. Two-phase operator:

1. **Free size check** — runs `python3 .claude/memory/scripts/lint.py --audit-sizes` to flag `.claude/skills/*-guidance/SKILL.md` over 500 lines (Anthropic's recommended ceiling). No LLM calls.
2. **Semantic clustering** — for each flagged file, the agent reads the content, groups entries by topic, and proposes a split to the user if 2-4 independent clusters exist. Execution happens only on user «да».

Complement to `/close-day` (which audits for promotion) and `/memory-lint` (which audits for link/backlink hygiene).

## When to run

- User feels reference skills are «unweildy»
- Periodically (monthly/quarterly) as background hygiene
- Agent surfaces on `/close-day` if a bloated file was spotted during promotion pass

## What the skill does (summary — full logic in `.claude/skills/memory-audit/SKILL.md`)

- Never splits without verbal confirmation
- Never splits if clusters interleave (defers instead)
- Never splits < 500 lines (noise threshold)
- Never splits `founder-profile` (always consulted, stays monolith)

## Related

- `/memory-lint --audit-sizes` — just the size check, no clustering
- `/close-day` — daily promotion audit (pattern → reference-skill entry)
- `/memory-compile` — daily → knowledge/concepts/
