# Example: Recipe Sharing App — Backlog

<!-- EXAMPLE: This is a demo project. Delete this file and folder when you create your first real project. -->

**Last updated:** 2026-03-15
**Source of truth:** This file for all tasks, decisions, and status of this project

---

## Statuses

- `TODO` — in queue, not started
- `IN PROGRESS` — active work
- `DONE` — completed
- `BLOCKED` — waiting for external input

---

## Active Tasks

### T-003: Add recipe search by ingredient
**Status:** IN PROGRESS
**Priority:** P0

Users want to find recipes by what they have in the fridge. Add full-text search across ingredient lists.

**Acceptance criteria:**
- [ ] Search endpoint returns recipes matching any of the provided ingredients
- [ ] Results ranked by number of matching ingredients (most matches first)
- [ ] Response time < 200ms for up to 5 ingredients

**Decision made:** Using PostgreSQL full-text search instead of Elasticsearch — simpler infra, sufficient for our scale (< 50k recipes).

---

### T-004: Mobile-responsive recipe cards
**Status:** TODO
**Priority:** P1

Recipe cards break on screens < 400px. Images overflow, text wraps incorrectly.

**Acceptance criteria:**
- [ ] Cards display correctly on 320px-768px screens
- [ ] Images scale proportionally
- [ ] No horizontal scroll on any mobile viewport

---

## Completed

> Completed tasks move here with date.

- **T-001** (2026-03-01): [Project setup] — Next.js 15 + Tailwind v4 + PostgreSQL. Deployed to Vercel.
- **T-002** (2026-03-10): [User auth] — Added email/password auth via NextAuth. Decision: no social login for MVP — adds complexity without validated demand.

---

**Maintained by:** Claude Code agent
