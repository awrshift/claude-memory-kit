# Screen Brief Template

Use this template when requesting a new screen via `/design generate` with the `frontend-design` plugin. Fill in each section to give the generator enough context for a high-fidelity, token-adherent screen.

---

## Screen

- **Name:** [e.g., "Executive Dashboard", "Brand Detail", "Alert Center"]
- **Actor:** [Who uses this screen? e.g., "Marketing analyst", "Brand manager"]
- **Purpose:** [One sentence — what does the user accomplish here?]

## Layout

Describe the page structure in terms of regions:

- **Sidebar:** [Fixed/collapsible, width, nav items]
- **Header:** [Page title, breadcrumbs, action buttons]
- **Content areas:** [Grid layout, number of columns, card arrangement]
- **Footer/status bar:** [If applicable]

## Data Shape

What data appears on this screen? Include sample values so the generator can create realistic content.

| Element | Type | Sample Value |
|---------|------|-------------|
| [KPI card title] | text | "Total Mentions" |
| [KPI value] | number | "14,238" |
| [Chart] | [bar/line/donut] | [describe series] |
| [Table columns] | list | [col1, col2, col3] |

## Token Overrides

If this page deviates from the default primary action color, specify here.
Most pages use the default `primary` token (amber). Some pages need a different accent to avoid semantic collision.

- **Primary action color:** [default / override token name, e.g., "secondary-action (teal)" for alert-heavy screens]
- **Custom tokens:** [Any page-specific additions]

## Constraints

- [ ] Must be visually consistent with: [list existing screens]
- [ ] Reuse component patterns from: [e.g., "Dashboard KPI cards", "Brands table"]
- [ ] Specific requirements: [e.g., "Sortable table headers", "Date range picker in header"]

## Reference

- **Design tokens:** `design-tokens.json` (auto-injected via Token Injection Protocol)
- **Design rules:** `design-rules.md` (behavioral guidelines)
- **Existing screens:** [List paths to related HTML files for consistency]
