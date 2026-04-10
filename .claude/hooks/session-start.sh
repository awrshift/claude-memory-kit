#!/bin/bash
# SessionStart hook — context overview at session start
#
# Shows: session counter, memory capacity + staleness, project list with
# task counts and staleness, active experiments, git status.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STATE_DIR="$HOME/.claude-starter-kit/hook_state"
mkdir -p "$STATE_DIR"

NOW=$(date +%s)

# Session counter
SESSION_FILE="$STATE_DIR/session_count"
SESSION_NUM=1
if [ -f "$SESSION_FILE" ]; then
    SESSION_NUM=$(cat "$SESSION_FILE")
    SESSION_NUM=$((SESSION_NUM + 1))
fi
echo "$SESSION_NUM" > "$SESSION_FILE"

echo "=== SESSION START (#$SESSION_NUM) ==="
echo ""

# 1. Memory summary
echo "## Memory"
MEMORY_FILE="$PROJECT_DIR/.claude/memory/MEMORY.md"
if [ -f "$MEMORY_FILE" ]; then
    LINES=$(wc -l < "$MEMORY_FILE" | tr -d ' ')
    CAPACITY=$((LINES * 100 / 200))
    TOPICS=$(find "$PROJECT_DIR/.claude/memory/topics" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

    MTIME=$(stat -f '%m' "$MEMORY_FILE" 2>/dev/null || stat -c '%Y' "$MEMORY_FILE" 2>/dev/null)
    if [ -n "$MTIME" ]; then
        DAYS_AGO=$(( (NOW - MTIME) / 86400 ))
        if [ "$DAYS_AGO" -eq 0 ]; then AGE="today"
        elif [ "$DAYS_AGO" -eq 1 ]; then AGE="1 day ago"
        else AGE="$DAYS_AGO days ago"; fi
    else
        AGE="unknown"
    fi

    STALE_FLAG=""
    [ -n "$MTIME" ] && [ "$DAYS_AGO" -ge 5 ] && STALE_FLAG=" !! STALE"

    echo "MEMORY.md: $LINES/200 lines (${CAPACITY}% full) — updated $AGE$STALE_FLAG"
    echo "Topics: $TOPICS files"
else
    echo "No MEMORY.md found"
fi
echo ""

# 2. Projects with task counts and staleness
echo "## Projects"
if [ -d "$PROJECT_DIR/projects" ]; then
    for backlog in "$PROJECT_DIR"/projects/*/BACKLOG.md; do
        if [ -f "$backlog" ]; then
            PROJECT_NAME=$(basename "$(dirname "$backlog")")
            ACTIVE=$(grep -c "Status:.*IN PROGRESS\|Status:.*TODO\|Status:.*BLOCKED" "$backlog" 2>/dev/null || echo 0)
            DONE=$(grep -c "^- \*\*T-" "$backlog" 2>/dev/null || echo 0)

            B_MTIME=$(stat -f '%m' "$backlog" 2>/dev/null || stat -c '%Y' "$backlog" 2>/dev/null)
            B_STALE=""
            if [ -n "$B_MTIME" ]; then
                B_DAYS=$(( (NOW - B_MTIME) / 86400 ))
                [ "$B_DAYS" -ge 5 ] && B_STALE=" !! STALE ($B_DAYS days)"
            fi

            echo "- $PROJECT_NAME: $ACTIVE active, $DONE completed$B_STALE"
        fi
    done
else
    echo "No projects yet"
fi
echo ""

# 3. Active experiments
echo "## Experiments"
EXP_COUNT=0
if [ -d "$PROJECT_DIR/experiments" ]; then
    for exp_dir in "$PROJECT_DIR"/experiments/[0-9]*/; do
        if [ -f "$exp_dir/EXPERIMENT.md" ]; then
            EXP_NAME=$(basename "$exp_dir")
            STATUS=$(grep -o "Status:.*" "$exp_dir/EXPERIMENT.md" 2>/dev/null | head -1 | sed 's/.*Status:\*\* *//' | sed 's/\*\*Status:\*\* *//')
            [ -n "$STATUS" ] && echo "- $EXP_NAME: $STATUS" || echo "- $EXP_NAME"
            EXP_COUNT=$((EXP_COUNT + 1))
        fi
    done
fi
[ "$EXP_COUNT" -eq 0 ] && echo "No active experiments"
echo ""

# 4. Git status
echo "## Git"
cd "$PROJECT_DIR" && git branch --show-current 2>/dev/null && git status --short 2>/dev/null | head -5
echo ""

echo "=== Read context/next-session-prompt.md for full context ==="
