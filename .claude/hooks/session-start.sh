#!/bin/bash
# SessionStart hook — inject context into Claude Code at session start

PROJECT_DIR="$(dirname "$0")/../.."

echo "=== SESSION START ==="
echo ""

# 1. Memory summary
echo "## Memory Summary"
if [ -f "$PROJECT_DIR/.claude/memory/MEMORY.md" ]; then
  VERIFIED=$(grep -c "VERIFIED" "$PROJECT_DIR/.claude/memory/MEMORY.md" 2>/dev/null || echo 0)
  PROBABLE=$(grep -c "PROBABLE" "$PROJECT_DIR/.claude/memory/MEMORY.md" 2>/dev/null || echo 0)
  HYPOTHESIS=$(grep -c "HYPOTHESIS" "$PROJECT_DIR/.claude/memory/MEMORY.md" 2>/dev/null || echo 0)
  LINES=$(wc -l < "$PROJECT_DIR/.claude/memory/MEMORY.md" 2>/dev/null || echo 0)
  echo "Patterns: $VERIFIED verified, $PROBABLE probable, $HYPOTHESIS hypotheses ($LINES lines)"
else
  echo "No MEMORY.md found"
fi
echo ""

# 2. Current context (quick orientation)
echo "## Current Context"
if [ -f "$PROJECT_DIR/.claude/memory/CONTEXT.md" ]; then
  cat "$PROJECT_DIR/.claude/memory/CONTEXT.md" 2>/dev/null
else
  echo "No CONTEXT.md found"
fi
echo ""

# 3. Git status
echo "## Git Status"
cd "$PROJECT_DIR" && git branch --show-current 2>/dev/null && git status --short 2>/dev/null | head -10
echo ""

# 4. Snapshots
SNAPSHOT_DIR="$PROJECT_DIR/.claude/memory/snapshots"
if [ -d "$SNAPSHOT_DIR" ]; then
  SNAP_COUNT=$(find "$SNAPSHOT_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$SNAP_COUNT" -gt 0 ]; then
    LATEST=$(ls -t "$SNAPSHOT_DIR"/*.md 2>/dev/null | head -1 | xargs basename)
    echo "## Snapshots: $SNAP_COUNT saved, latest: $LATEST"
  fi
fi
echo ""

echo "=== Read context/next-session-prompt.md and .claude/memory/MEMORY.md for full context ==="
