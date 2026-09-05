from PySide6.QtCore import (
    Qt,
    Signal,
    QUrl,
)

from PySide6.QtGui import (
    QPixmap,
)

from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply,
)

from data.youtube_favorites_store import (
    youtube_favorites_store
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSlider,
    QWidget,
    QSizePolicy,
)

from ui.home.home_screen import HomeScreen
from ui.favorites.favorites_screen import FavoritesScreen
from ui.discover.discover_screen import DiscoverScreen
from ui.basic_page import BasicPage
from ui.library.library_screen import LibraryScreen
from ui.playlists.playlist_screen import PlaylistScreen
from ui.assistant.assistant_screen import AssistantScreen
from ui.yt_box.yt_box_screen import YTBoxScreen
from widgets.sidebar import Sidebar
from data.playlist_store import playlist_store
from services.youtube_service import youtube_service

from core.theme_manager import ThemeManager


# ============================================================
# FLOATING PLAYER
# ============================================================

class FloatingPlayer(QFrame):

    play_pause_requested = Signal()
    previous_requested = Signal()
    next_requested = Signal()
    close_requested = Signal()

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setObjectName("FloatingPlayer")

        self.current_image = ""
        self.current_title = ""
        self.current_artist = ""

        self.is_playing = True

        # ========================================================
        # ONLINE COVER ART
        # ========================================================

        self.cover_network = QNetworkAccessManager(
            self
        )

        self.cover_reply = None

        self.setFixedSize(
            820,
            82
        )

        self.build_ui()

        self.apply_theme(True)

        self.hide()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(
            14,
            10,
            10,
            10
        )

        root.setSpacing(10)

        # ====================================================
        # ALBUM ART
        # ====================================================

        self.album = QLabel()

        self.album.setFixedSize(
            58,
            58
        )

        self.album.setAlignment(
            Qt.AlignCenter
        )

        self.album.setScaledContents(False)

        root.addWidget(
            self.album
        )

        # ====================================================
        # SONG INFO
        # ====================================================

        info = QVBoxLayout()

        info.setContentsMargins(
            0,
            2,
            0,
            2
        )

        info.setSpacing(3)

        self.song_label = QLabel(
            "Nothing Playing"
        )

        self.song_label.setObjectName(
            "FloatingSongTitle"
        )

        self.song_label.setMinimumWidth(
            110
        )

        self.artist_label = QLabel(
            "Select a song to start listening"
        )

        self.artist_label.setObjectName(
            "FloatingArtist"
        )

        self.artist_label.setMinimumWidth(
            110
        )

        info.addWidget(
            self.song_label
        )

        info.addWidget(
            self.artist_label
        )

        info.addStretch()

        root.addLayout(
            info,
            1
        )

        # ====================================================
        # PREVIOUS
        # ====================================================

        self.previous_button = QPushButton(
            "⏮"
        )

        self.previous_button.setObjectName(
            "previousButton"
        )

        self.previous_button.setFixedSize(
            36,
            36
        )

        self.previous_button.setCursor(
            Qt.PointingHandCursor
        )

        self.previous_button.clicked.connect(
            self.previous_requested.emit
        )

        root.addWidget(
            self.previous_button
        )

        # ====================================================
        # PLAY / PAUSE
        # ====================================================

        self.play_button = QPushButton(
            "Ⅱ"
        )

        self.play_button.setObjectName(
            "floatingPlayButton"
        )

        self.play_button.setFixedSize(
            44,
            44
        )

        self.play_button.setCursor(
            Qt.PointingHandCursor
        )

        self.play_button.clicked.connect(
            self.play_pause_requested.emit
        )

        root.addWidget(
            self.play_button
        )

        # ====================================================
        # NEXT
        # ====================================================

        self.next_button = QPushButton(
            "⏭"
        )

        self.next_button.setObjectName(
            "nextButton"
        )

        self.next_button.setFixedSize(
            36,
            36
        )

        self.next_button.setCursor(
            Qt.PointingHandCursor
        )

        self.next_button.clicked.connect(
            self.next_requested.emit
        )

        root.addWidget(
            self.next_button
        )

        # ====================================================
        # PROGRESS AREA
        # ====================================================

        progress_layout = QVBoxLayout()

        progress_layout.setContentsMargins(
            4,
            0,
            4,
            0
        )

        progress_layout.setSpacing(2)

        self.progress = QSlider(
            Qt.Horizontal
        )

        self.progress.setObjectName(
            "floatingProgress"
        )

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(0)

        self.progress.setCursor(
            Qt.PointingHandCursor
        )

        progress_layout.addWidget(
            self.progress
        )

        # ====================================================
        # TIME
        # ====================================================

        time_layout = QHBoxLayout()

        time_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.current_time = QLabel(
            "0:00"
        )

        self.current_time.setObjectName(
            "floatingCurrentTime"
        )

        self.total_time = QLabel(
            "0:00"
        )

        self.total_time.setObjectName(
            "floatingTotalTime"
        )

        time_layout.addWidget(
            self.current_time
        )

        time_layout.addStretch()

        time_layout.addWidget(
            self.total_time
        )

        progress_layout.addLayout(
            time_layout
        )

        root.addLayout(
            progress_layout,
            1
        )

        # ====================================================
        # CLOSE BUTTON
        # ====================================================

        self.close_button = QPushButton(
            "X"
        )

        self.close_button.setObjectName(
            "floatingCloseButton"
        )

        self.close_button.setFixedSize(
            32,
            32
        )

        self.close_button.setCursor(
            Qt.PointingHandCursor
        )

        self.close_button.setFocusPolicy(
            Qt.NoFocus
        )

        self.close_button.clicked.connect(
            self.close_requested.emit
        )

        root.addWidget(
            self.close_button
        )

    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(
        self,
        is_dark
    ):

        if is_dark:

            self.setStyleSheet("""
            QFrame#FloatingPlayer {
                background: rgba(18, 14, 32, 248);
                border: 1px solid rgba(139, 92, 246, 110);
                border-radius: 20px;
            }

            QLabel {
                background: transparent;
                border: none;
            }

            QPushButton {
                background: transparent;
                color: #AAA0C5;
                border: none;
                border-radius: 18px;
                font-family: "Segoe UI";
                outline: none;
            }

            QPushButton:hover {
                background: rgba(139, 92, 246, 45);
                color: white;
            }

            QPushButton:pressed {
                background: rgba(139, 92, 246, 75);
            }

            QPushButton#previousButton,
            QPushButton#nextButton {
                font-family: "Segoe UI Symbol";
                font-size: 15px;
                font-weight: 600;
            }

            QPushButton#floatingPlayButton {
                background: #8B5CF6;
                color: white;
                border: none;
                border-radius: 22px;
                font-family: "Segoe UI";
                font-size: 17px;
                font-weight: 700;
            }

            QPushButton#floatingPlayButton:hover {
                background: #A78BFA;
                color: white;
            }

            QPushButton#floatingPlayButton:pressed {
                background: #7C3AED;
            }

            QPushButton#floatingCloseButton {
                background: transparent;
                color: #8D83A3;
                border: none;
                border-radius: 16px;
                font-family: "Segoe UI";
                font-size: 14px;
                font-weight: 700;
                padding: 0px;
                margin: 0px;
            }

            QPushButton#floatingCloseButton:hover {
                background: rgba(239, 68, 68, 45);
                color: #FFFFFF;
            }

            QPushButton#floatingCloseButton:pressed {
                background: rgba(239, 68, 68, 80);
                color: #FFFFFF;
            }

            QLabel#FloatingSongTitle {
                color: white;
                font-family: "Segoe UI";
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#FloatingArtist {
                color: #9185AA;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 400;
            }

            QLabel#floatingCurrentTime,
            QLabel#floatingTotalTime {
                color: #756A91;
                font-family: "Segoe UI";
                font-size: 9px;
            }

            QSlider#floatingProgress::groove:horizontal {
                height: 3px;
                background: #332A48;
                border-radius: 2px;
            }

            QSlider#floatingProgress::sub-page:horizontal {
                background: #8B5CF6;
                border-radius: 2px;
            }

            QSlider#floatingProgress::add-page:horizontal {
                background: #332A48;
                border-radius: 2px;
            }

            QSlider#floatingProgress::handle:horizontal {
                width: 9px;
                height: 9px;
                margin: -3px 0px;
                border-radius: 5px;
                background: white;
            }
            """)

            self.album.setStyleSheet("""
            QLabel {
                background: #211936;
                border: none;
                border-radius: 11px;
            }
            """)

        else:

            self.setStyleSheet("""
            QFrame#FloatingPlayer {
                background: rgba(255, 255, 255, 245);
                border: 1px solid rgba(124, 58, 237, 65);
                border-radius: 20px;
            }

            QLabel {
                background: transparent;
                border: none;
            }

            QPushButton {
                background: transparent;
                color: #67567D;
                border: none;
                border-radius: 18px;
                font-family: "Segoe UI";
                outline: none;
            }

            QPushButton:hover {
                background: rgba(124, 58, 237, 25);
                color: #4B2875;
            }

            QPushButton:pressed {
                background: rgba(124, 58, 237, 45);
            }

            QPushButton#previousButton,
            QPushButton#nextButton {
                font-family: "Segoe UI Symbol";
                font-size: 15px;
                font-weight: 600;
            }

            QPushButton#floatingPlayButton {
                background: #7C3AED;
                color: white;
                border: none;
                border-radius: 22px;
                font-family: "Segoe UI";
                font-size: 17px;
                font-weight: 700;
            }

            QPushButton#floatingPlayButton:hover {
                background: #8B5CF6;
                color: white;
            }

            QPushButton#floatingPlayButton:pressed {
                background: #6D28D9;
            }

            QPushButton#floatingCloseButton {
                background: transparent;
                color: #8A779C;
                border: none;
                border-radius: 16px;
                font-family: "Segoe UI";
                font-size: 14px;
                font-weight: 700;
                padding: 0px;
                margin: 0px;
            }

            QPushButton#floatingCloseButton:hover {
                background: rgba(124, 58, 237, 25);
                color: #4B2875;
            }

            QPushButton#floatingCloseButton:pressed {
                background: rgba(124, 58, 237, 45);
                color: #3B1E62;
            }

            QLabel#FloatingSongTitle {
                color: #2B2140;
                font-family: "Segoe UI";
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#FloatingArtist {
                color: #806D95;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 400;
            }

            QLabel#floatingCurrentTime,
            QLabel#floatingTotalTime {
                color: #8A779C;
                font-family: "Segoe UI";
                font-size: 9px;
            }

            QSlider#floatingProgress::groove:horizontal {
                height: 3px;
                background: #DDD4E7;
                border-radius: 2px;
            }

            QSlider#floatingProgress::sub-page:horizontal {
                background: #7C3AED;
                border-radius: 2px;
            }

            QSlider#floatingProgress::add-page:horizontal {
                background: #DDD4E7;
                border-radius: 2px;
            }

            QSlider#floatingProgress::handle:horizontal {
                width: 9px;
                height: 9px;
                margin: -3px 0px;
                border-radius: 5px;
                background: #7C3AED;
            }
            """)

            self.album.setStyleSheet("""
            QLabel {
                background: #EDE7F4;
                border: none;
                border-radius: 11px;
            }
            """)

    # ========================================================
    # FLOATING ONLINE COVER
    # ========================================================

    def load_online_cover(
        self,
        image_url
    ):

        image_url = str(
            image_url or ""
        ).strip()

        if not image_url:

            self.album.clear()

            return

        # ----------------------------------------------------
        # OLD REQUEST
        # ----------------------------------------------------

        if self.cover_reply is not None:

            try:

                if self.cover_reply.isRunning():

                    self.cover_reply.abort()

            except Exception:

                pass

            self.cover_reply = None

        # ----------------------------------------------------
        # REQUEST
        # ----------------------------------------------------

        url = QUrl.fromUserInput(
            image_url
        )

        if not url.isValid():

            print(
                "Floating invalid cover URL:",
                image_url
            )

            return

        request = QNetworkRequest(
            url
        )

        request.setRawHeader(
            b"User-Agent",
            b"Mozilla/5.0 LYRx/0.2"
        )

        self.cover_reply = (
            self.cover_network.get(
                request
            )
        )

        self.cover_reply.finished.connect(
            self.online_cover_loaded
        )

    # ========================================================
    # FLOATING ONLINE COVER LOADED
    # ========================================================

    def online_cover_loaded(self):

        reply = self.sender()

        if reply is None:

            return

        try:

            if (
                reply.error()
                != QNetworkReply.NetworkError.NoError
            ):

                print(
                    "Floating cover network error:",
                    reply.errorString()
                )

                self.album.clear()

                return

            raw_data = bytes(
                reply.readAll()
            )

            pixmap = QPixmap()

            if not pixmap.loadFromData(
                raw_data
            ):

                print(
                    "Floating cover decode failed"
                )

                self.album.clear()

                return

            pixmap = pixmap.scaled(
                58,
                58,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            self.album.clear()

            self.album.setPixmap(
                pixmap
            )

        except Exception as error:

            print(
                "Floating online cover error:",
                error
            )

        finally:

            try:

                reply.deleteLater()

            except Exception:

                pass

            if reply is self.cover_reply:

                self.cover_reply = None

    # ========================================================
    # SET COVER PIXMAP
    # ========================================================

    def set_cover_pixmap(self, pixmap):

        try:
            if pixmap is None or pixmap.isNull():
                return

            scaled = pixmap.scaled(
                58,
                58,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            self.album.clear()
            self.album.setPixmap(scaled)

        except Exception as error:
            print("Floating shared cover error:", error)

    # ========================================================
    # SET SONG
    # ========================================================

    def set_song(
        self,
        image_path,
        title,
        artist
    ):

        self.current_image = (
            image_path
        )

        self.current_title = (
            title
        )

        self.current_artist = (
            artist
        )

        # ====================================================
        # TEXT
        # ====================================================

        self.song_label.setText(
            title
        )

        self.artist_label.setText(
            artist
        )

        # ====================================================
        # ONLINE COVER
        # ====================================================

        image_value = str(
            image_path or ""
        ).strip()

        if image_value.startswith(
            (
                "http://",
                "https://"
            )
        ):

            self.album.clear()

            self.load_online_cover(
                image_value
            )

        # ====================================================
        # LOCAL COVER
        # ====================================================

        else:

            from pathlib import Path

            file_dir = Path(
                __file__
            ).resolve()

            project_dir = (
                file_dir.parents[2]
            )

            candidates = [

                project_dir
                / image_value,

                file_dir.parents[1]
                / image_value,

                Path.cwd()
                / image_value,

                Path(
                    image_value
                ),
            ]

            image_file = None

            for path in candidates:

                try:

                    if (
                        path.exists()
                        and
                        path.is_file()
                    ):

                        image_file = (
                            path
                        )

                        break

                except Exception:

                    pass

            if image_file:

                pix = QPixmap(
                    str(
                        image_file
                    )
                )

                if not pix.isNull():

                    scaled_pix = (
                        pix.scaled(
                            58,
                            58,
                            Qt.KeepAspectRatioByExpanding,
                            Qt.SmoothTransformation
                        )
                    )

                    self.album.setPixmap(
                        scaled_pix
                    )

                else:

                    self.album.clear()

            else:

                self.album.clear()

        # ====================================================
        # RESET PROGRESS
        # ====================================================

        self.progress.blockSignals(
            True
        )

        self.progress.setValue(
            0
        )

        self.progress.blockSignals(
            False
        )

        self.current_time.setText(
            "0:00"
        )

        self.total_time.setText(
            "0:00"
        )

        # ====================================================
        # PLAY STATE
        # ====================================================

        self.is_playing = True

        self.play_button.setText(
            "Ⅱ"
        )

        # ====================================================
        # SHOW
        # ====================================================

        self.show()

        self.raise_()

    # ========================================================
    # PLAY STATE
    # ========================================================

    def set_playing(
        self,
        playing
    ):

        self.is_playing = playing

        self.play_button.setText(
            "Ⅱ"
            if playing
            else "▶"
        )

    # ========================================================
    # PROGRESS
    # ========================================================

    def set_progress(
        self,
        value,
        current_time=None,
        total_time=None
    ):

        self.progress.blockSignals(True)

        self.progress.setValue(value)

        self.progress.blockSignals(False)

        if current_time is not None:

            self.current_time.setText(
                current_time
            )

        if total_time is not None:

            self.total_time.setText(
                total_time
            )


# ============================================================
# YT BOX PAGE SHELL
# ============================================================

class YTBoxPage(QWidget):

    play_requested = Signal(object)
    favorite_requested = Signal(object)
    playlist_requested = Signal(object)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setObjectName("YTBoxPage")
        self.current_is_dark = True

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        root.addWidget(self.sidebar)

        self.main = YTBoxScreen()

        self.main.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.main,
            1
        )

        self.main.play_requested.connect(
            self.play_requested.emit
        )

        self.main.favorite_requested.connect(
            self.favorite_requested.emit
        )

        self.main.playlist_requested.connect(
            self.playlist_requested.emit
        )

    def set_theme_state(
        self,
        is_dark
    ):

        self.current_is_dark = bool(is_dark)

        try:
            self.sidebar.set_theme_state(
                self.current_is_dark
            )
        except Exception as error:
            print(
                "YT BOX sidebar theme error:",
                error
            )

        try:
            self.main.set_theme_state(
                self.current_is_dark
            )
        except Exception as error:
            print(
                "YT BOX content theme error:",
                error
            )

        self.update()


# ============================================================
# APP WINDOW
# ============================================================

class AppWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        # ====================================================
        # THEME
        # ====================================================

        self.theme_manager = ThemeManager()

        self.theme_manager.theme_changed.connect(
            self.apply_theme
        )

        # ====================================================
        # WINDOW
        # ====================================================

        self.setWindowTitle("🎵 LYRx")

        self.setWindowFlags(
            Qt.FramelessWindowHint
        )

        # ====================================================
        # SCREEN
        # ====================================================

        screen = QApplication.primaryScreen()

        available = screen.availableGeometry()

        window_width = min(
            1400,
            available.width() - 20
        )

        window_height = min(
            850,
            available.height() - 20
        )

        window_width = max(
            window_width,
            1200
        )

        window_height = max(
            window_height,
            700
        )

        self.resize(
            window_width,
            window_height
        )

        self.move(
            available.x()
            + (
                available.width()
                - window_width
            ) // 2,

            available.y()
            + (
                available.height()
                - window_height
            ) // 2
        )

        self.setMinimumSize(
            1200,
            700
        )

        # ====================================================
        # PAGE STACK
        # ====================================================

        self.pages = QStackedWidget()

        self.pages.setObjectName(
            "PageStack"
        )

        self.setCentralWidget(
            self.pages
        )

        # ====================================================
        # HOME
        # ====================================================

        self.home = HomeScreen()

        self.pages.addWidget(
            self.home
        )

        # ====================================================
        # DISCOVER
        # ====================================================

        self.discover = DiscoverScreen()

        self.pages.addWidget(
            self.discover
        )

        # ====================================================
        # FAVORITES
        # ====================================================

        self.favorites = FavoritesScreen()

        self.pages.addWidget(
            self.favorites
        )

        # ====================================================
        # LIBRARY
        # ====================================================

        self.library = LibraryScreen()

        self.library.song_requested.connect(
            self.play_library_song
        )

        self.pages.addWidget(
            self.library
        )

        # ====================================================
        # PLAYLISTS
        # ====================================================

        self.playlists = PlaylistScreen()

        self.pages.addWidget(
            self.playlists
        )

        # ====================================================
        # AI ASSISTANT
        # ====================================================
        #
        # DAY 18
        #
        # This was missing before.
        #

        self.assistant = AssistantScreen()

        self.pages.addWidget(
            self.assistant
        )

        # ====================================================
        # DAY 21 - YT BOX
        # ====================================================

        self.yt_box = YTBoxPage()

        self.pages.addWidget(
            self.yt_box
        )

        # ====================================================
        # SETTINGS
        # ====================================================

        self.settings = BasicPage(
            "Settings",
            "Customize your LYRx experience.",
            "⚙"
        )

        self.pages.addWidget(
            self.settings
        )

        # ====================================================
        # SIDEBARS
        # ====================================================

        self.sidebars = [
            self.home.sidebar,
            self.discover.sidebar,
            self.favorites.sidebar,
            self.library.sidebar,
            self.playlists.sidebar,
            self.assistant.sidebar,
            self.yt_box.sidebar,
            self.settings.sidebar
        ]

        # ====================================================
        # SIDEBAR SIGNALS
        # ====================================================

        for sidebar in self.sidebars:

            sidebar.page_changed.connect(
                self.handle_page_change
            )

            sidebar.theme_toggle_requested.connect(
                self.theme_manager.toggle
            )

        # ====================================================
        # DISCOVER
        # ====================================================

        self.discover.song_requested.connect(
            self.play_discover_song
        )

        # ====================================================
        # DAY 19 - ONLINE DISCOVER MUSIC
        # ====================================================

        self.discover.online_song_requested.connect(
            self.play_online_discover_song
        )

        # ====================================================
        # DAY 20 - GLOBAL ONLINE SEARCH
        # ====================================================
        #
        # Home Header:
        #     type query
        #     press Enter
        #         ↓
        # HomeScreen.online_search_requested
        #         ↓
        # AppWindow.handle_global_online_search()
        #         ↓
        # DiscoverScreen.search_online_music()
        #
        # The actual API/network work stays inside DiscoverScreen
        # and its worker thread. AppWindow only routes the request.
        #

        self.home.online_search_requested.connect(
            self.handle_global_online_search
        )

        # ====================================================
        # DAY 21 - YT BOX SIGNALS
        # ====================================================
        #
        # File 4 only wires the screen into AppWindow.
        # Play/Favorite/Playlist behavior is handled by the
        # dedicated YT BOX integration steps that follow.
        #

        self.yt_box.play_requested.connect(
            self.play_youtube_track
        )

        self.yt_box.favorite_requested.connect(
            self.handle_yt_box_favorite_requested
        )

        self.yt_box.playlist_requested.connect(
            self.handle_yt_box_playlist_requested
        )

        # ====================================================
        # FAVORITES
        # ====================================================

        self.favorites.play_requested.connect(
            self.play_favorite_song
        )

        self.favorites.youtube_play_requested.connect(
            self.play_youtube_favorite
        )

        # ====================================================
        # AI ASSISTANT PLAYER CONTROL
        # ====================================================
        #
        # DAY 18 - PHASE 2
        #
        # AssistantScreen understands commands like:
        #
        # "Play Faded"
        # "Play Believer"
        # "Play Arcade"
        # "Play Let Her Go"
        #
        # It emits:
        #
        # play_song_requested(
        #     image_path,
        #     title,
        #     artist
        # )
        #
        # AppWindow receives that signal here and sends it
        # to the existing HomeScreen / NowPlaying engine.
        #

        self.assistant.play_song_requested.connect(
            self.play_assistant_song
        )

        # ====================================================
        # AI ASSISTANT PLAYER CONTROLS
        # ====================================================

        self.assistant.pause_requested.connect(
            self.pause_assistant_song
        )

        self.assistant.resume_requested.connect(
            self.resume_assistant_song
        )

        self.assistant.stop_requested.connect(
            self.stop_assistant_song
        )

        self.assistant.next_requested.connect(
            self.next_assistant_song
        )

        self.assistant.previous_requested.connect(
            self.previous_assistant_song
        )

        self.assistant.create_playlist_requested.connect(
            self.create_assistant_playlist
        )

        # ====================================================
        # FLOATING PLAYER
        # ====================================================

        self.floating_player = FloatingPlayer(
            self
        )

        self.floating_player.hide()

        self.floating_player.play_pause_requested.connect(
            self.toggle_floating_play
        )

        self.floating_player.previous_requested.connect(
            self.previous_floating_song
        )

        self.floating_player.next_requested.connect(
            self.next_floating_song
        )

        self.floating_player.close_requested.connect(
            self.close_floating_player
        )

        # ====================================================
        # HOME PLAYER SYNC
        # ====================================================

        try:

            now_playing = self.home.now_playing

            now_playing.song_changed.connect(
                self.sync_floating_song
            )

            now_playing.cover_pixmap_changed.connect(
                self.floating_player.set_cover_pixmap
            )

            now_playing.audio_player.positionChanged.connect(
                self.sync_floating_progress
            )

            now_playing.audio_player.durationChanged.connect(
                self.sync_floating_duration
            )

            now_playing.audio_player.playbackStateChanged.connect(
                self.sync_floating_play_state
            )

        except Exception as error:

            print(
                "Floating player sync setup error:",
                error
            )

        # ====================================================
        # START HOME
        # ====================================================

        self.pages.setCurrentWidget(
            self.home
        )

        self.update_sidebar_states(
            "Home"
        )

        # ====================================================
        # APPLY THEME
        # ====================================================

        self.apply_theme()

    # ========================================================
    # THEME → ALL PAGES
    # ========================================================

    def apply_theme_to_pages(
        self,
        is_dark
    ):

        pages = [
            self.home,
            self.discover,
            self.favorites,
            self.library,
            self.playlists,
            self.assistant,
            self.yt_box,
            self.settings
        ]

        for page in pages:

            try:

                if hasattr(
                    page,
                    "set_theme_state"
                ):

                    page.set_theme_state(
                        is_dark
                    )

            except Exception as error:

                print(
                    "Page theme error:",
                    type(page).__name__,
                    error
                )

        if is_dark:

            self.pages.setStyleSheet("""
            QStackedWidget#PageStack {
                background: #0B0913;
                border: none;
            }
            """)

        else:

            self.pages.setStyleSheet("""
            QStackedWidget#PageStack {
                background: #F7F4FB;
                border: none;
            }
            """)

    # ========================================================
    # GLOBAL THEME
    # ========================================================

    def apply_theme(
        self,
        theme=None
    ):

        app = QApplication.instance()

        if app is None:
            return

        is_dark = (
            self.theme_manager.current_theme
            == ThemeManager.DARK
        )

        app.setStyleSheet(
            self.theme_manager.get_stylesheet()
        )

        self.apply_theme_to_pages(
            is_dark
        )

        # ====================================================
        # SIDEBARS
        # ====================================================

        for sidebar in self.sidebars:

            try:

                sidebar.set_theme_state(
                    is_dark
                )

            except Exception as error:

                print(
                    "Sidebar theme error:",
                    error
                )

        # ====================================================
        # FLOATING PLAYER
        # ====================================================

        if hasattr(
            self,
            "floating_player"
        ):

            try:

                self.floating_player.apply_theme(
                    is_dark
                )

            except Exception as error:

                print(
                    "Floating player theme error:",
                    error
                )

        # ====================================================
        # REFRESH
        # ====================================================

        self.setUpdatesEnabled(False)
        self.setUpdatesEnabled(True)

        self.update()
        self.pages.update()

        for page in (
            self.home,
            self.discover,
            self.favorites,
            self.library,
            self.playlists,
            self.assistant,
            self.yt_box,
            self.settings
        ):

            page.update()

        print(
            "THEME:",
            "DARK"
            if is_dark
            else "LIGHT"
        )

    # ========================================================
    # DAY 20 - GLOBAL ONLINE SEARCH ROUTER
    # ========================================================

    def handle_global_online_search(
        self,
        query
    ):

        query = str(
            query or ""
        ).strip()

        if not query:

            return

        print()
        print("=" * 60)
        print("LYRx DAY 20 - GLOBAL ONLINE SEARCH")
        print("Query:", query)
        print("=" * 60)
        print()

        # ====================================================
        # OPEN DISCOVER
        # ====================================================

        self.pages.setCurrentWidget(
            self.discover
        )

        self.update_sidebar_states(
            "Discover"
        )

        # ====================================================
        # KEEP FLOATING PLAYER RULES CONSISTENT
        # ====================================================

        self.update_floating_visibility()

        self.position_floating_player()

        if self.floating_player.isVisible():

            self.floating_player.raise_()

        # ====================================================
        # SEND QUERY TO DISCOVER
        # ====================================================
        #
        # FILE 4 / DiscoverScreen will provide:
        #
        #     search_online_music(query)
        #
        # Keeping this hasattr guard means window.py can still
        # launch safely before File 4 is pasted.
        #

        if hasattr(
            self.discover,
            "search_online_music"
        ):

            try:

                self.discover.search_online_music(
                    query
                )

            except Exception as error:

                print(
                    "Global online search routing error:",
                    error
                )

        else:

            print(
                "DiscoverScreen.search_online_music() "
                "is not added yet. Apply File 4 next."
            )

    # ========================================================
    # PAGE NAVIGATION
    # ========================================================

    def handle_page_change(
        self,
        page_name: str
    ):

        page_map = {

            "Home": self.home,

            "Discover": self.discover,

            "Library": self.library,

            "Favorites": self.favorites,

            "Playlists": self.playlists,

            "AI Assistant": self.assistant,

            "YT BOX": self.yt_box,

            "Settings": self.settings
        }

        target_page = page_map.get(
            page_name
        )

        if target_page is None:

            print(
                f"Unknown page: {page_name}"
            )

            return

        # ====================================================
        # FAVORITES REFRESH
        # ====================================================

        if page_name == "Favorites":

            try:

                self.favorites.reload_favorites()

            except Exception as error:

                print(
                    "Favorites reload error:",
                    error
                )

        # ====================================================
        # ASSISTANT PAGE
        # ====================================================

        if page_name == "AI Assistant":

            try:

                self.assistant.input_box.setFocus()

            except Exception:

                pass

        # ====================================================
        # YT BOX PAGE
        # ====================================================

        if page_name == "YT BOX":

            try:

                self.yt_box.main.search_input.setFocus()

            except Exception:

                pass

        # ====================================================
        # CHANGE PAGE
        # ====================================================

        self.pages.setCurrentWidget(
            target_page
        )

        self.update_sidebar_states(
            page_name
        )

        self.update_floating_visibility()

        self.position_floating_player()

        print(
            f"Page changed: {page_name}"
        )

    # ========================================================
    # SIDEBAR STATES
    # ========================================================

    def update_sidebar_states(
        self,
        page_name: str
    ):

        for sidebar in self.sidebars:

            for button in sidebar.buttons:

                button.blockSignals(True)

                button.setChecked(
                    button.page_name
                    == page_name
                )

                button.blockSignals(False)

    # ========================================================
    # FLOATING PLAYER VISIBILITY
    # ========================================================

    def update_floating_visibility(self):

        current = self.pages.currentWidget()

        # ----------------------------------------------------
        # HOME
        # ----------------------------------------------------

        if current is self.home:

            self.floating_player.hide()

            return

        # ----------------------------------------------------
        # SUPPORTED PAGES
        # ----------------------------------------------------

        if current in (
            self.discover,
            self.favorites,
            self.library
        ):

            if (
                self.floating_player.current_title
                and self.floating_player.current_image
            ):

                self.floating_player.show()

                self.position_floating_player()

                self.floating_player.raise_()

            return

        # ----------------------------------------------------
        # OTHER PAGES
        # ----------------------------------------------------

        self.floating_player.hide()

    # ========================================================
    # DISCOVER SONG
    # ========================================================

    def play_discover_song(
        self,
        image_path,
        title,
        artist
    ):

        self.home.play_selected_song(
            image_path,
            title,
            artist
        )

        self.floating_player.set_song(
            image_path,
            title,
            artist
        )

        self.pages.setCurrentWidget(
            self.discover
        )

        self.update_sidebar_states(
            "Discover"
        )

        self.update_floating_visibility()

        self.position_floating_player()

        self.floating_player.raise_()

    # ========================================================
    # DAY 20 - ONLINE DISCOVER / SEARCH SONG
    # ========================================================

    def play_online_discover_song(
        self,
        song
    ):

        try:

            if song is None:

                return

            # ====================================================
            # SAFE SONG DATA
            # ====================================================

            title = str(
                getattr(
                    song,
                    "title",
                    ""
                )
                or "Unknown Track"
            )

            artist = str(
                getattr(
                    song,
                    "artist",
                    ""
                )
                or "Unknown Artist"
            )

            image_url = str(
                getattr(
                    song,
                    "image_url",
                    ""
                )
                or ""
            )

            # ====================================================
            # DAY 20 - UNIFIED PLAYABLE URL
            # ====================================================
            #
            # Jamendo:
            #     song.audio_url
            #
            # iTunes:
            #     song.preview_url
            #
            # Unified provider Song:
            #     song.playable_url()
            #
            # This keeps Day 19 Jamendo playback working while
            # allowing Day 20 iTunes preview playback.
            #

            audio_url = ""

            try:

                if hasattr(
                    song,
                    "playable_url"
                ):

                    audio_url = str(
                        song.playable_url()
                        or ""
                    ).strip()

                else:

                    audio_url = str(

                        getattr(
                            song,
                            "audio_url",
                            ""
                        )

                        or

                        getattr(
                            song,
                            "preview_url",
                            ""
                        )

                        or

                        ""

                    ).strip()

            except Exception as error:

                print(
                    "Playable URL resolve error:",
                    error
                )

                audio_url = str(

                    getattr(
                        song,
                        "audio_url",
                        ""
                    )

                    or

                    getattr(
                        song,
                        "preview_url",
                        ""
                    )

                    or

                    ""

                ).strip()

            # ====================================================
            # DAY 19 PLAYER COMPATIBILITY
            # ====================================================
            #
            # NowPlaying.update_online_song() still uses audio_url
            # as its playback source. For preview-only providers
            # such as iTunes, expose the resolved preview through
            # audio_url for the playback layer.
            #

            if audio_url:

                try:

                    song.audio_url = (
                        audio_url
                    )

                except Exception:

                    pass

            # ====================================================
            # DAY 20 PROVIDER COMPATIBILITY
            # ====================================================
            #
            # Old Song model:
            #     song.source
            #
            # New provider model:
            #     song.provider
            #
            # Support BOTH so Day 19 and Day 20 code can coexist.
            #

            source_name = str(

                getattr(
                    song,
                    "source",
                    ""
                )

                or

                getattr(
                    song,
                    "provider",
                    ""
                )

                or

                "online"

            )

            print()
            print("=" * 60)

            print(
                "APP WINDOW ONLINE SONG"
            )

            print(
                "Title:",
                title
            )

            print(
                "Artist:",
                artist
            )

            print(
                "Source:",
                source_name
            )

            print(
                "Audio:",
                audio_url
            )

            print("=" * 60)
            print()

            # ====================================================
            # VALIDATE AUDIO
            # ====================================================

            if not audio_url:

                print(
                    "Online song has no playable audio or preview URL:",
                    title
                )

                return

            print(
                "Resolved playable URL:",
                audio_url
            )

            # ====================================================
            # GET CURRENT DISCOVER QUEUE
            # ====================================================

            online_queue = list(
                getattr(
                    self.discover,
                    "online_songs",
                    []
                )
                or []
            )

            # ====================================================
            # SEARCH RESULTS MAY USE ANOTHER RESULT COLLECTION
            # ====================================================

            search_results = list(
                getattr(
                    self.discover,
                    "search_results",
                    []
                )
                or []
            )

            if search_results:

                # ------------------------------------------------
                # Use search queue only if clicked song belongs
                # to it.
                # ------------------------------------------------

                song_id = str(
                    getattr(
                        song,
                        "id",
                        ""
                    )
                    or ""
                )

                found_in_search = False

                for item in search_results:

                    if item is song:

                        found_in_search = True
                        break

                    item_id = str(
                        getattr(
                            item,
                            "id",
                            ""
                        )
                        or ""
                    )

                    if (
                        song_id
                        and
                        item_id
                        and
                        song_id == item_id
                    ):

                        found_in_search = True
                        break

                if found_in_search:

                    online_queue = (
                        search_results
                    )

            # ====================================================
            # FALLBACK
            # ====================================================

            if not online_queue:

                online_queue = [
                    song
                ]

            # ====================================================
            # SET COMPLETE ONLINE QUEUE
            # ====================================================

            self.home.now_playing.set_online_queue(
                online_queue,
                current_song=song
            )

            # ====================================================
            # PLAY SELECTED ONLINE SONG
            # ====================================================

            self.home.now_playing.update_online_song(
                song,
                preserve_queue=True
            )

            # ====================================================
            # KEEP USER ON DISCOVER
            # ====================================================

            self.pages.setCurrentWidget(
                self.discover
            )

            self.update_sidebar_states(
                "Discover"
            )

            # ====================================================
            # FLOATING PLAYER IMMEDIATE SYNC
            # ====================================================
            #
            # Normally NowPlaying.song_changed handles this.
            # We also sync here so artwork/text doesn't depend
            # on network/event timing.
            #

            self.floating_player.set_song(
                image_url,
                title,
                artist
            )

            # ====================================================
            # VISIBILITY
            # ====================================================

            self.update_floating_visibility()

            self.position_floating_player()

            if (
                self.floating_player
                .isVisible()
            ):

                self.floating_player.raise_()

            print(
                "Online playback started:",
                title,
                "-",
                artist
            )

        except Exception as error:

            print()
            print("=" * 60)

            print(
                "ONLINE DISCOVER PLAY ERROR"
            )

            print(
                "Type:",
                type(
                    error
                ).__name__
            )

            print(
                "Error:",
                error
            )

            print("=" * 60)
            print()

    # ========================================================
    # DAY 21 - YT BOX PLAY
    # ========================================================

    def play_youtube_track(
        self,
        track
    ):

        """
        DAY 22 stable YT BOX playback.

        YT BOX remains a YouTube discovery/search surface.
        The selected exact YouTube result is opened through the
        official YouTube URL.

        IMPORTANT:
            - No iTunes/Jamendo resolver substitution.
            - No 30-second preview pretending to be the YT track.
            - No mixed provider Next/Previous queue.
            - Existing Discover/Library playback remains untouched.
        """

        if track is None:
            return

        try:

            # =================================================
            # TRACK DATA
            # =================================================

            title = str(
                getattr(
                    track,
                    "title",
                    ""
                )
                or "YouTube Track"
            )

            channel = str(
                getattr(
                    track,
                    "channel",
                    ""
                )
                or getattr(
                    track,
                    "artist",
                    ""
                )
                or "YouTube"
            )

            # =================================================
            # STOP NATIVE LYRx AUDIO
            # =================================================
            #
            # If iTunes/Jamendo/local playback was active before
            # the user selected a YT BOX result, stop it so LYRx
            # does not keep unrelated audio running underneath
            # YouTube.
            # =================================================

            try:
                self.home.now_playing.audio_player.stop()
            except Exception as error:
                print(
                    "YT BOX native player stop warning:",
                    error
                )

            # =================================================
            # CLEAR ONLINE QUEUE
            # =================================================
            #
            # This prevents floating-player Next/Previous from
            # continuing an old Discover/iTunes/Jamendo queue.
            # =================================================

            try:
                self.home.now_playing.set_online_queue(
                    [],
                    current_song=None
                )
            except Exception:
                pass

            # =================================================
            # KEEP USER ON YT BOX
            # =================================================

            self.pages.setCurrentWidget(
                self.yt_box
            )

            self.update_sidebar_states(
                "YT BOX"
            )

            # YT BOX browser playback is not controlled by LYRx's
            # QMediaPlayer, so the floating player must not pretend
            # it can pause/seek/next that YouTube playback.
            self.floating_player.hide()

            # =================================================
            # OPEN EXACT SELECTED YOUTUBE RESULT
            # =================================================

            print()
            print("=" * 60)
            print("YT BOX OFFICIAL PLAYBACK")
            print("Title:", title)
            print("Channel:", channel)

            opened = youtube_service.open_track(
                track
            )

            if opened:
                print("Opened selected YouTube result.")
            else:
                print("Could not open selected YouTube result.")

            print("=" * 60)
            print()

        except Exception as error:

            print()
            print("=" * 60)
            print("YT BOX PLAY ERROR")
            print("Type:", type(error).__name__)
            print("Error:", error)
            print("=" * 60)
            print()

    # ========================================================
    # DAY 21 - YT BOX PLAY ROUTER
    # ========================================================

    def handle_yt_box_play_requested(self, track):
        """
        File 4 routing checkpoint.

        The YT BOX card is now connected all the way to
        AppWindow. The dedicated playback behavior is added
        in the next YT BOX integration file.
        """

        if track is None:
            return

        print()
        print("=" * 60)
        print("APP WINDOW - YT BOX PLAY REQUEST")
        print("Title:", getattr(track, "title", ""))
        print("Channel:", getattr(track, "channel", ""))

        try:
            print("URL:", track.youtube_url())
        except Exception:
            print("URL:", getattr(track, "webpage_url", ""))

        print("YT BOX playback integration is the next step.")
        print("=" * 60)
        print()

    def handle_yt_box_favorite_requested(
        self,
        track
    ):
        
        if track is None:
            return

        try:

            is_favorite = (
                youtube_favorites_store
                .toggle(
                    track
                )
            )

            print(
                "YT BOX favorite:",
                "ADDED"
                if is_favorite
                else "REMOVED",
                "-",
                getattr(
                    track,
                    "title",
                    "YouTube Track"
                )
            )

            self.favorites.reload_favorites()

        
        except Exception as error:

            print(
                "YT BOX favorite error:",
                error
            )

    def handle_yt_box_playlist_requested(
        self,
        track
    ):

        if track is None:
            return

        try:

            # ====================================================
            # YOUTUBE TRACK METADATA
            # ====================================================

            title = str(
                getattr(
                    track,
                    "title",
                    ""
                )
                or "YouTube Track"
            )

            channel = str(
                getattr(
                    track,
                    "channel",
                    ""
                )
                or "YouTube"
            )

            thumbnail_url = str(
                getattr(
                    track,
                    "thumbnail_url",
                    ""
                )
                or ""
            )

            video_id = str(
                getattr(
                    track,
                    "video_id",
                    ""
                )
                or ""
            )

            youtube_url = ""

            try:

                if hasattr(
                    track,
                    "youtube_url"
                ):

                    youtube_url = str(
                        track.youtube_url()
                        or ""
                    ).strip()

            except Exception:

                youtube_url = ""

            if not youtube_url:

                youtube_url = str(
                    getattr(
                        track,
                        "webpage_url",
                        ""
                    )
                    or ""
                ).strip()

            # ====================================================
            # DEBUG
            # ====================================================

            print()
            print("=" * 60)
            print("LYRx YT BOX - ADD TO PLAYLIST")
            print("Title:", title)
            print("Channel:", channel)
            print("Video ID:", video_id)
            print("URL:", youtube_url)
            print("=" * 60)
            print()

            # ====================================================
            # EXISTING PLAYLIST SYSTEM
            # ====================================================
            #
            # Day 21:
            # Store YT track using the existing playlist schema:
            #
            # image  -> YouTube thumbnail
            # title  -> video/song title
            # artist -> YouTube channel
            #
            # Day 22:
            # We will extend playlist metadata with:
            # source/video_id/webpage_url
            # when unified YouTube playback is implemented.
            # ====================================================

            added = (
                self.playlists
                .add_song_to_playlist(
                    thumbnail_url,
                    title,
                    channel
                )
            )

            if added:

                print(
                    "YT BOX added to playlist:",
                    title
                )

            else:

                print(
                    "YT BOX playlist add cancelled "
                    "or track already exists:",
                    title
                )

        except Exception as error:

            print()
            print("=" * 60)
            print("YT BOX PLAYLIST ERROR")
            print(
                "Type:",
                type(error).__name__
            )
            print(
                "Error:",
                error
            )
            print("=" * 60)
            print()

    def play_youtube_favorite(
        self,
        item
    ):

        from types import SimpleNamespace

        if not isinstance(
            item,
            dict
        ):

            return

        track = SimpleNamespace(
            **item
        )

        self.play_youtube_track(
            track
        )

    # ========================================================
    # FAVORITE SONG
    # ========================================================

    def play_favorite_song(
        self,
        image_path,
        title,
        artist
    ):

        self.home.play_selected_song(
            image_path,
            title,
            artist
        )

        self.floating_player.set_song(
            image_path,
            title,
            artist
        )

        self.pages.setCurrentWidget(
            self.favorites
        )

        self.update_sidebar_states(
            "Favorites"
        )

        self.update_floating_visibility()

        self.position_floating_player()

        self.floating_player.raise_()

    # ========================================================
    # LIBRARY SONG
    # ========================================================

    def play_library_song(
        self,
        image_path,
        title,
        artist
    ):

        self.home.play_selected_song(
            image_path,
            title,
            artist
        )

        self.floating_player.set_song(
            image_path,
            title,
            artist
        )

        self.pages.setCurrentWidget(
            self.library
        )

        self.update_sidebar_states(
            "Library"
        )

        self.update_floating_visibility()

        self.position_floating_player()

        self.floating_player.raise_()

    # ========================================================
    # AI ASSISTANT - PLAY SONG
    # ========================================================

    def play_assistant_song(
        self,
        image_path,
        title,
        artist
    ):

        try:

            print(
                "LYRx AI requested:",
                title,
                "-",
                artist
            )

            # ====================================================
            # FIND SONG IN HOME MASTER QUEUE
            # ====================================================

            song_index = None

            for index, song in enumerate(
                self.home.player_queue
            ):

                if (
                    song[0] == image_path
                    and
                    song[1] == title
                    and
                    song[2] == artist
                ):

                    song_index = index

                    break

            if song_index is None:

                print(
                    "AI song not found:",
                    title
                )

                return

            # ====================================================
            # SYNC HOME
            # ====================================================

            self.home.current_index = (
                song_index
            )

            self.home.now_playing.set_queue(
                self.home.player_queue
            )

            self.home.now_playing.set_current_index(
                song_index
            )

            # ====================================================
            # ACTUAL PLAY
            # ====================================================

            self.home.now_playing.update_song(
                image_path,
                title,
                artist
            )

            print(
                "LYRx AI playing:",
                title,
                "-",
                artist
            )

        except Exception as error:

            print(
                "AI play error:",
                error
            )


    # ========================================================
    # AI ASSISTANT - PAUSE
    # ========================================================

    def pause_assistant_song(self):

        try:

            player_widget = (
                self.home.now_playing
            )

            audio_player = (
                player_widget.audio_player
            )

            from PySide6.QtMultimedia import (
                QMediaPlayer
            )

            state = (
                audio_player
                .playbackState()
            )

            if (
                state
                ==
                QMediaPlayer
                .PlaybackState
                .PlayingState
            ):

                audio_player.pause()

                player_widget.is_playing = False

                player_widget.play_btn.setText(
                    "▶"
                )

                player_widget.play_state_changed.emit(
                    False
                )

                print(
                    "LYRx AI: playback paused"
                )

            else:

                print(
                    "LYRx AI: nothing currently playing"
                )

        except Exception as error:

            print(
                "AI pause error:",
                error
            )


    # ========================================================
    # AI ASSISTANT - RESUME
    # ========================================================

    def resume_assistant_song(self):

        try:

            player_widget = (
                self.home.now_playing
            )

            audio_player = (
                player_widget.audio_player
            )

            if not (
                player_widget.current_title
            ):

                print(
                    "AI resume: no song selected"
                )

                return

            audio_player.play()

            player_widget.is_playing = True

            player_widget.play_btn.setText(
                "Ⅱ"
            )

            player_widget.play_state_changed.emit(
                True
            )

            print(
                "LYRx AI: playback resumed"
            )

        except Exception as error:

            print(
                "AI resume error:",
                error
            )


    # ========================================================
    # AI ASSISTANT - STOP
    # ========================================================

    def stop_assistant_song(self):

        try:

            player_widget = (
                self.home.now_playing
            )

            audio_player = (
                player_widget.audio_player
            )

            # ====================================================
            # STOP AUDIO
            # ====================================================

            audio_player.stop()

            # ====================================================
            # RESET STATE
            # ====================================================

            player_widget.is_playing = False

            player_widget.play_btn.setText(
                "▶"
            )

            # ====================================================
            # RESET PROGRESS
            # ====================================================

            player_widget.slider.blockSignals(
                True
            )

            player_widget.slider.setValue(
                0
            )

            player_widget.slider.blockSignals(
                False
            )

            player_widget.current_time.setText(
                "0:00"
            )

            # ====================================================
            # STATE SIGNAL
            # ====================================================

            player_widget.play_state_changed.emit(
                False
            )

            # ====================================================
            # FLOATING PLAYER
            # ====================================================

            if hasattr(
                self,
                "floating_player"
            ):

                self.floating_player.set_playing(
                    False
                )

                self.floating_player.progress.setValue(
                    0
                )

                self.floating_player.current_time.setText(
                    "0:00"
                )

            print(
                "LYRx AI: playback stopped"
            )

        except Exception as error:

            print(
                "AI stop error:",
                error
            )


    # ========================================================
    # AI ASSISTANT - NEXT SONG
    # ========================================================

    def next_assistant_song(self):

        try:

            # Use the SAME queue logic already used by Home.
            self.home.play_next()

            print(
                "LYRx AI: next song"
            )

        except Exception as error:

            print(
                "AI next error:",
                error
            )


    # ========================================================
    # AI ASSISTANT - PREVIOUS SONG
    # ========================================================

    def previous_assistant_song(self):

        try:

            self.home.play_previous()

            print(
                "LYRx AI: previous song"
            )

        except Exception as error:

            print(
                "AI previous error:",
                error
            )

    # ========================================================
    # AI ASSISTANT - CREATE PLAYLIST
    # ========================================================

    def create_assistant_playlist(
        self,
        playlist_name,
        description,
        songs
    ):

        try:

            # ====================================================
            # CREATE PLAYLIST
            # ====================================================

            playlist = (
                playlist_store.create_playlist(
                    playlist_name,
                    description
                )
            )

            # ====================================================
            # DUPLICATE PLAYLIST
            # ====================================================

            if playlist is None:

                existing_playlist = None

                for item in (
                    playlist_store.get_playlists()
                ):

                    if (
                        item.get(
                            "name",
                            ""
                        ).strip().lower()
                        ==
                        playlist_name
                        .strip()
                        .lower()
                    ):

                        existing_playlist = item

                        break

                if existing_playlist is None:

                    self.assistant.add_ai_message(
                        "I couldn't create the playlist. "
                        "Please try again."
                    )

                    return

                playlist = existing_playlist

            # ====================================================
            # PLAYLIST ID
            # ====================================================

            playlist_id = playlist.get(
                "id"
            )

            if not playlist_id:

                self.assistant.add_ai_message(
                    "I couldn't access the playlist."
                )

                return

            # ====================================================
            # ADD SONGS
            # ====================================================

            added_titles = []

            for song in songs:

                image_path = song.get(
                    "image",
                    ""
                )

                title = song.get(
                    "title",
                    ""
                )

                artist = song.get(
                    "artist",
                    ""
                )

                success, message = (
                    playlist_store.add_song(
                        playlist_id,
                        image_path,
                        title,
                        artist
                    )
                )

                # ------------------------------------------------
                # SUCCESS
                # ------------------------------------------------

                if success:

                    added_titles.append(
                        title
                    )

                # ------------------------------------------------
                # ALREADY EXISTS
                # ------------------------------------------------

                else:

                    existing_songs = (
                        playlist.get(
                            "songs",
                            []
                        )
                    )

                    already_exists = any(

                        existing.get(
                            "title",
                            ""
                        ).strip().lower()
                        ==
                        title.strip().lower()

                        and

                        existing.get(
                            "artist",
                            ""
                        ).strip().lower()
                        ==
                        artist.strip().lower()

                        for existing in existing_songs
                    )

                    if already_exists:

                        added_titles.append(
                            title
                        )

            # ====================================================
            # REFRESH PLAYLIST PAGE
            # ====================================================

            try:

                self.playlists.playlists = (
                    playlist_store.get_playlists()
                )

                self.playlists.rebuild_playlist_cards()

            except Exception as error:

                print(
                    "AI playlist page refresh error:",
                    error
                )

            # ====================================================
            # REFRESH HOME PLAYLIST PREVIEW
            # ====================================================

            try:

                self.home.refresh_playlist_preview()

            except Exception as error:

                print(
                    "AI home playlist refresh error:",
                    error
                )

            # ====================================================
            # RESPONSE
            # ====================================================

            if added_titles:

                song_lines = "\n".join(
                    f"• {title}"
                    for title
                    in added_titles
                )

                self.assistant.add_ai_message(
                    "Playlist created. 💜\n\n"
                    f"{playlist_name}\n\n"
                    f"{song_lines}\n\n"
                    "You can open it from the "
                    "Playlists section."
                )

            else:

                self.assistant.add_ai_message(
                    f'"{playlist_name}" is ready, '
                    "but no new tracks needed to be added."
                )

            print(
                "LYRx AI playlist ready:",
                playlist_name
            )

        except Exception as error:

            print(
                "AI playlist creation error:",
                error
            )

            try:

                self.assistant.add_ai_message(
                    "Something went wrong while "
                "creating the playlist."
                )

            except Exception:

                pass

    # ========================================================
    # FLOATING PLAY / PAUSE
    # ========================================================

    def toggle_floating_play(self):

        try:

            player = (
                self.home
                .now_playing
                .audio_player
            )

            from PySide6.QtMultimedia import QMediaPlayer

            state = player.playbackState()

            if (
                state
                == QMediaPlayer
                .PlaybackState
                .PlayingState
            ):

                player.pause()

            else:

                player.play()

        except Exception as error:

            print(
                "Floating play/pause error:",
                error
            )

    # ========================================================
    # FLOATING PREVIOUS
    # ========================================================

    def previous_floating_song(self):

        try:

            self.home.now_playing.previous_requested.emit()

        except Exception as error:

            print(
                "Previous song error:",
                error
            )

    # ========================================================
    # FLOATING NEXT
    # ========================================================

    def next_floating_song(self):

        try:

            self.home.now_playing.next_requested.emit()

        except Exception as error:

            print(
                "Next song error:",
                error
            )

    # ========================================================
    # CLOSE FLOATING PLAYER
    # ========================================================

    def close_floating_player(self):

        self.floating_player.hide()

        try:

            self.home.now_playing.audio_player.stop()

        except Exception as error:

            print(
                "Close player error:",
                error
            )

    # ========================================================
    # SONG SYNC
    # ========================================================

    def sync_floating_song(
        self,
        image_path,
        title,
        artist
    ):

        try:

            self.floating_player.set_song(
                image_path,
                title,
                artist
            )

            self.update_floating_visibility()

            self.position_floating_player()

            self.floating_player.raise_()

        except Exception as error:

            print(
                "Floating song sync error:",
                error
            )

    # ========================================================
    # PROGRESS SYNC
    # ========================================================

    def sync_floating_progress(
        self,
        position
    ):

        try:

            duration = (
                self.home
                .now_playing
                .audio_player
                .duration()
            )

            if duration <= 0:
                return

            progress = int(
                position
                / duration
                * 100
            )

            self.floating_player.set_progress(
                progress,
                self.format_time(position),
                self.format_time(duration)
            )

        except Exception as error:

            print(
                "Floating progress error:",
                error
            )

    # ========================================================
    # DURATION SYNC
    # ========================================================

    def sync_floating_duration(
        self,
        duration
    ):

        if duration <= 0:
            return

        self.floating_player.total_time.setText(
            self.format_time(duration)
        )

    # ========================================================
    # PLAY STATE SYNC
    # ========================================================

    def sync_floating_play_state(
        self,
        state
    ):

        try:

            from PySide6.QtMultimedia import QMediaPlayer

            playing = (
                state
                == QMediaPlayer
                .PlaybackState
                .PlayingState
            )

            self.floating_player.set_playing(
                playing
            )

        except Exception as error:

            print(
                "Floating play state error:",
                error
            )

    # ========================================================
    # FORMAT TIME
    # ========================================================

    @staticmethod
    def format_time(
        milliseconds
    ):

        if (
            milliseconds is None
            or milliseconds <= 0
        ):

            return "0:00"

        total_seconds = (
            milliseconds // 1000
        )

        minutes = (
            total_seconds // 60
        )

        seconds = (
            total_seconds % 60
        )

        return (
            f"{minutes}:"
            f"{seconds:02d}"
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

        self.position_floating_player()

    # ========================================================
    # POSITION FLOATING PLAYER
    # ========================================================

    def position_floating_player(self):

        if not hasattr(
            self,
            "floating_player"
        ):

            return

        player = self.floating_player

        if not player.isVisible():
            return

        current = self.pages.currentWidget()

        if current not in (
            self.discover,
            self.favorites,
            self.library
        ):

            return

        page = current

        main = getattr(
            page,
            "main",
            None
        )

        # ----------------------------------------------------
        # CENTER PLAYER
        # ----------------------------------------------------

        if main is None:

            x = (
                self.width()
                - player.width()
            ) // 2

        else:

            top_left = main.mapTo(
                self,
                main.rect().topLeft()
            )

            x = (
                top_left.x()
                + (
                    main.width()
                    - player.width()
                ) // 2
            )

        # ----------------------------------------------------
        # BOTTOM
        # ----------------------------------------------------

        y = (
            self.height()
            - player.height()
            - 18
        )

        # ----------------------------------------------------
        # KEEP INSIDE WINDOW
        # ----------------------------------------------------

        x = max(
            10,
            min(
                x,
                self.width()
                - player.width()
                - 10
            )
        )

        y = max(
            10,
            min(
                y,
                self.height()
                - player.height()
                - 10
            )
        )

        player.move(
            int(x),
            int(y)
        )

        player.raise_()

    # ========================================================
    # SHOW
    # ========================================================

    def showEvent(
        self,
        event
    ):

        super().showEvent(
            event
        )

        self.update_floating_visibility()

        self.position_floating_player()

        if self.floating_player.isVisible():

            self.floating_player.raise_()
