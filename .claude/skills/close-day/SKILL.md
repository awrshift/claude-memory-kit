---
name: close-day
description: End-of-day audit ritual — synthesize sessions into daily log, audit patterns against MEMORY.md and existing concepts/rules, propose promotions verbally, write approved patches
---

# /close-day — The audit ritual

You are closing the user's working day. This is NOT just "dump today into a file". This is the **audit moment** where you inspect what the day produced, compare it against accumulated memory, and propose what should grow into the user's knowledge base or rules.

## Your goal in two phases

### Phase 1: SYNTHESIZE

Create `daily/YYYY-MM-DD.md` (today's date in ISO format). Include:

- **Session count and approximate total duration.** How many times did the user start a fresh session today? Rough total time.
- **Projects worked on.** Which `projects/<name>/` were active today.
- **Key decisions made.** What did the user decide today that will shape future work?
- **Artifacts produced.** Code shipped, copy drafted, design finalized, research completed.
- **Open threads.** What's left unfinished and should be picked up next session.
- **Notable moments.** Things the user reacted strongly to (positive or negative). These are high-signal for the audit.

Format: concise, structured markdown. This file is the chronological record. Target 200-500 words.

Also update `context/next-session-prompt.md` (NSP) with the immediate-action handoff: "Tomorrow: continue X. Open questions: Y, Z."

### Phase 2: AUDIT

Now the ritual. Read:

1. **Today's daily log** (just written)
2. **`MEMORY.md`** — date-tagged patterns from prior sessions
3. **Existing knowledge articles** — `knowledge/concepts/*.md`
4. **Existing rules** — `.claude/rules/*.md`

Compare. Look for three kinds of signals:

#### Signal A: Cross-session repetition
A pattern you noticed today matches a date-tagged entry in `MEMORY.md` from earlier days. Example: today user rejected "em-dash in short copy" — and MEMORY.md shows they rejected the same thing Tuesday and last Friday.

**What to do:** Propose codifying it.

> "Noticed: you've rejected em-dashes in short copy three times this week. Looks like a stable preference. Codify as a rule in `.claude/rules/copy-style.md`: 'em-dash forbidden in UI copy ≤20 words'? Or as a section in `knowledge/concepts/copy-style.md` if you want the rationale alongside? I can write it — confirm."

#### Signal B: New strong preference
User expressed a clear preference today, even once, but it was emphatic. Example: "I hate blurry previews — never do that".

**What to do:** Propose adding it. If emphatic enough, propose a rule directly. Otherwise add to MEMORY.md and wait for repetition.

> "You said clearly that blurry previews are unacceptable. Even though it's the first time in this project — should we lock it in `.claude/rules/visual-quality.md` now, or save to MEMORY and wait for a repeat?"

#### Signal C: Contradiction with existing canon
Today you did something that contradicts an existing rule or concept article. Example: `concepts/design-tokens.md` says "warm palette default" but today user insisted on a cold palette for a specific page.

**What to do:** Surface the tension. Don't silently update — ask.

> "Today we built page X in a cold palette. `concepts/design-tokens.md` says 'warm palette default for editorial pages'. Is this an exception or should the rule be updated?"

#### Signal D: Article-worthy topic emerged
Today's work surfaced a topic that's been touched several times across `daily/*.md` with accumulating detail (5+ times) and the facts are stable.

**What to do:** Propose compiling a `knowledge/concepts/<topic>.md` article via `/memory-compile`.

> "Topic 'Stripe webhook patterns' came up again today — fifth time across 3 weeks. Want me to compile a `knowledge/concepts/stripe-webhooks.md` article that pulls together the rationale from all those daily logs?"

### Phase 3: EXECUTE APPROVED PATCHES

For each signal user approved verbally:

1. **Write the patch.** Open the target file, add the new entry at the right section, or update MEMORY.md, or modify NSP — whatever was proposed.
2. **Confirm briefly to user.** "Saved."
3. **Commit mentally to what you DIDN'T approve.** If user said "not now", DON'T write it. Keep it in next session's awareness so you can propose again if pattern recurs.

### What you do NOT do

- **Don't ask user to open any file.** Never say "open the rules file and add...". Say "I'll write it — confirm?".
- **Don't promote to `.claude/rules/` casually.** Rules are forever. A pattern needs to be either: emphatic AND clearly mechanical, OR repeated 3+ times in MEMORY without contradiction. Otherwise prefer `knowledge/concepts/<topic>.md` (which can be edited later) or a longer wait in MEMORY.
- **Don't write patches without explicit verbal approval.** "yes", "ok", "go", "save it" all count. Silence or ambiguity does not — ask again.
- **Don't surface more than 3-4 candidates per `/close-day`.** Pick the most signal-rich. Overwhelming the user with proposals kills the ritual.
- **Don't repeat proposals user already rejected.** If on last week's `/close-day` user said "not now" to adding X — don't propose X again unless there's new evidence (another repetition, related pattern, etc.).

## Session definition (context for your audit)

A "session" is **one Claude context window**. As you accumulate context (~300-500k tokens of 1M), you ask user to save state and start fresh. A day can have 3-10 sessions.

When synthesizing today's daily log, include ALL sessions of the day, not just the current one. You may need to read prior NSP states or session-start hook snapshots to know what earlier sessions contained. If uncertain, ask user: "how many times did we restart today? What was in the morning session?".

## Output format

When the user types `/close-day`, respond in this shape:

```
Synthesizing the day...
[brief note: X sessions, projects Y, Z, key decisions]

daily/2026-04-24.md written.
NSP updated.

Audit:

1. [Signal description]
   Proposal: [what to add where]
   Add? [yes/no]

2. [Signal description]
   ...

(Waits for user response to each item)
```

After user confirms each, execute patches and confirm briefly.

## Edge cases

- **User says "cancel" or "not now" mid-ritual** — acknowledge, stop the ritual, nothing is lost. Today's daily + NSP is already saved. Audit candidates can be revisited next time.
- **Nothing notable happened today** — the audit may surface zero candidates. That's fine. Just synthesize the daily and confirm: "Quiet day, no promotion candidates. Done."
- **User wants to preview patches before approving** — show the exact text you'd write, so they can adjust wording via speech. "Was going to write: 'X'. Wording OK?".
- **Current session still has active work** — if user types /close-day mid-task, clarify: "Close out the day now, including unfinished work? Or finish first?".

## Why this ritual exists

Memory Kit's invariant: **user only talks, agent writes**. Prior versions tried to automate promotion detection with background scripts — unreliable + violated the invariant by implicitly pushing users to edit files. `/close-day` replaces that with an agent-in-the-loop ritual: the agent has full conversational context at end of day, can spot patterns a script would miss, and does the writing itself.

The user's job is to **notice what they notice** during the day's work. Yours is to **catch it and structure it**.
