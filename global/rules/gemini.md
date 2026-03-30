# Gemini Rules

## How to Call Gemini

Use the **gemini skill** (`~/.claude/skills/gemini/`). CLI via Bash subprocess.

```bash
SCRIPT=~/.claude/skills/gemini/gemini.py

# Quick question
python3 $SCRIPT ask "prompt"

# Second opinion (3.1 Pro, deep reasoning)
python3 $SCRIPT second-opinion "question" --context "context" --save output.md

# Read prompt from file (avoids shell escaping for long prompts)
python3 $SCRIPT second-opinion @prompt.txt --save output.md

# Visual review — send screenshots (multimodal)
python3 $SCRIPT second-opinion @prompt.txt --image site.png --image ref.png --save review.md
```

**Env required:** `set -a && source .env && set +a`

Full CLI reference: `~/.claude/skills/gemini/SKILL.md`

**Stability note:** Gemini 3.1 Pro occasionally returns 503 errors under load. If a call fails, retry once before switching to `ask` (uses Flash, more reliable).

## When to Use Gemini vs Claude Subagents

**Principle:** Claude subagents (Task tool) = DEFAULT. Gemini only where unique value.

### Claude subagents WIN (use Task tool):
- Code review (can READ files, follow imports)
- Codebase exploration (has Grep, Glob, Read)
- Deep reasoning (`Task(model="opus")`)
- Any task needing file I/O or project context

### Gemini WINS (use CLI skill):
- **Independent second opinion** — different model family = different biases
- **Quick stateless questions** — `ask` (<3s, cheap)
- **Fact-check verification** — cross-validate Claude's analysis
- **Visual design review** — `--image` for screenshot comparison (multimodal)
- **Parallel batch calls** — 4+ background processes via `&` + `wait`
- **Web-grounded research** — `--grounded` flag for real-time facts

## Critical Evaluation Rule

Gemini's `second-opinion` is an INPUT, NOT the decision itself.

After every `second-opinion` call:

1. **Challenge each recommendation** — is this fact or speculation?
2. **Check for missing context** — Gemini doesn't see codebase, prior decisions, or constraints
3. **Verify numbers** — predictions are estimates, not measurements
4. **Look for blind spots** — implementation complexity, side effects, existing code
5. **Present critical assessment to user** — "Gemini said / My evaluation / Reason"

**Workflow:** Gemini recommends -> Claude evaluates critically -> present BOTH to user -> user decides

## High-Value Triggers (when to call Gemini proactively)

### 1. Prompt Stress-Test
**Trigger:** Writing a new prompt template that controls core logic.
**Action:** Send draft to Gemini: "Identify how an LLM could misinterpret this. Find loopholes, missing constraints."
**Use Gemini's critique as input — do NOT accept Gemini's rewritten prompt** (prompt optimization is model-specific).

### 2. Architecture Split Detection
**Trigger:** A prompt is getting complex (>500 words, 5+ rules).
**Action:** Ask Gemini: "Is this prompt doing too much? Should any part be a separate step?"

### 3. Hypothesis Falsification
**Trigger:** You propose a heuristic hypothesis.
**Action:** Ask Gemini for 3 concrete scenarios where it fails.

### 4. Evaluation Rubric Check
**Trigger:** Designing evaluation criteria.
**Action:** Ask Gemini to critique for bias and edge case vulnerability.
**Why:** Claude designs metrics -> Claude evaluates = circular validation. Different model family breaks the loop.

### 5. Visual Design Review
**Trigger:** Any UI/visual change — colors, spacing, typography, layout.
**Action:** Screenshot our page + reference → `gemini.py second-opinion --image our.png --image ref.png`
**Score targets:** Typography ≥7, Spacing ≥7, Hierarchy ≥7, Polish ≥7. Loop if < 7 (max 2 iterations).
**Why:** Gemini natively multimodal — catches visual issues Claude can't see from code alone.
