#!/usr/bin/env bash
#
# SessionEnd hook — auto-capture conversation transcript to daily/ log.
#
# Reads hook input from stdin (JSON with session_id, transcript_path),
# extracts last N conversation turns, spawns flush.py as background process.
#
# Recursion guard: exit if invoked by flush.py itself.

set -euo pipefail

# Recursion guard
if [[ -n "${CLAUDE_INVOKED_BY:-}" ]]; then
    exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SCRIPTS_DIR="$PROJECT_DIR/.claude/memory/scripts"
STATE_DIR="$PROJECT_DIR/.claude/state"
mkdir -p "$STATE_DIR"
LOG_FILE="$STATE_DIR/flush.log"

# Read stdin JSON
HOOK_INPUT=$(cat)
SESSION_ID=$(echo "$HOOK_INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', 'unknown'))" 2>/dev/null || echo "unknown")
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('transcript_path', ''))" 2>/dev/null || echo "")

echo "$(date '+%Y-%m-%d %H:%M:%S') [hook] SessionEnd fired: session=$SESSION_ID" >> "$LOG_FILE"

# Skip if no transcript
if [[ -z "$TRANSCRIPT_PATH" || ! -f "$TRANSCRIPT_PATH" ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') [hook] SKIP: no transcript" >> "$LOG_FILE"
    exit 0
fi

# Extract last ~100 conversation turns as markdown (fast, no LLM)
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
CONTEXT_FILE="$STATE_DIR/session-flush-${SESSION_ID}-${TIMESTAMP}.md"

python3 <<EOF >> "$LOG_FILE" 2>&1
import json
from pathlib import Path

transcript_path = Path("$TRANSCRIPT_PATH")
context_file = Path("$CONTEXT_FILE")

MAX_TURNS = 100
MAX_CHARS = 50000

turns = []
try:
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = entry.get("message", {})
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
            else:
                role = entry.get("role", "")
                content = entry.get("content", "")

            if role not in ("user", "assistant"):
                continue

            if isinstance(content, list):
                parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        parts.append(block)
                content = "\n".join(parts)

            if isinstance(content, str) and content.strip():
                label = "User" if role == "user" else "Assistant"
                turns.append(f"**{label}:** {content.strip()}\n")

    recent = turns[-MAX_TURNS:]
    ctx = "\n".join(recent)
    if len(ctx) > MAX_CHARS:
        ctx = ctx[-MAX_CHARS:]

    context_file.write_text(ctx, encoding="utf-8")
    print(f"[hook] Extracted {len(recent)} turns, {len(ctx)} chars")
except Exception as e:
    print(f"[hook] ERROR extracting transcript: {e}")
EOF

# Spawn flush.py in background, detached
if [[ -f "$CONTEXT_FILE" ]]; then
    nohup python3 "$SCRIPTS_DIR/flush.py" "$CONTEXT_FILE" "$SESSION_ID" \
        >> "$LOG_FILE" 2>&1 &
    disown
    echo "$(date '+%Y-%m-%d %H:%M:%S') [hook] Spawned flush.py for $SESSION_ID" >> "$LOG_FILE"
fi

exit 0
