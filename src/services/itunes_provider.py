# ============================================================
# LYRx
# DAY 20 - FINAL TASK
# MULTI-PROVIDER ARCHITECTURE
#
# FILE 2
# itunes_provider.py
#
# PATH:
# src/services/itunes_provider.py
#
# PURPOSE:
#   - Mainstream music catalog search
#   - Hindi / English / Bollywood discovery
#   - Artist search
#   - Song search
#   - Genre-style search
#   - Preview playback when available
#
# IMPORTANT:
#   This provider does NOT replace Jamendo.
#
#   Jamendo:
#       full playable indie catalog
#
#   iTunes Search:
#       broad mainstream catalog
#       preview playback when available
#
#   ProviderRegistry will combine both.
# ============================================================

from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
)

import requests

from services.music_provider import (
    MusicProvider,
    MusicSearchResult,
    Song,
)


# ============================================================
# ITUNES PROVIDER
# ============================================================

class ITunesProvider(MusicProvider):

    # ========================================================
    # IDENTITY
    # ========================================================

    provider_name = "itunes"

    display_name = "Apple Music Catalog"

    # ========================================================
    # CAPABILITIES
    # ========================================================

    supports_search = True

    supports_trending = False

    supports_popular = False

    supports_genres = True

    supports_moods = True

    supports_hindi = True

    supports_english = True

    supports_artist_search = True

    supports_song_search = True

    supports_charts = False

    # --------------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------------
    #
    # iTunes Search results commonly expose preview URLs.
    # Treat them as previews, NOT full licensed playback.
    #

    supports_full_playback = False

    supports_preview = True

    supports_download = False

    # ========================================================
    # API
    # ========================================================

    SEARCH_URL = (
        "https://itunes.apple.com/search"
    )

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self
    ):

        super().__init__()

        self.timeout = 15

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent":
                    "LYRx-Music-Player/0.3"
            }
        )

    # ========================================================
    # AVAILABLE
    # ========================================================

    def is_available(
        self
    ) -> bool:

        return bool(
            self.enabled
        )

    # ========================================================
    # REQUEST
    # ========================================================

    def _get(
        self,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:

        try:

            response = self.session.get(

                self.SEARCH_URL,

                params=params,

                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            self.clear_error()

            if not isinstance(
                data,
                dict
            ):

                raise RuntimeError(
                    "Invalid iTunes response."
                )

            return data

        except Exception as error:

            self.set_error(
                error
            )

            raise

    # ========================================================
    # NORMALIZE ARTWORK
    # ========================================================

    @staticmethod
    def _high_res_artwork(
        artwork_url: str
    ) -> str:

        artwork_url = str(
            artwork_url
            or ""
        ).strip()

        if not artwork_url:

            return ""

        # ----------------------------------------------------
        # iTunes artwork often ends with:
        #
        #     100x100bb.jpg
        #
        # Increase it for LYRx cards/player.
        # ----------------------------------------------------

        replacements = [

            (
                "100x100bb.jpg",
                "600x600bb.jpg"
            ),

            (
                "100x100bb.png",
                "600x600bb.png"
            ),

            (
                "60x60bb.jpg",
                "600x600bb.jpg"
            ),

            (
                "60x60bb.png",
                "600x600bb.png"
            ),
        ]

        for old, new in replacements:

            if old in artwork_url:

                return artwork_url.replace(
                    old,
                    new
                )

        return artwork_url

    # ========================================================
    # DURATION
    # ========================================================

    @staticmethod
    def _duration_seconds(
        milliseconds
    ) -> int:

        try:

            milliseconds = int(
                milliseconds
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            return 0

        if milliseconds <= 0:

            return 0

        return int(
            milliseconds // 1000
        )

    # ========================================================
    # NORMALIZE RESULT
    # ========================================================

    def _song_from_item(
        self,
        item
    ) -> Song | None:

        if not isinstance(
            item,
            dict
        ):

            return None

        # ====================================================
        # ONLY MUSIC TRACKS
        # ====================================================

        wrapper_type = str(
            item.get(
                "wrapperType",
                ""
            )
            or ""
        ).lower()

        kind = str(
            item.get(
                "kind",
                ""
            )
            or ""
        ).lower()

        if (
            wrapper_type
            and
            wrapper_type != "track"
        ):

            return None

        if (
            kind
            and
            kind not in (
                "song",
                "music-video",
            )
        ):

            return None

        # ====================================================
        # CORE DATA
        # ====================================================

        track_id = str(
            item.get(
                "trackId",
                ""
            )
            or ""
        )

        title = str(
            item.get(
                "trackName",
                ""
            )
            or ""
        ).strip()

        artist = str(
            item.get(
                "artistName",
                ""
            )
            or ""
        ).strip()

        album = str(
            item.get(
                "collectionName",
                ""
            )
            or ""
        ).strip()

        if not title:

            return None

        # ====================================================
        # ARTWORK
        # ====================================================

        image_url = (
            self._high_res_artwork(
                item.get(
                    "artworkUrl100",
                    ""
                )
                or
                item.get(
                    "artworkUrl60",
                    ""
                )
                or
                ""
            )
        )

        # ====================================================
        # PREVIEW
        # ====================================================

        preview_url = str(
            item.get(
                "previewUrl",
                ""
            )
            or ""
        ).strip()

        # ====================================================
        # URL
        # ====================================================

        external_url = str(
            item.get(
                "trackViewUrl",
                ""
            )
            or ""
        ).strip()

        # ====================================================
        # GENRE
        # ====================================================

        genre = str(
            item.get(
                "primaryGenreName",
                ""
            )
            or ""
        ).strip()

        # ====================================================
        # RELEASE DATE
        # ====================================================

        release_date = str(
            item.get(
                "releaseDate",
                ""
            )
            or ""
        ).strip()

        # ====================================================
        # EXPLICIT
        # ====================================================

        explicit_value = str(
            item.get(
                "trackExplicitness",
                ""
            )
            or ""
        ).lower()

        explicit = (
            explicit_value
            not in (
                "",
                "cleaned",
                "notexplicit",
            )
        )

        # ====================================================
        # LANGUAGE HINT
        # ====================================================

        country = str(
            item.get(
                "country",
                ""
            )
            or ""
        )

        language = ""

        if country.upper() == "IND":

            language = "Hindi/Indian"

        # ====================================================
        # SONG
        # ====================================================

        return Song(

            id=track_id,

            title=title,

            artist=artist,

            album=album,

            image_url=image_url,

            # ------------------------------------------------
            # IMPORTANT:
            #
            # Do NOT put preview into audio_url.
            #
            # This keeps LYRx aware that this is not a
            # guaranteed full track.
            # ------------------------------------------------

            audio_url="",

            preview_url=preview_url,

            duration=self._duration_seconds(
                item.get(
                    "trackTimeMillis",
                    0
                )
            ),

            provider=self.provider_name,

            downloadable=False,

            download_url="",

            share_url=external_url,

            external_url=external_url,

            genre=genre,

            language=language,

            release_date=release_date,

            explicit=explicit,

            full_playback=False,

            preview_available=bool(
                preview_url
            ),

            metadata={

                "artist_id":
                    str(
                        item.get(
                            "artistId",
                            ""
                        )
                        or ""
                    ),

                "collection_id":
                    str(
                        item.get(
                            "collectionId",
                            ""
                        )
                        or ""
                    ),

                "collection_artist":
                    str(
                        item.get(
                            "collectionArtistName",
                            ""
                        )
                        or ""
                    ),

                "country":
                    country,

                "currency":
                    str(
                        item.get(
                            "currency",
                            ""
                        )
                        or ""
                    ),

                "content_advisory":
                    str(
                        item.get(
                            "contentAdvisoryRating",
                            ""
                        )
                        or ""
                    ),

                "raw_kind":
                    kind,
            },
        )

    # ========================================================
    # PARSE RESULTS
    # ========================================================

    def _parse_results(
        self,
        data
    ) -> List[Song]:

        songs = []

        if not isinstance(
            data,
            dict
        ):

            return songs

        results = data.get(
            "results",
            []
        )

        if not isinstance(
            results,
            list
        ):

            return songs

        seen = set()

        for item in results:

            song = self._song_from_item(
                item
            )

            if song is None:

                continue

            key = song.unique_key()

            if key in seen:

                continue

            seen.add(
                key
            )

            songs.append(
                song
            )

        return songs

    # ========================================================
    # CORE SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        limit: int = 20,
        country: str = "IN",
    ) -> MusicSearchResult:

        query = str(
            query
            or ""
        ).strip()

        if not query:

            return MusicSearchResult(

                query="",

                songs=[],

                total=0,

                provider=self.provider_name,

                error="Empty search query.",
            )

        limit = self.normalize_limit(
            limit,
            maximum=50
        )

        try:

            data = self._get(
                {
                    "term":
                        query,

                    "country":
                        str(
                            country
                            or "IN"
                        ).upper(),

                    "media":
                        "music",

                    "entity":
                        "song",

                    "limit":
                        limit,

                    "explicit":
                        "Yes",
                }
            )

            songs = self._parse_results(
                data
            )

            return MusicSearchResult(

                query=query,

                songs=songs,

                total=len(
                    songs
                ),

                provider=self.provider_name,

                error="",
            )

        except Exception as error:

            print(
                "ITunesProvider search error:",
                error
            )

            return MusicSearchResult(

                query=query,

                songs=[],

                total=0,

                provider=self.provider_name,

                error=str(
                    error
                ),
            )

    # ========================================================
    # SEARCH SONG
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

            country="IN",
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # SEARCH ARTIST
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

        # ----------------------------------------------------
        # Searching songs with artist name gives LYRx
        # playable preview results directly.
        # ----------------------------------------------------

        result = self.search(

            artist,

            limit=limit,

            country="IN",
        )

        songs = list(
            result.songs
            or []
        )

        # ====================================================
        # PRIORITIZE ARTIST MATCH
        # ====================================================

        artist_lower = (
            artist.lower()
        )

        songs.sort(
            key=lambda song: (
                0
                if artist_lower
                in song.display_artist().lower()
                else 1
            )
        )

        return songs

    # ========================================================
    # HINDI
    # ========================================================

    def get_hindi(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = self.normalize_limit(
            limit
        )

        # ====================================================
        # MULTIPLE SEARCH TERMS
        # ====================================================
        #
        # Single query "Hindi" can be too generic.
        #
        # These queries improve mainstream Indian results.
        # ====================================================

        queries = [

            "Hindi songs",

            "Bollywood",

            "Hindi hits",

            "Hindi music",
        ]

        collected = []

        seen = set()

        for query in queries:

            result = self.search(

                query,

                limit=limit,

                country="IN",
            )

            for song in (
                result.songs
                or []
            ):

                key = song.unique_key()

                if key in seen:

                    continue

                seen.add(
                    key
                )

                collected.append(
                    song
                )

                if len(
                    collected
                ) >= limit:

                    return collected

        return collected

    # ========================================================
    # ENGLISH
    # ========================================================

    def get_english(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = self.normalize_limit(
            limit
        )

        queries = [

            "English pop",

            "English hits",

            "Pop music",

            "Top English songs",
        ]

        collected = []

        seen = set()

        for query in queries:

            result = self.search(

                query,

                limit=limit,

                country="US",
            )

            for song in (
                result.songs
                or []
            ):

                key = song.unique_key()

                if key in seen:

                    continue

                seen.add(
                    key
                )

                collected.append(
                    song
                )

                if len(
                    collected
                ) >= limit:

                    return collected

        return collected

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

        limit = self.normalize_limit(
            limit
        )

        # ====================================================
        # GENRE QUERY MAPPING
        # ====================================================

        genre_queries = {

            "pop":
                "Pop",

            "rock":
                "Rock",

            "hip hop":
                "Hip Hop",

            "hip-hop":
                "Hip Hop",

            "rap":
                "Hip Hop Rap",

            "electronic":
                "Electronic",

            "edm":
                "EDM",

            "dance":
                "Dance",

            "indie":
                "Indie",

            "jazz":
                "Jazz",

            "classical":
                "Classical",

            "r&b":
                "R&B",

            "rnb":
                "R&B",

            "country":
                "Country",

            "metal":
                "Metal",

            "folk":
                "Folk",

            "bollywood":
                "Bollywood",

            "hindi":
                "Hindi Bollywood",
        }

        search_query = (
            genre_queries.get(
                genre.lower(),
                genre
            )
        )

        result = self.search(

            search_query,

            limit=limit,

            country=(
                "IN"
                if genre.lower()
                in (
                    "bollywood",
                    "hindi",
                )
                else "US"
            ),
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

        mood = str(
            mood
            or ""
        ).strip()

        if not mood:

            return []

        limit = self.normalize_limit(
            limit
        )

        mood_queries = {

            "happy":
                "Happy songs",

            "sad":
                "Sad songs",

            "chill":
                "Chill music",

            "relax":
                "Relaxing music",

            "romantic":
                "Romantic songs",

            "love":
                "Love songs",

            "focus":
                "Focus music",

            "workout":
                "Workout music",

            "energetic":
                "Energetic songs",

            "party":
                "Party songs",

            "sleep":
                "Sleep music",

            "nostalgic":
                "Nostalgic songs",
        }

        query = mood_queries.get(

            mood.lower(),

            f"{mood} songs"
        )

        result = self.search(

            query,

            limit=limit,

            country="IN",
        )

        return list(
            result.songs
            or []
        )

    # ========================================================
    # TRENDING FALLBACK
    # ========================================================
    #
    # iTunes Search endpoint is a search API, not a reliable
    # live chart endpoint.
    #
    # ProviderRegistry should still prefer another provider
    # for true trending data.
    #
    # We return a discovery mix here only as a fallback.
    # ========================================================

    def get_trending(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = self.normalize_limit(
            limit
        )

        queries = [

            "latest Hindi songs",

            "latest English songs",

            "Bollywood hits",

            "Pop hits",
        ]

        songs = []

        seen = set()

        per_query = max(
            3,
            min(
                8,
                limit
            )
        )

        for index, query in enumerate(
            queries
        ):

            country = (
                "IN"
                if index in (
                    0,
                    2,
                )
                else "US"
            )

            result = self.search(

                query,

                limit=per_query,

                country=country,
            )

            for song in (
                result.songs
                or []
            ):

                key = song.unique_key()

                if key in seen:

                    continue

                seen.add(
                    key
                )

                songs.append(
                    song
                )

                if len(
                    songs
                ) >= limit:

                    return songs

        return songs

    # ========================================================
    # POPULAR FALLBACK
    # ========================================================

    def get_popular(
        self,
        limit: int = 20,
    ) -> List[Song]:

        limit = self.normalize_limit(
            limit
        )

        queries = [

            "Bollywood hits",

            "Hindi hits",

            "Pop hits",

            "English hits",
        ]

        songs = []

        seen = set()

        for index, query in enumerate(
            queries
        ):

            country = (
                "IN"
                if index in (
                    0,
                    1,
                )
                else "US"
            )

            result = self.search(

                query,

                limit=limit,

                country=country,
            )

            for song in (
                result.songs
                or []
            ):

                key = song.unique_key()

                if key in seen:

                    continue

                seen.add(
                    key
                )

                songs.append(
                    song
                )

                if len(
                    songs
                ) >= limit:

                    return songs

        return songs

    # ========================================================
    # DEBUG
    # ========================================================

    def print_test(
        self,
        query="Arijit Singh",
        limit=5,
    ):

        print()
        print("=" * 60)

        print(
            "LYRx ITUNES PROVIDER TEST"
        )

        print("=" * 60)

        print(
            "Provider:",
            self.provider_name
        )

        print(
            "Available:",
            self.is_available()
        )

        print(
            "Search:",
            query
        )

        result = self.search(
            query,
            limit
        )

        print(
            "Results:",
            len(
                result.songs
            )
        )

        print()

        for index, song in enumerate(
            result.songs,
            start=1
        ):

            print(
                f"{index}. "
                f"{song.display_title()}"
            )

            print(
                "   Artist:",
                song.display_artist()
            )

            print(
                "   Album:",
                song.album
            )

            print(
                "   Provider:",
                song.provider
            )

            print(
                "   Duration:",
                song.duration_text()
            )

            print(
                "   Preview:",
                (
                    "YES"
                    if song.preview_url
                    else "NO"
                )
            )

            print(
                "   Artwork:",
                song.image_url
            )

            print()

        if result.error:

            print(
                "Error:",
                result.error
            )

        print("=" * 60)
        print()


# ============================================================
# OPTIONAL SHARED INSTANCE
# ============================================================
#
# ProviderRegistry may create its own instance.
#
# Keeping this shared object is still useful for debugging and
# direct tests.
# ============================================================

itunes_provider = (
    ITunesProvider()
)