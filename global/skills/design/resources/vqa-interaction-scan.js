/**
 * VQA Interaction Scan — Step 2
 * Run AFTER vqa-extract-styles.js (which captures normal state).
 *
 * This script prepares elements for hover scanning.
 * It finds interactive elements, stores their normal-state styles,
 * and exposes a function to read hover-state delta after Chrome MCP hover.
 *
 * WORKFLOW (orchestrated by Claude via Chrome MCP):
 *   1. Run this script → returns element positions for hover targets
 *   2. For each target: Chrome MCP hover(x, y) → run window.__vqa_readHover(index)
 *   3. After all hovers: run window.__vqa_getInteractionReport()
 *
 * Also extracts:
 *   - CSS :hover rules from stylesheets (static)
 *   - transition/animation properties per element (static)
 *   - Keyframe animation definitions (static)
 */
(function() {
  const cs = (el) => el ? getComputedStyle(el) : null;

  // Properties to track for hover delta
  const TRACKED = [
    'color', 'backgroundColor', 'opacity', 'transform',
    'fontWeight', 'fontSize', 'letterSpacing', 'textDecoration',
    'borderColor', 'borderWidth', 'borderRadius',
    'boxShadow', 'filter', 'scale'
  ];

  function snapStyles(el) {
    if (!el) return null;
    const s = cs(el);
    const snap = {};
    for (const p of TRACKED) snap[p] = s[p];
    return snap;
  }

  // Find interactive elements
  const nav = document.querySelector('nav, header');
  const navLinks = nav ? [...nav.querySelectorAll('a')].filter(a =>
    a.textContent.trim().length > 0 && a.textContent.trim().length < 30
  ).slice(0, 4) : [];

  const navCTA = nav ? nav.querySelector('a[class*="btn"], a[class*="button"], a[class*="cta"], a[href*="download"]') : null;

  const allButtons = [...document.querySelectorAll('a, button')].filter(el => {
    const s = cs(el);
    return s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent'
      && el.offsetHeight > 35 && !el.closest('nav, header');
  });
  const heroCTA = allButtons[0];

  // Build target list with coordinates
  const targets = [];
  function addTarget(el, label) {
    if (!el) return;
    const rect = el.getBoundingClientRect();
    targets.push({
      label,
      text: el.textContent?.trim().substring(0, 30),
      x: Math.round(rect.left + rect.width / 2),
      y: Math.round(rect.top + rect.height / 2),
      normalStyles: snapStyles(el),
      hoverStyles: null,  // filled after Chrome MCP hover
      transition: cs(el).transition,
      cursor: cs(el).cursor,
      _el: el  // internal ref, not serialized
    });
  }

  navLinks.forEach((el, i) => addTarget(el, `navLink_${i}`));
  addTarget(navCTA, 'navCTA');
  addTarget(heroCTA, 'heroCTA');

  // Extract :hover CSS rules from stylesheets
  const hoverRules = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.selectorText?.includes(':hover')) {
          const props = {};
          for (const p of rule.style) props[p] = rule.style.getPropertyValue(p).trim();
          if (Object.keys(props).length > 0) {
            hoverRules.push({ selector: rule.selectorText.substring(0, 100), props });
          }
        }
      }
    } catch(e) {}
  }

  // Extract keyframe animations
  const keyframes = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.type === CSSRule.KEYFRAMES_RULE) {
          keyframes.push({ name: rule.name, css: rule.cssText.substring(0, 300) });
        }
      }
    } catch(e) {}
  }

  // Store globally for hover readback
  window.__vqa_targets = targets;

  // Call this AFTER Chrome MCP hover on target[index]
  window.__vqa_readHover = function(index) {
    const t = window.__vqa_targets[index];
    if (!t || !t._el) return JSON.stringify({error: 'invalid index'});
    t.hoverStyles = snapStyles(t._el);
    // Compute delta
    const delta = {};
    for (const p of TRACKED) {
      if (t.normalStyles[p] !== t.hoverStyles[p]) {
        delta[p] = { from: t.normalStyles[p], to: t.hoverStyles[p] };
      }
    }
    return JSON.stringify({ label: t.label, delta, transition: t.transition });
  };

  // Call this AFTER all hovers to get full report
  window.__vqa_getInteractionReport = function() {
    const report = window.__vqa_targets.map(t => {
      const delta = {};
      if (t.hoverStyles) {
        for (const p of TRACKED) {
          if (t.normalStyles[p] !== t.hoverStyles[p]) {
            delta[p] = { from: t.normalStyles[p], to: t.hoverStyles[p] };
          }
        }
      }
      return {
        label: t.label,
        text: t.text,
        transition: t.transition,
        cursor: t.cursor,
        hoverDelta: Object.keys(delta).length > 0 ? delta : 'no change detected',
        hasHoverData: !!t.hoverStyles
      };
    });
    return JSON.stringify({
      hoverRules,
      keyframes,
      elements: report
    }, null, 2);
  };

  // Return hover targets with coordinates (for Chrome MCP hover)
  const serializable = targets.map(t => ({
    label: t.label,
    text: t.text,
    x: t.x,
    y: t.y,
    transition: t.transition,
    cursor: t.cursor
  }));

  return JSON.stringify({
    targetCount: serializable.length,
    targets: serializable,
    hoverRuleCount: hoverRules.length,
    keyframeCount: keyframes.length,
    instruction: 'For each target: Chrome MCP hover(x, y) → then run window.__vqa_readHover(index). After all: window.__vqa_getInteractionReport()'
  }, null, 2);
})();
