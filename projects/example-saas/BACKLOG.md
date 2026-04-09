# Example: Invoice Automation API — Backlog

<!-- EXAMPLE: This is a demo project. Delete this file and folder when you create your first real project. -->

**Last updated:** 2026-03-18
**Source of truth:** This file for all tasks, decisions, and status of this project

---

## Statuses

- `TODO` — in queue, not started
- `IN PROGRESS` — active work
- `DONE` — completed
- `BLOCKED` — waiting for external input

---

## Active Tasks

### T-005: PDF parsing for multi-page invoices
**Status:** BLOCKED
**Priority:** P0
**Blocked by:** Waiting for sample invoices from beta tester (ETA: March 20)

Current parser handles single-page PDFs. Multi-page invoices split line items across pages, and the parser misses items on page 2+.

**Acceptance criteria:**
- [ ] Parse invoices up to 10 pages
- [ ] All line items extracted regardless of page breaks
- [ ] Unit tests with 5+ multi-page invoice samples

---

### T-006: Rate limiting for API endpoints
**Status:** TODO
**Priority:** P1

No rate limiting currently. One bad client could take down the service.

**Acceptance criteria:**
- [ ] 100 req/min per API key (configurable)
- [ ] 429 response with Retry-After header when exceeded
- [ ] Rate limit status in response headers (X-RateLimit-Remaining)

---

## Completed

- **T-001** (2026-02-15): [Project setup] — FastAPI + SQLAlchemy + PostgreSQL. Docker Compose for local dev.
- **T-002** (2026-02-20): [PDF parsing v1] — Single-page invoice extraction. Using pdfplumber. Decision: pdfplumber over PyMuPDF — better table detection for structured invoices.
- **T-003** (2026-03-01): [API key auth] — Bearer token auth with hashed keys in DB. No OAuth for now — B2B API, keys are sufficient.
- **T-004** (2026-03-12): [Webhook notifications] — POST to client URL on invoice processed. Retry 3x with exponential backoff.

---

**Maintained by:** Claude Code agent
