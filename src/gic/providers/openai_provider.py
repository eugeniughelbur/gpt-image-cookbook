"""OpenAI gpt-image-2 provider — text-to-image, edits, inpainting."""

from __future__ import annotations

import base64
import os
from pathlib import Path

import httpx

from .base import GenerateRequest, GenerateResult, Provider, ProviderError

_BASE_URL = "https://api.openai.com/v1"

_SIZE_MAP = {
    "1k": "1024x1024",
    "2k": "2048x2048",
    "4k": "4096x4096",
    "square": "1024x1024",
    "portrait": "1024x1536",
    "landscape": "1536x1024",
    "wide": "1536x1024",
    "tall": "1024x1536",
}


def _resolve_size(size: str) -> str:
    return _SIZE_MAP.get(size, size)


class OpenAIProvider(Provider):
    name = "openai"
    default_model = "gpt-image-2"
    api_key_env = "OPENAI_API_KEY"

    def generate(self, req: GenerateRequest) -> GenerateResult:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise ProviderError(
                f"missing {self.api_key_env}. Set it in your environment or .env."
            )

        model = req.model or self.default_model
        size = _resolve_size(req.size)
        headers = {"Authorization": f"Bearer {api_key}"}

        params: dict[str, object] = {
            "model": model,
            "prompt": req.prompt,
            "size": size,
            "n": req.n,
        }
        if req.quality and req.quality != "auto":
            params["quality"] = req.quality
        if req.background and req.background != "auto":
            params["background"] = req.background
        if req.user:
            params["user"] = req.user
        if req.output_format and req.output_format != "png":
            params["output_format"] = req.output_format

        try:
            if req.is_edit:
                resp = self._call_edits(headers, params, req)
            else:
                resp = self._call_generations(headers, params)
        except httpx.HTTPError as e:
            raise ProviderError(f"OpenAI request failed: {e}") from e

        return self._write_outputs(resp, req)

    def _call_generations(
        self, headers: dict[str, str], params: dict[str, object]
    ) -> dict:
        url = f"{_BASE_URL}/images/generations"
        with httpx.Client(timeout=300) as client:
            r = client.post(url, headers=headers, json=params)
        if r.status_code >= 400:
            raise ProviderError(f"OpenAI {r.status_code}: {r.text}")
        return r.json()

    def _call_edits(
        self,
        headers: dict[str, str],
        params: dict[str, object],
        req: GenerateRequest,
    ) -> dict:
        url = f"{_BASE_URL}/images/edits"
        files: list[tuple[str, tuple[str, bytes, str]]] = []
        for ref in req.references:
            files.append(("image[]", (ref.name, ref.read_bytes(), "image/png")))
        if req.mask:
            files.append(
                ("mask", (req.mask.name, req.mask.read_bytes(), "image/png"))
            )
        data = {k: str(v) for k, v in params.items()}
        with httpx.Client(timeout=300) as client:
            r = client.post(url, headers=headers, data=data, files=files)
        if r.status_code >= 400:
            raise ProviderError(f"OpenAI {r.status_code}: {r.text}")
        return r.json()

    def _write_outputs(self, resp: dict, req: GenerateRequest) -> GenerateResult:
        items = resp.get("data") or []
        if not items:
            raise ProviderError(f"OpenAI returned no images: {resp}")

        out_paths: list[Path] = []
        for idx, item in enumerate(items):
            target = self._target_path(req.output_path, idx, len(items))
            target.parent.mkdir(parents=True, exist_ok=True)
            b64 = item.get("b64_json")
            url = item.get("url")
            if b64:
                target.write_bytes(base64.b64decode(b64))
            elif url:
                with httpx.Client(timeout=120) as client:
                    img = client.get(url)
                img.raise_for_status()
                target.write_bytes(img.content)
            else:
                raise ProviderError(f"OpenAI image {idx} had no b64_json or url")
            out_paths.append(target)

        return GenerateResult(
            files=out_paths,
            provider=self.name,
            model=str(req.model or self.default_model),
        )

    @staticmethod
    def _target_path(base: Path, idx: int, total: int) -> Path:
        if total == 1:
            return base
        stem, suffix = base.stem, base.suffix or ".png"
        return base.with_name(f"{stem}-{idx + 1}{suffix}")
