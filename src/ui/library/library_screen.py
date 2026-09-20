from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QFileDialog,
)

from widgets.sidebar import Sidebar
from widgets.cards.music_card import MusicCard
from core.local_media import read_local_media, format_duration


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# LIBRARY SCREEN
# ============================================================

class LibraryScreen(QWidget):

    # --------------------------------------------------------
    # SIGNALS
    # --------------------------------------------------------

    song_requested = Signal(
        str,
        str,
        str
    )

    # DAY 29.2 - full local file path + display metadata
    local_song_requested = Signal(
        str, str, str, str
    )

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "🎵 LYRx - Library"
        )

        self.setMinimumSize(
            1200,
            700
        )

        # ----------------------------------------------------
        # THEME STATE
        # ----------------------------------------------------

        self.current_is_dark = True

        # ----------------------------------------------------
        # MUSIC DATA
        # ----------------------------------------------------

        self.settings = QSettings(
            "LYRx",
            "DesktopMusicPlayer"
        )

        # Each item:
        # (cover_path, title, artist, local_audio_path_or_empty)
        self.library_songs = [
            (
                "assets/album_art/believer.jpg",
                "Believer",
                "Imagine Dragons",
                "",
            ),
            (
                "assets/album_art/faded.jpg",
                "Faded",
                "Alan Walker",
                "",
            ),
            (
                "assets/album_art/arcade.jpg",
                "Arcade",
                "Duncan Laurence",
                "",
            ),
            (
                "assets/album_art/lethergo.jpg",
                "Let Her Go",
                "Passenger",
                "",
            ),
        ]

        self._load_local_library()

        self.music_cards = []

        self.build_ui()

        self.populate_library()

        # ----------------------------------------------------
        # DEFAULT DARK
        # ----------------------------------------------------

        self.set_theme_state(
            True
        )

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # ROOT
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.sidebar
        )

        # ----------------------------------------------------
        # MAIN
        # ----------------------------------------------------

        self.main = QWidget()

        self.main.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.main.setStyleSheet("""
        QWidget {
            background: transparent;
        }
        """)

        root.addWidget(
            self.main,
            1
        )

        main_layout = QVBoxLayout(
            self.main
        )

        main_layout.setContentsMargins(
            28,
            24,
            28,
            22
        )

        main_layout.setSpacing(
            18
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

        main_layout.addWidget(
            self.scroll
        )

        # ====================================================
        # CONTENT
        # ====================================================

        self.content = QWidget()

        self.content.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.content.setStyleSheet("""
        QWidget {
            background: transparent;
        }
        """)

        self.scroll.setWidget(
            self.content
        )

        self.content_layout = QVBoxLayout(
            self.content
        )

        self.content_layout.setContentsMargins(
            0,
            0,
            4,
            20
        )

        self.content_layout.setSpacing(
            20
        )

        self.content_layout.setAlignment(
            Qt.AlignTop
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0
        )

        header_text = QVBoxLayout()

        header_text.setSpacing(
            4
        )

        self.title = QLabel(
            "Your Library"
        )

        header_text.addWidget(
            self.title
        )

        self.subtitle = QLabel(
            "Everything you love, all in one place."
        )

        header_text.addWidget(
            self.subtitle
        )

        header.addLayout(
            header_text
        )

        header.addStretch()

        # ====================================================
        # SONG COUNT
        # ====================================================

        self.song_count = QLabel(
            "0 songs"
        )

        self.song_count.setAlignment(
            Qt.AlignCenter
        )

        self.song_count.setMinimumWidth(
            90
        )

        header.addWidget(
            self.song_count
        )

        self.content_layout.addLayout(
            header
        )

        # ====================================================
        # FEATURE PANEL
        # ====================================================

        self.feature = QFrame()

        self.feature.setMinimumHeight(
            130
        )

        self.feature.setObjectName(
            "LibraryFeature"
        )

        feature_layout = QHBoxLayout(
            self.feature
        )

        feature_layout.setContentsMargins(
            24,
            18,
            24,
            18
        )

        feature_text = QVBoxLayout()

        self.feature_title = QLabel(
            "Your music. Your collection."
        )

        feature_text.addWidget(
            self.feature_title
        )

        feature_text.addSpacing(
            4
        )

        self.feature_subtitle = QLabel(
            "Pick a track and let LYRx take care of the rest."
        )

        feature_text.addWidget(
            self.feature_subtitle
        )

        feature_text.addStretch()

        feature_layout.addLayout(
            feature_text
        )

        feature_layout.addStretch()

        self.music_icon = QLabel(
            "♫"
        )

        self.music_icon.setAlignment(
            Qt.AlignCenter
        )

        feature_layout.addWidget(
            self.music_icon
        )

        self.content_layout.addWidget(
            self.feature
        )

        # ====================================================
        # TOOLBAR
        # ====================================================

        toolbar = QHBoxLayout()

        toolbar.setSpacing(
            10
        )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search your library..."
        )

        self.search.setClearButtonEnabled(
            True
        )

        self.search.setMinimumHeight(
            42
        )

        self.search.textChanged.connect(
            self.filter_library
        )

        toolbar.addWidget(
            self.search,
            1
        )

        # ----------------------------------------------------
        # ADD LOCAL MUSIC BUTTON
        # ----------------------------------------------------

        self.all_button = QPushButton(
            "＋ Add Local Music"
        )

        self.all_button.setCursor(
            Qt.PointingHandCursor
        )

        self.all_button.setMinimumHeight(
            42
        )

        self.all_button.clicked.connect(
            self.add_local_music
        )

        toolbar.addWidget(
            self.all_button
        )

        self.content_layout.addLayout(
            toolbar
        )

        # ====================================================
        # SECTION HEADER
        # ====================================================

        section_header = QHBoxLayout()

        self.section_title = QLabel(
            "All Songs"
        )

        section_header.addWidget(
            self.section_title
        )

        section_header.addStretch()

        self.result_label = QLabel(
            "4 tracks"
        )

        section_header.addWidget(
            self.result_label
        )

        self.content_layout.addLayout(
            section_header
        )

        # ====================================================
        # CARD GRID
        # ====================================================

        self.grid_container = QWidget()

        self.grid_container.setStyleSheet("""
        QWidget {
            background: transparent;
        }
        """)

        self.grid = QGridLayout(
            self.grid_container
        )

        self.grid.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.grid.setHorizontalSpacing(
            16
        )

        self.grid.setVerticalSpacing(
            18
        )

        self.content_layout.addWidget(
            self.grid_container
        )

        # ====================================================
        # EMPTY STATE
        # ====================================================

        self.empty_state = QLabel(
            "No songs found in your library."
        )

        self.empty_state.setAlignment(
            Qt.AlignCenter
        )

        self.empty_state.setMinimumHeight(
            180
        )

        self.empty_state.hide()

        self.content_layout.addWidget(
            self.empty_state
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

        if self.current_is_dark:

            self.apply_dark_theme()

        else:

            self.apply_light_theme()

        # ----------------------------------------------------
        # UPDATE MUSIC CARDS
        # ----------------------------------------------------

        for card in self.music_cards:

            try:

                if hasattr(
                    card,
                    "set_theme_state"
                ):

                    card.set_theme_state(
                        self.current_is_dark
                    )

                elif hasattr(
                    card,
                    "apply_theme"
                ):

                    card.apply_theme(
                        self.current_is_dark
                    )

            except Exception as error:

                print(
                    "Library MusicCard theme error:",
                    error
                )

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        try:

            self.sidebar.set_theme_state(
                self.current_is_dark
            )

        except Exception as error:

            print(
                "Library sidebar theme error:",
                error
            )

        self.update()

    # ========================================================
    # DARK THEME
    # ========================================================

    def apply_dark_theme(
        self
    ):

        # ----------------------------------------------------
        # MAIN TEXT
        # ----------------------------------------------------

        self.title.setStyleSheet("""
        QLabel {
            color: #FFFFFF;
            font-size: 34px;
            font-weight: 800;
            background: transparent;
        }
        """)

        self.subtitle.setStyleSheet("""
        QLabel {
            color: #9D94B8;
            font-size: 14px;
            background: transparent;
        }
        """)

        # ----------------------------------------------------
        # SONG COUNT
        # ----------------------------------------------------

        self.song_count.setStyleSheet("""
        QLabel {
            color: #C9B8F4;
            background: rgba(124,58,237,35);
            border: 1px solid rgba(139,92,246,70);
            border-radius: 14px;
            padding: 9px 14px;
            font-size: 12px;
            font-weight: 600;
        }
        """)

        # ----------------------------------------------------
        # FEATURE
        # ----------------------------------------------------

        self.feature.setStyleSheet("""
        QFrame#LibraryFeature {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 0,
                stop: 0 #211635,
                stop: 0.55 #302052,
                stop: 1 #472A78
            );

            border: 1px solid rgba(139,92,246,80);
            border-radius: 22px;
        }

        QFrame#LibraryFeature:hover {
            border: 1px solid rgba(180,140,255,150);
        }
        """)

        self.feature_title.setStyleSheet("""
        QLabel {
            color: #FFFFFF;
            font-size: 21px;
            font-weight: 800;
            background: transparent;
        }
        """)

        self.feature_subtitle.setStyleSheet("""
        QLabel {
            color: #B8ACD2;
            font-size: 13px;
            background: transparent;
        }
        """)

        self.music_icon.setStyleSheet("""
        QLabel {
            color: #B77AFF;
            font-size: 58px;
            font-weight: 800;
            background: transparent;
        }
        """)

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        self.search.setStyleSheet("""
        QLineEdit {
            color: #FFFFFF;
            background: #171126;
            border: 1px solid #342553;
            border-radius: 13px;
            padding-left: 14px;
            padding-right: 14px;
            font-size: 13px;
            selection-background-color: #7C3AED;
        }

        QLineEdit:hover {
            border: 1px solid #5C3B8D;
        }

        QLineEdit:focus {
            border: 1px solid #8B5CF6;
            background: #1C1430;
        }

        QLineEdit::placeholder {
            color: #756A91;
        }
        """)

        # ----------------------------------------------------
        # ALL SONGS
        # ----------------------------------------------------

        self.all_button.setStyleSheet("""
        QPushButton {
            color: #FFFFFF;
            background: #7C3AED;
            border: 1px solid #9B67F3;
            border-radius: 13px;
            padding: 0 16px;
            font-size: 12px;
            font-weight: 600;
        }

        QPushButton:hover {
            background: #9555F5;
            border: 1px solid #C6A5FF;
        }

        QPushButton:pressed {
            background: #6325B5;
        }
        """)

        # ----------------------------------------------------
        # SECTION
        # ----------------------------------------------------

        self.section_title.setStyleSheet("""
        QLabel {
            color: #FFFFFF;
            font-size: 23px;
            font-weight: 700;
            background: transparent;
        }
        """)

        self.result_label.setStyleSheet("""
        QLabel {
            color: #756A91;
            font-size: 11px;
            background: transparent;
        }
        """)

        # ----------------------------------------------------
        # EMPTY
        # ----------------------------------------------------

        self.empty_state.setStyleSheet("""
        QLabel {
            color: #716889;
            background: rgba(255,255,255,4);
            border: 1px dashed rgba(139,92,246,55);
            border-radius: 18px;
            font-size: 13px;
        }
        """)

        # ----------------------------------------------------
        # SCROLLBAR
        # ----------------------------------------------------

        self.scroll.setStyleSheet("""
        QScrollArea {
            background: transparent;
            border: none;
        }

        QScrollArea > QWidget > QWidget {
            background: transparent;
        }

        QScrollBar:vertical {
            width: 8px;
            background: transparent;
            margin: 2px;
        }

        QScrollBar::handle:vertical {
            background: #6F3CC4;
            border-radius: 4px;
            min-height: 50px;
        }

        QScrollBar::handle:vertical:hover {
            background: #9B62F0;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }
        """)

    # ========================================================
    # LIGHT THEME
    # ========================================================

    def apply_light_theme(
        self
    ):

        # ----------------------------------------------------
        # MAIN TEXT
        # ----------------------------------------------------

        self.title.setStyleSheet("""
        QLabel {
            color: #2B2140;
            font-size: 34px;
            font-weight: 800;
            background: transparent;
        }
        """)

        self.subtitle.setStyleSheet("""
        QLabel {
            color: #78698D;
            font-size: 14px;
            background: transparent;
        }
        """)

        # ----------------------------------------------------
        # SONG COUNT
        # ----------------------------------------------------

        self.song_count.setStyleSheet("""
        QLabel {
            color: #68429A;
            background: rgba(124,58,237,12);
            border: 1px solid rgba(124,58,237,42);
            border-radius: 14px;
            padding: 9px 14px;
            font-size: 12px;
            font-weight: 600;
        }
        """)

        # ----------------------------------------------------
        # FEATURE
        # ----------------------------------------------------

        self.feature.setStyleSheet("""
        QFrame#LibraryFeature {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 0,
                stop: 0 #EAE0F8,
                stop: 0.55 #DDD0F2,
                stop: 1 #D3C0EC
            );

            border: 1px solid rgba(124,58,237,48);
            border-radius: 22px;
        }

        QFrame#LibraryFeature:hover {
            border: 1px solid rgba(124,58,237,95);
        }
        """)

        self.feature_title.setStyleSheet("""
        QLabel {
            color: #35254E;
            font-size: 21px;
            font-weight: 800;
            background: transparent;
        }
        """)

        self.feature_subtitle.setStyleSheet("""
        QLabel {
            color: #756489;
            font-size: 13px;
            background: transparent;
        }
        """)

        self.music_icon.setStyleSheet("""
        QLabel {
            color: #8050C6;
            font-size: 58px;
            font-weight: 800;
            background: transparent;
        }
        """)

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        self.search.setStyleSheet("""
        QLineEdit {
            color: #352A45;
            background: #F0EBF7;
            border: 1px solid #D5C9E2;
            border-radius: 13px;
            padding-left: 14px;
            padding-right: 14px;
            font-size: 13px;
            selection-background-color: #8B5CF6;
            selection-color: white;
        }

        QLineEdit:hover {
            background: #F4EFF9;
            border: 1px solid #B9A5D2;
        }

        QLineEdit:focus {
            background: #F7F2FB;
            border: 1px solid #8B5CF6;
        }

        QLineEdit::placeholder {
            color: #9A8CA9;
        }
        """)

        # ----------------------------------------------------
        # ALL SONGS
        # ----------------------------------------------------

        self.all_button.setStyleSheet("""
        QPushButton {
            color: #FFFFFF;
            background: #7C3AED;
            border: 1px solid #9460E8;
            border-radius: 13px;
            padding: 0 16px;
            font-size: 12px;
            font-weight: 600;
        }

        QPushButton:hover {
            background: #8B4AF0;
            border: 1px solid #A97CF4;
        }

        QPushButton:pressed {
            background: #6828C5;
        }
        """)

        # ----------------------------------------------------
        # SECTION
        # ----------------------------------------------------

        self.section_title.setStyleSheet("""
        QLabel {
            color: #352A45;
            font-size: 23px;
            font-weight: 700;
            background: transparent;
        }
        """)

        self.result_label.setStyleSheet("""
        QLabel {
            color: #8A779C;
            font-size: 11px;
            background: transparent;
        }
        """)

        # ----------------------------------------------------
        # EMPTY
        # ----------------------------------------------------

        self.empty_state.setStyleSheet("""
        QLabel {
            color: #897A9A;
            background: rgba(255,255,255,70);
            border: 1px dashed rgba(124,58,237,65);
            border-radius: 18px;
            font-size: 13px;
        }
        """)

        # ----------------------------------------------------
        # SCROLLBAR
        # ----------------------------------------------------

        self.scroll.setStyleSheet("""
        QScrollArea {
            background: transparent;
            border: none;
        }

        QScrollArea > QWidget > QWidget {
            background: transparent;
        }

        QScrollBar:vertical {
            width: 8px;
            background: transparent;
            margin: 2px;
        }

        QScrollBar::handle:vertical {
            background: #9B7ACC;
            border-radius: 4px;
            min-height: 50px;
        }

        QScrollBar::handle:vertical:hover {
            background: #7C3AED;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }
        """)

    # ========================================================
    # POPULATE LIBRARY
    # ========================================================

    def populate_library(
        self,
        songs=None
    ):

        if songs is None:

            songs = self.library_songs

        # ----------------------------------------------------
        # REMOVE OLD CARDS
        # ----------------------------------------------------

        while self.grid.count():

            item = self.grid.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        self.music_cards.clear()

        # ----------------------------------------------------
        # EMPTY
        # ----------------------------------------------------

        if not songs:

            self.empty_state.show()

            self.result_label.setText(
                "0 tracks"
            )

            return

        self.empty_state.hide()

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        columns = 4

        for index, song_data in enumerate(songs):

            image_path,title,artist,local_audio_path,duration_seconds,album = self._normalize_library_item(song_data)

            card = MusicCard(
                image_path,
                title,
                artist
            )

            card.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
            if local_audio_path and duration_seconds:
                for name in ("duration","duration_label","time_label"):
                    label=getattr(card,name,None)
                    if label is not None and hasattr(label,"setText"):
                        label.setText(format_duration(duration_seconds)); break

            if local_audio_path:
                card.play_requested.connect(
                    lambda _img, _title, _artist,
                    audio=local_audio_path,
                    display_title=title,
                    display_artist=artist,
                    cover=image_path:
                    self.handle_local_song_request(audio,display_title,display_artist,cover)
                )
            else:
                card.play_requested.connect(
                    self.handle_song_request
                )

            # ------------------------------------------------
            # APPLY CURRENT THEME TO NEW CARD
            # ------------------------------------------------

            try:

                if hasattr(
                    card,
                    "set_theme_state"
                ):

                    card.set_theme_state(
                        self.current_is_dark
                    )

                elif hasattr(
                    card,
                    "apply_theme"
                ):

                    card.apply_theme(
                        self.current_is_dark
                    )

            except Exception as error:

                print(
                    "New MusicCard theme error:",
                    error
                )

            row = index // columns

            column = index % columns

            self.grid.addWidget(
                card,
                row,
                column
            )

            self.music_cards.append(
                card
            )

        # ----------------------------------------------------
        # COLUMN STRETCH
        # ----------------------------------------------------

        for column in range(columns):

            self.grid.setColumnStretch(
                column,
                1
            )

        # ----------------------------------------------------
        # COUNT
        # ----------------------------------------------------

        count = len(
            songs
        )

        self.result_label.setText(
            f"{count} "
            f"{'track' if count == 1 else 'tracks'}"
        )

        self.song_count.setText(
            f"{count} "
            f"{'song' if count == 1 else 'songs'}"
        )

    # ========================================================
    # SEARCH / FILTER
    # ========================================================

    def filter_library(
        self,
        text
    ):

        query = text.strip().lower()

        if not query:

            self.populate_library()

            return

        filtered = []

        for song in self.library_songs:

            image_path,title,artist,local_audio_path,duration_seconds,album = self._normalize_library_item(song)
            searchable=f"{title} {artist} {album} {local_audio_path}".lower()

            if query in searchable:

                filtered.append(
                    song
                )

        self.populate_library(
            filtered
        )

    # ========================================================
    # DAY 29.2 - LOCAL MUSIC LIBRARY
    # ========================================================

    @staticmethod
    def _normalize_library_item(song):
        v=list(song)
        while len(v)<6: v.append(0 if len(v)==4 else "")
        try: duration=int(v[4] or 0)
        except: duration=0
        return v[0],v[1],v[2],v[3],duration,v[5]

    def _load_local_library(self):
        saved = self.settings.value(
            "library/local_files",
            [],
        )

        if isinstance(saved, str):
            saved = [saved] if saved else []

        seen = set()

        for raw_path in saved or []:
            audio_path = Path(str(raw_path))

            if (
                not audio_path.exists()
                or not audio_path.is_file()
            ):
                continue

            resolved = str(audio_path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)

            self.library_songs.append(
                self._library_item_from_file(
                    audio_path
                )
            )

    def _library_item_from_file(self, audio_path):
        m=read_local_media(audio_path)
        return (m["cover_path"],m["title"],m["artist"],m["path"],m["duration"],m["album"])

    def _save_local_library(self):
        local_files = []

        for song in self.library_songs:
            _,_,_,audio_path,_,_ = self._normalize_library_item(song)
            if audio_path:
                local_files.append(audio_path)

        self.settings.setValue(
            "library/local_files",
            local_files,
        )
        self.settings.sync()

    def add_local_music(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Add music to LYRx",
            str(Path.home() / "Music"),
            (
                "Audio Files "
                "(*.mp3 *.wav *.flac *.m4a *.aac *.ogg *.wma);;"
                "All Files (*)"
            ),
        )

        if not files:
            return

        existing = {
            self._normalize_library_item(song)[3]
            for song in self.library_songs
            if self._normalize_library_item(song)[3]
        }

        added = 0

        for file_path in files:
            audio_path = Path(file_path)

            if not audio_path.exists():
                continue

            resolved = str(audio_path.resolve())
            if resolved in existing:
                continue

            self.library_songs.append(
                self._library_item_from_file(
                    audio_path
                )
            )
            existing.add(resolved)
            added += 1

        if added:
            self._save_local_library()
            self.search.clear()
            self.populate_library()

    def handle_local_song_request(self,audio_path,title,artist,cover_path):
        self.local_song_requested.emit(str(audio_path),str(title),str(artist),str(cover_path or ""))

    # ========================================================
    # CLEAR SEARCH
    # ========================================================

    def clear_search(
        self
    ):

        self.search.clear()

        self.populate_library()

    # ========================================================
    # PLAY SONG
    # ========================================================

    def handle_song_request(
        self,
        image_path,
        title,
        artist
    ):

        print(
            f"Library song selected: "
            f"{title} - {artist}"
        )

        self.song_requested.emit(
            image_path,
            title,
            artist
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
        # DARK BACKGROUND
        # ====================================================

        if self.current_is_dark:

            gradient = QLinearGradient(
                0,
                0,
                rect.width(),
                rect.height()
            )

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

            painter.fillRect(
                rect,
                gradient
            )

            # -----------------------------------------------
            # TOP PURPLE GLOW
            # -----------------------------------------------

            painter.setPen(
                Qt.NoPen
            )

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    22
                )
            )

            painter.drawEllipse(
                -170,
                -170,
                430,
                360
            )

            # -----------------------------------------------
            # RIGHT AMBIENT GLOW
            # -----------------------------------------------

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    14
                )
            )

            painter.drawEllipse(
                rect.width() - 380,
                100,
                500,
                500
            )

        # ====================================================
        # LIGHT BACKGROUND
        # ====================================================

        else:

            gradient = QLinearGradient(
                0,
                0,
                rect.width(),
                rect.height()
            )

            gradient.setColorAt(
                0.0,
                QColor("#F5F1FA")
            )

            gradient.setColorAt(
                0.45,
                QColor("#EEE8F5")
            )

            gradient.setColorAt(
                1.0,
                QColor("#E9E2F1")
            )

            painter.fillRect(
                rect,
                gradient
            )

            # -----------------------------------------------
            # SOFT PURPLE GLOW
            # -----------------------------------------------

            painter.setPen(
                Qt.NoPen
            )

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    12
                )
            )

            painter.drawEllipse(
                -170,
                -170,
                430,
                360
            )

            # -----------------------------------------------
            # RIGHT SOFT GLOW
            # -----------------------------------------------

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    8
                )
            )

            painter.drawEllipse(
                rect.width() - 380,
                100,
                500,
                500
            )

        painter.end()

        super().paintEvent(
            event
        )