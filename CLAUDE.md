<!-- SETUP:START — Agent deletes this entire section (from SETUP:START to SETUP:END) after completing first run setup -->
## First Run Setup

**You are reading this for the first time. Complete ALL steps in order, then delete this section.**

The setup has two phases: **Onboarding** (learn about the user) and **Configuration** (adapt the system).

---

### Phase 1: Onboarding

**Use `AskUserQuestion` to gather project context.** Do NOT skip this — the answers personalize the entire system.

**Question batch 1 (4 questions):**

1. **"What is your project name?"** (header: "Project")
   - Options: "My App", "My SaaS", "My Website" + Other (user types their own)
   - Description for each: just the label, user will likely type their own

2. **"What is your name?"** (header: "Owner")
   - Options: use 2 placeholder options + Other
   - User will type their own name

3. **"What language should I use for all communication?"** (header: "Language")
   - Options: "English", "Russian", "Ukrainian", "Spanish" + Other
   - Description: "I'll use this language for all responses, comments, and documentation"

4. **"Describe your project in 1-2 sentences"** (header: "Description")
   - Options: "Web application", "API / Backend service", "CLI tool", "Mobile app" + Other
   - Description: "Brief description helps me understand context for decisions"

**Question batch 2 (2 questions):**

5. **"Do you want to install Gemini skill for second opinions from Google AI?"** (header: "Gemini")
   - Options:
     - "Yes, install (Recommended)" — "Gives you second opinions from a different AI model. Requires: pip install google-genai + GOOGLE_API_KEY"
     - "No, skip for now" — "You can install it later anytime"

6. **"Do you have an existing project to import, or starting fresh?"** (header: "Start mode")
   - Options:
     - "Starting fresh" — "I'll create your first project structure"
     - "I have existing code" — "Point me to your codebase and I'll set up the project around it"

---

### Phase 2: Configuration

Execute these steps using the answers from Phase 1.

#### Step 1: Initialize git

If this directory is not a git repo yet, run `git init` and create initial commit with all files (so scaffolding is preserved in history).

#### Step 2: Global settings

Check if `~/.claude/CLAUDE.md` exists:
- **If it does NOT exist** — copy `global/CLAUDE.md` to `~/.claude/CLAUDE.md`
- **If it exists** — skip (don't overwrite the user's existing settings)

#### Step 3: Install global skills and rules

**Skills** — copy from `global/skills/` to `~/.claude/skills/`:
- For each skill directory in `global/skills/`:
  - **If `~/.claude/skills/<name>/` does NOT exist** — copy the entire skill directory
  - **If it exists** — skip (don't overwrite existing skills)
- If user answered "No" to Gemini in Q5 — still copy the skill files (no harm), but note it's not configured yet

**Rules** — copy from `global/rules/` to `.claude/rules/` (project-level):
- For each rule file in `global/rules/`:
  - Copy to `.claude/rules/` (these are project-specific, not global)

#### Step 4: Personalize CLAUDE.md

Using answers from Phase 1, replace ALL placeholders in this file (below the SETUP:END marker):

- `[PROJECT NAME — replace this]` -> user's project name (Q1)
- `[YOUR NAME]` -> user's name (Q2)
- `[DATE]` -> today's date
- `[Brief description of what this project is about. 2-3 sentences max.]` -> user's description (Q4)
- `[Your preferred language]` -> user's language choice (Q3)

#### Step 5: Create first real project

Using the project name from Q1 (kebab-case):

1. Create `projects/{project-name}/JOURNAL.md` with a clean template:
   ```markdown
   # {Project Name} — Journal

   **Last updated:** {today}
   **Source of truth:** This file for all tasks, decisions, and status

   ---

   ## Statuses
   - `TODO` — in queue, not started
   - `IN PROGRESS` — active work
   - `DONE` — completed
   - `BLOCKED` — waiting for external input

   ---

   ## Active Tasks

   > Add your first task here. Example:
   > ### T-001: [Task name]
   > **Status:** TODO
   > **Priority:** P0
   > [What needs to be done]

   ---

   ## Completed

   - **T-000** ({today}): [Project setup] — starter kit configured

   ---

   **Maintained by:** Claude Code agent
   ```

2. Update `context/next-session-prompt.md` — replace ALL example content with:
   ```markdown
   # Next Session Prompt

   **Updated:** {today}
   **Session:** 1

   > **Rule:** Each project section is wrapped in `<!-- PROJECT:name -->` / `<!-- /PROJECT:name -->` tags.

   ---

   <!-- PROJECT:{project-name} -->
   ## {Project Name}

   **Journal:** `projects/{project-name}/JOURNAL.md`

   **Last session:** Initial setup complete.

   ### IMMEDIATE NEXT
   1. Define first tasks in JOURNAL.md
   2. Start working on the project
   <!-- /PROJECT:{project-name} -->

   ---

   <!-- SHARED -->
   ## Shared Context

   [Cross-project information goes here]
   <!-- /SHARED -->
   ```

3. Update `.claude/memory/CONTEXT.md`:
   ```markdown
   # Project Context

   > Pointer layer. Quick orientation for session start.

   ## Source of Truth
   - **Tasks & decisions:** `projects/{project-name}/JOURNAL.md`
   - **Experiments:** `experiments/README.md`
   - **Next actions:** `context/next-session-prompt.md`
   - **Long-term memory:** `.claude/memory/MEMORY.md`

   ## Active Project
   {project-name}

   ## Paused Tracks
   [Nothing paused yet]
   ```

#### Step 6: Set up .env (if Gemini selected)

If user answered "Yes" to Q5:
1. Check if `.env` exists — if not, create it
2. Ask user: "Paste your Google API key (GOOGLE_API_KEY) or type 'skip' to set it up later"
3. If provided, add `GOOGLE_API_KEY={key}` to `.env`
4. Add `.env` to `.gitignore` if not already there
5. Run `pip install google-genai` (or note it as a prerequisite)

#### Step 7: Verify hooks

Make hooks executable:
```bash
chmod +x .claude/hooks/session-start.sh .claude/hooks/pre-compact.sh
```

#### Step 8: Clean up ALL scaffolding

Delete these files/directories (they were only needed for setup and GitHub repo):
- `global/` directory (entire folder — skills already copied)
- `README.md` (GitHub repo readme, not needed locally)
- `.github/` directory (repo images, not needed locally)
- `projects/example-webapp/` (demo project)
- `projects/example-saas/` (demo project)
- `experiments/001-landing-page-redesign.md` (demo experiment)
- `experiments/002-payment-provider-selection.md` (demo experiment)
- `.claude/rules/example-domain.md` (demo rule)

Keep:
- `experiments/README.md` (explains how experiments work — still useful)
- `.claude/memory/` (already personalized in Step 5)
- `.claude/hooks/` (configured)
- `.claude/settings.json` (configured)

Commit: `git commit -am "setup: personalized project, removed scaffolding"`

#### Step 9: Remove this section

Delete everything between `<!-- SETUP:START -->` and `<!-- SETUP:END -->` markers (inclusive) from this file.

Commit: `git commit -am "setup: remove first-run instructions"`

#### Step 10: Greet the user

Tell the user in their chosen language:

"Setup complete. Here's your project:"
- Project: {name} — `projects/{project-name}/JOURNAL.md`
- Memory: `.claude/memory/` — I'll save patterns across sessions
- Experiments: `experiments/` — for research before building
- Skills installed: {list with prerequisites status}
- Hooks: session-start (auto-loads context) + pre-compact (saves before compression)

"To start working, just tell me what you want to build. I'll create tasks in your journal and track progress."

If user selected "I have existing code" in Q6, add:
"Point me to your codebase and I'll analyze the structure, then set up appropriate rules and initial tasks."
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
4. If user asks about a specific project -> read that project's `JOURNAL.md`

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
4. **Cross-project data** -> update in `<!-- SHARED -->` section only.
5. **Header** (date, session number) -> last writer wins, acceptable.

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
| **L4: Reference** | Experiments, snapshots, any other docs | On-demand |

### Key principles

- **Each project = one JOURNAL.md** — single source of truth for tasks, decisions, status
- **Decisions live inline with tasks** in JOURNAL, not in separate files
- **next-session-prompt = pointers** to journals (5-7 lines per project, not full history)
- **Rules = stable behavior**, not volatile data (counts, statuses go in journals)
- **Memory = verified cross-session patterns** managed in `.claude/memory/MEMORY.md`

## Experiments

The `experiments/` folder holds structured research for decisions that need investigation before implementation. Unlike tasks in JOURNAL.md (clear path, just build it), experiments are for questions with multiple possible answers.

**Lifecycle:**
```
IDENTIFY -> RESEARCH -> HYPOTHESIZE -> PLAN -> IMPLEMENT -> EVALUATE -> DECIDE (GO/NO-GO)
```

**Rules:**
1. One experiment = one focused question
2. Starts with IDENTIFY (problem, current state, target, gap)
3. Ends with DECIDE — GO/NO-GO with clear reasoning
4. After DECIDE(GO), create implementation tasks in the relevant project's JOURNAL.md
5. Index: `experiments/README.md` — keep the Active Experiments table updated

**Naming:** `NNN-short-description.md` (sequential number + kebab-case)

**When to use experiments vs tasks:**
- Unknown path, multiple options -> experiment
- Clear path, just build it -> task in JOURNAL.md

### Example files (delete when ready)

The kit includes two demo experiments to show the system in action:
- `experiments/001-landing-page-redesign.md` — completed experiment (full cycle through DECIDE)
- `experiments/002-payment-provider-selection.md` — in-progress experiment (RESEARCH phase)

These are **not real projects**. They demonstrate how experiments, journals, and the session prompt work together. Delete them when you create your first real experiment.

## Projects

Projects live in `projects/`. Each project has a `JOURNAL.md` — the single source of truth for tasks, decisions, and status.

### Example projects (delete when ready)

Two demo projects are included:
- `projects/example-webapp/` — Recipe Sharing App (Next.js, shows active tasks and decisions)
- `projects/example-saas/` — Invoice Automation API (FastAPI, shows blocked tasks and completed work)

These are **not real projects**. Delete both folders when you create your first real project.

## Adding a New Project

1. Create `projects/new-project/JOURNAL.md` (copy the template from any example project)
2. Add a `<!-- PROJECT:new-project -->` section in `context/next-session-prompt.md` before `<!-- SHARED -->`
3. Optionally add `.claude/rules/new-project.md` with domain-specific rules (use `paths:` frontmatter to scope)

## Skills

After setup, three skills are installed at `~/.claude/skills/`. They are available in every project.

| Skill | Path | What it does | When to use |
|-------|------|-------------|-------------|
| **Gemini** | `~/.claude/skills/gemini/` | Second opinions from Google Gemini (different model family = different blind spots) | Fact-check, prompt stress-test, hypothesis falsification, architecture review |
| **Brainstorm** | `~/.claude/skills/brainstorm/` | 3-round Claude x Gemini adversarial dialogue. Diverge -> Deepen -> Converge. | Multiple viable paths, strategic decisions, need to converge on one action |
| **Design** | `~/.claude/skills/design/` | Design system lifecycle: extract -> palette -> tokens -> CSS -> audit -> VQA | Creating/auditing design systems, visual QA, token management |

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

**Decision rule:** One clear path + need validation -> Gemini `second-opinion`. Multiple viable paths + need to converge -> Brainstorm.

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
- **Behavioral rule** -> `.claude/rules/*.md`
- **Task/decision** -> `projects/X/JOURNAL.md` (inline with the task)
- **What to do next** -> `context/next-session-prompt.md` (your project section only)
- **Learned pattern** -> `.claude/memory/MEMORY.md`
- **Active project changed** -> `.claude/memory/CONTEXT.md`
- **New experiment** -> `experiments/NNN-description.md` + update `experiments/README.md`

## Rules

`.claude/rules/` contains domain-specific rules that auto-load. Rules without `paths:` frontmatter load globally (every session). Rules with `paths:` load only when working on matching files.

- `gemini.md` — loaded globally, controls when/how to use Gemini skill
- `example-domain.md` — scoped to `projects/example-*/` and `experiments/`, delete and replace with your own

## Communication

- **Language:** [Your preferred language]
- **Tone:** Direct, practical
- **Format:** Tables for comparison, options with trade-offs
