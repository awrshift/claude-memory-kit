# Experiments (Sandbox)

<!-- EXAMPLE: This folder contains demo experiments. Replace with your own when ready. -->

Isolated sandbox for research, prototyping, and validation — outside the main project flow.

## Structure

Every experiment = a folder with EXPERIMENT.md inside:

```
experiments/
├── README.md                        ← This file (index + rules)
└── NNN-short-description/           ← Each experiment = own folder
    ├── EXPERIMENT.md                ← Required: context, status, findings
    └── (phases/, prototypes/, data/, code/ — as needed)
```

## When to Create an Experiment

**Create experiment:**
- Choosing between multiple approaches (framework, architecture, vendor)
- Unknowns that need research before committing
- Want to validate an idea before investing implementation time
- System-level improvement (not tied to one project)

**Just add a task to BACKLOG.md:**
- Path is clear, just build it
- Bug fix or routine maintenance
- No real alternatives to evaluate

## Lifecycle

```
IDENTIFY    — What's the problem? What's the gap?
RESEARCH    — Gather data, explore options
HYPOTHESIZE — Form concrete options with trade-offs
PLAN        — Pick an approach, define steps
IMPLEMENT   — Build it
EVALUATE    — Did it work? Measure against criteria
DECIDE      — GO (continue) / NO-GO (pivot) / ITERATE (refine)
```

Not every experiment needs all phases. A quick PoC can go IDENTIFY → IMPLEMENT → DECIDE.

## Active Experiments

| # | Focus | Status | Project |
|---|-------|--------|---------|
| 001 | Landing page redesign | EVALUATE | example-webapp |
| 002 | Payment provider selection | RESEARCH | example-saas |

## Rules

1. **Always a folder** — `NNN-description/` with EXPERIMENT.md inside. Never a single file.
2. **Sandbox isolation** — code/data stays in the experiment folder, not in project dirs.
3. **One experiment = one focused question.** Don't mix unrelated investigations.
4. **Port results, not files** — after DECIDE(GO), create tasks in BACKLOG and patterns in MEMORY.md.
5. **Keep this index updated** — add/remove from Active Experiments table.

## Naming

`NNN-short-description/` — sequential number + kebab-case.
