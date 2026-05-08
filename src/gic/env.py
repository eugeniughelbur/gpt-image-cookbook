"""Env loading: process env > ./.env > ~/.env. Never overrides existing values."""

from __future__ import annotations

import os
from pathlib import Path


def load_env() -> None:
    """Load .env files into os.environ without overriding existing values."""
    candidates = [Path.cwd() / ".env", Path.home() / ".env"]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
