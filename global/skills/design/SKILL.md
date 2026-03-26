---
name: design
description: Design system automation — initialize, sync, audit, explore, generate screens, and visual QA using design tokens. Use when the user asks to "create a design system", "set up brand tokens", "sync design changes", "check design consistency", "audit my screens", "generate a screen with my tokens", "explore layouts in Pencil", or "compare with reference". Handles design-tokens.json lifecycle, Token Injection Protocol for frontend-design plugin, Pencil MCP visual exploration (Smart Wireframe), drift detection, HTML token adherence auditing, and Visual QA loop (VQA) for pixel-level comparison against reference sites. Trigger when the user mentions design tokens, brand colors, theme setup, color palette, typography scale, spacing system, visual consistency, wireframe, visual prototype, layout comparison, visual QA, design diff, or reference matching — even without saying "design system". Also trigger for "set up colors for my project", "I need a dark theme", "make my screens consistent", "where are my design tokens", "audit my HTML", "check token adherence", "explore layout", "pencil wireframe", "compare layouts", "how close is it to the reference", "visual comparison", "match the design", or Tailwind theme configuration.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Design System Automation

Manages the design token lifecycle for a project. Two-file SSOT: `design-tokens.json` (precise values for code generators) + `design-rules.md` (behavioral rules for AI prompts). All other files (CSS variables, Tailwind theme, Stitch context) are generated from these two sources — editing generated files directly leads to drift that gets overwritten on next sync.

**Primary workflow:** Token Injection Protocol — load tokens, build `:root` CSS variables, inject into `frontend-design` prompt for high-fidelity screen generation with 100% token adherence.

**Use this skill when:** setting up a new design system, propagating token changes, auditing HTML for token adherence, or generating screens via Token Injection Protocol.

**Do NOT use this skill for:** generating UI screens directly (use `frontend-design` skill with injected tokens), reviewing component code (use `ux-audit`), or accessibility auditing beyond contrast ratios (use `ux-audit`).

---

## Subcommands

### /design init (v3 — Visual-to-Blueprint Pipeline)

**Triggers:** "create design system", "set up brand", "initialize design", "new project design", "I need a dark theme", "set up colors for my project", "analyze this design", "use this as reference", "screenshot to design system"

The v3 init generates a **senior-grade design system** from a visual reference (URL or screenshot). Instead of requiring a hex color and text description, it extracts colors, typography, and structural patterns from an existing design — then computes a perceptually uniform OKLCH palette and produces 90+ tokens.

**Fallback modes:**
- `/design init --seed` — v2 Seed-to-System (provide hex + text description, no reference needed)
- `/design init --legacy` — template-based init (uses `init_design_system.py`)

---

#### Phase 1: Reference Capture (~5 min)

##### Step 1.1 — Acquire Reference

**If URL provided:**
1. Chrome MCP `navigate` to URL + `resize_window(1440, 900)`
2. Chrome MCP `computer(screenshot)` → save to `/tmp/ref-screenshot.png`
3. **Parallel:** Chrome MCP `javascript_tool` → extract computed styles:
   ```javascript
   JSON.stringify({
     fonts: [
       getComputedStyle(document.querySelector('h1, h2') || document.body).fontFamily,
       getComputedStyle(document.querySelector('p, main') || document.body).fontFamily
     ],
     fontSize: getComputedStyle(document.body).fontSize,
     borderRadius: getComputedStyle(
       document.querySelector('button, .card, [class*="card"], [class*="btn"]') || document.body
     ).borderRadius
   })
   ```

**If screenshot file provided:**
- Read the file directly (Claude analyzes natively). Skip JS extraction.

##### Step 1.2 — Visual Analysis (Claude multimodal)

Read the screenshot with the Read tool. Extract and document:
- **Mood:** 3-5 keywords (e.g., "professional, clean, trustworthy")
- **Density:** compact / comfortable / spacious
- **Typography family guess:** heading + body font families
- **Border radius pattern:** none / sm / md / lg / xl
- **Elevation style:** flat / border / shadow / glass
- **Theme:** dark / light
- **Layout pattern:** sidebar / top-nav / full-width

##### Step 1.3 — Color Extraction

```bash
python3 ~/.claude/skills/design/scripts/extract_colors.py \
  --image /tmp/ref-screenshot.png --count 5
```

This extracts dominant colors using OKLCH-aware K-means with vibrant/neutral separation. Output includes hex, OKLCH values, pixel percentage, and role hints (primary_candidate, accent_candidate, background_candidate).

##### Step 1.4 — Reconciliation

Combine all three signal sources with this priority order:
1. **extract_colors.py** for hex values (objective, pixel-level)
2. **JS computed styles** for font families and border-radius (from live DOM)
3. **Claude visual analysis** for mood, density, layout, elevation (spatial/aesthetic)

Never use Claude's guessed hex values when extract_colors.py provides data. Font names from JS > Claude's guesses.

---

#### Phase 2: Blueprint (~10 min)

##### Step 2.1 — Synthesize Blueprint JSON

Combine reconciled signals into a blueprint:

```json
{
  "brand_colors": {
    "primary_hex": "#635BFF",
    "secondary_hex": "#00D4AA"
  },
  "surface_colors": {
    "background_hex": "#FFFFFF",
    "text_main_hex": "#1A1A2E"
  },
  "theme": "light",
  "density": "comfortable",
  "aesthetic": "minimal",
  "project_type": "landing_page",
  "font_ui": "Inter",
  "font_data": "JetBrains Mono",
  "border_radius": "md",
  "mood": "professional, clean, trustworthy",
  "reference_url": "https://stripe.com"
}

```

`brand_colors.primary_hex` = highest-chroma vibrant cluster (primary_candidate from extract_colors).
`brand_colors.secondary_hex` = accent_candidate (optional — omit if no accent found).
`surface_colors` = background_candidate + text_candidate from neutral clusters.

##### Step 2.2 — Present 3 Variants

- **A: Faithful** — closest to reference (extracted hex, detected fonts, same density)
- **B: Refined** — adjust density/radius for better token math (e.g., compact→comfortable)
- **C: Reinterpreted** — keep mood, shift aesthetic (e.g., same colors but brutalist→minimal)

User selects one, merges ideas, or asks for adjustments.

##### Step 2.3 — Compute Palette + Generate System

```bash
python3 ~/.claude/skills/design/scripts/compute_palette.py \
  --hex "<primary_hex>" --theme <theme> --density <density> > /tmp/palette.json
```

Write `/tmp/design-config.json` with blueprint fields (name, description, aesthetic, project_type, fonts, extra_rules).

**Font pairing by aesthetic** (fallback when no JS fonts extracted):
| Aesthetic | font_ui | font_data |
|-----------|---------|-----------|
| minimal | Inter | JetBrains Mono |
| brutalist | Space Grotesk | IBM Plex Mono |
| playful | Nunito | Fira Code |
| corporate | Geist | IBM Plex Mono |
| elegant | DM Sans | DM Mono |

```bash
python3 ~/.claude/skills/design/scripts/generate_system.py \
  --palette /tmp/palette.json \
  --config /tmp/design-config.json \
  --output <project-root> --css
```

**Check the contrast report.** If there are failures beyond "primary on elevated surfaces" (expected), investigate before proceeding.

##### Step 2.4 — Gemini Gate 1 (Palette Coherence)

Send blueprint JSON + contrast report summary to Gemini:
```bash
python3 ~/.claude/skills/gemini/gemini.py second-opinion \
  "Is this palette coherent? Aesthetic cues consistent? Blind spots?" \
  --context "<blueprint JSON + contrast report>"
```

Gate is **advisory** — failures don't block, but flag issues for user review. If Gemini 503 → retry once, then skip.

---

#### Phase 3: Screen DNA (~10 min)

##### Step 3.1 — Define Screens

User specifies screens or accept defaults by project_type:
| project_type | Default screens |
|-------------|----------------|
| dashboard | overview, detail, settings |
| landing_page | hero, features, pricing |
| ecommerce | catalog, product, cart |
| web_app | dashboard, list, form |

##### Step 3.2 — Write Screen DNA

Write `<project-root>/screen-dna.md` — 5-8 structural patterns extracted from the reference:
- **Card anatomy** — dimensions, padding, header/body/footer structure
- **Navigation pattern** — sidebar/top, width, active indicator style
- **Data display** — table/grid/list, column behavior
- **Action pattern** — button sizes, grouping, spacing
- **Spacing rhythm** — section gaps, card gaps, internal padding
- **Header/footer patterns** — sticky/fixed, height, content structure
- **Typography rhythm** — heading scale, body/label/caption sizes

These patterns are observational descriptions from the reference, not token values.

##### Step 3.3 — Write Design Rules

Write `<project-root>/design-rules.md` using the **Design Knowledge** section below. Include:
- Universal rules (D-5, D-20 through D-25) — always
- Project-specific rules from config (D-1, D-2, etc.)
- Aesthetic direction (1-sentence pitch + character keywords + anti-patterns)
- Component patterns relevant to `project_type`
- Reference-informed constraints from screen-dna.md

The rules file should be 200-400 lines covering: aesthetic identity, color usage, typography, elevation, state layers, borders, component patterns, data resilience, accessibility, layout, animation, anti-patterns.

##### Step 3.4 — Gemini Gate 2 (Pattern Sufficiency)

Send screen-dna.md + design-rules.md to Gemini:
```bash
python3 ~/.claude/skills/gemini/gemini.py second-opinion \
  "Sufficient patterns for <project_type>? Missing patterns?" \
  --context "<screen-dna.md + design-rules.md>"
```

Advisory gate — same retry/skip logic as Gate 1.

---

#### Phase 4: Summary + Handoff

Show the user:
- Token count and breakdown (core/semantic/chart)
- Contrast report summary (X/Y pairs pass)
- Files written (design-tokens.json, design-rules.md, design-tokens.css, screen-dna.md)
- Reference used (URL or file path)
- Next steps: `/design generate` to create screens, `/design explore` to prototype in Pencil

---

#### /design init --seed (v2 Seed-to-System — fallback)

When user provides a hex color directly instead of a reference, use the seed pipeline:

1. **Extract Parameters** from natural language: `primary_hex` (required), `theme`, `density`, `aesthetic`, `project_type`
2. **Compute Palette:** `compute_palette.py --hex <hex> --theme <theme> --density <density>`
3. **Write Config:** `/tmp/design-config.json` with fonts, description, extra rules
4. **Generate System:** `generate_system.py --palette ... --config ... --output <root> --css`
5. **Write Design Rules:** `design-rules.md` from Design Knowledge section
6. **Summary:** token count, contrast report, files written, next steps

This is the original v2 pipeline — no reference capture, no screen DNA, no Gemini gates.

---

### /design sync

**Triggers:** "sync design", "update design tokens", "propagate design changes", "design changed", "regenerate design files"

Mutation path: user edits `design-tokens.json` directly → runs `/design sync` → all output files regenerated from the updated source.

Steps:

1. Read `design-tokens.json` from project root (fail fast if not found — run `/design init` first)
2. Validate before regenerating:
   ```bash
   python3 ~/.claude/skills/design/scripts/validate_tokens.py design-tokens.json
   ```
   If validation fails → show errors, stop. Do not regenerate from broken tokens.
3. Regenerate all output files:
   ```bash
   python3 ~/.claude/skills/design/scripts/generate_tailwind.py design-tokens.json
   python3 ~/.claude/skills/design/scripts/generate_css_vars.py design-tokens.json
   ```
4. Scan codebase for drift (hardcoded hex values not in tokens):
   ```bash
   python3 ~/.claude/skills/design/scripts/sync_drift.py design-tokens.json
   ```
5. Show summary of regenerated files and any drift warnings.

**--dry-run flag:** If the user passes `--dry-run`, show what would change (diff of current vs regenerated output) without writing files.

---

### /design generate

**Triggers:** "generate a screen", "create a page with my tokens", "build a screen using design tokens", "design generate"

The Token Injection Protocol for generating screens via `frontend-design` plugin with guaranteed token adherence.

Steps:

1. Load `design-tokens.json` from project root. If not found → offer `/design init`.
2. Load `design-rules.md` from project root. If not found → warn (rules are optional but recommended).
2.5. Load `screen-dna.md` from project root (optional, created by `/design init` v3).
     If found: include structural patterns as "Layout Patterns" section in the
     `frontend-design` prompt. Patterns constrain card anatomy, nav style, spacing rhythm.
     When building the screen brief (step 3), pre-fill the Layout section with matching
     patterns from screen-dna.md (e.g., card anatomy → card component structure).
3. If the user hasn't provided a screen brief, offer the template:
   ```bash
   cat ~/.claude/skills/design/resources/templates/screen-brief.md
   ```
4. Build the `:root` CSS variable block from token values:
   - Resolve all aliases (`{color.core.cyan-500}` → actual hex)
   - Generate CSS custom properties: `--bg`, `--surface`, `--text-primary`, etc.
   - Include font-family declarations
   - Include `font-variant-numeric: tabular-nums` for data elements (rule D-4)
5. Construct the `frontend-design` prompt by appending:
   - The `:root` CSS block as inline `<style>` at the top of the page
   - Behavioral rules from `design-rules.md` as generation constraints
   - Screen brief details (layout, data shape, constraints)
6. Apply per-page token overrides if specified in the brief:
   - Example: Alerts page uses `secondary-action` (teal) instead of `primary` (amber) for CTAs to avoid amber-on-amber semantic collision
7. After generation, run audit:
   ```bash
   python3 ~/.claude/skills/design/scripts/audit_html.py --html <generated-file> --tokens design-tokens.json
   ```
8. If audit shows violations → fix inline and re-audit until 100%.

**Key insight (D-26):** Injecting resolved tokens as `:root` CSS variables directly into the HTML gives the LLM concrete values to use, achieving 100% adherence. The old Stitch+postprocess pipeline required fixing after generation; Token Injection Protocol prevents violations at generation time.

---

### /design audit

**Triggers:** "audit my HTML", "check token adherence", "are my screens using the right colors", "design audit"

Steps:

1. Run the audit script:
   ```bash
   python3 ~/.claude/skills/design/scripts/audit_html.py --html <file.html> --tokens design-tokens.json
   ```
2. For multiple files:
   ```bash
   for f in *.html; do
     python3 ~/.claude/skills/design/scripts/audit_html.py --html "$f" --tokens design-tokens.json
   done
   ```
3. Report results:
   - **PASS** — 100% token adherence, fonts match, tabular-nums present
   - **FAIL** — violations found with line numbers and context

The audit checks:
- All hex colors against resolved token values
- Font families against token font definitions
- Presence of `tabular-nums` on data containers (rule D-4)
- rgba() values converted to hex for comparison

---

### /design check

**Triggers:** "check design consistency", "design check", "verify design tokens", "validate tokens"

Steps:

1. Validate token structure, aliases, circular deps, contrast ratios, and types:
   ```bash
   python3 ~/.claude/skills/design/scripts/validate_tokens.py design-tokens.json --verbose
   ```
2. Scan code for hardcoded values that bypass the token system:
   ```bash
   python3 ~/.claude/skills/design/scripts/sync_drift.py design-tokens.json
   ```
3. Report results with overall status:
   - **PASS** — no errors, no drift
   - **WARNING** — contrast warnings or minor drift detected
   - **FAIL** — validation errors or critical drift

---

### /design explore

**Triggers:** "explore layout", "wireframe", "visual prototype", "compare layouts", "pencil wireframe", "design explore"

Visual exploration via Pencil MCP — create disposable wireframes to compare layout directions before committing to production HTML. Uses Smart Wireframe workflow (validated: 5/5 tests passed).

**Prerequisites:** Pencil MCP server must be configured in Claude Code settings.

Steps:

1. Load `design-tokens.json` from project root. If not found → offer `/design init`.
2. Convert tokens to Pencil variables:
   ```bash
   python3 ~/.claude/skills/design/scripts/tokens_to_pencil_vars.py design-tokens.json --json
   ```
3. Open a new .pen file and inject variables:
   - `open_document("new")` → `set_variables` with converted token dict
4. Build layout using Pencil MCP `batch_design`:
   - **Flexbox only** — `layout: "horizontal"/"vertical"` + `fill_container` + `gap`. Never manual X/Y.
   - **Variables for visual values** — `$primary`, `$spacing-grid-gap`, `$radius-lg`, etc.
   - **fontFamily exception** — use literal strings ("IBM Plex Mono"), NOT variable refs. Pencil limitation.
   - **< 25 ops per call** — split large screens by logical sections.
   - **Modals/overlays** — use `layout: "none"` on parent + absolute X/Y + flexbox inside dialog.
5. Verify with `get_screenshot` after each batch.
6. For **side-by-side comparison**: wrap variants in a horizontal parent frame with `gap: 60`:
   ```
   canvas (layout:horizontal, gap:60)
   ├── Variant A (width:720, layout:vertical)
   └── Variant B (width:720, layout:vertical)
   ```
7. Iterate: `D()` to remove, `R()` to replace, `U()` to update, `I()` to add.
8. When approved → switch to `/design generate` for production HTML.
9. Delete or archive the .pen file — **Pencil is disposable, never SSOT.**

**Key rules:**
- design-tokens.json = SSOT. Always. Never .pen files.
- Unidirectional flow: tokens → Pencil → visual → HTML. Never Pencil → tokens.
- .pen files are exploration artifacts, not production assets.

---

### /design vqa

**Triggers:** "compare designs", "visual QA", "design diff", "how close is it", "visual comparison", "match the reference", "design vqa", "compare with reference"

Automated Visual QA loop: compares generated site against a reference URL, identifies differences per component, gets CSS patches from Gemini 3.1 Pro, and iterates until visual parity.

**Prerequisites:**
- Chrome MCP must be available (for screenshots + JS extraction)
- Gemini CLI (`~/.claude/skills/gemini/gemini.py`) configured with API key
- Both reference URL and generated site must be accessible

**When to use:** After `/design generate` produces a page, run VQA to close the gap between "stylistically similar" and "visually identical".

Steps:

1. **Setup** — Ensure both sites are accessible:
   - Reference: the target URL (e.g., `https://www.diabrowser.com/`)
   - Generated: local server or file (e.g., `http://localhost:8888/index.html`)

2. **Extract static styles from BOTH sites** via Chrome MCP:
   - Navigate to reference URL → `resize_window(1440, 900)` → `computer(screenshot)`
   - Run `javascript_tool` with the extraction script:
     ```bash
     cat ~/.claude/skills/design/resources/vqa-extract-styles.js
     ```
   - Save output to `/tmp/vqa-ref-styles.json`
   - Repeat for generated site → save to `/tmp/vqa-gen-styles.json`

2b. **Extract interaction DNA from BOTH sites** via Chrome MCP hover loop:

   This step captures hover states, transitions, and animation patterns that static extraction misses.

   **Phase 1 — Prepare targets:**
   Run `javascript_tool` with the interaction scan script:
   ```bash
   cat ~/.claude/skills/design/resources/vqa-interaction-scan.js
   ```
   This returns a JSON with `targets[]` — each target has `{label, text, x, y, transition, cursor}`.

   **Phase 2 — Hover loop (for each target):**
   ```
   for i in range(targetCount):
     1. Chrome MCP: computer(action="hover", coordinate=[target.x, target.y])
     2. Chrome MCP: javascript_tool → window.__vqa_readHover(i)
        → returns {label, delta: {prop: {from, to}}, transition}
   ```
   Each `__vqa_readHover(i)` compares the current (hovered) computed styles against the
   previously stored normal-state styles and returns only the properties that changed.

   **Phase 3 — Collect full report:**
   ```
   Chrome MCP: javascript_tool → window.__vqa_getInteractionReport()
   ```
   Returns JSON with:
   - `elements[]` — per-element hover delta (what changed: color, opacity, fontWeight, transform, etc.)
   - `hoverRules[]` — CSS `:hover` rules from stylesheets
   - `keyframes[]` — `@keyframes` animation definitions

   Save to `/tmp/vqa-ref-interactions.json` and `/tmp/vqa-gen-interactions.json`.

   **Phase 4 — Scroll state scan (reference site only):**
   ```
   1. Chrome MCP: javascript_tool → snap nav styles (normal)
   2. Chrome MCP: computer(action="scroll", scroll_direction="down", scroll_amount=5)
   3. Chrome MCP: javascript_tool → snap nav styles (scrolled)
   4. Record delta: what changed on scroll (background, backdrop-filter, border, shadow)
   ```

   **What this catches:**
   - Nav links that change font-weight on hover (Dia: 400→700)
   - CTA buttons with opacity transitions (Dia: opacity 0.6 on disabled hover)
   - Scroll-triggered nav background changes (transparent → blur + bg)
   - Card hover shadows (0→elevated)
   - Animation names and keyframe definitions (e.g., `chroma-sweep`)

3. **Generate structured diff:**
   ```bash
   python3 ~/.claude/skills/design/scripts/vqa_diff.py \
     --reference /tmp/vqa-ref-styles.json \
     --generated /tmp/vqa-gen-styles.json \
     --output /tmp/vqa-report.md
   ```
   This outputs a per-component comparison with severity ratings (critical/moderate/minor) and a visual parity score (%).

4. **Get CSS patches from Gemini 3.1 Pro:**
   ```bash
   python3 ~/.claude/skills/gemini/gemini.py second-opinion \
     "Based on this VQA comparison, provide SPECIFIC CSS overrides to close the visual gap. Focus on CRITICAL differences. Output exact CSS selectors and values. Include design token update suggestions." \
     --context "$(cat /tmp/vqa-report.md)" \
     --save /tmp/vqa-css-patches.md
   ```

5. **Apply patches:**
   - Read Gemini's CSS patch recommendations
   - Map patch selectors to actual class names in the generated HTML
   - Apply edits via Edit tool
   - Update `design-tokens.json` if token-level changes needed
   - Run `/design sync` to regenerate CSS variables

6. **Verify (iterate):**
   - Re-screenshot the generated site
   - Visually compare with reference
   - If visual parity score < 85% → repeat from step 2
   - If score >= 85% → done, report final score

7. **Report:**
   - Show before/after visual parity scores
   - List applied patches
   - List remaining differences (accepted or deferred)

**Iteration limits:** Maximum 3 VQA iterations. If score doesn't improve between iterations, stop and report blockers (usually font differences or animation gaps that CSS patches can't fix).

**Key insight:** The VQA loop compensates for LLM spatial reasoning limits. Generation gives ~60-70% visual parity. Each VQA iteration adds ~10-15%. Three iterations typically reach 85-95%.

**What VQA catches that token audit doesn't:**

Static differences:
- Border radius mismatches (pill vs square buttons)
- Shadow/depth differences (flat vs elevated mockups)
- Font weight/size discrepancies per component
- Letter-spacing and text-transform mismatches
- Background gradient intensity and color differences
- Padding/height proportions of interactive elements

Interaction differences (step 2b):
- Hover state transitions (color change, opacity, font-weight shift, scale)
- Transition timing and easing curves per element
- Scroll-triggered state changes (nav background, shadow appearance)
- Animation keyframes (scroll reveals, chroma effects, parallax)
- Cursor style per interactive element

**Scripts:**
| Script | Purpose | CLI |
|--------|---------|-----|
| `resources/vqa-extract-styles.js` | Chrome MCP JS — static component-level style extraction | Paste into `javascript_tool` |
| `resources/vqa-interaction-scan.js` | Chrome MCP JS — hover/transition/animation extraction | Paste into `javascript_tool`, then hover loop |
| `scripts/vqa_diff.py` | Structured diff between two style extractions | `python3 vqa_diff.py -r ref.json -g gen.json -o report.md` |

---

## Token Injection Protocol

The core workflow for generating token-adherent screens. Proven at 100% adherence across 4 screens (Dashboard 18/18, Brands 18/18, Alerts 24/24, Reports 21/21 token values).

### How It Works

1. **Load tokens** — Read `design-tokens.json`, resolve all `{alias}` references to final hex values
2. **Build CSS vars** — Generate a `:root` block with all resolved values as CSS custom properties
3. **Compose prompt** — Add CSS block + design-rules.md content + screen brief to the `frontend-design` prompt
4. **Generate** — `frontend-design` plugin uses the injected values directly in the HTML
5. **Audit** — Run `audit_html.py` to verify 100% adherence

### Per-Page Overrides

Some screens need different accent colors to avoid semantic collision. Specify in the screen brief's "Token Overrides" section:

```
# Alerts page — uses teal for CTAs instead of amber
Primary action color: secondary-action (teal #5CC8A0)
Reason: Amber is used for warning alerts; teal CTAs avoid confusion
```

The generator applies the override only to that page's action buttons and interactive elements.

### Why Not Stitch+Postprocess

The original workflow (Stitch generation → postprocess_stitch.py correction) had two problems:
1. Stitch ignores injected design context ~40% of the time, requiring post-processing
2. Post-processing via regex is fragile — name-based mapping works for known keys but misses custom Stitch color names

Token Injection Protocol with `frontend-design` avoids both issues by giving the LLM resolved values upfront.

---

## Two-File SSOT

Tokens and rules are separated because they serve different consumers: tokens provide precise values for code generators (CSS, Tailwind), while rules provide behavioral guidelines for AI prompt generation (frontend-design, ux-audit).

| File | Role | Edit? |
|------|------|-------|
| `design-tokens.json` | Token values — colors, spacing, radius, typography | YES — this is the source |
| `design-rules.md` | Behavioral rules — component style, motion, density | YES — scaffold, fully editable |
| `tailwind-theme.css` | Tailwind v4 @theme block | NO — generated |
| `tokens.css` | CSS custom properties (--color-primary, etc.) | NO — generated |

Generated files are overwritten on every `/design sync`. Edits to them get lost — always change the source files instead.

---

## Token Format

`design-tokens.json` follows the W3C Design Token Community Group format with two layers:

```json
{
  "$meta": { "name": "My Project", "version": "1.0.0", "theme": "dark" },
  "color": {
    "$type": "color",
    "core": {
      "cyan-500": { "value": "#06b6d4", "description": "Electric Cyan" }
    },
    "semantic": {
      "primary":    { "value": "{color.core.cyan-500}", "description": "CTAs, active states" },
      "background": { "value": "#0c1222", "description": "Page background" }
    }
  },
  "typography": {
    "font-primary": { "value": "DM Sans", "description": "Primary typeface" }
  },
  "spacing": {
    "$type": "dimension",
    "base": { "value": "4px", "description": "Base unit" },
    "md":   { "value": "16px", "description": "Standard component padding" }
  },
  "radius": {
    "$type": "dimension",
    "sm":  { "value": "4px" },
    "md":  { "value": "8px" },
    "lg":  { "value": "12px" }
  }
}
```

**Core layer:** raw values. **Semantic layer:** aliases using `{dot.path}` syntax. Semantic tokens map meaning to core values (e.g., `primary` → `cyan-500`). Always prefer semantic token names in generated code.

---

## Scripts Reference

All scripts use Python stdlib only — no external dependencies. Scripts live in `~/.claude/skills/design/scripts/`.

### v2 Pipeline (Seed-to-System)

| Script | Purpose | CLI |
|--------|---------|-----|
| `extract_colors.py` | Dominant colors from screenshot (Pillow + K-means, vibrant/neutral split) | `python3 extract_colors.py --image img.png --count 5` |
| `compute_palette.py` | OKLCH color engine: hex → full palette (scales, semantic, surfaces, chart) | `python3 compute_palette.py --hex "#2563EB" --theme dark --density compact` |
| `generate_system.py` | Merge palette + scaffold + config → design-tokens.json | `python3 generate_system.py --palette p.json --config c.json --output ./ --css` |
| `build_system.py` | Validate (6 phases) + generate CSS variables | `python3 build_system.py design-tokens.json --css output.css` |

### Existing (unchanged)

| Script | Purpose | CLI |
|--------|---------|-----|
| `init_design_system.py` | Legacy template-based init | `python3 init_design_system.py --template saas-dark --name "Project" --output-dir .` |
| `validate_tokens.py` | Validate structure, aliases, WCAG contrast, types | `python3 validate_tokens.py design-tokens.json [--verbose]` |
| `sync_drift.py` | Scan code for hardcoded values not in tokens | `python3 sync_drift.py design-tokens.json [--scan-dir ./src]` |
| `audit_html.py` | Audit HTML file for token adherence | `python3 audit_html.py --html page.html --tokens design-tokens.json` |
| `generate_tailwind.py` | Generate Tailwind v4 @theme from tokens | `python3 generate_tailwind.py design-tokens.json` |
| `generate_css_vars.py` | Generate CSS custom properties from tokens | `python3 generate_css_vars.py design-tokens.json` |
| `tokens_to_pencil_vars.py` | Convert tokens to Pencil MCP variables format | `python3 tokens_to_pencil_vars.py design-tokens.json [--json] [--dry-run]` |
| `compile_stitch_context.py` | Compile .stitch-context.md for Stitch MCP | `python3 compile_stitch_context.py design-tokens.json` |
| `legacy/postprocess_stitch.py` | Post-process Stitch HTML (deprecated) | `python3 legacy/postprocess_stitch.py input.html --tokens design-tokens.json` |

---

## Stitch Integration (Legacy)

The original workflow used Google Stitch MCP for screen generation, followed by `postprocess_stitch.py` to fix token violations. This workflow is **deprecated** in favor of Token Injection Protocol with `frontend-design`.

**Why deprecated:**
- Stitch ignores design context injection ~40% of the time
- Post-processing fixes are regex-based and fragile
- Token Injection Protocol achieves 100% adherence without post-processing

**Still available:**
- `compile_stitch_context.py` — compiles `.stitch-context.md` for Stitch MCP (functional, for Stitch users)
- `legacy/postprocess_stitch.py` — post-processes Stitch HTML (moved to `scripts/legacy/`)
- `resources/prompts/stitch-context-template.md` — template for Stitch context compilation

To use the legacy workflow:
```bash
python3 ~/.claude/skills/design/scripts/compile_stitch_context.py design-tokens.json
# Generate via Stitch MCP, then:
python3 ~/.claude/skills/design/scripts/legacy/postprocess_stitch.py output.html --tokens design-tokens.json
```

---

## Design Knowledge — 27 Rules for Senior-Grade Systems

These rules encode what senior designers know. Use them when writing `design-rules.md` during `/design init`. Rules D-5, D-20–D-25 are universal (included in scaffold). Others are applied based on project_type and aesthetic.

### Layout & Structure
1. **Max-width constraint** — Content max-width 1200-1600px. Sidebar fixed (240-280px). Never full-bleed data.
2. **Grid gap consistency** — One grid-gap value per density. Never mix 16px and 24px gaps on same page.
3. **Card anatomy** — Every card: header (title + action), body (content), footer (metadata). No orphan content.

### Elevation (Dark Mode)
4. **Surface lightness = elevation** — Higher surface = lighter color. 4 levels: background < surface < surface-hover < tooltip-bg. No box-shadows in dark mode.
5. **Border replaces shadow** — Cards use 1px border (border-default), not drop shadow. Active/selected = border-strong.

### State System (M3-inspired)
6. **D-20: State overlays** — Never hardcode hover/focus backgrounds. Use state-hover (8%), state-focus (10%), state-pressed (16%) via `color-mix(in srgb, var(--surface), white N%)`.
7. **D-21: Semantic borders** — 3 tiers: border-subtle (rgba transparent), border-default (card edges), border-strong (active). Never arbitrary hex.
8. **Focus ring** — 2px solid info color, 2px offset. Instant transition (0ms). Never remove for keyboard users.

### Color
9. **D-5: Never color alone** — Status always = color + icon + text label. Colorblind users must understand state.
10. **Accent hierarchy** — Primary for CTAs only. If warning uses same hue as primary, add icon disambiguation.
11. **Chart palette** — 8 categorical colors, equally-spaced hues. Series 1 = primary (brand). Minimum 3:1 between adjacent series.

### Typography
12. **D-24: Skip-a-weight** — Never pair Regular (400) with Medium (500). Use Regular + Semibold (600) for clear hierarchy.
13. **Two font families max** — UI font (sans) + Data font (mono). No third font unless explicitly justified.
14. **tabular-nums** — All numeric data: KPIs, tables, timestamps, charts. Prevents layout shift on value changes.
15. **Line-height system** — 4 ratios: 1.0 (display/KPI), 1.2 (compact UI), 1.4 (labels), 1.5 (body text).

### Data Resilience
16. **D-22: Truncation by default** — All dynamic text containers: `text-overflow: ellipsis; overflow: hidden; white-space: nowrap`. 50+ char assumption.
17. **D-23: Skeleton +1** — Skeleton loader = one surface level higher than container. At max elevation → outline pulse.
18. **Empty states** — Every data container must have an empty state (icon + message + CTA). Never blank space.
19. **Loading sequence** — Skeleton first, then data populate. Never spinner for layout regions.

### Accessibility
20. **D-25: Reduced motion** — `@media (prefers-reduced-motion: reduce)`: disable transitions, skeleton shimmer becomes static.
21. **Touch targets** — Minimum 44×44px clickable area. Minimum 8px spacing between targets.
22. **Contrast floors** — Body text: 4.5:1 (AA). Muted/disabled: 3:1. Large text (18px+): 3:1. Icons: 3:1.

### Component Patterns (by project_type)

**Dashboard:**
23. **KPI cards** — Large mono number + small label above + trend indicator (icon + %). Never more than 4-6 KPIs visible.
24. **Table defaults** — Sticky header, alternating row color via border-subtle, sortable columns, right-align numbers.
25. **Sidebar nav** — Fixed width, active indicator (3px left-border primary color, no bg fill).

**Landing Page:**
26. **Hero section** — Social proof numbers in mono font. One CTA above fold. Screenshot/demo as validation.
27. **Progressive disclosure** — Features → Pricing → Social proof → CTA. Never reverse.

---

## Starter Templates

| Template | Theme | Aesthetic |
|----------|-------|-----------|
| `saas-dark` | Dark | Professional, data-driven SaaS dashboard |
| `marketing-light` | Light | Clean, airy marketing/landing pages |
| `editorial-mono` | Dark | High-contrast monochrome editorial |

Templates live in `~/.claude/skills/design/resources/starter-templates/`.

---

## Bundled Resources

Read these files only when needed — they don't need to be loaded into context upfront.

| Resource | When to read | Purpose |
|----------|-------------|---------|
| `resources/starter-templates/*.json` | During `/design init` when copying a template | Pre-built token sets for common aesthetics |
| `resources/token-schema.json` | When validating custom-created token files | JSON Schema (draft 2020-12) for token structure |
| `resources/templates/screen-brief.md` | During `/design generate` when user needs a brief template | Structured input for screen generation |
| `resources/prompts/stitch-context-template.md` | Legacy Stitch workflow only | Mustache-style template for Stitch context |

---

## Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `hooks/check-token-drift.sh` | PostToolUse | Passive drift hints — outputs JSON `systemMessage` when drift detected |
| `hooks/pre-commit-drift.sh` | git pre-commit | Block commits with token drift (runs mtime check first for speed) |
