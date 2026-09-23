# -*- mode: python ; coding: utf-8 -*-
"""Production PyInstaller spec for LYRx."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT = Path(SPECPATH)
SRC = ROOT / "src"
ASSETS = ROOT / "assets"
ICON = ASSETS / "icons" / "logo" / "LYRx.ico"


# =========================================================
# BUNDLED APPLICATION ASSETS
# =========================================================

# Keep the EXE self-contained for runtime assets.
#
# Deliberately DO NOT bundle:
# - .env
# - user_data
# - local music
# - cached artwork
# - private credentials
#
# Firebase runtime configuration is generated temporarily by
# build_lyrx.bat and imported as a Python module.
datas = [
    (str(ASSETS), "assets"),
]


# =========================================================
# EXPLICIT HIDDEN IMPORTS
# =========================================================

hiddenimports = [
    # PySide6
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",

    # Configuration / media
    "dotenv",
    "mutagen",
    "mutagen.id3",
    "mutagen.flac",
    "mutagen.mp4",

    # Providers / services
    "services.spotify_provider",
    "services.itunes_provider",
    "services.jamendo_provider",
    "services.youtube_service",
    "services.full_track_resolver",

    # Authentication
    "services.auth.firebase_auth",
    "services.auth._runtime_config",
    "services.auth.google_auth",
    "services.auth.phone_auth",
]


# =========================================================
# COLLECT PROJECT SUBMODULES
# =========================================================

for package in (
    "ui",
    "widgets",
    "services",
    "services.auth",
    "core",
    "data",
    "models",
):
    try:
        hiddenimports.extend(
            collect_submodules(package)
        )
    except Exception:
        pass


# =========================================================
# ANALYSIS
# =========================================================

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


# =========================================================
# PYZ
# =========================================================

pyz = PYZ(
    analysis.pure
)


# =========================================================
# FINAL WINDOWS EXE
# =========================================================

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