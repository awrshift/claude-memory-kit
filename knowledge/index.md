# Knowledge — Topical reference index

`knowledge/` is the **facts + rationale** layer. Topic-oriented articles that explain *what* and *why*, not *how a role should think* (that's the `<role>-guidance` reference skills under `.claude/skills/`).

**Agent writes these too.** Articles are compiled from `daily/*.md` via `/memory-compile` when enough observations have accumulated around a single topic.

---

## Structure

```
knowledge/
├── index.md                    This catalog (auto-updated by /memory-compile)
├── concepts/                   Topic articles — canonical reference
│   └── <topic>.md              e.g. typography-scale.md, crawler-compatibility.md
├── connections/                Cross-references between concepts
└── meetings/                   Meeting synthesis (if applicable)
```

---

## When to write to `knowledge/concepts/`

- A topic has been touched 5+ times across `daily/*.md` with accumulating detail
- The facts are stable (not changing session-to-session)
- The article would be read by a future self who forgot the rationale

**Not** for:
- Tacit role wisdom → `.claude/skills/<role>-guidance/SKILL.md` (reference skills)
- Short cross-session patterns → `.claude/memory/MEMORY.md`
- Mechanical constraints → `.claude/rules/*.md`

---

## Article frontmatter

Every article in `concepts/` starts with:

```yaml
---
title: <topic>
status: canonical | draft | archived
compiled-from: [daily/2026-04-20.md, daily/2026-04-22.md, ...]
updated: YYYY-MM-DD
tags: [tag1, tag2]
---
```

---

## Index

<!-- Agent maintains this list via /memory-compile. One line per concept. -->

(empty — `/memory-compile` will populate when enough daily observations accumulate)

---

## Differences from adjacent layers

| Layer | Answers | Scope | Example entry |
|---|---|---|---|
| `knowledge/concepts/` | «what is X, why is it the way it is» | Facts + rationale | «our typography scale: 43 paired sub-tokens, reasoning per level» |
| `.claude/skills/<role>-guidance/SKILL.md` | «how should a <role> think about X» | Tacit judgment (reference skill, user-invocable: false) | «warm tones read editorial, cool tones read SaaS — default to warm» |
| `.claude/memory/MEMORY.md` | «short patterns noticed recently» | Date-tagged one-liners | «[2026-04-24] user prefers plain prose in status updates» |
| `.claude/rules/*.md` | «what must always / never happen» | Mechanical constraints | «never push upstream without preflight exit 0» |

Same fact can surface at different layers in its lifecycle: observation → pattern in MEMORY → judgment in reference skill → canonical article in knowledge → enforceable rule. Promotion is agent-driven, always on `/close-day`, always with user verbal confirmation.
