/**
 * VQA Style Extraction Script
 * Run via Chrome MCP javascript_tool on both reference and generated sites.
 * Extracts component-level computed styles for structured comparison.
 *
 * Usage: Chrome MCP → javascript_tool → paste this script
 * Returns: JSON with component-level style data
 */
(function() {
  const cs = (el) => el ? getComputedStyle(el) : null;

  function extractEl(el, label) {
    if (!el) return null;
    const s = cs(el);
    return {
      label,
      tag: el.tagName,
      text: el.textContent?.trim().substring(0, 60),
      font: {
        family: s.fontFamily?.split(',')[0].replace(/['"]/g, '').trim(),
        size: s.fontSize,
        weight: s.fontWeight,
        letterSpacing: s.letterSpacing,
        lineHeight: s.lineHeight,
        textTransform: s.textTransform
      },
      color: s.color,
      bg: s.backgroundColor,
      border: {
        radius: s.borderRadius,
        width: s.borderWidth,
        color: s.borderColor,
        style: s.borderStyle
      },
      spacing: {
        padding: s.padding,
        margin: s.margin,
        height: s.height,
        width: s.width
      },
      depth: {
        boxShadow: s.boxShadow,
        backdropFilter: s.backdropFilter || s.webkitBackdropFilter,
        opacity: s.opacity,
        mixBlendMode: s.mixBlendMode
      },
      position: s.position
    };
  }

  // Find elements by role
  const nav = document.querySelector('nav, header, [class*="nav"]');
  const navLinks = nav ? [...nav.querySelectorAll('a')].filter(a =>
    !a.querySelector('img') && a.textContent.trim().length < 30
  ) : [];
  const navCTA = navLinks.find(a => {
    const s = cs(a);
    return s.backgroundColor !== 'rgba(0, 0, 0, 0)' &&
           s.backgroundColor !== 'transparent' ||
           s.borderWidth !== '0px';
  });

  const h1 = document.querySelector('h1');
  const subtitle = h1 ? h1.previousElementSibling || h1.parentElement?.querySelector('p') : null;

  // Find hero CTA — largest prominent button near h1
  const allButtons = [...document.querySelectorAll('a, button')].filter(el => {
    const s = cs(el);
    const bg = s.backgroundColor;
    return bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent' &&
           el.offsetHeight > 35 && el.closest('nav, header') === null;
  });
  const heroCTA = allButtons[0];

  // Find mockup/screenshot container
  const mockup = document.querySelector(
    '[class*="mockup"], [class*="browser"], [class*="preview"], [class*="demo"], [class*="screenshot"]'
  ) || document.querySelector('section img, main img');

  // Find announcement bar/pill
  const announcement = document.querySelector(
    '[class*="announce"], [class*="banner"], [class*="notification"], [class*="alert"]:not([role])'
  );

  // Background/gradient of hero area
  const hero = document.querySelector(
    'section, [class*="hero"], main'
  );
  const heroStyles = hero ? {
    background: cs(hero).background?.substring(0, 500),
    backgroundColor: cs(hero).backgroundColor
  } : null;

  // Body
  const body = cs(document.body);

  // CSS custom properties
  const cssVars = {};
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.selectorText?.includes(':root') || rule.selectorText === 'html') {
          for (const prop of rule.style) {
            if (prop.startsWith('--')) {
              cssVars[prop] = rule.style.getPropertyValue(prop).trim();
            }
          }
        }
      }
    } catch(e) {}
  }

  return JSON.stringify({
    url: location.href,
    viewport: { w: innerWidth, h: innerHeight },
    body: {
      fontFamily: body.fontFamily?.split(',')[0].replace(/['"]/g, '').trim(),
      fontSize: body.fontSize,
      color: body.color,
      backgroundColor: body.backgroundColor
    },
    nav: extractEl(nav, 'nav'),
    navLink: navLinks[0] ? extractEl(navLinks[0], 'nav-link') : null,
    navCTA: extractEl(navCTA, 'nav-cta'),
    subtitle: extractEl(subtitle, 'subtitle'),
    h1: extractEl(h1, 'h1'),
    heroCTA: extractEl(heroCTA, 'hero-cta'),
    mockup: extractEl(mockup, 'mockup'),
    announcement: extractEl(announcement, 'announcement'),
    heroBackground: heroStyles,
    cssVarCount: Object.keys(cssVars).length,
    cssVars: Object.fromEntries(
      Object.entries(cssVars).slice(0, 50)
    )
  }, null, 2);
})();
