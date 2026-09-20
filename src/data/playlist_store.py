from pathlib import Path
import random
import json


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()
PLAYLISTS_FILE = Path.home() / ".lyrx" / "playlists.json"


# ============================================================
# DEFAULT MUSIC QUEUE
# ============================================================

DEFAULT_QUEUE = [
    (
        "assets/album_art/believer.jpg",
        "Believer",
        "Imagine Dragons",
    ),
    (
        "assets/album_art/faded.jpg",
        "Faded",
        "Alan Walker",
    ),
    (
        "assets/album_art/arcade.jpg",
        "Arcade",
        "Duncan Laurence",
    ),
    (
        "assets/album_art/lethergo.jpg",
        "Let Her Go",
        "Passenger",
    ),
]


# ============================================================
# DEFAULT PLAYLISTS
# ============================================================

DEFAULT_PLAYLISTS = [
    {
        "id": "daily_mix",
        "name": "Daily Mix",
        "description": "Your everyday favorites",
        "songs": [
            {
                "image": "assets/album_art/believer.jpg",
                "title": "Believer",
                "artist": "Imagine Dragons",
            },
            {
                "image": "assets/album_art/faded.jpg",
                "title": "Faded",
                "artist": "Alan Walker",
            },
            {
                "image": "assets/album_art/arcade.jpg",
                "title": "Arcade",
                "artist": "Duncan Laurence",
            },
        ],
        "thumbnail": "assets/album_art/believer.jpg",
    },
    {
        "id": "late_night",
        "name": "Late Night",
        "description": "Music for quiet nights",
        "songs": [
            {
                "image": "assets/album_art/faded.jpg",
                "title": "Faded",
                "artist": "Alan Walker",
            },
            {
                "image": "assets/album_art/lethergo.jpg",
                "title": "Let Her Go",
                "artist": "Passenger",
            },
        ],
        "thumbnail": "assets/album_art/faded.jpg",
    },
    {
        "id": "emotional",
        "name": "Emotional",
        "description": "Songs that hit different",
        "songs": [
            {
                "image": "assets/album_art/arcade.jpg",
                "title": "Arcade",
                "artist": "Duncan Laurence",
            },
            {
                "image": "assets/album_art/lethergo.jpg",
                "title": "Let Her Go",
                "artist": "Passenger",
            },
        ],
        "thumbnail": "assets/album_art/arcade.jpg",
    },
]


# ============================================================
# SHARED PLAYLIST STORE
# ============================================================

class PlaylistStore:
    """
    Shared in-memory playlist manager.

    HomeScreen and PlaylistScreen both use the same store.

    This means:
        Home -> Add song
        PlaylistScreen -> instantly sees updated playlist
    """

    def __init__(self):
        self.playlists = []
        if not self.load():
            self.reset()
            self.save()

    # ========================================================
    # PERSISTENCE
    # ========================================================

    def load(self):
        try:
            if not PLAYLISTS_FILE.exists():
                return False
            data = json.loads(PLAYLISTS_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return False
            self.playlists = [
                item for item in data
                if isinstance(item, dict) and item.get("id")
            ]
            return bool(self.playlists)
        except Exception as error:
            print("Playlist load error:", error)
            return False

    def save(self):
        try:
            PLAYLISTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            PLAYLISTS_FILE.write_text(
                json.dumps(self.playlists, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
        except Exception as error:
            print("Playlist save error:", error)
            return False

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.playlists = []

        for playlist in DEFAULT_PLAYLISTS:

            copied_playlist = {
                "id": playlist.get("id"),
                "name": playlist.get("name"),
                "description": playlist.get(
                    "description",
                    ""
                ),
                "thumbnail": playlist.get(
                    "thumbnail",
                    ""
                ),
                "songs": [],
            }

            for song in playlist.get(
                "songs",
                []
            ):

                copied_playlist["songs"].append(
                    dict(song)
                )

            self.playlists.append(
                copied_playlist
            )

    # ========================================================
    # GET ALL
    # ========================================================

    def get_playlists(self):

        return self.playlists

    # ========================================================
    # FIND
    # ========================================================

    def get_playlist(
        self,
        playlist_id
    ):

        playlist_id = str(
            playlist_id
        )

        for playlist in self.playlists:

            if str(
                playlist.get("id", "")
            ) == playlist_id:

                return playlist

        return None

    # ========================================================
    # SONG COUNT
    # ========================================================

    def song_count(
        self,
        playlist
    ):

        if not playlist:

            return 0

        return len(
            playlist.get(
                "songs",
                []
            )
        )

    # ========================================================
    # SONG KEY
    # ========================================================

    @staticmethod
    def song_key(song):

        return (
            str(
                song.get(
                    "image",
                    ""
                )
            ),
            str(
                song.get(
                    "title",
                    ""
                )
            ).strip().lower(),
            str(
                song.get(
                    "artist",
                    ""
                )
            ).strip().lower(),
        )

    # ========================================================
    # CONVERT TUPLE -> DICT
    # ========================================================

    @staticmethod
    def song_from_tuple(
        image_path,
        title,
        artist,
        **metadata
    ):
        song = {
            "image": str(image_path or ""),
            "title": str(title or "Unknown"),
            "artist": str(artist or "Unknown Artist"),
        }

        # Keep real provider playback metadata with the playlist entry.
        for key in (
            "id",
            "audio_url",
            "preview_url",
            "image_url",
            "provider",
            "source",
            "duration",
            "share_url",
            "web_url",
        ):
            value = metadata.get(key)
            if value not in (None, ""):
                song[key] = value

        return song

    # ========================================================
    # CONVERT DICT -> TUPLE
    # ========================================================

    @staticmethod
    def song_to_tuple(song):

        return (
            song.get(
                "image",
                ""
            ),
            song.get(
                "title",
                "Unknown"
            ),
            song.get(
                "artist",
                "Unknown Artist"
            ),
        )

    # ========================================================
    # ADD SONG
    # ========================================================

    def add_song(
        self,
        playlist_id,
        image_path,
        title,
        artist,
        **metadata
    ):

        playlist = self.get_playlist(
            playlist_id
        )

        if playlist is None:

            return False, "Playlist not found."

        song = self.song_from_tuple(
            image_path,
            title,
            artist,
            **metadata
        )

        new_key = self.song_key(
            song
        )

        # ----------------------------------------------------
        # DUPLICATE CHECK
        # ----------------------------------------------------

        for existing_song in playlist.get(
            "songs",
            []
        ):

            if self.song_key(
                existing_song
            ) == new_key:

                return (
                    False,
                    f'"{title}" is already in this playlist.'
                )

        # ----------------------------------------------------
        # ADD
        # ----------------------------------------------------

        playlist.setdefault(
            "songs",
            []
        ).append(
            song
        )

        # ----------------------------------------------------
        # THUMBNAIL
        # ----------------------------------------------------

        if not playlist.get(
            "thumbnail"
        ):

            playlist["thumbnail"] = image_path

        self.save()
        return (
            True,
            f'"{title}" added to "{playlist.get("name", "Playlist")}".'
        )

    # ========================================================
    # REMOVE SONG
    # ========================================================

    def remove_song(
        self,
        playlist_id,
        song_index
    ):

        playlist = self.get_playlist(
            playlist_id
        )

        if playlist is None:

            return None

        songs = playlist.get(
            "songs",
            []
        )

        if (
            song_index < 0
            or
            song_index >= len(songs)
        ):

            return None

        removed = songs.pop(
            song_index
        )
        self.save()

        # ----------------------------------------------------
        # UPDATE THUMBNAIL
        # ----------------------------------------------------

        if songs:

            playlist["thumbnail"] = songs[0].get(
                "image",
                playlist.get(
                    "thumbnail",
                    ""
                )
            )

        return removed

    # ========================================================
    # CREATE PLAYLIST
    # ========================================================

    def create_playlist(
        self,
        name,
        description=""
    ):

        name = str(
            name
        ).strip()

        description = str(
            description
        ).strip()

        if not name:

            return None

        # ----------------------------------------------------
        # DUPLICATE NAME CHECK
        # ----------------------------------------------------

        for playlist in self.playlists:

            if (
                playlist.get(
                    "name",
                    ""
                ).strip().lower()
                ==
                name.lower()
            ):

                return None

        # ----------------------------------------------------
        # ID
        # ----------------------------------------------------

        playlist_id = (
            "playlist_"
            f"{len(self.playlists) + 1}_"
            f"{random.randint(1000, 9999)}"
        )

        playlist = {
            "id": playlist_id,
            "name": name,
            "description": (
                description
                if description
                else "Your new playlist"
            ),
            "songs": [],
            "thumbnail": "",
        }

        self.playlists.append(
            playlist
        )
        self.save()

        return playlist

    # ========================================================
    # DELETE PLAYLIST
    # ========================================================

    def delete_playlist(
        self,
        playlist_id
    ):

        playlist_id = str(
            playlist_id
        )

        for index, playlist in enumerate(
            self.playlists
        ):

            if str(
                playlist.get(
                    "id",
                    ""
                )
            ) == playlist_id:

                removed = self.playlists.pop(index)
                self.save()
                return removed

        return None

    # ========================================================
    # PLAYLIST QUEUE
    # ========================================================

    def playlist_queue(
        self,
        playlist_id
    ):

        playlist = self.get_playlist(
            playlist_id
        )

        if playlist is None:

            return []

        return [
            dict(song)
            for song in playlist.get(
                "songs",
                []
            )
            if isinstance(song, dict)
        ]


# ============================================================
# SINGLE SHARED INSTANCE
# ============================================================

playlist_store = PlaylistStore()