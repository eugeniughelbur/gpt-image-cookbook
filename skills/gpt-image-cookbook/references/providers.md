# Providers Reference

Per-provider semantics, model defaults, and capability notes. Loaded when the agent needs to know whether a feature is supported, or which provider fits a request.

## openai (default)

- Default model: `gpt-image-2`
- Endpoints: `/v1/images/generations`, `/v1/images/edits`
- Env var: `OPENAI_API_KEY`
- Strengths: text rendering, posters, UI mockups, Chinese typography, research figures, multi-reference edits.
- Sizes: `1024x1024`, `1024x1536`, `1536x1024`, `2048x2048`, `4096x4096` (model-dependent).
- Quality: `low`, `medium`, `high`, `auto`.
- Background: `auto`, `opaque`, `transparent` (gpt-image-2 supports transparent).
- Inpaint: yes, via `/v1/images/edits` with PNG mask (alpha channel = inpaint region).
- Multi-reference: yes, pass multiple `image[]` files to edits endpoint.

## imagen (Google)

- Default model: `imagen-4`
- Endpoint: Vertex AI `predict` or Google AI Studio `generateImages`
- Env var: `GOOGLE_API_KEY` (AI Studio) or `GOOGLE_APPLICATION_CREDENTIALS` (Vertex)
- Strengths: photorealism, faces, product shots, lighting realism, natural scenes.
- Sizes: `1:1`, `9:16`, `16:9`, `3:4`, `4:3` aspect ratios; pixel sizes are model-fixed.
- Quality: not a separate dial — controlled via model variant (`imagen-4` vs `imagen-4-fast`).
- Background: no transparent mode at this writing.
- Inpaint: supported on Vertex AI via the imagegeneration model.
- Multi-reference: limited; check the specific model variant.

## atlascloud

- Default models: `bytedance/seedream-v5.0-lite` for generation and `bytedance/seedream-v5.0-lite/edit` when references are supplied.
- Env var: `ATLASCLOUD_API_KEY`; optional media API override: `ATLASCLOUD_MEDIA_API_BASE`.
- Flow: one asynchronous generation POST followed by bounded prediction GET polling. The billable POST is never retried automatically.
- Sizes: named CLI sizes and literal `WxH` values map to the closest supported Seedream preset.
- Formats: PNG and JPEG.
- Multi-reference: up to 14 local images, encoded as data URIs.
- Not supported: masks, transparent background mode, WebP output, or `n > 1` in one call.

## flux (fal.ai or Replicate)

- Default model: `flux-pro-1.1` (or `flux-schnell` for fast/cheap)
- Endpoints: vendor-specific (fal.ai REST or Replicate predictions API)
- Env var: `FAL_KEY` (fal.ai) or `REPLICATE_API_TOKEN` (Replicate)
- Strengths: speed, cost, stylized art, broad style range, LoRA support on some hosts.
- Sizes: arbitrary `WxH` within model limits.
- Quality: not a dial — pick model variant (`flux-schnell` cheap/fast, `flux-pro` quality).
- Background: depends on host.
- Inpaint: supported via `flux-fill` or vendor-specific edit models.
- Multi-reference: limited to single-reference edits at this writing.

## Routing heuristics (when the user hasn't specified)

| Request shape | Default provider |
|---|---|
| Anything with rendered text (posters, UI, signs, labels) | `openai` |
| Photoreal portraits, products, scenes | `imagen` |
| Drafts, exploration, many variants, stylized art | `flux` (`flux-schnell`) |
| Reference-image edits with text preserved | `openai` |
| Inpainting | provider that already produced the source image, if known; otherwise `openai` |

## Cost notes

Costs change. The CLI does **not** print or estimate costs — it surfaces the provider's invoice channel. Tell the user to check their provider dashboard.

Rough cost order (low to high, as of this writing):
1. `flux-schnell` — cheapest, ~$0.003/image
2. `gpt-image-2` low — ~$0.01/image
3. `imagen-4-fast` — ~$0.02/image
4. `gpt-image-2` medium — ~$0.04/image
5. `imagen-4` — ~$0.04/image
6. `gpt-image-2` high — ~$0.17/image
7. `flux-pro-1.1` — ~$0.04/image

These move; trust the provider's pricing page over this file.

## Capability matrix

| Capability | openai | atlascloud | imagen | flux |
|---|---|---|---|---|
| Text-to-image | ✓ | ✓ | ✓ | ✓ |
| Reference edit (img2img) | ✓ | ✓ | partial | ✓ |
| Inpaint (mask) | ✓ | — | ✓ (Vertex) | ✓ (flux-fill) |
| Multi-reference | ✓ | ✓ | partial | partial |
| Transparent background | ✓ | — | — | — |
| Exact text rendering | strong | strong | medium | weak |
| Photorealism | strong | strong | strongest | strong |
| Speed (low quality) | medium | medium | fast | fastest |
