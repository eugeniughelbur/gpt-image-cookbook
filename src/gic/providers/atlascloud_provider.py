"""Atlas Cloud provider using its asynchronous image generation API."""

from __future__ import annotations

import base64
import mimetypes
import os
import time
from pathlib import Path

import httpx

from .base import GenerateRequest, GenerateResult, Provider, ProviderError

_BASE_URL = "https://api.atlascloud.ai/api/v1"
_GENERATE_MODEL = "bytedance/seedream-v5.0-lite"
_EDIT_MODEL = "bytedance/seedream-v5.0-lite/edit"
_POLL_INTERVAL_SECONDS = 3
_POLL_TIMEOUT_SECONDS = 300

_SIZE_PRESETS = (
    (2048, 2048),
    (2304, 1728),
    (1728, 2304),
    (2848, 1600),
    (1600, 2848),
    (2496, 1664),
    (1664, 2496),
    (3136, 1344),
    (3072, 3072),
    (3456, 2592),
    (2592, 3456),
    (4096, 2304),
    (2304, 4096),
    (2496, 3744),
    (3744, 2496),
    (4704, 2016),
)

_SIZE_ALIASES = {
    "1k": "2048*2048",
    "2k": "2048*2048",
    "4k": "3072*3072",
    "square": "2048*2048",
    "portrait": "1728*2304",
    "landscape": "2304*1728",
    "wide": "2848*1600",
    "tall": "1600*2848",
}


def _resolve_size(size: str) -> str:
    if size in _SIZE_ALIASES:
        return _SIZE_ALIASES[size]
    if "x" not in size.lower():
        raise ProviderError(
            "Atlas Cloud size must be 1k, 2k, 4k, portrait, landscape, "
            "square, wide, tall, or literal WxH"
        )
    try:
        width_text, height_text = size.lower().split("x", 1)
        width, height = int(width_text), int(height_text)
    except ValueError as exc:
        raise ProviderError(f"invalid Atlas Cloud size: {size}") from exc
    if width <= 0 or height <= 0:
        raise ProviderError(f"invalid Atlas Cloud size: {size}")

    target_ratio = width / height
    tier = 0 if max(width, height) <= 2560 else 1
    candidates = _SIZE_PRESETS[:8] if tier == 0 else _SIZE_PRESETS[8:]
    selected = min(candidates, key=lambda item: abs((item[0] / item[1]) - target_ratio))
    return f"{selected[0]}*{selected[1]}"


def _data_uri(path: Path) -> str:
    if not path.is_file():
        raise ProviderError(f"reference image not found: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _response_data(payload: object) -> dict:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data", payload)
    return data if isinstance(data, dict) else {}


def _output_url(data: dict) -> str | None:
    outputs = data.get("outputs") or data.get("output")
    if isinstance(outputs, str):
        return outputs
    if isinstance(outputs, list) and outputs:
        first = outputs[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            value = first.get("url")
            return value if isinstance(value, str) else None
    return None


class AtlasCloudProvider(Provider):
    name = "atlascloud"
    default_model = _GENERATE_MODEL
    api_key_env = "ATLASCLOUD_API_KEY"

    def generate(self, req: GenerateRequest) -> GenerateResult:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise ProviderError(
                f"missing {self.api_key_env}. Set it in your environment or .env."
            )
        if req.n != 1:
            raise ProviderError("Atlas Cloud currently supports one image per CLI call")
        if req.mask:
            raise ProviderError("Atlas Cloud Seedream edit does not support masks")
        if req.background not in {"", "auto", None}:
            raise ProviderError("Atlas Cloud Seedream does not support background mode")
        if req.output_format not in {"png", "jpeg"}:
            raise ProviderError(
                "Atlas Cloud Seedream output format must be png or jpeg"
            )
        if len(req.references) > 14:
            raise ProviderError(
                "Atlas Cloud Seedream accepts at most 14 reference images"
            )

        model = req.model or (_EDIT_MODEL if req.is_edit else _GENERATE_MODEL)
        payload: dict[str, object] = {
            "model": model,
            "prompt": req.prompt,
            "size": _resolve_size(req.size),
            "output_format": req.output_format,
        }
        if req.is_edit:
            payload["images"] = [_data_uri(path) for path in req.references]

        base_url = os.environ.get("ATLASCLOUD_MEDIA_API_BASE", _BASE_URL).rstrip("/")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "gpt-image-cookbook/0.1 (+https://github.com/eugeniughelbur/gpt-image-cookbook)",
        }
        try:
            with httpx.Client(timeout=60, headers=headers) as client:
                # Generation is billable, so this POST is intentionally never retried.
                response = client.post(f"{base_url}/model/generateImage", json=payload)
                response.raise_for_status()
                data = _response_data(response.json())
                prediction_id = data.get("id") or data.get("prediction_id")
                if not prediction_id:
                    raise ProviderError("Atlas Cloud returned no prediction id")
                urls = data.get("urls") if isinstance(data.get("urls"), dict) else {}
                prediction_url = (
                    urls.get("get") or f"{base_url}/model/prediction/{prediction_id}"
                )
                completed = self._poll(client, str(prediction_url))
                output_url = _output_url(completed)
                if not output_url:
                    raise ProviderError("Atlas Cloud completed without an output URL")
                image = client.get(output_url)
                image.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Atlas Cloud request failed: {exc}") from exc
        except ValueError as exc:
            raise ProviderError(f"Atlas Cloud returned invalid JSON: {exc}") from exc

        req.output_path.parent.mkdir(parents=True, exist_ok=True)
        req.output_path.write_bytes(image.content)
        return GenerateResult(
            files=[req.output_path], provider=self.name, model=str(model)
        )

    @staticmethod
    def _poll(client: httpx.Client, prediction_url: str) -> dict:
        deadline = time.monotonic() + _POLL_TIMEOUT_SECONDS
        while True:
            response = client.get(prediction_url)
            response.raise_for_status()
            data = _response_data(response.json())
            status = str(data.get("status", "")).lower()
            if status in {"completed", "succeeded", "success"}:
                return data
            if status in {"failed", "canceled", "cancelled", "timeout"}:
                detail = data.get("error") or data.get("message") or "no detail"
                raise ProviderError(
                    f"Atlas Cloud prediction ended with status={status}: {detail}"
                )
            if time.monotonic() >= deadline:
                raise ProviderError(
                    "Atlas Cloud prediction timed out after 300 seconds"
                )
            time.sleep(_POLL_INTERVAL_SECONDS)
