# Changelog

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
