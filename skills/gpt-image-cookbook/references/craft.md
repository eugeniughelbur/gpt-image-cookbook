# Prompt Craft Cheatsheet

Loaded when:
- The gallery has no close match
- The request involves dense text, exact typography, UI grammar, data viz, multi-panel layouts
- A first generation came back wrong and needs prompt repair

## The four levers

Every image prompt is a combination of these. Tune the weakest one first.

1. **Subject** — what the image is *of*. Concrete nouns beat adjectives.
2. **Composition** — framing, camera angle, focal length, where the subject sits in the frame.
3. **Style** — medium, era, artistic reference, color treatment, mood.
4. **Constraints** — exact text, aspect ratio, what must NOT appear, mandatory elements.

## Universal anatomy

```
[Subject] [doing what], [composition], [style/medium], [lighting], [color palette],
[constraints: exact text, must-have elements], [negatives: what to exclude],
[aspect/format hint].
```

## Exact text rendering

For posters, UI copy, signage, labels — text must be quoted exactly:

> The headline reads exactly: **"Your headline here"** in [font style], all caps, kerning tight.

Rules:
- Quote the literal string. Do not paraphrase.
- Specify font character (bold sans, condensed serif, hand-drawn marker) — providers don't honor specific font names reliably, but they honor character.
- For long strings, render at `--quality high`. Low/medium quality regularly mangles text >5 words.
- For non-Latin scripts (Chinese, Arabic, Cyrillic), state the script explicitly: "Simplified Chinese characters" / "Cyrillic" / "Arabic script".

## UI/UX mockups

```
[App type] interface, [screen purpose], [layout: list/grid/sidebar/etc],
[components: buttons labeled "X", input fields with placeholder "Y", cards],
[design system tone], [theme: light/dark], [device frame or none], [aspect ratio].
```

Rules:
- Name every label in quotes.
- State the platform (iOS, Android, web) — providers render different chrome.
- For dashboards, specify the chart type and what data it represents.

## Diagrams & data viz

```
[Diagram type: bar/line/flow/architecture/anatomy], [what it shows], [labeled elements: A, B, C with arrows from A → B],
[style: editorial / technical / textbook], [color: limited palette / monochrome],
[whitespace level], [optional title text rendered exactly].
```

Rules:
- List every label literally.
- Specify direction of arrows (left-to-right, radial).
- State whether labels go *inside* shapes or in a legend.

## Edit / inpainting invariants

When editing a reference image, you must state what stays and what changes.

```
Edit the reference image. PRESERVE: [subject's face, pose, background composition].
CHANGE: [shirt color from blue to red, add sunglasses].
Do not alter the rest of the image.
```

For inpainting (with mask):
```
Within the masked region only, [describe what fills the masked area].
Match the lighting, perspective, and grain of the surrounding image.
```

Rules:
- Always have a "preserve" list. Without it, providers redraw too much.
- Match the original style language ("photorealistic," "watercolor," etc.) so the edit blends.

## Multi-panel & consistency

For comics, storyboards, before/after, character sheets:

```
[N] panels, [layout: horizontal strip / 2x2 grid / vertical scroll].
Panel 1: [subject + action + framing].
Panel 2: [...].
Same character across all panels: [character description, reusable].
Consistent style: [single style descriptor used everywhere].
```

## Repair patterns

When generation came back wrong:

| Problem | Fix |
|---|---|
| Text is garbled | Bump to `--quality high`; shorten the string; quote it more emphatically |
| Wrong subject | Move subject to start of prompt; add concrete nouns |
| Style drift | Add style descriptor twice — once early, once at end |
| Composition off | State framing explicitly: "centered, full body, eye-level camera" |
| Extra elements appeared | Add a negative: "no text, no logos, no people in background" |
| Edit changed too much | Add a stronger PRESERVE clause; state what NOT to touch |

## Negatives that actually work

Most providers don't have true negative prompts, but stating exclusions in the prompt does help.

```
... no text overlay, no watermark, no human figures, no logos, no UI chrome ...
```

Keep negatives short and specific. Long negative lists confuse the model.

## Cost-aware drafting

1. Draft at `--quality low` to validate composition and subject.
2. Move to `--quality medium` to dial in style.
3. Final at `--quality high` only when the prompt is locked.

This is 5–10x cheaper than starting at high.
