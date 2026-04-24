# Architecture Viz — Water Machine (v1.0)

**Status:** shipped 2026-04-24. First complete version of the metaphorical architecture visualization.

## What this is

Interactive HTML/SVG explorable explanation of Memory Kit architecture, built for **non-technical audiences** — specifically Russian-speaking marketers and CMOs at 50-200 emp agencies. Single self-contained file, no build step, pure CSS animations + vanilla JS.

Complements the existing pyramid diagrams in the main `README.md` with an alternative metaphor (water + vessels + mechanical apparatus) that communicates the **dynamic** aspects of memory architecture that static pyramids can't — promotion, splitting, trigger-routing, pressure.

## How to open

```bash
open experiments/architecture-viz-water-machine/index.html
```

For full interaction testing (some browsers gate `file://` scripts), serve via:

```bash
cd experiments/architecture-viz-water-machine
python3 -m http.server 8765
# → http://127.0.0.1:8765/index.html
```

## Four scenes (SCQA arc)

### Scene 1 — Playable failure

User lands on the recognizable pain. A single big vessel, six buttons labeled with real agency context («Бренд-гайд клиента», «Архив кампаний, 50 страниц», «Tone of voice», etc.) Each click adds water and climbs the manometer «Риск потери контекста». Cracks appear at 85%, verdict banner at 100%: «Память закончилась».

This scene answers «а почему просто не скинуть весь бриф в чат?» by making the user experience the answer, not just read it.

### Scene 2 — The machine

Full apparatus reveal. Layers: Hot Path (рабочая память) → Rules (короткие правила) → Playbooks (роль-гайды) → Deep Memory (глубокая память) → Sediment (архив). Interactive legend on the right — hover any item to highlight its vessel in the machine.

Below: **trigger-resonance demo**. Three chips in italic serif represent marketer queries («помоги с типографикой», «собери SEO-стратегию», «проверь tone of voice»). Click one → only the relevant vessels glow terracotta, others dim to 0.32 opacity. The «только нужное поднимается» concept becomes visible.

### Scene 3 — Promotion journey

Four stations show how raw observations become canonical rules via phase transition: **Жидкость → Янтарь → Playbook → Кристалл**. Each phase is grounded in agency reality per Gemini critique — «разовая правка в брифе → частый фидбек от арт-директора → утверждённый закон бренда».

Threshold ladder below: 1× → structured → 3× → ratified → 6mo stable → crystal.

### Scene 4 — Mitosis (splitting)

The best metaphor in the piece. A big vessel contains 3 emerging color clusters (rose / sage / amber) pulsing inside an alarm ring. Agent's proposal quoted in a side panel: «В этом гайде три самостоятельные темы — типографика, цвет, анимация. Разделить по темам?»

Two buttons: **«Разделить по темам»** (black primary) + **«Пока не надо»** (ghost). Click to split → parent fades away, three children ellipses animate outward to their positions, parent becomes a dashed-line index pointer.

Reframed as «агент сам наводит порядок — вы подтверждаете», not «approve every administrative split» (per Gemini's "selling a chore" critique).

## Closing — «Что дальше»

Three editorial-style links: GitHub repo, full ARCHITECTURE.md, README. Low-pressure, invitation to explore.

## Design language

Separate visual identity from any other project. Editorial-atelier feel, not SaaS.

| Element | Value | Intent |
|---|---|---|
| Paper | `#F7F3EA` | Warm off-white — feels like aged scientific journal |
| Ink | `#16181C` | Deep warm black for outlines + primary text |
| Fresh water | `#5B8FA8` | Muted teal — observations, daily |
| Amber | `#D4954A` | Warm ochre — structured lessons |
| Crystal | `#BFD2D7` | Pale ice — canonical rules |
| Alarm | `#D65F3E` | Terracotta — critical states, manometer red zone |
| Sage | `#7A9377` | Muted olive — stable states, confirmations |
| Sediment | `#3D3630` | Dark warm brown — archive layer |
| Brass | `#BD9B5D` | Gears / pumps (hooks) |

**Typography:** Instrument Serif (display, editorial warmth) · Inter (body, clean readability) · JetBrains Mono (technical labels, consistency).

## Gemini partnership

Three 3.1 Pro consultations, all adversarial. Full exchange summaries live in the CHANGELOG entry. Short version:

1. **Pre-build pattern harvest** — Gemini recommended SCQA arc (problem first, solution second) + playable failure (Nicky Case pattern) + business-language gauges. All adopted.
2. **Mid-build landing check** — Gemini flagged «selling a chore» in mitosis («вы одобряете» reads as admin). Reframed to «агент сам наводит порядок». Gave Russian-translation subtitles to Hot Path / Playbooks / Deep Memory.
3. **Final adversarial gate** — flagged «800+ строк» as developer jargon → replaced with «десятки новых правил и исключений». Flagged Scene 3 alchemy → grounded in agency reality («разовая правка → фидбек арт-директора → закон бренда»). Flagged missing next-action → added closing section.

Gemini pushbacks I **rejected**: switching to distillation metaphor (his strawman that «ice flows through pipes» — my crystal sits in reservoir, doesn't flow); cutting scenes 3 and 4 entirely (the artifact is educational, not sales); personalized input anchor (too much friction for coffee-break reading).

## Verification

Playwright-driven. 18 active CSS animations inventoried via `document.getAnimations()`. Transform-matrix deltas captured over timed intervals confirm all animations run per declared periods:

- `gear-spin` — 22s full rotation ± 1° tolerance ✓
- `needle-breathe` — 7s oscillation between −45° and −30° ✓
- `drop-fall` — 3.5s cycle with staggered 1.1s / 2.2s delays ✓
- `water-rise`, `wave-shift`, `alarm-ring-pulse`, `cluster-drift-a/b/c` — all verified ✓

Interactive flows tested:
- Scene 1 dump-button chain → 100% fill → cracks + escape drops + verdict ✓
- Scene 1 reset → all buttons re-enabled ✓
- Scene 2 legend hover → vessel highlight + dim-others ✓
- Scene 2 resonance chip click → specific vessels glow + dim-others ✓
- Scene 4 approve → pending fades, children spread to positions ✓
- Scene 4 reject → text updates, stays pending ✓
- Scene 4 reset → returns to pending state ✓
- Mobile layout 480px — all grids stack cleanly ✓

## Technical notes

- Single file. No build step. No external dependencies beyond Google Fonts (Instrument Serif, Inter, JetBrains Mono).
- ~1850 lines HTML + inline CSS + inline JS.
- SVG-based illustrations (scalable, animatable via CSS).
- IntersectionObserver for scroll-reveal on scene entry.
- `prefers-reduced-motion` respected — all animations disabled when user has OS preference set.
- No JS animation loops (no `requestAnimationFrame`); all animation is CSS keyframes, which browsers pause efficiently when offscreen.

## Distribution

**Not suitable as email attachment.** Corporate firewalls and Russian email providers flag large-HTML-with-scripts as suspicious. Share via:

- GitHub Pages (free, works immediately from `/experiments/` folder with Jekyll off)
- Vercel / Netlify drop (zero-config for a static file)
- Linked from the main README as an interactive counterpart to static diagrams

Copy the file to your own hosting if you want to present it in a talk or onboard a new marketer.

## What's explicitly NOT in v1.0

Deferred to v1.1 or killed:

- **Scrubbable scene 3** (scroll-bound promotion animation à la Bartosz Ciechanowski) — added complexity without clear ROI for coffee-break reading. Skipped.
- **Time-lapse mode** — «6 месяцев за 30 секунд», would show natural evolution of the machine. Reserved for v1.1.
- **English translation** — this version Russian-only, targeting Sergey's primary ICP. English pass reserved for distribution to non-Russian audiences.
- **Audio layer** — soft clockwork ticks, water flowing — considered but would violate `prefers-reduced-motion` semantics and complicate mobile autoplay. Skipped.
- **Personalized anchors** (Gemini's "ask user how many pages your brand-guide has") — too much friction for passive reading. Skipped.

## Feedback channels

Currently: Telegram → Sergey. Future: structured form at the end of the visualization for readers to flag which scene confused them most.

---

Built 2026-04-24 by Claude (Opus 4.7) + Sergey over one working session, with three Gemini 3.1 Pro adversarial consultations. Single-file ships.
