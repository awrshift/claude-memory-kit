"""Path constants for the knowledge base scripts."""

from pathlib import Path
from datetime import datetime, timezone

# Root = Head-of-AI project (config.py is at .claude/memory/scripts/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Knowledge base paths
MEMORY_DIR = ROOT_DIR / ".claude" / "memory"
KNOWLEDGE_DIR = MEMORY_DIR / "knowledge"
CONCEPTS_DIR = KNOWLEDGE_DIR / "concepts"
CONNECTIONS_DIR = KNOWLEDGE_DIR / "connections"
QA_DIR = KNOWLEDGE_DIR / "qa"
EXPERIMENTS_WIKI_DIR = KNOWLEDGE_DIR / "experiments"
PROJECTS_WIKI_DIR = KNOWLEDGE_DIR / "projects"
MEETINGS_WIKI_DIR = KNOWLEDGE_DIR / "meetings"
INDEX_FILE = KNOWLEDGE_DIR / "index.md"
LOG_FILE = KNOWLEDGE_DIR / "log.md"

# Raw sources
DAILY_DIR = ROOT_DIR / "daily"
EXPERIMENTS_RAW_DIR = ROOT_DIR / "experiments"
ARCHIVE_DIR = ROOT_DIR / "archive"

# State tracking (runtime state in .claude/state/, gitignored)
SCRIPTS_DIR = Path(__file__).resolve().parent
STATE_DIR = ROOT_DIR / ".claude" / "state"
STATE_FILE = STATE_DIR / "compile-state.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
