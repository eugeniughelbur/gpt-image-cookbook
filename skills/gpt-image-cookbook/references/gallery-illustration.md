# Gallery — Illustration

Editorial, flat, line, character work.

See `gallery-posters.md` for the entry template.

---

## Flat editorial illustration — interior scene

**Provider**: openai · **Model**: gpt-image-2 · **Quality**: low · **Size**: square

**Prompt**:
```
Flat editorial illustration, person seated cross-legged on a green couch reading a book, a tabby cat curled on the armrest beside them, indoor scene with a tall potted plant and a brass floor lamp behind the couch. Muted earth-tone palette: olive, warm cream, terracotta, charcoal. Clean shapes, no harsh outlines, gentle grain texture.
```

**Notes**: Specify the palette by name (`olive, cream, terracotta, charcoal`) — vague color requests give muddy results. "No harsh outlines" prevents the model from adding cartoon contours.

**Preview**: `docs/illustration/illo-01-reading-flat.png`

---

## Single continuous-line illustration

**Provider**: openai · **Model**: gpt-image-2 · **Quality**: low · **Size**: square

**Prompt**:
```
Single-line continuous-line illustration of a coffee plant branch with two leaves and three coffee cherries, drawn with one unbroken charcoal-black line of consistent stroke weight on a warm cream background. Generous whitespace, no shading, no fill, calligraphic feel.
```

**Notes**: "Continuous-line" + "consistent stroke weight" + explicit "no shading, no fill" together push the model into the minimalist line look. Without all three it adds texture or breaks the line.

**Preview**: `docs/illustration/illo-02-line-coffee.png`
