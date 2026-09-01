# ============================================================
# LYRx
# DAY 21 - PHASE 1
#
# FILE 2
# provider_registry.py
#
# PURPOSE:
#   Unified multi-provider registry.
#
# PROVIDERS:
#
#   Spotify
#       - mainstream catalog
#       - authenticated full playback control
#
#   iTunes
#       - mainstream catalog
#       - preview fallback
#
#   Jamendo
#       - independent catalog
#       - direct full-track streaming
#
# IMPORTANT:
#
#   Spotify is only considered "catalog ready" after the user
#   has authenticated.
#
#   Therefore a configured-but-logged-out Spotify provider
#   cannot break Discover/Home search.
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

from services.spotify_provider import (
    SpotifyProvider,
)

from services.itunes_provider import (
    ITunesProvider,
)

from services.jamendo_provider import (
    JamendoProvider,
)


# ============================================================
# PROVIDER REGISTRY
# ============================================================

class ProviderRegistry:

    """
    Central provider manager for LYRx.

    ==========================================================
    ARCHITECTURE
    ==========================================================

        LYRx UI
           │
           ▼
    ProviderRegistry
           │
           ├── SpotifyProvider
           │       authenticated mainstream playback
           │
           ├── ITunesProvider
           │       mainstream catalog / preview
           │
           └── JamendoProvider
                   direct online music

    ==========================================================
    PROVIDER PRIORITY
    ==========================================================

    When Spotify is authenticated:

        Spotify
        iTunes
        Jamendo

    When Spotify is NOT authenticated:

        iTunes
        Jamendo

    Existing Day 19 / Day 20 architecture remains compatible.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self
    ):

        # ----------------------------------------------------
        # PROVIDERS
        # ----------------------------------------------------

        self.providers: Dict[
            str,
            MusicProvider
        ] = {}

        # ----------------------------------------------------
        # PRIORITY
        # ----------------------------------------------------

        self.provider_priority: List[str] = []

        # ----------------------------------------------------
        # DEFAULT
        # ----------------------------------------------------

        self.default_provider_name = ""

        # ----------------------------------------------------
        # REGISTER BUILT-IN PROVIDERS
        # ----------------------------------------------------

        self._register_default_providers()

    # ========================================================
    # REGISTER DEFAULT PROVIDERS
    # ========================================================

    def _register_default_providers(
        self
    ):

        # ====================================================
        # SPOTIFY
        # ====================================================
        #
        # Highest priority once authenticated.
        # ====================================================

        try:

            spotify = SpotifyProvider()

            self.register(
                spotify,
                make_default=False,
            )

        except Exception as error:

            print(
                "ProviderRegistry Spotify init error:",
                error
            )

        # ====================================================
        # ITUNES
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
        # JAMENDO
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

        # ====================================================
        # EXPLICIT PRIORITY
        # ====================================================

        preferred_order = [

            "spotify",

            "itunes",

            "jamendo",
        ]

        ordered = []

        for provider_name in preferred_order:

            if provider_name in self.providers:

                ordered.append(
                    provider_name
                )

        for provider_name in self.provider_priority:

            if provider_name not in ordered:

                ordered.append(
                    provider_name
                )

        self.provider_priority = (
            ordered
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

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        self.providers[
            provider_name
        ] = provider

        # ----------------------------------------------------
        # PRIORITY
        # ----------------------------------------------------

        if (
            provider_name
            not in self.provider_priority
        ):

            self.provider_priority.append(
                provider_name
            )

        # ----------------------------------------------------
        # DEFAULT
        # ----------------------------------------------------

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
            ==
            provider_name
        ):

            self.default_provider_name = ""

            # ------------------------------------------------
            # Pick first usable normal provider.
            # ------------------------------------------------

            for candidate in (
                self.provider_priority
            ):

                if candidate in self.providers:

                    self.default_provider_name = (
                        candidate
                    )

                    break

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
    # SPOTIFY PROVIDER
    # ========================================================

    def get_spotify_provider(
        self
    ) -> Optional[SpotifyProvider]:

        provider = self.get_provider(
            "spotify"
        )

        if isinstance(
            provider,
            SpotifyProvider
        ):

            return provider

        return None

    # ========================================================
    # ITUNES PROVIDER
    # ========================================================

    def get_itunes_provider(
        self
    ) -> Optional[ITunesProvider]:

        provider = self.get_provider(
            "itunes"
        )

        if isinstance(
            provider,
            ITunesProvider
        ):

            return provider

        return None

    # ========================================================
    # JAMENDO PROVIDER
    # ========================================================

    def get_jamendo_provider(
        self
    ) -> Optional[JamendoProvider]:

        provider = self.get_provider(
            "jamendo"
        )

        if isinstance(
            provider,
            JamendoProvider
        ):

            return provider

        return None

    # ========================================================
    # DEFAULT PROVIDER
    # ========================================================

    def get_default_provider(
        self
    ) -> Optional[MusicProvider]:

        # ====================================================
        # AUTHENTICATED SPOTIFY BECOMES EFFECTIVE DEFAULT
        # ====================================================

        spotify = (
            self.get_spotify_provider()
        )

        if spotify is not None:

            try:

                if (
                    spotify.is_available()
                    and
                    spotify.is_authenticated()
                ):

                    return spotify

            except Exception:

                pass

        # ====================================================
        # CONFIGURED DEFAULT
        # ====================================================

        if self.default_provider_name:

            provider = self.get_provider(
                self.default_provider_name
            )

            if provider is not None:

                return provider

        # ====================================================
        # FALLBACK
        # ====================================================

        providers = (
            self.available_providers()
        )

        if providers:

            return providers[0]

        return None

    # ========================================================
    # SET DEFAULT PROVIDER
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
    # PROVIDER AVAILABLE
    # ========================================================

    @staticmethod
    def _provider_available(
        provider
    ) -> bool:

        if provider is None:

            return False

        try:

            return bool(
                provider.is_available()
            )

        except Exception:

            return False

    # ========================================================
    # PROVIDER READY FOR CATALOG
    # ========================================================

    @staticmethod
    def _provider_catalog_ready(
        provider
    ) -> bool:

        if provider is None:

            return False

        # ----------------------------------------------------
        # PROVIDER AVAILABLE
        # ----------------------------------------------------

        try:

            if not provider.is_available():

                return False

        except Exception:

            return False

        # ====================================================
        # SPOTIFY SPECIAL CASE
        # ====================================================
        #
        # Spotify API catalog requests require authorization.
        #
        # Configured but logged-out Spotify should NOT be
        # considered ready.
        # ====================================================

        provider_name = str(
            getattr(
                provider,
                "provider_name",
                ""
            )
            or ""
        ).lower()

        if provider_name == "spotify":

            try:

                return bool(
                    provider.is_authenticated()
                )

            except Exception:

                return False

        return True

    # ========================================================
    # AVAILABLE PROVIDERS
    # ========================================================

    def available_providers(
        self
    ) -> List[MusicProvider]:

        """
        Providers ready for actual catalog requests.

        Spotify will only appear here after authentication.
        """

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

                if self._provider_catalog_ready(
                    provider
                ):

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
    # CONFIGURED PROVIDERS
    # ========================================================

    def configured_providers(
        self
    ) -> List[MusicProvider]:

        """
        Returns providers that have enough configuration to exist,
        even if login is still required.
        """

        result = []

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

                    result.append(
                        provider
                    )

            except Exception:

                continue

        return result

    # ========================================================
    # HAS AVAILABLE PROVIDER
    # ========================================================

    def has_available_provider(
        self
    ) -> bool:

        return bool(
            self.available_providers()
        )

    # ========================================================
    # SPOTIFY CONFIGURED
    # ========================================================

    def spotify_configured(
        self
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if spotify is None:

            return False

        try:

            return bool(
                spotify.is_configured()
            )

        except Exception:

            return False

    # ========================================================
    # SPOTIFY AUTHENTICATED
    # ========================================================

    def spotify_authenticated(
        self
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if spotify is None:

            return False

        try:

            return bool(
                spotify.is_authenticated()
            )

        except Exception:

            return False

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

            try:

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

            except Exception:

                continue

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
    # SONG PROVIDER
    # ========================================================

    @staticmethod
    def song_provider_name(
        song
    ) -> str:

        if song is None:

            return ""

        return str(

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

    # ========================================================
    # SONG KEY
    # ========================================================

    @staticmethod
    def _song_key(
        song
    ):

        if song is None:

            return (
                "",
                "",
            )

        # ----------------------------------------------------
        # MODEL-SUPPLIED KEY
        # ----------------------------------------------------

        try:

            if hasattr(
                song,
                "unique_key"
            ):

                return song.unique_key()

        except Exception:

            pass

        provider = (
            ProviderRegistry
            .song_provider_name(
                song
            )
        )

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
    # CROSS-PROVIDER SONG KEY
    # ========================================================

    @staticmethod
    def _cross_provider_key(
        song
    ):

        """
        Used to prevent the same song from appearing repeatedly
        from Spotify + iTunes + Jamendo.
        """

        if song is None:

            return (
                "",
                ""
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

        # ----------------------------------------------------
        # BASIC NORMALIZATION
        # ----------------------------------------------------

        title = (
            title
            .replace(
                " - single",
                ""
            )
            .replace(
                "(single)",
                ""
            )
            .strip()
        )

        artist = artist.strip()

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
        cross_provider=True,
    ) -> List[Song]:

        result = []

        seen_provider = set()

        seen_cross = set()

        for song in (
            songs
            or []
        ):

            if song is None:

                continue

            provider_key = (
                self._song_key(
                    song
                )
            )

            if provider_key in seen_provider:

                continue

            if cross_provider:

                cross_key = (
                    self._cross_provider_key(
                        song
                    )
                )

                if (
                    cross_key
                    !=
                    (
                        "",
                        ""
                    )
                    and
                    cross_key in seen_cross
                ):

                    continue

                seen_cross.add(
                    cross_key
                )

            seen_provider.add(
                provider_key
            )

            result.append(
                song
            )

            if (
                limit is not None
                and
                len(result)
                >=
                limit
            ):

                break

        return result

    # ========================================================
    # SEARCH SCORE
    # ========================================================

    @staticmethod
    def _search_score(
        song,
        query
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

        provider = (
            ProviderRegistry
            .song_provider_name(
                song
            )
        )

        score = 100

        # ====================================================
        # TITLE RELEVANCE
        # ====================================================

        if title == query:

            score -= 60

        elif query in title:

            score -= 40

        # ====================================================
        # ARTIST RELEVANCE
        # ====================================================

        if artist == query:

            score -= 50

        elif query in artist:

            score -= 30

        # ====================================================
        # PROVIDER PRIORITY
        # ====================================================
        #
        # Spotify authenticated:
        #     strongest result preference
        #
        # iTunes:
        #     strong mainstream fallback
        #
        # Jamendo:
        #     independent fallback
        # ====================================================

        if provider == "spotify":

            score -= 20

        elif provider == "itunes":

            score -= 10

        elif provider == "jamendo":

            score -= 3

        # ====================================================
        # FULL PLAYBACK BONUS
        # ====================================================

        try:

            if song.has_full_playback():

                score -= 5

        except Exception:

            if bool(
                getattr(
                    song,
                    "full_playback",
                    False
                )
            ):

                score -= 5

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

        # ====================================================
        # EMPTY QUERY
        # ====================================================

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

            # ------------------------------------------------
            # SPOTIFY REQUIRES LOGIN
            # ------------------------------------------------

            if (
                str(
                    provider_name
                ).lower()
                ==
                "spotify"
            ):

                try:

                    if not provider.is_authenticated():

                        return MusicSearchResult(

                            query=query,

                            songs=[],

                            total=0,

                            provider="spotify",

                            error=(
                                "Spotify account is "
                                "not authenticated."
                            ),
                        )

                except Exception:

                    return MusicSearchResult(

                        query=query,

                        songs=[],

                        total=0,

                        provider="spotify",

                        error=(
                            "Spotify authentication "
                            "state unavailable."
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

                try:

                    return result.normalize()

                except Exception:

                    return result

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
        # MULTI-PROVIDER SEARCH
        # ====================================================

        collected = []

        providers_used = []

        errors = []

        # ----------------------------------------------------
        # Ask all catalog-ready providers.
        # ----------------------------------------------------

        for provider in (
            self.available_providers()
        ):

            provider_name_value = str(
                getattr(
                    provider,
                    "provider_name",
                    ""
                )
                or ""
            )

            try:

                if not getattr(
                    provider,
                    "supports_search",
                    True
                ):

                    continue

                # ------------------------------------------------
                # Spotify provider caps search internally.
                # ------------------------------------------------

                provider_limit = (
                    min(
                        limit,
                        10
                    )
                    if provider_name_value == "spotify"
                    else limit
                )

                result = provider.search(

                    query,

                    provider_limit
                )

            except Exception as error:

                errors.append(
                    str(error)
                )

                print(
                    "Provider search error:",
                    provider_name_value,
                    error
                )

                continue

            if getattr(
                result,
                "error",
                ""
            ):

                errors.append(
                    str(
                        result.error
                    )
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
                    provider_name_value
                )

        # ====================================================
        # DEDUPLICATE
        # ====================================================

        collected = (
            self._deduplicate(
                collected
            )
        )

        # ====================================================
        # RELEVANCE
        # ====================================================

        collected.sort(
            key=lambda song:
                self._search_score(
                    song,
                    query
                )
        )

        songs = (
            collected[
                :limit
            ]
        )

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
    # COLLECT METHOD
    # ========================================================

    def _collect_provider_method(
        self,
        method_name,
        *args,
        limit=20,
    ) -> List[Song]:

        limit = (
            self._normalize_limit(
                limit
            )
        )

        collected = []

        for provider in (
            self.available_providers()
        ):

            provider_name = str(
                getattr(
                    provider,
                    "provider_name",
                    "unknown"
                )
                or "unknown"
            )

            method = getattr(
                provider,
                method_name,
                None
            )

            if not callable(
                method
            ):

                continue

            try:

                provider_limit = (
                    min(
                        limit,
                        10
                    )
                    if provider_name
                    ==
                    "spotify"
                    else limit
                )

                songs = method(

                    *args,

                    provider_limit
                )

            except Exception as error:

                print(
                    f"Provider {method_name} error:",
                    provider_name,
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
    # TRENDING
    # ========================================================

    def get_trending(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = (
            self._normalize_limit(
                limit
            )
        )

        collected = []

        # ====================================================
        # SPOTIFY
        # ====================================================
        #
        # Day 21 Spotify provider does not yet implement a
        # dedicated chart endpoint.
        #
        # Therefore use Hindi/mainstream discovery when
        # authenticated.
        # ====================================================

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is not None
            and
            self.spotify_authenticated()
        ):

            try:

                spotify_songs = (
                    spotify.get_hindi(
                        min(
                            limit,
                            10
                        )
                    )
                )

                collected.extend(
                    spotify_songs
                    or []
                )

            except Exception as error:

                print(
                    "Spotify trending fallback error:",
                    error
                )

        # ====================================================
        # OTHER PROVIDERS
        # ====================================================

        for provider in (
            self.available_providers()
        ):

            provider_name = (
                self.song_provider_name(
                    provider
                )
            )

            provider_name = str(
                getattr(
                    provider,
                    "provider_name",
                    provider_name
                )
                or ""
            ).lower()

            if provider_name == "spotify":

                continue

            method = getattr(
                provider,
                "get_trending",
                None
            )

            if not callable(
                method
            ):

                continue

            try:

                songs = method(
                    limit
                )

            except Exception as error:

                print(
                    "Provider trending error:",
                    provider_name,
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

        spotify = (
            self.get_spotify_provider()
        )

        # ====================================================
        # SPOTIFY MAINSTREAM
        # ====================================================

        if (
            spotify is not None
            and
            self.spotify_authenticated()
        ):

            try:

                songs = (
                    spotify.get_hindi(
                        min(
                            limit,
                            10
                        )
                    )
                )

                collected.extend(
                    songs
                    or []
                )

            except Exception as error:

                print(
                    "Spotify popular fallback error:",
                    error
                )

        # ====================================================
        # ITUNES / JAMENDO
        # ====================================================

        for provider in (
            self.available_providers()
        ):

            provider_name = str(
                getattr(
                    provider,
                    "provider_name",
                    ""
                )
                or ""
            ).lower()

            if provider_name == "spotify":

                continue

            method = getattr(
                provider,
                "get_popular",
                None
            )

            if not callable(
                method
            ):

                continue

            try:

                songs = method(
                    limit
                )

            except Exception as error:

                print(
                    "Provider popular error:",
                    provider_name,
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

        return (
            self._collect_provider_method(

                "get_by_genre",

                genre,

                limit=limit,
            )
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

        return (
            self._collect_provider_method(

                "get_by_mood",

                mood,

                limit=limit,
            )
        )

    # ========================================================
    # HINDI
    # ========================================================

    def get_hindi(
        self,
        limit: int = 20,
    ) -> List[Song]:

        return (
            self._collect_provider_method(

                "get_hindi",

                limit=limit,
            )
        )

    # ========================================================
    # ENGLISH
    # ========================================================

    def get_english(
        self,
        limit: int = 20,
    ) -> List[Song]:

        return (
            self._collect_provider_method(

                "get_english",

                limit=limit,
            )
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

        songs = (
            self._collect_provider_method(

                "search_artist",

                artist,

                limit=limit,
            )
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

        # ----------------------------------------------------
        # Generic search has better relevance handling.
        # ----------------------------------------------------

        result = self.search(

            title,

            limit=limit,
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # SONG NEEDS REMOTE PLAYBACK
    # ========================================================

    def song_uses_remote_playback(
        self,
        song
    ) -> bool:

        provider = (
            self.song_provider_name(
                song
            )
        )

        if provider == "spotify":

            return True

        metadata = getattr(
            song,
            "metadata",
            {}
        )

        if isinstance(
            metadata,
            dict
        ):

            return (
                metadata.get(
                    "playback_mode"
                )
                ==
                "spotify_remote"
            )

        return False

    # ========================================================
    # PLAY SONG
    # ========================================================

    def play_song(
        self,
        song,
        device_id="",
    ) -> bool:

        """
        Provider-aware playback entry point.

        Spotify:
            Spotify Connect / remote playback.

        Jamendo / iTunes:
            Existing QMediaPlayer path remains handled by
            NowPlaying/AppWindow for now.
        """

        if song is None:

            return False

        provider_name = (
            self.song_provider_name(
                song
            )
        )

        # ====================================================
        # SPOTIFY
        # ====================================================

        if provider_name == "spotify":

            spotify = (
                self.get_spotify_provider()
            )

            if spotify is None:

                print(
                    "Spotify provider is unavailable."
                )

                return False

            if not self.spotify_authenticated():

                print(
                    "Spotify is not authenticated."
                )

                return False

            return spotify.play_track(

                song,

                device_id=device_id,
            )

        # ====================================================
        # DIRECT PLAYBACK PROVIDERS
        # ====================================================

        return False

    # ========================================================
    # SPOTIFY LOGIN
    # ========================================================

    def login_spotify(
        self
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if spotify is None:

            print(
                "Spotify provider is not registered."
            )

            return False

        if not spotify.is_configured():

            print(
                "Spotify provider is not configured."
            )

            return False

        return spotify.login_interactive()

    # ========================================================
    # SPOTIFY LOGOUT
    # ========================================================

    def logout_spotify(
        self
    ):

        spotify = (
            self.get_spotify_provider()
        )

        if spotify is None:

            return

        spotify.logout()

    # ========================================================
    # PAUSE SPOTIFY
    # ========================================================

    def pause_spotify(
        self
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is None
            or
            not self.spotify_authenticated()
        ):

            return False

        return spotify.pause()

    # ========================================================
    # RESUME SPOTIFY
    # ========================================================

    def resume_spotify(
        self
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is None
            or
            not self.spotify_authenticated()
        ):

            return False

        return spotify.resume()

    # ========================================================
    # NEXT SPOTIFY
    # ========================================================

    def next_spotify(
        self
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is None
            or
            not self.spotify_authenticated()
        ):

            return False

        return spotify.next_track()

    # ========================================================
    # PREVIOUS SPOTIFY
    # ========================================================

    def previous_spotify(
        self
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is None
            or
            not self.spotify_authenticated()
        ):

            return False

        return spotify.previous_track()

    # ========================================================
    # SEEK SPOTIFY
    # ========================================================

    def seek_spotify(
        self,
        position_ms
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is None
            or
            not self.spotify_authenticated()
        ):

            return False

        return spotify.seek(
            position_ms
        )

    # ========================================================
    # SPOTIFY VOLUME
    # ========================================================

    def set_spotify_volume(
        self,
        value
    ) -> bool:

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is None
            or
            not self.spotify_authenticated()
        ):

            return False

        return spotify.set_volume(
            value
        )

    # ========================================================
    # SPOTIFY DEVICES
    # ========================================================

    def spotify_devices(
        self
    ):

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is None
            or
            not self.spotify_authenticated()
        ):

            return []

        return spotify.get_devices()

    # ========================================================
    # SPOTIFY RECENTLY PLAYED
    # ========================================================

    def spotify_recently_played(
        self,
        limit=10,
    ):

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is None
            or
            not self.spotify_authenticated()
        ):

            return []

        return spotify.recently_played(
            limit
        )

    # ========================================================
    # FULL PLAYBACK ALTERNATIVE
    # ========================================================

    def find_full_playback_alternative(
        self,
        song,
        limit=10,
    ) -> Optional[Song]:

        """
        Day 21:

        First try Spotify exact-match search.

        If Spotify is unavailable, try other providers that
        support full playback.
        """

        if song is None:

            return None

        # ----------------------------------------------------
        # Already Spotify.
        # ----------------------------------------------------

        if (
            self.song_provider_name(
                song
            )
            ==
            "spotify"
        ):

            return song

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

        # ====================================================
        # SPOTIFY FIRST
        # ====================================================

        spotify = (
            self.get_spotify_provider()
        )

        if (
            spotify is not None
            and
            self.spotify_authenticated()
        ):

            query = (
                f"{title} {artist}"
                if artist
                else title
            )

            result = spotify.search(

                query,

                limit=min(
                    limit,
                    10
                )
            )

            title_lower = (
                title.lower()
            )

            artist_lower = (
                artist.lower()
            )

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
                ).lower()

                candidate_artist = str(
                    getattr(
                        candidate,
                        "artist",
                        ""
                    )
                    or ""
                ).lower()

                title_match = (

                    title_lower
                    ==
                    candidate_title

                    or

                    title_lower
                    in candidate_title

                    or

                    candidate_title
                    in title_lower
                )

                artist_match = (

                    not artist_lower

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

        # ====================================================
        # OTHER FULL-PLAYBACK PROVIDERS
        # ====================================================

        for provider in (
            self.full_playback_providers()
        ):

            provider_name = str(
                getattr(
                    provider,
                    "provider_name",
                    ""
                )
                or ""
            ).lower()

            if provider_name == "spotify":

                continue

            search_method = getattr(
                provider,
                "search",
                None
            )

            if not callable(
                search_method
            ):

                continue

            query = (
                f"{title} {artist}"
                if artist
                else title
            )

            try:

                result = search_method(

                    query,

                    limit
                )

            except Exception:

                continue

            for candidate in (
                getattr(
                    result,
                    "songs",
                    []
                )
                or []
            ):

                candidate_title = str(
                    getattr(
                        candidate,
                        "title",
                        ""
                    )
                    or ""
                ).lower()

                candidate_artist = str(
                    getattr(
                        candidate,
                        "artist",
                        ""
                    )
                    or ""
                ).lower()

                if (
                    title.lower()
                    ==
                    candidate_title
                    and
                    (
                        not artist
                        or
                        artist.lower()
                        in candidate_artist
                    )
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

            # =================================================
            # BASE STATUS
            # =================================================

            try:

                available = bool(
                    provider.is_available()
                )

            except Exception:

                available = False

            # =================================================
            # AUTH
            # =================================================

            authenticated = None

            if provider_name == "spotify":

                try:

                    authenticated = bool(
                        provider.is_authenticated()
                    )

                except Exception:

                    authenticated = False

            # =================================================
            # CATALOG READY
            # =================================================

            catalog_ready = bool(
                self._provider_catalog_ready(
                    provider
                )
            )

            status_data[
                provider_name
            ] = {

                "available":
                    available,

                "catalog_ready":
                    catalog_ready,

                "authenticated":
                    authenticated,

                "enabled":
                    bool(
                        getattr(
                            provider,
                            "enabled",
                            True
                        )
                    ),

                "full_playback":
                    bool(
                        getattr(
                            provider,
                            "supports_full_playback",
                            False
                        )
                    ),

                "preview":
                    bool(
                        getattr(
                            provider,
                            "supports_preview",
                            False
                        )
                    ),

                "last_error":
                    str(
                        getattr(
                            provider,
                            "last_error",
                            ""
                        )
                        or ""
                    ),
            }

        return status_data

    # ========================================================
    # PRINT STATUS
    # ========================================================

    def print_status(
        self
    ):

        print()
        print("=" * 64)

        print(
            "LYRx DAY 21 MULTI-PROVIDER REGISTRY"
        )

        print("=" * 64)

        print(
            "Registered:",
            self.provider_names()
        )

        print(
            "Configured:",
            [
                getattr(
                    provider,
                    "provider_name",
                    "unknown"
                )
                for provider
                in self.configured_providers()
            ]
        )

        print(
            "Catalog ready:",
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
            "Spotify configured:",
            self.spotify_configured()
        )

        print(
            "Spotify authenticated:",
            self.spotify_authenticated()
        )

        print(
            "Effective default:",
            (
                getattr(
                    self.get_default_provider(),
                    "provider_name",
                    "None"
                )
                if self.get_default_provider()
                else "None"
            )
        )

        print()

        for (
            provider_name,
            info
        ) in self.status().items():

            print(
                provider_name.upper()
            )

            print(
                "  Available:",
                info[
                    "available"
                ]
            )

            print(
                "  Catalog ready:",
                info[
                    "catalog_ready"
                ]
            )

            if (
                info[
                    "authenticated"
                ]
                is not None
            ):

                print(
                    "  Authenticated:",
                    info[
                        "authenticated"
                    ]
                )

            print(
                "  Full playback:",
                info[
                    "full_playback"
                ]
            )

            print(
                "  Preview:",
                info[
                    "preview"
                ]
            )

            print(
                "  Error:",
                (
                    info[
                        "last_error"
                    ]
                    or "None"
                )
            )

            print()

        print("=" * 64)
        print()


# ============================================================
# SHARED REGISTRY
# ============================================================

provider_registry = (
    ProviderRegistry()
)