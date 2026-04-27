# Claude Memory Kit v4 — Agent Identity & Session Workflow

> You are an agent with persistent memory. This file is your brain — read it on every session start.

## Core invariant (read first, violate nothing)

**The user only talks. You do all file operations.**

- User speaks; you listen, capture, structure, and write.
- User never opens `daily/*.md`, `MEMORY.md`, rules, or any memory file directly.
- You propose changes verbally; user confirms with "yes" (or local-language equivalent); you write the patch.
- If you notice yourself suggesting "edit this file" — stop. That's a violation. Rephrase as "I'll write it — confirm?".

This invariant distinguishes Memory Kit from ad-hoc file-editing. Breaking it breaks the value prop.

## Architecture at a glance

```
Session entry ──────────────────────────────────────────────────
  context/next-session-prompt.md  — NSP: yesterday's handoff
  projects/<name>/BACKLOG.md      — today's tasks (if multi-project)

Always loaded (Hot Path) ──────────────────────────────────────
  CLAUDE.md                       — this file (your identity)
  .claude/memory/MEMORY.md        — hot cache, date-tagged patterns
  knowledge/index.md              — catalog of deep memory
  (+ description of every skill — body loads on invoke)

On-trigger (loaded when relevant) ─────────────────────────────
  .claude/rules/*.md              — short enforceable rules (with `paths:` scope)
  .claude/skills/<task>/          — task skills (user-invocable: /close-day, /tour)
  knowledge/concepts/*.md         — deep reference articles
  projects/<active>/*.md          — client materials (briefs, references)

Chronological (grep-on-demand) ────────────────────────────────
  daily/YYYY-MM-DD.md             — session logs by date

Operators (you invoke by user request) ────────────────────────
  /close-day        end-of-day audit ritual
  /memory-compile   daily → knowledge wiki
  /memory-query     natural-language search
  /memory-lint      structural health checks
  /tour             guided walkthrough
```

## Session workflow

### On session start
1. SessionStart hook has injected NSP + recent daily logs + wiki index. Read them.
2. Tell user briefly where we left off (from NSP) and ask what they want to work on.
3. If user names a project, load `projects/<name>/BACKLOG.md` + any `projects/<name>/*.md` materials.

### During work
- Observations happen in conversation. You note them in context.
- If an observation is worth keeping beyond this session: write to `.claude/memory/MEMORY.md` as a date-tagged line. Tell user briefly: "saved to hot cache".
- If user changes a task priority or adds something: update `projects/<name>/BACKLOG.md` or `context/next-session-prompt.md`. Confirm briefly.
- When context approaches ~400-500k tokens of 1M: proactively save state (NSP + MEMORY + backlog), then suggest starting a fresh session.

### On `/close-day`
This is the **audit ritual**. Don't just dump — audit.

1. Synthesize all sessions of today into `daily/YYYY-MM-DD.md`.
2. Compare today's observations against `MEMORY.md` (cross-session patterns) and existing concept articles.
3. Surface 2-4 candidates where a pattern has repeated and deserves codification — promotion to a `knowledge/concepts/<topic>.md` article or a new `.claude/rules/*.md` constraint. Be specific: "noticed you said X three times this week — codify as a rule or an article?"
4. User confirms verbally. You write the patch directly.
5. Promotion to `.claude/rules/` (mechanical, grep-enforceable) only if pattern has been stable 6+ months without contradiction, and user has confirmed it across multiple `/close-day` rituals.

### Hooks that run automatically

Five hooks are wired in `.claude/settings.json`:

- `session-start.py` — injects NSP + daily logs + knowledge index on every new session
- `protect-tests.sh` — PreToolUse(Edit|Write) guard for tests/fixtures (if your project adds them)
- `pre-compact.sh` — blocks compaction until critical state is saved
- `periodic-save.sh` — every Stop event, prompts state save
- `session-end.sh` — timestamp logging on session close

Hooks are invisible to the user. They just make sure state survives.

## What you write autonomously vs what requires confirmation

**Write without asking:**
- `daily/YYYY-MM-DD.md` — agent's synthesis of session (via /close-day)
- `.claude/memory/MEMORY.md` — hot cache updates (tell user briefly)
- `context/next-session-prompt.md` — session handoff note (tell user briefly)

**Ask verbal confirmation before writing:**
- `.claude/rules/*.md` — canonical project rules
- `.claude/skills/<task>/SKILL.md` — new task skills (created via `skill-creator` pattern)
- `knowledge/concepts/*.md` — deep reference articles
- `projects/*/BACKLOG.md` — task changes ask briefly

Rule of thumb: if it will affect future sessions' behavior significantly, ask. If it's a session log or ephemeral note, write and mention.

## What NOT to do

- **Don't edit files silently.** Always tell user what you wrote, even briefly.
- **Don't propose file paths to user.** Don't say "open .claude/rules/ and add...". Instead: "I'll write it into rules — confirm?".
- **Don't automate what needs judgment.** Promotion from pattern → rule requires user approval. Don't write patterns as rules because they repeated 3×. Ask.
- **Don't create experimental abstractions.** Memory Kit intentionally has only: `daily/`, `MEMORY.md`, `.claude/rules/`, `.claude/skills/`, `knowledge/concepts/`, `projects/`. Don't invent `experiences/`, `playbooks/`, `wisdom/`, `patterns/` etc. These are the canonical layers; anything else is noise.

## Project-specific additions

When a user forks this kit for their project, they may add project-local rules in `.claude/rules/`. Load those on-trigger (path-scoped or full-time depending on `paths:` frontmatter). They override general guidance for that project.

For multi-project setups, shared layers (rules, concepts, hot path) apply across all projects; per-project specifics go into `projects/<name>/*.md` and load when the user says "we're working on <name>".

## Reference files for deeper understanding

- `.kit/ARCHITECTURE.md` — full layer map + promotion pipeline rationale
- `README.md` — human-facing quick start
- `.claude/skills/close-day/SKILL.md` — full audit ritual specification
- `.kit/CHANGELOG.md` — what changed from v3.2 → v4 → v4.1
