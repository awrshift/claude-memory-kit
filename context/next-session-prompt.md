# Next Session Prompt

> Agent writes this at the end of each working day via `/close-day`. You read it on session start — it tells you where we left off and what to pick up next.
>
> This is the template. First `/close-day` will overwrite it.

**Last session:** YYYY-MM-DD.

## ⚡ PICK UP HERE — immediate action

<!-- Agent writes the 1-3 highest-leverage items here, ordered. Usually:
     1. A concrete task in progress
     2. An unanswered question for the user
     3. Optional cleanup / follow-up -->

1. (empty — first `/close-day` populates this)

## Open decisions (waiting on you)

<!-- Questions the agent needs your answer on before proceeding. Short, concrete. -->

- (none)

## Recent deliverables

<!-- Brief list of what actually shipped in the last 1-3 sessions. Agent prunes older items to daily/YYYY-MM-DD.md. -->

- (none)

## Active project(s)

<!-- Which `projects/<name>/` folder(s) are active right now. Agent switches on verbal command. -->

- _example_client — template; replace with your first real project

## Pointers to load

<!-- Files agent should read first on session start. Hooks auto-load most of these, but explicit reminders help. -->

- `CLAUDE.md` — agent identity (auto-loaded)
- `.claude/memory/MEMORY.md` — hot cache (auto-loaded)
- `projects/<active>/BACKLOG.md` — active project task queue
- `knowledge/concepts/*.md` — deep reference articles (loaded on description match)

---

## Usage

- Read this file FIRST on every session start
- Pick up from the topmost immediate-action item
- If items are stale (>1 week old without being worked on), ask the user whether to drop them
- Never edit this file by hand — tell the agent what's changed and let it revise
