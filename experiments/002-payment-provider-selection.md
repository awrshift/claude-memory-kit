# Experiment 002: Payment Provider Selection

<!-- EXAMPLE: This is a demo experiment. Delete when you create your first real experiment. -->

**Project:** example-saas (Invoice Automation API)
**Status:** RESEARCH
**Created:** 2026-03-10
**Last updated:** 2026-03-18

---

## IDENTIFY

**Problem:** Need to add paid tiers to the API. Currently free-only. Revenue target: $2k MRR by month 3.

**Current state:** No payment integration. All users on free tier (100 invoices/month).

**Target:** Three tiers — Free (100/mo), Pro $29/mo (1,000/mo), Business $99/mo (10,000/mo).

**Gap:** Need: billing UI, subscription management, usage metering, dunning (failed payment recovery).

**Unknowns:**
- Which provider handles usage-based billing natively?
- What's the integration effort for each?
- How do they handle SCA/3DS for European customers?

---

## RESEARCH

### Stripe

- Usage-based billing: native via metered billing API
- Integration: excellent Python SDK, 2-3 days for basic flow
- SCA/3DS: fully supported, automatic
- Pricing: 2.9% + 30c per transaction
- Dunning: Smart Retries (built-in)
- Docs quality: best in class

### Paddle

- Usage-based billing: supported but less flexible than Stripe
- Integration: simpler (they handle tax + compliance as merchant of record)
- SCA/3DS: handled automatically (they're the merchant)
- Pricing: 5% + 50c — higher, but includes tax handling
- Dunning: built-in
- Docs quality: good, fewer examples than Stripe

### Lemon Squeezy

- Usage-based billing: limited — mainly seat-based or flat tiers
- Integration: simple API, but Python SDK is community-maintained
- SCA/3DS: handled (merchant of record)
- Pricing: 5% + 50c
- Dunning: basic
- Docs quality: adequate

---

## HYPOTHESIZE

*Pending — will form options after completing research on tax implications for B2B SaaS in EU.*

**Preliminary leaning:** Stripe for control + lower fees, Paddle if tax compliance becomes a blocker.

---

## Next Steps

- [ ] Research EU VAT requirements for B2B SaaS
- [ ] Talk to 2 beta testers about acceptable price points
- [ ] Form concrete options in HYPOTHESIZE phase
