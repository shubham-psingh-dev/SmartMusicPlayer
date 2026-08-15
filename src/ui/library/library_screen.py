from pathlib import Path

from PySide6.QtCore import Qt, Signal
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
)

from widgets.sidebar import Sidebar
from widgets.cards.music_card import MusicCard


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
        # MUSIC DATA
        # ----------------------------------------------------

        self.library_songs = [
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

        self.music_cards = []

        self.build_ui()

        self.populate_library()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # ROOT
        # ----------------------------------------------------

        root = QHBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(0)

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

        title = QLabel(
            "Your Library"
        )

        title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 34px;
            font-weight: 800;
            background: transparent;
        }
        """)

        subtitle = QLabel(
            "Everything you love, all in one place."
        )

        subtitle.setStyleSheet("""
        QLabel {
            color: #9D94B8;
            font-size: 14px;
            background: transparent;
        }
        """)

        header_text.addWidget(
            title
        )

        header_text.addWidget(
            subtitle
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

        header.addWidget(
            self.song_count
        )

        self.content_layout.addLayout(
            header
        )

        # ====================================================
        # FEATURE PANEL
        # ====================================================

        feature = QFrame()

        feature.setMinimumHeight(
            130
        )

        feature.setObjectName(
            "LibraryFeature"
        )

        feature.setStyleSheet("""
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

        feature_layout = QHBoxLayout(
            feature
        )

        feature_layout.setContentsMargins(
            24,
            18,
            24,
            18
        )

        feature_text = QVBoxLayout()

        feature_title = QLabel(
            "Your music. Your collection."
        )

        feature_title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 21px;
            font-weight: 800;
            background: transparent;
        }
        """)

        feature_subtitle = QLabel(
            "Pick a track and let LYRx take care of the rest."
        )

        feature_subtitle.setStyleSheet("""
        QLabel {
            color: #B8ACD2;
            font-size: 13px;
            background: transparent;
        }
        """)

        feature_text.addWidget(
            feature_title
        )

        feature_text.addSpacing(
            4
        )

        feature_text.addWidget(
            feature_subtitle
        )

        feature_text.addStretch()

        feature_layout.addLayout(
            feature_text
        )

        feature_layout.addStretch()

        music_icon = QLabel(
            "♫"
        )

        music_icon.setAlignment(
            Qt.AlignCenter
        )

        music_icon.setStyleSheet("""
        QLabel {
            color: #B77AFF;
            font-size: 58px;
            font-weight: 800;
            background: transparent;
        }
        """)

        feature_layout.addWidget(
            music_icon
        )

        self.content_layout.addWidget(
            feature
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

        self.search.setStyleSheet("""
        QLineEdit {
            color: white;

            background: #171126;

            border: 1px solid #342553;
            border-radius: 13px;

            padding-left: 14px;
            padding-right: 14px;

            font-size: 13px;
        }

        QLineEdit:hover {
            border: 1px solid #5C3B8D;
        }

        QLineEdit:focus {
            border: 1px solid #8B5CF6;
            background: #1C1430;
        }
        """)

        self.search.textChanged.connect(
            self.filter_library
        )

        toolbar.addWidget(
            self.search,
            1
        )

        # ----------------------------------------------------
        # ALL SONGS BUTTON
        # ----------------------------------------------------

        self.all_button = QPushButton(
            "All Songs"
        )

        self.all_button.setCursor(
            Qt.PointingHandCursor
        )

        self.all_button.setMinimumHeight(
            42
        )

        self.all_button.setStyleSheet("""
        QPushButton {
            color: white;

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

        self.all_button.clicked.connect(
            self.clear_search
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

        section_title = QLabel(
            "All Songs"
        )

        section_title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 23px;
            font-weight: 700;
            background: transparent;
        }
        """)

        section_header.addWidget(
            section_title
        )

        section_header.addStretch()

        self.result_label = QLabel(
            "4 tracks"
        )

        self.result_label.setStyleSheet("""
        QLabel {
            color: #756A91;
            font-size: 11px;
            background: transparent;
        }
        """)

        section_header.addWidget(
            self.result_label
        )

        self.content_layout.addLayout(
            section_header
        )

        # ====================================================
        # CARD GRID CONTAINER
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

        self.empty_state.setStyleSheet("""
        QLabel {
            color: #716889;

            background: rgba(255,255,255,4);

            border: 1px dashed rgba(139,92,246,55);
            border-radius: 18px;

            font-size: 13px;
        }
        """)

        self.empty_state.hide()

        self.content_layout.addWidget(
            self.empty_state
        )

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

            item = self.grid.takeAt(0)

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

        for index, (
            image_path,
            title,
            artist
        ) in enumerate(songs):

            card = MusicCard(
                image_path,
                title,
                artist
            )

            card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            card.play_requested.connect(
                self.handle_song_request
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

        count = len(songs)

        self.result_label.setText(
            f"{count} "
            f"{'track' if count == 1 else 'tracks'}"
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

            image_path, title, artist = song

            searchable = (
                f"{title} {artist}"
            ).lower()

            if query in searchable:

                filtered.append(
                    song
                )

        self.populate_library(
            filtered
        )

    # ========================================================
    # CLEAR SEARCH
    # ========================================================

    def clear_search(self):

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

        # ----------------------------------------------------
        # TOP PURPLE GLOW
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # RIGHT AMBIENT GLOW
        # ----------------------------------------------------

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

        painter.end()

        super().paintEvent(
            event
        )