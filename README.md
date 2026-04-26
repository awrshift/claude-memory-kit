![Claude Memory Kit — The OS layer for Claude Code](.github/assets/og-banner.png)

# Claude Memory Kit

**Your Claude agent remembers everything. Across sessions. Across projects. Zero setup.**

[![Version](https://img.shields.io/github/v/release/awrshift/claude-memory-kit?label=version&color=brightgreen)](https://github.com/awrshift/claude-memory-kit/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-6366f1)](https://docs.anthropic.com/en/docs/claude-code/overview)
[![Stars](https://img.shields.io/github/stars/awrshift/claude-memory-kit?style=social)](https://github.com/awrshift/claude-memory-kit/stargazers)

## The Problem

Every new Claude session starts from zero. Yesterday's decisions, last week's research, the bug you fixed three days ago — gone. You waste the first 10 minutes re-explaining what Claude already knew.

**Claude Memory Kit fixes this in 3 commands. No API cost. Runs on your existing subscription.**

## Get Started

```bash
git clone https://github.com/awrshift/claude-memory-kit.git my-project
cd my-project
claude
```

That's it. Claude sets everything up and asks a few questions (your name, project name, language).

> [!TIP]
> Type `/tour` after setup — Claude walks you through the system using your actual files.

---

## Before and After

![](.github/assets/01-before-after.png)

| | Without Memory Kit | With Memory Kit |
|---|---|---|
| **New session** | Starts from zero. "What project is this?" | Knows your project, last session, current tasks |
| **After 10 sessions** | Nothing accumulated | Searchable wiki of decisions, patterns, lessons |
| **Multiple projects** | Total chaos | Each project has its own context, automatically |
| **Context compression** | Silently loses everything | Hook blocks Claude until it saves first |
| **Next day** | "Remind me what we did yesterday" | Agent already knows — injected at session start |

---

## Your Daily Workflow

![](.github/assets/02-daily-workflow.png)

Three steps. That's your entire workflow:

### 1. Open a session
Claude automatically loads your context — project state, recent decisions, knowledge wiki. You don't do anything.

### 2. Work normally
Talk to Claude. Build features. Fix bugs. Research. Safety hooks run invisibly — they checkpoint your progress every ~50 exchanges and before context compression.

### 3. Close the day
When you're done, type `/close-day`. Claude doesn't just dump today into a file — it **audits** what happened, compares against accumulated memory, and proposes which patterns deserve to grow into your reference skills. You confirm verbally («да»). Agent writes.

**That's the v4 ritual.** Tomorrow's session starts exactly where you left off.

---

## Knowledge Compounds Over Time

![](.github/assets/03-knowledge-growth.png)

Every `/close-day` feeds a four-layer memory pipeline:

| Layer | Answers | Written by |
|---|---|---|
| `daily/YYYY-MM-DD.md` | "what happened today" | `/close-day` synthesis |
| `.claude/memory/MEMORY.md` | "what patterns repeat across sessions" | Agent as you speak (date-tagged) |
| `.claude/skills/<role>-guidance/SKILL.md` | "how should a designer / editor / engineer think about X" | `/close-day` audit promotion |
| `.claude/rules/*.md` | "what must always / never happen" | After 6+ months stable, agent proposes promotion |

- **Day 1–7:** Basic patterns, project structure, your preferences
- **Week 2–4:** Decisions accumulate. Agent starts referencing past reasoning
- **Month 2+:** Full wiki of concepts, cross-project connections, lessons learned

Run `/memory-compile` periodically to structure daily logs into searchable wiki articles. Or don't — the daily logs alone give you 80% of the value.

---

## What's New in v4

If you're coming from v3, the architecture changed:

- **Agent-driven promotion ritual.** When a pattern repeats, the agent surfaces it on `/close-day` and asks: «заметил X три раза за неделю — добавить в design-guidance?». You confirm verbally. Agent writes the patch. No manual file editing, no background detection scripts.
- **Reference skills replace `playbooks/`.** Role wisdom (designer / editor / marketer / engineer / SEO / PM / founder taste) lives in `.claude/skills/<role>-guidance/SKILL.md` with `user-invocable: false` — Anthropic's native primitive. Claude auto-loads them when the conversation matches their `description`. No custom trigger tables to maintain.
- **`/memory-audit`** — new operator. Detects oversized reference skills (> 500 lines) and proposes semantic splits. You confirm; agent executes.
- **Multi-project isolation.** Each project has its own `projects/<name>/` folder with backlog + uploaded materials (PDFs, briefs). Switch projects by saying «работаем над X» — agent swaps context.
- **Removed complexity:** `experiences/` staging layer, background `promote-patterns.py` detector, `flush.py` auto-flush, separate `playbooks/` directory. Simpler pipeline.

See [CHANGELOG.md](CHANGELOG.md) for the full v3.2 → v4 migration notes.

---

## What You Get

| What | How it helps |
|------|-------------|
| **Persistent memory** | Patterns and decisions survive between sessions |
| **Reference skills** | Role wisdom that auto-loads when relevant (no manual triggering) |
| **Multi-project support** | Each project has its own backlog + materials |
| **Session handoff** | `next-session-prompt.md` — "pick up exactly here" |
| **Knowledge wiki** | Structured articles with search, built from your daily work |
| **Safety hooks** | Agent can't lose context during compression or long sessions |
| **Commands** | `/close-day`, `/memory-audit`, `/memory-compile`, `/memory-lint`, `/memory-query`, `/tour` |

Everything is plain Markdown files. No database. No external services. `git checkout` recovers anything.

---

## FAQ

<details>
<summary><b>Do I need to know how to code?</b></summary>

No. You talk to Claude in plain language. "Read the marketing plan and draft three emails" works perfectly.

</details>

<details>
<summary><b>How much does it cost?</b></summary>

The kit is free and open source. You need a Claude Pro or Max subscription (which you probably already have). No extra API cost.

</details>

<details>
<summary><b>Is my data private?</b></summary>

Yes. Everything stays on your computer in plain text files.

</details>

<details>
<summary><b>Can I use this with an existing project?</b></summary>

Yes. During setup, tell Claude you have existing code. It analyzes the structure and sets up context around it.

</details>

<details>
<summary><b>What if I forget to run /close-day?</b></summary>

Nothing bad happens. Your in-session saves (patterns, tasks, handoff notes) are already captured by safety hooks. `/close-day` adds a richer audit ritual on top — nice to have, not critical.

</details>

<details>
<summary><b>What happens if I mess up the memory files?</b></summary>

Everything is in git. `git checkout .claude/memory/` rolls back instantly. Or run `/memory-lint` to auto-fix structural issues. The "user only talks; agent writes" invariant means you never edit memory files manually anyway — so this scenario is rare.

</details>

<details>
<summary><b>Upgrading from v3.2?</b></summary>

Don't merge in-place. Start a fresh project with v4 and tell Claude «мы мигрируем с v3.2, вот мой старый проект». Agent walks you through importing — `experiences/` → reference-skill candidates, old MEMORY → re-tagged, daily/concepts/rules copied verbatim.

</details>

---

## Project Structure

```
SKILL.md                          ← Skill entry point (for aggregators)
CLAUDE.md                         ← Agent brain (identity + session workflow)
README.md                         ← You are here
ARCHITECTURE.md                   ← Full layer map + promotion pipeline
CHANGELOG.md                      ← Version history (v3.2 → v4 migration)
skills/                           ← Aggregator-facing skill index (symlinks into .claude/skills/)
├── close-day/SKILL.md            → ../../.claude/skills/close-day/SKILL.md
├── memory-audit/SKILL.md         → ../../.claude/skills/memory-audit/SKILL.md
└── tour/SKILL.md                 → ../../.claude/skills/tour/SKILL.md
knowledge/                        ← Wiki articles (grows over time)
├── concepts/                     ← Topic articles — facts + rationale
├── connections/                  ← Cross-references
└── meetings/                     ← Meeting synthesis
projects/                         ← Per-project backlogs + uploaded materials
context/next-session-prompt.md    ← Session handoff
daily/YYYY-MM-DD.md               ← Chronological session logs
experiments/                      ← Sandbox for research with EXPERIMENT.md template
.claude/
├── memory/MEMORY.md              ← Hot cache (~200 lines, date-tagged patterns)
├── memory/scripts/               ← Pipeline: compile, lint, query, config
├── hooks/                        ← 5 hooks (context injection + safety nets)
├── rules/                        ← Mechanical project rules (path-scopable)
├── commands/                     ← Slash commands
├── skills/<role>-guidance/       ← Reference skills (user-invocable: false)
├── skills/<task>/                ← Task skills (/close-day, /memory-audit, /tour)
└── settings.json                 ← Hook + permission registration
```

Runtime reads skills from `.claude/skills/`. The root `skills/` directory exists for Claude Code skill aggregators that scan repository roots — kept in sync via symlinks so edits to one reflect in the other.

---

## How It Works (for the curious)

You interact with three things: your project files, slash commands, and Claude. Everything else is automatic.

Under the hood:
- `session-start.py` hook injects your knowledge wiki index + recent daily logs at startup (~24K tokens budget)
- Safety hooks (`pre-compact.sh`, `periodic-save.sh`) checkpoint progress automatically and block context compression until state is saved
- Reference skills auto-load via Anthropic's `description`-matching — when you say «давай поработаем над дизайном», `design-guidance` loads with full body
- `/close-day` synthesizes today + audits patterns against accumulated memory and reference skills, proposes promotions verbally, writes on your «да»
- `/memory-compile` transforms daily logs into structured wiki entries (uses `claude -p` subscription, zero incremental cost)

**Full architecture details:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Provenance

Built on ideas from [Andrej Karpathy](https://karpathy.ai/) (LLM knowledge base patterns) and [Cole Medin](https://github.com/coleam00)'s `claude-memory-compiler`. Aligned with Anthropic's native Claude Code primitives (skills, hooks, settings).

700+ real sessions across 7+ projects. Every component earns its place; `experiences/`, `playbooks/`, and background-detection scripts didn't survive review.

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
