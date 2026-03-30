#!/bin/bash
# SessionStart hook — inject context into Claude Code at session start

PROJECT_DIR="$(dirname "$0")/../.."

echo "=== SESSION START ==="
echo ""

# 1. Memory summary
echo "## Memory"
if [ -f "$PROJECT_DIR/.claude/memory/MEMORY.md" ]; then
  LINES=$(wc -l < "$PROJECT_DIR/.claude/memory/MEMORY.md" 2>/dev/null || echo 0)
  TOPICS=$(find "$PROJECT_DIR/.claude/memory/topics" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "MEMORY.md: $LINES lines (index) + $TOPICS topic files"
else
  echo "No MEMORY.md found"
fi
echo ""

# 2. Active projects
echo "## Projects"
if [ -d "$PROJECT_DIR/projects" ]; then
  for journal in "$PROJECT_DIR"/projects/*/JOURNAL.md; do
    if [ -f "$journal" ]; then
      PROJECT_NAME=$(basename "$(dirname "$journal")")
      echo "- $PROJECT_NAME"
    fi
  done
else
  echo "No projects yet"
fi
echo ""

# 3. Git status
echo "## Git"
cd "$PROJECT_DIR" && git branch --show-current 2>/dev/null && git status --short 2>/dev/null | head -10
echo ""

echo "=== Read context/next-session-prompt.md for full context ==="
