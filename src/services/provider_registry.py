# ============================================================
# LYRx
# DAY 20 - FINAL TASK
# MULTI-PROVIDER ARCHITECTURE
#
# FILE 3
# provider_registry.py
#
# PURPOSE:
#   Central manager for all LYRx music providers.
#
# CURRENT PROVIDERS:
#
#   1. ITunesProvider
#      - mainstream catalog
#      - Hindi / Bollywood / English
#      - previews when available
#
#   2. JamendoProvider
#      - full playable independent catalog
#
# IMPORTANT:
#   UI should eventually talk only to ProviderRegistry.
# ============================================================

from __future__ import annotations

from typing import (
    Dict,
    List,
    Optional,
)

from services.music_provider import (
    MusicProvider,
    MusicSearchResult,
    Song,
)

from services.jamendo_provider import (
    JamendoProvider,
)

from services.itunes_provider import (
    ITunesProvider,
)


# ============================================================
# PROVIDER REGISTRY
# ============================================================

class ProviderRegistry:

    """
    Central music-provider manager for LYRx.

    ------------------------------------------------------------
    ARCHITECTURE
    ------------------------------------------------------------

        Home / Discover / AI / Search
                    │
                    ▼
            ProviderRegistry
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    ITunesProvider      JamendoProvider

    ------------------------------------------------------------
    GOAL
    ------------------------------------------------------------

    UI/player modules should not need provider-specific logic.

    They request:

        search()
        get_trending()
        get_popular()
        get_hindi()
        get_english()
        get_by_genre()
        get_by_mood()

    Registry handles provider priority and fallback.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self
    ):

        # ----------------------------------------------------
        # PROVIDER MAP
        # ----------------------------------------------------

        self.providers: Dict[
            str,
            MusicProvider
        ] = {}

        # ----------------------------------------------------
        # GENERAL PRIORITY
        # ----------------------------------------------------
        #
        # Mainstream catalog first.
        #
        # Jamendo remains fallback for full playable tracks.
        #

        self.provider_priority: List[str] = []

        # ----------------------------------------------------
        # DEFAULT
        # ----------------------------------------------------

        self.default_provider_name = ""

        # ----------------------------------------------------
        # BUILT-IN PROVIDERS
        # ----------------------------------------------------

        self._register_default_providers()

    # ========================================================
    # DEFAULT PROVIDERS
    # ========================================================

    def _register_default_providers(
        self
    ):

        # ====================================================
        # ITUNES FIRST
        # ====================================================
        #
        # Mainstream catalog:
        #
        #   Arijit Singh
        #   Bollywood
        #   Hindi
        #   English
        #   global artists
        #
        # Playback may be preview-only.
        # ====================================================

        try:

            itunes = ITunesProvider()

            self.register(
                itunes,
                make_default=True,
            )

        except Exception as error:

            print(
                "ProviderRegistry iTunes init error:",
                error
            )

        # ====================================================
        # JAMENDO SECOND
        # ====================================================
        #
        # Full playable independent catalog.
        # ====================================================

        try:

            jamendo = JamendoProvider()

            self.register(
                jamendo,
                make_default=False,
            )

        except Exception as error:

            print(
                "ProviderRegistry Jamendo init error:",
                error
            )

    # ========================================================
    # REGISTER
    # ========================================================

    def register(
        self,
        provider: MusicProvider,
        make_default: bool = False,
    ):

        if provider is None:

            return

        provider_name = str(
            getattr(
                provider,
                "provider_name",
                ""
            )
            or ""
        ).strip().lower()

        if not provider_name:

            raise ValueError(
                "Music provider must define provider_name."
            )

        self.providers[
            provider_name
        ] = provider

        if (
            provider_name
            not in self.provider_priority
        ):

            self.provider_priority.append(
                provider_name
            )

        if (
            make_default
            or
            not self.default_provider_name
        ):

            self.default_provider_name = (
                provider_name
            )

        print(
            "LYRx provider registered:",
            provider_name
        )

    # ========================================================
    # UNREGISTER
    # ========================================================

    def unregister(
        self,
        provider_name: str,
    ):

        provider_name = str(
            provider_name
            or ""
        ).strip().lower()

        if not provider_name:

            return

        self.providers.pop(
            provider_name,
            None
        )

        if (
            provider_name
            in self.provider_priority
        ):

            self.provider_priority.remove(
                provider_name
            )

        if (
            self.default_provider_name
            == provider_name
        ):

            if self.provider_priority:

                self.default_provider_name = (
                    self.provider_priority[0]
                )

            else:

                self.default_provider_name = ""

    # ========================================================
    # GET PROVIDER
    # ========================================================

    def get_provider(
        self,
        provider_name: str,
    ) -> Optional[MusicProvider]:

        provider_name = str(
            provider_name
            or ""
        ).strip().lower()

        if not provider_name:

            return None

        return self.providers.get(
            provider_name
        )

    # ========================================================
    # DEFAULT PROVIDER
    # ========================================================

    def get_default_provider(
        self
    ) -> Optional[MusicProvider]:

        if not self.default_provider_name:

            return None

        return self.get_provider(
            self.default_provider_name
        )

    # ========================================================
    # SET DEFAULT
    # ========================================================

    def set_default_provider(
        self,
        provider_name: str,
    ) -> bool:

        provider_name = str(
            provider_name
            or ""
        ).strip().lower()

        if (
            provider_name
            not in self.providers
        ):

            return False

        self.default_provider_name = (
            provider_name
        )

        return True

    # ========================================================
    # PROVIDER NAMES
    # ========================================================

    def provider_names(
        self
    ) -> List[str]:

        return list(
            self.provider_priority
        )

    # ========================================================
    # AVAILABLE PROVIDERS
    # ========================================================

    def available_providers(
        self
    ) -> List[MusicProvider]:

        available = []

        for provider_name in (
            self.provider_priority
        ):

            provider = self.providers.get(
                provider_name
            )

            if provider is None:

                continue

            try:

                if provider.is_available():

                    available.append(
                        provider
                    )

            except Exception as error:

                print(
                    "Provider availability error:",
                    provider_name,
                    error
                )

        return available

    # ========================================================
    # HAS AVAILABLE PROVIDER
    # ========================================================

    def has_available_provider(
        self,
    ) -> bool:

        return bool(
            self.available_providers()
        )

    # ========================================================
    # PLAYABLE PROVIDERS
    # ========================================================

    def playable_providers(
        self
    ) -> List[MusicProvider]:

        result = []

        for provider in (
            self.available_providers()
        ):

            try:

                if (
                    getattr(
                        provider,
                        "supports_full_playback",
                        False
                    )
                    or
                    getattr(
                        provider,
                        "supports_preview",
                        False
                    )
                ):

                    result.append(
                        provider
                    )

            except Exception:

                continue

        return result

    # ========================================================
    # FULL PLAYBACK PROVIDERS
    # ========================================================

    def full_playback_providers(
        self
    ) -> List[MusicProvider]:

        result = []

        for provider in (
            self.available_providers()
        ):

            if bool(
                getattr(
                    provider,
                    "supports_full_playback",
                    False
                )
            ):

                result.append(
                    provider
                )

        return result

    # ========================================================
    # NORMALIZE LIMIT
    # ========================================================

    @staticmethod
    def _normalize_limit(
        limit,
        maximum=50,
    ) -> int:

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            limit = 20

        return max(
            1,
            min(
                limit,
                maximum
            )
        )

    # ========================================================
    # SONG KEY
    # ========================================================

    @staticmethod
    def _song_key(
        song: Song,
    ):

        if song is None:

            return (
                "",
                "",
            )

        # ----------------------------------------------------
        # Prefer Song's own unified key.
        # ----------------------------------------------------

        try:

            if hasattr(
                song,
                "unique_key"
            ):

                return song.unique_key()

        except Exception:

            pass

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        provider = str(

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

            or

            ""

        ).strip().lower()

        song_id = str(
            getattr(
                song,
                "id",
                ""
            )
            or ""
        ).strip().lower()

        if song_id:

            return (
                provider,
                song_id,
            )

        title = str(
            getattr(
                song,
                "title",
                ""
            )
            or ""
        ).strip().lower()

        artist = str(
            getattr(
                song,
                "artist",
                ""
            )
            or ""
        ).strip().lower()

        return (
            title,
            artist,
        )

    # ========================================================
    # DEDUPLICATE
    # ========================================================

    def _deduplicate(
        self,
        songs,
        limit=None,
    ) -> List[Song]:

        result = []

        seen = set()

        for song in (
            songs
            or []
        ):

            if song is None:

                continue

            key = self._song_key(
                song
            )

            if key in seen:

                continue

            seen.add(
                key
            )

            result.append(
                song
            )

            if (
                limit is not None
                and
                len(result) >= limit
            ):

                break

        return result

    # ========================================================
    # SORT SEARCH RESULTS
    # ========================================================

    @staticmethod
    def _search_score(
        song: Song,
        query: str,
    ):

        query = str(
            query
            or ""
        ).strip().lower()

        title = str(
            getattr(
                song,
                "title",
                ""
            )
            or ""
        ).strip().lower()

        artist = str(
            getattr(
                song,
                "artist",
                ""
            )
            or ""
        ).strip().lower()

        provider = str(

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

            or

            ""

        ).strip().lower()

        score = 100

        # ----------------------------------------------------
        # EXACT TITLE
        # ----------------------------------------------------

        if title == query:

            score -= 50

        elif query in title:

            score -= 35

        # ----------------------------------------------------
        # ARTIST
        # ----------------------------------------------------

        if artist == query:

            score -= 40

        elif query in artist:

            score -= 25

        # ----------------------------------------------------
        # MAINSTREAM PROVIDER PRIORITY
        # ----------------------------------------------------

        if provider == "itunes":

            score -= 8

        # ----------------------------------------------------
        # FULL PLAYBACK BONUS
        # ----------------------------------------------------

        try:

            if song.has_full_playback():

                score -= 3

        except Exception:

            pass

        return score

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        limit: int = 20,
        provider_name: str | None = None,
    ) -> MusicSearchResult:

        query = str(
            query
            or ""
        ).strip()

        limit = self._normalize_limit(
            limit
        )

        if not query:

            return MusicSearchResult(

                query="",

                songs=[],

                total=0,

                provider="",

                error="Empty search query.",
            )

        # ====================================================
        # SPECIFIC PROVIDER
        # ====================================================

        if provider_name:

            provider = self.get_provider(
                provider_name
            )

            if provider is None:

                return MusicSearchResult(

                    query=query,

                    songs=[],

                    total=0,

                    provider=str(
                        provider_name
                    ),

                    error=(
                        "Requested music provider "
                        "is not registered."
                    ),
                )

            try:

                if not provider.is_available():

                    return MusicSearchResult(

                        query=query,

                        songs=[],

                        total=0,

                        provider=str(
                            provider_name
                        ),

                        error=(
                            "Requested music provider "
                            "is unavailable."
                        ),
                    )

                result = provider.search(
                    query,
                    limit
                )

                return result.normalize()

            except Exception as error:

                return MusicSearchResult(

                    query=query,

                    songs=[],

                    total=0,

                    provider=str(
                        provider_name
                    ),

                    error=str(
                        error
                    ),
                )

        # ====================================================
        # MULTI PROVIDER
        # ====================================================

        collected = []

        providers_used = []

        errors = []

        # ----------------------------------------------------
        # Ask every available provider.
        #
        # We do NOT stop immediately after iTunes results,
        # because Jamendo may also provide fully playable
        # alternatives.
        # ----------------------------------------------------

        per_provider_limit = max(
            limit,
            10
        )

        for provider in (
            self.available_providers()
        ):

            if not getattr(
                provider,
                "supports_search",
                True
            ):

                continue

            try:

                result = provider.search(

                    query,

                    per_provider_limit
                )

            except Exception as error:

                errors.append(
                    str(error)
                )

                print(
                    "Provider search error:",
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    ),
                    error
                )

                continue

            if getattr(
                result,
                "error",
                ""
            ):

                errors.append(
                    result.error
                )

            songs = list(
                getattr(
                    result,
                    "songs",
                    []
                )
                or []
            )

            if songs:

                collected.extend(
                    songs
                )

                providers_used.append(
                    str(
                        getattr(
                            provider,
                            "provider_name",
                            ""
                        )
                    )
                )

        # ====================================================
        # DEDUP
        # ====================================================

        collected = self._deduplicate(
            collected
        )

        # ====================================================
        # RELEVANCE SORT
        # ====================================================

        collected.sort(
            key=lambda song:
                self._search_score(
                    song,
                    query
                )
        )

        songs = collected[
            :limit
        ]

        return MusicSearchResult(

            query=query,

            songs=songs,

            total=len(
                songs
            ),

            provider=", ".join(
                providers_used
            ),

            error=(
                ""
                if songs
                else (
                    errors[0]
                    if errors
                    else (
                        "No music providers "
                        "returned results."
                    )
                )
            ),
        )

    # ========================================================
    # TRENDING
    # ========================================================

    def get_trending(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = self._normalize_limit(
            limit
        )

        collected = []

        # ----------------------------------------------------
        # Mainstream catalog first.
        # ----------------------------------------------------

        for provider in (
            self.available_providers()
        ):

            try:

                songs = provider.get_trending(
                    limit
                )

            except Exception as error:

                print(
                    "Provider trending error:",
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    ),
                    error
                )

                continue

            collected.extend(
                songs
                or []
            )

        return self._deduplicate(

            collected,

            limit
        )

    # ========================================================
    # POPULAR
    # ========================================================

    def get_popular(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = self._normalize_limit(
            limit
        )

        collected = []

        for provider in (
            self.available_providers()
        ):

            try:

                songs = provider.get_popular(
                    limit
                )

            except Exception as error:

                print(
                    "Provider popular error:",
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    ),
                    error
                )

                continue

            collected.extend(
                songs
                or []
            )

        return self._deduplicate(

            collected,

            limit
        )

    # ========================================================
    # GENRE
    # ========================================================

    def get_by_genre(
        self,
        genre: str,
        limit: int = 20,
    ) -> List[Song]:

        genre = str(
            genre
            or ""
        ).strip()

        if not genre:

            return []

        limit = self._normalize_limit(
            limit
        )

        collected = []

        for provider in (
            self.available_providers()
        ):

            try:

                songs = provider.get_by_genre(

                    genre,

                    limit
                )

            except Exception as error:

                print(
                    "Provider genre error:",
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    ),
                    error
                )

                continue

            collected.extend(
                songs
                or []
            )

        return self._deduplicate(

            collected,

            limit
        )

    # ========================================================
    # MOOD
    # ========================================================

    def get_by_mood(
        self,
        mood: str,
        limit: int = 20,
    ) -> List[Song]:

        mood = str(
            mood
            or ""
        ).strip()

        if not mood:

            return []

        limit = self._normalize_limit(
            limit
        )

        collected = []

        for provider in (
            self.available_providers()
        ):

            try:

                songs = provider.get_by_mood(

                    mood,

                    limit
                )

            except Exception as error:

                print(
                    "Provider mood error:",
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    ),
                    error
                )

                continue

            collected.extend(
                songs
                or []
            )

        return self._deduplicate(

            collected,

            limit
        )

    # ========================================================
    # HINDI
    # ========================================================

    def get_hindi(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = self._normalize_limit(
            limit
        )

        collected = []

        for provider in (
            self.available_providers()
        ):

            try:

                songs = provider.get_hindi(
                    limit
                )

            except Exception as error:

                print(
                    "Provider Hindi error:",
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    ),
                    error
                )

                continue

            collected.extend(
                songs
                or []
            )

        return self._deduplicate(

            collected,

            limit
        )

    # ========================================================
    # ENGLISH
    # ========================================================

    def get_english(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = self._normalize_limit(
            limit
        )

        collected = []

        for provider in (
            self.available_providers()
        ):

            try:

                songs = provider.get_english(
                    limit
                )

            except Exception as error:

                print(
                    "Provider English error:",
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    ),
                    error
                )

                continue

            collected.extend(
                songs
                or []
            )

        return self._deduplicate(

            collected,

            limit
        )

    # ========================================================
    # ARTIST SEARCH
    # ========================================================

    def search_artist(
        self,
        artist: str,
        limit: int = 20,
    ) -> List[Song]:

        artist = str(
            artist
            or ""
        ).strip()

        if not artist:

            return []

        limit = self._normalize_limit(
            limit
        )

        collected = []

        for provider in (
            self.available_providers()
        ):

            try:

                songs = provider.search_artist(

                    artist,

                    limit
                )

            except Exception as error:

                print(
                    "Provider artist error:",
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    ),
                    error
                )

                continue

            collected.extend(
                songs
                or []
            )

        songs = self._deduplicate(
            collected
        )

        artist_lower = (
            artist.lower()
        )

        songs.sort(
            key=lambda song: (
                0
                if artist_lower
                in str(
                    getattr(
                        song,
                        "artist",
                        ""
                    )
                    or ""
                ).lower()
                else 1
            )
        )

        return songs[
            :limit
        ]

    # ========================================================
    # SONG SEARCH
    # ========================================================

    def search_song(
        self,
        title: str,
        limit: int = 20,
    ) -> List[Song]:

        title = str(
            title
            or ""
        ).strip()

        if not title:

            return []

        result = self.search(

            title,

            limit=limit,
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # FIND FULL-PLAYBACK ALTERNATIVE
    # ========================================================

    def find_full_playback_alternative(
        self,
        song: Song,
        limit: int = 10,
    ) -> Optional[Song]:

        """
        If selected song only has a preview, try providers that
        support full playback for a matching track.

        This does NOT guarantee the exact copyrighted recording
        exists on another provider.

        It only returns a result when title/artist matching is
        reasonably strong.
        """

        if song is None:

            return None

        # ----------------------------------------------------
        # Already full playable.
        # ----------------------------------------------------

        try:

            if song.has_full_playback():

                return song

        except Exception:

            pass

        title = str(
            getattr(
                song,
                "title",
                ""
            )
            or ""
        ).strip()

        artist = str(
            getattr(
                song,
                "artist",
                ""
            )
            or ""
        ).strip()

        if not title:

            return None

        query = (
            f"{title} {artist}"
            if artist
            else title
        )

        for provider in (
            self.full_playback_providers()
        ):

            try:

                result = provider.search(

                    query,

                    limit
                )

            except Exception:

                continue

            for candidate in (
                result.songs
                or []
            ):

                candidate_title = str(
                    getattr(
                        candidate,
                        "title",
                        ""
                    )
                    or ""
                ).strip().lower()

                candidate_artist = str(
                    getattr(
                        candidate,
                        "artist",
                        ""
                    )
                    or ""
                ).strip().lower()

                title_lower = (
                    title.lower()
                )

                artist_lower = (
                    artist.lower()
                )

                title_match = (
                    title_lower
                    == candidate_title
                    or
                    title_lower in candidate_title
                    or
                    candidate_title in title_lower
                )

                artist_match = (

                    not artist_lower

                    or

                    artist_lower
                    == candidate_artist

                    or

                    artist_lower
                    in candidate_artist

                    or

                    candidate_artist
                    in artist_lower
                )

                if (
                    title_match
                    and
                    artist_match
                ):

                    return candidate

        return None

    # ========================================================
    # STATUS
    # ========================================================

    def status(
        self
    ):

        status_data = {}

        for provider_name in (
            self.provider_priority
        ):

            provider = self.providers.get(
                provider_name
            )

            if provider is None:

                continue

            try:

                provider_status = (
                    provider.status()
                )

            except Exception:

                provider_status = {

                    "provider":
                        provider_name,

                    "available":
                        False,

                    "enabled":
                        False,

                    "last_error":
                        "Status unavailable.",

                    "capabilities":
                        {},
                }

            status_data[
                provider_name
            ] = provider_status

        return status_data

    # ========================================================
    # PRINT STATUS
    # ========================================================

    def print_status(
        self
    ):

        print()
        print("=" * 60)

        print(
            "LYRx MULTI-PROVIDER REGISTRY"
        )

        print("=" * 60)

        print(
            "Registered:",
            self.provider_names()
        )

        print(
            "Default:",
            (
                self.default_provider_name
                or "None"
            )
        )

        print(
            "Available:",
            [
                getattr(
                    provider,
                    "provider_name",
                    "unknown"
                )
                for provider
                in self.available_providers()
            ]
        )

        print(
            "Full playback:",
            [
                getattr(
                    provider,
                    "provider_name",
                    "unknown"
                )
                for provider
                in self.full_playback_providers()
            ]
        )

        print()

        for (
            provider_name,
            info
        ) in self.status().items():

            print(
                f"{provider_name}:"
            )

            print(
                "  Available:",
                info.get(
                    "available",
                    False
                )
            )

            print(
                "  Enabled:",
                info.get(
                    "enabled",
                    False
                )
            )

            print(
                "  Last error:",
                (
                    info.get(
                        "last_error",
                        ""
                    )
                    or "None"
                )
            )

            capabilities = info.get(
                "capabilities",
                {}
            )

            print(
                "  Capabilities:",
                capabilities
            )

            print()

        print("=" * 60)
        print()


# ============================================================
# SHARED INSTANCE
# ============================================================

provider_registry = (
    ProviderRegistry()
)