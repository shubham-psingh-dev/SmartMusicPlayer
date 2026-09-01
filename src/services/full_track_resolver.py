# ============================================================
# LYRx
# DAY 21 - PROVIDER PLAYBACK LAYER
#
# FILE 3
# full_track_resolver.py
#
# PURPOSE
# ------------------------------------------------------------
#
# Resolve a Song into a playback strategy:
#
#   1. DIRECT FULL STREAM
#      Example:
#          Jamendo / future licensed direct-stream provider
#
#   2. REMOTE FULL PLAYBACK
#      Example:
#          Spotify Connect after authentication
#
#   3. FULL-TRACK ALTERNATIVE
#      Search another provider for the same song.
#
#   4. PREVIEW
#      Explicitly rejected by default because LYRx Day 21
#      target is full-track playback.
#
#
# IMPORTANT
# ------------------------------------------------------------
#
# This layer does NOT scrape copyrighted media.
# It only works with playback URLs/capabilities supplied
# by registered providers.
#
# Existing UI blueprint is not changed here.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass

from typing import (
    Any,
    Dict,
    Optional,
)

from services.provider_registry import (
    ProviderRegistry,
    provider_registry,
)


# ============================================================
# PLAYBACK MODES
# ============================================================

PLAYBACK_NONE = "none"

PLAYBACK_DIRECT = "direct"

PLAYBACK_REMOTE = "remote"

PLAYBACK_PREVIEW = "preview"


# ============================================================
# RESOLUTION RESULT
# ============================================================

@dataclass
class PlaybackResolution:

    """
    Unified result returned by FullTrackResolver.

    mode
    ----------------------------------------------------------
    direct
        QMediaPlayer can play audio_url.

    remote
        Provider controls playback itself.
        Example: Spotify.

    preview
        Only preview exists.

    none
        No playable source was found.
    """

    success: bool = False

    mode: str = PLAYBACK_NONE

    song: Any = None

    provider: str = ""

    audio_url: str = ""

    message: str = ""

    is_full_track: bool = False

    is_preview: bool = False

    used_alternative: bool = False

    original_song: Any = None

    # ========================================================
    # DICTIONARY
    # ========================================================

    def to_dict(
        self
    ) -> Dict[str, Any]:

        return {

            "success":
                self.success,

            "mode":
                self.mode,

            "song":
                self.song,

            "provider":
                self.provider,

            "audio_url":
                self.audio_url,

            "message":
                self.message,

            "is_full_track":
                self.is_full_track,

            "is_preview":
                self.is_preview,

            "used_alternative":
                self.used_alternative,

            "original_song":
                self.original_song,
        }


# ============================================================
# FULL TRACK RESOLVER
# ============================================================

class FullTrackResolver:

    """
    LYRx playback resolver.

    UI should eventually call:

        resolution = resolver.resolve(song)

    instead of checking:

        song.audio_url
        song.preview_url
        song.provider
        spotify
        jamendo

    everywhere in the app.

    This keeps the playback architecture clean.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
    ):

        self.registry = (
            registry
            if registry is not None
            else provider_registry
        )

    # ========================================================
    # SAFE TEXT
    # ========================================================

    @staticmethod
    def _text(
        value
    ) -> str:

        return str(
            value
            or ""
        ).strip()

    # ========================================================
    # PROVIDER NAME
    # ========================================================

    def provider_name(
        self,
        song
    ) -> str:

        if song is None:

            return ""

        # ----------------------------------------------------
        # Registry helper first.
        # ----------------------------------------------------

        try:

            return self._text(
                self.registry.song_provider_name(
                    song
                )
            ).lower()

        except Exception:

            pass

        # ----------------------------------------------------
        # Compatibility fallback.
        # ----------------------------------------------------

        return self._text(

            getattr(
                song,
                "provider",
                ""
            )

            or

            getattr(
                song,
                "source",
                ""
            )

        ).lower()

    # ========================================================
    # TITLE
    # ========================================================

    @staticmethod
    def song_title(
        song
    ) -> str:

        if song is None:

            return "Unknown Track"

        try:

            if hasattr(
                song,
                "display_title"
            ):

                value = song.display_title()

                if value:

                    return str(
                        value
                    )

        except Exception:

            pass

        return str(
            getattr(
                song,
                "title",
                ""
            )
            or
            "Unknown Track"
        )

    # ========================================================
    # ARTIST
    # ========================================================

    @staticmethod
    def song_artist(
        song
    ) -> str:

        if song is None:

            return "Unknown Artist"

        try:

            if hasattr(
                song,
                "display_artist"
            ):

                value = song.display_artist()

                if value:

                    return str(
                        value
                    )

        except Exception:

            pass

        return str(
            getattr(
                song,
                "artist",
                ""
            )
            or
            "Unknown Artist"
        )

    # ========================================================
    # AUDIO URL
    # ========================================================

    @staticmethod
    def audio_url(
        song
    ) -> str:

        if song is None:

            return ""

        return str(
            getattr(
                song,
                "audio_url",
                ""
            )
            or ""
        ).strip()

    # ========================================================
    # PREVIEW URL
    # ========================================================

    @staticmethod
    def preview_url(
        song
    ) -> str:

        if song is None:

            return ""

        return str(
            getattr(
                song,
                "preview_url",
                ""
            )
            or ""
        ).strip()

    # ========================================================
    # METADATA
    # ========================================================

    @staticmethod
    def metadata(
        song
    ) -> Dict[str, Any]:

        if song is None:

            return {}

        value = getattr(
            song,
            "metadata",
            {}
        )

        if isinstance(
            value,
            dict
        ):

            return value

        return {}

    # ========================================================
    # PLAYBACK MODE FROM METADATA
    # ========================================================

    def metadata_playback_mode(
        self,
        song
    ) -> str:

        metadata = (
            self.metadata(
                song
            )
        )

        return self._text(
            metadata.get(
                "playback_mode",
                ""
            )
        ).lower()

    # ========================================================
    # SONG SAYS FULL PLAYBACK
    # ========================================================

    @staticmethod
    def has_full_playback_flag(
        song
    ) -> bool:

        if song is None:

            return False

        # ----------------------------------------------------
        # Unified Song helper.
        # ----------------------------------------------------

        try:

            if hasattr(
                song,
                "has_full_playback"
            ):

                return bool(
                    song.has_full_playback()
                )

        except Exception:

            pass

        # ----------------------------------------------------
        # Dataclass / attribute fallback.
        # ----------------------------------------------------

        return bool(
            getattr(
                song,
                "full_playback",
                False
            )
        )

    # ========================================================
    # SONG SAYS PREVIEW
    # ========================================================

    def has_preview(
        self,
        song
    ) -> bool:

        if song is None:

            return False

        preview_url = (
            self.preview_url(
                song
            )
        )

        if preview_url:

            return True

        return bool(
            getattr(
                song,
                "preview_available",
                False
            )
        )

    # ========================================================
    # REMOTE PLAYBACK
    # ========================================================

    def is_remote_playback(
        self,
        song
    ) -> bool:

        if song is None:

            return False

        # ----------------------------------------------------
        # Registry helper.
        # ----------------------------------------------------

        try:

            if self.registry.song_uses_remote_playback(
                song
            ):

                return True

        except Exception:

            pass

        # ----------------------------------------------------
        # Metadata compatibility.
        # ----------------------------------------------------

        mode = (
            self.metadata_playback_mode(
                song
            )
        )

        if mode in {
            "spotify_remote",
            "remote",
            "provider_remote",
        }:

            return True

        # ----------------------------------------------------
        # Spotify.
        # ----------------------------------------------------

        if (
            self.provider_name(
                song
            )
            ==
            "spotify"
        ):

            return True

        return False

    # ========================================================
    # DIRECT URL IS LIKELY FULL TRACK
    # ========================================================

    def direct_url_is_full(
        self,
        song
    ) -> bool:

        if song is None:

            return False

        url = (
            self.audio_url(
                song
            )
        )

        if not url:

            return False

        provider = (
            self.provider_name(
                song
            )
        )

        # ====================================================
        # iTunes
        # ====================================================
        #
        # In our architecture iTunes audio is preview-only.
        # Even if old compatibility code copied preview_url
        # into audio_url, DO NOT call it a full track.
        # ====================================================

        if provider == "itunes":

            return False

        # ====================================================
        # EXPLICIT FULL FLAG
        # ====================================================

        if self.has_full_playback_flag(
            song
        ):

            return True

        # ====================================================
        # JAMENDO COMPATIBILITY
        # ====================================================
        #
        # Existing Jamendo Song models may not yet correctly
        # expose full_playback=True, but their audio endpoint
        # can be a direct playable provider stream.
        # ====================================================

        if provider == "jamendo":

            preview = (
                self.preview_url(
                    song
                )
            )

            # If audio URL is distinct from preview, treat as
            # direct provider playback.
            if (
                url
                and
                (
                    not preview
                    or
                    url != preview
                )
            ):

                return True

        # ====================================================
        # FUTURE DIRECT PROVIDERS
        # ====================================================

        metadata = (
            self.metadata(
                song
            )
        )

        if bool(
            metadata.get(
                "full_track",
                False
            )
        ):

            return True

        if (
            self._text(
                metadata.get(
                    "playback_mode",
                    ""
                )
            ).lower()
            ==
            "direct_full"
        ):

            return True

        return False

    # ========================================================
    # DIRECT FULL RESOLUTION
    # ========================================================

    def _resolve_direct(
        self,
        song,
        original_song=None,
        used_alternative=False,
    ) -> Optional[PlaybackResolution]:

        if song is None:

            return None

        url = (
            self.audio_url(
                song
            )
        )

        if not url:

            return None

        if not self.direct_url_is_full(
            song
        ):

            return None

        return PlaybackResolution(

            success=True,

            mode=PLAYBACK_DIRECT,

            song=song,

            provider=self.provider_name(
                song
            ),

            audio_url=url,

            message=(
                "Full direct stream resolved."
            ),

            is_full_track=True,

            is_preview=False,

            used_alternative=(
                used_alternative
            ),

            original_song=(
                original_song
            ),
        )

    # ========================================================
    # REMOTE FULL RESOLUTION
    # ========================================================

    def _resolve_remote(
        self,
        song,
        original_song=None,
        used_alternative=False,
    ) -> Optional[PlaybackResolution]:

        if song is None:

            return None

        if not self.is_remote_playback(
            song
        ):

            return None

        provider = (
            self.provider_name(
                song
            )
        )

        # ====================================================
        # SPOTIFY
        # ====================================================

        if provider == "spotify":

            try:

                if not self.registry.spotify_authenticated():

                    return None

            except Exception:

                return None

        return PlaybackResolution(

            success=True,

            mode=PLAYBACK_REMOTE,

            song=song,

            provider=provider,

            audio_url="",

            message=(
                "Full remote provider playback resolved."
            ),

            is_full_track=True,

            is_preview=False,

            used_alternative=(
                used_alternative
            ),

            original_song=(
                original_song
            ),
        )

    # ========================================================
    # FIND ALTERNATIVE
    # ========================================================

    def find_alternative(
        self,
        song
    ):

        if song is None:

            return None

        try:

            alternative = (
                self.registry
                .find_full_playback_alternative(
                    song
                )
            )

        except Exception as error:

            print(
                "FullTrackResolver alternative error:",
                error
            )

            return None

        if alternative is None:

            return None

        # ----------------------------------------------------
        # Prevent accidental same-object loop.
        # ----------------------------------------------------

        if alternative is song:

            return alternative

        return alternative

    # ========================================================
    # RESOLVE
    # ========================================================

    def resolve(
        self,
        song,
        allow_preview: bool = False,
        search_alternative: bool = True,
    ) -> PlaybackResolution:

        """
        Resolve a Song to the best playback method.

        Day 21 default:

            allow_preview=False

        because LYRx target is full songs rather than iTunes
        30-second previews.
        """

        # ====================================================
        # EMPTY
        # ====================================================

        if song is None:

            return PlaybackResolution(

                success=False,

                mode=PLAYBACK_NONE,

                song=None,

                message=(
                    "No song was supplied."
                ),
            )

        title = (
            self.song_title(
                song
            )
        )

        artist = (
            self.song_artist(
                song
            )
        )

        provider = (
            self.provider_name(
                song
            )
        )

        # ====================================================
        # DEBUG
        # ====================================================

        print()
        print("=" * 60)

        print(
            "LYRx FULL TRACK RESOLVER"
        )

        print(
            "Title:",
            title
        )

        print(
            "Artist:",
            artist
        )

        print(
            "Provider:",
            (
                provider
                or
                "unknown"
            )
        )

        # ====================================================
        # 1. REMOTE FULL
        # ====================================================

        remote = (
            self._resolve_remote(
                song
            )
        )

        if remote is not None:

            print(
                "Resolved:",
                "REMOTE FULL PLAYBACK"
            )

            print("=" * 60)
            print()

            return remote

        # ====================================================
        # 2. DIRECT FULL
        # ====================================================

        direct = (
            self._resolve_direct(
                song
            )
        )

        if direct is not None:

            print(
                "Resolved:",
                "DIRECT FULL STREAM"
            )

            print("=" * 60)
            print()

            return direct

        # ====================================================
        # 3. SEARCH FULL ALTERNATIVE
        # ====================================================

        if search_alternative:

            alternative = (
                self.find_alternative(
                    song
                )
            )

            if (
                alternative is not None
                and
                alternative is not song
            ):

                # --------------------------------------------
                # REMOTE ALTERNATIVE
                # --------------------------------------------

                remote_alt = (
                    self._resolve_remote(

                        alternative,

                        original_song=song,

                        used_alternative=True,
                    )
                )

                if remote_alt is not None:

                    print(
                        "Resolved:",
                        "REMOTE FULL ALTERNATIVE"
                    )

                    print(
                        "Alternative:",
                        self.song_title(
                            alternative
                        ),
                        "-",
                        self.song_artist(
                            alternative
                        )
                    )

                    print("=" * 60)
                    print()

                    return remote_alt

                # --------------------------------------------
                # DIRECT ALTERNATIVE
                # --------------------------------------------

                direct_alt = (
                    self._resolve_direct(

                        alternative,

                        original_song=song,

                        used_alternative=True,
                    )
                )

                if direct_alt is not None:

                    print(
                        "Resolved:",
                        "DIRECT FULL ALTERNATIVE"
                    )

                    print(
                        "Alternative:",
                        self.song_title(
                            alternative
                        ),
                        "-",
                        self.song_artist(
                            alternative
                        )
                    )

                    print("=" * 60)
                    print()

                    return direct_alt

        # ====================================================
        # 4. PREVIEW
        # ====================================================

        preview_url = (
            self.preview_url(
                song
            )
        )

        # ----------------------------------------------------
        # Old Day 20 compatibility may have copied the iTunes
        # preview into audio_url.
        # ----------------------------------------------------

        if (
            not preview_url
            and
            provider == "itunes"
        ):

            preview_url = (
                self.audio_url(
                    song
                )
            )

        if preview_url:

            if allow_preview:

                print(
                    "Resolved:",
                    "PREVIEW ONLY"
                )

                print("=" * 60)
                print()

                return PlaybackResolution(

                    success=True,

                    mode=PLAYBACK_PREVIEW,

                    song=song,

                    provider=provider,

                    audio_url=preview_url,

                    message=(
                        "Only a preview is available."
                    ),

                    is_full_track=False,

                    is_preview=True,

                    used_alternative=False,

                    original_song=None,
                )

            print(
                "Rejected:",
                "PREVIEW ONLY"
            )

            print("=" * 60)
            print()

            return PlaybackResolution(

                success=False,

                mode=PLAYBACK_PREVIEW,

                song=song,

                provider=provider,

                audio_url=preview_url,

                message=(
                    "Only a preview is available. "
                    "LYRx full-track mode rejected it."
                ),

                is_full_track=False,

                is_preview=True,
            )

        # ====================================================
        # NOTHING
        # ====================================================

        print(
            "Resolved:",
            "NO FULL TRACK SOURCE"
        )

        print("=" * 60)
        print()

        return PlaybackResolution(

            success=False,

            mode=PLAYBACK_NONE,

            song=song,

            provider=provider,

            audio_url="",

            message=(
                "No authorized full-track playback source "
                "is currently available for this song."
            ),

            is_full_track=False,

            is_preview=False,
        )

    # ========================================================
    # PLAY
    # ========================================================

    def play(
        self,
        song,
        allow_preview: bool = False,
    ) -> PlaybackResolution:

        """
        Resolve + initiate REMOTE provider playback when needed.

        Direct playback is intentionally returned to AppWindow /
        NowPlaying because Qt QMediaPlayer owns direct streams.
        """

        result = self.resolve(

            song,

            allow_preview=allow_preview,

            search_alternative=True,
        )

        if not result.success:

            return result

        # ====================================================
        # REMOTE
        # ====================================================

        if (
            result.mode
            ==
            PLAYBACK_REMOTE
        ):

            try:

                started = (
                    self.registry.play_song(
                        result.song
                    )
                )

            except Exception as error:

                started = False

                result.message = (
                    f"Remote playback error: {error}"
                )

            if not started:

                result.success = False

                if not result.message:

                    result.message = (
                        "Remote provider could not start playback."
                    )

        # ====================================================
        # DIRECT
        # ====================================================
        #
        # Caller should send:
        #
        #     result.audio_url
        #
        # to NowPlaying / QMediaPlayer.
        # ====================================================

        return result

    # ========================================================
    # DEBUG
    # ========================================================

    def print_song_capabilities(
        self,
        song
    ):

        print()
        print("=" * 60)

        print(
            "LYRx SONG PLAYBACK CAPABILITIES"
        )

        print("=" * 60)

        print(
            "Title:",
            self.song_title(
                song
            )
        )

        print(
            "Artist:",
            self.song_artist(
                song
            )
        )

        print(
            "Provider:",
            self.provider_name(
                song
            )
        )

        print(
            "Audio URL:",
            bool(
                self.audio_url(
                    song
                )
            )
        )

        print(
            "Preview URL:",
            bool(
                self.preview_url(
                    song
                )
            )
        )

        print(
            "Full flag:",
            self.has_full_playback_flag(
                song
            )
        )

        print(
            "Direct full:",
            self.direct_url_is_full(
                song
            )
        )

        print(
            "Remote:",
            self.is_remote_playback(
                song
            )
        )

        print("=" * 60)
        print()


# ============================================================
# SHARED INSTANCE
# ============================================================

full_track_resolver = (
    FullTrackResolver()
)