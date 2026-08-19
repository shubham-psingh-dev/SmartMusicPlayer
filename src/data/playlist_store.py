from pathlib import Path
import random


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()


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

        self.reset()

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
        artist
    ):

        return {
            "image": image_path,
            "title": title,
            "artist": artist,
        }

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
        artist
    ):

        playlist = self.get_playlist(
            playlist_id
        )

        if playlist is None:

            return False, "Playlist not found."

        song = self.song_from_tuple(
            image_path,
            title,
            artist
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

                return self.playlists.pop(
                    index
                )

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
            self.song_to_tuple(song)
            for song in playlist.get(
                "songs",
                []
            )
        ]


# ============================================================
# SINGLE SHARED INSTANCE
# ============================================================

playlist_store = PlaylistStore()