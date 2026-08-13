import json
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QLinearGradient
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QSizePolicy,
)

from widgets.sidebar import Sidebar
from widgets.cards.music_card import MusicCard


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()

# music_player_desktop/
PROJECT_DIR = FILE_DIR.parents[3]

FAVORITES_FILE = PROJECT_DIR / "favorites.json"


# ============================================================
# FAVORITES SCREEN
# ============================================================

class FavoritesScreen(QWidget):

    play_requested = Signal(
        str,
        str,
        str
    )

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "🎵 LYRx - Favorites"
        )

        self.favorite_cards = []

        self.build_ui()

        self.reload_favorites()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

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
        # MAIN AREA
        # ====================================================

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

        self.main_layout = QVBoxLayout(
            self.main
        )

        self.main_layout.setContentsMargins(
            34,
            30,
            34,
            30
        )

        self.main_layout.setSpacing(
            24
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = QWidget()

        header_layout = QVBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        header_layout.setSpacing(
            6
        )

        self.title = QLabel(
            "Favorites"
        )

        self.title.setStyleSheet("""
        QLabel {

            color: white;

            font-size: 32px;

            font-weight: 800;

            background: transparent;
        }
        """)

        self.subtitle = QLabel(
            "Your favorite songs, all in one place."
        )

        self.subtitle.setStyleSheet("""
        QLabel {

            color: #AFA4C8;

            font-size: 14px;

            background: transparent;
        }
        """)

        header_layout.addWidget(
            self.title
        )

        header_layout.addWidget(
            self.subtitle
        )

        self.main_layout.addWidget(
            header
        )

        # ====================================================
        # FAVORITES COUNT
        # ====================================================

        self.count_label = QLabel(
            "0 songs"
        )

        self.count_label.setStyleSheet("""
        QLabel {

            color: #9B7AFF;

            font-size: 13px;

            font-weight: 600;

            background: transparent;
        }
        """)

        self.main_layout.addWidget(
            self.count_label
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
        """)

        self.main_layout.addWidget(
            self.scroll,
            1
        )

        # ====================================================
        # SCROLL CONTENT
        # ====================================================

        self.content = QWidget()

        self.content.setStyleSheet("""
        QWidget {
            background: transparent;
        }
        """)

        self.content_layout = QVBoxLayout(
            self.content
        )

        self.content_layout.setContentsMargins(
            0,
            0,
            10,
            30
        )

        self.content_layout.setSpacing(
            20
        )

        self.content_layout.setAlignment(
            Qt.AlignTop
        )

        self.scroll.setWidget(
            self.content
        )

        # ====================================================
        # EMPTY STATE
        # ====================================================

        self.empty_state = QFrame()

        self.empty_state.setMinimumHeight(
            260
        )

        self.empty_state.setStyleSheet("""
        QFrame {

            background: #151024;

            border: 1px solid #2D2348;

            border-radius: 22px;
        }
        """)

        empty_layout = QVBoxLayout(
            self.empty_state
        )

        empty_layout.setAlignment(
            Qt.AlignCenter
        )

        empty_icon = QLabel(
            "♡"
        )

        empty_icon.setAlignment(
            Qt.AlignCenter
        )

        empty_icon.setStyleSheet("""
        QLabel {

            color: #8B5CF6;

            font-size: 52px;

            background: transparent;
        }
        """)

        self.empty_title = QLabel(
            "No favorites yet"
        )

        self.empty_title.setAlignment(
            Qt.AlignCenter
        )

        self.empty_title.setStyleSheet("""
        QLabel {

            color: white;

            font-size: 20px;

            font-weight: 700;

            background: transparent;
        }
        """)

        empty_text = QLabel(
            "Songs you favorite will appear here."
        )

        empty_text.setAlignment(
            Qt.AlignCenter
        )

        empty_text.setStyleSheet("""
        QLabel {

            color: #8F86AA;

            font-size: 13px;

            background: transparent;
        }
        """)

        empty_layout.addWidget(
            empty_icon
        )

        empty_layout.addSpacing(
            8
        )

        empty_layout.addWidget(
            self.empty_title
        )

        empty_layout.addSpacing(
            4
        )

        empty_layout.addWidget(
            empty_text
        )

        self.content_layout.addWidget(
            self.empty_state
        )

        self.empty_state.hide()

    # ========================================================
    # READ FAVORITES
    # ========================================================

    def read_favorites(self):

        try:

            if not FAVORITES_FILE.exists():

                return []

            with open(
                FAVORITES_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, list):

                    return [
                        item
                        for item in data
                        if isinstance(item, dict)
                    ]

        except (
            json.JSONDecodeError,
            OSError,
            TypeError
        ):

            print(
                "Could not read favorites.json"
            )

        return []

    # ========================================================
    # CLEAR OLD CARDS
    # ========================================================

    def clear_cards(self):

        for card in self.favorite_cards:

            card.deleteLater()

        self.favorite_cards.clear()

    # ========================================================
    # RELOAD FAVORITES
    # ========================================================

    def reload_favorites(self):

        self.clear_cards()

        favorites = self.read_favorites()

        self.count_label.setText(
            f"{len(favorites)} "
            f"{'song' if len(favorites) == 1 else 'songs'}"
        )

        # ====================================================
        # EMPTY
        # ====================================================

        if not favorites:

            self.empty_state.show()

            return

        # ====================================================
        # SONGS EXIST
        # ====================================================

        self.empty_state.hide()

        for item in favorites:

            image_path = item.get(
                "image_path",
                ""
            )

            title = item.get(
                "title",
                "Unknown Song"
            )

            artist = item.get(
                "artist",
                "Unknown Artist"
            )

            if not image_path:

                continue

            card = MusicCard(
                image_path,
                title,
                artist
            )

            card.setSizePolicy(
                QSizePolicy.Fixed,
                QSizePolicy.Fixed
            )

            card.play_requested.connect(
                self.handle_play_request
            )

            card.favorite_changed.connect(
                self.handle_favorite_changed
            )

            self.content_layout.addWidget(
                card,
                alignment=Qt.AlignLeft
            )

            self.favorite_cards.append(
                card
            )

    # ========================================================
    # PLAY FAVORITE
    # ========================================================

    def handle_play_request(
        self,
        image_path,
        title,
        artist
    ):

        self.play_requested.emit(
            image_path,
            title,
            artist
        )

    # ========================================================
    # FAVORITE CHANGED
    # ========================================================

    def handle_favorite_changed(
        self,
        image_path,
        title,
        is_favorite
    ):

        # If user removed the song
        # while inside Favorites,
        # refresh the screen.

        if not is_favorite:

            self.reload_favorites()

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

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                124,
                58,
                237,
                24
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