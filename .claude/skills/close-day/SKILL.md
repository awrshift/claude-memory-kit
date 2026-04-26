---
name: close-day
description: End-of-day audit ritual — synthesize sessions into daily log, audit patterns against MEMORY.md and reference skills, propose promotions verbally, write approved patches
---

# /close-day — The audit ritual

You are closing the user's working day. This is NOT just «dump today into a file». This is the **audit moment** where you inspect what the day produced, compare it to accumulated memory, and propose what should grow into the user's reference skills (`.claude/skills/<role>-guidance/SKILL.md`).

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

Also update `context/next-session-prompt.md` (NSP) with the immediate-action handoff: «Завтра: продолжить X. Открытые вопросы: Y, Z.»

### Phase 2: AUDIT

Now the ritual. Read:

1. **Today's daily log** (just written)
2. **`MEMORY.md`** — date-tagged patterns from prior sessions
3. **Relevant reference skills** — `.claude/skills/<role>-guidance/SKILL.md` for whichever roles were active today (design-guidance if design work, editorial-guidance if copy work, etc.)

Compare. Look for three kinds of signals:

#### Signal A: Cross-session repetition
A pattern you noticed today matches a date-tagged entry in `MEMORY.md` from earlier days. Example: today user rejected "em-dash in short copy" — and MEMORY.md shows they rejected the same thing Tuesday and last Friday.

**What to do:** Propose adding to the relevant reference skill.

> «Заметил: ты три раза на этой неделе отклонил тексты с em-dash в коротких фразах. Похоже на устойчивое правило. Добавить в `editorial-guidance` как "em-dash запрещён в UI-копии ≤20 слов"? Могу сразу написать — подтверди.»

#### Signal B: New strong preference
User expressed a clear preference today, even once, but it was emphatic. Example: «ненавижу когда превью размытые — никогда так не делай».

**What to do:** Propose adding to the relevant reference skill (often `founder-profile`) with "observed once but emphatic" note.

> «Ты чётко сказал что размытые превью недопустимы. Даже хотя это первый раз за наш проект — стоит ли зафиксировать сейчас в `founder-profile`, чтобы я не забыл? Или подождать повтора?»

#### Signal C: Contradiction with existing canon
Today you did something that contradicts an existing reference-skill entry. Example: `design-guidance` says "warm palette default" but today user insisted on cold palette for a specific page.

**What to do:** Surface the tension. Don't silently update — ask.

> «Сегодня мы делали страницу X в холодной палитре. В `design-guidance` у нас "warm palette default for editorial pages". Это исключение или нужно обновить правило?»

#### Signal D: Potential reference-skill split
If during audit you notice a reference skill has grown very large (> 500 lines, Anthropic's guidance for SKILL.md) or contains multiple clearly independent topics, mention it. Don't do the split here — that's `/memory-audit`'s job. Just flag.

> «Кстати, `design-guidance` выросла до 720 строк и внутри вижу три темы: типографика, цвет, анимация. Стоит запустить `/memory-audit` чтобы предложить разделение?»

### Phase 3: EXECUTE APPROVED PATCHES

For each signal user approved verbally:

1. **Write the patch.** Open the reference-skill SKILL.md file, add the new entry at the right section, or update MEMORY.md, or modify NSP — whatever was proposed.
2. **Confirm briefly to user.** «Записал.»
3. **Commit mentally to what you DIDN'T approve.** If user said «не сейчас», DON'T write it. Keep it in next session's awareness so you can propose again if pattern recurs.

### What you do NOT do

- **Don't ask user to open any file.** Never say «открой design-guidance и добавь...». Say «я запишу — подтверди?».
- **Don't promote to `.claude/rules/` unilaterally.** That requires 6+ months of stability. You can PROPOSE it on a future `/close-day` after enough history, but not today.
- **Don't write patches without explicit verbal approval.** «да», «угу», «хорошо», «го», «запиши» all count. Silence or ambiguity does not — ask again.
- **Don't surface more than 3-4 candidates per `/close-day`.** Pick the most signal-rich. Overwhelming the user with proposals kills the ritual.
- **Don't repeat proposals user already rejected.** If on last week's `/close-day` user said «не сейчас» to adding X — don't propose X again unless there's new evidence (another repetition, related pattern, etc.).

## Session definition (context for your audit)

A «session» is **one Claude context window**. As you accumulate context (~300-500k tokens of 1M), you ask user to save state and start fresh. A day can have 3-10 sessions.

When synthesizing today's daily log, include ALL sessions of the day, not just the current one. You may need to read prior NSP states or session-start hook snapshots to know what earlier sessions contained. If uncertain, ask user: «сколько раз мы сегодня перезапускались? Что было в утренней сессии?».

## Output format

When the user types `/close-day`, respond in this shape:

```
Синтезирую день...
[brief note: X сессий, проекты Y, Z, основные решения]

daily/2026-04-24.md записан.
NSP обновлён.

Аудит:

1. [Signal description]
   Предложение: [what to add where]
   Добавить? [да/нет]

2. [Signal description]
   ...

(Ждёт ответа пользователя по каждому пункту)
```

After user confirms each, execute patches and confirm briefly.

## Edge cases

- **User says «отмена» or «не сейчас» partway through** — acknowledge, stop the ritual, nothing is lost. Today's daily + NSP is already saved. Audit candidates can be revisited next time.
- **Nothing notable happened today** — the audit may surface zero candidates. That's fine. Just synthesize the daily and confirm: «Короткий день, паттернов для промоушена не вижу. Завершено.»
- **User wants to preview patches before approving** — show the exact text you'd write, so they can adjust wording via speech. «Собирался записать "X". Устраивает формулировка?».
- **Current session still has active work** — if user types /close-day while mid-task, clarify: «Хочешь закрыть день сейчас, с учётом незаконченных задач? Или доделать и потом?».

## Why this ritual exists

Memory Kit's invariant: **user only talks, agent writes**. Prior versions tried to automate promotion detection with background scripts — unreliable + violated the invariant by implicitly pushing users to edit files. `/close-day` replaces that with an agent-in-the-loop ritual: the agent has full conversational context at end of day, can spot patterns a script would miss, and does the writing itself.

The user's job is to **notice what they notice** during the day's work. Yours is to **catch it and structure it**.
