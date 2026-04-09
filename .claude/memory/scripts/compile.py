"""
Compile daily conversation logs into structured knowledge articles.

Reads daily/*.md logs and uses `claude -p` (subscription, no API key)
to create/update wiki articles in .claude/memory/knowledge/.

Usage:
    python scripts/compile.py                         # compile new/changed only
    python scripts/compile.py --all                   # force recompile everything
    python scripts/compile.py --file daily/2026-04-09.md  # compile specific log
    python scripts/compile.py --dry-run               # show what would be compiled
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from config import (
    CONCEPTS_DIR,
    CONNECTIONS_DIR,
    DAILY_DIR,
    INDEX_FILE,
    KNOWLEDGE_DIR,
    LOG_FILE,
    MEETINGS_WIKI_DIR,
    ROOT_DIR,
    SCRIPTS_DIR,
    STATE_FILE,
    now_iso,
    today_iso,
)


def file_hash(path: Path) -> str:
    """SHA-256 hash of a file (first 16 hex chars)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"ingested": {}, "total_compiles": 0}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def list_daily_logs() -> list[Path]:
    if not DAILY_DIR.exists():
        return []
    return sorted(DAILY_DIR.glob("*.md"))


def list_wiki_articles() -> list[Path]:
    articles = []
    for subdir in [CONCEPTS_DIR, CONNECTIONS_DIR, MEETINGS_WIKI_DIR]:
        if subdir.exists():
            articles.extend(sorted(subdir.glob("*.md")))
    return articles


def read_wiki_index() -> str:
    if INDEX_FILE.exists():
        return INDEX_FILE.read_text(encoding="utf-8")
    return "(empty index)"


def read_existing_articles_summary() -> str:
    """Read article titles and key points for context (not full content to save tokens)."""
    parts = []
    for article in list_wiki_articles():
        rel = article.relative_to(KNOWLEDGE_DIR)
        content = article.read_text(encoding="utf-8")
        # Extract just title and key points (first 500 chars)
        summary = content[:500]
        parts.append(f"### {rel}\n{summary}\n...")
    return "\n\n".join(parts) if parts else "(no existing articles)"


def build_compile_prompt(log_path: Path) -> str:
    """Build the compilation prompt for claude -p."""
    log_content = log_path.read_text(encoding="utf-8")
    wiki_index = read_wiki_index()
    existing = read_existing_articles_summary()
    timestamp = now_iso()

    return f"""You are a knowledge compiler. Read the daily conversation log below and extract
knowledge into structured wiki articles.

## Current Wiki Index

{wiki_index}

## Existing Articles (summaries)

{existing}

## Daily Log to Compile

**File:** {log_path.name}

{log_content}

## Your Task

Extract knowledge from this daily log into wiki articles. Follow these rules exactly:

### Article Format (concepts/)
```yaml
---
title: "Concept Name"
tags: [tag1, tag2]
project: project-name-or-global
sources:
  - "daily/{log_path.name}"
created: {timestamp[:10]}
updated: {timestamp[:10]}
---

# Concept Name

[2-4 sentence core explanation]

## Key Points
- [3-5 bullet points]

## Details
[Deeper explanation]

## Related Concepts
- [[concepts/related-concept]] - How it connects

## Sources
- [[daily/{log_path.name}]] - What was learned
```

### Rules:
1. Extract 2-5 distinct concepts worth their own article
2. If an existing concept article covers this topic: UPDATE it (add info, add source)
3. If it's a new topic: CREATE a new concepts/ article
4. If the log reveals a connection between 2+ concepts: CREATE a connections/ article
5. UPDATE {INDEX_FILE.relative_to(ROOT_DIR)} — add new entries to the table
6. APPEND to {LOG_FILE.relative_to(ROOT_DIR)} — add timestamped entry:
   ```
   ## [{timestamp}] compile | {log_path.name}
   - Source: daily/{log_path.name}
   - Articles created: [[concepts/x]], [[concepts/y]]
   - Articles updated: (list)
   ```
7. Use Obsidian [[wikilinks]] without .md extension
8. Write in encyclopedia style — factual, concise
9. Every article MUST have YAML frontmatter
10. Prefer updating existing articles over creating near-duplicates

### File paths (absolute):
- Concepts: {CONCEPTS_DIR}
- Connections: {CONNECTIONS_DIR}
- Index: {INDEX_FILE}
- Log: {LOG_FILE}
"""


def compile_daily_log(log_path: Path, state: dict) -> bool:
    """Compile a single daily log using claude -p."""
    prompt = build_compile_prompt(log_path)

    # Strip ANTHROPIC_API_KEY so claude -p uses subscription
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}

    cmd = [
        "claude",
        "-p", prompt,
        "--allowedTools", "Read,Write,Edit,Glob,Grep",
        "--output-format", "text",
        "--max-turns", "20",
        "--model", "sonnet",
    ]

    print(f"  Running claude -p (this may take 30-60s)...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(ROOT_DIR),
            timeout=300,  # 5 min max
        )

        if result.returncode != 0:
            print(f"  Error (exit {result.returncode}): {result.stderr[:500]}")
            return False

        print(f"  Done. Output: {len(result.stdout)} chars")

    except subprocess.TimeoutExpired:
        print("  Error: claude -p timed out after 5 minutes")
        return False
    except FileNotFoundError:
        print("  Error: 'claude' command not found. Is Claude Code installed?")
        return False

    # Update state
    state.setdefault("ingested", {})[log_path.name] = {
        "hash": file_hash(log_path),
        "compiled_at": now_iso(),
    }
    state["total_compiles"] = state.get("total_compiles", 0) + 1
    save_state(state)

    return True


def main():
    parser = argparse.ArgumentParser(description="Compile daily logs into knowledge articles")
    parser.add_argument("--all", action="store_true", help="Force recompile all logs")
    parser.add_argument("--file", type=str, help="Compile a specific daily log file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be compiled")
    args = parser.parse_args()

    # Ensure directories exist
    for d in [DAILY_DIR, CONCEPTS_DIR, CONNECTIONS_DIR, MEETINGS_WIKI_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    state = load_state()

    # Determine which files to compile
    if args.file:
        target = Path(args.file)
        if not target.is_absolute():
            target = DAILY_DIR / target.name
            if not target.exists():
                target = ROOT_DIR / args.file
        if not target.exists():
            print(f"Error: {args.file} not found")
            sys.exit(1)
        to_compile = [target]
    else:
        all_logs = list_daily_logs()
        if args.all:
            to_compile = all_logs
        else:
            to_compile = []
            for log_path in all_logs:
                prev = state.get("ingested", {}).get(log_path.name, {})
                if not prev or prev.get("hash") != file_hash(log_path):
                    to_compile.append(log_path)

    if not to_compile:
        print("Nothing to compile — all daily logs are up to date.")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Files to compile ({len(to_compile)}):")
    for f in to_compile:
        print(f"  - {f.name}")

    if args.dry_run:
        return

    # Compile each file sequentially
    success = 0
    for i, log_path in enumerate(to_compile, 1):
        print(f"\n[{i}/{len(to_compile)}] Compiling {log_path.name}...")
        if compile_daily_log(log_path, state):
            success += 1

    articles = list_wiki_articles()
    print(f"\nCompilation complete. {success}/{len(to_compile)} succeeded.")
    print(f"Knowledge base: {len(articles)} articles")


if __name__ == "__main__":
    main()
