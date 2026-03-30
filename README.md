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
- Ask you about your project (name, description, language)
- Install global skills (Gemini, Brainstorm, AWRSHIFT, Skill Creator)
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
│   │   ├── MEMORY.md                # Index: patterns & lessons (< 200 lines, auto-loaded)
│   │   └── topics/                  # Detailed knowledge by theme (loaded on-demand)
│   ├── rules/                       # Domain rules (auto-loaded by file path)
│   ├── hooks/
│   │   ├── session-start.sh         # Shows memory + projects at session start
│   │   └── pre-compact.sh           # Saves context before /compact
│   └── settings.json                # Permissions + hooks config
├── context/
│   └── next-session-prompt.md       # Cross-project hub ("what to do next")
├── experiments/                     # Research & decisions (IDENTIFY → DECIDE cycle)
│   ├── README.md                    # How experiments work
│   ├── 001-landing-page-redesign.md # Example: completed experiment
│   └── 002-payment-provider.md      # Example: in-progress experiment
├── projects/
│   ├── example-webapp/              # Example project (delete when ready)
│   │   └── JOURNAL.md               # Tasks, decisions, status
│   └── example-saas/                # Example project (delete when ready)
│       └── JOURNAL.md               # Tasks, decisions, status
└── global/                          # Installed to ~/.claude/ on first run
    ├── skills/
    │   ├── gemini/                   # Second opinions from Google Gemini
    │   ├── brainstorm/              # 3-round Claude x Gemini dialogue
    │   ├── awrshift/                # Adaptive decision framework
    │   └── skill-creator/           # Build and test custom skills
    └── rules/
        └── gemini.md                # Gemini usage rules (auto-loaded)
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
| **Memory** | `.claude/memory/MEMORY.md` + `topics/` | Agent updates across sessions |
| **Rules** | `.claude/rules/*.md` | You write domain rules |
| **Skills** | `~/.claude/skills/` | Installed once, available everywhere |
| **Journal** | `projects/X/JOURNAL.md` | Agent tracks tasks and decisions |
| **Context Hub** | `context/next-session-prompt.md` | Agent updates at session end |

### Memory Architecture

Memory uses a **two-tier system** (following [Anthropic's official recommendations](https://code.claude.com/docs/en/memory)):

```
.claude/memory/
├── MEMORY.md          ← Index (< 200 lines, loaded EVERY session)
└── topics/            ← Detailed knowledge (loaded ON-DEMAND)
    ├── api.md         ← Only when working on API
    ├── database.md    ← Only when working on DB
    └── ...            ← Grows with your project
```

**Why 200 lines?** Anthropic truncates MEMORY.md at 200 lines / 25KB. Content beyond that is silently lost. The index stays compact; details live in topic files that Claude reads when needed.

### Context Layers

Not everything loads every time. The kit uses a layered system — always-on at the bottom, on-demand at the top:

<p align="center">
  <img src=".github/assets/02-context-layers-pyramid.png" alt="Context Layers Pyramid" width="100%">
</p>

| Layer | What loads | When |
|-------|-----------|------|
| **L1: Auto** | CLAUDE.md + rules + MEMORY.md (index) | Every session |
| **L2: Start** | next-session-prompt.md | Session start |
| **L3: Project** | JOURNAL.md | When working on a project |
| **L4: Topics** | .claude/memory/topics/*.md | When working on specific area |
| **L5: Reference** | Experiments, docs | Only when needed |

### Session Lifecycle

Every session follows the same cycle — start, work, end. Context is saved automatically:

<p align="center">
  <img src=".github/assets/03-session-lifecycle-flow.png" alt="Session Lifecycle Flow" width="100%">
</p>

The `pre-compact.sh` hook ensures context is saved even when Claude's conversation gets compressed mid-session.

## Skills

Four skills are included and installed globally (`~/.claude/skills/`) on first run. Each one gives Claude a new capability. You don't need all of them — start with what you need.

---

### 1. Gemini — Get a Second Opinion

> *"Two heads are better than one — especially when they think differently."*

Claude is great, but every AI has blind spots. Gemini is a completely different AI (Google's), so it catches things Claude misses. It's like having a colleague review your work.

```
   You ask Claude           Claude asks Gemini          You get both views
  ┌─────────────┐         ┌──────────────────┐        ┌─────────────────┐
  │ "Is this     │───────▶│ Gemini analyzes   │──────▶│ Claude: "Here's  │
  │  plan solid?" │        │ independently     │       │  what Gemini     │
  └─────────────┘         └──────────────────┘        │  found + my take"│
                                                       └─────────────────┘
```

**How to trigger:** Say "ask Gemini", "second opinion", "check with Gemini", or "fact-check this"

**Setup:** `pip install google-genai` + add `GOOGLE_API_KEY` to your `.env` file ([get key here](https://aistudio.google.com/apikey))

---

### 2. Brainstorm — Two AIs Debate Your Idea

> *"When Claude and Gemini disagree, that's where the best insights hide."*

A structured 3-round dialogue where Claude and Gemini challenge each other's ideas. Think of it as a debate that ends with a clear winner.

**How to trigger:** Say "brainstorm", "let's think through options", or "explore this idea with Gemini"

**Setup:** Needs Gemini skill configured first

---

### 3. AWRSHIFT — Think Before You Build

> *"The framework that stops you from coding the wrong thing."*

When you face a decision with unknowns, AWRSHIFT guides you step by step: define the problem, research options, set success metrics, verify your plan, test in a sandbox — then decide.

**How to trigger:** Say "awrshift", "let's think this through", "research first", or "experiment"

**Setup:** No dependencies. Works standalone. Even better with Gemini.

---

### 4. Skill Creator — Build Your Own Skills

> *"Turn any repeatable workflow into a reusable skill."*

If you find yourself giving Claude the same instructions again and again, turn them into a skill.

**How to trigger:** Say "create a skill", "improve this skill", or "run skill evals"

**Setup:** Python stdlib only. Uses `claude -p` CLI for running evals.

---

### Skills at a Glance

| Skill | One-liner | Needs Gemini? | Needs setup? |
|-------|-----------|:---:|:---:|
| **Gemini** | Second opinion from a different AI | - | API key |
| **Brainstorm** | Two AIs debate, one answer emerges | Yes | - |
| **AWRSHIFT** | Step-by-step decision framework | Better with | - |
| **Skill Creator** | Turn workflows into reusable skills | No | - |

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
5. **Memory = index + topics** — compact index auto-loaded, details on-demand
6. **MEMORY.md < 200 lines** — Anthropic truncates beyond this, so keep it lean

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

Absolutely. All 4 skills are optional. The core system (memory, context, journals, rules, hooks) works without any skills. AWRSHIFT works standalone too — it just gets enhanced when Gemini is available.
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
