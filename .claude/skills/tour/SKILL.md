---
name: tour
description: Interactive guided tour of the Claude Memory Kit. Claude teaches the system from inside by reading actual project files and explaining what they do. Use this skill whenever the user says "/tour", "show me how memory works", "how does this kit work", "проведи тур", "покажи как всё устроено", "explain this system", "help me get started", or seems lost after cloning the repo. Also trigger on questions about specific components (memory, journals, hooks, rules, experiments). This is the primary onboarding and education tool — prefer it over ad-hoc explanations.
---

# Tour — Interactive Guide to Claude Memory Kit

An interactive walkthrough where you teach the user the Memory Kit by working with their actual files. You read real files, explain what you see, and help the user create their first entries.

## Principles

1. **Problem-First.** Every component exists to solve a pain. Start each step with the pain it fixes — not a feature description. If the user doesn't feel the WHY, the HOW is noise.

2. **Read, don't recite.** Never explain a component from memory. Read the actual file first (`CLAUDE.md`, `MEMORY.md`, hook scripts, etc.), then explain what you see. The files ARE the documentation. This keeps explanations accurate as the kit evolves.

3. **One step at a time.** Never dump multiple steps in one message. Present one step, wait for the user's response, then continue. This is a conversation.

4. **Do, don't lecture.** Each step ends with the user (or you) actually writing to a file. The tour produces real artifacts — a memory entry, a project journal, maybe a rule. Not just knowledge.

5. **Adapt.** Use the language from CLAUDE.md. Match the user's technical level. If they're experienced, be concise. If they're new, use analogies. Never condescend.

## Before starting

- Check if `<!-- SETUP:START -->` still exists in CLAUDE.md. If yes — run onboarding first, tour second.
- Detect user's language from CLAUDE.md. If unclear, ask.
- If user asks about a SPECIFIC component ("how do hooks work?"), skip to that step directly. Don't force the full tour.

## The Steps

Run in order for a full tour. Each step: **Pain → Read actual files → Do something → Confirm it worked.**

### Step 1: Memory — Two Tiers
**Pain:** Without this, I forget everything between sessions. Your name, decisions, preferences — gone.
- Read `.claude/memory/MEMORY.md` — show it, explain the structure (date convention `[YYYY-MM]`, sections, 200-line cap)
- Read `.claude/memory/knowledge/index.md` — explain this is the wiki layer (concepts, connections, meetings, qa) loaded on-demand, not every session
- Explain the split: MEMORY.md = hot cache (one-line patterns, auto-loaded), knowledge/ = deep articles (Markdown + `[[wikilinks]]`, Obsidian-compatible but Obsidian NOT required)
- Ask the user for something to remember (stack, preference, convention)
- Write it to MEMORY.md in the format the file already uses
- Show the result

### Step 2: Projects & Journal
**Pain:** Tasks said out loud disappear when the conversation gets long. The Journal survives.
- Show `projects/` directory — what exists
- Help create a project with a JOURNAL.md (follow the pattern from CLAUDE.md or existing examples)
- Add the project to `context/next-session-prompt.md` with PROJECT tags
- Show both files — explain that next session starts by reading these

### Step 3: Context Protection (Hooks)
**Pain:** Long conversations get compressed by Claude Code. Without protection, progress disappears mid-session.
- Read the 5 hook scripts in `.claude/hooks/` — explain each one IN PLAIN WORDS based on what you see in the code:
  - `session-start.sh` — context overview at session start
  - `pre-compact.sh` — BLOCKS `/compact` until MEMORY.md is updated (mtime check)
  - `periodic-save.sh` — auto-checkpoint every 50 exchanges (configurable via `CLAUDE_SAVE_INTERVAL`)
  - `session-end.sh` — auto-captures conversation transcripts to `daily/YYYY-MM-DD.md` in background (spawns `flush.py`)
  - `protect-tests.sh` — blocks edits to existing test files (Write new tests allowed)
- Show `daily/` directory — explain that each session gets its own file, auto-written by the session-end hook, zero user action needed
- Reference the session-start output if it fired this session
- Key message: all automatic, user does nothing. Say "save context" to force a manual save anytime.

### Check-in
Ask: "That's the core. Want to see Rules, Scripts pipeline, and Experiments too, or start working?" Steps 4-6 are optional.

### Step 4: Rules
**Pain:** If I make the same mistake twice, it's because nobody wrote it down.
- Show `.claude/rules/` — read any existing rules, explain what they do
- Offer to create one if the user has a convention. If not: "Say 'make this a rule' anytime I repeat a mistake."

### Step 5: Memory Kit v2 Scripts (power user)
**Pain:** After 50 sessions, `daily/` has hundreds of entries — useful, but too raw to search efficiently.
- Show `.claude/memory/scripts/` — list the 5 files: `compile.py`, `lint.py`, `query.py`, `flush.py`, `config.py`
- Explain in one sentence each:
  - `compile.py` — reads `daily/` logs and writes structured wiki articles into `knowledge/` (via `claude -p` subscription, zero API cost)
  - `lint.py` — 7 structural health checks on `knowledge/` + `--fix` auto-repairs broken backlinks
  - `query.py` — index-guided retrieval across `knowledge/`, with optional `--file-back` to save answers as Q&A articles (compounding loop)
  - `flush.py` — called by `session-end.sh` hook in background; user never invokes manually
  - `config.py` — path constants (don't touch)
- Demo: run `python3 .claude/memory/scripts/lint.py` against the empty wiki — show the output (likely 0 errors on a fresh clone)
- Key message: scripts are OPT-IN. Only `flush.py` runs automatically (via hook). The rest you call when you want to compile/query/lint. Pure Python stdlib, zero `pip install`.

### Step 6: Experiments
**Pain:** Sometimes you need to research before building. Without a sandbox, research and production code mix.
- Show `experiments/` — read README.md, explain the lifecycle based on what the file says
- Offer to create one if the user has an open question. If not: "Say 'create an experiment' when you hit a fork."

## Wrap-up

Summarize what was created during the tour (table). Three takeaways:
1. Just work normally — I track and save automatically
2. "Save context" forces a checkpoint
3. `/tour` anytime to revisit

"Ready? Tell me what you need."
