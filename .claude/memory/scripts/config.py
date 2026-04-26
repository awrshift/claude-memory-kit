"""Path constants for the knowledge base scripts."""

from pathlib import Path
from datetime import datetime, timezone

# Root = Head-of-AI project (config.py is at .claude/memory/scripts/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Knowledge base paths — 3 subdirs since v3.1 (moved to project root to avoid
# Claude Code .claude/** sensitive file protection blocking compile.py writes).
MEMORY_DIR = ROOT_DIR / ".claude" / "memory"
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
CONCEPTS_DIR = KNOWLEDGE_DIR / "concepts"
CONNECTIONS_DIR = KNOWLEDGE_DIR / "connections"
MEETINGS_WIKI_DIR = KNOWLEDGE_DIR / "meetings"
INDEX_FILE = KNOWLEDGE_DIR / "index.md"
LOG_FILE = KNOWLEDGE_DIR / "log.md"

# Raw sources
DAILY_DIR = ROOT_DIR / "daily"

# Skills (v4: role-based reference skills live under .claude/skills/*-guidance/)
# Reference skills are user-invocable:false, auto-loaded by Claude on description match.
SKILLS_DIR = ROOT_DIR / ".claude" / "skills"
REFERENCE_SKILL_SUFFIX = "-guidance"  # directory naming convention
PROJECTS_DIR = ROOT_DIR / "projects"

# Thresholds
OVERSIZED_SKILL_LINES = 500  # Reference skills above this are split candidates
                             # (matches Anthropic's recommended SKILL.md ceiling)

# State tracking (runtime state in .claude/state/, gitignored)
SCRIPTS_DIR = Path(__file__).resolve().parent
STATE_DIR = ROOT_DIR / ".claude" / "state"
STATE_FILE = STATE_DIR / "compile-state.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
