from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
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
)

from ui.home.home_screen import HomeScreen
from ui.favorites.favorites_screen import FavoritesScreen
from ui.discover.discover_screen import DiscoverScreen
from ui.basic_page import BasicPage
from ui.library.library_screen import LibraryScreen


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

        # ====================================================
        # PLAYER STATE
        # ====================================================

        self.current_image = ""
        self.current_title = ""
        self.current_artist = ""

        self.is_playing = True

        # ====================================================
        # SIZE
        # ====================================================

        self.setFixedSize(
            820,
            82
        )

        # ====================================================
        # STYLE
        # ====================================================

        self.setStyleSheet("""
        QFrame#FloatingPlayer {

            background: rgba(24, 18, 42, 248);

            border: 1px solid rgba(139, 92, 246, 115);

            border-radius: 20px;

        }

        QLabel {

            background: transparent;

        }

        QPushButton {

            background: transparent;

            color: #AAA0C5;

            border: none;

            border-radius: 18px;

        }

        QPushButton:hover {

            background: rgba(139, 92, 246, 45);

            color: white;

        }

        QPushButton:pressed {

            background: rgba(139, 92, 246, 75);

        }

        QSlider::groove:horizontal {

            height: 3px;

            background: #3A304F;

            border-radius: 2px;

        }

        QSlider::sub-page:horizontal {

            background: #8B5CF6;

            border-radius: 2px;

        }

        QSlider::handle:horizontal {

            width: 9px;

            height: 9px;

            margin: -3px 0;

            border-radius: 5px;

            background: white;

        }

        QSlider::handle:horizontal:hover {

            background: #B58AFF;

        }
        """)

        self.build_ui()

        self.hide()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(
            14,
            10,
            14,
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

        self.album.setStyleSheet("""
        QLabel {

            background: #24183D;

            border-radius: 11px;

        }
        """)

        root.addWidget(
            self.album
        )

        # ====================================================
        # SONG INFORMATION
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

        self.song_label.setStyleSheet("""
        QLabel {

            color: white;

            font-size: 13px;

            font-weight: 700;

        }
        """)

        self.artist_label = QLabel(
            "Select a song to start listening"
        )

        self.artist_label.setStyleSheet("""
        QLabel {

            color: #8F84A8;

            font-size: 11px;

        }
        """)

        info.addWidget(
            self.song_label
        )

        info.addWidget(
            self.artist_label
        )

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

        self.previous_button.setFixedSize(
            36,
            36
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

        self.play_button.setFixedSize(
            44,
            44
        )

        self.play_button.setStyleSheet("""
        QPushButton {

            background: #8B5CF6;

            color: white;

            border: none;

            border-radius: 22px;

            font-size: 16px;

            font-weight: 700;

        }

        QPushButton:hover {

            background: #A970FF;

        }

        QPushButton:pressed {

            background: #6D28D9;

        }
        """)

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

        self.next_button.setFixedSize(
            36,
            36
        )

        self.next_button.clicked.connect(
            self.next_requested.emit
        )

        root.addWidget(
            self.next_button
        )

        # ====================================================
        # PROGRESS
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

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            0
        )

        progress_layout.addWidget(
            self.progress
        )

        # ====================================================
        # TIME
        # ====================================================

        time_layout = QHBoxLayout()

        self.current_time = QLabel(
            "0:00"
        )

        self.total_time = QLabel(
            "0:00"
        )

        for label in (
            self.current_time,
            self.total_time
        ):

            label.setStyleSheet("""
            QLabel {

                color: #756A91;

                font-size: 9px;

            }
            """)

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
        # CLOSE
        # ====================================================

        self.close_button = QPushButton(
            "×"
        )

        self.close_button.setFixedSize(
            30,
            30
        )

        self.close_button.setStyleSheet("""
        QPushButton {

            color: #756A91;

            font-size: 20px;

            border-radius: 15px;

        }

        QPushButton:hover {

            color: white;

            background: rgba(255,255,255,20);

        }
        """)

        self.close_button.clicked.connect(
            self.close_requested.emit
        )

        root.addWidget(
            self.close_button
        )

    # ========================================================
    # SET SONG
    # ========================================================

    def set_song(
        self,
        image_path,
        title,
        artist
    ):

        self.current_image = image_path
        self.current_title = title
        self.current_artist = artist

        self.song_label.setText(
            title
        )

        self.artist_label.setText(
            artist
        )

        # ====================================================
        # FIND IMAGE
        # ====================================================

        from pathlib import Path

        file_dir = Path(__file__).resolve()

        project_dir = file_dir.parents[2]

        candidates = [

            project_dir / image_path,

            file_dir.parents[1] / image_path,

            Path.cwd() / image_path,

            Path(image_path)

        ]

        image_file = None

        for path in candidates:

            try:

                if path.exists() and path.is_file():

                    image_file = path

                    break

            except Exception:

                pass

        # ====================================================
        # SET IMAGE
        # ====================================================

        if image_file:

            pix = QPixmap(
                str(image_file)
            )

            if not pix.isNull():

                scaled = pix.scaled(
                    58,
                    58,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                self.album.setPixmap(
                    scaled
                )

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

        if playing:

            self.play_button.setText(
                "Ⅱ"
            )

        else:

            self.play_button.setText(
                "▶"
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

        self.progress.blockSignals(
            True
        )

        self.progress.setValue(
            value
        )

        self.progress.blockSignals(
            False
        )

        if current_time is not None:

            self.current_time.setText(
                current_time
            )

        if total_time is not None:

            self.total_time.setText(
                total_time
            )


# ============================================================
# APP WINDOW
# ============================================================

class AppWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        # ====================================================
        # WINDOW SETTINGS
        # ====================================================

        self.setWindowTitle(
            "🎵 LYRx"
        )

        self.setWindowFlags(
            Qt.FramelessWindowHint
        )

        # ====================================================
        # SCREEN SIZE
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

        # ====================================================
        # CENTER WINDOW
        # ====================================================

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

        # ====================================================
        # OTHER PAGES
        # ====================================================

        self.playlists = BasicPage(
            "Playlists",
            "Create and manage your playlists.",
            "☷"
        )

        self.settings = BasicPage(
            "Settings",
            "Customize your LYRx experience.",
            "⚙"
        )

        self.pages.addWidget(
            self.library
        )

        self.pages.addWidget(
            self.playlists
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
            self.settings.sidebar

        ]

        for sidebar in self.sidebars:

            sidebar.page_changed.connect(
                self.handle_page_change
            )

        # ====================================================
        # DISCOVER SONG
        # ====================================================

        self.discover.song_requested.connect(
            self.play_discover_song
        )

        # ====================================================
        # FAVORITE SONG
        # ====================================================

        self.favorites.play_requested.connect(
            self.play_favorite_song
        )

        # ====================================================
        # FLOATING PLAYER
        # ====================================================

        self.floating_player = FloatingPlayer(
            self
        )

        self.floating_player.hide()

        # ====================================================
        # FLOATING PLAYER SIGNALS
        # ====================================================

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
        # HOME PLAYER SIGNAL SYNC
        # ====================================================

        try:

            now_playing = self.home.now_playing

            # ------------------------------------------------
            # SONG CHANGE
            # ------------------------------------------------

            now_playing.song_changed.connect(
                self.sync_floating_song
            )

            # ------------------------------------------------
            # PROGRESS
            # ------------------------------------------------

            now_playing.audio_player.positionChanged.connect(
                self.sync_floating_progress
            )

            # ------------------------------------------------
            # DURATION
            # ------------------------------------------------

            now_playing.audio_player.durationChanged.connect(
                self.sync_floating_duration
            )

            # ------------------------------------------------
            # PLAY / PAUSE
            # ------------------------------------------------

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

        self.update_floating_visibility()

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
        # REFRESH FAVORITES
        # ====================================================

        if page_name == "Favorites":

            self.favorites.reload_favorites()

        # ====================================================
        # CHANGE PAGE
        # ====================================================

        self.pages.setCurrentWidget(
            target_page
        )

        self.update_sidebar_states(
            page_name
        )

        # ====================================================
        # FLOATING PLAYER
        # ====================================================

        self.update_floating_visibility()

        self.position_floating_player()

        print(
            f"Page changed: {page_name}"
        )

    # ========================================================
    # FLOATING PLAYER VISIBILITY
    # ========================================================

    def update_floating_visibility(self):

        current = self.pages.currentWidget()

        # ====================================================
        # HOME
        # ====================================================

        if current is self.home:

            self.floating_player.hide()

            return

        # ====================================================
        # DISCOVER / FAVORITES / LIBRARY
        # ====================================================

        if current in (
            self.discover,
            self.favorites,
            self.library
        ):

            # ------------------------------------------------
            # Show only when a song exists
            # ------------------------------------------------

            if (
                self.floating_player.current_title
                and self.floating_player.current_image
            ):

                self.floating_player.show()

                self.position_floating_player()

                self.floating_player.raise_()

            return

        # ====================================================
        # OTHER PAGES
        # ====================================================

        self.floating_player.hide()

    # ========================================================
    # SIDEBAR STATES
    # ========================================================

    def update_sidebar_states(
        self,
        page_name: str
    ):

        for sidebar in self.sidebars:

            for button in sidebar.buttons:

                button.blockSignals(
                    True
                )

                button.setChecked(
                    button.page_name == page_name
                )

                button.blockSignals(
                    False
                )

    # ========================================================
    # DISCOVER SONG
    # ========================================================

    def play_discover_song(
        self,
        image_path,
        title,
        artist
    ):

        print(
            f"Playing from Discover: "
            f"{title} - {artist}"
        )

        # ====================================================
        # START AUDIO
        # ====================================================

        self.home.play_selected_song(
            image_path,
            title,
            artist
        )

        # ====================================================
        # UPDATE FLOATING PLAYER
        # ====================================================

        self.floating_player.set_song(
            image_path,
            title,
            artist
        )

        # ====================================================
        # STAY ON DISCOVER
        # ====================================================

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
    # FAVORITE SONG
    # ========================================================

    def play_favorite_song(
        self,
        image_path,
        title,
        artist
    ):

        print(
            f"Playing from Favorites: "
            f"{title} - {artist}"
        )

        # ====================================================
        # START AUDIO
        # ====================================================

        self.home.play_selected_song(
            image_path,
            title,
            artist
        )

        # ====================================================
        # UPDATE FLOATING PLAYER
        # ====================================================

        self.floating_player.set_song(
            image_path,
            title,
            artist
        )

        # ====================================================
        # STAY ON FAVORITES
        # ====================================================

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

        print(
            f"Playing from Library: "
            f"{title} - {artist}"
        )

        # ====================================================
        # START ACTUAL AUDIO
        # ====================================================

        self.home.play_selected_song(
            image_path,
            title,
            artist
        )

        # ====================================================
        # UPDATE FLOATING PLAYER
        # ====================================================
        # THIS WAS MISSING BEFORE.

        self.floating_player.set_song(
            image_path,
            title,
            artist
        )

        # ====================================================
        # STAY ON LIBRARY
        # ====================================================

        self.pages.setCurrentWidget(
            self.library
        )

        self.update_sidebar_states(
            "Library"
        )

        # ====================================================
        # SHOW + POSITION
        # ====================================================

        self.update_floating_visibility()

        self.position_floating_player()

        self.floating_player.raise_()

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

            state = player.playbackState()

            if (
                state
                == player.PlaybackState.PlayingState
            ):

                player.pause()

                self.floating_player.set_playing(
                    False
                )

            else:

                player.play()

                self.floating_player.set_playing(
                    True
                )

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
    # SYNC FLOATING SONG
    # ========================================================

    def sync_floating_song(
        self,
        image_path,
        title,
        artist
    ):

        try:

            print(
                f"Floating player song sync: "
                f"{title} - {artist}"
            )

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
    # SYNC FLOATING PROGRESS
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
                (
                    position / duration
                ) * 100
            )

            current_time = self.format_time(
                position
            )

            total_time = self.format_time(
                duration
            )

            self.floating_player.set_progress(
                progress,
                current_time,
                total_time
            )

        except Exception as error:

            print(
                "Floating progress error:",
                error
            )

    # ========================================================
    # SYNC FLOATING DURATION
    # ========================================================

    def sync_floating_duration(
        self,
        duration
    ):

        if duration <= 0:

            return

        self.floating_player.total_time.setText(
            self.format_time(
                duration
            )
        )

    # ========================================================
    # SYNC PLAY STATE
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
    # RESIZE EVENT
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

        # ====================================================
        # DISCOVER / FAVORITES / LIBRARY
        # ====================================================

        if current not in (
            self.discover,
            self.favorites,
            self.library
        ):

            return

        # ====================================================
        # FIND PAGE MAIN CONTENT
        # ====================================================

        page = current

        main = getattr(
            page,
            "main",
            None
        )

        if main is None:

            parent_width = self.width()

            x = (
                parent_width
                - player.width()
            ) // 2

        else:

            main_top_left = main.mapTo(
                self,
                main.rect().topLeft()
            )

            main_width = main.width()

            x = (
                main_top_left.x()
                + (
                    main_width
                    - player.width()
                ) // 2
            )

        # ====================================================
        # BOTTOM POSITION
        # ====================================================

        margin_bottom = 18

        y = (
            self.height()
            - player.height()
            - margin_bottom
        )

        # ====================================================
        # SAFETY BOUNDARIES
        # ====================================================

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

        # ====================================================
        # MOVE
        # ====================================================

        player.move(
            int(x),
            int(y)
        )

        player.raise_()

    # ========================================================
    # SHOW EVENT
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