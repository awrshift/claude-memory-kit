# CLAUDE.md

<!-- SETUP:START — Agent deletes this entire section (from SETUP:START to SETUP:END) after completing first run setup -->
## First Run Setup

**You are reading this for the first time. Complete these setup steps, then delete this section.**

### Step 1: Initialize git

If this directory is not a git repo yet, run `git init` and create initial commit with all files (so scaffolding is preserved in history).

### Step 2: Global settings

Check if `~/.claude/CLAUDE.md` exists:
- **If it does NOT exist** — copy `global/CLAUDE.md` to `~/.claude/CLAUDE.md`
- **If it exists** — skip (don't overwrite the user's existing settings)

### Step 3: Install global skills and rules

**Skills** — copy from `global/skills/` to `~/.claude/skills/`:
- For each skill directory in `global/skills/`:
  - **If `~/.claude/skills/<name>/` does NOT exist** — copy the entire skill directory
  - **If it exists** — skip (don't overwrite existing skills)

**Rules** — copy from `global/rules/` to `.claude/rules/` (project-level):
- For each rule file in `global/rules/`:
  - Copy to `.claude/rules/` (these are project-specific, not global)

After copying, tell the user which skills were installed and any prerequisites:
- **Gemini skill** requires: `pip install google-genai` and `GOOGLE_API_KEY` in `.env`
- **Brainstorm skill** requires: Gemini skill (uses it for multi-round dialogue)
- **Design skill** requires: no external deps (Python stdlib only). Uses `frontend-design` plugin for screen generation and optionally Stitch MCP for prototyping

### Step 4: Verify memory directory

Check that `.claude/memory/MEMORY.md` and `.claude/memory/CONTEXT.md` exist (they should — included in the starter kit). These are your persistent files. You will update them as you work.

If they exist, tell the user: "Memory is set up. I'll save patterns and context here across sessions."

### Step 5: Verify hooks

Make hooks executable:
```bash
chmod +x .claude/hooks/session-start.sh .claude/hooks/pre-compact.sh
```

The hooks are already configured in `.claude/settings.json`:
- `session-start.sh` — runs at session start, shows memory summary + context
- `pre-compact.sh` — runs before /compact, reminds to save context

### Step 6: Clean up scaffolding

Delete these files/directories (they are only needed for first run):
- `global/` directory (entire folder)
- `README.md`

Commit the cleanup: `git commit -am "setup: clean scaffolding after first run"`

### Step 7: Remove this section

Delete everything between `<!-- SETUP:START -->` and `<!-- SETUP:END -->` markers (inclusive) from this file. Commit.

### Step 8: Greet the user

Tell the user in their language: "Setup complete. Project is ready. Here's what was configured..." and briefly explain:
- File structure (CLAUDE.md, memory, context, rules, hooks)
- Installed skills and their prerequisites
- How sessions work (start → work → end cycle)
<!-- SETUP:END -->

## Project Overview

**Project:** [PROJECT NAME — replace this]
**Owner:** [YOUR NAME]
**Started:** [DATE]

[Brief description of what this project is about. 2-3 sentences max.]

## Session Workflow

**Start:**
1. Read `context/next-session-prompt.md` — find your `<!-- PROJECT:name -->` section
2. Read `.claude/memory/CONTEXT.md` — quick orientation (active project, pointers)
3. Read `.claude/memory/MEMORY.md` — recall patterns from past sessions
4. If user asks about a specific project → read that project's `JOURNAL.md`

**During:** Work on tasks. Update project JOURNAL.md after completing work.

**End (all steps, in order):**
1. **MEMORY.md** — add new verified patterns, update existing. Shared across all projects.
2. **next-session-prompt.md** — update ONLY your `<!-- PROJECT:name -->` section. Include: what was done, files changed, decisions made, `### IMMEDIATE NEXT` (exact first steps for next session).
3. **CONTEXT.md** — update active project name, paused tracks
4. **JOURNAL.md** — update task statuses if any active tasks
5. **Snapshot** — write to `.claude/memory/snapshots/YYYY-MM-DD-projectname-NNN.md` (max 50 lines)

**Before /compact (MANDATORY):**
Context is about to compress. Execute End steps 1-4 BEFORE allowing compact to proceed. The `pre-compact.sh` hook will remind you, but you must actually do the work.

**Context Save triggers:** User says "save context", "update context", or session is ending.

### Multi-Project Safety

When the user has multiple projects, each project gets its own `<!-- PROJECT:name -->` section in `next-session-prompt.md`. Multiple Claude Code windows may run in parallel on different projects.

**Critical rules:**
- **next-session-prompt.md** — ONLY edit within your project's `<!-- PROJECT:name -->` / `<!-- /PROJECT:name -->` tags. Another window may be editing a different project section at the same time.
- **MEMORY.md** — shared across all projects. Write patterns that apply broadly. Tag project-specific patterns: `[Project: name]`.
- **CONTEXT.md** — update the "Active Project" field to YOUR current project. If another session set a different project, don't overwrite — add yours as a second line.
- **JOURNAL.md** — each project has its own. No conflicts possible (one file per project).

### next-session-prompt.md — How It Works

This file is the **cross-project hub**. It uses `<!-- PROJECT:name -->` / `<!-- /PROJECT:name -->` tags so multiple sessions can work in parallel without overwriting each other.

**Rules:**
1. **Only edit your project's section.** Use Edit tool scoped within your project tags.
2. **Never touch other projects' sections.** Another session may be updating them.
3. **New project?** Append a new `<!-- PROJECT:name -->` block before `<!-- SHARED -->`.
4. **Cross-project data** → update in `<!-- SHARED -->` section only.
5. **Header** (date, session number) → last writer wins, acceptable.

**What goes in each project section (max 5-7 lines):**
- Pointer to project JOURNAL.md (source of truth)
- What was done (key files, decisions)
- `### IMMEDIATE NEXT` — exact first steps after restart
- Any urgent deadlines or pending actions

**What does NOT go here:**
- Full task lists (those live in JOURNAL.md)
- Session history or detailed notes
- Decision rationale (inline in JOURNAL tasks)

## Context Architecture

| Layer | Files | When loaded |
|-------|-------|-------------|
| **L1: Auto** | This file + `.claude/rules/` + `.claude/memory/MEMORY.md` | Every session |
| **L2: Start** | `context/next-session-prompt.md` + `.claude/memory/CONTEXT.md` | Session start |
| **L3: Project** | `projects/X/JOURNAL.md` | When working on project X |
| **L4: Reference** | Any other docs, snapshots | On-demand |

### Key principles

- **Each project = one JOURNAL.md** — single source of truth for tasks, decisions, status
- **Decisions live inline with tasks** in JOURNAL, not in separate files
- **next-session-prompt = pointers** to journals (5-7 lines per project, not full history)
- **Rules = stable behavior**, not volatile data (counts, statuses go in journals)
- **Memory = verified cross-session patterns** managed in `.claude/memory/MEMORY.md`

## Skills

After setup, three skills are installed at `~/.claude/skills/`. They are available in every project.

| Skill | Path | What it does | When to use |
|-------|------|-------------|-------------|
| **Gemini** | `~/.claude/skills/gemini/` | Second opinions from Google Gemini (different model family = different blind spots) | Fact-check, prompt stress-test, hypothesis falsification, architecture review |
| **Brainstorm** | `~/.claude/skills/brainstorm/` | 3-round Claude x Gemini adversarial dialogue. Diverge → Deepen → Converge. | Multiple viable paths, strategic decisions, need to converge on one action |
| **Design** | `~/.claude/skills/design/` | Design system lifecycle: extract → palette → tokens → CSS → audit → VQA | Creating/auditing design systems, visual QA, token management |

### How to invoke

```bash
# Gemini — quick question
python3 ~/.claude/skills/gemini/gemini.py ask "your question"

# Gemini — second opinion (deeper analysis)
python3 ~/.claude/skills/gemini/gemini.py second-opinion "question" --context "context"

# Brainstorm and Design — see their SKILL.md for full CLI reference
```

**Prerequisites (must be installed for skills to work):**
- `pip install google-genai` — required for Gemini and Brainstorm
- `GOOGLE_API_KEY` in `.env` — required for Gemini and Brainstorm
- Before calling: `set -a && source .env && set +a`

**Decision rule:** One clear path + need validation → Gemini `second-opinion`. Multiple viable paths + need to converge → Brainstorm.

See `.claude/rules/gemini.md` for detailed usage rules (auto-loaded every session).

## Memory System

Three files in `.claude/memory/` work together to preserve context across sessions:

| File | Purpose | When to update |
|------|---------|----------------|
| **MEMORY.md** | Long-term patterns, decisions, lessons learned | After significant insight or user correction |
| **CONTEXT.md** | Quick orientation — active project, source of truth pointers | Start/end of session |
| **snapshots/** | Session summaries (backup if context compresses) | End of session |

### MEMORY.md — What to save

- Patterns confirmed across multiple sessions (bug traps, conventions)
- Key architectural decisions and file paths
- User preferences for workflow and communication
- Solutions to recurring problems

### MEMORY.md — What NOT to save

- Session-specific details (current task, temporary state)
- Unverified assumptions from reading a single file
- Anything already in CLAUDE.md or rules/

### CONTEXT.md — Quick orientation

Update at session start and end. Contains:
- Pointers to source-of-truth files
- Currently active project name
- Paused tracks (so you don't forget them)

### Snapshots — Session backup

At session end, write a snapshot to `.claude/memory/snapshots/YYYY-MM-DD-projectname-NNN.md` (max 50 lines). Include: summary, key files changed, decisions made, next steps. This protects against context loss if conversation history compresses.

## System Evolution

After significant work — update relevant files:
- **Behavioral rule** → `.claude/rules/*.md`
- **Task/decision** → `projects/X/JOURNAL.md` (inline with the task)
- **What to do next** → `context/next-session-prompt.md` (your project section only)
- **Learned pattern** → `.claude/memory/MEMORY.md`
- **Active project changed** → `.claude/memory/CONTEXT.md`

## Adding a New Project

1. Create `projects/new-project/JOURNAL.md` (copy the template from `my-first-project`)
2. Add a `<!-- PROJECT:new-project -->` section in `context/next-session-prompt.md` before `<!-- SHARED -->`
3. Optionally add `.claude/rules/new-project.md` with domain-specific rules (use `paths:` frontmatter to scope)

## Rules

`.claude/rules/` contains domain-specific rules that auto-load. Rules without `paths:` frontmatter load globally (every session). Rules with `paths:` load only when working on matching files.

- `gemini.md` — loaded globally, controls when/how to use Gemini skill
- `example-domain.md` — scoped to `projects/my-first-project/`, delete and replace with your own

## Communication

- **Language:** [Your preferred language]
- **Tone:** Direct, practical
- **Format:** Tables for comparison, options with trade-offs
