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
- Install global skills (Gemini, Brainstorm, AWRSHIFT, Design, Skill Creator)
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
    │   ├── design/                  # Design system lifecycle
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

Five skills are included and installed globally (`~/.claude/skills/`) on first run. Each one gives Claude a new capability. You don't need all of them — start with what you need.

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

**Real example:**
```
You: "Review my success metrics for this feature"

Claude sends to Gemini → Gemini flags:
  - "Metric #3 can be gamed by adding empty buttons"
  - "You're missing accessibility checks"
  - "Target of 100% is unrealistic, try 90%"

Claude shows you: "Gemini caught 3 issues. Here's what I agree with..."
```

**How to trigger:** Say "ask Gemini", "second opinion", "check with Gemini", or "fact-check this"

**Setup:** `pip install google-genai` + add `GOOGLE_API_KEY` to your `.env` file ([get key here](https://aistudio.google.com/apikey))

---

### 2. Brainstorm — Two AIs Debate Your Idea

> *"When Claude and Gemini disagree, that's where the best insights hide."*

A structured 3-round dialogue where Claude and Gemini challenge each other's ideas. Think of it as a debate that ends with a clear winner.

```
  Round 1: DIVERGE          Round 2: DEEPEN           Round 3: CONVERGE
  ┌─────────────────┐      ┌─────────────────┐       ┌─────────────────┐
  │ Claude: Option A │      │ Gemini: "A fails │       │ Both agree:      │
  │ Gemini: Option B │─────▶│  when X happens" │──────▶│ "Option A with   │
  │ Gemini: Option C │      │ Claude: "B costs │       │  B's safeguard"  │
  └─────────────────┘      │  too much"       │       └─────────────────┘
                            └─────────────────┘
```

**Real example:**
```
You: "brainstorm — should we use PostgreSQL or MongoDB for this project?"

Round 1: Claude argues PostgreSQL, Gemini argues MongoDB
Round 2: Gemini finds PostgreSQL JSONB covers 90% of MongoDB use cases
Round 3: Both converge on PostgreSQL + JSONB columns for flexible data

Result: One clear recommendation with reasoning from both sides
```

**How to trigger:** Say "brainstorm", "let's think through options", or "explore this idea with Gemini"

**Setup:** Needs Gemini skill (above) to be configured first

---

### 3. AWRSHIFT — Think Before You Build

> *"The framework that stops you from coding the wrong thing."*

When you face a decision with unknowns, AWRSHIFT guides you step by step: define the problem, research options, set success metrics, verify your plan, test in a sandbox — then decide. You choose how deep to go at every step.

```
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ IDENTIFY │───▶│ RESEARCH │───▶│ METRICS  │───▶│   PLAN   │
  │          │    │          │    │          │    │          │
  │ "What's  │    │ Gather   │    │ How will │    │ Concrete │
  │ the      │    │ evidence │    │ we know  │    │ tasks    │
  │ problem?"│    │ first    │    │ it works?│    │          │
  └──────────┘    └──────────┘    └──────────┘    └──────────┘
       │                │               │               │
       ▼                ▼               ▼               ▼
    You answer     Claude researches  Gemini checks   You approve
    questions      (+ agents)        for bias         the plan
                                                          │
  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
  │FACTCHECK │◀───│          │    │   TEST   │◀──────────┘
  │          │    │  Gemini  │    │          │
  │ "Did we  │───▶│  cross-  │    │ Try in   │
  │  miss    │    │  check"  │    │ sandbox  │
  │ anything?"    └──────────┘    │ (safe!)  │
  └──────────┘                    └──────────┘
       │                               │
       ▼                               ▼
  ┌──────────┐                    ┌──────────┐
  │  DECIDE  │                    │IMPLEMENT │
  │          │                    │          │
  │ GO /     │───────────────────▶│ Apply to │
  │ NO-GO /  │   only after GO    │ main     │
  │ PIVOT    │                    │ project  │
  └──────────┘                    └──────────┘
```

**Key feature:** At every step, you get structured choices (not walls of text):
```
Claude asks:
  A) "Proceed with research on all 3 unknowns"
  B) "I have context to share first"
  C) "Skip research — I already know the answer"
  D) [type your own response]
```

**Real example:**
```
You: "awrshift — should we migrate from REST to GraphQL?"

IDENTIFY:  Claude asks 4 questions, maps the problem
RESEARCH:  3 parallel agents investigate performance, DX, migration cost
METRICS:   Proposes success criteria → Gemini checks for bias
PLAN:      Sequenced tasks with risks
FACTCHECK: Gemini cross-checks → finds missing rollback plan
TEST:      Prototype in sandbox folder (main project untouched)
DECIDE:    GO with conditions — migrate read endpoints first
```

**How to trigger:** Say "awrshift", "let's think this through", "research first", or "experiment"

**Setup:** No dependencies. Works standalone. Even better with Gemini skill installed.

---

### 4. Design — From Reference to Design System

> *"Extract design tokens from any website, generate a full design system."*

Point Claude at a reference website, and it extracts colors, fonts, spacing into a structured token system. Then generates CSS, audits your code for consistency, and runs visual QA.

```
  Reference URL          Extract             Generate            Audit
  ┌─────────────┐      ┌────────────┐      ┌────────────┐     ┌──────────┐
  │ stripe.com  │─────▶│ Colors     │─────▶│ design-    │────▶│ Check    │
  │ or any site │      │ Fonts      │      │ tokens.json│     │ your CSS │
  └─────────────┘      │ Spacing    │      │ + CSS vars │     │ matches  │
                        │ Radius     │      │ + rules    │     │ tokens   │
                        └────────────┘      └────────────┘     └──────────┘
```

**What you get:**
- `design-tokens.json` — W3C standard, works with any framework
- `design-rules.md` — behavioral rules for AI ("never use more than 3 font sizes")
- CSS custom properties — drop into Tailwind, vanilla CSS, or any stack
- Drift detection — warns when code diverges from tokens

**How to trigger:** Say "create a design system", "extract colors from [url]", or "audit my tokens"

**Setup:** Python stdlib only. Optional: Chrome MCP for visual comparison.

---

### 5. Skill Creator — Build Your Own Skills

> *"Turn any repeatable workflow into a reusable skill."*

If you find yourself giving Claude the same instructions again and again, turn them into a skill. Skill Creator helps you write it, test it with automated evals, and improve it iteratively.

```
  Your idea          Draft             Test              Ship
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ "I want  │────▶│ SKILL.md │────▶│ Run 5    │────▶│ Install  │
  │  Claude  │     │ generated│     │ test     │     │ globally │
  │  to..."  │     │          │     │ cases    │     │          │
  └──────────┘     └──────────┘     │ Score:   │     └──────────┘
                                     │ 4/5 PASS │
                                     └──────────┘
                                          │
                                     Fix failing ──▶ Re-test ──▶ 5/5 PASS
```

**Real example:**
```
You: "create a skill that generates changelog entries from git commits"

Skill Creator:
  1. Drafts SKILL.md with instructions
  2. Generates 5 test cases (edge cases included)
  3. Runs evals using `claude -p` CLI
  4. Shows results: 4/5 pass, 1 fails on merge commits
  5. Fixes the prompt, re-runs: 5/5 pass
  6. Installs to ~/.claude/skills/changelog/
```

**How to trigger:** Say "create a skill", "improve this skill", or "run skill evals"

**Setup:** Python stdlib only. Uses `claude -p` CLI for running evals.

---

### Skills at a Glance

| Skill | One-liner | Needs Gemini? | Needs setup? |
|-------|-----------|:---:|:---:|
| **Gemini** | Second opinion from a different AI | - | API key |
| **Brainstorm** | Two AIs debate, one answer emerges | Yes | - |
| **AWRSHIFT** | Step-by-step decision framework | Better with | - |
| **Design** | Reference site to design system | No | - |
| **Skill Creator** | Turn workflows into reusable skills | No | - |

## Experiments

For decisions that need research before building, use the AWRSHIFT skill or experiments directly. Each experiment follows a structured cycle:

```
IDENTIFY → RESEARCH → EVALUATE-DESIGN → PLAN → FACTCHECK → TEST → DECIDE
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

Absolutely. All 5 skills are optional. The core system (memory, context, journals, rules, hooks) works without any skills. AWRSHIFT works standalone too — it just gets enhanced when Gemini is available.
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
