---
name: brainstorm
description: "Multi-round brainstorm between Claude and Gemini that turns a single idea into one converged, actionable decision. Use this skill whenever the user wants to brainstorm, ideate, explore strategic options, compare approaches, or think through a decision with multiple viable paths. Also trigger when user says 'brainstorm', 'let's think through options', 'ideation session', 'explore this idea with Gemini', 'brainstorm with Gemini', 'diverge and converge', or wants more than a simple second opinion — a real multi-round dialogue between two top models. This is the upgrade from a single Gemini second-opinion call to a structured 3-round adversarial dialogue."
allowed-tools: Bash, Write, Read, Edit, WebSearch
---

# 3-Round Brainstorm: Claude x Gemini (v2.1 — Two-Layer Architecture)

Two-layer model architecture: **Flash researches, Pro reasons.** Claude orchestrates both.

```
                  Claude (orchestrator)
                     |         |
        Phase 0.5    |         |    R1 / R2 / R3
        Phase 3.5    |         |
                     v         v
              Flash-Lite --grounded    Pro (no grounding)
              (research layer)    (reasoning layer)
                     |                  ^
                     +--Verified Context-+
```

**Flash-Lite** (`gemini-3.1-flash-lite-preview`, $0.25/1M, 381 tok/s) searches the web and produces verified facts.
**Pro** (`gemini-3.1-pro-preview`, $2/1M, #1 reasoning) reasons on those facts without wasting tokens on search.
**Claude** runs its own WebSearch in parallel during Phase 0.5 and Phase 3.5.

## Version History

- **v1:** 3 rounds, no web access. Result: 2/6 decisions invalidated by stale knowledge (A488).
- **v2:** Added `--grounded` to all Pro calls. Problem: Pro wastes thinking tokens on search processing.
- **v2.1:** Two-layer split. Flash does research, Pro focuses on reasoning. Faster, cheaper, better quality.

## Why two layers beat one

In v2, Pro with `--grounded` does both searching AND thinking. But search processing is low-value work — it doesn't need deep reasoning to check "what version is Next.js?" Pro's thinking tokens are expensive and should be spent on challenging ideas, finding blind spots, and synthesizing arguments — not on parsing search results.

Splitting the layers means:
- Flash (grounded): ~$0.15/1M input, 3-5 sec per query, returns verified facts
- Pro (ungrounded): all thinking tokens go to critical analysis, gets pre-verified context

## Process

### Phase 0: Gather Context

Before writing Round 1, check if the user provided enough context. A good R1 prompt needs:
- What exists (product, tech, assets)
- Hard constraints (time, team size, budget, regulatory)
- The goal (what decision needs to be made)

If any of these are missing, ask the user before starting. A brainstorm with vague input produces vague output.

### Phase 0.5: GROUNDING (dual research — Claude + Flash)

**This phase is mandatory.** Extract all technology names, frameworks, APIs, and services from the context.

**Two parallel research tracks:**

1. **Claude** runs 5-7 WebSearch queries (versions, pricing, compatibility, licenses)
2. **Flash** (grounded) gets a batch research prompt covering the same technologies

Run both in parallel. Merge results into a "Verified Context" block.

**Flash research prompt** (saved to `/tmp/brainstorm-{agent}-ground.txt`):
```
Research the following technologies and provide CURRENT (2026) facts for each.
For each one, include: current version, pricing/free tier, license, known issues.
Use Google Search to verify — do NOT rely on training data.

Technologies to research:
1. [Technology A]
2. [Technology B]
3. [Technology C]
...

Output format per technology:
- Name: current version, release date
- Pricing: free tier details, paid plans
- License: open-source? which license?
- Compatibility: works with [other stack items]?
- Red flags: any known issues, deprecations, EOL dates
```

**Flash call:**
```bash
python3 ~/.claude/skills/gemini/gemini.py ask @/tmp/brainstorm-${AGENT}-ground.txt \
  --grounded --save /tmp/brainstorm-${AGENT}-ground-response.md
```

**Merge:** Claude reads Flash's response + own WebSearch results, resolves conflicts (if any), produces final Verified Context block:

```
## Verified Context (dual-checked: Claude WebSearch + Flash Google Search)
- Next.js: v16.1.6 (Oct 2025 release, 16.2 canary). Source: nextjs.org, confirmed by Flash
- Clerk: Free 10K MAU. Pro $25/mo. @clerk/nextjs@6.36.7. Source: clerk.com
- Drizzle: v0.45.x, zero-codegen, Neon HTTP driver. Source: drizzle.team
- CONFLICT: [if Claude and Flash disagree, note both and flag for R1]
```

### Phase 1: DIVERGE (Round 1)

**Claude writes** a prompt with:
1. **Verified Context** from Phase 0.5 (at the top)
2. Full context (what exists, constraints, goals)
3. Initial honest assessment (strengths, weaknesses)
4. Instructions for Gemini to challenge, not agree

**Pro is called WITHOUT `--grounded`** — it receives pre-verified facts and focuses entirely on critical thinking.

**R1 prompt template:**
```
You are acting as an adversarial brainstorming partner. I am the lead developer framing the problem.
This is Round 1 of a 3-round brainstorm.
Your job is NOT to be agreeable -- challenge, flip assumptions, add angles I haven't considered.

IMPORTANT: The "Verified Context" section below has been web-checked moments ago.
Treat these facts as ground truth. Focus your energy on STRATEGY and ARCHITECTURE,
not on verifying versions or prices — that's already done.
If you want to recommend a technology NOT in the verified list, flag it clearly
so we can verify it before Round 2.

## Verified Context (web-checked)
[Include Phase 0.5 merged findings]

## Context
[Describe the idea, what you have, constraints, goals]

## My Initial Assessment
[Your honest evaluation: strengths, weaknesses, open questions]

## What I want from you (Round 1)
1. Challenge my framing -- what am I NOT seeing?
2. Propose 3-5 alternative angles/applications
3. Kill at least 1 idea I proposed (with reasoning)
4. Add 1 wildcard idea I haven't considered
5. If you recommend a NEW technology not in Verified Context, flag it for verification
```

**After R1:** If Gemini recommended new technologies not in Verified Context, run a quick Flash grounded check on those before proceeding to R2. Tell the user what new angles Gemini generated.

**Mid-round verification** (only if R1 introduced new technologies):
```bash
python3 ~/.claude/skills/gemini/gemini.py ask \
  "Verify these technologies: [new tech from R1]. Current version, pricing, license, compatibility with [our stack]." \
  --grounded --save /tmp/brainstorm-${AGENT}-r1-verify.md
```

### Phase 2: DEEPEN (Round 2)

**Claude reads R1 response**, then writes R2 prompt that:
1. Summarizes Gemini's ideas (including any mid-round verification results)
2. **Kills ideas with concrete arguments** (synthesize, do NOT copy-paste raw R1 output)
3. Adds real-world constraints (time, solo dev, regulatory, etc.)

**Pro is called WITHOUT `--grounded`.**

**R2 prompt template:**
```
This is Round 2 of our brainstorm. Here's what you said in Round 1, followed by my critical evaluation.
Your job now: STRESS-TEST my pushback, pick the 2 strongest surviving threads, and kill everything else.

All technology claims have been web-verified. Focus on architecture and strategy.

## Your Round 1 Key Ideas (summary)
[Summarize Gemini's R1 ideas — synthesize, don't copy-paste]

## My Critical Evaluation
[For each idea: KILL or KEEP with concrete reasoning]

## Constraints you must respect
[Time, resources, regulatory, skill gaps]

## What I want from you (Round 2)
1. Where am I wrong in my kills? You get ONE sentence per killed idea to defend it.
2. Pick the 2 strongest surviving threads (from ideas I kept).
3. For each survivor: concrete 2-week plan.
4. Propose 1 new idea that combines surviving threads.
```

**After R2 — USER CHECK-IN (mandatory):** Present the 2-3 surviving ideas to the user and ask: "Do you have a preference before we lock one in, or should I proceed to Round 3?" This prevents the models from converging on something the user doesn't care about.

### Phase 3: CONVERGE (Round 3)

**Claude synthesizes** both rounds, raises one remaining objection. Incorporate user preference from check-in if given.

**Pro is called WITHOUT `--grounded`.**

**R3 prompt template:**
```
This is Round 3 (FINAL) of our brainstorm. Time to converge.

## What survived 2 rounds
[List 2-3 artifacts with descriptions — synthesize, don't copy-paste]

## My objection
[Raise one remaining concern]

## What I want from you (Round 3 -- FINAL)
1. Address my objection -- defend or kill.
2. Pick ONE primary action (not 2, not 3 -- ONE).
3. Sequence: primary -> secondary -> kill list.
4. Write the 1-sentence pitch for the winner.
5. Give a concrete timeline (hours/days, not weeks).
6. Define go/no-go signal.
```

### Phase 3.5: FACT-CHECK (dual verification of final decisions)

After R3, extract all technology decisions, pricing claims, and compatibility assumptions from the final recommendation.

**Two parallel verification tracks** (same as Phase 0.5):

1. **Claude** runs WebSearch on each claim
2. **Flash** (grounded) gets a verification prompt with all claims

**Flash fact-check prompt:**
```
Verify each of these claims using Google Search. For each one, state:
CONFIRMED (with source) or INCORRECT (with correction and source).

Claims to verify:
1. [Claim from R3]
2. [Claim from R3]
...
```

**Output format (merged from both tracks):**

| Claim | Claude WebSearch | Flash Google Search | Status |
|-------|-----------------|-------------------|--------|
| Clerk free 10K MAU | clerk.com: confirmed | Confirmed | OK |
| Drizzle zero-codegen | drizzle.team: confirmed | Confirmed | OK |
| Firecrawl free 500 pages | firecrawl.dev: confirmed | Says 100 pages | CONFLICT — investigate |

If any claim is invalidated or conflicted, flag it and note the correction. Include the fact-check table in the final synthesis.

### Phase 4: Synthesize

Read all 3 responses + fact-check results and produce:

1. **Summary table:**

| Round | Claude Role | Gemini Model | Result |
|-------|------------|-------------|--------|
| Phase 0.5: GROUND | WebSearch (parallel) | Flash-Lite --grounded | Verified Context |
| R1: DIVERGE | Thesis + assessment | **Pro** (ungrounded) | N ideas on table |
| R1.5: VERIFY | — | Flash-Lite --grounded (if needed) | New tech verified |
| R2: DEEPEN | Kill with arguments | **Pro** (ungrounded) | 2-3 survivors |
| R3: CONVERGE | Objection | **Pro** (ungrounded) | 1 concrete action |
| Phase 3.5: CHECK | WebSearch (parallel) | Flash-Lite --grounded | X/Y claims verified |

2. **Final recommendation** — the ONE action with timeline
3. **Fact-check results** — merged verification table
4. **Kill list** — everything considered and rejected (with reasons)

## Execution

### File naming convention

**All temp files MUST include the agent ID** to prevent collisions when multiple agents brainstorm in parallel.

Pattern: `/tmp/brainstorm-{agent}-{phase}.txt` and `/tmp/brainstorm-{agent}-{phase}-response.md`

Where `{agent}` is the agent's identifier from the project (e.g., `rnd`, `cmo`, `seo-geo`, `qa`). If no agent ID is defined, use the project directory name.

### Model assignment

| Phase | Model | Grounded? | Why |
|-------|-------|-----------|-----|
| Phase 0.5 (research) | `gemini-3.1-flash-lite-preview` | YES | Cheapest ($0.25/1M), fastest (381 tok/s), only needs facts |
| R1, R2, R3 (reasoning) | `gemini-3.1-pro-preview` | NO | Deep thinking on pre-verified facts |
| R1.5 mid-verify (if needed) | `gemini-3.1-flash-lite-preview` | YES | Quick check of new technologies |
| Phase 3.5 (fact-check) | `gemini-3.1-flash-lite-preview` | YES | Final verification, cheapest |

### Sending prompts

```bash
set -a && source "$PROJECT_ENV" && set +a
SCRIPT=~/.claude/skills/gemini/gemini.py
AGENT="cmo"  # Replace with your agent ID: rnd, cmo, seo-geo, qa

# Phase 0.5: Flash-Lite grounded research
python3 $SCRIPT ask @/tmp/brainstorm-${AGENT}-ground.txt \
  -m gemini-3.1-flash-lite-preview --grounded --save /tmp/brainstorm-${AGENT}-ground-response.md

# R1: Pro reasoning (no grounding)
python3 $SCRIPT second-opinion @/tmp/brainstorm-${AGENT}-r1.txt \
  --save /tmp/brainstorm-${AGENT}-r1-response.md

# R1.5: Flash-Lite verify new tech (only if R1 introduced unverified tech)
python3 $SCRIPT ask "Verify: [new tech]" \
  -m gemini-3.1-flash-lite-preview --grounded --save /tmp/brainstorm-${AGENT}-r1-verify.md

# R2: Pro reasoning
python3 $SCRIPT second-opinion @/tmp/brainstorm-${AGENT}-r2.txt \
  --save /tmp/brainstorm-${AGENT}-r2-response.md

# R3: Pro reasoning
python3 $SCRIPT second-opinion @/tmp/brainstorm-${AGENT}-r3.txt \
  --save /tmp/brainstorm-${AGENT}-r3-response.md

# Phase 3.5: Flash-Lite fact-check
python3 $SCRIPT ask @/tmp/brainstorm-${AGENT}-factcheck.txt \
  -m gemini-3.1-flash-lite-preview --grounded --save /tmp/brainstorm-${AGENT}-factcheck-response.md
```

Where `$PROJECT_ENV` is the project's `.env` file containing `GOOGLE_API_KEY` and `$AGENT` is the agent identifier.

If a Gemini call fails (rate limit, API failure, timeout), retry once. If it fails again, stop and report the error to the user.

### Saving artifacts

- All prompts + responses in `/tmp/brainstorm-{agent}-*.txt` and `/tmp/brainstorm-{agent}-*-response.md`
- If brainstorm is about a project experiment, copy all artifacts to the experiment directory so they survive /tmp cleanup

## Key Principles

1. **Flash researches, Pro reasons** — never waste Pro's thinking tokens on factual lookups.
2. **Web-ground before reasoning** — Phase 0.5 is mandatory. Stale facts poison all 3 rounds.
3. **Dual verification** — Claude WebSearch + Flash Google Search in parallel. Conflicts get flagged.
4. **Claude challenges between rounds** — not relay. Write kills with arguments, not just summaries.
5. **Synthesize, don't copy-paste** — R2 and R3 prompts should distill previous rounds, not dump raw output.
6. **Mid-round verify** — if Pro suggests a new technology in R1, Flash checks it before R2.
7. **Kill early, kill often** — R1: 7+ ideas, R2: cut to 3, R3: converge to 1.
8. **Constraints are ammunition** — real limits (time, solo dev, budget) kill impractical ideas.
9. **One action, not a strategy** — R3 must end with a single deliverable + timeline.
10. **Fact-check closes the loop** — Phase 3.5 catches anything grounding missed.
11. **Go/no-go criteria** — every brainstorm ends with "if X doesn't happen by Y, abandon."
12. **Show the user the journey** — present the funnel (7 -> 3 -> 1) so the user sees why the winner won.
13. **Additional rounds when needed** — 3 rounds is the default, not the limit. After R3 convergence, add R4+ rounds when: (a) the Go/No-Go test produces results that need Gemini evaluation, (b) new information invalidates R3 assumptions, or (c) the fact-check reveals a critical correction that changes the recommendation. Additional rounds follow the same Pro (ungrounded) model. Label them R4, R5, etc. with clear purpose: "R4: test results validation", "R5: pivot evaluation".
