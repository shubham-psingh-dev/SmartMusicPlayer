import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()

PROJECT_DIR = FILE_DIR.parents[2]

USER_DATA_DIR = (
    PROJECT_DIR
    / "user_data"
)

FAVORITES_FILE = (
    USER_DATA_DIR
    / "youtube_favorites.json"
)


# ============================================================
# YOUTUBE FAVORITES STORE
# ============================================================

class YouTubeFavoritesStore:

    def __init__(self):

        USER_DATA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        self.ensure_file()

    # ========================================================
    # ENSURE FILE
    # ========================================================

    def ensure_file(self):

        if FAVORITES_FILE.exists():

            return

        try:

            with open(
                FAVORITES_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    [],
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as error:

            print(
                "YT favorites create error:",
                error
            )

    # ========================================================
    # TRACK -> DICT
    # ========================================================

    def track_to_dict(
        self,
        track
    ):

        if track is None:

            return None

        if isinstance(
            track,
            dict
        ):

            data = dict(
                track
            )

        else:

            data = {

                "video_id":
                    str(
                        getattr(
                            track,
                            "video_id",
                            ""
                        )
                        or ""
                    ),

                "title":
                    str(
                        getattr(
                            track,
                            "title",
                            ""
                        )
                        or "YouTube Track"
                    ),

                "channel":
                    str(
                        getattr(
                            track,
                            "channel",
                            ""
                        )
                        or "YouTube"
                    ),

                "thumbnail_url":
                    str(
                        getattr(
                            track,
                            "thumbnail_url",
                            ""
                        )
                        or ""
                    ),

                "duration":
                    int(
                        getattr(
                            track,
                            "duration",
                            0
                        )
                        or 0
                    ),

                "webpage_url":
                    str(
                        getattr(
                            track,
                            "webpage_url",
                            ""
                        )
                        or ""
                    ),

                "source":
                    "youtube",
            }

            # --------------------------------------------
            # URL fallback
            # --------------------------------------------

            if not data[
                "webpage_url"
            ]:

                try:

                    if hasattr(
                        track,
                        "youtube_url"
                    ):

                        data[
                            "webpage_url"
                        ] = str(
                            track.youtube_url()
                            or ""
                        )

                except Exception:

                    pass

        video_id = str(
            data.get(
                "video_id",
                ""
            )
            or ""
        ).strip()

        webpage_url = str(
            data.get(
                "webpage_url",
                ""
            )
            or ""
        ).strip()

        if (
            not webpage_url
            and video_id
        ):

            webpage_url = (
                "https://www.youtube.com/watch?v="
                + video_id
            )

        if not video_id:

            # Try obtaining ID from URL
            if "v=" in webpage_url:

                video_id = (
                    webpage_url
                    .split("v=", 1)[1]
                    .split("&", 1)[0]
                )

        if not video_id:

            return None

        try:

            duration = int(
                data.get(
                    "duration",
                    0
                )
                or 0
            )

        except Exception:

            duration = 0

        return {

            "video_id":
                video_id,

            "title":
                str(
                    data.get(
                        "title",
                        ""
                    )
                    or "YouTube Track"
                ),

            "channel":
                str(
                    data.get(
                        "channel",
                        ""
                    )
                    or "YouTube"
                ),

            "thumbnail_url":
                str(
                    data.get(
                        "thumbnail_url",
                        ""
                    )
                    or ""
                ),

            "duration":
                duration,

            "webpage_url":
                webpage_url,

            "source":
                "youtube",
        }

    # ========================================================
    # LOAD
    # ========================================================

    def get_favorites(self):

        self.ensure_file()

        try:

            with open(
                FAVORITES_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if not isinstance(
                data,
                list
            ):

                return []

            return [

                item

                for item in data

                if isinstance(
                    item,
                    dict
                )
            ]

        except Exception as error:

            print(
                "YT favorites load error:",
                error
            )

            return []

    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        items
    ):

        try:

            USER_DATA_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(
                FAVORITES_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    items,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except Exception as error:

            print(
                "YT favorites save error:",
                error
            )

            return False

    # ========================================================
    # IS FAVORITE
    # ========================================================

    def is_favorite(
        self,
        track
    ):

        item = (
            self.track_to_dict(
                track
            )
        )

        if item is None:

            return False

        video_id = item[
            "video_id"
        ]

        for favorite in (
            self.get_favorites()
        ):

            if str(
                favorite.get(
                    "video_id",
                    ""
                )
            ) == video_id:

                return True

        return False

    # ========================================================
    # ADD
    # ========================================================

    def add(
        self,
        track
    ):

        item = (
            self.track_to_dict(
                track
            )
        )

        if item is None:

            print(
                "YT favorite invalid track"
            )

            return False

        favorites = (
            self.get_favorites()
        )

        video_id = item[
            "video_id"
        ]

        for favorite in favorites:

            if str(
                favorite.get(
                    "video_id",
                    ""
                )
            ) == video_id:

                return True

        favorites.append(
            item
        )

        saved = (
            self.save(
                favorites
            )
        )

        if saved:

            print(
                "YT Favorite added:",
                item[
                    "title"
                ]
            )

        return saved

    # ========================================================
    # REMOVE
    # ========================================================

    def remove(
        self,
        track
    ):

        item = (
            self.track_to_dict(
                track
            )
        )

        if item is None:

            return False

        video_id = item[
            "video_id"
        ]

        favorites = [

            favorite

            for favorite
            in self.get_favorites()

            if str(
                favorite.get(
                    "video_id",
                    ""
                )
            )
            !=
            video_id
        ]

        saved = (
            self.save(
                favorites
            )
        )

        if saved:

            print(
                "YT Favorite removed:",
                item[
                    "title"
                ]
            )

        return saved

    # ========================================================
    # TOGGLE
    # ========================================================

    def toggle(
        self,
        track
    ):

        if self.is_favorite(
            track
        ):

            self.remove(
                track
            )

            return False

        self.add(
            track
        )

        return True


# ============================================================
# SHARED INSTANCE
# ============================================================

youtube_favorites_store = (
    YouTubeFavoritesStore()
)