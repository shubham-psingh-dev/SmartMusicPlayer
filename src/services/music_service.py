import os

import requests

from dotenv import load_dotenv

from models.song import Song


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# MUSIC SERVICE
# ============================================================

class MusicService:
    """
    LYRx online music service.

    Day 19 Phase 1:
        Jamendo-backed online catalog.

    Later this class can support:
        - multiple providers
        - recommendations
        - charts
        - caching
        - user history
        - AI music search
    """

    # ========================================================
    # JAMENDO
    # ========================================================

    JAMENDO_BASE_URL = (
        "https://api.jamendo.com/v3.0"
    )

    def __init__(self):

        # ----------------------------------------------------
        # CLIENT ID
        # ----------------------------------------------------

        self.client_id = (
            os.getenv(
                "JAMENDO_CLIENT_ID",
                ""
            )
            .strip()
        )

        # ----------------------------------------------------
        # SESSION
        # ----------------------------------------------------

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent":
                    "LYRx-Music-Player/0.2"
            }
        )

        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        self.timeout = 15

    # ========================================================
    # AVAILABLE
    # ========================================================

    def is_configured(self):

        return bool(
            self.client_id
        )

    # ========================================================
    # REQUEST
    # ========================================================

    def _get(
        self,
        endpoint,
        params=None
    ):

        if not self.client_id:

            raise RuntimeError(
                "JAMENDO_CLIENT_ID is missing."
            )

        if params is None:

            params = {}

        # ----------------------------------------------------
        # COMMON PARAMETERS
        # ----------------------------------------------------

        params = dict(
            params
        )

        params["client_id"] = (
            self.client_id
        )

        params["format"] = "json"

        # ----------------------------------------------------
        # REQUEST
        # ----------------------------------------------------

        url = (
            f"{self.JAMENDO_BASE_URL}"
            f"/{endpoint}"
        )

        response = self.session.get(

            url,

            params=params,

            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        # ----------------------------------------------------
        # API ERROR
        # ----------------------------------------------------

        headers = data.get(
            "headers",
            {}
        )

        status = str(
            headers.get(
                "status",
                ""
            )
        )

        if (
            status
            and
            status != "success"
        ):

            error_message = (
                headers.get(
                    "error_message"
                )
                or
                "Jamendo API request failed."
            )

            raise RuntimeError(
                error_message
            )

        return data

    # ========================================================
    # NORMALIZE JAMENDO SONG
    # ========================================================

    @staticmethod
    def _song_from_jamendo(
        item
    ):

        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        downloadable = bool(
            item.get(
                "audiodownload_allowed",
                False
            )
        )

        download_url = ""

        if downloadable:

            download_url = (
                item.get(
                    "audiodownload",
                    ""
                )
                or ""
            )

        # ----------------------------------------------------
        # ALBUM
        # ----------------------------------------------------

        album = (

            item.get(
                "album_name"
            )

            or

            item.get(
                "album"
            )

            or

            ""
        )

        # ----------------------------------------------------
        # COVER
        # ----------------------------------------------------

        image_url = (
            item.get(
                "image",
                ""
            )
            or
            item.get(
                "album_image",
                ""
            )
            or
            ""
        )

        # ----------------------------------------------------
        # AUDIO
        # ----------------------------------------------------

        audio_url = (
            item.get(
                "audio",
                ""
            )
            or ""
        )

        # ----------------------------------------------------
        # SHARE URL
        # ----------------------------------------------------

        share_url = (
            item.get(
                "shareurl",
                ""
            )
            or ""
        )

        # ----------------------------------------------------
        # DURATION
        # ----------------------------------------------------

        try:

            duration = int(
                item.get(
                    "duration",
                    0
                )
                or 0
            )

        except (
            ValueError,
            TypeError
        ):

            duration = 0

        # ----------------------------------------------------
        # MODEL
        # ----------------------------------------------------

        return Song(

            id=str(
                item.get(
                    "id",
                    ""
                )
            ),

            title=str(
                item.get(
                    "name",
                    "Unknown Track"
                )
            ),

            artist=str(
                item.get(
                    "artist_name",
                    "Unknown Artist"
                )
            ),

            album=str(
                album
            ),

            image_url=str(
                image_url
            ),

            audio_url=str(
                audio_url
            ),

            duration=duration,

            source="jamendo",

            downloadable=downloadable,

            download_url=str(
                download_url
            ),

            share_url=str(
                share_url
            ),
        )

    # ========================================================
    # PARSE
    # ========================================================

    def _parse_tracks(
        self,
        data
    ):

        songs = []

        results = data.get(
            "results",
            []
        )

        if not isinstance(
            results,
            list
        ):

            return songs

        for item in results:

            if not isinstance(
                item,
                dict
            ):

                continue

            song = (
                self._song_from_jamendo(
                    item
                )
            )

            # ------------------------------------------------
            # IMPORTANT
            # ------------------------------------------------
            #
            # LYRx only wants tracks that have a playable
            # online audio URL.
            #

            if not song.audio_url:

                continue

            songs.append(
                song
            )

        return songs

    # ========================================================
    # SEARCH TRACKS
    # ========================================================

    def search_tracks(
        self,
        query,
        limit=20
    ):

        query = str(
            query
        ).strip()

        if not query:

            return []

        limit = max(
            1,
            min(
                int(limit),
                50
            )
        )

        data = self._get(

            "tracks/",

            {

                "limit": limit,

                "search": query,

                "include":
                    "musicinfo",

                "audioformat":
                    "mp32",

            }
        )

        return self._parse_tracks(
            data
        )

    # ========================================================
    # POPULAR TRACKS
    # ========================================================

    def get_popular_tracks(
        self,
        limit=20
    ):

        limit = max(
            1,
            min(
                int(limit),
                50
            )
        )

        data = self._get(

            "tracks/",

            {

                "limit": limit,

                "order":
                    "popularity_total",

                "include":
                    "musicinfo",

                "audioformat":
                    "mp32",

            }
        )

        return self._parse_tracks(
            data
        )

    # ========================================================
    # TRENDING / RECENT POPULAR
    # ========================================================

    def get_trending_tracks(
        self,
        limit=20
    ):

        limit = max(
            1,
            min(
                int(limit),
                50
            )
        )

        data = self._get(

            "tracks/",

            {

                "limit": limit,

                "order":
                    "popularity_week",

                "include":
                    "musicinfo",

                "audioformat":
                    "mp32",

            }
        )

        return self._parse_tracks(
            data
        )

    # ========================================================
    # TRACK
    # ========================================================

    def get_track(
        self,
        track_id
    ):

        track_id = str(
            track_id
        ).strip()

        if not track_id:

            return None

        data = self._get(

            "tracks/",

            {

                "id": track_id,

                "limit": 1,

                "include":
                    "musicinfo",

                "audioformat":
                    "mp32",

            }
        )

        songs = self._parse_tracks(
            data
        )

        if not songs:

            return None

        return songs[0]

    # ========================================================
    # SAFE SEARCH
    # ========================================================

    def safe_search_tracks(
        self,
        query,
        limit=20
    ):

        try:

            return (
                self.search_tracks(
                    query,
                    limit
                )
            )

        except Exception as error:

            print(
                "MusicService search error:",
                error
            )

            return []

    # ========================================================
    # SAFE POPULAR
    # ========================================================

    def safe_popular_tracks(
        self,
        limit=20
    ):

        try:

            return (
                self.get_popular_tracks(
                    limit
                )
            )

        except Exception as error:

            print(
                "MusicService popular error:",
                error
            )

            return []

    # ========================================================
    # SAFE TRENDING
    # ========================================================

    def safe_trending_tracks(
        self,
        limit=20
    ):

        try:

            return (
                self.get_trending_tracks(
                    limit
                )
            )

        except Exception as error:

            print(
                "MusicService trending error:",
                error
            )

            return []


# ============================================================
# SHARED INSTANCE
# ============================================================

music_service = MusicService()