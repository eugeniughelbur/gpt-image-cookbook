# Cookbook Gallery — Routing Index

This file is the **first thing the agent loads**. It tells the agent which category file to open next based on the user's request. Keep it short and high-signal.

Each category gets one row. The agent loads exactly one category file for normal requests, two or three for hybrids.

## How to read this

For a given request, match the user's intent to one or more categories below, then open the corresponding `gallery-<slug>.md` file. Read actual `**Prompt**` text inside before choosing a pattern — never guess from the category name alone.

## Categories

| Category | When to use | File |
|---|---|---|
| Posters & typography | Posters, type-led design, exact text rendering, lockups | `gallery-posters.md` |
| UI / UX mockups | App screens, dashboards, settings UI, web layouts | `gallery-ui.md` |
| Photography | Photoreal scenes, portraits, products, lifestyle | `gallery-photography.md` |
| Illustration | Editorial, flat, line, character work | `gallery-illustration.md` |
| Diagrams & data viz | Charts, infographics, scientific figures, paper figures | `gallery-diagrams.md` |
| Brand systems | Logos, identity systems, packaging, brand guides | `gallery-brand.md` |
| Edit & inpaint | Reference-image edits, inpainting workflows, multi-reference | `gallery-edits.md` |

## Adding a new category

1. Create `gallery-<slug>.md` with at least 3 working prompts and a thumbnail in `docs/<slug>/`.
2. Add a row above with a clear one-line "when to use".
3. Keep this index under ~20 rows — split or merge categories before it gets noisy.

## Loading policy

- Default: load exactly one category file based on the request.
- Hybrid requests (e.g. "poster with a chart"): load up to two.
- Never load all categories by default.
- If no category matches, fall back to `craft.md` and ask the user for direction.
