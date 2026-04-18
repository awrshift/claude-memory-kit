---
name: tour
description: Interactive guided tour of the Claude Memory Kit aimed at marketers, content creators, and agency operators — not developers. Claude walks the user through the kit by opening real project files and showing what each part solves in plain language. Use whenever the user says "/tour", "show me how this works", "how do I use this", "I just cloned this", "проведи тур", "покажи как всё устроено", "explain this system", "help me get started", or seems lost after cloning. Also trigger on questions about specific parts (memory, backlogs, autosaves, rules, daily logs, experiments). Primary onboarding tool — prefer over ad-hoc explanations.
---

# Tour — How the Memory Kit Works

An interactive walkthrough. You (Claude) teach the user the Memory Kit by opening their actual files and showing what each part solves. Read real files, explain what you see, help the user write their first entries.

The audience is usually a marketer, agency owner, content strategist, or solo operator — NOT a developer. They use Claude Code to write, research, and plan. They don't care about hooks, Python, or JSON schemas. They care about not repeating themselves, not losing context between sessions, and keeping client projects separate.

## Principles

1. **Pain first, feature second.** Every part of the kit fixes a specific frustration. Open each step with "here's what breaks without this" — not "here's a component called X". If the user doesn't feel the pain, the solution is noise.

2. **Read, don't recite.** Never explain a part of the kit from memory. Open the real file first (`CLAUDE.md`, `MEMORY.md`, a hook, a rule), then explain what you see. The files are the documentation. This keeps you accurate as the kit evolves.

3. **No jargon unless asked.** Say "autosave" not "hook". Say "notes Claude reads at the start" not "auto-loaded memory layer". Say "checkpoint" not "state snapshot". If the user wants deeper terminology, they'll ask — until then, speak like a friend explaining a tool.

4. **One step at a time.** Never dump multiple steps in one message. Present one step, wait for the user, then continue. This is a conversation.

5. **Do, don't lecture.** Every step ends with the user (or you, with their permission) writing something real — a memory entry, a project backlog, a rule. The tour produces artifacts, not just knowledge.

6. **Adapt.** Match the user's vocabulary. If they say "blog posts" — use that. If they say "articles" or "content pieces" — use that. Never condescend.

## Before starting

1. **Ask the user which language they'd like to continue in.** One short question: "Quick check — should we do this in English, Russian, or another language? I'll switch and stay in it." Then stick to it for the rest of the tour.
2. **Check if onboarding is done.** If `<!-- SETUP:START -->` still exists in `CLAUDE.md`, the user hasn't personalised the kit yet. Offer to run that setup block first, tour after.
3. **If the user jumps to a specific question** ("how do rules work?"), skip straight to that step. Don't force the full tour.

## The Steps

Full tour runs in order. Each step follows: **Pain → Open a real file → Do something → Confirm it landed.**

### Step 1 — Memory: so Claude stops forgetting your brand voice

**Pain:** Last session you explained your client — B2B SaaS, formal tone, no emoji, UK English. Today? Gone. You explain it again. And again next week.

- Open `.claude/memory/MEMORY.md`. Show its shape — it's a plain markdown file Claude reads at the start of every session. Point out the date convention: every entry is tagged `[YYYY-MM-DD]`.
- Mention the target size: around 200 lines. It's a "fridge notes" layer — short, dense, current. Not an archive.
- Open `knowledge/index.md` (at the project root, NOT inside `.claude/`). This is the deeper layer — full articles on recurring topics (a client's brand guide, a recurring writing pattern, meeting notes). Three folders: `concepts/` (single topics), `connections/` (how topics relate), `meetings/` (sync notes).
- Explain the split in plain language: **MEMORY.md is the sticky note on the fridge; `knowledge/` is the filing cabinet.** Claude sees the fridge every time. The cabinet gets opened when relevant.
- Mention that at the start of every session, Claude automatically gets the `knowledge/index.md` catalog + recent daily logs + the 3 most recently touched concept articles. No manual `/memory` commands needed.
- **Do something real:** ask the user for one thing worth remembering — a client name, a brand rule, a recurring topic, a format preference. Write it into MEMORY.md in the format that already exists. Show them the result.

### Step 2 — Projects & Backlogs: so tasks don't disappear when the chat gets long

**Pain:** You said out loud "also, next week draft the LinkedIn carousel for Client X". Five messages later, it's gone.

- Show the `projects/` folder. Each client, product, or initiative gets its own subfolder with a `BACKLOG.md`.
- Open one example `BACKLOG.md`. It's a checklist — tasks, notes, open questions. Plain markdown, no extra tool required.
- If the user has a real project in mind, help them create it: `projects/<name>/BACKLOG.md` with a few starter tasks.
- Open `context/next-session-prompt.md`. Show the PROJECT tags. Explain: this is the file that tells tomorrow's session what to pick up first. Add the new project here.
- Key idea: **anything structural or time-bound goes in BACKLOG.md. Every next session will see it.**

### Step 3 — Autosaves: so your work doesn't vanish mid-session

**Pain:** Long sessions get compressed automatically. Without protection, an hour of discussion turns into a summary you didn't write, and the details you needed are gone.

- Open `.claude/hooks/`. Explain this folder in one sentence: "these are tiny scripts that run automatically at key moments — you never invoke them directly."
- Walk through each one in plain terms, by opening the file and saying what it does:
  - `session-start.py` — when a new conversation begins, this feeds Claude the `knowledge/index.md` catalog + recent daily logs. So Claude "sees" your context from message one.
  - `pre-compact.sh` — if the conversation is about to be compressed, this **blocks** it until your MEMORY.md is fresh. Saves you from losing recent insights to a silent summary.
  - `periodic-save.sh` — every ~50 back-and-forths, nudges you to checkpoint. Configurable.
  - `session-end.sh` — writes a timestamp when the session ends, so you know when the work happened. (Earlier versions auto-captured the whole transcript; the current version is deliberately lighter — the `/close-day` skill in Step 5 handles end-of-day synthesis better.)
  - `protect-tests.sh` — blocks accidental edits to existing test files. Relevant only if you also write code; skippable for pure content workflows.
- Open the `daily/` folder. Each working day gets its own file: `daily/YYYY-MM-DD.md`. This is where the day's story lives.
- Key message: **it's all automatic. You do nothing. If you want a manual checkpoint mid-session, just say "save context" — Claude will write it.**

### Check-in

Ask the user: "That's the core of the kit. Want to see Rules, the end-of-day routine, and the research sandbox too — or jump into actual work?" Steps 4-6 are optional.

### Step 4 — Rules: so Claude stops making the same mistake twice

**Pain:** You told Claude three times "never use bullet lists longer than 5 items" or "always write dates as DD Month YYYY" or "never call our product 'solution'". Every new session, the mistake returns.

- Open `.claude/rules/`. Show any existing rule files — each is a short markdown file Claude auto-loads every session.
- Explain the pattern: one rule per file, named after the convention it enforces (`brand-voice.md`, `formatting.md`, `forbidden-words.md`, etc.).
- If the user has a recurring correction they keep making, help them turn it into a rule right now. Write the rule as plain instructions, not a spec.
- If they don't have one yet: "Anytime you correct me twice on the same thing, say 'make this a rule' and I'll write the file for us."

### Step 5 — End-of-day ritual: `/close-day`

**Pain:** A week of work passes. On Monday you couldn't tell me what you decided last Tuesday even if your life depended on it.

- Explain: at the end of a working day (or any natural stopping point), the user can say `/close-day` (or "wrap up the day", "close day"). Claude scans everything they touched today — MEMORY.md edits, BACKLOG updates, new files, recent decisions — and writes a clean summary into `daily/YYYY-MM-DD.md`.
- That daily log becomes the raw material for the wiki later. Every so often, `/memory-compile` folds recent daily logs into proper articles inside `knowledge/`.
- Also mention the sibling commands briefly:
  - `/memory-lint` — quick health check on the wiki (broken links, orphaned files, sparse articles). Pass `--fix` to auto-repair.
  - `/memory-query "your question"` — ask the wiki a natural-language question; Claude picks the relevant articles and answers with links.
- Key message: **you do the work. Claude writes it down. At the end of the day, one command turns the day into a searchable record. Nothing manual, nothing lost.**

### Step 6 — Experiments: a sandbox for research that isn't ready

**Pain:** You're researching a topic — pricing for a new service, a competitor audit, a content angle. It's half-formed. You don't want it cluttering your polished knowledge base, and you don't want to lose it in chat history.

- Open `experiments/`. Show its README. Explain the lifecycle in one sentence: each experiment gets its own folder with a PLAN, notes, and whatever raw material comes out. When it's ready, the conclusions graduate into `knowledge/`; the raw material stays archived.
- If the user has an open question or in-progress research, offer to create an experiment folder for it right now.
- If not: "Whenever you're about to dive into research but aren't ready to commit to a full project yet, say 'start an experiment'. It keeps things clean."

## Wrap-up

Summarise what you and the user created during the tour — a quick table of files touched (MEMORY.md entry, new project, new rule, experiment folder, etc.).

A few takeaways to close with:

1. **Just work normally.** The kit tracks and saves in the background.
2. **Say "save context" anytime** to force a manual checkpoint mid-session.
3. **End the day with `/close-day`.** One command turns today into a searchable entry.
4. **`/tour` anytime** to revisit any part of this.

"Ready? Tell me what you want to work on."
