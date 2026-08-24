from PySide6.QtCore import (
    Qt,
    Signal,
    QThread,
    QTimer,
)

from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
)

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
)

from widgets.sidebar import Sidebar
from widgets.cards.music_card import MusicCard

from data.discover_data import (
    MOODS,
    GENRES,
)

from services.music_service import (
    MusicService,
)


# ============================================================
# ONLINE MUSIC LOADER
# ============================================================

class OnlineMusicLoader(QThread):

    songs_loaded = Signal(list)
    load_failed = Signal(str)

    def __init__(
        self,
        limit=10,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.limit = limit

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        try:

            print()
            print("=" * 60)
            print("LYRx Discover online loader started")
            print("=" * 60)

            # ==================================================
            # CREATE SERVICE INSIDE WORKER THREAD
            # ==================================================

            service = MusicService()

            print(
                "Discover Jamendo configured:",
                service.is_configured()
            )

            if not service.is_configured():

                raise RuntimeError(
                    "JAMENDO_CLIENT_ID is not configured."
                )

            songs = []

            # ==================================================
            # 1. TRENDING
            # ==================================================

            try:

                print(
                    "Discover: requesting trending tracks..."
                )

                songs = service.get_trending_tracks(
                    limit=self.limit
                )

                print(
                    "Discover trending returned:",
                    len(songs)
                )

            except Exception as error:

                print(
                    "Discover trending error:",
                    repr(error)
                )

                songs = []

            # ==================================================
            # 2. POPULAR FALLBACK
            # ==================================================

            if not songs:

                try:

                    print(
                        "Discover: requesting popular tracks..."
                    )

                    songs = service.get_popular_tracks(
                        limit=self.limit
                    )

                    print(
                        "Discover popular returned:",
                        len(songs)
                    )

                except Exception as error:

                    print(
                        "Discover popular error:",
                        repr(error)
                    )

                    songs = []

            # ==================================================
            # 3. SEARCH FALLBACK
            # ==================================================
            #
            # Jamendo can occasionally return zero results for
            # popularity orders even though the catalog itself
            # is available.
            #
            # LYRx therefore tries real catalog searches.
            # ==================================================

            if not songs:

                print(
                    "Discover: popular feeds empty."
                )

                print(
                    "Discover: starting catalog search fallback..."
                )

                search_queries = [

                    "music",
                    "love",
                    "rock",
                    "pop",
                    "chill",
                    "electronic",
                    "acoustic",
                    "dance",

                ]

                collected = []

                seen_ids = set()

                for query in search_queries:

                    # ------------------------------------------------
                    # Enough tracks already collected
                    # ------------------------------------------------

                    if len(collected) >= self.limit:

                        break

                    try:

                        print(
                            f"Discover fallback search: {query}"
                        )

                        results = service.search_tracks(
                            query,
                            limit=self.limit
                        )

                        print(
                            f"Search '{query}' returned:",
                            len(results)
                        )

                        # --------------------------------------------
                        # DEDUPLICATE
                        # --------------------------------------------

                        for song in results:

                            if song is None:

                                continue

                            song_id = str(
                                getattr(
                                    song,
                                    "id",
                                    ""
                                )
                            )

                            audio_url = str(
                                getattr(
                                    song,
                                    "audio_url",
                                    ""
                                )
                            ).strip()

                            # ----------------------------------------
                            # PLAYABLE TRACKS ONLY
                            # ----------------------------------------

                            if not audio_url:

                                continue

                            if (
                                song_id
                                and
                                song_id in seen_ids
                            ):

                                continue

                            if song_id:

                                seen_ids.add(
                                    song_id
                                )

                            collected.append(
                                song
                            )

                            if (
                                len(collected)
                                >= self.limit
                            ):

                                break

                    except Exception as error:

                        print(
                            f"Fallback search "
                            f"'{query}' error:",
                            repr(error)
                        )

                songs = collected

                print(
                    "Discover fallback total:",
                    len(songs)
                )

            # ==================================================
            # FINAL CLEANUP
            # ==================================================

            clean_songs = []

            seen_ids = set()

            for song in songs:

                if song is None:

                    continue

                audio_url = str(
                    getattr(
                        song,
                        "audio_url",
                        ""
                    )
                ).strip()

                if not audio_url:

                    continue

                song_id = str(
                    getattr(
                        song,
                        "id",
                        ""
                    )
                )

                if (
                    song_id
                    and
                    song_id in seen_ids
                ):

                    continue

                if song_id:

                    seen_ids.add(
                        song_id
                    )

                clean_songs.append(
                    song
                )

                if (
                    len(clean_songs)
                    >= self.limit
                ):

                    break

            songs = clean_songs

            # ==================================================
            # DEBUG
            # ==================================================

            print(
                "Discover FINAL song count:",
                len(songs)
            )

            if songs:

                for index, song in enumerate(
                    songs[:5],
                    start=1
                ):

                    print(
                        f"{index}. "
                        f"{song.title} "
                        f"- {song.artist}"
                    )

            else:

                print(
                    "Discover: no online songs "
                    "available after all fallbacks."
                )

            print("=" * 60)
            print()

            # ==================================================
            # SEND TO UI
            # ==================================================

            self.songs_loaded.emit(
                songs
            )

        except Exception as error:

            print()
            print(
                "Discover loader fatal error:",
                repr(error)
            )
            print()

            self.load_failed.emit(
                str(error)
            )

# ============================================================
# DISCOVER SCREEN
# ============================================================

class DiscoverScreen(QWidget):

    # ========================================================
    # OLD LOCAL SIGNAL
    # ========================================================

    song_requested = Signal(
        str,
        str,
        str
    )

    # ========================================================
    # DAY 19 ONLINE SIGNAL
    # ========================================================

    online_song_requested = Signal(
        object
    )

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        super().__init__()

        # ====================================================
        # THEME
        # ====================================================

        self.is_dark = True

        # ====================================================
        # ONLINE STATE
        # ====================================================

        self.online_songs = []

        self.music_loader = None

        # ====================================================
        # COLLECTIONS
        # ====================================================

        self.music_cards = []

        self.mood_cards = []

        self.mood_icons = []

        self.mood_names = []

        self.genre_cards = []

        self.genre_labels = []

        # ====================================================
        # REFERENCES
        # ====================================================

        self.title_label = None

        self.subtitle_label = None

        self.banner = None

        self.banner_title = None

        self.banner_subtitle = None

        self.banner_icon = None

        self.section_titles = []

        self.section_actions = []

        self.bottom_text = None

        # ====================================================
        # BUILD
        # ====================================================

        self.build_ui()

        # ====================================================
        # THEME
        # ====================================================

        self.set_theme_state(
            True
        )

        # ====================================================
        # ONLINE LOAD
        # ====================================================

        QTimer.singleShot(
            100,
            self.load_online_music
        )

    # ========================================================
    # BUILD
    # ========================================================

    def build_ui(self):

        # ====================================================
        # ROOT
        # ====================================================

        root = QHBoxLayout(
            self
        )

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(
            0
        )

        # ====================================================
        # SIDEBAR
        # ====================================================

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.sidebar
        )

        # ====================================================
        # MAIN
        # ====================================================

        self.main = QWidget()

        self.main.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.main.setObjectName(
            "DiscoverMain"
        )

        self.main.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.main,
            1
        )

        # ====================================================
        # MAIN LAYOUT
        # ====================================================

        main_layout = QVBoxLayout(
            self.main
        )

        main_layout.setContentsMargins(
            30,
            26,
            22,
            26
        )

        main_layout.setSpacing(
            0
        )

        # ====================================================
        # SCROLL
        # ====================================================

        self.scroll = QScrollArea()

        self.scroll.setObjectName(
            "DiscoverScroll"
        )

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        main_layout.addWidget(
            self.scroll
        )

        # ====================================================
        # CONTENT
        # ====================================================

        self.content = QWidget()

        self.content.setObjectName(
            "DiscoverContent"
        )

        self.content.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.scroll.setWidget(
            self.content
        )

        self.content_layout = QVBoxLayout(
            self.content
        )

        self.content_layout.setContentsMargins(
            0,
            0,
            8,
            150
        )

        self.content_layout.setSpacing(
            24
        )

        self.content_layout.setAlignment(
            Qt.AlignTop
        )

        # ====================================================
        # HEADER
        # ====================================================

        self.title_label = QLabel(
            "Discover"
        )

        self.content_layout.addWidget(
            self.title_label
        )

        self.subtitle_label = QLabel(
            "Explore new sounds, moods and music."
        )

        self.content_layout.addWidget(
            self.subtitle_label
        )

        # ====================================================
        # FEATURE BANNER
        # ====================================================

        self.banner = QFrame()

        self.banner.setObjectName(
            "DiscoverBanner"
        )

        self.banner.setMinimumHeight(
            170
        )

        banner_layout = QHBoxLayout(
            self.banner
        )

        banner_layout.setContentsMargins(
            28,
            24,
            28,
            24
        )

        banner_text = QVBoxLayout()

        self.banner_title = QLabel(
            "Find Your Next Favorite"
        )

        self.banner_subtitle = QLabel(
            "Discover music streaming live from the LYRx online catalog."
        )

        self.banner_subtitle.setWordWrap(
            True
        )

        banner_text.addWidget(
            self.banner_title
        )

        banner_text.addSpacing(
            8
        )

        banner_text.addWidget(
            self.banner_subtitle
        )

        banner_text.addStretch()

        banner_layout.addLayout(
            banner_text
        )

        banner_layout.addStretch()

        self.banner_icon = QLabel(
            "♫"
        )

        self.banner_icon.setAlignment(
            Qt.AlignCenter
        )

        banner_layout.addWidget(
            self.banner_icon
        )

        self.content_layout.addWidget(
            self.banner
        )

        # ====================================================
        # TRENDING HEADER
        # ====================================================

        trending_header = (
            self.create_section_header(
                "Trending Now",
                "Online  ●",
            )
        )

        self.content_layout.addWidget(
            trending_header
        )

        # ====================================================
        # ONLINE STATUS
        # ====================================================

        self.online_status = QLabel(
            "Connecting to LYRx online music..."
        )

        self.online_status.setAlignment(
            Qt.AlignLeft
        )

        self.content_layout.addWidget(
            self.online_status
        )

        # ====================================================
        # TRENDING CONTAINER
        # ====================================================

        self.trending_container = QWidget()

        self.trending_container.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.trending_layout = QHBoxLayout(
            self.trending_container
        )

        self.trending_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.trending_layout.setSpacing(
            16
        )

        self.trending_layout.setAlignment(
            Qt.AlignLeft
        )

        self.content_layout.addWidget(
            self.trending_container
        )

        # ====================================================
        # LOADING PLACEHOLDERS
        # ====================================================

        self.build_loading_cards()

        # ====================================================
        # MOODS
        # ====================================================

        mood_header = (
            self.create_section_header(
                "Browse by Mood",
                "View All  ›",
            )
        )

        self.content_layout.addWidget(
            mood_header
        )

        mood_container = QWidget()

        mood_container.setAttribute(
            Qt.WA_TranslucentBackground
        )

        mood_layout = QHBoxLayout(
            mood_container
        )

        mood_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        mood_layout.setSpacing(
            14
        )

        for mood in MOODS:

            mood_name = mood[
                "name"
            ]

            mood_icon = mood[
                "icon"
            ]

            mood_card = QFrame()

            mood_card.setObjectName(
                "MoodCard"
            )

            mood_card.setMinimumHeight(
                105
            )

            mood_card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            mood_inner = QVBoxLayout(
                mood_card
            )

            mood_inner.setContentsMargins(
                12,
                12,
                12,
                12
            )

            mood_inner.setAlignment(
                Qt.AlignCenter
            )

            icon = QLabel(
                mood_icon
            )

            icon.setObjectName(
                "MoodIcon"
            )

            icon.setAlignment(
                Qt.AlignCenter
            )

            name = QLabel(
                mood_name
            )

            name.setObjectName(
                "MoodName"
            )

            name.setAlignment(
                Qt.AlignCenter
            )

            mood_inner.addWidget(
                icon
            )

            mood_inner.addWidget(
                name
            )

            mood_layout.addWidget(
                mood_card
            )

            self.mood_cards.append(
                mood_card
            )

            self.mood_icons.append(
                icon
            )

            self.mood_names.append(
                name
            )

        self.content_layout.addWidget(
            mood_container
        )

        # ====================================================
        # GENRES
        # ====================================================

        genre_header = (
            self.create_section_header(
                "Explore Genres",
                "View All  ›",
            )
        )

        self.content_layout.addWidget(
            genre_header
        )

        genre_container = QWidget()

        genre_container.setAttribute(
            Qt.WA_TranslucentBackground
        )

        genre_layout = QHBoxLayout(
            genre_container
        )

        genre_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        genre_layout.setSpacing(
            14
        )

        for genre in GENRES:

            genre_name = genre[
                "name"
            ]

            background = genre[
                "background"
            ]

            genre_card = QFrame()

            genre_card.setObjectName(
                "GenreCard"
            )

            genre_card.setProperty(
                "genre_background",
                background
            )

            genre_card.setMinimumHeight(
                90
            )

            genre_card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            genre_layout_inner = (
                QVBoxLayout(
                    genre_card
                )
            )

            genre_layout_inner.setAlignment(
                Qt.AlignCenter
            )

            genre_label = QLabel(
                genre_name
            )

            genre_label.setObjectName(
                "GenreLabel"
            )

            genre_label.setAlignment(
                Qt.AlignCenter
            )

            genre_layout_inner.addWidget(
                genre_label
            )

            genre_layout.addWidget(
                genre_card
            )

            self.genre_cards.append(
                genre_card
            )

            self.genre_labels.append(
                genre_label
            )

        self.content_layout.addWidget(
            genre_container
        )

        # ====================================================
        # BOTTOM
        # ====================================================

        self.bottom_text = QLabel(
            "LYRx online catalog powered by Jamendo ✦"
        )

        self.bottom_text.setAlignment(
            Qt.AlignCenter
        )

        self.content_layout.addWidget(
            self.bottom_text
        )

        self.content_layout.addSpacing(
            120
        )

    # ========================================================
    # LOADING CARDS
    # ========================================================

    def build_loading_cards(self):

        self.clear_trending_cards()

        for index in range(4):

            card = QFrame()

            card.setFixedSize(
                176,
                310
            )

            card.setObjectName(
                "LoadingMusicCard"
            )

            layout = QVBoxLayout(
                card
            )

            layout.setContentsMargins(
                10,
                10,
                10,
                12
            )

            placeholder = QLabel(
                "♫"
            )

            placeholder.setAlignment(
                Qt.AlignCenter
            )

            placeholder.setFixedSize(
                150,
                150
            )

            placeholder.setObjectName(
                "LoadingCover"
            )

            title = QLabel(
                "Loading..."
            )

            title.setObjectName(
                "LoadingText"
            )

            layout.addWidget(
                placeholder,
                alignment=Qt.AlignCenter
            )

            layout.addSpacing(
                8
            )

            layout.addWidget(
                title
            )

            layout.addStretch()

            self.trending_layout.addWidget(
                card
            )

        self.apply_loading_theme()

    # ========================================================
    # CLEAR TRENDING
    # ========================================================

    def clear_trending_cards(self):

        while self.trending_layout.count():

            item = (
                self.trending_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget:

                widget.setParent(
                    None
                )

                widget.deleteLater()

        self.music_cards.clear()

    # ========================================================
    # LOAD ONLINE
    # ========================================================

    def load_online_music(self):

        if (
            self.music_loader is not None
            and
            self.music_loader.isRunning()
        ):

            return

        self.online_status.setText(
            "Connecting to LYRx online music..."
        )

        self.music_loader = (
            OnlineMusicLoader(
                limit=10,
                parent=self
            )
        )

        self.music_loader.songs_loaded.connect(
            self.online_music_loaded
        )

        self.music_loader.load_failed.connect(
            self.online_music_failed
        )

        self.music_loader.finished.connect(
            self.online_loader_finished
        )

        self.music_loader.start()

    # ========================================================
    # ONLINE LOADED
    # ========================================================

    def online_music_loaded(
        self,
        songs
    ):

        self.online_songs = list(
            songs or []
        )

        self.clear_trending_cards()

        if not self.online_songs:

            self.online_status.setText(
                "Online catalog connected, but no tracks were returned."
            )

            self.apply_online_status_theme()

            self.show_online_empty_state()

            print(
                "Discover: API returned 0 usable songs."
            )

            return

        # ----------------------------------------------------
        # Preserve current blueprint:
        # four cards in this row.
        # ----------------------------------------------------

        visible_songs = (
            self.online_songs[:4]
        )

        for song in visible_songs:

            card = MusicCard(

                song.image_url,

                song.display_title(),

                song.display_artist(),

                duration_text=(
                    song.duration_text()
                ),

                song_data=song,

                # Online favorites will be upgraded
                # after the unified Library migration.
                favorite_enabled=False,
            )

            card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            card.online_play_requested.connect(
                self.handle_online_song_request
            )

            card.set_theme_state(
                self.is_dark
            )

            self.trending_layout.addWidget(
                card
            )

            self.music_cards.append(
                card
            )

        self.online_status.setText(
            f"●  Live catalog connected  ·  "
            f"{len(self.online_songs)} tracks loaded"
        )

        self.apply_online_status_theme()

        print(
            "Discover online songs loaded:",
            len(self.online_songs)
        )

    # ========================================================
    # ONLINE FAILED
    # ========================================================

    def online_music_failed(
        self,
        error_message
    ):

        print(
            "Discover online load error:",
            error_message
        )

        self.clear_trending_cards()

        self.online_status.setText(
            "Online music is temporarily unavailable."
        )

        self.show_online_empty_state()

        self.apply_online_status_theme()

    # ========================================================
    # LOADER FINISHED
    # ========================================================

    def online_loader_finished(self):

        if self.music_loader:

            self.music_loader.deleteLater()

            self.music_loader = None

    # ========================================================
    # EMPTY STATE
    # ========================================================

    def show_online_empty_state(self):

        empty = QLabel(
            "♫\n\n"
            "No online tracks are available right now.\n"
            "Check your internet connection and Jamendo configuration."
        )

        empty.setAlignment(
            Qt.AlignCenter
        )

        empty.setMinimumHeight(
            220
        )

        empty.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        empty.setObjectName(
            "OnlineEmpty"
        )

        self.trending_layout.addWidget(
            empty,
            1
        )

        self.apply_online_empty_theme(
            empty
        )

    # ========================================================
    # ONLINE SONG REQUEST
    # ========================================================

    def handle_online_song_request(
        self,
        song
    ):

        if song is None:

            return

        print(
            "Discover ONLINE song selected:",
            song.title,
            "-",
            song.artist
        )

        print(
            "Audio URL:",
            song.audio_url
        )

        self.online_song_requested.emit(
            song
        )

    # ========================================================
    # OLD LOCAL SONG REQUEST
    # ========================================================

    def handle_song_request(
        self,
        image_path,
        title,
        artist
    ):

        print(
            f"Discover local song selected: "
            f"{title} - {artist}"
        )

        self.song_requested.emit(
            image_path,
            title,
            artist
        )

    # ========================================================
    # SECTION HEADER
    # ========================================================

    def create_section_header(
        self,
        title_text,
        action_text
    ):

        header = QWidget()

        header.setAttribute(
            Qt.WA_TranslucentBackground
        )

        layout = QHBoxLayout(
            header
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            0
        )

        title = QLabel(
            title_text
        )

        title.setObjectName(
            "SectionTitle"
        )

        action = QLabel(
            action_text
        )

        action.setObjectName(
            "SectionAction"
        )

        action.setAlignment(
            Qt.AlignRight
            |
            Qt.AlignVCenter
        )

        layout.addWidget(
            title
        )

        layout.addStretch()

        layout.addWidget(
            action
        )

        self.section_titles.append(
            title
        )

        self.section_actions.append(
            action
        )

        return header

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.is_dark = bool(
            is_dark
        )

        try:

            self.sidebar.set_theme_state(
                self.is_dark
            )

        except Exception as error:

            print(
                "Discover sidebar theme error:",
                error
            )

        self.apply_scroll_theme()

        # ====================================================
        # HEADER
        # ====================================================

        if self.is_dark:

            title_color = "#FFFFFF"

            subtitle_color = "#AFA4C8"

        else:

            title_color = "#241B35"

            subtitle_color = "#766A89"

        self.title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {title_color};
                font-size: 34px;
                font-weight: 800;
                background: transparent;
            }}
            """
        )

        self.subtitle_label.setStyleSheet(
            f"""
            QLabel {{
                color: {subtitle_color};
                font-size: 14px;
                background: transparent;
            }}
            """
        )

        self.apply_banner_theme()

        # ====================================================
        # SECTION
        # ====================================================

        for title in self.section_titles:

            title.setStyleSheet(
                f"""
                QLabel {{
                    color: {
                        "#FFFFFF"
                        if self.is_dark
                        else "#2A203B"
                    };
                    font-size: 23px;
                    font-weight: 700;
                    background: transparent;
                }}
                """
            )

        for action in self.section_actions:

            action.setStyleSheet(
                f"""
                QLabel {{
                    color: {
                        "#A78BFA"
                        if self.is_dark
                        else "#7440D9"
                    };
                    font-size: 13px;
                    font-weight: 600;
                    background: transparent;
                }}
                """
            )

        self.apply_mood_theme()

        self.apply_genre_theme()

        self.apply_online_status_theme()

        self.apply_loading_theme()

        # ====================================================
        # BOTTOM
        # ====================================================

        self.bottom_text.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#716889"
                    if self.is_dark
                    else "#8B7D9E"
                };
                font-size: 12px;
                padding: 20px;
                background: transparent;
            }}
            """
        )

        # ====================================================
        # MUSIC CARDS
        # ====================================================

        for card in self.music_cards:

            try:

                card.set_theme_state(
                    self.is_dark
                )

            except Exception as error:

                print(
                    "Discover MusicCard theme error:",
                    error
                )

        self.update()

        self.main.update()

        self.content.update()

        self.scroll.viewport().update()

    # ========================================================
    # ONLINE STATUS THEME
    # ========================================================

    def apply_online_status_theme(self):

        if not hasattr(
            self,
            "online_status"
        ):

            return

        if self.is_dark:

            color = "#8F84A6"

        else:

            color = "#756A88"

        self.online_status.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                font-size: 11px;
                font-weight: 600;
                background: transparent;
                padding-left: 2px;
            }}
            """
        )

    # ========================================================
    # LOADING THEME
    # ========================================================

    def apply_loading_theme(self):

        if not hasattr(
            self,
            "trending_container"
        ):

            return

        if self.is_dark:

            card_bg = "#181329"

            border = "#30224B"

            text_color = "#756A91"

            cover_bg = "#211633"

        else:

            card_bg = "#F1EBFA"

            border = "#D7CBE8"

            text_color = "#8A7899"

            cover_bg = "#E5DCEB"

        self.trending_container.setStyleSheet(
            f"""
            QFrame#LoadingMusicCard {{
                background: {card_bg};
                border: 1px solid {border};
                border-radius: 20px;
            }}

            QLabel#LoadingCover {{
                background: {cover_bg};
                color: #8B5CF6;
                border-radius: 18px;
                font-size: 40px;
            }}

            QLabel#LoadingText {{
                color: {text_color};
                background: transparent;
                font-size: 12px;
            }}
            """
        )

    # ========================================================
    # EMPTY THEME
    # ========================================================

    def apply_online_empty_theme(
        self,
        label
    ):

        if self.is_dark:

            label.setStyleSheet(
                """
                QLabel#OnlineEmpty {
                    color: #9589AA;
                    background: #181329;
                    border: 1px solid #30224B;
                    border-radius: 18px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 25px;
                }
                """
            )

        else:

            label.setStyleSheet(
                """
                QLabel#OnlineEmpty {
                    color: #756A88;
                    background: #F1EBFA;
                    border: 1px solid #D7CBE8;
                    border-radius: 18px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 25px;
                }
                """
            )

    # ========================================================
    # SCROLL THEME
    # ========================================================

    def apply_scroll_theme(self):

        self.scroll.setStyleSheet(
            f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}

            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}

            QScrollBar:vertical {{
                width: 9px;
                background: transparent;
                margin: 2px;
            }}

            QScrollBar::handle:vertical {{
                background: {
                    "#7C3AED"
                    if self.is_dark
                    else "#8B5CF6"
                };
                border-radius: 4px;
                min-height: 55px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {
                    "#9F67FF"
                    if self.is_dark
                    else "#7040D4"
                };
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            """
        )

    # ========================================================
    # BANNER THEME
    # ========================================================

    def apply_banner_theme(self):

        if self.is_dark:

            banner_bg = "#18122A"

            border = "#30224B"

            hover_border = "#53358A"

            title = "#FFFFFF"

            subtitle = "#AAA0C5"

            icon = "#A970FF"

        else:

            banner_bg = "#EDE6FA"

            border = "#D3C5EA"

            hover_border = "#B99BEA"

            title = "#281B3B"

            subtitle = "#756785"

            icon = "#7C3AED"

        self.banner.setStyleSheet(
            f"""
            QFrame#DiscoverBanner {{
                background: {banner_bg};
                border: 1px solid {border};
                border-radius: 24px;
            }}

            QFrame#DiscoverBanner:hover {{
                border: 1px solid {hover_border};
            }}
            """
        )

        self.banner_title.setStyleSheet(
            f"""
            QLabel {{
                color: {title};
                font-size: 25px;
                font-weight: 800;
                background: transparent;
            }}
            """
        )

        self.banner_subtitle.setStyleSheet(
            f"""
            QLabel {{
                color: {subtitle};
                font-size: 14px;
                background: transparent;
            }}
            """
        )

        self.banner_icon.setStyleSheet(
            f"""
            QLabel {{
                color: {icon};
                font-size: 72px;
                font-weight: 800;
                background: transparent;
            }}
            """
        )

    # ========================================================
    # MOOD THEME
    # ========================================================

    def apply_mood_theme(self):

        if self.is_dark:

            card_style = """
            QFrame#MoodCard {
                background: #181329;
                border: 1px solid #30224B;
                border-radius: 18px;
            }

            QFrame#MoodCard:hover {
                background: #24183D;
                border: 1px solid #7048C7;
            }
            """

            icon_style = """
            QLabel#MoodIcon {
                color: #FFFFFF;
                font-size: 25px;
                background: transparent;
            }
            """

            name_style = """
            QLabel#MoodName {
                color: #D9D3EA;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
            }
            """

        else:

            card_style = """
            QFrame#MoodCard {
                background: #F1EBFA;
                border: 1px solid #D7CBE8;
                border-radius: 18px;
            }

            QFrame#MoodCard:hover {
                background: #E8DDF7;
                border: 1px solid #A98AD7;
            }
            """

            icon_style = """
            QLabel#MoodIcon {
                color: #49366A;
                font-size: 25px;
                background: transparent;
            }
            """

            name_style = """
            QLabel#MoodName {
                color: #594B6E;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
            }
            """

        for card in self.mood_cards:

            card.setStyleSheet(
                card_style
            )

        for icon in self.mood_icons:

            icon.setStyleSheet(
                icon_style
            )

        for name in self.mood_names:

            name.setStyleSheet(
                name_style
            )

    # ========================================================
    # GENRE THEME
    # ========================================================

    def apply_genre_theme(self):

        for card in self.genre_cards:

            original_background = (
                card.property(
                    "genre_background"
                )
            )

            if original_background is None:

                original_background = (
                    "#30224B"
                )

            card.setStyleSheet(
                f"""
                QFrame#GenreCard {{
                    background: {original_background};
                    border-radius: 18px;
                    border: 1px solid rgba(255,255,255,20);
                }}

                QFrame#GenreCard:hover {{
                    border: 1px solid {
                        "#A970FF"
                        if self.is_dark
                        else "#7C3AED"
                    };
                }}
                """
            )

        for label in self.genre_labels:

            label.setStyleSheet(
                """
                QLabel#GenreLabel {
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

    # ========================================================
    # BACKGROUND
    # ========================================================

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        # ====================================================
        # DARK
        # ====================================================

        if self.is_dark:

            gradient.setColorAt(
                0.0,
                QColor("#0B0913")
            )

            gradient.setColorAt(
                0.45,
                QColor("#151124")
            )

            gradient.setColorAt(
                1.0,
                QColor("#09070F")
            )

        # ====================================================
        # LIGHT
        # ====================================================

        else:

            gradient.setColorAt(
                0.0,
                QColor("#F4F0FA")
            )

            gradient.setColorAt(
                0.45,
                QColor("#EDE7F5")
            )

            gradient.setColorAt(
                1.0,
                QColor("#E8E1F1")
            )

        painter.fillRect(
            rect,
            gradient
        )

        # ====================================================
        # GLOW
        # ====================================================

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                124,
                58,
                237,
                24
                if self.is_dark
                else 15
            )
        )

        painter.drawEllipse(
            -180,
            -180,
            500,
            400
        )

        painter.setBrush(
            QColor(
                139,
                92,
                246,
                16
                if self.is_dark
                else 10
            )
        )

        painter.drawEllipse(
            rect.width() - 420,
            120,
            500,
            500
        )

        painter.end()

        super().paintEvent(
            event
        )