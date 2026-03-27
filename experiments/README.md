# Experiments

<!-- EXAMPLE: This folder contains demo experiments. Replace with your own when ready. -->

Each major initiative or research question gets its own experiment file. Experiments follow a structured decision cycle — from identifying the problem to a final GO/NO-GO decision.

## How It Works

An experiment is a focused investigation with a clear deliverable. Unlike tasks in JOURNAL.md (which track implementation work), experiments track **decisions that need research before implementation**.

**When to create an experiment:**
- You're choosing between multiple approaches (framework, architecture, vendor)
- A decision has unknowns that need research before committing
- You want to validate an idea before investing implementation time

**When NOT to create an experiment (just add a task to JOURNAL.md):**
- The path is clear, you just need to build it
- It's a bug fix or routine maintenance
- No real alternatives to evaluate

## Experiment Lifecycle

```
IDENTIFY    — What's the problem? What's the gap?
RESEARCH    — Gather data, explore options
HYPOTHESIZE — Form concrete options with trade-offs
PLAN        — Pick an approach, define steps
IMPLEMENT   — Build it
EVALUATE    — Did it work? Measure against criteria
DECIDE      — GO (continue) / NO-GO (pivot) / ITERATE (refine)
```

Not every experiment needs all phases. Quick experiments can skip RESEARCH and go straight to PLAN.

## Active Experiments

| # | Focus | Status | Project |
|---|-------|--------|---------|
| 001 | Landing page redesign | EVALUATE | example-webapp |
| 002 | Payment provider selection | RESEARCH | example-saas |

## Naming Convention

`NNN-short-description.md` — sequential number + kebab-case description.

## Rules

1. One experiment = one focused question. Don't mix unrelated decisions.
2. Each experiment starts with IDENTIFY (why this matters).
3. Experiment ends with DECIDE — a clear GO/NO-GO with reasoning.
4. After DECIDE(GO), create implementation tasks in the relevant project's JOURNAL.md.
5. Keep experiment files as living documents — update status as you progress.
