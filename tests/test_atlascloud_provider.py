from unittest.mock import MagicMock, patch

import httpx
import pytest

from gic.providers.atlascloud_provider import AtlasCloudProvider, _resolve_size
from gic.providers.base import GenerateRequest, ProviderError


def _response(
    status_code: int, payload: dict | None = None, content: bytes = b""
) -> httpx.Response:
    request = httpx.Request("GET", "https://example.test")
    return (
        httpx.Response(status_code, request=request, json=payload)
        if payload is not None
        else httpx.Response(status_code, request=request, content=content)
    )


def test_size_aliases_and_literal_mapping():
    assert _resolve_size("square") == "2048*2048"
    assert _resolve_size("2560x1440") == "2848*1600"
    assert _resolve_size("3840x2160") == "4096*2304"


def test_generation_submits_once_and_polls_with_get(monkeypatch, tmp_path):
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "private-test-key")
    monkeypatch.setenv("ATLASCLOUD_API_BASE", "https://api.atlascloud.ai/v1")
    output = tmp_path / "result.png"
    req = GenerateRequest(prompt="draw a test", output_path=output)
    client = MagicMock()
    client.__enter__.return_value = client
    client.__exit__.return_value = False
    client.post.return_value = _response(
        200,
        {"data": {"id": "prediction-1", "status": "starting"}},
    )
    client.get.side_effect = [
        _response(200, {"data": {"status": "processing"}}),
        _response(
            200,
            {
                "data": {
                    "status": "completed",
                    "outputs": ["https://example.test/result.png"],
                }
            },
        ),
        _response(200, content=b"png-bytes"),
    ]

    with (
        patch("gic.providers.atlascloud_provider.httpx.Client", return_value=client),
        patch("gic.providers.atlascloud_provider.time.sleep"),
    ):
        result = AtlasCloudProvider().generate(req)

    assert client.post.call_count == 1
    assert client.post.call_args.args[0] == (
        "https://api.atlascloud.ai/api/v1/model/generateImage"
    )
    assert client.get.call_count == 3
    assert client.post.call_args.kwargs["json"] == {
        "model": "bytedance/seedream-v5.0-lite",
        "prompt": "draw a test",
        "size": "2048*2048",
        "output_format": "png",
    }
    assert output.read_bytes() == b"png-bytes"
    assert result.provider == "atlascloud"


def test_edit_uses_edit_model_and_data_uri(monkeypatch, tmp_path):
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "private-test-key")
    reference = tmp_path / "reference.png"
    reference.write_bytes(b"reference")
    req = GenerateRequest(
        prompt="edit it",
        output_path=tmp_path / "result.png",
        references=[reference],
    )
    client = MagicMock()
    client.__enter__.return_value = client
    client.__exit__.return_value = False
    client.post.return_value = _response(200, {"data": {"id": "prediction-2"}})
    client.get.side_effect = [
        _response(
            200,
            {
                "data": {
                    "status": "completed",
                    "outputs": ["https://example.test/result.png"],
                }
            },
        ),
        _response(200, content=b"edited"),
    ]

    with patch("gic.providers.atlascloud_provider.httpx.Client", return_value=client):
        result = AtlasCloudProvider().generate(req)

    payload = client.post.call_args.kwargs["json"]
    assert payload["model"] == "bytedance/seedream-v5.0-lite/edit"
    assert payload["images"][0].startswith("data:image/png;base64,")
    assert result.files[0].read_bytes() == b"edited"


def test_unsupported_options_fail_before_network(monkeypatch, tmp_path):
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "private-test-key")
    req = GenerateRequest(
        prompt="draw a test",
        output_path=tmp_path / "result.webp",
        output_format="webp",
    )
    with pytest.raises(ProviderError, match="png or jpeg"):
        AtlasCloudProvider().generate(req)
