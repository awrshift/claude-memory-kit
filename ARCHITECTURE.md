# Memory Kit v4 — Architecture

> Full architecture with rationale. Read after CLAUDE.md for depth.

## The core invariant

**User only talks. Agent captures, proposes, writes.** This is the one rule that makes everything else consistent.

If an architectural decision violates this invariant (e.g., «user should periodically review memory files and edit them»), it's wrong by definition.

## Layer map (what lives where)

v4 aligns tightly with Anthropic-canonical Claude Code primitives. Every layer maps to a native concept documented at `code.claude.com/docs`.

```
╔══════════════════════════════════════════════════════════════╗
║  SESSION ENTRY (loaded automatically)                        ║
║  ──────────────────────────────────────────────────────────  ║
║  context/next-session-prompt.md                              ║
║      ↓ "where we left off, what's next"                      ║
║  projects/<active>/BACKLOG.md                                ║
║      ↓ "today's task queue"                                  ║
╠══════════════════════════════════════════════════════════════╣
║  HOT PATH (always in context)                                ║
║  ──────────────────────────────────────────────────────────  ║
║  CLAUDE.md                  — agent identity (this)          ║
║  .claude/memory/MEMORY.md   — date-tagged patterns           ║
║  knowledge/index.md         — deep-memory catalog            ║
║  (+ every skill's `description` — body loads on invoke)      ║
╠══════════════════════════════════════════════════════════════╣
║  ON-TRIGGER (loaded when relevant)                           ║
║  ──────────────────────────────────────────────────────────  ║
║  .claude/rules/*.md             — short enforceable rules    ║
║                                   (unconditional or path-    ║
║                                   scoped via `paths:`)       ║
║  .claude/skills/<role>-guidance/                             ║
║    SKILL.md                     — reference skills           ║
║                                   (user-invocable: false;    ║
║                                   role wisdom auto-loaded    ║
║                                   on description match)      ║
║  .claude/skills/<task>/SKILL.md — task skills (user-         ║
║                                   invocable; /close-day,     ║
║                                   /deploy, etc.)             ║
║  knowledge/concepts/*.md        — deep reference articles    ║
║  projects/<active>/*.md         — client materials (PDFs,    ║
║                                   briefs, references)        ║
╠══════════════════════════════════════════════════════════════╣
║  CHRONOLOGICAL (grep-on-demand, not auto-loaded)             ║
║  ──────────────────────────────────────────────────────────  ║
║  daily/YYYY-MM-DD.md      — session logs by date             ║
╠══════════════════════════════════════════════════════════════╣
║  OPERATORS (invoked by user speech)                          ║
║  ──────────────────────────────────────────────────────────  ║
║  /close-day     end-of-day AUDIT ritual                      ║
║  /memory-compile  daily → knowledge/concepts                 ║
║  /memory-query    natural-language search                    ║
║  /memory-lint     structural health checks                   ║
║  /memory-audit    oversized reference skill detection        ║
║  /tour            interactive walkthrough                    ║
╚══════════════════════════════════════════════════════════════╝
```

## What each layer is FOR (and is NOT)

### CLAUDE.md — agent identity
**Is:** stable DNA of the project. Who the agent is, what tone, what's forbidden, how it thinks.
**Is not:** daily notes. Doesn't change often. Target ≤ 200 lines (Anthropic guidance).

### .claude/memory/MEMORY.md — hot cache
**Is:** date-tagged patterns that have already been noticed 2+ times. Short strings. Cross-session accumulator. First 200 lines / 25KB auto-loaded (Anthropic auto-memory contract).
**Is not:** full logs (those live in daily/). Not detailed articles.

### .claude/rules/*.md — rules
**Is:** mechanical constraints. «Не используй X», «Всегда проверяй Y». Short. Enforceable by grep/linter in principle. Can be `paths:`-scoped to apply only when working with matching files.
**Is not:** advice. Not judgment heuristics. Not role-specific wisdom (those are reference skills).

### .claude/skills/<role>-guidance/SKILL.md — reference skills (role wisdom)
**Is:** how a senior specialist in that role thinks. Judgment heuristics. Tacit knowledge. `user-invocable: false` + rich `description` → Claude auto-loads whenever the conversation matches the description.

**Example** (`design-guidance`):
> «Тёплые тона (sand, burgundy) читаются editorial. Холодные (cool grey, cobalt) — SaaS. На новых страницах всегда пробуем тёплую палитру первой.»

**Is not:** raw facts or reference data (those are concepts). Not enforceable rules (those are `.claude/rules/`). Not user-invocable workflows (those are task skills).

**This layer replaces the earlier draft's `playbooks/` directory.** Both serve the same purpose — role-based tacit wisdom. v4 uses reference skills because they are the native Anthropic primitive, which gives us auto-invocation via `description` matching for free (no custom routing tables) and lets Claude manage context budget automatically.

### .claude/skills/<task>/SKILL.md — task skills
**Is:** repeatable workflow the user (or agent) invokes with `/task-name`. Operators like `/close-day`, `/memory-audit`, `/tour`.
**Is not:** knowledge. If it's a "read and apply," that's a reference skill; if it's "do these steps," that's a task skill.

### knowledge/concepts/*.md — deep reference
**Is:** facts + rationale, topic-oriented. «Наша типографическая шкала: 43 токена. Размеры, высоты строк, веса. Обоснование каждого.»
**Is not:** tacit wisdom (that's reference skills). Not workflow methodology (that's a task skill or rule).

### projects/<name>/ — per-project scope
**Is:** everything specific to one client or project. `BACKLOG.md` (tasks), any `*.md` or `*.pdf` user has uploaded as reference.
**Is not:** shared knowledge. Don't put brand-system stuff here if it applies across projects.

### daily/YYYY-MM-DD.md — session archive
**Is:** agent-written synthesis of sessions (via `/close-day`). Chronological.
**Is not:** manually curated. Not a wiki.

## The promotion pipeline (pattern → law)

Four phases. All agent-driven.

```
  Жидкость (Liquid)  ──→  Янтарь (Amber)    ──→  Reference skill    ──→  Crystal (rule)
  daily/*.md              MEMORY.md                .claude/skills/           .claude/rules/
                          (date-tagged)            <role>-guidance/          *.md
                                                   SKILL.md                  (grep-enforceable)
```

### Phase 1 — Liquid (daily/)
Observation mentioned in a session. Agent captures in today's daily log. Candidate, nothing more.

### Phase 2 — Amber (MEMORY.md)
Pattern repeats within the session. Agent writes a date-tagged string to `MEMORY.md`. Tells user briefly: «записал». User does nothing.

### Phase 3 — Reference skill (via /close-day audit)
On `/close-day`, agent:
1. Synthesizes today into `daily/YYYY-MM-DD.md`
2. Compares today + `MEMORY.md` against existing `.claude/skills/*-guidance/SKILL.md` files
3. Surfaces repeats verbally: «заметил X три раза за неделю в разных сессиях, похоже на то, что уже в design-guidance в позиции Y — добавить?»
4. User confirms «да». Agent writes the patch into the right SKILL.md body.

This is the KEY moment. Not automatic detection, not manual editing. An agent-driven audit ritual.

### Phase 4 — Crystal (.claude/rules/)
After 6+ months of stable use without contradiction AND landmark impact, agent proposes promotion from a reference skill entry to a canonical rule on a later `/close-day`. User confirms. Agent writes the rule (with `paths:` frontmatter if it should be path-scoped). Rule is now auto-loaded by every matching session.

## Why no automation for 3× detection?

In earlier drafts we considered `experiences/` staging + `promote-patterns.py` background script to auto-detect 3× repetitions. Killed 2026-04-24 because:

1. **Cross-session detection is unreliable.** Without persistent background process, agent can't reliably match semantics across session boundaries.
2. **The automation solved a hypothetical problem.** After one day the scaffold had zero entries, and no case of «I wish I'd caught X earlier» had arisen.
3. **The ritual is better.** `/close-day` audit runs agent-with-full-context at end of day. Cross-session patterns get noticed WITH intent, not via fragile signature matching.

The kill reduced complexity + restored the «user only talks» invariant that an automated background detector would have threatened (users would start editing memory files if the script proposed them).

## The audit ritual (mechanics of /close-day)

```
User types: /close-day
    │
    ▼
Agent synthesizes today's sessions → daily/YYYY-MM-DD.md
    │
    ▼
Agent reads MEMORY.md (date-tagged cross-session patterns)
Agent reads today's daily
Agent reads existing .claude/skills/*-guidance/SKILL.md files
    │
    ▼
Agent audits: which today's patterns match or extend MEMORY.md?
              Which look like fits for existing reference-skill slots?
    │
    ▼
Agent surfaces 0-4 candidates to user verbally:
  "заметил Y три раза за неделю — добавить в design-guidance?"
  "X уже в design-guidance, но сегодня мы делали его по-другому — обновить?"
  "этот паттерн противоречит editorial-guidance — что-то изменилось?"
    │
    ▼
User responds verbally:
  "да" → agent writes the patch (new entry, modification, etc.)
  "нет" / "не сейчас" → agent acknowledges, doesn't write
  "покажи снова" → agent shows proposed patch text
    │
    ▼
Agent writes patches sequentially, confirms each completion
```

Key property: **user never opens a file during the entire ritual.** They talk, agent writes.

## Oversized reference-skill detection (/memory-audit)

Separate operator for structural refactor. When a reference skill grows beyond ~500 lines (Anthropic's guidance for SKILL.md size) AND contains 2-4 semantically independent topics, it should split.

```
User types: /memory-audit
    │
    ▼
Script check_oversized_reference_skills() in scripts/lint.py:
  scans .claude/skills/*-guidance/SKILL.md, flags files > 500 lines  [FREE check]
    │
    ▼
For each flagged file, agent (in session) reads contents and
groups sections by topic.  [LLM call, happens in live conversation]
    │
    ▼
If 2-4 independent topical clusters → agent proposes split:
  "design-guidance выросла до 847 строк. Внутри три темы:
   типографика / цвет / анимация. Они редко ссылаются друг на
   друга. Разделить?"
    │
    ▼
User: "да" → agent creates .claude/skills/design-guidance-type/,
             .claude/skills/design-guidance-color/, etc., moves
             sections, turns original design-guidance into index
             (with `user-invocable: false` and a description that
             lists child skills)
User: "нет" → defers. Agent remembers on next /memory-audit.
```

## Multi-project architecture

One agent, many projects. Shared layers (rules, concepts, reference skills, hot path) apply across all projects. Per-project layers (BACKLOG.md, client materials) are scoped.

```
Shared (loaded always):
  CLAUDE.md, MEMORY.md, knowledge/, .claude/skills/*-guidance/,
  .claude/rules/, .claude/skills/<task>/

Project-scoped (loaded when user names the project):
  projects/<active>/BACKLOG.md
  projects/<active>/*.md    (client brief, brand guide, notes)
  projects/<active>/*.pdf   (user-uploaded references)
```

Switch command (in conversation): «работаем над client-a» → agent unloads client-b materials, loads client-a. For project-scoped rules, use `paths: [projects/client-a/**]` frontmatter on the rule file.

## Hooks (automatic, no user action)

- **session-start.py** — on every new Claude session, injects NSP + recent daily logs + knowledge index into agent context
- **pre-compact.sh** — when context is about to compact, blocks until agent has saved state to MEMORY.md + NSP
- **periodic-save.sh** — every ~50 exchanges, prompts agent to save new patterns

Hooks are invisible to the user. They just make sure state survives.

## Naming discipline

File names are in English for canonical compatibility (`.claude/skills/design-guidance/SKILL.md`, `.claude/skills/editorial-guidance/SKILL.md`). Agent references them in Russian conversation naturally: «design-guidance», «editorial-guidance» или «руководство по дизайну». No need to teach the user English filenames.

Per-project folders can use any naming: `projects/client-nestle/`, `projects/nachalo/`, `projects/mvp-launch/` — whatever the user prefers.

## What's NOT in the architecture (by design)

- **`experiences/`** — over-engineered staging layer, deleted v4
- **`promote-patterns.py`** — background detection script, replaced by /close-day ritual
- **`playbooks/`** — draft-era separate directory for role wisdom; in v4 this lives in `.claude/skills/<role>-guidance/SKILL.md` with `user-invocable: false` (Anthropic-native)
- **Custom trigger keyword tables in CLAUDE.md** — Claude auto-invokes skills from their `description`; no hand-maintained routing
- **`wisdom/`**, **`lessons/`** — synonyms of existing layers, kept out
- **Automatic rule generation** — rules are user-approved only, never auto-written

## Related

- `README.md` — human-facing value prop
- `CLAUDE.md` — agent-facing session workflow
- `CHANGELOG.md` — what changed from v3.2.2 → v4.0.0 (includes the playbook→reference-skill reclassification)
- Anthropic docs: `code.claude.com/docs/en/skills`, `code.claude.com/docs/en/memory`, `code.claude.com/docs/en/best-practices`
