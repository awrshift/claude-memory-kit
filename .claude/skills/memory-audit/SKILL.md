---
name: memory-audit
description: Structural health check — detect oversized reference skills and propose splits. Runs free grep-based size check then agent-in-session semantic clustering
---

# /memory-audit — Structural check with split proposals

Complement to `/close-day`. While `/close-day` audits for **promotion** (pattern → reference-skill entry), `/memory-audit` audits for **structure** (reference skills getting too big → split proposals).

## Two-phase mechanism

### Phase 1: Free size check (non-LLM)

Run the underlying lint script:

```bash
python3 .claude/memory/scripts/lint.py --audit-sizes
```

This lists all `.claude/skills/*-guidance/SKILL.md` files with line counts, flags any > 500 lines (Anthropic's recommended SKILL.md ceiling) as **candidates for split**. No LLM calls — pure file stat.

### Phase 2: Semantic clustering (you, in session)

For each flagged file:

1. Read the entire reference-skill file into context.
2. Group its sections/entries by topic. Look for groups where entries within a cluster cross-reference each other, but rarely reference entries in other clusters.
3. If you can identify **2-4 independent clusters**, propose a split to the user.
4. If the reference skill is large but thematically unified (all entries build on each other), report "big but coherent — no split needed yet".

### Proposal format

```
Проверил размер reference skills. Кандидаты на split:

1. design-guidance — 847 строк.
   Вижу 3 независимые темы:
   - типографика (14 entries)
   - цвет (18 entries)
   - анимация (9 entries)
   Они почти не ссылаются друг на друга. Предлагаю split
   на design-type-guidance / design-color-guidance / design-motion-guidance.
   Исходный design-guidance станет index-skill'ом с ссылками на детей.
   
   Делим? [да / не сейчас / покажи детали]

2. editorial-guidance — 612 строк.
   Темы: voice contract (12), rejected copy (24).
   Две темы, но не уверен — voice и rejects сильно
   переплетены. Предлагаю оставить, вернуться через месяц.
```

### Execute the split (on user «да»)

1. Create new skill directories with topical names: `.claude/skills/design-type-guidance/`, `.claude/skills/design-color-guidance/`, etc. Each gets its own `SKILL.md`.
2. Move entries by topic. Preserve all content — nothing is lost.
3. Each child gets its own YAML frontmatter: rich `description` (keyword-focused on the topical slice), `user-invocable: false` (inheriting from parent), optional `paths:` if it should be path-scoped.
4. Transform the original `design-guidance/SKILL.md` into an **index skill**:

```yaml
---
name: design-guidance
description: Index of design reference skills — typography, color, motion. Use for any design question; Claude will also auto-load the specific child skill matching the topic.
user-invocable: false
split-into: [design-type-guidance, design-color-guidance, design-motion-guidance]
---

# Design guidance (index)

This reference skill was split 2026-04-24 into three topic-specific sub-skills. Claude auto-loads the child whose description best matches the current task.

- **Typography** → `.claude/skills/design-type-guidance/SKILL.md`
- **Color** → `.claude/skills/design-color-guidance/SKILL.md`
- **Motion** → `.claude/skills/design-motion-guidance/SKILL.md`

Split preserved 847 original lines across three files.
```

5. Confirm briefly: «Готово. design-guidance разделён на 3 reference skill, исходный стал index-skill'ом. 847 строк сохранены все.»

### What you do NOT do

- **Don't split without verbal approval.** Grep-flagging alone never triggers a write. User must confirm.
- **Don't split if clusters aren't clear.** If topics interleave, say so and recommend deferring. Forced splits create more chaos than monolith.
- **Don't split < 500 lines.** That's noise. Let the reference skill grow until it genuinely warrants a split.
- **Don't split `founder-profile`.** That's the single most important reference skill, always loaded on non-trivial decisions. Even large, it stays one file.

## When to run

- When user feels their reference skills are getting «unweildy»
- Periodically (monthly or quarterly) as background hygiene
- Agent may suggest on `/close-day` if it notices a particularly bloated file: «Замечу: design-guidance разросся до 847 строк. Запустить `/memory-audit`?»

## Relationship to /close-day and /memory-lint

| Operator | What it checks | Frequency | LLM needed |
|---|---|---|---|
| `/close-day` | Promotion candidates (pattern → reference-skill entry) | Daily (end of working day) | Yes |
| `/memory-audit` | Oversized reference skills + semantic splits | On-demand or monthly | Partial (size check free; clustering uses LLM) |
| `/memory-lint` | Structural hygiene (broken links, sparse articles, orphans, oversized reference skills) | On-demand | No |

Three separate concerns, three separate operators.

## Why grep-size check is separate from semantic clustering

Size check is cheap and deterministic — it should run even when user isn't at keyboard, producing a text report. Semantic clustering needs full context and user judgment — only works in live session.

So: script handles size flagging (free), agent handles clustering (in conversation).
