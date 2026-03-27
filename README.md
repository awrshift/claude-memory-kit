<p align="center">
  <img src=".github/assets/hero-banner.png" alt="Claude Code Starter Kit" width="100%">
</p>

<p align="center">
  <strong>Ready-to-use project structure for Claude Code agents</strong><br>
  Memory that persists. Context that doesn't get lost. Skills that work out of the box.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#whats-inside">What's Inside</a> &bull;
  <a href="#how-it-works">How It Works</a> &bull;
  <a href="#skills">Skills</a> &bull;
  <a href="#faq">FAQ</a>
</p>

---

## The Problem

You start a Claude Code session. You work for an hour. You close the terminal. Next time you open it — Claude has **no idea** what happened. You explain everything again. And again. And again.

**This kit fixes that.**

It gives Claude Code a structured memory, session continuity, and reusable skills — so every session picks up exactly where the last one left off.

## Quick Start

```bash
# 1. Copy the kit and rename to your project
cp -r claude-starter-kit my-project
cd my-project

# 2. Start Claude Code
claude

# 3. That's it — Claude sets everything up automatically on first run
```

On first launch, Claude will:
- Install global skills (Gemini, Brainstorm, Design)
- Set up memory and context files
- Initialize git repository
- Clean up scaffolding
- Greet you and explain the structure

**No manual configuration needed.**

## What's Inside

```
your-project/
├── CLAUDE.md                        # Agent brain — reads this every session
├── .claude/
│   ├── memory/
│   │   ├── MEMORY.md                # Long-term patterns (agent updates this)
│   │   ├── CONTEXT.md               # Quick orientation (active project, pointers)
│   │   └── snapshots/               # Session backups (protection against context loss)
│   ├── rules/                       # Domain rules (auto-loaded by file path)
│   ├── hooks/
│   │   ├── session-start.sh         # Shows memory + context at session start
│   │   └── pre-compact.sh          # Saves context before /compact
│   └── settings.json                # Permissions + hooks config
├── context/
│   └── next-session-prompt.md       # Cross-project hub ("what to do next")
├── experiments/                     # Research & decisions (IDENTIFY → DECIDE cycle)
│   ├── README.md                    # How experiments work
│   ├── 001-landing-page-redesign.md # Example: completed experiment
│   └── 002-payment-provider.md      # Example: in-progress experiment
└── projects/
    ├── example-webapp/              # Example project (delete when ready)
    │   └── JOURNAL.md               # Tasks, decisions, status
    └── example-saas/                # Example project (delete when ready)
        └── JOURNAL.md               # Tasks, decisions, status
```

## How It Works

### Agent Anatomy

Every Claude Code agent built with this kit has 6 core components:

<p align="center">
  <img src=".github/assets/01-agent-anatomy-mindmap.png" alt="Agent Anatomy Mind Map" width="100%">
</p>

| Component | File | Who maintains it |
|-----------|------|-----------------|
| **Brain** | `CLAUDE.md` | You write it, agent follows |
| **Memory** | `.claude/memory/MEMORY.md` | Agent updates across sessions |
| **Rules** | `.claude/rules/*.md` | You write domain rules |
| **Skills** | `~/.claude/skills/` | Installed once, available everywhere |
| **Journal** | `projects/X/JOURNAL.md` | Agent tracks tasks and decisions |
| **Context Hub** | `context/next-session-prompt.md` | Agent updates at session end |

### Context Layers

Not everything loads every time. The kit uses a 4-layer system — always-on at the bottom, on-demand at the top:

<p align="center">
  <img src=".github/assets/02-context-layers-pyramid.png" alt="Context Layers Pyramid" width="100%">
</p>

| Layer | What loads | When |
|-------|-----------|------|
| **L1: Auto** | CLAUDE.md + rules + MEMORY.md | Every session |
| **L2: Start** | next-session-prompt + CONTEXT.md | Session start |
| **L3: Project** | JOURNAL.md | When working on a project |
| **L4: Reference** | Docs, snapshots | Only when needed |

### Session Lifecycle

Every session follows the same cycle — start, work, end. Context is saved automatically:

<p align="center">
  <img src=".github/assets/03-session-lifecycle-flow.png" alt="Session Lifecycle Flow" width="100%">
</p>

The `pre-compact.sh` hook ensures context is saved even when Claude's conversation gets compressed mid-session.

## Skills

Three skills are included and installed globally (`~/.claude/skills/`) on first run:

### Gemini — Second Opinions

Get analysis from a different AI model family (Google Gemini). Different model = different blind spots caught.

```bash
# Quick question
python3 ~/.claude/skills/gemini/gemini.py ask "your question"

# Deep analysis
python3 ~/.claude/skills/gemini/gemini.py second-opinion "question" --context "context"
```

**Requires:** `pip install google-genai` + `GOOGLE_API_KEY` in `.env`

### Brainstorm — Claude x Gemini Dialogue

3-round adversarial dialogue between Claude and Gemini. Diverge ideas → Deepen analysis → Converge to one action.

**When to use:** Multiple viable paths and you need to pick one. Strategic decisions. Architecture choices.

**Requires:** Gemini skill (above)

### Design — Design System Lifecycle

Full design token pipeline: extract from reference → OKLCH palette → tokens → CSS → audit → Visual QA.

**Requires:** Python stdlib only (no external deps). Optional: Chrome MCP for visual QA.

## Experiments

For decisions that need research before building, use experiments. Each experiment follows a structured cycle:

```
IDENTIFY → RESEARCH → HYPOTHESIZE → PLAN → IMPLEMENT → EVALUATE → DECIDE
```

See `experiments/README.md` for details. Two example experiments are included — one completed (landing page A/B test) and one in-progress (payment provider comparison).

## Multiple Projects

The kit supports multiple projects in one workspace. Each project gets:
- Its own `JOURNAL.md` in `projects/`
- Its own `<!-- PROJECT:name -->` section in `next-session-prompt.md`

Multiple Claude Code windows can work on different projects in parallel — they only edit their own sections.

```bash
# Adding a new project
mkdir projects/my-new-project
cp projects/example-webapp/JOURNAL.md projects/my-new-project/
# Then add <!-- PROJECT:my-new-project --> section in next-session-prompt.md
```

## Key Principles

1. **One project = one JOURNAL.md** — all tasks and decisions in one place
2. **Decisions live with tasks** — not in separate decision log files
3. **next-session-prompt = pointers** — brief "what's next", not full history
4. **Rules = stable behavior** — things that don't change session to session
5. **Memory grows organically** — agent learns patterns and saves them automatically

## FAQ

<details>
<summary><strong>Do I need to know how to code?</strong></summary>

No. Copy the folder, open terminal, type `claude`, and start talking. The agent handles setup automatically.
</details>

<details>
<summary><strong>Does this work with Claude Code Pro/Max subscription?</strong></summary>

Yes. This is a project structure — it works with any Claude Code plan.
</details>

<details>
<summary><strong>Can I use this without the Gemini skill?</strong></summary>

Absolutely. Gemini, Brainstorm, and Design are optional. The core system (memory, context, journals, rules, hooks) works without any skills.
</details>

<details>
<summary><strong>What happens if I don't say "save context" at the end?</strong></summary>

The `pre-compact.sh` hook acts as a safety net — it reminds the agent to save before context compression. But explicitly saying "save context" or "update context" at session end is a good habit.
</details>

<details>
<summary><strong>Can I add my own skills?</strong></summary>

Yes. Create a directory in `~/.claude/skills/your-skill/` with a `SKILL.md` file describing what it does and how to invoke it. Then reference it in your `CLAUDE.md`.
</details>

<details>
<summary><strong>How is this different from just using CLAUDE.md?</strong></summary>

CLAUDE.md alone gives instructions but no memory, no session continuity, no structured task tracking, no hooks, no skills. This kit adds all of that as a coherent system.
</details>

---

## Credits

Built by **Serhii Kravchenko** — based on 1000+ sessions of iterative refinement building AI content generation pipelines, multi-agent systems, and GEO optimization tools.

## License

MIT — use it, modify it, share it.
