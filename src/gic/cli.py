"""`gic` CLI entry point."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from .env import load_env
from .providers import GenerateRequest, ProviderError, get_provider


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gic",
        description="Multi-provider AI image generation CLI (gpt-image-cookbook).",
    )
    p.add_argument("-p", "--prompt", required=True, help="prompt or edit instruction")
    p.add_argument("-f", "--file", type=Path, help="output path; auto-named if omitted")
    p.add_argument(
        "-i",
        "--image",
        action="append",
        type=Path,
        default=[],
        help="reference image (repeatable; switches to edits endpoint)",
    )
    p.add_argument(
        "-m", "--mask", type=Path, help="PNG alpha mask for inpaint; requires -i"
    )
    p.add_argument(
        "--provider",
        default=None,
        help="provider: openai (default), atlascloud, imagen, flux. Falls back to GIC_DEFAULT_PROVIDER env.",
    )
    p.add_argument("--model", help="override the provider's default model")
    p.add_argument(
        "--size",
        default="1k",
        help="1k, 2k, 4k, portrait, landscape, square, wide, tall, or literal WxH",
    )
    p.add_argument(
        "--quality", default="auto", choices=["low", "medium", "high", "auto"]
    )
    p.add_argument("-n", "--n", type=int, default=1, help="number of images")
    p.add_argument(
        "--background",
        default="auto",
        choices=["auto", "opaque", "transparent"],
    )
    p.add_argument(
        "--format", dest="output_format", default="png", choices=["png", "jpeg", "webp"]
    )
    p.add_argument("--user", help="optional end-user identifier passed to provider")
    return p


def _resolve_provider(arg: str | None) -> str:
    return arg or os.environ.get("GIC_DEFAULT_PROVIDER") or "openai"


def _auto_output_path(prompt: str, fmt: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = "".join(
        c.lower() if c.isalnum() else "-" for c in prompt[:40]
    ).strip("-")
    if not slug:
        slug = "image"
    return Path("generated") / f"{ts}-{slug}.{fmt}"


def main(argv: list[str] | None = None) -> int:
    load_env()
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.mask and not args.image:
        print("error: --mask requires at least one -i/--image reference", file=sys.stderr)
        return 2

    provider_name = _resolve_provider(args.provider)
    output = args.file or _auto_output_path(args.prompt, args.output_format)

    req = GenerateRequest(
        prompt=args.prompt,
        output_path=output,
        references=args.image,
        mask=args.mask,
        model=args.model,
        size=args.size,
        quality=args.quality,
        n=args.n,
        background=args.background,
        output_format=args.output_format,
        user=args.user,
    )

    try:
        provider = get_provider(provider_name)
        result = provider.generate(req)
    except ProviderError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    for path in result.files:
        print(str(path))
    print(
        f"# provider={result.provider} model={result.model} mode="
        f"{'inpaint' if req.is_inpaint else 'edit' if req.is_edit else 'generate'}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
