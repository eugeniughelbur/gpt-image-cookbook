"""Flux provider — stub. Implement against fal.ai or Replicate."""

from __future__ import annotations

from .base import GenerateRequest, GenerateResult, Provider, ProviderError


class FluxProvider(Provider):
    name = "flux"
    default_model = "flux-pro-1.1"
    api_key_env = "FAL_KEY"

    def generate(self, req: GenerateRequest) -> GenerateResult:
        raise ProviderError(
            "flux provider not yet implemented. "
            "See providers.md for the integration shape, then implement here."
        )
