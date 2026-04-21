---
name: claude-memory-kit
description: "Persistent memory system for Claude Code. Your agent remembers everything across sessions and projects. Two-layer architecture: hot cache (MEMORY.md) + knowledge wiki. Safety hooks prevent context loss. /close-day captures your day in one command. Zero external dependencies, runs on existing subscription."
tags: [memory, context-management, productivity, claude-code, agent-memory, knowledge-base]
version: 3.2.1
author: awrshift
license: MIT
repository: https://github.com/awrshift/claude-memory-kit
---

# Claude Memory Kit

Persistent memory system for Claude Code agents. Clone, start, and your agent remembers everything across sessions.

## What it does

- **Persistent memory** across sessions (MEMORY.md hot cache + knowledge wiki)
- **Multi-project support** with per-project backlogs and context
- **Safety hooks** that prevent context loss during compression and long sessions
- **`/close-day`** command synthesizes your entire day into a searchable daily article
- **`/tour`** interactive guided walkthrough of the system

## Quick Start

```bash
git clone https://github.com/awrshift/claude-memory-kit.git my-project
cd my-project
claude
```

## Daily Workflow

1. **Open** a session. Context loads automatically.
2. **Work** normally. Safety hooks protect your progress.
3. **`/close-day`** when done. One command captures the day.

Tomorrow starts where today left off.

## Included Skills

| Skill | Description |
|-------|-------------|
| `/close-day` | End-of-day synthesis into daily article |
| `/tour` | Interactive guided tour of the system |
| `/memory-compile` | Compile daily logs into wiki articles |
| `/memory-lint` | Run structural health checks |
| `/memory-query` | Natural-language knowledge base search |

## Architecture

700+ production sessions across 7 projects. Built on ideas from Karpathy and Cole Medin, simplified for daily CLI use.

See [ARCHITECTURE.md](ARCHITECTURE.md) for full technical details.
