import sys
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent

SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(
    0,
    str(SRC_DIR)
)


# ============================================================
# IMPORT ONLINE MUSIC SERVICE
# ============================================================

from services.music_service import music_service


# ============================================================
# DAY 19 - ONLINE MUSIC TEST
# ============================================================

print()
print("=" * 60)
print("LYRx DAY 19 - ONLINE MUSIC TEST")
print("=" * 60)

print(
    "\nMusic service configured:",
    music_service.is_configured()
)


# ============================================================
# POPULAR ONLINE SONGS
# ============================================================

print(
    "\nFetching online songs..."
)

songs = music_service.safe_popular_tracks(
    10
)


# ============================================================
# RESULT
# ============================================================

print(
    "\nONLINE SONGS FOUND:",
    len(songs)
)


if not songs:

    print(
        "\nNo songs were returned."
    )

    print(
        "Check JAMENDO_CLIENT_ID and internet connection."
    )


# ============================================================
# DISPLAY SONGS
# ============================================================

for index, song in enumerate(
    songs,
    start=1
):

    print()
    print(
        f"{index}. {song.title}"
    )

    print(
        "   Artist:",
        song.artist
    )

    print(
        "   Album:",
        song.album
    )

    print(
        "   Duration:",
        song.duration_text()
    )

    print(
        "   Source:",
        song.source
    )

    print(
        "   Audio:",
        song.audio_url[:100]
    )

    print(
        "   Image:",
        song.image_url[:100]
    )

    print(
        "   Downloadable:",
        song.downloadable
    )


# ============================================================
# FINISH
# ============================================================

print()
print("=" * 60)
print("DAY 19 ONLINE MUSIC TEST COMPLETE")
print("=" * 60)
print()