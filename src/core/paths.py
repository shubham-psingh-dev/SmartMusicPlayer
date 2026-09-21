from __future__ import annotations

from pathlib import Path
import sys


def runtime_root() -> Path:
    """Return the correct LYRx runtime root in source and PyInstaller builds."""
    bundled_root = getattr(sys, "_MEIPASS", None)
    if bundled_root:
        return Path(bundled_root).resolve()

    # src/core/paths.py -> project root is three parents up.
    return Path(__file__).resolve().parents[2]


def asset_path(*parts: str) -> Path:
    """Resolve a bundled/local asset in both development and packaged LYRx."""
    return runtime_root().joinpath("assets", *parts)
