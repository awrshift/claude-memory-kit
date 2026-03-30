---
name: gemini
description: Use when calling Gemini models for second opinions, analysis, code review, data extraction, or deep reasoning. Use for framework research, fact verification, cross-model validation. Use when you need an independent opinion from a different model family, when evaluating hypotheses, or when the user asks to consult Gemini. Also use when user says "ask Gemini", "second opinion", "cross-validate", "check with Gemini", or any request involving Google AI models.
allowed-tools: Bash
---

# Gemini SDK CLI

Direct Google GenAI SDK calls via Python subprocess. Different model family = different blind spots from Claude.

## Prerequisites

1. Install the SDK: `pip install google-genai`
2. Get a Google API key from [Google AI Studio](https://aistudio.google.com/apikey)
3. Set `GOOGLE_API_KEY` in your project `.env` or export it:

```bash
export GOOGLE_API_KEY="your-key-here"
# Or source from .env:
set -a && source .env && set +a
```

## Quick Reference

```bash
SCRIPT=~/.claude/skills/gemini/gemini.py

# Quick question (Gemini 3 Flash, cheap + fast)
python3 $SCRIPT ask "prompt"

# Second opinion (Gemini 3.1 Pro, high thinking)
python3 $SCRIPT second-opinion "question" --context "context"

# Web-grounded answer (Gemini searches Google before responding)
python3 $SCRIPT ask "What is the latest version of Next.js?" --grounded

# Web-grounded second opinion (real-time facts + critical analysis)
python3 $SCRIPT second-opinion @prompt.txt --grounded --save output.md

# Deep reasoning (Gemini 3.1 Pro, high thinking)
python3 $SCRIPT think "prompt"

# Save response to file
python3 $SCRIPT second-opinion "question" --save output.md

# Read prompt from file (avoids shell escaping for long prompts)
python3 $SCRIPT second-opinion @prompt.txt --save output.md

# Multimodal — send images with any command (Gemini is natively multimodal)
python3 $SCRIPT ask "Describe this UI" --image screenshot.png
python3 $SCRIPT second-opinion "Compare these designs" --image our-site.png --image reference.png
python3 $SCRIPT ask "What accessibility issues?" --image page.png --save a11y-review.md
```

## Image Support (Multimodal)

Gemini 3.x models are natively multimodal. Use `--image` (repeatable) to send images:

```bash
# Single image — design review, describe, analyze
python3 $SCRIPT ask "Rate this UI design 1-10" --image hero.png

# Multiple images — visual diff, before/after comparison
python3 $SCRIPT second-opinion @review-prompt.txt \
  --image current-site.png \
  --image reference-site.png \
  --save design-review.md

# JSON scoring with images
python3 $SCRIPT ask "Score typography alignment" --image site.png --json-mode
```

Supported formats: PNG, JPEG, WebP, GIF. Max ~20MB per request total.
Use cases: design review, visual QA, screenshot diff, accessibility audit, UI critique.

### Visual Design Review Pipeline

Proven workflow for comparing your site against a design reference:

```bash
# 1. Capture screenshots
# Our site (localhost) — via playwright:
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={'width': 1440, 'height': 900})
    page.goto('http://localhost:3000/')
    page.wait_for_timeout(3000)
    page.screenshot(path='/tmp/our-site.png')
    b.close()
"

# Reference site — via Firecrawl MCP:
# firecrawl_scrape(url, formats:["screenshot"]) → download PNG

# 2. Send both to Gemini
python3 $SCRIPT second-opinion @review-prompt.txt \
  --image /tmp/our-site.png \
  --image /tmp/reference.png \
  --save /tmp/design-review.md

# 3. Score targets: Typography ≥7, Spacing ≥7, Hierarchy ≥7, Polish ≥7
# If any < 7 → apply fixes → re-screenshot → re-verify (max 2 iterations)
```

## Commands

| Command | Default Model | System Instruction | Use When |
|---------|---------------|-------------------|----------|
| `ask` | 3-flash-preview | none | Quick questions |
| `second-opinion` | **3.1-pro-preview** | Critical reviewer | Decisions, validation |
| `analyze` | 3-flash-preview | Data analyst | CSV, patterns |
| `review` | 3-flash-preview | Code reviewer | Code quality |
| `extract` | 3.1-flash-lite | JSON extractor | Structured data |
| `think` | **3.1-pro-preview** | none | Deep reasoning (high thinking) |

## Arguments

| Arg | Short | Description |
|-----|-------|-------------|
| `--model` | `-m` | Override model |
| `--context` | `-c` | Additional context (second-opinion, analyze) |
| `--thinking` | `-t` | Level: minimal/low/medium/high (Gemini 3.x) |
| `--system` | `-s` | Override system instruction |
| `--save` | | Save response to file |
| `--grounded` | `-g` | Enable Google Search grounding — Gemini searches the web before answering |
| `--temp` | | Temperature: 0.0-2.0 (default 1.0, **keep default for Gemini 3**) |
| `--top-p` | | Top-p nucleus sampling: 0.0-1.0 (default 0.95) |
| `--top-k` | | Top-k sampling (default ~40) |
| `--max-tokens` | | Max output tokens: 1-65536 (default model max 64K) |
| `--json-mode` | | Force structured JSON output |
| `--seed` | | Seed for reproducible output |
| `--focus` | | Focus area for review |
| `--json` | | Raw JSON output (for piping) |
| `@file` | | Read prompt from file instead of inline |

## Parallel Execution

Run multiple calls simultaneously via background Bash:

```bash
python3 $SCRIPT second-opinion @aspect1.txt --save aspect1-response.md &
python3 $SCRIPT second-opinion @aspect2.txt --save aspect2-response.md &
python3 $SCRIPT second-opinion @aspect3.txt --save aspect3-response.md &
wait
```

## Critical Evaluation Rule

Gemini's `second-opinion` is an INPUT for decision-making, NOT the decision itself. After every `second-opinion` call:

1. **Challenge each recommendation** — is this fact or speculation?
2. **Check for missing context** — Gemini doesn't see codebase, prior decisions, or constraints
3. **Verify numbers** — predictions like "90% speedup" are estimates, not measurements
4. **Look for blind spots** — implementation complexity, side effects, existing code
5. **Present critical assessment to user** — "Gemini said / My evaluation / Reason" table

**Workflow:** Gemini recommends -> Claude evaluates critically -> present BOTH to user -> user decides

## Key Parameter Rules (Gemini 3)

- **Temperature 1.0 is mandatory** — Google strongly recommends keeping default. Lower values cause looping/degradation in reasoning tasks.
- **thinking_level replaces thinking_budget** — Do NOT combine both (-> error). Pro: low/medium/high. Flash: minimal/low/medium/high.
- **JSON mode** — Use `--json-mode` for guaranteed valid JSON output.
- **Grounding is a Tool** — `--grounded` adds Google Search as a tool, not a parameter.

## References

- **Models, pricing, thinking levels**: `references/models.md`
- **All API parameters with ranges and defaults**: `references/parameters.md`
