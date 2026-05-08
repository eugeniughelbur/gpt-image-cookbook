---
name: gpt-image-cookbook
description: "Use this skill whenever a user asks to generate, create, draw, render, or edit images with AI image models — gpt-image-2, DALL-E, Google Imagen, Flux, or others. Covers text-to-image, reference-image editing, inpainting, posters, typography, UI mockups, diagrams, and curated gallery prompts. Search the bundled cookbook references for matching patterns, confer on direction when ambiguous, then call the packaged `gic` CLI. Do not write new image-generation code unless the user explicitly asks to modify this repo."
compatibility: "Requires Python 3.11+ and one of `gic`, `uv`, or `uvx`. CLI/API calls read provider API keys from env (`OPENAI_API_KEY`, `GOOGLE_API_KEY`, `FAL_KEY`, etc.) and may incur charges on the user's account."
metadata: {"openclaw":{"requires":{"anyBins":["gic","uv","uvx"]},"primaryEnv":"OPENAI_API_KEY","homepage":"https://github.com/eugeniughelbur/gpt-image-cookbook"}}
---

# gpt-image-cookbook

Agent runbook for multi-provider AI image generation and editing. Use the prompt cookbook + packaged `gic` CLI. Do not reimplement image API code.

## Operating loop

1. **Classify the request**: `generate`, `edit`, `inpaint`, or `multi-reference`. Identify asset type, exact text to render, aspect ratio, references, safety constraints, and budget/quality tier.
2. **Pick a provider**: default to `openai` (`gpt-image-2`). Switch to `imagen` for Google-native quality on photoreal scenes, or `flux` for fast/cheap drafts and stylized art. The user's explicit request always wins.
3. **Search references first**: open `references/gallery.md` (the routing index). Load the closest `references/gallery-<category>.md` file(s). Read actual `**Prompt**` text before choosing a pattern — never guess from category name alone.
4. **Refine with craft**: load `references/craft.md` for dense text, diagrams, UI mockups, data visualization, multi-panel layouts, or when the gallery has no close match.
5. **Confer when useful**: before costly, ambiguous, or high-polish calls, present 1–3 matched directions plus planned size/quality/provider; ask at most one concise question. Skip the discussion for precise "generate now" requests.
6. **Preflight, no side effects**: check `command -v gic` first. Do not reinstall, overwrite skill folders, create or modify `.env`, or write API keys. Global/shared installs are opt-in only.
7. **Execute via CLI only**: call `gic`. Do not create a new `generate.py`, SDK wrapper, or ad-hoc script for normal image requests.
8. **Report**: output file path(s), the provider/model used, key flags, and one concise refinement suggestion if useful.

Fast path: precise prompt + explicit "generate now" → quick reference/craft check, then CLI.

## CLI resolution

Preferred call order:

```bash
# Existing CLI on PATH
gic -p "PROMPT" [-f OUT] [-i REF...] [-m MASK] [--provider openai|imagen|flux] [options]

# Repo-local launcher (when the skill folder is bundled with the runtime)
uv run "$SKILL_DIR/scripts/generate.py" -p "PROMPT" [options]

# Transient install when the user requested a one-off CLI execution
uvx --from git+https://github.com/eugeniughelbur/gpt-image-cookbook gic -p "PROMPT" [options]
```

`scripts/generate.py` is a launcher: repo-local `src/gic` → installed `gic` on PATH → transient `uvx` fallback.

## Provider selection

| Provider | Model default | When to use |
|---|---|---|
| `openai` | `gpt-image-2` | Default. Strong on text rendering, posters, UI mockups, Chinese typography, research figures. |
| `imagen` | `imagen-4` | Photoreal scenes, product shots, faces, lighting realism. Google-account billing. |
| `flux` | `flux-pro-1.1` | Fast/cheap drafts, stylized art, broad style exploration. fal.ai or Replicate billing. |

The CLI resolves the provider from the `--provider` flag, then `GIC_DEFAULT_PROVIDER` env var, then falls back to `openai`.

## Key and cost rules

- The CLI reads provider keys from process env, then `.env`, then `~/.env` without overriding existing env. Successful API calls bill the user's provider account.
- If a host runtime has native platform-managed image generation and the user wants that path, use the host tool instead of this CLI.
- If the required key is unset, report the missing key and the env var name; do not write secrets.
- If the user wants to avoid local-key use, respect `unset OPENAI_API_KEY` (etc.); if a key exists in `.env`/`~/.env`, tell them to remove or rename it for the session rather than working around it.
- Never print secret values.

## Flags

| Flag | Values | Use |
|---|---|---|
| `-p, --prompt` | string | Required prompt or edit instruction |
| `-f, --file` | path | Output path; auto-named if omitted |
| `-i, --image` | repeatable path | Use the edits endpoint; supports multiple references |
| `-m, --mask` | PNG path | Inpaint with alpha mask; requires `-i` |
| `--provider` | `openai`, `imagen`, `flux` | Provider router |
| `--model` | string | Override the provider's default model |
| `--size` | `1k`, `2k`, `4k`, `portrait`, `landscape`, `square`, `wide`, `tall`, or literal `WxH` | Canvas size |
| `--quality` | `low`, `medium`, `high`, `auto` | Cost/quality dial (provider-mapped) |
| `-n, --n` | integer | Number of images |
| `--background` | `auto`, `opaque`, `transparent` | Background mode (provider-dependent) |
| `--format` | `png`, `jpeg`, `webp` | Output encoding |
| `--user` | string | Optional end-user identifier passed to provider |

Quality policy:
- `low`: cheap drafts, broad exploration, many variants.
- `medium`: normal exploration, style probing, balanced cost.
- `high`: final assets, dense text, posters, diagrams, UI mockups, paper figures, dense labels.

Size policy:
- default/social square: `1k` / `1024x1024`
- poster/mobile/beauty: `portrait`
- landscape/gameplay/photo: `landscape`
- print/paper figure: `2k`
- widescreen hero: `4k`
- vertical story/banner: `tall`

## Endpoint routing

| Mode | Trigger | Endpoint family |
|---|---|---|
| Text-to-image | no `-i` | provider's generations endpoint |
| Reference edit | one or more `-i` | provider's edits endpoint |
| Inpaint | `-i` + `-m` | provider's edits endpoint with mask |

Surface API errors verbatim enough for debugging. Exit codes: `0` success, `1` API/refusal, `2` bad args/missing key.

## Reference loading

- `references/gallery.md`: routing index for the cookbook gallery. Load first.
- `references/gallery-*.md`: concrete prompts, previews, paths, metadata. Load 1 category for normal requests; 2–3 for hybrids.
- `references/craft.md`: prompt-craft checklist. Load for prompt repair, exact text rendering, UI/data/diagram grammar, edit invariants, and multi-panel consistency.
- `references/providers.md`: provider/model semantics. Load for API behavior or capability questions.

Reference loading policy: load the smallest useful slice; never load all category files by default.

## Verification

After a generation call:
1. Confirm the output file exists at the reported path.
2. If the prompt requested specific text, verify the text renders correctly — re-run with `--quality high` if it doesn't.
3. For edits/inpainting, confirm the unmasked regions are preserved.
