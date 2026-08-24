from dataclasses import dataclass


@dataclass
class Song:
    """
    Unified LYRx song model.

    From Day 19 onward, UI/player modules should not care
    whether a song came from Jamendo, another provider,
    cache, search, playlist, or recommendation engine.

    They only work with Song objects.
    """

    id: str

    title: str

    artist: str

    album: str = ""

    image_url: str = ""

    audio_url: str = ""

    duration: int = 0

    source: str = "online"

    downloadable: bool = False

    download_url: str = ""

    share_url: str = ""

    # ========================================================
    # DISPLAY TITLE
    # ========================================================

    def display_title(self):

        return (
            self.title
            if self.title
            else "Unknown Track"
        )

    # ========================================================
    # DISPLAY ARTIST
    # ========================================================

    def display_artist(self):

        return (
            self.artist
            if self.artist
            else "Unknown Artist"
        )

    # ========================================================
    # DURATION TEXT
    # ========================================================

    def duration_text(self):

        if not self.duration:

            return "0:00"

        minutes = (
            self.duration // 60
        )

        seconds = (
            self.duration % 60
        )

        return (
            f"{minutes}:"
            f"{seconds:02d}"
        )

    # ========================================================
    # DICTIONARY
    # ========================================================

    def to_dict(self):

        return {

            "id": self.id,

            "title": self.title,

            "artist": self.artist,

            "album": self.album,

            "image_url": self.image_url,

            "audio_url": self.audio_url,

            "duration": self.duration,

            "source": self.source,

            "downloadable": self.downloadable,

            "download_url": self.download_url,

            "share_url": self.share_url,

        }

    # ========================================================
    # FROM DICTIONARY
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data
    ):

        return cls(

            id=str(
                data.get(
                    "id",
                    ""
                )
            ),

            title=str(
                data.get(
                    "title",
                    ""
                )
            ),

            artist=str(
                data.get(
                    "artist",
                    ""
                )
            ),

            album=str(
                data.get(
                    "album",
                    ""
                )
            ),

            image_url=str(
                data.get(
                    "image_url",
                    ""
                )
            ),

            audio_url=str(
                data.get(
                    "audio_url",
                    ""
                )
            ),

            duration=int(
                data.get(
                    "duration",
                    0
                )
                or 0
            ),

            source=str(
                data.get(
                    "source",
                    "online"
                )
            ),

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
            ),

            share_url=str(
                data.get(
                    "share_url",
                    ""
                )
            ),
        )

    # ========================================================
    # DEBUG
    # ========================================================

    def __str__(self):

        return (
            f"{self.title} "
            f"— {self.artist}"
        )