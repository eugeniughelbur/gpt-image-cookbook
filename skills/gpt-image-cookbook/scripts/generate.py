#!/usr/bin/env python3
"""Launcher for the `gic` CLI.

Resolution order:
1. Repo-local `src/gic` if running inside this repo (PYTHONPATH-aware).
2. Installed `gic` on PATH.
3. Transient `uvx --from git+https://github.com/eugeniughelbur/gpt-image-cookbook gic`.

Forwards all argv to the CLI's main entry point.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    args = sys.argv[1:]

    repo_root = Path(__file__).resolve().parents[3]
    repo_src = repo_root / "src"
    if (repo_src / "gic" / "cli.py").exists():
        env = os.environ.copy()
        existing_pp = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{repo_src}{os.pathsep}{existing_pp}" if existing_pp else str(repo_src)
        )
        return subprocess.call([sys.executable, "-m", "gic.cli", *args], env=env)

    if shutil.which("gic"):
        return subprocess.call(["gic", *args])

    if shutil.which("uvx"):
        return subprocess.call([
            "uvx",
            "--from",
            "git+https://github.com/eugeniughelbur/gpt-image-cookbook",
            "gic",
            *args,
        ])

    print(
        "gic CLI not found. Install with `pip install gpt-image-cookbook` "
        "or run via `uvx --from git+https://github.com/eugeniughelbur/gpt-image-cookbook gic`.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
