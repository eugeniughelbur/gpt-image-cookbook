"""Provider registry. Add a new provider by implementing Provider and registering below."""

from __future__ import annotations

from .base import GenerateRequest, Provider, ProviderError
from .openai_provider import OpenAIProvider
from .imagen_provider import ImagenProvider
from .flux_provider import FluxProvider

_REGISTRY: dict[str, type[Provider]] = {
    "openai": OpenAIProvider,
    "imagen": ImagenProvider,
    "flux": FluxProvider,
}


def get_provider(name: str) -> Provider:
    try:
        cls = _REGISTRY[name]
    except KeyError as e:
        known = ", ".join(sorted(_REGISTRY))
        raise ProviderError(f"unknown provider '{name}'. Known: {known}") from e
    return cls()


__all__ = [
    "GenerateRequest",
    "Provider",
    "ProviderError",
    "get_provider",
]
