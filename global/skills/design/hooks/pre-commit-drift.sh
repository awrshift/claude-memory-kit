#!/usr/bin/env bash
# pre-commit-drift.sh — Git pre-commit hook: design token drift check.
#
# Install:
#   cp pre-commit-drift.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Or source from an existing pre-commit hook:
#   source "$(git rev-parse --show-toplevel)/.claude/skills/design/hooks/pre-commit-drift.sh"
#
# Exit codes:
#   0 = clean (commit proceeds)
#   1 = drift or stale files detected (commit blocked)

set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TOKENS_FILE="design-tokens.json"
GENERATED_CSS="design-tokens.css"
GENERATED_TAILWIND="design-tokens.tailwind.css"

# Filenames to skip when checking staged files (basename match)
SKIP_BASENAMES=(
  "design-tokens.json"
  "design-tokens.css"
  "design-tokens.tailwind.css"
  ".stitch-context.md"
)

# Extensions to check
CODE_EXTENSIONS=("css" "js" "jsx" "ts" "tsx" "html")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Return 0 if the extension of $1 is in CODE_EXTENSIONS
is_code_file() {
  local file="$1"
  local ext="${file##*.}"
  for e in "${CODE_EXTENSIONS[@]}"; do
    [[ "$ext" == "$e" ]] && return 0
  done
  return 1
}

# Return 0 if basename of $1 is in SKIP_BASENAMES
is_skip_file() {
  local file="$1"
  local base
  base="$(basename "$file")"
  for s in "${SKIP_BASENAMES[@]}"; do
    [[ "$base" == "$s" ]] && return 0
  done
  return 1
}

# ---------------------------------------------------------------------------
# Step 1: Check stale generated files
# ---------------------------------------------------------------------------

stale_warning=""

if [[ -f "$TOKENS_FILE" ]]; then
  for gen_file in "$GENERATED_CSS" "$GENERATED_TAILWIND"; do
    if [[ -f "$gen_file" ]]; then
      # Compare modification times: tokens newer than generated → stale
      if [[ "$TOKENS_FILE" -nt "$gen_file" ]]; then
        stale_warning="$gen_file"
        break
      fi
    fi
  done
fi

if [[ -n "$stale_warning" ]]; then
  echo ""
  echo "⚠ Design system files are out of date:"
  echo "  design-tokens.json was modified after generated files."
  echo "  Run \`/design sync\` before committing."
  echo ""
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 2: Get staged code files
# ---------------------------------------------------------------------------

# Get staged files (Added, Copied, Modified, Renamed)
staged_files=()
while IFS= read -r file; do
  staged_files+=("$file")
done < <(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)

if [[ ${#staged_files[@]} -eq 0 ]]; then
  exit 0
fi

# Filter to code files, excluding skip files
code_files=()
for file in "${staged_files[@]}"; do
  is_code_file "$file" || continue
  is_skip_file "$file" && continue
  # Only check files that exist on disk (could be renamed/deleted edge case)
  [[ -f "$file" ]] || continue
  code_files+=("$file")
done

if [[ ${#code_files[@]} -eq 0 ]]; then
  exit 0
fi

# ---------------------------------------------------------------------------
# Step 3: Scan for hardcoded color values
# ---------------------------------------------------------------------------

drift_lines=()

for file in "${code_files[@]}"; do
  # Read the file line by line with line numbers
  lineno=0
  while IFS= read -r line; do
    lineno=$((lineno + 1))

    # Check for hex colors: #[0-9a-fA-F]{3,8}
    # Use grep -oE to find all matches on the line, then iterate
    if echo "$line" | grep -qE '#[0-9a-fA-F]{3,8}'; then
      # Extract matches; skip if inside a URL (contains ://)
      if ! echo "$line" | grep -qE '://[^\s]*#[0-9a-fA-F]{3,8}'; then
        while IFS= read -r match; do
          drift_lines+=("  $file:$lineno — found hardcoded color $match")
        done < <(echo "$line" | grep -oE '#[0-9a-fA-F]{3,8}' || true)
      fi
    fi

    # Check for rgb() / rgba()
    if echo "$line" | grep -qE 'rgba?\([[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+'; then
      while IFS= read -r match; do
        drift_lines+=("  $file:$lineno — found hardcoded color $match")
      done < <(echo "$line" | grep -oE 'rgba?\([[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+[^)]*\)?' || true)
    fi

    # Check for hsl() / hsla()
    if echo "$line" | grep -qE 'hsla?\([[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+%?[[:space:]]*,[[:space:]]*[0-9]+%?'; then
      while IFS= read -r match; do
        drift_lines+=("  $file:$lineno — found hardcoded color $match")
      done < <(echo "$line" | grep -oE 'hsla?\([[:space:]]*[0-9]+[[:space:]]*,[[:space:]]*[0-9]+%?[[:space:]]*,[[:space:]]*[0-9]+%?[^)]*\)?' || true)
    fi

  done < "$file"
done

# ---------------------------------------------------------------------------
# Step 4: Report
# ---------------------------------------------------------------------------

if [[ ${#drift_lines[@]} -eq 0 ]]; then
  exit 0
fi

echo ""
echo "⚠ Design token drift detected in staged files:"
echo ""
for line in "${drift_lines[@]}"; do
  echo "$line"
done
echo ""
echo "Run \`/design check\` to analyze, or \`/design sync\` to fix."
echo "To bypass: git commit --no-verify"
echo ""

exit 1
