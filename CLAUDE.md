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

**Question batch 2 (1 question):**

5. **"Do you have an existing project to import, or starting fresh?"** (header: "Start mode")
   - Options:
     - "Starting fresh" — "I'll create your first project structure"
     - "I have existing code" — "Point me to your codebase and I'll set up the project around it"

---

### Phase 2: Configuration

Execute these steps using the answers from Phase 1.

#### Step 1: Initialize git

If this directory is not a git repo yet, run `git init` and create initial commit with all files (so scaffolding is preserved in history).

#### Step 2: Personalize CLAUDE.md

Using answers from Phase 1, replace ALL placeholders in this file (below the SETUP:END marker):

- `[PROJECT NAME — replace this]` -> user's project name (Q1)
- `[YOUR NAME]` -> user's name (Q2)
- `[DATE]` -> today's date
- `[Brief description of what this project is about. 2-3 sentences max.]` -> user's description (Q4)
- `[Your preferred language]` -> user's language choice (Q3)

#### Step 3: Create first real project

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

#### Step 4: Verify hooks

Make hooks executable:
```bash
chmod +x .claude/hooks/session-start.sh .claude/hooks/pre-compact.sh .claude/hooks/periodic-save.sh
```

#### Step 5: Clean up ALL scaffolding

Delete these files/directories (they were only needed for setup and GitHub repo):
- `README.md` (GitHub repo readme, not needed locally)
- `.github/` directory (repo images, not needed locally)
- `projects/example-webapp/` (demo project)
- `projects/example-saas/` (demo project)
- `experiments/001-landing-page-redesign/` (demo experiment)
- `experiments/002-payment-provider-selection/` (demo experiment)

Keep:
- `experiments/README.md` (explains how experiments work — still useful)
- `.claude/memory/` (already personalized)
- `.claude/hooks/` (configured)
- `.claude/settings.json` (configured)

Commit: `git commit -am "setup: personalized project, removed scaffolding"`

#### Step 6: Remove this section

Delete everything between `<!-- SETUP:START -->` and `<!-- SETUP:END -->` markers (inclusive) from this file.

Commit: `git commit -am "setup: remove first-run instructions"`

#### Step 7: Greet the user

Tell the user in their chosen language:

"Setup complete. Here's your project:"
- Project: {name} — `projects/{project-name}/JOURNAL.md`
- Memory: `.claude/memory/` — I'll save patterns across sessions
- Experiments: `experiments/` — for research before building
- Hooks: session-start (context overview) + pre-compact (blocks until saved) + periodic-save (checkpoint every 15 exchanges)

"To start working, just tell me what you want to build. I'll create tasks in your journal and track progress."

If user selected "I have existing code" in Q5, add:
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
2. `.claude/memory/MEMORY.md` is auto-loaded (patterns from past sessions)
3. If user asks about a specific project -> read that project's `JOURNAL.md`
4. If working on specific area -> read relevant `.claude/memory/topics/*.md`

**During:** Work on tasks. Update project JOURNAL.md after completing work.

**End — Context Save Protocol:**

Triggers: user says "save context" / "update context", session is ending, or hook blocks you.

Execute ALL 3 steps in order:

1. **MEMORY.md** — add new verified patterns (with `[YYYY-MM]` date). Keep < 200 lines. If a theme grows > 5 entries → create topic file.
2. **next-session-prompt.md** — update ONLY your `<!-- PROJECT:name -->` section: what was done, key decisions, `### IMMEDIATE NEXT` (exact first steps for next session).
3. **JOURNAL.md** — update task statuses if any active tasks.

**Definition of Done (all must be true):**
- [ ] MEMORY.md has new patterns from this session (or explicitly "no new patterns")
- [ ] Each new MEMORY.md entry has `[YYYY-MM]` date tag
- [ ] Your project section in next-session-prompt.md has `### IMMEDIATE NEXT` with 3+ concrete steps
- [ ] JOURNAL.md task statuses reflect current reality (not stale from session start)
- [ ] No unsaved decisions — if you made a choice during the session, it's recorded somewhere

**Before /compact (MANDATORY):**
The `pre-compact.sh` hook BLOCKS compaction until MEMORY.md is updated (mtime check). Execute steps 1-3 above — compaction proceeds only after files are saved.

**Periodic save:** The `periodic-save.sh` hook blocks every 15 exchanges to checkpoint progress. Same 3 steps, same Definition of Done.

### Multi-Project Safety

When the user has multiple projects, each project gets its own `<!-- PROJECT:name -->` section in `next-session-prompt.md`. Multiple Claude Code windows may run in parallel on different projects.

**Critical rules:**
- **next-session-prompt.md** — ONLY edit within your project's `<!-- PROJECT:name -->` / `<!-- /PROJECT:name -->` tags. Another window may be editing a different project section at the same time.
- **MEMORY.md** — shared across all projects. Write patterns that apply broadly. Tag project-specific patterns: `[Project: name]`.
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
| **L1: Auto** | This file + `.claude/rules/` + `.claude/memory/MEMORY.md` (index, < 200 lines) | Every session |
| **L2: Start** | `context/next-session-prompt.md` | Session start |
| **L3: Project** | `projects/X/JOURNAL.md` | When working on project X |
| **L4: Topics** | `.claude/memory/topics/*.md` | On-demand (when working on specific area) |
| **Sandbox** | `experiments/NNN-*/` | On-demand (isolated research) |

### Key principles

- **Each project = one JOURNAL.md** — single source of truth for tasks, decisions, status
- **Decisions live inline with tasks** in JOURNAL, not in separate files
- **next-session-prompt = pointers** to journals (5-7 lines per project, not full history)
- **Rules = stable behavior**, not volatile data (counts, statuses go in journals)
- **Memory = verified cross-session patterns** managed in `.claude/memory/MEMORY.md`

## Experiments (Sandbox)

The `experiments/` folder is an isolated sandbox for research, prototyping, and validation — outside the main project flow. Unlike tasks in JOURNAL.md (clear path, just build it), experiments are for questions that need investigation before committing.

An experiment can serve one project, multiple projects, or the system itself.

### Structure

Every experiment = a folder (never a single file):

```
experiments/
├── README.md                    ← Index of all experiments + rules
└── NNN-short-description/       ← Each experiment = own folder
    ├── EXPERIMENT.md            ← Required: context, status, findings
    └── (anything else needed)   ← phases/, prototypes/, data/, code/
```

**EXPERIMENT.md** is the only required file. Everything else grows as the experiment demands — phase files, prototypes, test data, research notes, code.

### EXPERIMENT.md Template

```markdown
# Experiment NNN: [Title]

**Status:** IDENTIFY | RESEARCH | HYPOTHESIZE | PLAN | IMPLEMENT | EVALUATE | DECIDE
**Created:** [date]
**Project:** [project name] or "system" if not project-specific

## Problem
What question are we answering? What gap exists?

## Current State
What do we know now?

## Target
What does success look like?

## Findings
(Updated as experiment progresses)

## Decision
GO / NO-GO / ITERATE — with reasoning.
If GO: what tasks to create in which JOURNAL, what patterns to save to MEMORY.md.
```

### Lifecycle

```
IDENTIFY → RESEARCH → HYPOTHESIZE → PLAN → IMPLEMENT → EVALUATE → DECIDE
```

Not every experiment needs all phases. A quick PoC can go IDENTIFY → IMPLEMENT → DECIDE.

### Rules

1. **Always a folder** — `experiments/NNN-description/` with EXPERIMENT.md inside
2. **Sandbox isolation** — experiment code/data stays in the experiment folder, not in project dirs
3. **One experiment = one focused question** — don't mix unrelated investigations
4. **Port results, not files** — after DECIDE(GO), create tasks in JOURNAL.md and patterns in MEMORY.md. Don't move experiment files into the project.
5. **Index** — keep `experiments/README.md` Active Experiments table updated

**Naming:** `NNN-short-description/` (sequential number + kebab-case)

**When to use experiments vs tasks:**
- Unknown path, multiple options, need to research → experiment
- Clear path, just build it → task in JOURNAL.md

### Example experiments (delete when ready)

- `experiments/001-landing-page-redesign/` — completed experiment (full cycle through DECIDE)
- `experiments/002-payment-provider-selection/` — in-progress experiment (RESEARCH phase)

These are demos. Delete them when you create your first real experiment.

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

## Memory System (Tier-based)

Two tiers preserve context across sessions:

| Tier | File | Loaded | Size limit |
|------|------|--------|-----------|
| **Index** | `.claude/memory/MEMORY.md` | Every session (auto) | **< 200 lines** (Anthropic limit — content beyond 200 lines is truncated) |
| **Topics** | `.claude/memory/topics/*.md` | On-demand (when needed) | No limit |

### MEMORY.md (Index) — What goes here

- One-line patterns confirmed across multiple sessions
- User preferences for workflow and communication
- Key architectural decisions (one line each)
- Failed approaches table (so you don't repeat mistakes)
- **Topic Files table** — index of what's in `topics/` and when to read each file

### Temporal Facts

Every entry in MEMORY.md MUST include a date tag:

```markdown
- **Pattern name** [2026-03] — description
- ~~**Old pattern** [2025-11 → 2026-02]~~ — superseded by X
```

- `[YYYY-MM]` = when first confirmed
- `[YYYY-MM → YYYY-MM]` = temporal range (superseded facts)
- Strikethrough `~~` = invalidated entry (keep for history, prevents re-learning)

### Memory Entry Quality

Before writing to MEMORY.md, self-check every entry:
1. **Dated** — has `[YYYY-MM]`? If no → add it
2. **Specific** — "always use parameterized queries" > "be careful with SQL"
3. **Actionable** — changes your future behavior, not just states a fact
4. **Not duplicate** — scan existing entries, update if exists
5. **One line** — needs more? → topic file

### MEMORY.md — What does NOT go here

- Session-specific details (current task, temporary state)
- Detailed knowledge on a single topic (move to `topics/`)
- Anything already in CLAUDE.md or rules/

### Topic Files — Detailed knowledge

When a theme in MEMORY.md grows beyond 5-10 entries, move details to `.claude/memory/topics/{name}.md`. Keep a one-line summary + table entry in MEMORY.md. Claude reads topic files on-demand — they don't consume context every session.

```
.claude/memory/
├── MEMORY.md              ← Index (< 200 lines, loaded every session)
└── topics/
    ├── api.md             ← Example: API conventions, endpoints, auth
    ├── database.md        ← Example: Schema decisions, migration patterns
    └── deployment.md      ← Example: CI/CD, hosting, env variables
```

## System Evolution

After significant work — update relevant files:
- **Behavioral rule** -> `.claude/rules/*.md`
- **Task/decision** -> `projects/X/JOURNAL.md` (inline with the task)
- **What to do next** -> `context/next-session-prompt.md` (your project section only)
- **Learned pattern** -> `.claude/memory/MEMORY.md` (index, < 200 lines)
- **Detailed knowledge** -> `.claude/memory/topics/*.md` (on-demand, no size limit)
- **New experiment** -> `experiments/NNN-description/EXPERIMENT.md` + update `experiments/README.md`

## Rules

`.claude/rules/` contains domain-specific rules that auto-load. Rules without `paths:` frontmatter load globally (every session). Rules with `paths:` load only when working on matching files.

Create your own rules as needed. Example: `api-conventions.md` for API patterns, `testing.md` for test requirements.

## Communication

- **Language:** [Your preferred language]
- **Tone:** Direct, practical
- **Format:** Tables for comparison, options with trade-offs
