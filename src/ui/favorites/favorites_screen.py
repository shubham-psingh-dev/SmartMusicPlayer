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

        self.current_is_dark = True

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
            18
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

            border: none;
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

            border: none;
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

            border: none;
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

        self.empty_state.setObjectName(
            "EmptyState"
        )

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

            font-family: "Segoe UI Symbol";

            font-size: 52px;

            background: transparent;

            border: none;
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

            border: none;
        }
        """)

        self.empty_text = QLabel(
            "Songs you favorite will appear here."
        )

        self.empty_text.setAlignment(
            Qt.AlignCenter
        )

        self.empty_text.setStyleSheet("""
        QLabel {

            color: #8F86AA;

            font-size: 13px;

            background: transparent;

            border: none;
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
            self.empty_text
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

        if not is_favorite:

            self.reload_favorites()

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

            title_color = "#FFFFFF"
            subtitle_color = "#AFA4C8"
            count_color = "#9B7AFF"

            empty_bg = "#151024"
            empty_border = "#2D2348"

            empty_title_color = "#FFFFFF"
            empty_text_color = "#8F86AA"

        else:

            title_color = "#302744"
            subtitle_color = "#766783"
            count_color = "#7C3AED"

            empty_bg = "#F4EEF8"
            empty_border = "#DCCEF0"

            empty_title_color = "#302744"
            empty_text_color = "#81728F"

        self.title.setStyleSheet(
            f"""
            QLabel {{

                color: {title_color};

                font-size: 32px;

                font-weight: 800;

                background: transparent;

                border: none;
            }}
            """
        )

        self.subtitle.setStyleSheet(
            f"""
            QLabel {{

                color: {subtitle_color};

                font-size: 14px;

                background: transparent;

                border: none;
            }}
            """
        )

        self.count_label.setStyleSheet(
            f"""
            QLabel {{

                color: {count_color};

                font-size: 13px;

                font-weight: 600;

                background: transparent;

                border: none;
            }}
            """
        )

        self.empty_state.setStyleSheet(
            f"""
            QFrame#EmptyState {{

                background: {empty_bg};

                border: 1px solid {empty_border};

                border-radius: 22px;
            }}
            """
        )

        self.empty_title.setStyleSheet(
            f"""
            QLabel {{

                color: {empty_title_color};

                font-size: 20px;

                font-weight: 700;

                background: transparent;

                border: none;
            }}
            """
        )

        self.empty_text.setStyleSheet(
            f"""
            QLabel {{

                color: {empty_text_color};

                font-size: 13px;

                background: transparent;

                border: none;
            }}
            """
        )

        # Update existing cards
        for card in self.favorite_cards:

            try:

                card.set_theme_state(
                    self.current_is_dark
                )

            except Exception as error:

                print(
                    "Favorite card theme error:",
                    error
                )

        self.update()

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

        # ====================================================
        # BACKGROUND
        # ====================================================

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        if self.current_is_dark:

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

        else:

            gradient.setColorAt(
                0.0,
                QColor("#F7F4FB")
            )

            gradient.setColorAt(
                0.45,
                QColor("#F0EAF7")
            )

            gradient.setColorAt(
                1.0,
                QColor("#E9E1F1")
            )

        painter.fillRect(
            rect,
            gradient
        )

        # ====================================================
        # TOP PURPLE GLOW
        # ====================================================

        painter.setPen(
            Qt.NoPen
        )

        if self.current_is_dark:

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    24
                )
            )

        else:

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    14
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

        if self.current_is_dark:

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    16
                )
            )

        else:

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    10
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