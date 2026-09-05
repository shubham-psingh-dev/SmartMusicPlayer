# ============================================================
# LYRx
# DAY 22 - YT BOX
#
# FILE 1
# youtube_service.py
#
# PURPOSE
# ------------------------------------------------------------
#
# YouTube discovery/search metadata service for LYRx.
#
# FEATURES
# ------------------------------------------------------------
#
#   - YouTube metadata search
#   - Title
#   - Channel / artist
#   - Duration
#   - Video ID
#   - Official YouTube URL
#   - Reliable thumbnail fallback URLs
#   - Favorites / Playlists metadata support
#   - Day 22 playback capability metadata
#
# IMPORTANT
# ------------------------------------------------------------
#
# yt-dlp is used here only for search/catalog metadata.
#
# This service does NOT download media files and does NOT
# resolve direct copyrighted media stream URLs.
# ============================================================

from __future__ import annotations

from dataclasses import (
    dataclass,
    asdict,
)

import re
import webbrowser

from typing import (
    List,
    Optional,
)

import yt_dlp


# ============================================================
# YOUTUBE CONSTANTS
# ============================================================

YOUTUBE_WATCH_BASE = (
    "https://www.youtube.com/watch?v="
)

YOUTUBE_THUMB_BASE = (
    "https://i.ytimg.com/vi/"
)


# ============================================================
# YOUTUBE TRACK MODEL
# ============================================================

@dataclass
class YouTubeTrack:

    # --------------------------------------------------------
    # IDENTIFICATION
    # --------------------------------------------------------

    video_id: str

    title: str

    channel: str = ""

    # --------------------------------------------------------
    # MEDIA INFORMATION
    # --------------------------------------------------------

    thumbnail_url: str = ""

    duration: int = 0

    # --------------------------------------------------------
    # LINKS
    # --------------------------------------------------------

    webpage_url: str = ""

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    source: str = "youtube"

    provider: str = "youtube"

    # --------------------------------------------------------
    # DAY 22 PLAYBACK METADATA
    # --------------------------------------------------------
    #
    # Current stable route:
    #
    #     official_external
    #
    # Tracks returned by search can later be attempted with an
    # official embedded playback route:
    #
    #     official_embed_candidate
    #
    # --------------------------------------------------------

    playback_mode: str = (
        "official_external"
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

        return "Unknown Video"

    # ========================================================
    # DISPLAY ARTIST
    # ========================================================

    def display_artist(
        self
    ) -> str:

        channel = str(
            self.channel
            or ""
        ).strip()

        if channel:

            return channel

        return "YouTube"

    # ========================================================
    # DURATION TEXT
    # ========================================================

    def duration_text(
        self
    ) -> str:

        try:

            seconds = int(
                self.duration
                or 0
            )

        except (
            TypeError,
            ValueError,
        ):

            seconds = 0

        if seconds <= 0:

            return "0:00"

        minutes = (
            seconds
            //
            60
        )

        remaining = (
            seconds
            %
            60
        )

        return (
            f"{minutes}:"
            f"{remaining:02d}"
        )

    # ========================================================
    # YOUTUBE URL
    # ========================================================

    def youtube_url(
        self
    ) -> str:

        webpage_url = str(
            self.webpage_url
            or ""
        ).strip()

        if webpage_url.startswith(
            (
                "http://",
                "https://",
            )
        ):

            return webpage_url

        video_id = str(
            self.video_id
            or ""
        ).strip()

        if video_id:

            return (
                YOUTUBE_WATCH_BASE
                +
                video_id
            )

        return ""

    # ========================================================
    # THUMBNAIL CANDIDATES
    # ========================================================

    def thumbnail_candidates(
        self
    ) -> List[str]:

        """
        Returns thumbnails in fallback order.

        Example:

            metadata thumbnail
            maxresdefault
            hqdefault
            mqdefault
            default
        """

        candidates = []

        current_thumbnail = str(
            self.thumbnail_url
            or ""
        ).strip()

        if current_thumbnail:

            candidates.append(
                current_thumbnail
            )

        video_id = str(
            self.video_id
            or ""
        ).strip()

        if video_id:

            names = (

                "maxresdefault.jpg",

                "hqdefault.jpg",

                "mqdefault.jpg",

                "default.jpg",
            )

            for name in names:

                url = (
                    YOUTUBE_THUMB_BASE
                    +
                    video_id
                    +
                    "/"
                    +
                    name
                )

                if url not in candidates:

                    candidates.append(
                        url
                    )

        return candidates

    # ========================================================
    # UNIQUE KEY
    # ========================================================

    def unique_key(
        self
    ):

        return (

            "youtube",

            str(
                self.video_id
                or ""
            ),
        )

    # ========================================================
    # DICTIONARY
    # ========================================================

    def to_dict(
        self
    ):

        return asdict(
            self
        )

    # ========================================================
    # FROM DICTIONARY
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data
    ):

        if not isinstance(
            data,
            dict
        ):

            return cls(

                video_id="",

                title=(
                    "Unknown Video"
                ),
            )

        # ----------------------------------------------------
        # DURATION
        # ----------------------------------------------------

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
            ValueError,
        ):

            duration = 0

        # ----------------------------------------------------
        # OBJECT
        # ----------------------------------------------------

        return cls(

            video_id=str(
                data.get(
                    "video_id",
                    ""
                )
                or ""
            ).strip(),

            title=str(
                data.get(
                    "title",
                    "Unknown Video"
                )
                or
                "Unknown Video"
            ).strip(),

            channel=str(
                data.get(
                    "channel",
                    ""
                )
                or ""
            ).strip(),

            thumbnail_url=str(
                data.get(
                    "thumbnail_url",
                    ""
                )
                or ""
            ).strip(),

            duration=duration,

            webpage_url=str(
                data.get(
                    "webpage_url",
                    ""
                )
                or ""
            ).strip(),

            source=str(
                data.get(
                    "source",
                    "youtube"
                )
                or
                "youtube"
            ).strip(),

            provider=str(
                data.get(
                    "provider",
                    "youtube"
                )
                or
                "youtube"
            ).strip(),

            playback_mode=str(
                data.get(
                    "playback_mode",
                    "official_external"
                )
                or
                "official_external"
            ).strip(),
        )


# ============================================================
# YOUTUBE SERVICE
# ============================================================

class YouTubeService:

    """
    LYRx YouTube metadata/search service.

    yt-dlp configuration:

        skip_download=True
        extract_flat=True

    So search remains metadata-only.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self
    ):

        self.last_error = ""

    # ========================================================
    # ERROR
    # ========================================================

    def clear_error(
        self
    ):

        self.last_error = ""

    # --------------------------------------------------------

    def set_error(
        self,
        error
    ):

        self.last_error = str(
            error
            or ""
        )

    # ========================================================
    # YT-DLP OPTIONS
    # ========================================================

    def _ydl_options(
        self
    ):

        return {

            # ------------------------------------------------
            # METADATA ONLY
            # ------------------------------------------------

            "skip_download":
                True,

            "extract_flat":
                True,

            # ------------------------------------------------
            # TERMINAL
            # ------------------------------------------------

            "quiet":
                True,

            "no_warnings":
                True,

            # ------------------------------------------------
            # FILE CREATION DISABLED
            # ------------------------------------------------

            "writeinfojson":
                False,

            "writethumbnail":
                False,

            "writesubtitles":
                False,

            "writeautomaticsub":
                False,

            # ------------------------------------------------
            # SEARCH RESILIENCE
            # ------------------------------------------------

            "ignoreerrors":
                True,

            # ------------------------------------------------
            # RESULT SHOULD BE A SINGLE VIDEO REFERENCE
            # ------------------------------------------------

            "noplaylist":
                True,
        }

    # ========================================================
    # NORMALIZE LIMIT
    # ========================================================

    @staticmethod
    def _normalize_limit(
        limit
    ) -> int:

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError,
        ):

            limit = 10

        return max(

            1,

            min(
                limit,
                30
            )
        )

    # ========================================================
    # NORMALIZE VIDEO ID
    # ========================================================

    @staticmethod
    def normalize_video_id(
        value
    ) -> str:

        """
        Accepts:

            Umqb9KENgmk

            https://youtube.com/watch?v=Umqb9KENgmk

            https://youtu.be/Umqb9KENgmk

            /shorts/...
            /embed/...
            /live/...
        """

        value = str(
            value
            or ""
        ).strip()

        if not value:

            return ""

        # ----------------------------------------------------
        # RAW VIDEO ID
        # ----------------------------------------------------

        if re.fullmatch(
            r"[A-Za-z0-9_-]{6,20}",
            value
        ):

            return value

        # ----------------------------------------------------
        # WATCH URL
        # ----------------------------------------------------

        watch_match = re.search(

            r"(?:[?&]v=)"
            r"([A-Za-z0-9_-]{6,20})",

            value,
        )

        if watch_match:

            return (
                watch_match.group(
                    1
                )
            )

        # ----------------------------------------------------
        # SHORT / EMBED / LIVE
        # ----------------------------------------------------

        path_match = re.search(

            r"(?:youtu\.be/|embed/|shorts/|live/)"
            r"([A-Za-z0-9_-]{6,20})",

            value,
        )

        if path_match:

            return (
                path_match.group(
                    1
                )
            )

        return ""

    # ========================================================
    # BUILD WATCH URL
    # ========================================================

    @classmethod
    def build_watch_url(
        cls,
        video_id
    ) -> str:

        video_id = (
            cls.normalize_video_id(
                video_id
            )
        )

        if not video_id:

            return ""

        return (
            YOUTUBE_WATCH_BASE
            +
            video_id
        )

    # ========================================================
    # BUILD THUMBNAIL
    # ========================================================

    @classmethod
    def build_thumbnail_url(
        cls,
        video_id,
        quality="hqdefault"
    ) -> str:

        video_id = (
            cls.normalize_video_id(
                video_id
            )
        )

        if not video_id:

            return ""

        allowed_quality = {

            "maxresdefault",

            "hqdefault",

            "mqdefault",

            "default",
        }

        quality = str(
            quality
            or
            "hqdefault"
        ).strip()

        if quality not in allowed_quality:

            quality = (
                "hqdefault"
            )

        return (

            YOUTUBE_THUMB_BASE

            +

            video_id

            +

            "/"

            +

            quality

            +

            ".jpg"
        )

    # ========================================================
    # GET THUMBNAIL FROM ENTRY
    # ========================================================

    def _thumbnail_from_entry(
        self,
        entry,
        video_id
    ) -> str:

        # ----------------------------------------------------
        # DIRECT THUMBNAIL
        # ----------------------------------------------------

        thumbnail_url = str(
            entry.get(
                "thumbnail",
                ""
            )
            or ""
        ).strip()

        if thumbnail_url.startswith(
            (
                "http://",
                "https://",
            )
        ):

            return thumbnail_url

        # ----------------------------------------------------
        # THUMBNAILS ARRAY
        # ----------------------------------------------------

        thumbnails = (
            entry.get(
                "thumbnails",
                []
            )
            or []
        )

        if isinstance(
            thumbnails,
            list
        ):

            # Usually later entries are larger/better.

            for thumbnail in reversed(
                thumbnails
            ):

                if not isinstance(
                    thumbnail,
                    dict
                ):

                    continue

                candidate = str(
                    thumbnail.get(
                        "url",
                        ""
                    )
                    or ""
                ).strip()

                if candidate.startswith(
                    (
                        "http://",
                        "https://",
                    )
                ):

                    return candidate

        # ----------------------------------------------------
        # DETERMINISTIC FALLBACK
        # ----------------------------------------------------

        return (
            self.build_thumbnail_url(
                video_id,
                "hqdefault"
            )
        )

    # ========================================================
    # BUILD TRACK
    # ========================================================

    def _track_from_entry(
        self,
        entry
    ) -> Optional[YouTubeTrack]:

        if not isinstance(
            entry,
            dict
        ):

            return None

        # ====================================================
        # VIDEO ID
        # ====================================================

        video_id = (
            self.normalize_video_id(
                entry.get(
                    "id",
                    ""
                )
            )
        )

        # ----------------------------------------------------
        # Some flat results may expose ID in url.
        # ----------------------------------------------------

        if not video_id:

            video_id = (
                self.normalize_video_id(
                    entry.get(
                        "url",
                        ""
                    )
                )
            )

        if not video_id:

            return None

        # ====================================================
        # TITLE
        # ====================================================

        title = str(
            entry.get(
                "title",
                ""
            )
            or ""
        ).strip()

        if not title:

            title = (
                "YouTube Video"
            )

        # ====================================================
        # CHANNEL / ARTIST
        # ====================================================

        channel = str(

            entry.get(
                "channel",
                ""
            )

            or

            entry.get(
                "uploader",
                ""
            )

            or

            entry.get(
                "channel_name",
                ""
            )

            or

            ""

        ).strip()

        # ====================================================
        # DURATION
        # ====================================================

        try:

            duration = int(
                entry.get(
                    "duration",
                    0
                )
                or 0
            )

        except (
            TypeError,
            ValueError,
        ):

            duration = 0

        # ====================================================
        # THUMBNAIL
        # ====================================================

        thumbnail_url = (
            self._thumbnail_from_entry(

                entry,

                video_id,
            )
        )

        # ====================================================
        # OFFICIAL WEBPAGE URL
        # ====================================================

        webpage_url = str(
            entry.get(
                "webpage_url",
                ""
            )
            or ""
        ).strip()

        if not webpage_url.startswith(
            (
                "http://",
                "https://",
            )
        ):

            webpage_url = (
                self.build_watch_url(
                    video_id
                )
            )

        # ====================================================
        # TRACK
        # ====================================================

        return YouTubeTrack(

            video_id=video_id,

            title=title,

            channel=channel,

            thumbnail_url=thumbnail_url,

            duration=duration,

            webpage_url=webpage_url,

            source="youtube",

            provider="youtube",

            playback_mode=(
                "official_embed_candidate"
            ),
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> List[YouTubeTrack]:

        query = str(
            query
            or ""
        ).strip()

        if not query:

            return []

        limit = (
            self._normalize_limit(
                limit
            )
        )

        search_expression = (
            f"ytsearch{limit}:"
            f"{query}"
        )

        print()
        print("=" * 60)

        print(
            "LYRx YT BOX SEARCH"
        )

        print(
            "Query:",
            query
        )

        print(
            "Limit:",
            limit
        )

        print("=" * 60)

        try:

            with yt_dlp.YoutubeDL(
                self._ydl_options()
            ) as ydl:

                info = (
                    ydl.extract_info(

                        search_expression,

                        download=False,
                    )
                )

        except Exception as error:

            self.set_error(
                error
            )

            print(
                "YT BOX search error:",
                error
            )

            print("=" * 60)
            print()

            return []

        # ====================================================
        # RESULT ROOT
        # ====================================================

        if not isinstance(
            info,
            dict
        ):

            return []

        entries = (
            info.get(
                "entries",
                []
            )
            or []
        )

        # ====================================================
        # BUILD RESULT TRACKS
        # ====================================================

        tracks = []

        seen = set()

        for entry in entries:

            track = (
                self._track_from_entry(
                    entry
                )
            )

            if track is None:

                continue

            key = (
                track.unique_key()
            )

            if key in seen:

                continue

            seen.add(
                key
            )

            tracks.append(
                track
            )

            if (
                len(
                    tracks
                )
                >=
                limit
            ):

                break

        self.clear_error()

        # ====================================================
        # DEBUG
        # ====================================================

        print(
            "YT BOX results:",
            len(
                tracks
            )
        )

        for (
            index,
            track
        ) in enumerate(

            tracks[:5],

            start=1,
        ):

            print(
                f"{index}. "
                f"{track.title} "
                f"- "
                f"{track.channel}"
            )

        print("=" * 60)
        print()

        return tracks

    # ========================================================
    # SEARCH SONG
    # ========================================================

    def search_song(
        self,
        song_name: str,
        limit: int = 10,
    ) -> List[YouTubeTrack]:

        return self.search(

            song_name,

            limit=limit,
        )

    # ========================================================
    # SEARCH ARTIST
    # ========================================================

    def search_artist(
        self,
        artist_name: str,
        limit: int = 10,
    ) -> List[YouTubeTrack]:

        artist_name = str(
            artist_name
            or ""
        ).strip()

        if not artist_name:

            return []

        return self.search(

            f"{artist_name} songs",

            limit=limit,
        )

    # ========================================================
    # SEARCH HINDI
    # ========================================================

    def search_hindi(
        self,
        limit: int = 10,
    ) -> List[YouTubeTrack]:

        return self.search(

            "latest Hindi Bollywood songs",

            limit=limit,
        )

    # ========================================================
    # SEARCH ENGLISH
    # ========================================================

    def search_english(
        self,
        limit: int = 10,
    ) -> List[YouTubeTrack]:

        return self.search(

            "latest English songs",

            limit=limit,
        )

    # ========================================================
    # OFFICIAL EMBED CAPABILITY
    # ========================================================

    @staticmethod
    def can_attempt_official_embed(
        track: YouTubeTrack
    ) -> bool:

        if track is None:

            return False

        video_id = str(
            getattr(
                track,
                "video_id",
                ""
            )
            or ""
        ).strip()

        return bool(
            video_id
        )

    # ========================================================
    # OPEN TRACK
    # ========================================================

    @staticmethod
    def open_track(
        track: YouTubeTrack
    ) -> bool:

        """
        Stable browser fallback.

        Day 22 internal playback routing will be handled
        separately from this metadata service.
        """

        if track is None:

            return False

        url = (
            track.youtube_url()
        )

        if not url:

            return False

        try:

            webbrowser.open(
                url
            )

            return True

        except Exception as error:

            print(
                "YT BOX open error:",
                error
            )

            return False

    # ========================================================
    # DEBUG
    # ========================================================

    def print_track(
        self,
        track: YouTubeTrack
    ):

        if track is None:

            return

        print()
        print("=" * 60)

        print(
            "LYRx YT BOX TRACK"
        )

        print("=" * 60)

        print(
            "ID:",
            track.video_id
        )

        print(
            "Title:",
            track.title
        )

        print(
            "Channel:",
            track.channel
        )

        print(
            "Duration:",
            track.duration_text()
        )

        print(
            "Thumbnail:",
            track.thumbnail_url
        )

        print(
            "Thumbnail candidates:"
        )

        for thumbnail in (
            track.thumbnail_candidates()
        ):

            print(
                " -",
                thumbnail
            )

        print(
            "URL:",
            track.youtube_url()
        )

        print(
            "Playback mode:",
            track.playback_mode
        )

        print("=" * 60)
        print()


# ============================================================
# SHARED INSTANCE
# ============================================================

youtube_service = (
    YouTubeService()
)