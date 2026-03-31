<p align="center">
  <img src=".github/assets/hero-banner.png" alt="Claude Code Starter Kit" width="100%">
</p>

<h2 align="center">Turn Claude into an AI assistant that actually remembers your work.</h2>

<p align="center">
  <a href="#the-problem">The Problem</a> ·
  <a href="#3-steps-to-start">Quick Start</a> ·
  <a href="#what-you-get">What You Get</a> ·
  <a href="#superpowers">Skills</a> ·
  <a href="#faq">FAQ</a>
</p>

---

## The Problem

If you use Claude or ChatGPT in your browser, you know this feeling:

- **The Amnesia Loop** — Every new chat starts from scratch. You re-explain your project, your brand voice, your team, what you did yesterday. Every. Single. Time.
- **The Context Wall** — You hit "conversation too long" right when you're making progress. Everything disappears.
- **The Copy-Paste Dance** — The AI can't see your files. You manually feed it documents, screenshots, spreadsheets. Over and over.

**This kit fixes all of that.**

It gives Claude a permanent memory, file access, and reusable skills — so every conversation picks up exactly where the last one left off.

## What Changes

| | Regular Chat 🌐 | With This Kit 🤖 |
|---|---|---|
| **Memory** | Forgets everything when you close the tab | Remembers your project details across sessions |
| **Your Files** | You copy-paste documents into chat | Claude reads and edits your files directly |
| **Consistency** | Drifts off-topic, ignores past instructions | Follows your rules and preferences every time |
| **Skills** | Does whatever the base model can do | You can teach it new abilities (like asking Google AI for help) |

---

## 3 Steps to Start

You don't need to know how to code. The whole setup takes about 5 minutes.

**What you need first:**
1. [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) installed (Anthropic's CLI tool — follow their install guide)
2. A Claude Max/Pro subscription, or an [Anthropic API key](https://console.anthropic.com/)

**Then:**

```bash
# 1. Download and rename this kit
git clone https://github.com/awrshift/claude-starter-kit.git my-project
cd my-project

# 2. Launch Claude Code
claude

# 3. That's it — Claude sets everything up automatically
```

> **New to Terminal?** Terminal is a text-based app on every computer. On Mac: search "Terminal" in Spotlight. On Windows: search "Command Prompt". You just type commands and press Enter.

> **Tip:** If you need to navigate to a folder, type `cd ` (with a space), then drag the folder from Finder/Explorer into the Terminal window. Press Enter.

On first launch, Claude will:
- Ask about your project (name, description, language)
- Set up memory and context files
- Offer to install the Gemini skill (optional — needs a free Google API key)
- Clean up demo files and greet you

**No manual configuration needed. Just talk to Claude.**

---

## What You Get

Think of this kit as a fully furnished office for your AI assistant:

### 🧠 Permanent Memory
Claude keeps a notebook (`.claude/memory/`) that it reads every session. Your project details, decisions, preferences — all remembered automatically. You never re-explain anything.

### 🛠️ Built-in Skills
Four pre-installed "superpowers" that extend what Claude can do. Get second opinions from Google AI, run structured brainstorms, make complex decisions with a framework. All included in `.claude/skills/`.

### 📋 Project Tracking
Each project gets a Journal (`projects/your-project/JOURNAL.md`) — a single file where Claude tracks tasks, decisions, and progress. You can have multiple projects running at once.

### 🔬 Experiment System
Trying different approaches? The `experiments/` folder is built for structured research — define a question, explore options, compare results, make a decision.

### 💾 Auto-Save
Before Claude's conversation gets long and compresses, a built-in safety net reminds it to save all progress. Nothing gets lost.

---

## Superpowers

Four skills are included right in the project (`.claude/skills/`). Each one gives Claude a new ability. You don't need all of them — start with what makes sense for your work.

### Gemini — Get a Second Opinion

> *"Two AI brains are better than one — especially when they think differently."*

Claude asks Google's Gemini AI to review its own work. Different AI = different blind spots caught.

**Real scenario:** You ask Claude to write a marketing strategy. Before showing it to you, Claude sends it to Gemini for critique. You get the best of both worlds.

**How to use:** Say *"ask Gemini"*, *"second opinion"*, or *"check with Gemini"*

**Setup:** `pip install google-genai` + a free [Google API key](https://aistudio.google.com/apikey)

---

### Brainstorm — Two AIs Debate Your Idea

> *"When Claude and Gemini disagree, that's where the best insights hide."*

A structured 3-round dialogue where Claude and Gemini challenge each other. Diverge → Deepen → Converge. Ends with one clear recommendation.

**Real scenario:** You're choosing between three campaign approaches. Claude and Gemini debate the pros and cons in three rounds, then present you with a winner.

**How to use:** Say *"brainstorm"*, *"let's think through options"*, or *"explore this with Gemini"*

---

### AWRSHIFT — Think Before You Build

> *"The framework that stops you from building the wrong thing."*

A step-by-step decision process: define the problem → research options → set success metrics → test → decide. Perfect for complex choices with unknowns.

**Real scenario:** Your team can't agree on which tool to use for project management. AWRSHIFT guides you through structured evaluation — not gut feeling, but evidence.

**How to use:** Say *"awrshift"*, *"let's research this"*, or *"think this through"*

---

### Skill Creator — Teach Claude New Tricks

> *"Turn any repeatable workflow into a reusable command."*

If you find yourself giving Claude the same instructions every week (e.g., "write my Friday report in this format"), turn it into a permanent skill.

**How to use:** Say *"create a skill"* or *"turn this into a skill"*

---

### Skills at a Glance

| Skill | What it does | Needs setup? |
|-------|-------------|:---:|
| **Gemini** | Second opinion from Google AI | Free API key |
| **Brainstorm** | Two AIs debate, one answer | Needs Gemini |
| **AWRSHIFT** | Step-by-step decision framework | No |
| **Skill Creator** | Build your own skills | No |

---

## What People Build With This

Because Claude can read, write, and remember — non-technical professionals are building things like:

1. **Content Strategist** — Claude remembers a 20-page brand guideline. It drafts blog posts, saves them to a "Drafts" folder, and updates a content calendar — all automatically.

2. **HR Specialist** — Claude acts as an interview prep assistant. It knows the company values, generates custom questions based on a resume, and saves evaluation notes.

3. **Project Manager** — Claude maintains risk logs and status reports. Every Friday, the PM talks through the week and Claude updates all project documents.

4. **Marketer** — Claude tracks A/B test experiments. It remembers which ad copy worked last month and uses that data to write next month's campaigns.

5. **Course Creator** — Claude organizes entire curriculums. When you change Module 2, it automatically knows to update references in Module 5.

---

## How It Actually Works

### Your Agent's Anatomy

Every Claude agent built with this kit has 6 core components working together:

<p align="center">
  <img src=".github/assets/01-agent-anatomy-mindmap.png" alt="Agent Anatomy" width="100%">
</p>

| Component | What it is | Simple analogy |
|-----------|-----------|----------------|
| **Brain** | `CLAUDE.md` | Your agent's job description |
| **Memory** | `.claude/memory/` | A notebook it reads every morning |
| **Rules** | `.claude/rules/` | House rules posted on the wall |
| **Skills** | `.claude/skills/` | Special abilities in a toolbox |
| **Journal** | `projects/X/JOURNAL.md` | A to-do list for each project |
| **Context Hub** | `context/next-session-prompt.md` | A sticky note: "pick up here tomorrow" |

### What Loads When

Not everything loads every time. The kit uses layers — always-on at the bottom, on-demand at the top:

<p align="center">
  <img src=".github/assets/02-context-layers-pyramid.png" alt="Context Layers" width="100%">
</p>

| Layer | What loads | When |
|-------|-----------|------|
| **Always** | Brain + Rules + Memory index | Every session |
| **Start** | "What to do next" prompt | Session start |
| **Project** | Journal for that project | When you work on it |
| **Topics** | Detailed knowledge files | Only when relevant |
| **Reference** | Experiments, docs | Only when needed |

### Session Lifecycle

Every session follows the same cycle — start, work, save. Context is preserved automatically:

<p align="center">
  <img src=".github/assets/03-session-lifecycle-flow.png" alt="Session Lifecycle" width="100%">
</p>

A built-in safety net (`pre-compact` hook) makes sure progress is saved even when a long conversation gets compressed.

---

## FAQ

<details>
<summary><strong>What is "Terminal"? Is it safe?</strong></summary>

Terminal is a text-based way to talk to your computer. Every Mac and Windows PC has one built in. It's completely safe — you're just typing commands instead of clicking buttons. Think of it as texting your computer.
</details>

<details>
<summary><strong>Do I need to know how to code?</strong></summary>

No. After the 5-minute setup, you communicate entirely in plain English. You can say things like: *"Read the marketing plan and write three emails based on it, then save them in my emails folder."*
</details>

<details>
<summary><strong>Is my data private?</strong></summary>

Yes. Claude Code runs on your computer and talks to Anthropic's API, which by default does **not** train models on your data. This is significantly more private than free web chat tools.
</details>

<details>
<summary><strong>Does this cost money?</strong></summary>

Claude Code requires either a Claude Max/Pro subscription or Anthropic API credits. The Gemini skill needs a free Google API key. The kit itself is completely free and open source.
</details>

<details>
<summary><strong>What's the difference between this and regular Claude?</strong></summary>

Regular Claude lives in a browser, resets every chat, and can't see your files. Claude Code (with this kit) lives on your computer, remembers everything across sessions, creates and edits files, and follows your custom rules.
</details>

<details>
<summary><strong>Can I use this without the Gemini skill?</strong></summary>

Absolutely. All skills are optional. The core system (memory, context, journals, rules) works perfectly on its own.
</details>

<details>
<summary><strong>Can I add my own skills?</strong></summary>

Yes. Create a folder in `.claude/skills/your-skill/` with a `SKILL.md` file. Or just say "create a skill" and Claude will build one for you using the Skill Creator.
</details>

<details>
<summary><strong>I messed something up. How do I start over?</strong></summary>

Close Terminal. Delete the project folder. Download the kit again and start fresh. Your data is just files on your computer — nothing is locked.
</details>

---

## Credits

Built by **Serhii Kravchenko** ([@pmserhii](https://github.com/awrshift)) — based on 1000+ sessions of iterative refinement with Claude Code, building AI content pipelines, multi-agent systems, and GEO optimization tools.

## License

MIT — use it, modify it, share it.
