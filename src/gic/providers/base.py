"""Provider abstract interface and request/response types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


class ProviderError(RuntimeError):
    """Raised for provider-side failures (auth, API errors, refusals)."""


@dataclass
class GenerateRequest:
    prompt: str
    output_path: Path
    references: list[Path] = field(default_factory=list)
    mask: Path | None = None
    model: str | None = None
    size: str = "1k"
    quality: str = "auto"
    n: int = 1
    background: str = "auto"
    output_format: str = "png"
    user: str | None = None

    @property
    def is_edit(self) -> bool:
        return bool(self.references)

    @property
    def is_inpaint(self) -> bool:
        return self.is_edit and self.mask is not None


@dataclass
class GenerateResult:
    files: list[Path]
    provider: str
    model: str


class Provider(ABC):
    """Abstract base for all image providers."""

    name: str = "base"
    default_model: str = ""
    api_key_env: str = ""

    @abstractmethod
    def generate(self, req: GenerateRequest) -> GenerateResult:
        """Run a generation/edit/inpaint request and write output files to disk."""
        raise NotImplementedError
