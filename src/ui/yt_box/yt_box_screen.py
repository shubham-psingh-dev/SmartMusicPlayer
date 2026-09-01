# ============================================================
# LYRx
# DAY 21 - YT BOX
#
# FILE 2
# yt_box_screen.py
#
# PURPOSE
# ------------------------------------------------------------
#
# Dedicated YouTube discovery screen for LYRx.
#
# FEATURES
# ------------------------------------------------------------
#
#   - Same LYRx dark/purple UI blueprint
#   - YouTube search bar
#   - Search button
#   - Enter-to-search
#   - Dynamic yt-dlp metadata search
#   - Thumbnail loading
#   - Title
#   - Channel / artist
#   - Duration
#   - Play / Open button
#   - Favorite button UI
#   - Add-to-playlist button UI
#   - Loading state
#   - Empty state
#   - Error state
#   - Responsive result grid
#
# IMPORTANT
# ------------------------------------------------------------
#
# This screen does NOT download/extract YouTube audio.
#
# Playback/open routing will be connected through AppWindow
# in the next integration files.
# ============================================================

from __future__ import annotations

from typing import (
    List,
    Optional,
)

from PySide6.QtCore import (
    Qt,
    Signal,
    QObject,
    QThread,
    QUrl,
)

from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPixmap,
)


from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QGridLayout,
)

from services.youtube_service import (
    YouTubeTrack,
    YouTubeService,
)


# ============================================================
# SEARCH WORKER
# ============================================================

class YouTubeSearchWorker(QObject):

    # --------------------------------------------------------
    # SIGNALS
    # --------------------------------------------------------

    finished = Signal(
        list
    )

    error = Signal(
        str
    )

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        query: str,
        limit: int = 20,
    ):

        super().__init__()

        self.query = str(
            query
            or ""
        ).strip()

        self.limit = limit

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self
    ):

        try:

            # ------------------------------------------------
            # Create service inside worker thread.
            # ------------------------------------------------

            service = (
                YouTubeService()
            )

            tracks = (
                service.search(

                    self.query,

                    limit=self.limit,
                )
            )

            if (
                not tracks
                and
                service.last_error
            ):

                self.error.emit(
                    service.last_error
                )

                return

            self.finished.emit(
                tracks
            )

        except Exception as error:

            self.error.emit(
                str(
                    error
                )
            )


# ============================================================
# YOUTUBE RESULT CARD
# ============================================================

class YouTubeResultCard(
    QFrame
):

    # --------------------------------------------------------
    # SIGNALS
    # --------------------------------------------------------

    play_requested = Signal(
        object
    )

    favorite_requested = Signal(
        object
    )

    playlist_requested = Signal(
        object
    )

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        track: YouTubeTrack,
        is_dark: bool = True,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.track = track

        self.current_is_dark = bool(
            is_dark
        )

        self.thumbnail_pixmap = None

        self.thumbnail_network = QNetworkAccessManager(
            self
        )

        self.thumbnail_reply = None

        self.thumbnail_fallback_used = False

        self.setObjectName(
            "YouTubeResultCard"
        )

        self.setMinimumWidth(
            205
        )

        self.setMaximumWidth(
            255
        )

        self.setFixedHeight(
            350
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.build_ui()

        self.set_theme_state(
            self.current_is_dark
        )

        self.load_thumbnail()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(
        self
    ):

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            12,
            12,
            12,
            12
        )

        root.setSpacing(
            8
        )

        # ====================================================
        # THUMBNAIL AREA
        # ====================================================

        self.thumbnail_frame = QFrame()

        self.thumbnail_frame.setObjectName(
            "ThumbnailFrame"
        )

        self.thumbnail_frame.setFixedHeight(
            150
        )

        thumbnail_layout = QVBoxLayout(
            self.thumbnail_frame
        )

        thumbnail_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        self.thumbnail = QLabel(
            "▶"
        )

        self.thumbnail.setAlignment(
            Qt.AlignCenter
        )

        self.thumbnail.setMinimumHeight(
            150
        )

        self.thumbnail.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        thumbnail_layout.addWidget(
            self.thumbnail
        )

        # ====================================================
        # TITLE
        # ====================================================

        self.title_label = QLabel(
            self.track.display_title()
        )

        self.title_label.setWordWrap(
            True
        )

        self.title_label.setMaximumHeight(
            44
        )

        self.title_label.setToolTip(
            self.track.display_title()
        )

        root.addWidget(
            self.title_label
        )

        # ====================================================
        # CHANNEL
        # ====================================================

        self.channel_label = QLabel(
            self.track.display_artist()
        )

        self.channel_label.setWordWrap(
            False
        )

        self.channel_label.setToolTip(
            self.track.display_artist()
        )

        root.addWidget(
            self.channel_label
        )

        # ====================================================
        # DURATION + SOURCE
        # ====================================================

        metadata_row = QHBoxLayout()

        metadata_row.setContentsMargins(
            0,
            0,
            0,
            0
        )

        metadata_row.setSpacing(
            6
        )

        self.duration_label = QLabel(
            self.track.duration_text()
        )

        metadata_row.addWidget(
            self.duration_label
        )

        metadata_row.addStretch()

        self.source_label = QLabel(
            "YouTube"
        )

        metadata_row.addWidget(
            self.source_label
        )

        root.addLayout(
            metadata_row
        )

        root.addStretch()

        # ====================================================
        # ACTION BUTTONS
        # ====================================================

        buttons = QHBoxLayout()

        buttons.setContentsMargins(
            0,
            0,
            0,
            0
        )

        buttons.setSpacing(
            7
        )

        # ----------------------------------------------------
        # PLAY
        # ----------------------------------------------------

        self.play_button = QPushButton(
            "▶  Play"
        )

        self.play_button.setCursor(
            Qt.PointingHandCursor
        )

        self.play_button.setToolTip(
            "Open this track"
        )

        self.play_button.clicked.connect(
            self.handle_play
        )

        buttons.addWidget(
            self.play_button,
            1
        )

        # ----------------------------------------------------
        # FAVORITE
        # ----------------------------------------------------

        self.favorite_button = QPushButton(
            "♡"
        )

        self.favorite_button.setFixedSize(
            38,
            38
        )

        self.favorite_button.setCursor(
            Qt.PointingHandCursor
        )

        self.favorite_button.setToolTip(
            "Add to Favorites"
        )

        self.favorite_button.clicked.connect(
            self.handle_favorite
        )

        buttons.addWidget(
            self.favorite_button
        )

        # ----------------------------------------------------
        # PLAYLIST
        # ----------------------------------------------------

        self.playlist_button = QPushButton(
            "+"
        )

        self.playlist_button.setFixedSize(
            38,
            38
        )

        self.playlist_button.setCursor(
            Qt.PointingHandCursor
        )

        self.playlist_button.setToolTip(
            "Add to Playlist"
        )

        self.playlist_button.clicked.connect(
            self.handle_playlist
        )

        buttons.addWidget(
            self.playlist_button
        )

        root.addLayout(
            buttons
        )

    # ========================================================
    # PLAY
    # ========================================================

    def handle_play(
        self
    ):

        self.play_requested.emit(
            self.track
        )

    # ========================================================
    # FAVORITE
    # ========================================================

    def handle_favorite(
        self
    ):

        self.favorite_requested.emit(
            self.track
        )

    # ========================================================
    # PLAYLIST
    # ========================================================

    def handle_playlist(
        self
    ):

        self.playlist_requested.emit(
            self.track
        )

    # ========================================================
    # LOAD THUMBNAIL
    # ========================================================

    def load_thumbnail(
        self
    ):

        url = str(
            getattr(
                self.track,
                "thumbnail_url",
                ""
            )
            or ""
        ).strip()

        # yt-dlp search metadata can occasionally return no usable
        # thumbnail URL. YouTube's deterministic video thumbnail is
        # a safe metadata/image fallback for the known video id.
        if not url:

            video_id = str(
                getattr(
                    self.track,
                    "video_id",
                    ""
                )
                or ""
            ).strip()

            if video_id:

                url = (
                    "https://i.ytimg.com/vi/"
                    f"{video_id}/hqdefault.jpg"
                )

        if not url:

            return

        self.request_thumbnail(
            url
        )

    # ========================================================
    # REQUEST THUMBNAIL
    # ========================================================

    def request_thumbnail(
        self,
        image_url
    ):

        image_url = str(
            image_url
            or ""
        ).strip()

        if not image_url:

            return

        if self.thumbnail_reply is not None:

            try:

                if self.thumbnail_reply.isRunning():

                    self.thumbnail_reply.abort()

            except Exception:

                pass

            self.thumbnail_reply = None

        url = QUrl.fromUserInput(
            image_url
        )

        if not url.isValid():

            self.try_thumbnail_fallback()

            return

        request = QNetworkRequest(
            url
        )

        request.setRawHeader(
            b"User-Agent",
            b"Mozilla/5.0 LYRx/0.2"
        )

        request.setRawHeader(
            b"Accept",
            b"image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        )

        request.setRawHeader(
            b"Referer",
            b"https://www.youtube.com/"
        )

        self.thumbnail_reply = (
            self.thumbnail_network
            .get(
                request
            )
        )

        self.thumbnail_reply.finished.connect(
            self.thumbnail_loaded
        )

    # ========================================================
    # THUMBNAIL LOADED
    # ========================================================

    def thumbnail_loaded(
        self
    ):

        reply = self.sender()

        if reply is None:

            return

        try:

            if (
                reply.error()
                !=
                QNetworkReply.NetworkError.NoError
            ):

                print(
                    "YT BOX thumbnail network error:",
                    self.track.display_title(),
                    "-",
                    reply.errorString()
                )

                self.try_thumbnail_fallback()

                return

            data = bytes(
                reply.readAll()
            )

            pixmap = QPixmap()

            if not pixmap.loadFromData(
                data
            ):

                print(
                    "YT BOX thumbnail decode failed:",
                    self.track.display_title()
                )

                self.try_thumbnail_fallback()

                return

            self.thumbnail_pixmap = (
                pixmap
            )

            self.thumbnail.clear()

            self.apply_thumbnail()

        except RuntimeError:

            pass

        except Exception as error:

            print(
                "YT BOX thumbnail error:",
                self.track.display_title(),
                "-",
                error
            )

            self.try_thumbnail_fallback()

        finally:

            try:

                reply.deleteLater()

            except Exception:

                pass

            if reply is self.thumbnail_reply:

                self.thumbnail_reply = None

    # ========================================================
    # FALLBACK THUMBNAIL
    # ========================================================

    def try_thumbnail_fallback(
        self
    ):

        if self.thumbnail_fallback_used:

            return

        video_id = str(
            getattr(
                self.track,
                "video_id",
                ""
            )
            or ""
        ).strip()

        if not video_id:

            return

        self.thumbnail_fallback_used = True

        fallback_url = (
            "https://i.ytimg.com/vi/"
            f"{video_id}/hqdefault.jpg"
        )

        self.request_thumbnail(
            fallback_url
        )

    # ========================================================
    # APPLY THUMBNAIL
    # ========================================================

    def apply_thumbnail(
        self
    ):

        if (
            self.thumbnail_pixmap is None
            or
            self.thumbnail_pixmap.isNull()
        ):

            return

        width = max(
            1,
            self.thumbnail.width()
        )

        height = max(
            1,
            self.thumbnail.height()
        )

        scaled = (
            self.thumbnail_pixmap.scaled(

                width,
                height,

                Qt.KeepAspectRatioByExpanding,

                Qt.SmoothTransformation,
            )
        )

        self.thumbnail.setPixmap(
            scaled
        )

    # ========================================================
    # RESIZE
    # ========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        self.apply_thumbnail()

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_state(
        self,
        is_dark: bool
    ):

        self.current_is_dark = bool(
            is_dark
        )

        # ====================================================
        # DARK
        # ====================================================

        if self.current_is_dark:

            self.setStyleSheet(
                """
                QFrame#YouTubeResultCard {
                    background: #171126;
                    border: 1px solid #33254E;
                    border-radius: 18px;
                }

                QFrame#YouTubeResultCard:hover {
                    background: #1E1531;
                    border: 1px solid #7C3AED;
                }

                QFrame#ThumbnailFrame {
                    background: #211733;
                    border: none;
                    border-radius: 13px;
                }
                """
            )

            self.thumbnail.setStyleSheet(
                """
                QLabel {
                    background: #211733;
                    color: #9B6CFF;
                    border-radius: 13px;
                    font-size: 35px;
                    font-weight: 700;
                }
                """
            )

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #FFFFFF;
                    background: transparent;
                    border: none;
                    font-size: 14px;
                    font-weight: 700;
                }
                """
            )

            self.channel_label.setStyleSheet(
                """
                QLabel {
                    color: #B5A9CC;
                    background: transparent;
                    border: none;
                    font-size: 12px;
                }
                """
            )

            self.duration_label.setStyleSheet(
                """
                QLabel {
                    color: #8E82A7;
                    background: transparent;
                    border: none;
                    font-size: 11px;
                }
                """
            )

            self.source_label.setStyleSheet(
                """
                QLabel {
                    color: #A970FF;
                    background: transparent;
                    border: none;
                    font-size: 11px;
                    font-weight: 700;
                }
                """
            )

        # ====================================================
        # LIGHT
        # ====================================================

        else:

            self.setStyleSheet(
                """
                QFrame#YouTubeResultCard {
                    background: #FAF8FC;
                    border: 1px solid #DED3E8;
                    border-radius: 18px;
                }

                QFrame#YouTubeResultCard:hover {
                    background: #F5F0FA;
                    border: 1px solid #8B5CF6;
                }

                QFrame#ThumbnailFrame {
                    background: #EEE8F5;
                    border: none;
                    border-radius: 13px;
                }
                """
            )

            self.thumbnail.setStyleSheet(
                """
                QLabel {
                    background: #EEE8F5;
                    color: #7C3AED;
                    border-radius: 13px;
                    font-size: 35px;
                    font-weight: 700;
                }
                """
            )

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #302744;
                    background: transparent;
                    border: none;
                    font-size: 14px;
                    font-weight: 700;
                }
                """
            )

            self.channel_label.setStyleSheet(
                """
                QLabel {
                    color: #756A88;
                    background: transparent;
                    border: none;
                    font-size: 12px;
                }
                """
            )

            self.duration_label.setStyleSheet(
                """
                QLabel {
                    color: #8A7C9C;
                    background: transparent;
                    border: none;
                    font-size: 11px;
                }
                """
            )

            self.source_label.setStyleSheet(
                """
                QLabel {
                    color: #7C3AED;
                    background: transparent;
                    border: none;
                    font-size: 11px;
                    font-weight: 700;
                }
                """
            )

        # ====================================================
        # BUTTONS
        # ====================================================

        self.apply_button_theme()

    # ========================================================
    # BUTTON THEME
    # ========================================================

    def apply_button_theme(
        self
    ):

        self.play_button.setStyleSheet(
            """
            QPushButton {
                background: #7C3AED;
                color: white;

                border: 1px solid #8B5CF6;
                border-radius: 19px;

                min-height: 38px;

                padding-left: 13px;
                padding-right: 13px;

                font-size: 12px;
                font-weight: 700;
            }

            QPushButton:hover {
                background: #8B5CF6;
                border: 1px solid #A78BFA;
            }

            QPushButton:pressed {
                background: #6D28D9;
            }
            """
        )

        if self.current_is_dark:

            small_button_style = """
            QPushButton {
                background: #211A35;
                color: #D9D2E8;

                border: 1px solid #392A55;
                border-radius: 19px;

                font-size: 18px;
                font-weight: 600;

                padding: 0px;
            }

            QPushButton:hover {
                background: #30204F;
                color: white;
                border: 1px solid #7C3AED;
            }

            QPushButton:pressed {
                background: #7C3AED;
                color: white;
            }
            """

        else:

            small_button_style = """
            QPushButton {
                background: #F0EAF5;
                color: #594C6B;

                border: 1px solid #D6C9E2;
                border-radius: 19px;

                font-size: 18px;
                font-weight: 600;

                padding: 0px;
            }

            QPushButton:hover {
                background: #E8DDF2;
                color: #7C3AED;
                border: 1px solid #8B5CF6;
            }

            QPushButton:pressed {
                background: #7C3AED;
                color: white;
            }
            """

        self.favorite_button.setStyleSheet(
            small_button_style
        )

        self.playlist_button.setStyleSheet(
            small_button_style
        )


# ============================================================
# YT BOX SCREEN
# ============================================================

class YTBoxScreen(
    QWidget
):

    # --------------------------------------------------------
    # Signals forwarded to AppWindow.
    # --------------------------------------------------------

    play_requested = Signal(
        object
    )

    favorite_requested = Signal(
        object
    )

    playlist_requested = Signal(
        object
    )

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.current_is_dark = True

        # ----------------------------------------------------
        # Search data
        # ----------------------------------------------------

        self.current_query = ""

        self.current_tracks: List[
            YouTubeTrack
        ] = []

        self.result_cards: List[
            YouTubeResultCard
        ] = []

        # ----------------------------------------------------
        # Thread references
        # ----------------------------------------------------

        self.search_thread: Optional[
            QThread
        ] = None

        self.search_worker: Optional[
            YouTubeSearchWorker
        ] = None

        self.search_in_progress = False

        # ----------------------------------------------------
        # Responsive columns
        # ----------------------------------------------------

        self.current_columns = 4

        # ----------------------------------------------------
        # Build
        # ----------------------------------------------------

        self.build_ui()

        self.set_theme_state(
            True
        )

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(
        self
    ):

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            30,
            26,
            26,
            24
        )

        root.setSpacing(
            18
        )

        # ====================================================
        # PAGE TITLE
        # ====================================================

        title_row = QHBoxLayout()

        title_row.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.page_title = QLabel(
            "YT BOX"
        )

        title_row.addWidget(
            self.page_title
        )

        title_row.addStretch()

        self.live_label = QLabel(
            "●  YouTube"
        )

        title_row.addWidget(
            self.live_label
        )

        root.addLayout(
            title_row
        )

        # ====================================================
        # SUBTITLE
        # ====================================================

        self.subtitle = QLabel(
            "Search music and videos across YouTube."
        )

        root.addWidget(
            self.subtitle
        )

        # ====================================================
        # SEARCH PANEL
        # ====================================================

        self.search_panel = QFrame()

        self.search_panel.setObjectName(
            "SearchPanel"
        )

        search_panel_layout = QVBoxLayout(
            self.search_panel
        )

        search_panel_layout.setContentsMargins(
            22,
            20,
            22,
            20
        )

        search_panel_layout.setSpacing(
            13
        )

        # ----------------------------------------------------
        # LABEL
        # ----------------------------------------------------

        self.search_heading = QLabel(
            "Find Your Music"
        )

        search_panel_layout.addWidget(
            self.search_heading
        )

        self.search_description = QLabel(
            "Search by song, artist, album, live performance "
            "or music video."
        )

        self.search_description.setWordWrap(
            True
        )

        search_panel_layout.addWidget(
            self.search_description
        )

        # ----------------------------------------------------
        # SEARCH ROW
        # ----------------------------------------------------

        search_row = QHBoxLayout()

        search_row.setContentsMargins(
            0,
            4,
            0,
            0
        )

        search_row.setSpacing(
            10
        )

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Search YouTube..."
        )

        self.search_input.setClearButtonEnabled(
            True
        )

        self.search_input.setFixedHeight(
            46
        )

        self.search_input.returnPressed.connect(
            self.start_search
        )

        search_row.addWidget(
            self.search_input,
            1
        )

        self.search_button = QPushButton(
            "Search"
        )

        self.search_button.setFixedSize(
            110,
            46
        )

        self.search_button.setCursor(
            Qt.PointingHandCursor
        )

        self.search_button.clicked.connect(
            self.start_search
        )

        search_row.addWidget(
            self.search_button
        )

        search_panel_layout.addLayout(
            search_row
        )

        root.addWidget(
            self.search_panel
        )

        # ====================================================
        # RESULTS HEADER
        # ====================================================

        results_header = QHBoxLayout()

        results_header.setContentsMargins(
            0,
            3,
            0,
            0
        )

        self.results_title = QLabel(
            "Discover on YouTube"
        )

        results_header.addWidget(
            self.results_title
        )

        results_header.addStretch()

        self.results_count = QLabel(
            ""
        )

        results_header.addWidget(
            self.results_count
        )

        root.addLayout(
            results_header
        )

        # ====================================================
        # SCROLL AREA
        # ====================================================

        self.scroll = QScrollArea()

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

        # ----------------------------------------------------
        # CONTENT
        # ----------------------------------------------------

        self.scroll_content = QWidget()

        self.scroll_content.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.scroll.setWidget(
            self.scroll_content
        )

        self.content_layout = QVBoxLayout(
            self.scroll_content
        )

        self.content_layout.setContentsMargins(
            0,
            0,
            8,
            30
        )

        self.content_layout.setSpacing(
            18
        )

        self.content_layout.setAlignment(
            Qt.AlignTop
        )

        # ====================================================
        # STATUS PANEL
        # ====================================================

        self.status_panel = QFrame()

        self.status_panel.setObjectName(
            "StatusPanel"
        )

        self.status_panel.setMinimumHeight(
            180
        )

        status_layout = QVBoxLayout(
            self.status_panel
        )

        status_layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        status_layout.setSpacing(
            10
        )

        status_layout.setAlignment(
            Qt.AlignCenter
        )

        self.status_icon = QLabel(
            "♫"
        )

        self.status_icon.setAlignment(
            Qt.AlignCenter
        )

        status_layout.addWidget(
            self.status_icon
        )

        self.status_title = QLabel(
            "Search the YouTube catalog"
        )

        self.status_title.setAlignment(
            Qt.AlignCenter
        )

        status_layout.addWidget(
            self.status_title
        )

        self.status_message = QLabel(
            "Try searching for an artist or song."
        )

        self.status_message.setAlignment(
            Qt.AlignCenter
        )

        self.status_message.setWordWrap(
            True
        )

        status_layout.addWidget(
            self.status_message
        )

        self.content_layout.addWidget(
            self.status_panel
        )

        # ====================================================
        # RESULT GRID
        # ====================================================

        self.results_widget = QWidget()

        self.results_widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.results_grid = QGridLayout(
            self.results_widget
        )

        self.results_grid.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.results_grid.setHorizontalSpacing(
            16
        )

        self.results_grid.setVerticalSpacing(
            16
        )

        self.results_grid.setAlignment(
            Qt.AlignTop |
            Qt.AlignLeft
        )

        self.results_widget.hide()

        self.content_layout.addWidget(
            self.results_widget
        )

        root.addWidget(
            self.scroll,
            1
        )

    # ========================================================
    # START SEARCH
    # ========================================================

    def start_search(
        self
    ):

        query = (
            self.search_input
            .text()
            .strip()
        )

        if not query:

            self.show_status(

                icon="⌕",

                title="Type something to search",

                message=(
                    "Search by song, artist, album "
                    "or music video."
                ),
            )

            return

        # ----------------------------------------------------
        # Prevent duplicate click while worker is active.
        # ----------------------------------------------------

        if self.search_in_progress:

            return

        self.current_query = (
            query
        )

        self.search_in_progress = True

        self.search_button.setEnabled(
            False
        )

        self.search_input.setEnabled(
            False
        )

        self.results_title.setText(
            f'Search · "{query}"'
        )

        self.results_count.setText(
            ""
        )

        self.clear_results()

        self.show_status(

            icon="◌",

            title="Searching YouTube...",

            message=(
                f'Finding results for "{query}"'
            ),
        )

        # ====================================================
        # THREAD
        # ====================================================

        self.search_thread = (
            QThread()
        )

        self.search_worker = (
            YouTubeSearchWorker(

                query=query,

                limit=20,
            )
        )

        self.search_worker.moveToThread(
            self.search_thread
        )

        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        self.search_thread.started.connect(
            self.search_worker.run
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        self.search_worker.finished.connect(
            self.handle_search_results
        )

        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        self.search_worker.error.connect(
            self.handle_search_error
        )

        # ----------------------------------------------------
        # CLEANUP
        # ----------------------------------------------------

        self.search_worker.finished.connect(
            self.search_thread.quit
        )

        self.search_worker.error.connect(
            self.search_thread.quit
        )

        self.search_worker.finished.connect(
            self.search_worker.deleteLater
        )

        self.search_worker.error.connect(
            self.search_worker.deleteLater
        )

        self.search_thread.finished.connect(
            self.search_thread.deleteLater
        )

        self.search_thread.finished.connect(
            self.search_finished
        )

        self.search_thread.start()

    # ========================================================
    # SEARCH FINISHED
    # ========================================================

    def search_finished(
        self
    ):

        self.search_in_progress = False

        self.search_button.setEnabled(
            True
        )

        self.search_input.setEnabled(
            True
        )

        self.search_worker = None

        self.search_thread = None

        self.search_input.setFocus()

    # ========================================================
    # SEARCH RESULTS
    # ========================================================

    def handle_search_results(
        self,
        tracks
    ):

        self.current_tracks = list(
            tracks
            or []
        )

        # ----------------------------------------------------
        # EMPTY
        # ----------------------------------------------------

        if not self.current_tracks:

            self.results_count.setText(
                "0 results"
            )

            self.show_status(

                icon="♫",

                title="No results found",

                message=(
                    "Try another song, artist "
                    "or search phrase."
                ),
            )

            return

        # ----------------------------------------------------
        # COUNT
        # ----------------------------------------------------

        count = len(
            self.current_tracks
        )

        word = (
            "result"
            if count == 1
            else "results"
        )

        self.results_count.setText(
            f"{count} {word}"
        )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        self.status_panel.hide()

        self.results_widget.show()

        self.rebuild_grid()

    # ========================================================
    # SEARCH ERROR
    # ========================================================

    def handle_search_error(
        self,
        error
    ):

        print()
        print("=" * 60)

        print(
            "LYRx YT BOX SEARCH ERROR"
        )

        print(
            error
        )

        print("=" * 60)
        print()

        self.current_tracks = []

        self.results_count.setText(
            ""
        )

        self.show_status(

            icon="⚠",

            title="YouTube search unavailable",

            message=(
                "LYRx couldn't load YouTube results.\n\n"
                f"{error}"
            ),
        )

    # ========================================================
    # SHOW STATUS
    # ========================================================

    def show_status(
        self,
        icon: str,
        title: str,
        message: str,
    ):

        self.results_widget.hide()

        self.status_icon.setText(
            icon
        )

        self.status_title.setText(
            title
        )

        self.status_message.setText(
            message
        )

        self.status_panel.show()

    # ========================================================
    # CLEAR RESULTS
    # ========================================================

    def clear_results(
        self
    ):

        self.result_cards = []

        while (
            self.results_grid.count()
        ):

            item = (
                self.results_grid
                .takeAt(
                    0
                )
            )

            widget = (
                item.widget()
            )

            if widget is not None:

                widget.deleteLater()

    # ========================================================
    # CALCULATE COLUMNS
    # ========================================================

    def calculate_columns(
        self
    ) -> int:

        width = (
            self.scroll.viewport().width()
        )

        # ----------------------------------------------------
        # Keep cards comfortable at different app sizes.
        # ----------------------------------------------------

        if width >= 1150:

            return 5

        if width >= 900:

            return 4

        if width >= 680:

            return 3

        if width >= 450:

            return 2

        return 1

    # ========================================================
    # REBUILD GRID
    # ========================================================

    def rebuild_grid(
        self
    ):

        if not self.current_tracks:

            return

        # ----------------------------------------------------
        # Delete existing cards.
        # ----------------------------------------------------

        self.clear_results()

        self.current_columns = (
            self.calculate_columns()
        )

        # ====================================================
        # CREATE CARDS
        # ====================================================

        for (
            index,
            track
        ) in enumerate(
            self.current_tracks
        ):

            card = (
                YouTubeResultCard(

                    track=track,

                    is_dark=(
                        self.current_is_dark
                    ),
                )
            )

            # ------------------------------------------------
            # PLAY
            # ------------------------------------------------

            card.play_requested.connect(
                self.handle_play_requested
            )

            # ------------------------------------------------
            # FAVORITE
            # ------------------------------------------------

            card.favorite_requested.connect(
                self.handle_favorite_requested
            )

            # ------------------------------------------------
            # PLAYLIST
            # ------------------------------------------------

            card.playlist_requested.connect(
                self.handle_playlist_requested
            )

            row = (
                index
                //
                self.current_columns
            )

            column = (
                index
                %
                self.current_columns
            )

            self.results_grid.addWidget(

                card,

                row,

                column,
            )

            self.result_cards.append(
                card
            )

        # ----------------------------------------------------
        # Stretch unused horizontal space.
        # ----------------------------------------------------

        for column in range(
            self.current_columns
        ):

            self.results_grid.setColumnStretch(
                column,
                1
            )

    # ========================================================
    # PLAY REQUEST
    # ========================================================

    def handle_play_requested(
        self,
        track
    ):

        print()
        print("=" * 60)

        print(
            "YT BOX PLAY REQUEST"
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
            "URL:",
            track.youtube_url()
        )

        print("=" * 60)
        print()

        self.play_requested.emit(
            track
        )

    # ========================================================
    # FAVORITE REQUEST
    # ========================================================

    def handle_favorite_requested(
        self,
        track
    ):

        print(
            "YT BOX favorite requested:",
            track.title
        )

        self.favorite_requested.emit(
            track
        )

    # ========================================================
    # PLAYLIST REQUEST
    # ========================================================

    def handle_playlist_requested(
        self,
        track
    ):

        print(
            "YT BOX playlist requested:",
            track.title
        )

        self.playlist_requested.emit(
            track
        )

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.current_is_dark = bool(
            is_dark
        )

        # ====================================================
        # PAGE TEXT
        # ====================================================

        self.page_title.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#FFFFFF"
                    if self.current_is_dark
                    else "#302744"
                };

                background: transparent;

                font-size: 34px;
                font-weight: 800;
            }}
            """
        )

        self.subtitle.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#B5A9CC"
                    if self.current_is_dark
                    else "#756A88"
                };

                background: transparent;

                font-size: 13px;
            }}
            """
        )

        self.live_label.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#A970FF"
                    if self.current_is_dark
                    else "#7C3AED"
                };

                background: transparent;

                font-size: 12px;
                font-weight: 700;
            }}
            """
        )

        # ====================================================
        # SEARCH PANEL
        # ====================================================

        if self.current_is_dark:

            self.search_panel.setStyleSheet(
                """
                QFrame#SearchPanel {
                    background: #171126;
                    border: 1px solid #33254E;
                    border-radius: 20px;
                }
                """
            )

        else:

            self.search_panel.setStyleSheet(
                """
                QFrame#SearchPanel {
                    background: #FAF8FC;
                    border: 1px solid #DED3E8;
                    border-radius: 20px;
                }
                """
            )

        self.search_heading.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#FFFFFF"
                    if self.current_is_dark
                    else "#302744"
                };

                background: transparent;

                font-size: 21px;
                font-weight: 800;
            }}
            """
        )

        self.search_description.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#A99EBE"
                    if self.current_is_dark
                    else "#756A88"
                };

                background: transparent;

                font-size: 12px;
            }}
            """
        )

        # ====================================================
        # SEARCH INPUT
        # ====================================================

        if self.current_is_dark:

            self.search_input.setStyleSheet(
                """
                QLineEdit {
                    background: #211A35;
                    color: white;

                    border: 1px solid #3A2B58;
                    border-radius: 23px;

                    padding-left: 18px;
                    padding-right: 18px;

                    font-size: 13px;

                    selection-background-color: #7C3AED;
                }

                QLineEdit:hover {
                    background: #241C3A;
                    border: 1px solid #513A79;
                }

                QLineEdit:focus {
                    background: #241C3A;
                    border: 1px solid #7C3AED;
                }

                QLineEdit:disabled {
                    color: #817792;
                }
                """
            )

        else:

            self.search_input.setStyleSheet(
                """
                QLineEdit {
                    background: #FFFFFF;
                    color: #302744;

                    border: 1px solid #D6C9E2;
                    border-radius: 23px;

                    padding-left: 18px;
                    padding-right: 18px;

                    font-size: 13px;

                    selection-background-color: #8B5CF6;
                }

                QLineEdit:hover {
                    border: 1px solid #B69ADB;
                }

                QLineEdit:focus {
                    border: 1px solid #7C3AED;
                }

                QLineEdit:disabled {
                    color: #A79DB1;
                }
                """
            )

        # ====================================================
        # SEARCH BUTTON
        # ====================================================

        self.search_button.setStyleSheet(
            """
            QPushButton {
                background: #7C3AED;
                color: white;

                border: 1px solid #8B5CF6;
                border-radius: 23px;

                font-size: 13px;
                font-weight: 700;
            }

            QPushButton:hover {
                background: #8B5CF6;
                border: 1px solid #A78BFA;
            }

            QPushButton:pressed {
                background: #6D28D9;
            }

            QPushButton:disabled {
                background: #4C3B69;
                color: #9E94AD;
                border: 1px solid #57466F;
            }
            """
        )

        # ====================================================
        # RESULTS HEADER
        # ====================================================

        self.results_title.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#FFFFFF"
                    if self.current_is_dark
                    else "#302744"
                };

                background: transparent;

                font-size: 22px;
                font-weight: 800;
            }}
            """
        )

        self.results_count.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#A970FF"
                    if self.current_is_dark
                    else "#7C3AED"
                };

                background: transparent;

                font-size: 12px;
                font-weight: 700;
            }}
            """
        )

        # ====================================================
        # STATUS
        # ====================================================

        if self.current_is_dark:

            self.status_panel.setStyleSheet(
                """
                QFrame#StatusPanel {
                    background: #151024;
                    border: 1px solid #30234A;
                    border-radius: 18px;
                }
                """
            )

        else:

            self.status_panel.setStyleSheet(
                """
                QFrame#StatusPanel {
                    background: #FAF8FC;
                    border: 1px solid #DED3E8;
                    border-radius: 18px;
                }
                """
            )

        self.status_icon.setStyleSheet(
            """
            QLabel {
                color: #A970FF;
                background: transparent;
                font-size: 28px;
                font-weight: 700;
            }
            """
        )

        self.status_title.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#D9D1E8"
                    if self.current_is_dark
                    else "#4B3F5D"
                };

                background: transparent;

                font-size: 15px;
                font-weight: 700;
            }}
            """
        )

        self.status_message.setStyleSheet(
            f"""
            QLabel {{
                color: {
                    "#998EAE"
                    if self.current_is_dark
                    else "#756A88"
                };

                background: transparent;

                font-size: 12px;
            }}
            """
        )

        # ====================================================
        # SCROLLBAR
        # ====================================================

        self.scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea > QWidget > QWidget {
                background: transparent;
            }

            QScrollBar:vertical {
                width: 9px;
                background: transparent;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #7C3AED;
                border-radius: 4px;
                min-height: 55px;
            }

            QScrollBar::handle:vertical:hover {
                background: #9F67FF;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

        # ====================================================
        # EXISTING CARDS
        # ====================================================

        for card in (
            self.result_cards
        ):

            try:

                card.set_theme_state(
                    self.current_is_dark
                )

            except Exception as error:

                print(
                    "YT BOX card theme error:",
                    error
                )

        self.update()

    # ========================================================
    # RESIZE
    # ========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        if not self.current_tracks:

            return

        new_columns = (
            self.calculate_columns()
        )

        if (
            new_columns
            !=
            self.current_columns
        ):

            self.rebuild_grid()

    # ========================================================
    # PAINT EVENT
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

        rect = (
            self.rect()
        )

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        # ====================================================
        # DARK
        # ====================================================

        if self.current_is_dark:

            gradient.setColorAt(
                0.0,
                QColor(
                    "#0B0913"
                )
            )

            gradient.setColorAt(
                0.5,
                QColor(
                    "#121020"
                )
            )

            gradient.setColorAt(
                1.0,
                QColor(
                    "#09070F"
                )
            )

        # ====================================================
        # LIGHT
        # ====================================================

        else:

            gradient.setColorAt(
                0.0,
                QColor(
                    "#EEE9F4"
                )
            )

            gradient.setColorAt(
                0.5,
                QColor(
                    "#E8E0F0"
                )
            )

            gradient.setColorAt(
                1.0,
                QColor(
                    "#F2EDF6"
                )
            )

        painter.fillRect(
            rect,
            gradient
        )

        # ====================================================
        # PURPLE GLOW
        # ====================================================

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                124,
                58,
                237,
                22
                if self.current_is_dark
                else 10
            )
        )

        painter.drawEllipse(
            rect.width() - 430,
            70,
            520,
            520
        )

        painter.end()

        super().paintEvent(
            event
        )