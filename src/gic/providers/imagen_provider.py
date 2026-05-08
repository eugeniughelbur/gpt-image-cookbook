"""Google Imagen provider — stub. Implement against Vertex AI or AI Studio."""

from __future__ import annotations

from .base import GenerateRequest, GenerateResult, Provider, ProviderError


class ImagenProvider(Provider):
    name = "imagen"
    default_model = "imagen-4"
    api_key_env = "GOOGLE_API_KEY"

    def generate(self, req: GenerateRequest) -> GenerateResult:
        raise ProviderError(
            "imagen provider not yet implemented. "
            "See providers.md for the integration shape, then implement here."
        )
