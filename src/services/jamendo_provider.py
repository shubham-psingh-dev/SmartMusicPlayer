# ============================================================
# LYRx
# DAY 20 - PHASE 2
# JAMENDO PROVIDER ADAPTER
# ============================================================

from __future__ import annotations

from typing import List

from services.music_provider import (
    MusicProvider,
    MusicSearchResult,
    Song,
)

from services.music_service import (
    MusicService,
)


# ============================================================
# JAMENDO PROVIDER
# ============================================================

class JamendoProvider(MusicProvider):

    """
    Adapter between the existing LYRx MusicService
    and the new unified MusicProvider architecture.

    IMPORTANT:

    Existing:
        MusicService
        models.song.Song
        Discover online loader
        NowPlaying online playback

    remain untouched.

    This provider simply converts the old Jamendo Song
    objects into the new unified provider Song objects.

    Later LYRx can register:

        JamendoProvider
        AppleMusicProvider
        future providers

    without forcing the UI to know which API is being used.
    """

    # ========================================================
    # PROVIDER DETAILS
    # ========================================================

    provider_name = "jamendo"

    display_name = "Jamendo"

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        #
        # We create a MusicService instance here instead of
        # relying on the shared module-level instance.
        #
        # This keeps the provider self-contained.
        #

        self.service = MusicService()

    # ========================================================
    # AVAILABLE
    # ========================================================

    def is_available(self) -> bool:

        if not self.enabled:

            return False

        try:

            return bool(
                self.service.is_configured()
            )

        except Exception as error:

            self.set_error(
                error
            )

            return False

    # ========================================================
    # OLD SONG -> NEW SONG
    # ========================================================

    @staticmethod
    def convert_song(
        old_song
    ) -> Song | None:

        """
        Converts models.song.Song coming from MusicService
        into services.music_provider.Song.
        """

        if old_song is None:

            return None

        try:

            song_id = str(
                getattr(
                    old_song,
                    "id",
                    ""
                )
                or ""
            )

            title = str(
                getattr(
                    old_song,
                    "title",
                    ""
                )
                or ""
            )

            artist = str(
                getattr(
                    old_song,
                    "artist",
                    ""
                )
                or ""
            )

            album = str(
                getattr(
                    old_song,
                    "album",
                    ""
                )
                or ""
            )

            image_url = str(
                getattr(
                    old_song,
                    "image_url",
                    ""
                )
                or ""
            )

            audio_url = str(
                getattr(
                    old_song,
                    "audio_url",
                    ""
                )
                or ""
            )

            share_url = str(
                getattr(
                    old_song,
                    "share_url",
                    ""
                )
                or ""
            )

            duration = int(
                getattr(
                    old_song,
                    "duration",
                    0
                )
                or 0
            )

            downloadable = bool(
                getattr(
                    old_song,
                    "downloadable",
                    False
                )
            )

            download_url = str(
                getattr(
                    old_song,
                    "download_url",
                    ""
                )
                or ""
            )

        except Exception:

            return None

        # ----------------------------------------------------
        # IGNORE EMPTY RESULTS
        # ----------------------------------------------------

        if not title.strip():

            return None

        if not artist.strip():

            artist = "Unknown Artist"

        # ----------------------------------------------------
        # CREATE NEW SONG
        # ----------------------------------------------------

        song = Song(

            id=song_id,

            title=title,

            artist=artist,

            album=album,

            image_url=image_url,

            audio_url=audio_url,

            preview_url="",

            duration=duration,

            provider="jamendo",

            downloadable=downloadable,

            download_url=download_url,

            share_url=share_url,

            external_url=share_url,

            genre="",

            language="",

            release_date="",

            full_playback=bool(audio_url),

            preview_available=False,

            metadata={

                "source":
                    "jamendo",

                "downloadable":
                    downloadable,

                "download_url":
                    download_url,

                "original_song":
                    old_song,

            },
        )

        return song

    # ========================================================
    # CONVERT SONG LIST
    # ========================================================

    @classmethod
    def convert_songs(
        cls,
        songs
    ) -> List[Song]:

        converted = []

        if not songs:

            return converted

        for old_song in songs:

            try:

                song = cls.convert_song(
                    old_song
                )

                if song is None:
                    continue

                # Unified Day-20 Song model does not have is_valid().
                # A converted Jamendo result is usable when it has a title.
                if not str(
                    getattr(
                        song,
                        "title",
                        ""
                    )
                    or ""
                ).strip():

                    continue

                converted.append(
                song
                )

            except Exception as error:

                print(
                    "JamendoProvider conversion error:",
                    error
                )

        return converted

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        limit: int = 20
    ) -> MusicSearchResult:

        query = str(
            query
        ).strip()

        if not query:

            return MusicSearchResult(

                query="",

                songs=[],

                total=0,

                provider=self.provider_name,

                error="Empty search query.",
            )

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            limit = 20

        limit = max(
            1,
            min(
                limit,
                50
            )
        )

        # ----------------------------------------------------
        # SEARCH JAMENDO
        # ----------------------------------------------------

        try:

            self.clear_error()

            old_songs = (
                self.service.search_tracks(
                    query,
                    limit
                )
            )

            songs = (
                self.convert_songs(
                    old_songs
                )
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

            self.set_error(
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
    # TRENDING
    # ========================================================

    def get_trending(
        self,
        limit: int = 20
    ) -> List[Song]:

        try:

            limit = int(
                limit
            )

        except (
            ValueError,
            TypeError
        ):

            limit = 20

        limit = max(
            1,
            min(
                limit,
                50
            )
        )

        try:

            self.clear_error()

            old_songs = (
                self.service.get_trending_tracks(
                    limit
                )
            )

            # ------------------------------------------------
            # FALLBACK
            # ------------------------------------------------
            #
            # We already discovered during Day 19 that
            # Jamendo's trending endpoint may occasionally
            # return zero tracks even though popular works.
            #

            if not old_songs:

                old_songs = (
                    self.service.get_popular_tracks(
                        limit
                    )
                )

            return self.convert_songs(
                old_songs
            )

        except Exception as error:

            self.set_error(
                error
            )

            return []

    # ========================================================
    # POPULAR
    # ========================================================

    def get_popular(
        self,
        limit: int = 20
    ) -> List[Song]:

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            limit = 20

        limit = max(
            1,
            min(
                limit,
                50
            )
        )

        try:

            self.clear_error()

            songs = (
                self.service
                .get_popular_tracks(
                    limit
                )
            )

            return self.convert_songs(
                songs
            )

        except Exception as error:

            self.set_error(
                error
            )

            return []

    # ========================================================
    # GENRE SEARCH
    # ========================================================

    def get_by_genre(
        self,
        genre: str,
        limit: int = 20
    ) -> List[Song]:

        genre = str(
            genre
        ).strip()

        if not genre:

            return []

        # ----------------------------------------------------
        # GENRE QUERY MAPPING
        # ----------------------------------------------------
        #
        # Jamendo does not behave exactly like Spotify-style
        # catalog filtering, so for now we use curated search
        # terms.
        #
        # Later Apple / another provider can implement true
        # genre-based endpoints behind the SAME method.
        #

        genre_map = {

            "pop":
                "pop",

            "rock":
                "rock",

            "hip hop":
                "hip hop",

            "hip-hop":
                "hip hop",

            "rap":
                "rap",

            "electronic":
                "electronic",

            "edm":
                "electronic",

            "dance":
                "dance",

            "chill":
                "chill",

            "lofi":
                "lofi",

            "lo-fi":
                "lofi",

            "jazz":
                "jazz",

            "classical":
                "classical",

            "ambient":
                "ambient",

            "acoustic":
                "acoustic",

            "instrumental":
                "instrumental",

            "romantic":
                "love romantic",

            "love":
                "love",

            "workout":
                "workout energetic",

            "focus":
                "focus instrumental",

            "sleep":
                "sleep ambient",

            "meditation":
                "meditation",

            "party":
                "party dance",

            "happy":
                "happy",

            "sad":
                "sad",

        }

        normalized = (
            genre
            .lower()
            .strip()
        )

        query = genre_map.get(
            normalized,
            genre
        )

        result = self.search(
            query,
            limit
        )

        return result.songs

    # ========================================================
    # HINDI
    # ========================================================

    def get_hindi(
        self,
        limit: int = 20
    ) -> List[Song]:

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        #
        # Jamendo is not a Bollywood / commercial Indian
        # catalog provider.
        #
        # This search can return Indian/Hindi tagged music,
        # but it should NOT be treated as Spotify-equivalent
        # Bollywood coverage.
        #

        search_queries = [

            "hindi",

            "india",

            "indian",

            "bollywood",
        ]

        return self._multi_query_search(

            search_queries,

            limit
        )

    # ========================================================
    # ENGLISH
    # ========================================================

    def get_english(
        self,
        limit: int = 20
    ) -> List[Song]:

        search_queries = [

            "pop",

            "rock",

            "electronic",

            "love",
        ]

        return self._multi_query_search(

            search_queries,

            limit
        )

    # ========================================================
    # MOOD
    # ========================================================

    def get_by_mood(
        self,
        mood: str,
        limit: int = 20
    ) -> List[Song]:

        mood = str(
            mood
        ).strip()

        if not mood:

            return []

        mood_map = {

            "chill":
                [
                    "chill",
                    "lofi",
                    "ambient",
                ],

            "happy":
                [
                    "happy",
                    "uplifting",
                    "feel good",
                ],

            "sad":
                [
                    "sad",
                    "emotional",
                    "melancholy",
                ],

            "energetic":
                [
                    "energetic",
                    "workout",
                    "dance",
                ],

            "romantic":
                [
                    "romantic",
                    "love",
                    "acoustic love",
                ],

            "focus":
                [
                    "focus",
                    "instrumental",
                    "ambient",
                ],

            "sleep":
                [
                    "sleep",
                    "relax",
                    "meditation",
                ],

        }

        queries = mood_map.get(

            mood.lower(),

            [
                mood
            ]
        )

        return self._multi_query_search(

            queries,

            limit
        )

    # ========================================================
    # MULTI QUERY SEARCH
    # ========================================================

    def _multi_query_search(
        self,
        queries,
        limit=20
    ) -> List[Song]:

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            limit = 20

        limit = max(
            1,
            min(
                limit,
                50
            )
        )

        collected = []

        used_ids = set()

        # ----------------------------------------------------
        # Do not request limit songs for every query.
        # Split the total roughly across queries.
        # ----------------------------------------------------

        query_count = max(
            1,
            len(
                queries
            )
        )

        per_query = max(
            5,
            (
                limit
                // query_count
            )
            + 3
        )

        for query in queries:

            if len(
                collected
            ) >= limit:

                break

            try:

                result = self.search(

                    query,

                    per_query
                )

            except Exception as error:

                print(
                    "JamendoProvider multi-search error:",
                    error
                )

                continue

            for song in result.songs:

                # --------------------------------------------
                # DEDUPLICATE
                # --------------------------------------------

                unique_key = (

                    song.id

                    or

                    (
                        song.title.lower(),
                        song.artist.lower()
                    )
                )

                if unique_key in used_ids:

                    continue

                used_ids.add(
                    unique_key
                )

                collected.append(
                    song
                )

                if len(
                    collected
                ) >= limit:

                    break

        return collected[
            :limit
        ]

    # ========================================================
    # ARTIST SEARCH
    # ========================================================

    def search_artist(
        self,
        artist: str,
        limit: int = 20
    ) -> List[Song]:

        artist = str(
            artist
        ).strip()

        if not artist:

            return []

        result = self.search(
            artist,
            limit
        )

        return result.songs

    # ========================================================
    # SONG SEARCH
    # ========================================================

    def search_song(
        self,
        title: str,
        limit: int = 20
    ) -> List[Song]:

        title = str(
            title
        ).strip()

        if not title:

            return []

        result = self.search(
            title,
            limit
        )

        return result.songs

    # ========================================================
    # DEBUG
    # ========================================================

    def print_status(self):

        print()

        print(
            "=" * 60
        )

        print(
            "LYRx JAMENDO PROVIDER"
        )

        print(
            "=" * 60
        )

        print(
            "Provider:",
            self.display_name
        )

        print(
            "Configured:",
            self.service.is_configured()
        )

        print(
            "Available:",
            self.is_available()
        )

        print(
            "Last error:",
            (
                self.last_error
                if self.last_error
                else "None"
            )
        )

        print(
            "=" * 60
        )

        print()


# ============================================================
# SHARED PROVIDER INSTANCE
# ============================================================

jamendo_provider = (
    JamendoProvider()
)