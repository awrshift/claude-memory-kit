# Experiment 001: Landing Page Redesign

<!-- EXAMPLE: This is a demo experiment. Delete when you create your first real experiment. -->

**Project:** example-webapp (Recipe Sharing App)
**Status:** EVALUATE
**Created:** 2026-03-05
**Last updated:** 2026-03-14

---

## IDENTIFY

**Problem:** Current landing page has 12% bounce rate and 2.1% signup conversion. Industry average for recipe apps is 4-5% conversion.

**Current state:** Static hero + feature list + CTA button. No social proof, no recipe previews.

**Target:** 4% signup conversion within 30 days of launch.

**Gap:** 2x improvement needed. Likely causes: no visual hook (people want to SEE recipes), no trust signals.

---

## RESEARCH

Analyzed 8 competitor landing pages (HelloFresh, Yummly, Allrecipes, Tasty, Cookpad, NYT Cooking, Epicurious, Budget Bytes).

Key findings:
- 7/8 show recipe images above the fold
- 5/8 include user-generated content (reviews, photos)
- 6/8 have "trending recipes" or "popular this week" section
- Only 2/8 use video — diminishing returns vs. static images

---

## HYPOTHESIZE

**Option A: Visual-first redesign**
- Hero with rotating recipe carousel (6 trending recipes)
- Social proof bar ("12,000 cooks sharing recipes")
- Pros: High visual impact, leverages existing content
- Cons: Slower load time, needs image optimization pipeline

**Option B: Interactive demo**
- "Search your ingredients" widget in the hero
- Show live results without signup
- Pros: Demonstrates core value immediately
- Cons: Higher dev effort, needs API rate limiting for anonymous users

---

## PLAN

Chose **Option A** — lower risk, faster to ship, directly addresses the "no visual hook" hypothesis.

Steps:
1. Design recipe carousel component (3 days)
2. Build image optimization pipeline — WebP, lazy loading (1 day)
3. Add social proof counter from DB (0.5 day)
4. A/B test old vs new landing for 2 weeks

---

## IMPLEMENT

- Built carousel with Swiper.js — `components/HeroCarousel.tsx`
- Image pipeline: Sharp for WebP conversion, blur placeholder via plaiceholder
- Social proof: live count from `users` table, cached 1 hour
- A/B test via Vercel Edge Config (50/50 split)

---

## EVALUATE

A/B test results (14 days, 4,200 visitors per variant):

| Metric | Old | New (Option A) | Delta |
|--------|-----|----------------|-------|
| Bounce rate | 12.1% | 8.3% | -31% |
| Signup conversion | 2.1% | 3.8% | +81% |
| Avg. time on page | 22s | 41s | +86% |
| LCP (Largest Contentful Paint) | 1.2s | 1.8s | +50% |

Conversion improved significantly but didn't hit 4% target. LCP degraded — needs optimization.

---

## DECIDE

**GO with iteration.** Ship Option A as default, then:
1. Optimize LCP (target < 1.5s) — create task T-005 in BACKLOG
2. Consider adding Option B (ingredient search) as secondary CTA — create experiment 003
