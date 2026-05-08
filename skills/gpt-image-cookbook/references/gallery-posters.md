# Gallery — Posters & Typography

Type-led design, posters, lockups, exact text rendering.

## Entry template

```markdown
### Title of the look

**Provider**: openai · **Model**: gpt-image-2 · **Quality**: high · **Size**: portrait

**Prompt**:
```
[Your full prompt here, with exact text in quotes if any]
```

**Notes**: One line on what makes this work.

**Preview**: `docs/posters/poster-XX.png`
```

---

## Typographic minimalism — single-word lockup

**Provider**: openai · **Model**: gpt-image-2 · **Quality**: low · **Size**: square

**Prompt**:
```
minimalist test poster on cream background, single bold word that reads exactly 'cookbook', sans-serif, large kerning, centered
```

**Notes**: Works at `--quality low` because the text is one word. Cream background + black sans = type-led baseline. Increase kerning explicitly or the model packs letters tight.

**Preview**: `docs/posters/poster-01-typographic-cookbook.png`

---

## Photo-led with overlay headline

**Provider**: openai · **Model**: gpt-image-2 · **Quality**: low · **Size**: portrait

**Prompt**:
```
Editorial poster: dramatic close-up of a steaming espresso cup on a wooden bar, warm cinematic lighting, shallow depth of field. Headline overlaid in the lower-third reads exactly: 'BREW SLOW'. Sans-serif, white, all caps, small kerning. Subtle film grain.
```

**Notes**: Two-word all-caps overlays are the safe ceiling for `--quality low`. Stating the overlay zone ("lower-third") gives the composition room; without it the text crashes into the subject. Film grain helps unify text with photo.

**Preview**: `docs/posters/poster-02-photo-led-overlay.png`

---

## Geometric / Bauhaus — shape + headline

**Provider**: openai · **Model**: gpt-image-2 · **Quality**: low · **Size**: square

**Prompt**:
```
Geometric Bauhaus-style poster: large red circle, two black diagonal lines crossing it, beige background. Headline reads exactly 'FORM FOLLOWS' in the top-left, geometric sans-serif, black, all caps. Below it 'FUNCTION' in same style. Tight grid layout, generous negative space.
```

**Notes**: Naming the movement ("Bauhaus") is a strong style anchor. Specify shape *count* and *position* — vague shape requests produce mush. "Generous negative space" prevents the model from filling every inch.

**Preview**: `docs/posters/poster-03-geometric-bauhaus.png`

---

## Adding more

1. Generate via `gic`. Start at `--quality low` to validate composition.
2. Save the keeper to `docs/posters/poster-XX-<slug>.png`.
3. Add an entry above using the template at the top of this file.
4. Open a PR.
