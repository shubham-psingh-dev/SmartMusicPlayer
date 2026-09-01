# ============================================================
# LYRx
# DAY 21 - YT BOX
#
# FILE 1
# youtube_service.py
#
# PURPOSE
# ------------------------------------------------------------
#
# YouTube discovery/search service for LYRx.
#
# CURRENT CAPABILITIES:
#
#   - Search YouTube dynamically
#   - Song/video title
#   - Channel / artist
#   - Thumbnail
#   - Duration
#   - Video ID
#   - Official YouTube URL
#   - Metadata ready for Favorites / Playlists
#
# IMPORTANT
# ------------------------------------------------------------
#
# This service does NOT download/extract copyrighted audio.
# yt-dlp is used only as a metadata/search resolver.
#
# Playback integration will be added separately.
# ============================================================

from __future__ import annotations

from dataclasses import (
    dataclass,
    asdict,
)

import webbrowser

from typing import (
    List,
    Optional,
)

import yt_dlp


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

    # ========================================================
    # DISPLAY TITLE
    # ========================================================

    def display_title(
        self
    ) -> str:

        return (
            self.title
            if self.title
            else "Unknown Video"
        )

    # ========================================================
    # DISPLAY ARTIST
    # ========================================================

    def display_artist(
        self
    ) -> str:

        return (
            self.channel
            if self.channel
            else "YouTube"
        )

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
            ValueError
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

        if self.webpage_url:

            return self.webpage_url

        if self.video_id:

            return (
                "https://www.youtube.com/watch?v="
                f"{self.video_id}"
            )

        return ""

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
                title="Unknown Video",
            )

        return cls(

            video_id=str(
                data.get(
                    "video_id",
                    ""
                )
                or ""
            ),

            title=str(
                data.get(
                    "title",
                    "Unknown Video"
                )
                or
                "Unknown Video"
            ),

            channel=str(
                data.get(
                    "channel",
                    ""
                )
                or ""
            ),

            thumbnail_url=str(
                data.get(
                    "thumbnail_url",
                    ""
                )
                or ""
            ),

            duration=int(
                data.get(
                    "duration",
                    0
                )
                or 0
            ),

            webpage_url=str(
                data.get(
                    "webpage_url",
                    ""
                )
                or ""
            ),

            source=str(
                data.get(
                    "source",
                    "youtube"
                )
                or
                "youtube"
            ),

            provider=str(
                data.get(
                    "provider",
                    "youtube"
                )
                or
                "youtube"
            ),
        )


# ============================================================
# YOUTUBE SERVICE
# ============================================================

class YouTubeService:

    """
    LYRx YT BOX search service.

    yt-dlp is deliberately configured with:

        skip_download=True
        extract_flat=True

    We only need catalog metadata in this phase.
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
            # Do not download media.
            # ------------------------------------------------

            "skip_download":
                True,

            # ------------------------------------------------
            # Fast metadata search.
            # ------------------------------------------------

            "extract_flat":
                True,

            # ------------------------------------------------
            # Quiet terminal.
            # ------------------------------------------------

            "quiet":
                True,

            "no_warnings":
                True,

            # ------------------------------------------------
            # Do not create files.
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
            # Ignore unavailable individual results.
            # ------------------------------------------------

            "ignoreerrors":
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
            ValueError
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

        video_id = str(
            entry.get(
                "id",
                ""
            )
            or ""
        ).strip()

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
            ValueError
        ):

            duration = 0

        # ====================================================
        # THUMBNAIL
        # ====================================================

        thumbnail_url = str(
            entry.get(
                "thumbnail",
                ""
            )
            or ""
        ).strip()

        # ----------------------------------------------------
        # Flat results may not expose thumbnail directly.
        # YouTube standard thumbnail can be derived safely
        # from the public video ID.
        # ----------------------------------------------------

        if not thumbnail_url:

            thumbnail_url = (
                "https://i.ytimg.com/vi/"
                f"{video_id}/hqdefault.jpg"
            )

        # ====================================================
        # WEBPAGE URL
        # ====================================================

        webpage_url = str(

            entry.get(
                "webpage_url",
                ""
            )

            or

            entry.get(
                "url",
                ""
            )

            or

            ""

        ).strip()

        # ----------------------------------------------------
        # extract_flat may return just the video ID as URL.
        # ----------------------------------------------------

        if (
            not webpage_url
            or
            webpage_url == video_id
            or
            not webpage_url.startswith(
                (
                    "http://",
                    "https://"
                )
            )
        ):

            webpage_url = (
                "https://www.youtube.com/watch?v="
                f"{video_id}"
            )

        # ====================================================
        # MODEL
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

        # ====================================================
        # SEARCH EXPRESSION
        # ====================================================

        search_expression = (
            f"ytsearch{limit}:{query}"
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
        # RESULTS
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
            start=1
        ):

            print(
                f"{index}. "
                f"{track.title} "
                f"- {track.channel}"
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
    # OPEN TRACK
    # ========================================================

    @staticmethod
    def open_track(
        track: YouTubeTrack
    ) -> bool:

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
            "URL:",
            track.youtube_url()
        )

        print("=" * 60)
        print()


# ============================================================
# SHARED INSTANCE
# ============================================================

youtube_service = (
    YouTubeService()
)