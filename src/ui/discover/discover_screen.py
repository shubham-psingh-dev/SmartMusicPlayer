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

from services.provider_registry import (
    ProviderRegistry,
)


# ============================================================
# LYRx
# DAY 20 - PHASE 2
# FILE 4
#
# DISCOVER SCREEN
#
# Provider architecture:
#
# DiscoverScreen
#       │
#       ▼
# OnlineMusicLoader
#       │
#       ▼
# ProviderRegistry
#       │
#       ├── JamendoProvider
#       ├── Future provider
#       └── Future provider
#
# ============================================================


# ============================================================
# ONLINE MUSIC LOADER
# ============================================================

class OnlineMusicLoader(QThread):

    # --------------------------------------------------------
    # songs, mode, query
    # --------------------------------------------------------

    songs_loaded = Signal(
        list,
        str,
        str,
    )

    # --------------------------------------------------------
    # error, mode, query
    # --------------------------------------------------------

    load_failed = Signal(
        str,
        str,
        str,
    )

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        mode="trending",
        query="",
        limit=12,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.mode = str(
            mode
            or "trending"
        ).strip().lower()

        self.query = str(
            query
            or ""
        ).strip()

        try:

            self.limit = max(
                1,
                min(
                    int(limit),
                    50
                )
            )

        except (
            TypeError,
            ValueError
        ):

            self.limit = 12

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        try:

            print()
            print(
                "=" * 60
            )

            print(
                "LYRx Discover provider loader started"
            )

            print(
                "Mode:",
                self.mode
            )

            if self.query:

                print(
                    "Query:",
                    self.query
                )

            print(
                "=" * 60
            )

            # ==================================================
            # IMPORTANT
            # ==================================================
            #
            # Create ProviderRegistry INSIDE the worker.
            #
            # This also creates the provider/service instances
            # inside this worker thread rather than reusing a
            # network/session object from the Qt main thread.
            #

            registry = (
                ProviderRegistry()
            )

            print(
                "Registered providers:",
                registry.provider_names()
            )

            print(
                "Available providers:",
                [
                    getattr(
                        provider,
                        "provider_name",
                        "unknown"
                    )
                    for provider
                    in registry.available_providers()
                ]
            )

            # ==================================================
            # NO PROVIDERS
            # ==================================================

            if not registry.has_available_provider():

                raise RuntimeError(
                    "No online music provider is available."
                )

            songs = []

            # ==================================================
            # TRENDING
            # ==================================================

            if self.mode == "trending":

                print(
                    "Discover: provider trending request..."
                )

                songs = (
                    registry.get_trending(
                        limit=self.limit
                    )
                )

                # ------------------------------------------------
                # FALLBACK
                # ------------------------------------------------

                if not songs:

                    print(
                        "Trending empty. Trying popular..."
                    )

                    songs = (
                        registry.get_popular(
                            limit=self.limit
                        )
                    )

            # ==================================================
            # POPULAR
            # ==================================================

            elif self.mode == "popular":

                print(
                    "Discover: provider popular request..."
                )

                songs = (
                    registry.get_popular(
                        limit=self.limit
                    )
                )

            # ==================================================
            # NORMAL SEARCH
            # ==================================================

            elif self.mode == "search":

                if not self.query:

                    songs = []

                else:

                    print(
                        "Discover provider search:",
                        self.query
                    )

                    result = (
                        registry.search(
                            self.query,
                            limit=self.limit
                        )
                    )

                    songs = list(
                        getattr(
                            result,
                            "songs",
                            []
                        )
                        or []
                    )

                    result_error = str(
                        getattr(
                            result,
                            "error",
                            ""
                        )
                        or ""
                    )

                    if (
                        not songs
                        and
                        result_error
                    ):

                        print(
                            "Registry search result error:",
                            result_error
                        )

            # ==================================================
            # GENRE
            # ==================================================

            elif self.mode == "genre":

                if not self.query:

                    songs = []

                else:

                    print(
                        "Discover genre request:",
                        self.query
                    )

                    songs = (
                        registry.get_by_genre(
                            self.query,
                            limit=self.limit
                        )
                    )

            # ==================================================
            # MOOD
            # ==================================================

            elif self.mode == "mood":

                if not self.query:

                    songs = []

                else:

                    print(
                        "Discover mood request:",
                        self.query
                    )

                    songs = (
                        registry.get_by_mood(
                            self.query,
                            limit=self.limit
                        )
                    )

            # ==================================================
            # HINDI
            # ==================================================

            elif self.mode == "hindi":

                print(
                    "Discover Hindi request..."
                )

                songs = (
                    registry.get_hindi(
                        limit=self.limit
                    )
                )

            # ==================================================
            # ENGLISH
            # ==================================================

            elif self.mode == "english":

                print(
                    "Discover English request..."
                )

                songs = (
                    registry.get_english(
                        limit=self.limit
                    )
                )

            # ==================================================
            # ARTIST
            # ==================================================

            elif self.mode == "artist":

                if not self.query:

                    songs = []

                else:

                    print(
                        "Discover artist request:",
                        self.query
                    )

                    songs = (
                        registry.search_artist(
                            self.query,
                            limit=self.limit
                        )
                    )

            # ==================================================
            # SONG TITLE
            # ==================================================

            elif self.mode == "song":

                if not self.query:

                    songs = []

                else:

                    print(
                        "Discover song title request:",
                        self.query
                    )

                    songs = (
                        registry.search_song(
                            self.query,
                            limit=self.limit
                        )
                    )

            # ==================================================
            # UNKNOWN MODE
            # ==================================================

            else:

                raise RuntimeError(
                    f"Unknown Discover loader mode: "
                    f"{self.mode}"
                )

            # ==================================================
            # NORMALIZE
            # ==================================================

            songs = list(
                songs
                or []
            )

            print(
                "Discover FINAL song count:",
                len(songs)
            )

            # ==================================================
            # DEBUG FIRST RESULTS
            # ==================================================

            for (
                index,
                song
            ) in enumerate(
                songs[:5],
                start=1
            ):

                print(
                    f"{index}. "
                    f"{getattr(song, 'title', 'Unknown')} "
                    f"- "
                    f"{getattr(song, 'artist', 'Unknown')}"
                )

            print(
                "=" * 60
            )

            print()

            # ==================================================
            # RESULT
            # ==================================================

            self.songs_loaded.emit(
                songs,
                self.mode,
                self.query,
            )

        except Exception as error:

            print()
            print(
                "=" * 60
            )

            print(
                "Discover provider loader ERROR"
            )

            print(
                "Mode:",
                self.mode
            )

            print(
                "Query:",
                self.query
            )

            print(
                "Error:",
                repr(error)
            )

            print(
                "=" * 60
            )

            print()

            self.load_failed.emit(
                str(error),
                self.mode,
                self.query,
            )


# ============================================================
# DISCOVER SCREEN
# ============================================================

class DiscoverScreen(QWidget):

    # ========================================================
    # OLD LOCAL SIGNAL
    # ========================================================
    #
    # KEEP.
    #
    # Some older LYRx modules still know local tracks using:
    #
    # image_path, title, artist
    #

    song_requested = Signal(
        str,
        str,
        str
    )

    # ========================================================
    # ONLINE SIGNAL
    # ========================================================
    #
    # Emits unified Song object.
    #

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

        self.current_mode = (
            "trending"
        )

        self.current_query = ""

        # ====================================================
        # REQUEST QUEUE
        # ====================================================
        #
        # If user clicks another genre/mood while a previous
        # network request is running, do NOT start two QThreads
        # simultaneously.
        #
        # Store newest requested action and execute it after
        # current loader finishes.
        #

        self.pending_mode = None

        self.pending_query = ""

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

        self.trending_title = None

        self.trending_action = None

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
        # INITIAL ONLINE LOAD
        # ====================================================

        QTimer.singleShot(
            120,
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

        # ----------------------------------------------------
        # Bottom margin preserved for floating player.
        # ----------------------------------------------------

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
            "Discover music through LYRx's "
            "multi-provider online catalog."
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

        # ====================================================
        # BANNER ICON
        # ====================================================

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
        # ONLINE RESULTS HEADER
        # ====================================================

        trending_header = (
            self.create_section_header(
                "Trending Now",
                "Online  ●",
            )
        )

        # ----------------------------------------------------
        # Save direct references.
        # ----------------------------------------------------

        if self.section_titles:

            self.trending_title = (
                self.section_titles[-1]
            )

        if self.section_actions:

            self.trending_action = (
                self.section_actions[-1]
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
        # MOOD HEADER
        # ====================================================

        mood_header = (
            self.create_section_header(
                "Browse by Mood",
                "Choose a mood  ›",
            )
        )

        self.content_layout.addWidget(
            mood_header
        )

        # ====================================================
        # MOOD CONTAINER
        # ====================================================

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

        # ====================================================
        # MOOD CARDS
        # ====================================================

        for mood in MOODS:

            mood_name = str(
                mood.get(
                    "name",
                    ""
                )
            ).strip()

            mood_icon = str(
                mood.get(
                    "icon",
                    "♫"
                )
            )

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

            mood_card.setCursor(
                Qt.PointingHandCursor
            )

            # ------------------------------------------------
            # Store mood name on widget.
            # ------------------------------------------------

            mood_card.setProperty(
                "mood_name",
                mood_name
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

            # ------------------------------------------------
            # ICON
            # ------------------------------------------------

            icon = QLabel(
                mood_icon
            )

            icon.setObjectName(
                "MoodIcon"
            )

            icon.setAlignment(
                Qt.AlignCenter
            )

            icon.setAttribute(
                Qt.WA_TransparentForMouseEvents,
                True
            )

            # ------------------------------------------------
            # NAME
            # ------------------------------------------------

            name = QLabel(
                mood_name
            )

            name.setObjectName(
                "MoodName"
            )

            name.setAlignment(
                Qt.AlignCenter
            )

            name.setAttribute(
                Qt.WA_TransparentForMouseEvents,
                True
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

            # ------------------------------------------------
            # CLICK
            # ------------------------------------------------

            mood_card.mousePressEvent = (
                lambda event,
                value=mood_name:
                self.handle_mood_click(
                    event,
                    value
                )
            )

        self.content_layout.addWidget(
            mood_container
        )

        # ====================================================
        # GENRE HEADER
        # ====================================================

        genre_header = (
            self.create_section_header(
                "Explore Genres",
                "Choose a genre  ›",
            )
        )

        self.content_layout.addWidget(
            genre_header
        )

        # ====================================================
        # GENRE CONTAINER
        # ====================================================

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

        # ====================================================
        # GENRE CARDS
        # ====================================================

        for genre in GENRES:

            genre_name = str(
                genre.get(
                    "name",
                    ""
                )
            ).strip()

            background = str(
                genre.get(
                    "background",
                    "#30224B"
                )
            )

            genre_card = QFrame()

            genre_card.setObjectName(
                "GenreCard"
            )

            genre_card.setProperty(
                "genre_background",
                background
            )

            genre_card.setProperty(
                "genre_name",
                genre_name
            )

            genre_card.setMinimumHeight(
                90
            )

            genre_card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            genre_card.setCursor(
                Qt.PointingHandCursor
            )

            genre_layout_inner = (
                QVBoxLayout(
                    genre_card
                )
            )

            genre_layout_inner.setAlignment(
                Qt.AlignCenter
            )

            # ------------------------------------------------
            # LABEL
            # ------------------------------------------------

            genre_label = QLabel(
                genre_name
            )

            genre_label.setObjectName(
                "GenreLabel"
            )

            genre_label.setAlignment(
                Qt.AlignCenter
            )

            genre_label.setAttribute(
                Qt.WA_TransparentForMouseEvents,
                True
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

            # ------------------------------------------------
            # CLICK
            # ------------------------------------------------

            genre_card.mousePressEvent = (
                lambda event,
                value=genre_name:
                self.handle_genre_click(
                    event,
                    value
                )
            )

        self.content_layout.addWidget(
            genre_container
        )

        # ====================================================
        # BOTTOM
        # ====================================================

        self.bottom_text = QLabel(
            "LYRx multi-provider music discovery ✦"
        )

        self.bottom_text.setAlignment(
            Qt.AlignCenter
        )

        self.content_layout.addWidget(
            self.bottom_text
        )

        # ====================================================
        # EXTRA BOTTOM SPACE
        # ====================================================

        self.content_layout.addSpacing(
            120
        )

    # ========================================================
    # LOADING CARDS
    # ========================================================

    def build_loading_cards(self):

        self.clear_trending_cards()

        # ----------------------------------------------------
        # Preserve existing LYRx blueprint:
        # 4 cards visible in one row.
        # ----------------------------------------------------

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

            layout.setSpacing(
                8
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
                "Loading music..."
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

        if not hasattr(
            self,
            "trending_layout"
        ):

            return

        while self.trending_layout.count():

            item = (
                self.trending_layout
                .takeAt(0)
            )

            widget = (
                item.widget()
            )

            if widget:

                widget.setParent(
                    None
                )

                widget.deleteLater()

        self.music_cards.clear()

    # ========================================================
    # INITIAL ONLINE LOAD
    # ========================================================

    def load_online_music(self):

        self.request_online_music(
            mode="trending",
            query=""
        )

    # ========================================================
    # GENERIC PROVIDER REQUEST
    # ========================================================

    def request_online_music(
        self,
        mode="search",
        query="",
        limit=12,
    ):

        mode = str(
            mode
            or "search"
        ).strip().lower()

        query = str(
            query
            or ""
        ).strip()

        # ====================================================
        # ACTIVE THREAD
        # ====================================================

        if (
            self.music_loader is not None
            and
            self.music_loader.isRunning()
        ):

            # ------------------------------------------------
            # Keep newest request.
            # ------------------------------------------------

            self.pending_mode = mode

            self.pending_query = query

            self.online_status.setText(
                "Finishing current request..."
            )

            self.apply_online_status_theme()

            return

        # ====================================================
        # STATE
        # ====================================================

        self.current_mode = mode

        self.current_query = query

        # ====================================================
        # SECTION TITLE
        # ====================================================

        self.update_results_heading(
            mode,
            query
        )

        # ====================================================
        # LOADING UI
        # ====================================================

        self.online_status.setText(
            self.loading_status_text(
                mode,
                query
            )
        )

        self.apply_online_status_theme()

        self.build_loading_cards()

        # ====================================================
        # THREAD
        # ====================================================

        self.music_loader = (
            OnlineMusicLoader(
                mode=mode,
                query=query,
                limit=limit,
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
    # LEGACY / GLOBAL SEARCH METHOD
    # ========================================================
    #
    # KEEP THIS METHOD NAME.
    #
    # Other LYRx screens can continue calling:
    #
    # discover.search_online_music("artist or song")
    #

    def search_online_music(
        self,
        query
    ):

        query = str(
            query
            or ""
        ).strip()

        if not query:

            self.load_online_music()

            return

        self.request_online_music(
            mode="search",
            query=query,
            limit=12,
        )

    # ========================================================
    # SEARCH ARTIST
    # ========================================================

    def search_artist(
        self,
        artist_name
    ):

        artist_name = str(
            artist_name
            or ""
        ).strip()

        if not artist_name:

            return

        self.request_online_music(
            mode="artist",
            query=artist_name,
            limit=12,
        )

    # ========================================================
    # SEARCH SONG
    # ========================================================

    def search_song(
        self,
        song_title
    ):

        song_title = str(
            song_title
            or ""
        ).strip()

        if not song_title:

            return

        self.request_online_music(
            mode="song",
            query=song_title,
            limit=12,
        )

    # ========================================================
    # HINDI
    # ========================================================

    def load_hindi_music(self):

        self.request_online_music(
            mode="hindi",
            query="Hindi",
            limit=12,
        )

    # ========================================================
    # ENGLISH
    # ========================================================

    def load_english_music(self):

        self.request_online_music(
            mode="english",
            query="English",
            limit=12,
        )

    # ========================================================
    # ONLINE LOADED
    # ========================================================

    def online_music_loaded(
        self,
        songs,
        mode,
        query
    ):

        # ====================================================
        # STATE
        # ====================================================

        self.current_mode = (
            str(mode)
        )

        self.current_query = (
            str(query)
        )

        self.online_songs = list(
            songs
            or []
        )

        # ====================================================
        # CLEAR LOADING
        # ====================================================

        self.clear_trending_cards()

        # ====================================================
        # NO RESULTS
        # ====================================================

        if not self.online_songs:

            self.online_status.setText(
                self.empty_status_text(
                    mode,
                    query
                )
            )

            self.apply_online_status_theme()

            self.show_online_empty_state(
                mode,
                query
            )

            print(
                "Discover: provider returned "
                "0 usable songs."
            )

            return

        # ====================================================
        # CURRENT BLUEPRINT
        # ====================================================
        #
        # Keep only 4 visible cards in the Discover row.
        #
        # The loader may fetch more because:
        #
        # - queue can use more songs later
        # - See All can use them later
        # - recommendation engine can use them later
        #

        visible_songs = (
            self.online_songs[:4]
        )

        # ====================================================
        # MUSIC CARDS
        # ====================================================

        for song in visible_songs:

            # ------------------------------------------------
            # Defensive display values.
            # ------------------------------------------------

            try:

                title = (
                    song.display_title()
                )

            except Exception:

                title = (
                    getattr(
                        song,
                        "title",
                        "Unknown Track"
                    )
                    or "Unknown Track"
                )

            try:

                artist = (
                    song.display_artist()
                )

            except Exception:

                artist = (
                    getattr(
                        song,
                        "artist",
                        "Unknown Artist"
                    )
                    or "Unknown Artist"
                )

            try:

                duration_text = (
                    song.duration_text()
                )

            except Exception:

                duration_text = "0:00"

            image_url = str(
                getattr(
                    song,
                    "image_url",
                    ""
                )
                or ""
            )

            # =================================================
            # MUSIC CARD
            # =================================================

            card = MusicCard(

                image_url,

                title,

                artist,

                duration_text=(
                    duration_text
                ),

                song_data=(
                    song
                ),

                # ------------------------------------------------
                # Online Favorites migration will be handled
                # separately once Favorites/Library are unified
                # around Song objects.
                # ------------------------------------------------

                favorite_enabled=False,
            )

            card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            # =================================================
            # ONLINE PLAY
            # =================================================

            card.online_play_requested.connect(
                self.handle_online_song_request
            )

            # =================================================
            # THEME
            # =================================================

            card.set_theme_state(
                self.is_dark
            )

            self.trending_layout.addWidget(
                card
            )

            self.music_cards.append(
                card
            )

        # ====================================================
        # STATUS
        # ====================================================

        self.online_status.setText(
            self.success_status_text(
                mode,
                query,
                len(
                    self.online_songs
                )
            )
        )

        self.apply_online_status_theme()

        # ====================================================
        # HEADING
        # ====================================================

        self.update_results_heading(
            mode,
            query
        )

        print(
            "Discover online songs loaded:",
            len(
                self.online_songs
            )
        )

    # ========================================================
    # ONLINE FAILED
    # ========================================================

    def online_music_failed(
        self,
        error_message,
        mode,
        query
    ):

        print(
            "Discover online load error:",
            error_message
        )

        self.clear_trending_cards()

        self.online_songs = []

        self.online_status.setText(
            "Online music is temporarily unavailable."
        )

        self.show_online_error_state(
            error_message
        )

        self.apply_online_status_theme()

        self.update_results_heading(
            mode,
            query
        )

    # ========================================================
    # LOADER FINISHED
    # ========================================================

    def online_loader_finished(self):

        # ----------------------------------------------------
        # Cleanup old worker.
        # ----------------------------------------------------

        if self.music_loader:

            self.music_loader.deleteLater()

            self.music_loader = None

        # ====================================================
        # PENDING REQUEST
        # ====================================================

        if self.pending_mode is not None:

            mode = self.pending_mode

            query = self.pending_query

            self.pending_mode = None

            self.pending_query = ""

            QTimer.singleShot(
                20,
                lambda:
                self.request_online_music(
                    mode=mode,
                    query=query,
                    limit=12,
                )
            )

    # ========================================================
    # HEADING
    # ========================================================

    def update_results_heading(
        self,
        mode,
        query
    ):

        if self.trending_title is None:

            return

        mode = str(
            mode
            or "trending"
        ).lower()

        query = str(
            query
            or ""
        ).strip()

        # ====================================================
        # TRENDING
        # ====================================================

        if mode == "trending":

            title = (
                "Trending Now"
            )

        # ====================================================
        # POPULAR
        # ====================================================

        elif mode == "popular":

            title = (
                "Popular Now"
            )

        # ====================================================
        # GENRE
        # ====================================================

        elif mode == "genre":

            title = (
                f"{query} · Online"
                if query
                else "Genre · Online"
            )

        # ====================================================
        # MOOD
        # ====================================================

        elif mode == "mood":

            title = (
                f"{query} Mood · Online"
                if query
                else "Mood Music · Online"
            )

        # ====================================================
        # HINDI
        # ====================================================

        elif mode == "hindi":

            title = (
                "Hindi Music · Online"
            )

        # ====================================================
        # ENGLISH
        # ====================================================

        elif mode == "english":

            title = (
                "English Music · Online"
            )

        # ====================================================
        # ARTIST
        # ====================================================

        elif mode == "artist":

            title = (
                f"Artist · {query}"
                if query
                else "Artist Results"
            )

        # ====================================================
        # SONG
        # ====================================================

        elif mode == "song":

            title = (
                f"Song · {query}"
                if query
                else "Song Results"
            )

        # ====================================================
        # SEARCH
        # ====================================================

        else:

            title = (
                f"Search · {query}"
                if query
                else "Online Search"
            )

        self.trending_title.setText(
            title
        )

        # ----------------------------------------------------
        # Right-side status text.
        # ----------------------------------------------------

        if self.trending_action is not None:

            self.trending_action.setText(
                "Online  ●"
            )

    # ========================================================
    # LOADING STATUS
    # ========================================================

    @staticmethod
    def loading_status_text(
        mode,
        query
    ):

        mode = str(
            mode
            or ""
        ).lower()

        query = str(
            query
            or ""
        ).strip()

        if mode == "trending":

            return (
                "Loading trending music "
                "from available providers..."
            )

        if mode == "genre":

            return (
                f"Finding {query} music..."
            )

        if mode == "mood":

            return (
                f"Finding music for your "
                f"{query} mood..."
            )

        if mode == "hindi":

            return (
                "Finding Hindi music..."
            )

        if mode == "english":

            return (
                "Finding English music..."
            )

        if mode == "artist":

            return (
                f"Searching artist: {query}..."
            )

        if mode == "song":

            return (
                f"Searching song: {query}..."
            )

        return (
            f"Searching online music"
            f"{f' for {query}' if query else ''}..."
        )

    # ========================================================
    # SUCCESS STATUS
    # ========================================================

    @staticmethod
    def success_status_text(
        mode,
        query,
        count
    ):

        mode = str(
            mode
            or ""
        ).lower()

        query = str(
            query
            or ""
        ).strip()

        if mode == "genre":

            return (
                f"●  {query} catalog connected"
                f"  ·  {count} tracks loaded"
            )

        if mode == "mood":

            return (
                f"●  {query} mood results"
                f"  ·  {count} tracks loaded"
            )

        if mode == "search":

            return (
                f"●  Search results for "
                f"“{query}”"
                f"  ·  {count} tracks"
            )

        if mode == "artist":

            return (
                f"●  Artist results for "
                f"“{query}”"
                f"  ·  {count} tracks"
            )

        if mode == "song":

            return (
                f"●  Song results for "
                f"“{query}”"
                f"  ·  {count} tracks"
            )

        if mode == "hindi":

            return (
                f"●  Hindi catalog"
                f"  ·  {count} tracks loaded"
            )

        if mode == "english":

            return (
                f"●  English catalog"
                f"  ·  {count} tracks loaded"
            )

        return (
            f"●  Live catalog connected"
            f"  ·  {count} tracks loaded"
        )

    # ========================================================
    # EMPTY STATUS
    # ========================================================

    @staticmethod
    def empty_status_text(
        mode,
        query
    ):

        mode = str(
            mode
            or ""
        ).lower()

        query = str(
            query
            or ""
        ).strip()

        if mode == "genre":

            return (
                f"No {query} tracks were returned "
                f"by the current providers."
            )

        if mode == "mood":

            return (
                f"No tracks were returned for "
                f"the {query} mood."
            )

        if mode in (
            "search",
            "artist",
            "song",
        ):

            return (
                f"No online tracks found for "
                f"“{query}”."
            )

        if mode == "hindi":

            return (
                "The current providers returned "
                "no Hindi tracks."
            )

        if mode == "english":

            return (
                "The current providers returned "
                "no English tracks."
            )

        return (
            "Online catalog connected, "
            "but no tracks were returned."
        )

    # ========================================================
    # EMPTY STATE
    # ========================================================

    def show_online_empty_state(
        self,
        mode="",
        query=""
    ):

        mode = str(
            mode
            or ""
        ).lower()

        query = str(
            query
            or ""
        ).strip()

        if mode == "genre":

            message = (
                f"♫\n\n"
                f"No {query} tracks are available "
                f"from the current provider.\n\n"
                f"More providers can be added to LYRx "
                f"without changing this screen."
            )

        elif mode == "mood":

            message = (
                f"♫\n\n"
                f"No music was found for the "
                f"{query} mood.\n\n"
                f"Try another mood or search."
            )

        elif mode in (
            "search",
            "artist",
            "song",
        ):

            message = (
                f"♫\n\n"
                f"No online music found for "
                f"“{query}”.\n\n"
                f"Try another song, artist, "
                f"genre or keyword."
            )

        else:

            message = (
                "♫\n\n"
                "No online tracks are available "
                "right now.\n\n"
                "Check your internet connection "
                "and provider configuration."
            )

        empty = QLabel(
            message
        )

        empty.setAlignment(
            Qt.AlignCenter
        )

        empty.setWordWrap(
            True
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
    # ERROR STATE
    # ========================================================

    def show_online_error_state(
        self,
        error_message
    ):

        error_message = str(
            error_message
            or "Unknown provider error."
        )

        label = QLabel(
            "⚠\n\n"
            "LYRx couldn't load online music.\n\n"
            f"{error_message}"
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        label.setWordWrap(
            True
        )

        label.setMinimumHeight(
            220
        )

        label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        label.setObjectName(
            "OnlineEmpty"
        )

        self.trending_layout.addWidget(
            label,
            1
        )

        self.apply_online_empty_theme(
            label
        )

    # ========================================================
    # MOOD CLICK
    # ========================================================

    def handle_mood_click(
        self,
        event,
        mood_name
    ):

        if (
            event is not None
            and
            event.button()
            != Qt.LeftButton
        ):

            return

        mood_name = str(
            mood_name
            or ""
        ).strip()

        if not mood_name:

            return

        print(
            "LYRx mood selected:",
            mood_name
        )

        # ====================================================
        # IMPORTANT
        # ====================================================
        #
        # This is NOT generic text search anymore.
        #
        # ProviderRegistry.get_by_mood()
        #

        self.request_online_music(
            mode="mood",
            query=mood_name,
            limit=12,
        )

    # ========================================================
    # GENRE CLICK
    # ========================================================

    def handle_genre_click(
        self,
        event,
        genre_name
    ):

        if (
            event is not None
            and
            event.button()
            != Qt.LeftButton
        ):

            return

        genre_name = str(
            genre_name
            or ""
        ).strip()

        if not genre_name:

            return

        print(
            "LYRx genre selected:",
            genre_name
        )

        # ====================================================
        # IMPORTANT
        # ====================================================
        #
        # This now uses:
        #
        # ProviderRegistry.get_by_genre()
        #
        # instead of:
        #
        # search_online_music(genre_name)
        #

        self.request_online_music(
            mode="genre",
            query=genre_name,
            limit=12,
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

        title = str(
            getattr(
                song,
                "title",
                "Unknown Track"
            )
        )

        artist = str(
            getattr(
                song,
                "artist",
                "Unknown Artist"
            )
        )

        audio_url = str(
            getattr(
                song,
                "audio_url",
                ""
            )
            or ""
        )

        print()
        print(
            "=" * 60
        )

        print(
            "Discover ONLINE song selected:"
        )

        print(
            "Song:",
            title
        )

        print(
            "Artist:",
            artist
        )

        print(
            "Audio:",
            audio_url
        )

        print(
            "=" * 60
        )

        print()

        # ====================================================
        # SEND SONG OBJECT TO APP WINDOW
        # ====================================================

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
    # THEME STATE
    # ========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.is_dark = bool(
            is_dark
        )

        # ====================================================
        # SIDEBAR
        # ====================================================

        try:

            self.sidebar.set_theme_state(
                self.is_dark
            )

        except Exception as error:

            print(
                "Discover sidebar theme error:",
                error
            )

        # ====================================================
        # SCROLL
        # ====================================================

        self.apply_scroll_theme()

        # ====================================================
        # HEADER COLORS
        # ====================================================

        if self.is_dark:

            title_color = (
                "#FFFFFF"
            )

            subtitle_color = (
                "#AFA4C8"
            )

        else:

            title_color = (
                "#241B35"
            )

            subtitle_color = (
                "#766A89"
            )

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

        # ====================================================
        # BANNER
        # ====================================================

        self.apply_banner_theme()

        # ====================================================
        # SECTION TITLES
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

        # ====================================================
        # SECTION ACTIONS
        # ====================================================

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

        # ====================================================
        # MOODS
        # ====================================================

        self.apply_mood_theme()

        # ====================================================
        # GENRES
        # ====================================================

        self.apply_genre_theme()

        # ====================================================
        # STATUS
        # ====================================================

        self.apply_online_status_theme()

        # ====================================================
        # LOADING
        # ====================================================

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

                if hasattr(
                    card,
                    "set_theme_state"
                ):

                    card.set_theme_state(
                        self.is_dark
                    )

            except Exception as error:

                print(
                    "Discover MusicCard theme error:",
                    error
                )

        # ====================================================
        # REPAINT
        # ====================================================

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

            color = (
                "#8F84A6"
            )

        else:

            color = (
                "#756A88"
            )

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

            card_bg = (
                "#181329"
            )

            border = (
                "#30224B"
            )

            text_color = (
                "#756A91"
            )

            cover_bg = (
                "#211633"
            )

        else:

            card_bg = (
                "#F1EBFA"
            )

            border = (
                "#D7CBE8"
            )

            text_color = (
                "#8A7899"
            )

            cover_bg = (
                "#E5DCEB"
            )

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

        if self.is_dark:

            handle = (
                "#7C3AED"
            )

            hover = (
                "#9F67FF"
            )

        else:

            handle = (
                "#8B5CF6"
            )

            hover = (
                "#7040D4"
            )

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
                background: {handle};

                border-radius: 4px;

                min-height: 55px;
            }}


            QScrollBar::handle:vertical:hover {{
                background: {hover};
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

            banner_bg = (
                "#18122A"
            )

            border = (
                "#30224B"
            )

            hover_border = (
                "#53358A"
            )

            title = (
                "#FFFFFF"
            )

            subtitle = (
                "#AAA0C5"
            )

            icon = (
                "#A970FF"
            )

        else:

            banner_bg = (
                "#EDE6FA"
            )

            border = (
                "#D3C5EA"
            )

            hover_border = (
                "#B99BEA"
            )

            title = (
                "#281B3B"
            )

            subtitle = (
                "#756785"
            )

            icon = (
                "#7C3AED"
            )

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

            if not original_background:

                original_background = (
                    "#30224B"
                )

            if self.is_dark:

                hover_border = (
                    "#A970FF"
                )

                normal_border = (
                    "rgba(255,255,255,20)"
                )

            else:

                hover_border = (
                    "#7C3AED"
                )

                normal_border = (
                    "rgba(70,50,100,45)"
                )

            card.setStyleSheet(
                f"""
                QFrame#GenreCard {{

                    background: {original_background};

                    border-radius: 18px;

                    border: 1px solid {normal_border};
                }}


                QFrame#GenreCard:hover {{

                    border: 1px solid {hover_border};
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

        # ====================================================
        # GRADIENT
        # ====================================================

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
        # TOP GLOW
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

        # ====================================================
        # RIGHT GLOW
        # ====================================================

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