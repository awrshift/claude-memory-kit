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

1. Create `projects/{project-name}/BACKLOG.md` with a clean template:
   ```markdown
   # {Project Name} — Backlog

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

   **Backlog:** `projects/{project-name}/BACKLOG.md`

   **Last session:** Initial setup complete.

   ### IMMEDIATE NEXT
   1. Define first tasks in BACKLOG.md
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
chmod +x .claude/hooks/session-start.py .claude/hooks/pre-compact.sh .claude/hooks/periodic-save.sh .claude/hooks/session-end.sh .claude/hooks/protect-tests.sh
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
- Project: {name} — `projects/{project-name}/BACKLOG.md`
- Memory: `.claude/memory/` — I'll save patterns across sessions
- Experiments: `experiments/` — for research before building
- Hooks: session-start.py (injects index.md + recent daily into every session via `additionalContext`) + pre-compact (blocks until saved) + periodic-save (checkpoint every 50 exchanges) + session-end (auto-flush transcripts to daily/, triggers end-of-day compile after 18:00) + protect-tests (blocks edits to existing test files)
- Memory Kit v3 pipeline: `.claude/memory/scripts/` — compile, lint, query, flush (opt-in, Python stdlib only)
- Slash commands: `/memory-compile`, `/memory-lint`, `/memory-query`

"To start working, just tell me what you want to build. I'll create tasks in your backlog and track progress."

If user selected "I have existing code" in Q5, add:
"Point me to your codebase and I'll analyze the structure, then set up appropriate rules and initial tasks."
<!-- SETUP:END -->

See @README.md for project overview and quick start.

## Project Overview

**Project:** [PROJECT NAME — replace this]
**Owner:** [YOUR NAME]
**Started:** [DATE]

[Brief description of what this project is about. 2-3 sentences max.]

## Session Workflow

**Start:**
1. `.claude/hooks/session-start.py` fires automatically and injects context into your session (see "SessionStart Injection" below). You see session stats, knowledge index, and recent daily logs as `additionalContext`.
2. Read `context/next-session-prompt.md` — find your `<!-- PROJECT:name -->` section.
3. `.claude/memory/MEMORY.md` is auto-loaded (patterns from past sessions).
4. If user asks about a specific project → read that project's `BACKLOG.md`.
5. If working on specific area → read relevant `knowledge/` articles via `index.md` (already injected at start).

**During:** Work on tasks. Update project BACKLOG.md after completing work.

**End — Context Save Protocol:**

Triggers: user says "save context" / "update context", session is ending, or hook blocks you.

Execute ALL 3 steps in order:

1. **MEMORY.md** — add new verified patterns (with `[YYYY-MM]` date). Keep < 200 lines. If a theme grows > 5 entries → write a knowledge article in `knowledge/concepts/{slug}.md`.
2. **next-session-prompt.md** — update ONLY your `<!-- PROJECT:name -->` section: what was done, key decisions, `### IMMEDIATE NEXT` (exact first steps for next session).
3. **BACKLOG.md** — update task statuses if any active tasks.

**Definition of Done (all must be true):**
- [ ] MEMORY.md has new patterns from this session (or explicitly "no new patterns")
- [ ] Each new MEMORY.md entry has `[YYYY-MM]` date tag
- [ ] Your project section in next-session-prompt.md has `### IMMEDIATE NEXT` with 3+ concrete steps
- [ ] BACKLOG.md task statuses reflect current reality (not stale from session start)
- [ ] No unsaved decisions — if you made a choice during the session, it's recorded somewhere

**Before /compact (MANDATORY):**
The `pre-compact.sh` hook BLOCKS compaction until MEMORY.md is updated (mtime check). Execute steps 1-3 above — compaction proceeds only after files are saved.

**Periodic save:** The `periodic-save.sh` hook blocks every 50 exchanges (configurable via `CLAUDE_SAVE_INTERVAL`) to checkpoint progress. Same 3 steps, same Definition of Done.

**Auto session-end flush:** The `session-end.sh` hook fires when the Claude Code process terminates. It extracts the last 100 turns / 50KB from the transcript and spawns `.claude/memory/scripts/flush.py` in background — uses `claude -p` (subscription, zero cost) to distill the session into structured markdown, appended to `daily/YYYY-MM-DD.md`. Completely transparent, logs to `.claude/state/flush.log`.

**End-of-day auto-compile:** After 18:00 local time (configurable via `CMK_COMPILE_AFTER_HOUR`), `flush.py` checks if today's `daily/YYYY-MM-DD.md` has changed since its last successful compile (hash comparison). If yes, it spawns `compile.py` as a detached background process — transforms raw daily logs into structured `knowledge/` wiki articles without manual intervention. Manual override available via `/memory-compile` slash command.

### SessionStart Injection (v3)

When a session starts, `.claude/hooks/session-start.py` prints a JSON object to stdout:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "..."
  }
}
```

Claude Code injects `additionalContext` into the agent's initial context. Content (in priority order):

1. **Session stats** — session counter, MEMORY.md capacity + staleness, projects with task counts, experiments with status, git branch + short status
2. **`knowledge/index.md`** — full master catalog so agent knows what articles exist
3. **Recent daily logs** — last 1-2 `daily/YYYY-MM-DD.md` entries for session-recency context
4. **Top recent concepts** — 3 most recently-modified articles from `knowledge/concepts/`

**Budget:** 50K chars default (configurable via `CMK_INJECT_BUDGET` env var). On Opus 4.6 1M-window this is ~1% usage — safe to inject aggressively.

This pattern is inspired by Cole Medin's `claude-memory-compiler` (Karpathy's LLM knowledge base architecture). The key value: agent always "sees" the knowledge base catalog without needing explicit `/memory` queries.

### End-of-day Auto-Compile (v3)

`flush.py` includes `maybe_trigger_compilation()` which checks if it's past `COMPILE_AFTER_HOUR` (default 18) local time and if today's daily log has unsaved changes. If both true, it spawns `compile.py` detached. This runs at most once per day per unique daily log state (SHA-256 hash skip).

Manual override: `/memory-compile` slash command (or `python3 .claude/memory/scripts/compile.py`).

Configure:
- `CMK_COMPILE_AFTER_HOUR=18` — hour threshold (0-23)
- Logs: `.claude/state/flush.log` + `.claude/state/compile.log`

### CLAUDE_INVOKED_BY — recursion guard (critical)

`flush.py` and `compile.py` spawn `claude -p` subprocesses. Each subprocess starts a new Claude Code session, which fires the SessionEnd hook → spawns another `flush.py` → infinite loop.

The guard: `flush.py` sets `os.environ["CLAUDE_INVOKED_BY"] = "memory_flush"` at the top of the file. `session-end.sh` (and any hook that spawns memory scripts) checks this env var at the top:

```bash
if [[ -n "${CLAUDE_INVOKED_BY:-}" ]]; then
    exit 0
fi
```

This short-circuits nested hook firing. The env var propagates through `subprocess.Popen` because we pass `env={k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}` + explicit `env["CLAUDE_INVOKED_BY"] = "memory_flush"`.

**IMPORTANT:** any future hook that spawns `claude -p` MUST propagate this guard, otherwise recursion is guaranteed.

### Multi-Project Safety

When the user has multiple projects, each project gets its own `<!-- PROJECT:name -->` section in `next-session-prompt.md`. Multiple Claude Code windows may run in parallel on different projects.

**Critical rules:**
- **next-session-prompt.md** — ONLY edit within your project's `<!-- PROJECT:name -->` / `<!-- /PROJECT:name -->` tags. Another window may be editing a different project section at the same time.
- **MEMORY.md** — shared across all projects. Write patterns that apply broadly. Tag project-specific patterns: `[Project: name]`.
- **BACKLOG.md** — each project has its own. No conflicts possible (one file per project).

### next-session-prompt.md — How It Works

This file is the **cross-project hub**. It uses `<!-- PROJECT:name -->` / `<!-- /PROJECT:name -->` tags so multiple sessions can work in parallel without overwriting each other.

**Rules:**
1. **Only edit your project's section.** Use Edit tool scoped within your project tags.
2. **Never touch other projects' sections.** Another session may be updating them.
3. **New project?** Append a new `<!-- PROJECT:name -->` block before `<!-- SHARED -->`.
4. **Cross-project data** -> update in `<!-- SHARED -->` section only.
5. **Header** (date, session number) -> last writer wins, acceptable.

**What goes in each project section (max 5-7 lines):**
- Pointer to project BACKLOG.md (source of truth)
- What was done (key files, decisions)
- `### IMMEDIATE NEXT` — exact first steps after restart
- Any urgent deadlines or pending actions

**What does NOT go here:**
- Full task lists (those live in BACKLOG.md)
- Session history or detailed notes
- Decision rationale (inline in BACKLOG tasks)

## Context Architecture

| Layer | Files | When loaded |
|-------|-------|-------------|
| **L1: Auto** | This file + `.claude/rules/` + `.claude/memory/MEMORY.md` (index, < 200 lines) + **SessionStart injection** (index.md + recent daily logs + top concepts, ~50K budget) | Every session |
| **L2: Start** | `context/next-session-prompt.md` | Session start (read explicitly) |
| **L3: Project** | `projects/X/BACKLOG.md` | When working on project X |
| **L4: Knowledge wiki** | `knowledge/{concepts,connections,meetings}/*.md` | On-demand via `index.md` (already injected at L1) |
| **L5: Daily logs** | `daily/YYYY-MM-DD.md` | Raw source, auto-captured by `session-end.sh` |
| **Sandbox** | `experiments/NNN-*/` | On-demand (isolated research) |

### Key principles

- **BACKLOG = task queue** (what to do). **daily/ = chronological log** (what happened). Two distinct files with different semantics.
- **Each project = one BACKLOG.md** — single source of truth for tasks, decisions, status
- **Decisions live inline with tasks** in BACKLOG, not in separate ADR files
- **next-session-prompt = pointers** to backlogs (5-7 lines per project, not full history)
- **Rules = stable behavior**, not volatile data (counts, statuses go in backlogs)
- **Memory = verified cross-session patterns** managed in `.claude/memory/MEMORY.md`

## Experiments (Sandbox)

The `experiments/` folder is an isolated sandbox for research, prototyping, and validation — outside the main project flow. Unlike tasks in BACKLOG.md (clear path, just build it), experiments are for questions that need investigation before committing.

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
If GO: what tasks to create in which BACKLOG, what patterns to save to MEMORY.md.
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
4. **Port results, not files** — after DECIDE(GO), create tasks in BACKLOG.md and patterns in MEMORY.md. Don't move experiment files into the project.
5. **Index** — keep `experiments/README.md` Active Experiments table updated

**Naming:** `NNN-short-description/` (sequential number + kebab-case)

**When to use experiments vs tasks:**
- Unknown path, multiple options, need to research → experiment
- Clear path, just build it → task in BACKLOG.md

### Example experiments (delete when ready)

- `experiments/001-landing-page-redesign/` — completed experiment (full cycle through DECIDE)
- `experiments/002-payment-provider-selection/` — in-progress experiment (RESEARCH phase)

These are demos. Delete them when you create your first real experiment.

## Projects

Projects live in `projects/`. Each project has a `BACKLOG.md` — the single source of truth for tasks, decisions, and status.

### Example projects (delete when ready)

Two demo projects are included:
- `projects/example-webapp/` — Recipe Sharing App (Next.js, shows active tasks and decisions)
- `projects/example-saas/` — Invoice Automation API (FastAPI, shows blocked tasks and completed work)

These are **not real projects**. Delete both folders when you create your first real project.

## Adding a New Project

1. Create `projects/new-project/BACKLOG.md` (copy the template from any example project)
2. Add a `<!-- PROJECT:new-project -->` section in `context/next-session-prompt.md` before `<!-- SHARED -->`
3. Optionally add `.claude/rules/new-project.md` with domain-specific rules (scoping via `paths:` frontmatter is documented but not verified — treat rules as globally loaded by default)

## Memory System (Tier-based)

Two tiers preserve context across sessions:

| Tier | File | Loaded | Size guidance |
|------|------|--------|-----------|
| **Index** | `.claude/memory/MEMORY.md` | Every session (auto) | Hot cache — see Rotation Rule below. Content beyond 200 lines is truncated by Claude Code auto-load (session-start hook can inject more via `additionalContext`) |
| **Wiki** | `knowledge/{concepts,connections,meetings}/*.md` | Via SessionStart injection (index.md + top concepts) + on-demand reads | No limit |

The wiki uses plain Markdown with `[[wikilinks]]`. **Obsidian is optional** — it only provides a visual graph view. The wiki works in any Markdown editor (VS Code, Sublime, plain `cat`, GitHub web view). Scripts and pipeline are fully independent of Obsidian.

### MEMORY.md (Index) — What goes here

- One-line patterns confirmed across multiple sessions
- User preferences for workflow and communication
- Key architectural decisions (one line each)
- Failed approaches table (so you don't repeat mistakes)
- **Wiki Index pointer** — note to read `knowledge/index.md` for deep queries

### Temporal Facts

Every entry in MEMORY.md MUST include a date tag:

```markdown
- **Pattern name** [2026-03] — description
- ~~**Old pattern** [2025-11 → 2026-02]~~ — superseded by X
```

- `[YYYY-MM]` = when first confirmed
- `[YYYY-MM → YYYY-MM]` = temporal range (superseded facts)
- Strikethrough `~~` = invalidated entry (keep for history, prevents re-learning)

### MEMORY.md Rotation Rule

MEMORY.md is a **hot cache, not an archive.** SSOT discipline matters more than line count — 500 lines of clean short one-liners is fine; 200 lines with paragraph-long entries that duplicate wiki concepts is not.

**Rotation triggers** (any one is sufficient):
1. **Duplicate detected** — any entry whose topic already has a `knowledge/concepts/{topic}.md` article → replace with 1-line pointer immediately. **This is the #1 trigger.**
2. **Entry too long** — any single entry over ~200 characters (one short paragraph) → move detail to a concept, keep 1-line summary with link.
3. **Section overgrown** — if a section grows past ~15 related entries that aren't clean one-liners, split by theme and rotate duplicates.
4. **Stale entries** — patterns from completed projects, resolved issues, one-time migration details.

**Rotation steps:**
1. Identify target (duplicate OR too-long entry OR overgrown section OR stale)
2. Move content to `knowledge/concepts/{topic}.md` (create if needed, **merge** if exists — do not overwrite)
3. Replace in MEMORY.md with a short pointer: `- Topic summary. Details: knowledge/concepts/{topic}.md`
4. Update `knowledge/index.md` if the concept is new
5. Update MEMORY.md header `Last updated` line

**Before writing NEW entries, self-check:**
1. **Dated** — has `[YYYY-MM]`?
2. **Specific** — "always use parameterized queries" > "be careful with SQL"
3. **Not duplicate** — scan BOTH MEMORY.md AND wiki concepts first
4. **Concise** — under ~200 characters. If longer → write to `knowledge/concepts/` article and put a 1-line pointer here
5. **Right layer** — is this hot cache (accessed every session) or wiki (on-demand)?

**Architectural principle:** MEMORY.md = orchestration layer (role, methodology, active projects, universal patterns, pointers). Wiki = SSOT details. If a fact exists in both places, wiki wins and MEMORY.md must be updated to point at it.

**Anti-pattern to avoid:** paragraph-length entries that technically fit under a line count but violate the hot-cache principle. A 200-line MEMORY.md full of 2000-char "one-liners" is WORSE than a 500-line MEMORY.md full of real one-liners.

### MEMORY.md — What does NOT go here

- Session-specific details (current task, temporary state)
- Detailed knowledge on a single topic (move to `knowledge/concepts/X.md`)
- Anything already in CLAUDE.md or rules/
- Anything that duplicates an existing wiki concept

### Knowledge Wiki — Detailed knowledge

When a theme in MEMORY.md grows beyond 5-10 entries, write detailed articles in `knowledge/concepts/{name}.md`. Keep a one-line summary in MEMORY.md. Claude reads wiki articles on-demand — they don't consume context every session.

```
.claude/memory/
├── MEMORY.md              ← Index (< 200 lines, loaded every session)
├── scripts/               ← Memory Kit v3 pipeline (compile/lint/query/flush/config)
└── knowledge/             ← Wiki (on-demand, Obsidian-compatible)
    ├── index.md           ← Master catalog (injected at session start)
    ├── log.md             ← Append-only build log
    ├── concepts/          ← Single-topic deep dives
    ├── connections/       ← Cross-concept relationships
    └── meetings/          ← Meeting index articles
```

### Memory Kit v3 Scripts

Production pipeline for auto-compiling knowledge from daily logs. All scripts use Python stdlib only (no `pip install`) and call `claude -p` as a subprocess (uses your existing subscription, zero extra cost).

```bash
# Compile: daily/ → knowledge/ articles (incremental via SHA-256 hash)
python3 .claude/memory/scripts/compile.py
# Or via slash command:
/memory-compile

# Lint: 6 structural health checks on knowledge wiki
python3 .claude/memory/scripts/lint.py
python3 .claude/memory/scripts/lint.py --fix    # auto-add missing backlinks
/memory-lint

# Query: index-guided retrieval across the wiki
python3 .claude/memory/scripts/query.py "your question"
/memory-query "your question"

# Flush: called automatically by session-end.sh hook (background, detached)
# Do not call manually — hook handles it
# Auto-triggers compile.py after 18:00 local (Cole's end-of-day pattern)
```

**Pipeline flow:**
```
session-end.sh → flush.py (claude -p, Opus, 100 turns/50KB)
             → daily/YYYY-MM-DD.md
             → (if >18:00) spawns compile.py detached
             → compile.py → knowledge/*.md articles
             → session-start.py injects updated index.md + latest daily next session
```

## Working Artifacts (Screenshots, Temp Files)

**NEVER save screenshots, console logs, or ephemeral scratch files to the repo root.** All working artifacts go to `tmp/` (gitignored).

| Artifact Type | Destination | Notes |
|---------------|-------------|-------|
| Screenshots (any source) | `tmp/screenshots/` | Use descriptive names with date prefix if multi-session work |
| Experiment scratch files | `experiments/<name>/` | If part of a real experiment |
| One-off debug output | `tmp/` | Delete when done |

**Rules:**
- If your toolchain includes a browser automation or screenshot capture step, pass an explicit file path (typically a `filename` / `output_path` parameter) pointing at `tmp/screenshots/{descriptive-name}.png` — never bare filenames (which default to cwd = repo root).
- `.gitignore` has `/*.png` as a safety net — PNGs in repo root will be ignored by git, but **do not rely on it** — clean up the root.
- If a screenshot is referenced by a doc/article, move it to the appropriate `projects/<project>/assets/` or `experiments/NNN/assets/` subdirectory with an explicit filename.

**Why:** git status pollution, review noise, accidental commits of binary data, loss of context when scattered across root.

## System Evolution

After significant work — update relevant files:
- **Behavioral rule** -> `.claude/rules/*.md`
- **Task/decision** -> `projects/X/BACKLOG.md` (inline with the task)
- **What to do next** -> `context/next-session-prompt.md` (your project section only)
- **Learned pattern** -> `.claude/memory/MEMORY.md` (hot cache — see Rotation Rule)
- **Detailed knowledge** -> `knowledge/concepts/{name}.md` (on-demand wiki, no size limit)
- **New experiment** -> `experiments/NNN-description/EXPERIMENT.md` + update `experiments/README.md`

## Rules

`.claude/rules/` contains domain-specific rules that auto-load. Rules without `paths:` frontmatter load globally (every session). Rules with `paths:` are documented to scope loading, but this has not been independently verified — treat all rules as globally loaded by default.

Create your own rules as needed. Example: `api-conventions.md` for API patterns, `testing.md` for test requirements.

## Communication

- **Language:** [Your preferred language]
- **Tone:** Direct, practical
- **Format:** Tables for comparison, options with trade-offs
