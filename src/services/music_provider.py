# ============================================================
# LYRx
# DAY 20 - FINAL TASK
# MULTI-PROVIDER ARCHITECTURE
#
# FILE 1
# music_provider.py
#
# PURPOSE:
#   Unified Song model
#   Unified provider interface
#   Unified search result
#   Provider capability system
#
# IMPORTANT:
#   This file is intentionally backward-compatible with
#   Day 19 playback and Day 20 provider architecture.
# ============================================================

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
    Dict,
    List,
    Optional,
)


# ============================================================
# SONG MODEL
# ============================================================

@dataclass
class Song:

    """
    Unified LYRx song model.

    Every music source should eventually convert its native
    response into this Song object.

    UI/player modules should not care whether a track came from:

        - Jamendo
        - Apple Music
        - another legal provider
        - local cache
        - user library
        - recommendations
        - search
        - playlists

    ------------------------------------------------------------
    IMPORTANT
    ------------------------------------------------------------

    The model keeps compatibility with older LYRx code.

    Old code may use:

        song.source
        song.display_title()
        song.display_artist()
        song.duration_text()

    New provider code may use:

        song.provider
        song.id
        song.audio_url
        song.preview_url

    BOTH are supported.
    """

    # ========================================================
    # CORE IDENTITY
    # ========================================================

    id: str = ""

    title: str = ""

    artist: str = ""

    album: str = ""

    # ========================================================
    # ARTWORK
    # ========================================================

    image_url: str = ""

    # ========================================================
    # AUDIO
    # ========================================================
    #
    # audio_url:
    #     Main playable stream when provider permits it.
    #
    # preview_url:
    #     Preview stream when provider only exposes previews.
    #

    audio_url: str = ""

    preview_url: str = ""

    # ========================================================
    # DURATION
    # ========================================================
    #
    # Stored in SECONDS.
    #

    duration: int = 0

    # ========================================================
    # PROVIDER
    # ========================================================

    provider: str = "online"

    # ========================================================
    # DOWNLOAD
    # ========================================================

    downloadable: bool = False

    download_url: str = ""

    # ========================================================
    # EXTERNAL LINKS
    # ========================================================

    share_url: str = ""

    external_url: str = ""

    # ========================================================
    # MUSIC INFORMATION
    # ========================================================

    genre: str = ""

    language: str = ""

    release_date: str = ""

    explicit: bool = False

    # ========================================================
    # PLAYBACK CAPABILITIES
    # ========================================================

    full_playback: bool = False

    preview_available: bool = False

    # ========================================================
    # PROVIDER METADATA
    # ========================================================
    #
    # Useful for provider-specific fields that LYRx does not
    # need as first-class Song attributes yet.
    #

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ========================================================
    # DISPLAY TITLE
    # ========================================================

    def display_title(
        self
    ) -> str:

        title = str(
            self.title
            or ""
        ).strip()

        if title:

            return title

        return "Unknown Track"

    # ========================================================
    # DISPLAY ARTIST
    # ========================================================

    def display_artist(
        self
    ) -> str:

        artist = str(
            self.artist
            or ""
        ).strip()

        if artist:

            return artist

        return "Unknown Artist"

    # ========================================================
    # DISPLAY ALBUM
    # ========================================================

    def display_album(
        self
    ) -> str:

        album = str(
            self.album
            or ""
        ).strip()

        if album:

            return album

        return "Unknown Album"

    # ========================================================
    # DURATION TEXT
    # ========================================================

    def duration_text(
        self
    ) -> str:

        try:

            duration = int(
                self.duration
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            duration = 0

        if duration <= 0:

            return "0:00"

        minutes = (
            duration // 60
        )

        seconds = (
            duration % 60
        )

        return (
            f"{minutes}:"
            f"{seconds:02d}"
        )

    # ========================================================
    # OLD SOURCE COMPATIBILITY
    # ========================================================
    #
    # Day 19 code used:
    #
    #     song.source
    #
    # Day 20 multi-provider architecture uses:
    #
    #     song.provider
    #
    # Keep both working.
    #

    @property
    def source(
        self
    ) -> str:

        provider = str(
            self.provider
            or ""
        ).strip()

        if provider:

            return provider

        return "online"

    # ========================================================
    # PLAYABLE AUDIO URL
    # ========================================================

    def playable_url(
        self
    ) -> str:

        """
        Returns the best currently usable audio URL.

        Priority:

            1. Full audio stream
            2. Preview stream
        """

        audio = str(
            self.audio_url
            or ""
        ).strip()

        if audio:

            return audio

        preview = str(
            self.preview_url
            or ""
        ).strip()

        if preview:

            return preview

        return ""

    # ========================================================
    # IS PLAYABLE
    # ========================================================

    def is_playable(
        self
    ) -> bool:

        return bool(
            self.playable_url()
        )

    # ========================================================
    # HAS FULL PLAYBACK
    # ========================================================

    def has_full_playback(
        self
    ) -> bool:

        if self.full_playback:

            return bool(
                str(
                    self.audio_url
                    or ""
                ).strip()
            )

        # ----------------------------------------------------
        # Backward compatibility:
        #
        # Older Jamendo Song objects may not explicitly set
        # full_playback but do contain audio_url.
        # ----------------------------------------------------

        if (
            self.audio_url
            and
            not self.preview_url
        ):

            return True

        return False

    # ========================================================
    # HAS PREVIEW
    # ========================================================

    def has_preview(
        self
    ) -> bool:

        if self.preview_available:

            return bool(
                str(
                    self.preview_url
                    or ""
                ).strip()
            )

        return bool(
            str(
                self.preview_url
                or ""
            ).strip()
        )

    # ========================================================
    # UNIQUE KEY
    # ========================================================

    def unique_key(
        self
    ):

        provider = str(
            self.provider
            or ""
        ).strip().lower()

        song_id = str(
            self.id
            or ""
        ).strip().lower()

        if song_id:

            return (
                provider,
                song_id,
            )

        return (
            self.display_title()
            .strip()
            .lower(),

            self.display_artist()
            .strip()
            .lower(),
        )

    # ========================================================
    # DICTIONARY
    # ========================================================

    def to_dict(
        self
    ) -> Dict[str, Any]:

        return {

            "id":
                self.id,

            "title":
                self.title,

            "artist":
                self.artist,

            "album":
                self.album,

            "image_url":
                self.image_url,

            "audio_url":
                self.audio_url,

            "preview_url":
                self.preview_url,

            "duration":
                self.duration,

            "provider":
                self.provider,

            # ------------------------------------------------
            # Keep old serialized key too.
            # ------------------------------------------------

            "source":
                self.source,

            "downloadable":
                self.downloadable,

            "download_url":
                self.download_url,

            "share_url":
                self.share_url,

            "external_url":
                self.external_url,

            "genre":
                self.genre,

            "language":
                self.language,

            "release_date":
                self.release_date,

            "explicit":
                self.explicit,

            "full_playback":
                self.full_playback,

            "preview_available":
                self.preview_available,

            "metadata":
                dict(
                    self.metadata
                    or {}
                ),
        }

    # ========================================================
    # FROM DICTIONARY
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data
    ) -> "Song":

        if not isinstance(
            data,
            dict
        ):

            data = {}

        # ====================================================
        # PROVIDER / SOURCE
        # ====================================================

        provider = str(

            data.get(
                "provider",
                ""
            )

            or

            data.get(
                "source",
                ""
            )

            or

            "online"

        ).strip()

        # ====================================================
        # DURATION
        # ====================================================

        try:

            duration = int(
                data.get(
                    "duration",
                    0
                )
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            duration = 0

        # ====================================================
        # METADATA
        # ====================================================

        metadata = data.get(
            "metadata",
            {}
        )

        if not isinstance(
            metadata,
            dict
        ):

            metadata = {}

        # ====================================================
        # CREATE
        # ====================================================

        return cls(

            id=str(
                data.get(
                    "id",
                    ""
                )
                or ""
            ),

            title=str(
                data.get(
                    "title",
                    ""
                )
                or ""
            ),

            artist=str(
                data.get(
                    "artist",
                    ""
                )
                or ""
            ),

            album=str(
                data.get(
                    "album",
                    ""
                )
                or ""
            ),

            image_url=str(
                data.get(
                    "image_url",
                    ""
                )
                or ""
            ),

            audio_url=str(
                data.get(
                    "audio_url",
                    ""
                )
                or ""
            ),

            preview_url=str(
                data.get(
                    "preview_url",
                    ""
                )
                or ""
            ),

            duration=duration,

            provider=provider,

            downloadable=bool(
                data.get(
                    "downloadable",
                    False
                )
            ),

            download_url=str(
                data.get(
                    "download_url",
                    ""
                )
                or ""
            ),

            share_url=str(
                data.get(
                    "share_url",
                    ""
                )
                or ""
            ),

            external_url=str(
                data.get(
                    "external_url",
                    ""
                )
                or ""
            ),

            genre=str(
                data.get(
                    "genre",
                    ""
                )
                or ""
            ),

            language=str(
                data.get(
                    "language",
                    ""
                )
                or ""
            ),

            release_date=str(
                data.get(
                    "release_date",
                    ""
                )
                or ""
            ),

            explicit=bool(
                data.get(
                    "explicit",
                    False
                )
            ),

            full_playback=bool(
                data.get(
                    "full_playback",
                    False
                )
            ),

            preview_available=bool(
                data.get(
                    "preview_available",
                    False
                )
            ),

            metadata=dict(
                metadata
            ),
        )

    # ========================================================
    # STRING
    # ========================================================

    def __str__(
        self
    ) -> str:

        return (
            f"{self.display_title()} "
            f"— "
            f"{self.display_artist()}"
        )


# ============================================================
# SEARCH RESULT
# ============================================================

@dataclass
class MusicSearchResult:

    """
    Standard result returned by providers and ProviderRegistry.
    """

    query: str = ""

    songs: List[Song] = field(
        default_factory=list
    )

    total: int = 0

    provider: str = ""

    error: str = ""

    # ========================================================
    # SUCCESS
    # ========================================================

    @property
    def success(
        self
    ) -> bool:

        return (
            not self.error
        )

    # ========================================================
    # HAS RESULTS
    # ========================================================

    def has_results(
        self
    ) -> bool:

        return bool(
            self.songs
        )

    # ========================================================
    # NORMALIZE TOTAL
    # ========================================================

    def normalize(
        self
    ) -> "MusicSearchResult":

        self.songs = list(
            self.songs
            or []
        )

        self.total = len(
            self.songs
        )

        return self


# ============================================================
# MUSIC PROVIDER
# ============================================================

class MusicProvider:

    """
    Base class / interface for every LYRx music provider.

    A provider may support only some capabilities.

    Example:

        Jamendo:
            search              YES
            full playback       YES
            previews            maybe
            mainstream catalog  limited

        Future catalog provider:
            search              YES
            full playback       depends on API/license
            previews            YES
            charts              YES

    ProviderRegistry can inspect these capabilities without
    hard-coding provider names.
    """

    # ========================================================
    # PROVIDER IDENTITY
    # ========================================================

    provider_name = (
        "base"
    )

    display_name = (
        "Music Provider"
    )

    # ========================================================
    # STATE
    # ========================================================

    enabled = True

    # ========================================================
    # CAPABILITIES
    # ========================================================

    supports_search = False

    supports_trending = False

    supports_popular = False

    supports_genres = False

    supports_moods = False

    supports_hindi = False

    supports_english = False

    supports_artist_search = False

    supports_song_search = False

    supports_charts = False

    supports_full_playback = False

    supports_preview = False

    supports_download = False

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self
    ):

        self.enabled = bool(
            getattr(
                self,
                "enabled",
                True
            )
        )

        self.last_error = ""

    # ========================================================
    # AVAILABLE
    # ========================================================

    def is_available(
        self
    ) -> bool:

        """
        Providers can override this.

        Example:
            Jamendo checks client ID.
            Apple may check token/configuration.
        """

        return bool(
            self.enabled
        )

    # ========================================================
    # CAPABILITY CHECK
    # ========================================================

    def supports(
        self,
        capability: str
    ) -> bool:

        capability = str(
            capability
            or ""
        ).strip().lower()

        if not capability:

            return False

        aliases = {

            "search":
                "supports_search",

            "trending":
                "supports_trending",

            "popular":
                "supports_popular",

            "genre":
                "supports_genres",

            "genres":
                "supports_genres",

            "mood":
                "supports_moods",

            "moods":
                "supports_moods",

            "hindi":
                "supports_hindi",

            "english":
                "supports_english",

            "artist":
                "supports_artist_search",

            "artist_search":
                "supports_artist_search",

            "song":
                "supports_song_search",

            "song_search":
                "supports_song_search",

            "charts":
                "supports_charts",

            "full_playback":
                "supports_full_playback",

            "preview":
                "supports_preview",

            "download":
                "supports_download",
        }

        attribute = aliases.get(
            capability,
            capability
        )

        return bool(
            getattr(
                self,
                attribute,
                False
            )
        )

    # ========================================================
    # CAPABILITY DICTIONARY
    # ========================================================

    def capabilities(
        self
    ) -> Dict[str, bool]:

        return {

            "search":
                bool(
                    self.supports_search
                ),

            "trending":
                bool(
                    self.supports_trending
                ),

            "popular":
                bool(
                    self.supports_popular
                ),

            "genres":
                bool(
                    self.supports_genres
                ),

            "moods":
                bool(
                    self.supports_moods
                ),

            "hindi":
                bool(
                    self.supports_hindi
                ),

            "english":
                bool(
                    self.supports_english
                ),

            "artist_search":
                bool(
                    self.supports_artist_search
                ),

            "song_search":
                bool(
                    self.supports_song_search
                ),

            "charts":
                bool(
                    self.supports_charts
                ),

            "full_playback":
                bool(
                    self.supports_full_playback
                ),

            "preview":
                bool(
                    self.supports_preview
                ),

            "download":
                bool(
                    self.supports_download
                ),
        }

    # ========================================================
    # NORMALIZE LIMIT
    # ========================================================

    @staticmethod
    def normalize_limit(
        limit,
        maximum=50
    ) -> int:

        try:

            value = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            value = 20

        return max(
            1,
            min(
                value,
                maximum
            )
        )

    # ========================================================
    # ERROR
    # ========================================================

    def set_error(
        self,
        error
    ):

        self.last_error = str(
            error
            or ""
        )

    # ========================================================
    # CLEAR ERROR
    # ========================================================

    def clear_error(
        self
    ):

        self.last_error = ""

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        limit: int = 20,
    ) -> MusicSearchResult:

        return MusicSearchResult(

            query=str(
                query
                or ""
            ),

            songs=[],

            total=0,

            provider=self.provider_name,

            error=(
                f"{self.display_name} "
                f"does not support search."
            ),
        )

    # ========================================================
    # TRENDING
    # ========================================================

    def get_trending(
        self,
        limit: int = 20,
    ) -> List[Song]:

        return []

    # ========================================================
    # POPULAR
    # ========================================================

    def get_popular(
        self,
        limit: int = 20,
    ) -> List[Song]:

        # ----------------------------------------------------
        # Safe fallback for older providers that only
        # implemented trending.
        # ----------------------------------------------------

        try:

            return list(
                self.get_trending(
                    limit
                )
                or []
            )

        except Exception:

            return []

    # ========================================================
    # GENRE
    # ========================================================

    def get_by_genre(
        self,
        genre: str,
        limit: int = 20,
    ) -> List[Song]:

        result = self.search(
            genre,
            limit
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # MOOD
    # ========================================================

    def get_by_mood(
        self,
        mood: str,
        limit: int = 20,
    ) -> List[Song]:

        result = self.search(
            mood,
            limit
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # HINDI
    # ========================================================

    def get_hindi(
        self,
        limit: int = 20,
    ) -> List[Song]:

        result = self.search(
            "Hindi",
            limit
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # ENGLISH
    # ========================================================

    def get_english(
        self,
        limit: int = 20,
    ) -> List[Song]:

        result = self.search(
            "English",
            limit
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # ARTIST SEARCH
    # ========================================================

    def search_artist(
        self,
        artist: str,
        limit: int = 20,
    ) -> List[Song]:

        result = self.search(
            artist,
            limit
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # SONG SEARCH
    # ========================================================

    def search_song(
        self,
        title: str,
        limit: int = 20,
    ) -> List[Song]:

        result = self.search(
            title,
            limit
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # STATUS
    # ========================================================

    def status(
        self
    ) -> Dict[str, Any]:

        try:

            available = (
                self.is_available()
            )

        except Exception:

            available = False

        return {

            "provider":
                self.provider_name,

            "display_name":
                self.display_name,

            "available":
                bool(
                    available
                ),

            "enabled":
                bool(
                    self.enabled
                ),

            "last_error":
                str(
                    self.last_error
                    or ""
                ),

            "capabilities":
                self.capabilities(),
        }

    # ========================================================
    # STRING
    # ========================================================

    def __str__(
        self
    ) -> str:

        return str(
            self.display_name
            or self.provider_name
        )