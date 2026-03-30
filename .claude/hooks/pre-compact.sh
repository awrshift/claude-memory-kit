#!/bin/bash
# PreCompact hook — remind agent to save context before compression

echo "=== PRE-COMPACT REMINDER ==="
echo ""
echo "Context is about to be compressed. Before continuing, you MUST:"
echo "1. Update .claude/memory/MEMORY.md — save any new patterns (keep < 200 lines)"
echo "2. Update context/next-session-prompt.md — your project section only"
echo "3. Update project JOURNAL.md — task statuses if any active tasks"
echo ""
echo "Do NOT proceed until all 3 steps are complete."
echo "=== END REMINDER ==="
