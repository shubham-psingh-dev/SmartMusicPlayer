# -*- mode: python ; coding: utf-8 -*-
"""Production PyInstaller spec for LYRx."""

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH)
SRC = ROOT / "src"
ASSETS = ROOT / "assets"
ICON = ASSETS / "icons" / "logo" / "LYRx.ico"

# Keep the EXE self-contained for runtime assets while deliberately NOT
# bundling .env, user_data, local music, cached artwork, or credentials.
datas = [
    (str(ASSETS), "assets"),
]

# PySide6 multimedia backends and provider/auth modules are partly discovered
# dynamically in LYRx, so make those modules explicit for the production build.
hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "dotenv",
    "mutagen",
    "mutagen.id3",
    "mutagen.flac",
    "mutagen.mp4",
    "services.spotify_provider",
    "services.itunes_provider",
    "services.jamendo_provider",
    "services.youtube_service",
    "services.full_track_resolver",
    "services.auth.firebase_auth",
    "services.auth.google_auth",
    "services.auth.phone_auth",
]

# Preserve any dynamically imported submodules used by the existing app.
for package in ("ui", "widgets", "services", "services.auth", "core", "data", "models"):
    try:
        hiddenimports.extend(collect_submodules(package))
    except Exception:
        pass

analysis = Analysis(
    [str(SRC / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=sorted(set(hiddenimports)),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "pytest",
        "IPython",
        "jupyter",
        "notebook",
    ],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="LYRx",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=str(ICON) if ICON.is_file() else None,
)
