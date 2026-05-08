<p align="center">
  <a href="https://github.com/eugeniughelbur/gpt-image-cookbook"><img src="docs/assets/hero.png" alt="gpt-image-cookbook — AI image recipes for OpenAI, Imagen, Flux" width="100%"/></a>
</p>

<h1 align="center">gpt-image-cookbook</h1>

<p align="center"><em>Multi-provider AI image generation cookbook — prompt gallery, agentic skill, and CLI for OpenAI gpt-image-2, Google Imagen, Flux, and more.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"/>
  <img src="https://img.shields.io/badge/python-%E2%89%A53.11-blue.svg" alt="Python ≥ 3.11"/>
  <img src="https://img.shields.io/badge/providers-openai%20%7C%20imagen%20%7C%20flux-purple.svg" alt="Providers"/>
</p>

---

## What this is

Three things bundled together:

1. **A curated prompt gallery** — copy-paste prompts organized by category (posters, UI mockups, photography, diagrams, etc.) that produce reliable results across providers.
2. **An agentic skill** — `SKILL.md` runbook for Claude Code, Codex, OpenClaw, Hermes, and other skill-capable agent runtimes. Tells the agent how to search the gallery, refine the prompt, and call the CLI without writing one-off scripts.
3. **A CLI (`gic`)** — one command, multiple providers. Switch between OpenAI `gpt-image-2`, Google Imagen, and Flux with a single `--provider` flag.

---

## Why a cookbook

Most prompt galleries are read-only inspiration. This one is wired into an agent that *uses* the gallery: search → refine → generate, with consistent semantics across providers. The CLI handles auth, encoding, sizing, edits, and inpainting so the agent never reinvents API plumbing.

---

## Install

```bash
# pip
pip install gpt-image-cookbook

# or one-shot via uvx
uvx --from git+https://github.com/eugeniughelbur/gpt-image-cookbook gic --help
```

Set at least one provider key:

```bash
export OPENAI_API_KEY=sk-...        # for openai (default)
export GOOGLE_API_KEY=...           # for imagen
export FAL_KEY=...                  # for flux
```

The CLI also reads `./.env` and `~/.env` (without overriding env vars already set).

---

## Quickstart

```bash
# Text-to-image, OpenAI default
gic -p "A minimalist conference poster, headline reads exactly 'Signal over Noise'" --quality high --size portrait

# Reference edit
gic -p "Make the sky a stormy sunset" -i ref.png

# Inpaint
gic -p "Replace the masked area with a coffee cup" -i ref.png -m mask.png

# Switch provider
gic -p "Photoreal product shot of a ceramic mug on oak" --provider imagen --quality high
```

Outputs land in `./generated/<timestamp>-<slug>.png` unless you pass `-f`.

---

## Use as a Claude Code plugin

```bash
# In Claude Code
/plugin install eugeniughelbur/gpt-image-cookbook
```

The agent loads `skills/gpt-image-cookbook/SKILL.md`, follows the operating loop (classify → search gallery → refine → generate), and calls `gic` for you.

---

## Use as an agent skill (Codex, OpenClaw, Hermes, …)

Point your runtime at `skills/gpt-image-cookbook/SKILL.md`. Compatible runtimes auto-resolve the `gic` CLI via `command -v gic`, `uv`, or `uvx`.

---

## Repo layout

```
.claude-plugin/        # Claude Code plugin + marketplace metadata
skills/
  gpt-image-cookbook/
    SKILL.md           # agent runbook
    references/        # gallery routing index, per-category prompts, craft cheatsheet
    scripts/           # generate.py launcher
    agents/            # runtime metadata for OpenClaw / Hermes / etc.
src/gic/               # the CLI (Python)
docs/                  # gallery thumbnails (added as you build entries)
```

---

## CLI reference

| Flag | Values | Use |
|---|---|---|
| `-p, --prompt` | string | required prompt or edit instruction |
| `-f, --file` | path | output path; auto-named if omitted |
| `-i, --image` | repeatable path | reference image; switches to edits endpoint |
| `-m, --mask` | PNG path | alpha mask for inpaint; requires `-i` |
| `--provider` | `openai`, `imagen`, `flux` | provider router |
| `--model` | string | override the provider's default model |
| `--size` | `1k`, `2k`, `4k`, `portrait`, `landscape`, `square`, `wide`, `tall`, or `WxH` | canvas size |
| `--quality` | `low`, `medium`, `high`, `auto` | cost/quality dial |
| `-n, --n` | integer | number of images |
| `--background` | `auto`, `opaque`, `transparent` | background mode |
| `--format` | `png`, `jpeg`, `webp` | output encoding |
| `--user` | string | passed to provider for end-user attribution |

Exit codes: `0` success · `1` API/refusal · `2` bad args/missing key.

---

## Adding a prompt to the gallery

1. Generate something you like with `gic`.
2. Save the preview thumbnail under `docs/<category>/`.
3. Add an entry to the matching `skills/gpt-image-cookbook/references/gallery-<category>.md` using the template documented inside that file.
4. Open a PR.

---

## Adding a new provider

The provider abstraction lives in `src/gic/providers/`. Each provider implements `Provider.generate(req: GenerateRequest)` and gets registered in `providers/__init__.py`. See `openai_provider.py` for the reference shape.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

Built and maintained by **Eugeniu Ghelbur** ([@eugeniughelbur](https://github.com/eugeniughelbur)).
