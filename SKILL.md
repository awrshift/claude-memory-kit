---
name: claude-memory-kit
description: "Persistent memory for Claude Code agents with an agent-audit-ritual architecture. User only talks; agent captures, audits, proposes promotions, and writes. Four layers — daily logs, hot cache (MEMORY.md), role-based reference skills (Anthropic-native, user-invocable: false), canonical rules. /close-day runs the audit ritual at end of day. Multi-project isolation via projects/<name>/. Zero external dependencies."
tags: [memory, context-management, productivity, claude-code, agent-memory, knowledge-base, reference-skills, multi-project]
version: 4.0.0
author: awrshift
license: MIT
repository: https://github.com/awrshift/claude-memory-kit
---

# Claude Memory Kit v4

Persistent memory for Claude Code agents. Four-layer architecture, agent-driven promotion, zero manual file editing.

## Core invariant

**User only talks. Agent captures, proposes, writes.** Every architectural decision passes this test.

## What's different from v3.2

- **Agent-driven promotion ritual** via `/close-day` (was: background `promote-patterns.py` detection, killed as unreliable)
- **Role-based reference skills** (`.claude/skills/<role>-guidance/SKILL.md` with `user-invocable: false`) alongside topic-based `knowledge/concepts/` — two axes, no overlap. Uses Anthropic-native auto-invoke via `description` matching — no custom trigger tables.
- **Multi-project isolation** via `projects/<name>/` — shared layers load always, per-project scope on demand
- **`/memory-audit`** operator for oversized-reference-skill detection + semantic split execution
- **Killed:** `experiences/` staging layer, `promote-patterns.py` background script, `flush.py` auto-flush, separate `playbooks/` directory (merged into reference skills)

See [CHANGELOG.md](CHANGELOG.md) for full migration notes.

## Quick start

```bash
git clone https://github.com/awrshift/claude-memory-kit-v4.git my-project
cd my-project
claude
```

First session: agent greets you, asks 2-3 setup questions, loads you in. Type `/tour` for a guided walkthrough.

## Daily workflow

1. Open a session — hooks auto-load NSP + MEMORY + knowledge index
2. Work normally — agent captures patterns in MEMORY.md as you speak
3. `/close-day` when done — agent synthesizes today, audits for promotions, proposes verbally, writes on your «да»

Tomorrow starts where today left off.

## Included skills

| Skill | Description |
|---|---|
| `/close-day` | End-of-day audit ritual: synthesis + promotion proposals |
| `/memory-audit` | Oversized-reference-skill structural check + split proposals |
| `/memory-lint` | Hygiene (broken links, sparse articles, orphans, oversized reference skills) |
| `/memory-compile` | Compile daily logs into `knowledge/concepts/` articles |
| `/memory-query` | Natural-language search across all memory layers |
| `/tour` | Interactive guided walkthrough |

## Architecture

Four layers, each with its own purpose:

| Layer | Answers | Written by |
|---|---|---|
| `daily/YYYY-MM-DD.md` | «what happened today» | `/close-day` |
| `.claude/memory/MEMORY.md` | «what patterns repeat across sessions» | agent as you speak |
| `.claude/skills/<role>-guidance/SKILL.md` | «how should a <role> think about X» | `/close-day` promotion |
| `.claude/rules/*.md` | «what must always / never happen» | `/close-day` after 6+ months stable |

See [ARCHITECTURE.md](ARCHITECTURE.md) for full details and [CLAUDE.md](CLAUDE.md) for the agent's session workflow.

## Built from production use

Iteration on 700+ real sessions across 7+ projects. Every component earns its place; `experiences/` and background-detection scripts didn't survive review.
