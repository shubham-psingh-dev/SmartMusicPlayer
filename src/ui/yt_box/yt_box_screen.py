# ============================================================
# LYRx
# DAY 22 - YT BOX
#
# FILE 2
# yt_box_screen.py
#
# PURPOSE
# ------------------------------------------------------------
#
# Dedicated YouTube discovery screen for LYRx.
#
# DAY 22 FEATURES
# ------------------------------------------------------------
#
#   - YouTube metadata search
#   - Background search worker
#   - Responsive result grid
#   - Reliable asynchronous thumbnail loading
#   - Multiple thumbnail fallbacks
#   - Play request
#   - Favorite request
#   - Add-to-playlist request
#   - Dark / Light theme
#   - Loading / empty / error states
#
# IMPORTANT
# ------------------------------------------------------------
#
# This screen does NOT download or extract YouTube audio.
#
# Actual playback routing is handled by AppWindow.
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

            # Service is deliberately created inside worker
            # thread so yt-dlp work remains outside UI thread.

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

        # ----------------------------------------------------
        # Thumbnail state
        # ----------------------------------------------------

        self.thumbnail_pixmap = None

        self.thumbnail_network = (
            QNetworkAccessManager(
                self
            )
        )

        self.thumbnail_reply = None

        self.thumbnail_urls = []

        self.thumbnail_index = -1

        # ----------------------------------------------------
        # Card
        # ----------------------------------------------------

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
        # THUMBNAIL
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

        self.thumbnail.setScaledContents(
            False
        )

        thumbnail_layout.addWidget(
            self.thumbnail
        )

        root.addWidget(
            self.thumbnail_frame
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
        # METADATA
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
        # BUTTONS
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
            "Play this track"
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
    # BUILD THUMBNAIL LIST
    # ========================================================

    def build_thumbnail_candidates(
        self
    ):

        candidates = []

        # ----------------------------------------------------
        # Day 22 YouTubeTrack method
        # ----------------------------------------------------

        try:

            method = getattr(
                self.track,
                "thumbnail_candidates",
                None
            )

            if callable(
                method
            ):

                track_candidates = (
                    method()
                    or []
                )

                for candidate in (
                    track_candidates
                ):

                    candidate = str(
                        candidate
                        or ""
                    ).strip()

                    if (
                        candidate
                        and
                        candidate not in candidates
                    ):

                        candidates.append(
                            candidate
                        )

        except Exception as error:

            print(
                "YT BOX thumbnail candidate error:",
                error
            )

        # ----------------------------------------------------
        # Direct metadata thumbnail
        # ----------------------------------------------------

        direct_url = str(
            getattr(
                self.track,
                "thumbnail_url",
                ""
            )
            or ""
        ).strip()

        if (
            direct_url
            and
            direct_url not in candidates
        ):

            candidates.insert(
                0,
                direct_url
            )

        # ----------------------------------------------------
        # Manual fallback list
        # ----------------------------------------------------

        video_id = str(
            getattr(
                self.track,
                "video_id",
                ""
            )
            or ""
        ).strip()

        if video_id:

            fallback_names = (

                "maxresdefault.jpg",

                "hqdefault.jpg",

                "mqdefault.jpg",

                "default.jpg",
            )

            for filename in (
                fallback_names
            ):

                url = (
                    "https://i.ytimg.com/vi/"
                    +
                    video_id
                    +
                    "/"
                    +
                    filename
                )

                if url not in candidates:

                    candidates.append(
                        url
                    )

        return candidates

    # ========================================================
    # LOAD THUMBNAIL
    # ========================================================

    def load_thumbnail(
        self
    ):

        self.thumbnail_urls = (
            self.build_thumbnail_candidates()
        )

        self.thumbnail_index = -1

        if not self.thumbnail_urls:

            self.show_thumbnail_placeholder()

            return

        self.request_next_thumbnail()

    # ========================================================
    # NEXT THUMBNAIL
    # ========================================================

    def request_next_thumbnail(
        self
    ):

        self.thumbnail_index += 1

        if (
            self.thumbnail_index
            >=
            len(
                self.thumbnail_urls
            )
        ):

            self.show_thumbnail_placeholder()

            return

        image_url = (
            self.thumbnail_urls[
                self.thumbnail_index
            ]
        )

        self.request_thumbnail(
            image_url
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

            self.request_next_thumbnail()

            return

        url = QUrl(
            image_url
        )

        if (
            not url.isValid()
            or
            url.scheme() not in (
                "http",
                "https",
            )
        ):

            self.request_next_thumbnail()

            return

        request = QNetworkRequest(
            url
        )

        # ----------------------------------------------------
        # Normal browser-like headers.
        #
        # We deliberately do not force a Referer here because
        # i.ytimg.com thumbnails are public image resources and
        # some environments behave better without it.
        # ----------------------------------------------------

        request.setRawHeader(
            b"User-Agent",
            (
                b"Mozilla/5.0 "
                b"(Windows NT 10.0; Win64; x64) "
                b"AppleWebKit/537.36 "
                b"Chrome/131.0 Safari/537.36"
            )
        )

        request.setRawHeader(
            b"Accept",
            (
                b"image/avif,"
                b"image/webp,"
                b"image/apng,"
                b"image/*,"
                b"*/*;q=0.8"
            )
        )

        reply = (
            self.thumbnail_network
            .get(
                request
            )
        )

        self.thumbnail_reply = (
            reply
        )

        reply.finished.connect(
            lambda current_reply=reply:
            self.thumbnail_loaded(
                current_reply
            )
        )

    # ========================================================
    # THUMBNAIL RESPONSE
    # ========================================================

    def thumbnail_loaded(
        self,
        reply
    ):

        # ----------------------------------------------------
        # Ignore an old/stale reply.
        # ----------------------------------------------------

        if reply is None:

            return

        is_current_reply = (
            reply
            is
            self.thumbnail_reply
        )

        if is_current_reply:

            self.thumbnail_reply = None

        success = False

        try:

            if (
                reply.error()
                ==
                QNetworkReply.NetworkError.NoError
            ):

                data = bytes(
                    reply.readAll()
                )

                if data:

                    pixmap = QPixmap()

                    if pixmap.loadFromData(
                        data
                    ):

                        self.thumbnail_pixmap = (
                            pixmap
                        )

                        self.thumbnail.setText(
                            ""
                        )

                        self.apply_thumbnail()

                        success = True

            else:

                print(
                    "YT BOX thumbnail failed:",
                    self.track.display_title(),
                    "-",
                    reply.errorString()
                )

        except RuntimeError:

            return

        except Exception as error:

            print(
                "YT BOX thumbnail error:",
                self.track.display_title(),
                "-",
                error
            )

        finally:

            try:

                reply.deleteLater()

            except Exception:

                pass

        # ----------------------------------------------------
        # If this candidate failed, automatically try next.
        # ----------------------------------------------------

        if (
            is_current_reply
            and
            not success
        ):

            self.request_next_thumbnail()

    # ========================================================
    # PLACEHOLDER
    # ========================================================

    def show_thumbnail_placeholder(
        self
    ):

        self.thumbnail_pixmap = None

        self.thumbnail.setPixmap(
            QPixmap()
        )

        self.thumbnail.setText(
            "▶"
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
            self.thumbnail_pixmap
            .scaled(

                width,

                height,

                Qt.KeepAspectRatioByExpanding,

                Qt.SmoothTransformation,
            )
        )

        # ----------------------------------------------------
        # Crop image to exact card thumbnail dimensions.
        # ----------------------------------------------------

        if (
            scaled.width() > width
            or
            scaled.height() > height
        ):

            x = max(
                0,
                (
                    scaled.width()
                    -
                    width
                )
                //
                2
            )

            y = max(
                0,
                (
                    scaled.height()
                    -
                    height
                )
                //
                2
            )

            scaled = scaled.copy(
                x,
                y,
                min(
                    width,
                    scaled.width()
                ),
                min(
                    height,
                    scaled.height()
                ),
            )

        self.thumbnail.setPixmap(
            scaled
        )

        self.thumbnail.setText(
            ""
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
    # Forwarded to AppWindow
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
        # Thread
        # ----------------------------------------------------

        self.search_thread: Optional[
            QThread
        ] = None

        self.search_worker: Optional[
            YouTubeSearchWorker
        ] = None

        self.search_in_progress = False

        # ----------------------------------------------------
        # Grid
        # ----------------------------------------------------

        self.current_columns = 4

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
        # TITLE
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
        # RESULT HEADER
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
        # STATUS
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
            Qt.AlignTop
            |
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

                title=(
                    "Type something to search"
                ),

                message=(
                    "Search by song, artist, album "
                    "or music video."
                ),
            )

            return

        if self.search_in_progress:

            return

        self.current_query = query

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

            title=(
                "Searching YouTube..."
            ),

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

        self.search_thread.started.connect(
            self.search_worker.run
        )

        self.search_worker.finished.connect(
            self.handle_search_results
        )

        self.search_worker.error.connect(
            self.handle_search_error
        )

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

        if not self.current_tracks:

            self.results_count.setText(
                "0 results"
            )

            self.show_status(

                icon="♫",

                title=(
                    "No results found"
                ),

                message=(
                    "Try another song, artist "
                    "or search phrase."
                ),
            )

            return

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

            title=(
                "YouTube search unavailable"
            ),

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

        old_cards = list(
            self.result_cards
        )

        self.result_cards = []

        while self.results_grid.count():

            item = (
                self.results_grid
                .takeAt(
                    0
                )
            )

            widget = item.widget()

            if widget is not None:

                widget.setParent(
                    None
                )

                widget.deleteLater()

        # Keep explicit reference until deleteLater has
        # been scheduled for every old card.

        old_cards.clear()

    # ========================================================
    # COLUMNS
    # ========================================================

    def calculate_columns(
        self
    ) -> int:

        width = (
            self.scroll
            .viewport()
            .width()
        )

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

        self.clear_results()

        self.current_columns = (
            self.calculate_columns()
        )

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

            card.play_requested.connect(
                self.handle_play_requested
            )

            card.favorite_requested.connect(
                self.handle_favorite_requested
            )

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
            track.display_title()
        )

        print(
            "Channel:",
            track.display_artist()
        )

        print(
            "Video ID:",
            track.video_id
        )

        print(
            "URL:",
            track.youtube_url()
        )

        print(
            "Playback:",
            getattr(
                track,
                "playback_mode",
                "official_external"
            )
        )

        print("=" * 60)
        print()

        self.play_requested.emit(
            track
        )

    # ========================================================
    # FAVORITE
    # ========================================================

    def handle_favorite_requested(
        self,
        track
    ):

        print(
            "YT BOX favorite requested:",
            track.display_title()
        )

        self.favorite_requested.emit(
            track
        )

    # ========================================================
    # PLAYLIST
    # ========================================================

    def handle_playlist_requested(
        self,
        track
    ):

        print(
            "YT BOX playlist requested:",
            track.display_title()
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
        # RESULTS
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
        # SCROLL
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
    # PAINT
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
                (
                    22
                    if self.current_is_dark
                    else 10
                )
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