"""
Flush conversation transcript to daily log.

Spawned by session-end hook as a background process. Reads pre-extracted
conversation context from a temp file, uses `claude -p` (subscription)
to extract important content, and appends to today's daily log.

Usage:
    python scripts/flush.py <context_file.md> <session_id>
"""

from __future__ import annotations

# Recursion guard: set BEFORE any imports that might trigger Claude
import os
os.environ["CLAUDE_INVOKED_BY"] = "memory_flush"

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
DAILY_DIR = ROOT / "daily"
SCRIPTS_DIR = Path(__file__).resolve().parent
STATE_DIR = ROOT / ".claude" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = STATE_DIR / "last-flush.json"
LOG_FILE = STATE_DIR / "flush.log"
COMPILE_STATE_FILE = STATE_DIR / "compile-state.json"
COMPILE_SCRIPT = SCRIPTS_DIR / "compile.py"

# End-of-day auto-compile: after this hour, spawn compile.py if today's
# daily log has new content since the last successful compile.
COMPILE_AFTER_HOUR = int(os.environ.get("CMK_COMPILE_AFTER_HOUR", "18"))

# File-based logging (parent redirects stdout/stderr to DEVNULL)
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def load_flush_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_flush_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state), encoding="utf-8")


def append_to_daily_log(content: str, session_id: str) -> None:
    """Append flushed content to today's daily log."""
    today = datetime.now(timezone.utc).astimezone()
    log_path = DAILY_DIR / f"{today.strftime('%Y-%m-%d')}.md"

    if not log_path.exists():
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"# Daily Log: {today.strftime('%Y-%m-%d')}\n\n## Sessions\n\n",
            encoding="utf-8",
        )

    time_str = today.strftime("%H:%M")
    entry = f"### Session {session_id[:8]} ({time_str})\n\n{content}\n\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)


def run_flush(context: str) -> str:
    """Call claude -p to extract important content from context."""
    prompt = f"""Review the conversation context below and extract a concise summary of what
should be preserved in the daily log.

Format as structured markdown with these sections (skip any that have no content):

**Context:** [One line about what the user was working on]

**Key Exchanges:**
- [Important Q&A or discussions]

**Decisions Made:**
- [Decisions with rationale]

**Lessons Learned:**
- [Gotchas, patterns, insights discovered]

**Action Items:**
- [Follow-ups or TODOs mentioned]

Skip routine tool calls, trivial exchanges, and clarifications. If nothing is
worth saving, respond with exactly: FLUSH_OK

## Conversation Context

{context}
"""

    # Strip ANTHROPIC_API_KEY to use subscription
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    env["CLAUDE_INVOKED_BY"] = "memory_flush"  # recursion guard

    try:
        result = subprocess.run(
            ["claude", "-p", prompt,
             "--output-format", "text",
             "--max-turns", "2",
             "--model", "opus"],
            capture_output=True,
            text=True,
            env=env,
            timeout=300,
        )
        if result.returncode != 0:
            logging.error("claude -p exit %d: %s", result.returncode, result.stderr[:500])
            return f"FLUSH_ERROR: exit {result.returncode}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logging.error("claude -p timed out")
        return "FLUSH_ERROR: timeout"
    except FileNotFoundError:
        logging.error("claude command not found")
        return "FLUSH_ERROR: claude not found"


def maybe_trigger_compilation() -> None:
    """
    End-of-day auto-compile trigger.

    After COMPILE_AFTER_HOUR local time, check if today's daily log has
    changed since the last successful compile. If yes, spawn compile.py
    as a detached background process so it doesn't block the current
    flush completion.

    Skips gracefully if: too early, no daily log, already compiled with
    matching hash, or compile.py missing.
    """
    import hashlib

    now = datetime.now(timezone.utc).astimezone()
    if now.hour < COMPILE_AFTER_HOUR:
        return

    today_name = f"{now.strftime('%Y-%m-%d')}.md"
    today_log = DAILY_DIR / today_name
    if not today_log.exists():
        return

    if not COMPILE_SCRIPT.exists():
        logging.warning("compile.py not found at %s, cannot auto-trigger", COMPILE_SCRIPT)
        return

    # Hash-based skip: if already compiled and content unchanged, do nothing.
    try:
        current_hash = hashlib.sha256(today_log.read_bytes()).hexdigest()[:16]
    except OSError as e:
        logging.error("Failed to hash %s: %s", today_log, e)
        return

    if COMPILE_STATE_FILE.exists():
        try:
            compile_state = json.loads(COMPILE_STATE_FILE.read_text(encoding="utf-8"))
            ingested = compile_state.get("ingested", {})
            if today_name in ingested and ingested[today_name].get("hash") == current_hash:
                logging.info("End-of-day compile: %s unchanged since last compile, skipping", today_name)
                return
        except (json.JSONDecodeError, OSError):
            pass

    logging.info("End-of-day compile triggered for %s (after %d:00)", today_name, COMPILE_AFTER_HOUR)

    # Spawn compile.py detached. Env inherits CLAUDE_INVOKED_BY so any
    # nested hooks (compile.py itself invokes claude -p) short-circuit.
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    env["CLAUDE_INVOKED_BY"] = "memory_flush"

    try:
        compile_log = open(str(STATE_DIR / "compile.log"), "a")
        subprocess.Popen(
            ["python3", str(COMPILE_SCRIPT)],
            stdout=compile_log,
            stderr=subprocess.STDOUT,
            cwd=str(ROOT),
            env=env,
            start_new_session=True,
        )
        logging.info("Spawned compile.py detached (pid logged to compile.log)")
    except Exception as e:
        logging.error("Failed to spawn compile.py: %s", e)


def main():
    if len(sys.argv) < 3:
        logging.error("Usage: %s <context_file.md> <session_id>", sys.argv[0])
        sys.exit(1)

    context_file = Path(sys.argv[1])
    session_id = sys.argv[2]

    logging.info("flush.py started for session %s", session_id)

    if not context_file.exists():
        logging.error("Context file not found: %s", context_file)
        return

    # Dedup: skip if same session flushed within 60 seconds
    state = load_flush_state()
    if (
        state.get("session_id") == session_id
        and time.time() - state.get("timestamp", 0) < 60
    ):
        logging.info("Skipping duplicate flush for %s", session_id)
        context_file.unlink(missing_ok=True)
        return

    context = context_file.read_text(encoding="utf-8").strip()
    if not context:
        logging.info("Empty context, skipping")
        context_file.unlink(missing_ok=True)
        return

    logging.info("Flushing %d chars for session %s", len(context), session_id)

    response = run_flush(context)

    if "FLUSH_OK" in response:
        logging.info("Nothing worth saving")
    elif "FLUSH_ERROR" in response:
        logging.error("Result: %s", response)
    else:
        logging.info("Saved %d chars to daily log", len(response))
        append_to_daily_log(response, session_id)

    save_flush_state({"session_id": session_id, "timestamp": time.time()})
    context_file.unlink(missing_ok=True)

    # End-of-day auto-compile trigger (Cole pattern, Karpathy's flush-then-compile loop)
    maybe_trigger_compilation()

    logging.info("Flush complete for %s", session_id)


if __name__ == "__main__":
    main()
