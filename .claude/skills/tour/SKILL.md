---
name: tour
description: Interactive walkthrough of the Memory Kit system using the user's actual project files
---

# /tour — Interactive walkthrough

You are giving the user a guided tour of their Memory Kit. Use their actual files (not generic descriptions) so they see how the abstraction maps to concrete files.

## Tour structure (10-15 minutes)

### Stop 1 — CLAUDE.md (agent identity)
Open and read aloud the first few lines. Say: «Это мой мозг. Я читаю это на каждой сессии. Здесь написано кто я для этого проекта, как с тобой общаться.»

### Stop 2 — Session entry (NSP + backlog)
Open `context/next-session-prompt.md` and, if multi-project mode, `projects/<active>/BACKLOG.md`. Say: «А это — записка от вчерашнего себя (NSP) и план на сегодня (backlog). Это первое что я читаю, чтобы знать где мы остановились.»

### Stop 3 — Hot path (MEMORY.md)
Open `.claude/memory/MEMORY.md`. Say: «Это моя короткая память. Здесь date-tagged строки паттернов из последних сессий. Обновляется часто — иногда по ходу сессии, когда я замечаю что-то важное.»

### Stop 4 — Rules (.claude/rules/)
List any `.claude/rules/*.md` files. If folder is mostly empty, say: «Здесь будут жёсткие правила твоего проекта. "Не пиши X", "Всегда проверяй Y". Они подгружаются автоматически по ключевым словам. Сейчас пусто — появятся когда ты начнёшь диктовать правила.»

### Stop 5 — Reference skills (role wisdom)
List `.claude/skills/*-guidance/` directories. Open 1-2 (e.g. `design-guidance/SKILL.md`, `editorial-guidance/SKILL.md`). Say: «Это гайды для разных ролей. Дизайнер думает по-своему, редактор по-своему, маркетолог по-своему. Когда разговор касается дизайна — я автоматически подгружаю `design-guidance` (Claude Code сам это делает по описанию в frontmatter — `user-invocable: false` означает "только я могу их вызвать, не ты"). Пока они пустые шаблоны. Будут расти через `/close-day` — я буду предлагать, ты подтверждать голосом.»

### Stop 6 — Knowledge/concepts/
List `knowledge/concepts/*.md`. Say: «Это глубокая память с фактами. "Какой у нас скейл типографики", "Что мы знаем про SEO для ИИ". Это reference-статьи. Тоже пусто сейчас — заполнятся когда ты начнёшь работать над конкретными темами и я буду предлагать компиляции из daily.»

### Stop 7 — Daily/
List recent `daily/*.md`. Say: «Архив. Каждый день после `/close-day` я пишу сюда всё что сегодня произошло. Ты не открываешь эти файлы — но я могу искать по ним, если ты спросишь "когда мы это решили?".»

### Stop 8 — Projects/ (if multi-project)
List `projects/*/`. Say: «Каждый клиент — своя папка. В ней backlog задач + твои материалы по этому клиенту (брифы, гайды, референсы). Когда ты говоришь "работаем над client-a", я подгружаю именно эту папку.»

### Stop 9 — Operators
List slash commands. Say:
- «`/close-day` — в конце дня. Я соберу день в архив и предложу промоушен паттернов в reference skills (`design-guidance`, `editorial-guidance`, и т.д.).»
- «`/memory-compile` — иногда. Превращает дневники в тематические статьи в knowledge.»
- «`/memory-query` — когда хочешь найти что-то: "что мы решили про X". Ищу везде.»
- «`/memory-lint` — структурная проверка: битые ссылки, orphans, oversized reference skills. Запускаешь когда кажется что база запуталась.»
- «`/memory-audit` — проверяет не раздулся ли какой-то reference skill (> 500 строк). Если да — предлагает разделить по темам.»

### Stop 10 — The invariant
Close by restating: «Главное правило Memory Kit — ты только говоришь, я всё пишу. Не открывай эти файлы вручную. Если хочешь что-то добавить, запретить, изменить — просто скажи мне, я оформлю и спрошу подтверждение. Всё.»

## Adapting the tour

- If user already knows Memory Kit, you can skip stops and ask «где показать подробнее?»
- If project is fresh (all folders empty), say so explicitly: «Большинство файлов сейчас пустые. Это нормально. Будут заполняться через 2-3 недели активной работы.»
- If user asks a specific question mid-tour, answer it and return to the next stop.

## Do NOT

- Don't dump technical jargon. Translate all English file paths to Russian concepts.
- Don't skip the invariant at the end. It's the most important takeaway.
- Don't go file-by-file reading the full content. Hit the structure + purpose, not the details.
