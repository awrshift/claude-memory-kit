# Gemini Models Reference

Last updated: 2026-03-12 (official docs verified via Context7 + ai.google.dev)

## Available Models

| Model | Tier | Cost (in/out $/1M) | Speed | Best For |
|-------|------|-------------------|-------|----------|
| `gemini-3.1-pro-preview` | Flagship | $2.00 / $12.00 | Medium | #1 reasoning, complex analysis, brainstorm R1-R3 |
| `gemini-3-flash-preview` | Mid-tier | $0.50 / $3.00 | Fast | Pro-quality coding, general tasks (default) |
| `gemini-3.1-flash-lite-preview` | Cost-efficient | $0.25 / $1.50 | **Fastest** (381 tok/s) | Research, fact-check, high-volume, grounded search |

### Deprecated / Removed

| Model | Status | Replacement |
|-------|--------|-------------|
| `gemini-3-pro-preview` | **SHUT DOWN** March 9, 2026 | `gemini-3.1-pro-preview` |
| `gemini-2.5-pro` | Deprecated | `gemini-3-flash-preview` |
| `gemini-2.5-flash` | Deprecated | `gemini-3-flash-preview` |
| `gemini-2.5-flash-lite` | Deprecated | `gemini-3.1-flash-lite-preview` |
| `gemini-2.5-flash-image` | Deprecated | `gemini-3.1-flash-image-preview` |
| `gemini-2.0-flash` | Retiring June 1, 2026 | `gemini-3-flash-preview` |
| `gemini-2.0-flash-lite` | Retiring June 1, 2026 | `gemini-3.1-flash-lite-preview` |

## Benchmarks (March 2026)

| Benchmark | 3.1 Pro | 3 Flash | 3.1 Flash-Lite |
|-----------|---------|---------|----------------|
| AI Intelligence Index | **57** (#1 tied) | — | 34 |
| GPQA Diamond | **94.3%** | — | 86.9% |
| ARC-AGI-2 | **77.1%** | — | — |
| SWE-bench Verified | — | **78%** | — |
| MMMU Pro | — | — | 76.8% |
| LiveCodeBench | — | — | 72.0% |
| Arena Elo | — | — | 1432 |

## Thinking Level Compatibility

All 3.x models use `thinking_level` (string). Legacy `thinking_budget` (int) is for 2.5 only — do not mix.

| Model | MINIMAL | LOW | MEDIUM | HIGH |
|-------|---------|-----|--------|------|
| `gemini-3-flash-preview` | YES | YES | YES | YES (default) |
| `gemini-3.1-flash-lite-preview` | YES | YES | YES | YES (dynamic) |
| `gemini-3.1-pro-preview` | NO | YES | YES (new in 3.1) | YES (default, dynamic) |

- **MINIMAL** (Flash only): near-zero thinking tokens. Best for simple classification, extraction.
- **LOW**: fewer tokens. Simple tasks where reasoning is not critical.
- **MEDIUM** (Flash + 3.1 Pro): balanced depth vs speed for moderate complexity.
- **HIGH** (default): maximum reasoning depth. May increase latency significantly.

Pro does not support MINIMAL (thinking can't be turned off). Auto-fallback to HIGH if unsupported level.

### Temperature (CRITICAL)

Google **strongly recommends** keeping temperature at **1.0** (default) for all Gemini 3 models.
Lower temperature may cause looping, degraded performance, especially for reasoning/math tasks.
Range: 0.0-2.0. Only adjust if you have a specific, tested reason.

### Thought Signatures

Gemini 3 returns encrypted thought signatures. SDK handles them automatically.
If using raw API: must pass signatures back in multi-turn conversations (400 error otherwise).

## Task-to-Model Matrix (Official Google Recommendations + Our Experience)

### Text Models

| Task Type | Model | Thinking | Why |
|-----------|-------|----------|-----|
| **Complex reasoning / planning** | 3.1 Pro | HIGH | #1 reasoning benchmarks, ARC-AGI-2 77.1% |
| **Vibe coding (idea to app)** | 3.1 Pro or 3 Flash | HIGH | Multi-step planning + coding |
| **Code review / generation** | 3 Flash | MEDIUM | SWE-bench 78%, fast, cost-effective |
| **Interactive apps / chatbots** | 3 Flash | MEDIUM | Good balance of quality and latency |
| **Quick factual questions** | 3 Flash | LOW | Fast response, minimal reasoning needed |
| **Research with web grounding** | 3.1 Flash-Lite + grounded | LOW | Cheapest, fastest, only needs facts |
| **Data extraction / structured** | 3.1 Flash-Lite | MINIMAL | High throughput, structured output |
| **Translation at scale** | 3.1 Flash-Lite | MINIMAL | Cost-efficient, 381 tok/s |
| **Content moderation** | 3.1 Flash-Lite | MINIMAL | Volume + speed priority |
| **Frontier science / math** | 3.1 Pro (Deep Think) | HIGH | Maximum reasoning depth |

### Our Skills Mapping

| Skill / Task | Model | Thinking | Rationale |
|-------------|-------|----------|-----------|
| **Brainstorm research** (Phase 0.5, 3.5) | 3.1 Flash-Lite + grounded | LOW | Facts only, cheapest |
| **Brainstorm reasoning** (R1-R3) | 3.1 Pro | HIGH | Deepest reasoning for strategic decisions |
| **Quick questions** (`ask`) | 3 Flash | MEDIUM | Balance of speed and quality |
| **Second opinion** | 3.1 Pro | HIGH | Critical analysis, different perspective |
| **Deep think** (`think`) | 3.1 Pro | HIGH | Maximum reasoning for complex problems |
| **Code review** (`review`) | 3 Flash | MEDIUM | SWE-bench 78%, fast |
| **Data extraction** (`extract`) | 3.1 Flash-Lite | MINIMAL | Structured output, high throughput |
| **ICF gates** | 3.1 Pro | HIGH | Critical decisions need top quality |
| **Fact-check** | 3.1 Flash-Lite + grounded | LOW | Web-verified facts, cheap |
| **Content pipeline** (S1-S7) | 3 Flash (balanced tier) | MEDIUM | Pipeline default, good quality/cost |

### Image Models

| Task Type | Model | Resolution | Why |
|-----------|-------|-----------|-----|
| **Architecture diagrams** | Flash Image (default) | 2K | Fast iteration, good text rendering |
| **Professional brand assets** | Pro Image | 4K | Best quality, complex scenes |
| **Mascots / characters** | Pro Image | 2K-4K | Advanced reasoning for complex instructions |
| **Quick mockups / iterations** | Flash Image | 1K | Fastest, cheapest |
| **Social media assets** | Flash Image | 2K | Supports extended aspect ratios (1:4, 8:1) |
| **Infographics / data viz** | Flash Image + grounded | 2K | Google Search grounding for real-time data |

## Image Generation (Nano Banana)

| Model ID | Codename | Speed | Resolutions | Aspect Ratios |
|----------|----------|-------|-------------|---------------|
| `gemini-3.1-flash-image-preview` | **Nano Banana 2** (default) | Fast | 512, 1K, 2K, 4K | 14 (standard + 1:4, 4:1, 1:8, 8:1) |
| `gemini-3-pro-image-preview` | Nano Banana Pro | Slow (~36s) | 1K, 2K, 4K | 10 (standard only) |

### Flash Image extras (not in Pro)
- Google Image Search grounding
- Thinking level control (MINIMAL/HIGH)
- Extended aspect ratios: 1:4, 4:1, 1:8, 8:1
- Resolution 512 (0.5K)
- Up to 10 reference objects, 4 characters

### Pro Image extras (not in Flash)
- Best quality for complex instructions
- High-fidelity text rendering
- Up to 6 reference objects, 5 characters

## Google Search Grounding

All Gemini 3.x text models + Flash Image support `--grounded` / Google Search tool.
Best used with Flash-Lite for factual research (cheap + fast + grounded = ideal for verification).
Flash Image can use Image Search grounding for real-time visual data.
