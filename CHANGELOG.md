# Changelog

## [3.0.0] — 2026-04-09

Major upgrade: ports 3 zero-cost features from Cole Medin's `claude-memory-compiler` (the Karpathy-inspired original that Memory Kit v2 was derived from) that were lost in the v1 → v2 stdlib port. Also renames `JOURNAL.md` → `BACKLOG.md` (cleaner semantic separation with `daily/`), collapses `knowledge/` from 6 → 3 subdirs, and promotes the `CLAUDE_INVOKED_BY` recursion guard from hidden quirk to documented feature.

All changes remain on Python stdlib + `claude -p` subscription. No new dependencies. Zero incremental API cost.

### Added

- **`.claude/hooks/session-start.py`** — new Python hook replacing `session-start.sh`. Outputs JSON `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}` so Claude Code injects `knowledge/index.md` + recent `daily/YYYY-MM-DD.md` logs + top 3 recently-modified concepts into every session's initial context. Adapted from coleam00/claude-memory-compiler. Budget: 50K chars default (`CMK_INJECT_BUDGET` env var to tune).
- **`flush.py` — `maybe_trigger_compilation()`** — after 18:00 local time (`CMK_COMPILE_AFTER_HOUR` env), checks if today's `daily/YYYY-MM-DD.md` has changed since last compile via SHA-256 hash comparison. If yes, spawns `compile.py` as a detached background process. End-of-day auto-compile without cron. Logs to `.claude/state/compile.log`.
- **`.claude/commands/memory-compile.md`** — slash command wrapper around `compile.py`. Manual override alongside auto-trigger.
- **`.claude/commands/memory-lint.md`** — slash command wrapper around `lint.py`. Pass `--fix` for auto-backlinks.
- **`.claude/commands/memory-query.md`** — slash command wrapper around `query.py`. Natural-language queries with index-guided retrieval.
- **CLAUDE.md sections:**
  - `SessionStart Injection` — describes additionalContext pattern, budget, priority order
  - `End-of-day Auto-Compile` — describes 18:00 trigger, hash skip logic, `/memory-compile` manual override
  - `CLAUDE_INVOKED_BY — recursion guard (critical)` — documents the recursion path that prompted the guard (was hidden quirk in v2)

### Changed

- **`JOURNAL.md` → `BACKLOG.md`** throughout the template. Renamed 3 example projects (`example-webapp`, `example-saas`, `my-first-project`). Updated all references in `CLAUDE.md`, `README.md`, `.claude/hooks/periodic-save.sh`, `.claude/hooks/pre-compact.sh`, `.claude/skills/tour/SKILL.md`, `experiments/README.md`, `experiments/001-*/EXPERIMENT.md`, `context/next-session-prompt.md`. Rationale: `BACKLOG` = task queue (future-forward), `daily/` = chronological log (past-forward). Two distinct files with clear semantics. `JOURNAL` was ambiguous — it conflated both.
- **`.claude/memory/knowledge/` collapsed from 6 → 3 subdirectories.** Kept: `concepts/`, `connections/`, `meetings/`. Removed: `qa/` (empty in practice — compounding loop rarely fired manually), `projects/` (duplicated root-level `projects/X/BACKLOG.md`), `experiments/` (duplicated root-level `experiments/NNN/EXPERIMENT.md`). Updated `config.py`, `compile.py`, `lint.py`, `query.py`, `knowledge/index.md`, `CLAUDE.md`.
- **`lint.py` checks: 7 → 6.** Removed `check_stale_experiments` because it required `knowledge/experiments/` which no longer exists. Remaining: broken links, orphan pages, orphan sources, missing backlinks, sparse articles, missing frontmatter.
- **`query.py`: removed `--file-back` flag.** It filed answers to `knowledge/qa/` which no longer exists. Query remains read-only, index-guided. If you miss it, the answer is in git history.
- **`.claude/settings.json`** — SessionStart hook command updated from `bash ".../session-start.sh"` to `python3 ".../session-start.py"`.

### Removed

- `.claude/hooks/session-start.sh` — replaced by `session-start.py`.
- `.claude/memory/knowledge/qa/` directory (and `.gitkeep`).
- `.claude/memory/knowledge/projects/` directory (and `.gitkeep`).
- `.claude/memory/knowledge/experiments/` directory (and `.gitkeep`).
- `check_stale_experiments()` function from `lint.py`.
- `parse_frontmatter()` helper from `lint.py` (became unused after stale_experiments removal).
- `QA_DIR`, `EXPERIMENTS_WIKI_DIR`, `PROJECTS_WIKI_DIR` constants from `config.py`.
- `EXPERIMENTS_RAW_DIR` constant from `config.py` (was only used by check_stale_experiments).

### Migration notes for v2 → v3

**Existing users with a v2 clone must:**

1. **Rename project files:** `find projects -name JOURNAL.md -exec sh -c 'mv "$0" "${0%JOURNAL.md}BACKLOG.md"' {} \;` (or do it manually per project).
2. **Update internal references** in `context/next-session-prompt.md`, `CLAUDE.md`, and any custom rules that mention `JOURNAL.md`.
3. **If you had content in `knowledge/qa/`, `knowledge/projects/`, or `knowledge/experiments/`:** move articles to `knowledge/concepts/` (they lose their subdir categorization but content is preserved). The v3 wiki has only 3 subdirs.
4. **Update hook command** in `.claude/settings.json`: change SessionStart command from `bash .../session-start.sh` to `python3 .../session-start.py`. Or re-copy `settings.json` from the updated template.
5. **Replace `session-start.sh` with `session-start.py`** from v3.
6. **Pull updated `flush.py`** to get `maybe_trigger_compilation()`.
7. **Optional but recommended:** enable end-of-day auto-compile by leaving default `CMK_COMPILE_AFTER_HOUR=18`, or disable with a high value like `99`.
8. **`query.py --file-back` users:** the flag is gone. Answers are no longer filed automatically. If you want this back, copy the pre-v3 version from git history.

**Breaking changes summary:**
- File rename: `JOURNAL.md` → `BACKLOG.md`
- Wiki structure: 6 → 3 subdirs
- Query flag: `--file-back` removed
- Hook command: bash → python3

**Not breaking:**
- MEMORY.md format unchanged
- `next-session-prompt.md` format unchanged (`<!-- PROJECT:name -->` tags still work)
- `daily/` format unchanged
- `compile.py` CLI args unchanged
- All of v2's other hooks (`session-end.sh`, `pre-compact.sh`, `periodic-save.sh`, `protect-tests.sh`) unchanged

### Fixed

- `compile.py` used to have an outdated prompt template that instructed the LLM to write to `knowledge/{qa,projects,experiments}/` subdirs. Now strictly references `concepts/` and `connections/` (and implicitly `meetings/` when applicable).
- `pre-compact.sh` counted project files by looking for `JOURNAL.md`. Now looks for `BACKLOG.md`.
- `periodic-save.sh` block message mentioned `projects/*/JOURNAL.md`. Now says `projects/*/BACKLOG.md`.

---

## [2.0.1] — 2026-04-09

Post-launch polish release. Fixes issues found after v2.0.0 shipped, adds brand asset, and corrects terminology leftovers.

### Fixed

- **README Mermaid diagram truncation** (`4a37c00`) — Long node labels in the architecture diagram were truncated on GitHub's rendered view. Fixed by wrapping labels with `<br/>` in quoted syntax so each visible line stays under ~25 chars. Verified via Chrome browser automation on live GitHub render.
- **`/tour` skill obsolete content** (`6da1f19`) — The `/tour` skill still referenced v1 architecture (3 hooks, `topics/` layer). Updated all steps to reflect v2: 5 hooks (added `session-end.sh` + `protect-tests.sh`), `knowledge/` wiki layer with two-tier memory explanation, new Step 5 for Memory Kit v2 Scripts (compile/lint/query/flush) as power-user optional content.
- **Terminology leftovers: `topics/` → `knowledge/`** (`ab1b0b5`) — Systematic audit caught v1 references still in the codebase:
  - `.claude/memory/MEMORY.md` template had a "Topic Files" section pointing to `.claude/memory/topics/` (v1 path that no longer exists in v2). Rewrote to "Knowledge Wiki" section pointing to `knowledge/concepts/`.
  - `CLAUDE.md` had two lines ("create topic file" in Context Save Protocol, "needs more? → topic file" in Memory Entry Quality) — updated to reference knowledge articles.
- **Missing CONTRIBUTING.md** (`ab1b0b5`) — README linked to `CONTRIBUTING.md` which did not exist (broken link on first click). Created minimal CONTRIBUTING.md with zero-dependencies guidelines, PR rules, and Obsidian-optional ground rule.

### Added

- **GitHub Social Preview banner** (`29afd04`, `b9cd78e`) — `.github/assets/og-banner.png` (1280×640). Dark editorial design with isometric 5-layer glass stack (BRAIN/MEMORY/RULES/JOURNAL/CONTEXT). Generated via Gemini Nano Banana Pro after evaluating 3 variants (Swiss editorial, terminal, isometric). Isometric chosen for strongest visual anchor at thumbnail size. Upload via repo Settings → Social preview.
- **Hero banner in README** (`de0990b`) — Banner now renders as the first element of the README via pure Markdown image syntax. Stays compliant with H3 Hybrid structure (no HTML wrappers in top zone). Visitors see the visual brand before reading any text.

### Notes for upgraders from v2.0.0

- No breaking changes. Pure additive + fixes.
- If you already cloned v2.0.0 and want to pull v2.0.1: `git pull origin main` — no action required.
- The `/tour` skill will show the updated v2 walkthrough automatically on next invocation.
- The Mermaid diagram fix only affects rendered view; no behavior change.

---

## [2.0.0] — 2026-04-09

Major upgrade: Memory Kit v2 pipeline ported from the private reference project.
All additions use Python stdlib only. No `pip install`, no new services, no database.

### Added

- **`.claude/memory/scripts/`** — 5 Python scripts:
  - `config.py` — path constants (single source of truth)
  - `compile.py` — `daily/*.md` → `knowledge/` wiki articles (incremental via SHA-256 hash, uses `claude -p` subscription)
  - `lint.py` — 7 structural health checks (broken links, orphans, missing backlinks, sparse articles, missing frontmatter, stale experiments) + `--fix` for auto-repair
  - `query.py` — index-guided retrieval engine with optional `--file-back` to save answers as Q&A articles (compounding loop)
  - `flush.py` — session transcript extractor (Opus, 100 turns / 50KB window)
- **`.claude/hooks/session-end.sh`** — auto-captures conversation transcripts to `daily/YYYY-MM-DD.md` at session end, spawns `flush.py` as detached background process
- **`.claude/hooks/protect-tests.sh`** — `PreToolUse` hook that blocks edits to existing test files (Edit blocked, Write-new allowed). Forces fixing implementation instead of tests.
- **`.claude/memory/knowledge/`** — structured wiki layer:
  - `concepts/` — single-topic deep dives
  - `connections/` — cross-concept relationships
  - `meetings/` — meeting index articles
  - `qa/` — filed query answers (compounding loop)
  - `projects/` — per-project wiki articles
  - `experiments/` — gravestone pattern (articles stay after raw files archived)
  - `index.md` — master catalog (read first for any deep query)
  - `log.md` — append-only build log
- **`daily/`** — directory for auto-captured session logs (content gitignored by default, only `.gitkeep` committed)
- **`.claude/state/`** — project-local runtime state (gitignored, replaces legacy `~/.claude-starter-kit/hook_state/`)
- **README** — new "What's New in v2" section and "Do I need Obsidian?" FAQ entry (answer: no, any Markdown editor works)
- **CLAUDE.md** — new "Memory Kit v2 Scripts" section, "Session-End Auto-Capture" description, Obsidian-optional note in Memory System

### Changed

- Hook state path migrated from `~/.claude-starter-kit/hook_state/` to project-local `.claude/state/` — cleaner, no cross-project collisions, gitignored runtime files
- All hook commands in `.claude/settings.json` now use `$CLAUDE_PROJECT_DIR` prefix — path-safe when agent runs `cd` away from project root
- `.claude/settings.json` hook format updated to use nested `hooks` arrays (matches current Claude Code spec)
- Periodic save default: every **15 → 50** exchanges (reduces noise, still catches long sessions). Configurable via `CLAUDE_SAVE_INTERVAL` env var.
- Memory System terminology: `topics/` renamed to `knowledge/` throughout `CLAUDE.md` (reflects the structured wiki layer, not flat topic files)
- `CLAUDE.md` Context Architecture table: added L5 `daily/YYYY-MM-DD.md` row (auto-captured raw source)
- `session-start.sh` now counts knowledge articles instead of flat topic files

### Removed

- `.claude/memory/topics/.gitkeep` — superseded by `knowledge/` wiki. (No user content lost — the directory was empty in v1.)

### Migration notes for v1 → v2

- **Existing users:** Your `~/.claude-starter-kit/hook_state/session_count` will no longer be read. The session counter resets to 1. Non-critical (cosmetic). If you want to preserve it: `cp ~/.claude-starter-kit/hook_state/session_count .claude/state/session_count`.
- **MEMORY.md format** is unchanged. Your existing patterns continue to work.
- **JOURNAL.md format** is unchanged.
- **next-session-prompt.md format** is unchanged (`<!-- PROJECT:name -->` tags still work).
- If you had content in the old empty `topics/` directory (unlikely, since v1 shipped it empty), move `.md` files to `.claude/memory/knowledge/concepts/`.
- After pulling v2: run `chmod +x .claude/hooks/session-end.sh .claude/hooks/protect-tests.sh` if the executable bit didn't survive the transfer.

### Dependencies

- Python 3 (stdlib only — no `pip install`)
- Claude Code CLI (existing requirement)
- Claude Pro/Max subscription or API key (existing requirement)
- **Obsidian is NOT required** — the wiki works in any Markdown editor. Obsidian is only for the optional visual graph view.

## [1.0.0] — 2026-04-08

Initial release. See commit history before this point.
