#!/usr/bin/env bash
# check-token-drift.sh — PostToolUse hook for Claude Code.
#
# Checks if a just-written file contains hardcoded color values.
# If drift is found, outputs a JSON system hint for Claude.
#
# Usage (invoked by Claude Code hook system):
#   The file path is passed either as $1 or read from stdin (JSON envelope).
#
# Output:
#   Prints ONLY a single JSON line if drift is found:
#   {"systemMessage": "The file you just wrote contains hardcoded color values. Consider running /design sync to check for design token drift."}
#
#   No output if clean or not a code file.
#
# Hook config example (.claude/settings.json):
#   {
#     "hooks": {
#       "PostToolUse": [{
#         "matcher": "Write|Edit",
#         "hooks": [{
#           "type": "command",
#           "command": "bash ~/.claude/skills/design/hooks/check-token-drift.sh",
#           "async": true
#         }]
#       }]
#     }
#   }

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CODE_EXTENSIONS="css js jsx ts tsx html"

SKIP_BASENAMES="design-tokens.json design-tokens.css design-tokens.tailwind.css .stitch-context.md"

# ---------------------------------------------------------------------------
# Resolve file path
# ---------------------------------------------------------------------------

# Claude Code PostToolUse hooks receive a JSON payload on stdin like:
#   {"tool_name":"Write","tool_input":{"file_path":"/abs/path/to/file","content":"..."}}
# We try to parse that first; fallback to $1.

FILEPATH=""

if [[ -n "${1:-}" ]]; then
  FILEPATH="$1"
else
  # Try reading JSON from stdin (with a short timeout to avoid hanging)
  if read -t 1 -r stdin_data 2>/dev/null; then
    # Extract file_path from JSON using basic string matching (no jq required)
    FILEPATH="$(echo "$stdin_data" | grep -oE '"file_path"\s*:\s*"[^"]+"' | head -1 | grep -oE '"[^"]+"\s*$' | tr -d '"' | tr -d ' ' || true)"
  fi
fi

# Nothing to check
[[ -z "$FILEPATH" ]] && exit 0
[[ ! -f "$FILEPATH" ]] && exit 0

# ---------------------------------------------------------------------------
# Extension check
# ---------------------------------------------------------------------------

filename="$(basename "$FILEPATH")"
ext="${filename##*.}"

# Check if extension is in CODE_EXTENSIONS
is_code=0
for e in $CODE_EXTENSIONS; do
  if [[ "$ext" == "$e" ]]; then
    is_code=1
    break
  fi
done

[[ $is_code -eq 0 ]] && exit 0

# ---------------------------------------------------------------------------
# Skip generated/token files
# ---------------------------------------------------------------------------

for s in $SKIP_BASENAMES; do
  if [[ "$filename" == "$s" ]]; then
    exit 0
  fi
done

# ---------------------------------------------------------------------------
# Scan for hardcoded color values
# ---------------------------------------------------------------------------

has_drift=0

# Hex colors: #RGB, #RRGGBB, #RRGGBBAA
# Exclude matches inside URLs (preceded by ://)
if grep -qE '#[0-9a-fA-F]{3,8}' "$FILEPATH" 2>/dev/null; then
  # Check there's at least one hex NOT inside a URL context
  if grep -E '#[0-9a-fA-F]{3,8}' "$FILEPATH" 2>/dev/null | grep -vE '://[^\s]*#[0-9a-fA-F]{3,8}' | grep -qE '#[0-9a-fA-F]{3,8}'; then
    has_drift=1
  fi
fi

# rgb() / rgba()
if [[ $has_drift -eq 0 ]]; then
  if grep -qE 'rgba?\([[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+' "$FILEPATH" 2>/dev/null; then
    has_drift=1
  fi
fi

# hsl() / hsla()
if [[ $has_drift -eq 0 ]]; then
  if grep -qE 'hsla?\([[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+%?[[:space:]]*,[[:space:]]*[0-9]+%?' "$FILEPATH" 2>/dev/null; then
    has_drift=1
  fi
fi

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

if [[ $has_drift -eq 1 ]]; then
  printf '{"systemMessage": "The file you just wrote contains hardcoded color values. Consider running /design sync to check for design token drift."}\n'
fi

exit 0
