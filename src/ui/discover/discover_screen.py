from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtGui import QLinearGradient
from PySide6.QtGui import QPainter
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
    TRENDING_SONGS,
    MOODS,
    GENRES,
)


class DiscoverScreen(QWidget):

    # ==================================================
    # SIGNALS
    # ==================================================

    song_requested = Signal(str, str, str)

    # ==================================================
    # INIT
    # ==================================================

    def __init__(self):

        super().__init__()

        self.music_cards = []

        self.build_ui()

    # ==================================================
    # BUILD UI
    # ==================================================

    def build_ui(self):

        # ==================================================
        # ROOT
        # ==================================================

        root = QHBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root.setSpacing(0)

        # ==================================================
        # SIDEBAR
        # ==================================================

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding,
        )

        root.addWidget(
            self.sidebar
        )

        # ==================================================
        # MAIN AREA
        # ==================================================

        self.main = QWidget()

        self.main.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.main.setStyleSheet(
            "QWidget { background: transparent; }"
        )

        root.addWidget(
            self.main,
            1,
        )

        # ==================================================
        # SCROLL AREA
        # ==================================================

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

        # ==================================================
        # MAIN LAYOUT
        # ==================================================

        main_layout = QVBoxLayout(
            self.main
        )

        main_layout.setContentsMargins(
            30,
            26,
            22,
            26,
        )

        main_layout.setSpacing(0)

        main_layout.addWidget(
            self.scroll
        )

        # ==================================================
        # CONTENT
        # ==================================================

        self.content = QWidget()

        self.content.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.content.setStyleSheet(
            "QWidget { background: transparent; }"
        )

        self.scroll.setWidget(
            self.content
        )

        self.content_layout = QVBoxLayout(
            self.content
        )

        # IMPORTANT:
        #
        # Bottom margin increased so the floating player
        # never hides the last part of Discover content.
        #
        self.content_layout.setContentsMargins(
            0,
            0,
            8,
            150,
        )

        self.content_layout.setSpacing(
            24
        )

        self.content_layout.setAlignment(
            Qt.AlignTop
        )

        # ==================================================
        # HEADER
        # ==================================================

        title = QLabel(
            "Discover"
        )

        title.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 34px;
                font-weight: 800;
                background: transparent;
            }
            """
        )

        subtitle = QLabel(
            "Explore new sounds, moods and music."
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                color: #AFA4C8;
                font-size: 14px;
                background: transparent;
            }
            """
        )

        self.content_layout.addWidget(
            title
        )

        self.content_layout.addWidget(
            subtitle
        )

        # ==================================================
        # FEATURE BANNER
        # ==================================================

        banner = QFrame()

        banner.setMinimumHeight(
            170
        )

        banner.setStyleSheet(
            """
            QFrame {
                background: #18122A;
                border: 1px solid #30224B;
                border-radius: 24px;
            }

            QFrame:hover {
                border: 1px solid #53358A;
            }
            """
        )

        banner_layout = QHBoxLayout(
            banner
        )

        banner_layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        # --------------------------------------------------
        # BANNER TEXT
        # --------------------------------------------------

        banner_text = QVBoxLayout()

        banner_title = QLabel(
            "Find Your Next Favorite"
        )

        banner_title.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 25px;
                font-weight: 800;
                background: transparent;
            }
            """
        )

        banner_subtitle = QLabel(
            "Discover music made for every mood and moment."
        )

        banner_subtitle.setStyleSheet(
            """
            QLabel {
                color: #AAA0C5;
                font-size: 14px;
                background: transparent;
            }
            """
        )

        banner_text.addWidget(
            banner_title
        )

        banner_text.addSpacing(
            8
        )

        banner_text.addWidget(
            banner_subtitle
        )

        banner_text.addStretch()

        banner_layout.addLayout(
            banner_text
        )

        banner_layout.addStretch()

        # --------------------------------------------------
        # BANNER ICON
        # --------------------------------------------------

        banner_icon = QLabel(
            "♫"
        )

        banner_icon.setAlignment(
            Qt.AlignCenter
        )

        banner_icon.setStyleSheet(
            """
            QLabel {
                color: #A970FF;
                font-size: 72px;
                font-weight: 800;
                background: transparent;
            }
            """
        )

        banner_layout.addWidget(
            banner_icon
        )

        self.content_layout.addWidget(
            banner
        )

        # ==================================================
        # TRENDING SECTION
        # ==================================================

        trending_header = self.create_section_header(
            "Trending Now",
            "See All  ›",
        )

        self.content_layout.addWidget(
            trending_header
        )

        # ==================================================
        # TRENDING CARDS
        # ==================================================

        trending_container = QWidget()

        trending_layout = QHBoxLayout(
            trending_container
        )

        trending_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        trending_layout.setSpacing(
            16
        )

        # --------------------------------------------------
        # DATA
        # --------------------------------------------------

        for song in TRENDING_SONGS:

            image_path = song["image"]
            song_title = song["title"]
            artist = song["artist"]

            card = MusicCard(
                image_path,
                song_title,
                artist,
            )

            card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )

            card.play_requested.connect(
                self.handle_song_request
            )

            trending_layout.addWidget(
                card
            )

            self.music_cards.append(
                card
            )

        self.content_layout.addWidget(
            trending_container
        )

        # ==================================================
        # MOOD SECTION
        # ==================================================

        mood_header = self.create_section_header(
            "Browse by Mood",
            "View All  ›",
        )

        self.content_layout.addWidget(
            mood_header
        )

        # ==================================================
        # MOOD CARDS
        # ==================================================

        mood_container = QWidget()

        mood_layout = QHBoxLayout(
            mood_container
        )

        mood_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        mood_layout.setSpacing(
            14
        )

        # --------------------------------------------------
        # DATA
        # --------------------------------------------------

        for mood in MOODS:

            mood_name = mood["name"]
            mood_icon = mood["icon"]

            mood_card = QFrame()

            mood_card.setMinimumHeight(
                105
            )

            mood_card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )

            mood_card.setStyleSheet(
                """
                QFrame {
                    background: #181329;
                    border: 1px solid #30224B;
                    border-radius: 18px;
                }

                QFrame:hover {
                    background: #24183D;
                    border: 1px solid #7048C7;
                }
                """
            )

            mood_inner = QVBoxLayout(
                mood_card
            )

            mood_inner.setContentsMargins(
                12,
                12,
                12,
                12,
            )

            mood_inner.setAlignment(
                Qt.AlignCenter
            )

            # --------------------------------------------------
            # ICON
            # --------------------------------------------------

            icon = QLabel(
                mood_icon
            )

            icon.setAlignment(
                Qt.AlignCenter
            )

            icon.setStyleSheet(
                """
                QLabel {
                    color: white;
                    font-size: 25px;
                    background: transparent;
                }
                """
            )

            # --------------------------------------------------
            # NAME
            # --------------------------------------------------

            name = QLabel(
                mood_name
            )

            name.setAlignment(
                Qt.AlignCenter
            )

            name.setStyleSheet(
                """
                QLabel {
                    color: #D9D3EA;
                    font-size: 13px;
                    font-weight: 600;
                    background: transparent;
                }
                """
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

        self.content_layout.addWidget(
            mood_container
        )

        # ==================================================
        # GENRES SECTION
        # ==================================================

        genre_header = self.create_section_header(
            "Explore Genres",
            "View All  ›",
        )

        self.content_layout.addWidget(
            genre_header
        )

        # ==================================================
        # GENRE CARDS
        # ==================================================

        genre_container = QWidget()

        genre_layout = QHBoxLayout(
            genre_container
        )

        genre_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        genre_layout.setSpacing(
            14
        )

        # --------------------------------------------------
        # DATA
        # --------------------------------------------------

        for genre in GENRES:

            genre_name = genre["name"]
            background = genre["background"]

            genre_card = QFrame()

            genre_card.setMinimumHeight(
                90
            )

            genre_card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )

            genre_card.setStyleSheet(
                f"""
                QFrame {{
                    background: {background};
                    border-radius: 18px;
                    border: 1px solid rgba(255,255,255,20);
                }}

                QFrame:hover {{
                    border: 1px solid #A970FF;
                }}
                """
            )

            genre_layout_inner = QVBoxLayout(
                genre_card
            )

            genre_layout_inner.setAlignment(
                Qt.AlignCenter
            )

            genre_label = QLabel(
                genre_name
            )

            genre_label.setAlignment(
                Qt.AlignCenter
            )

            genre_label.setStyleSheet(
                """
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            genre_layout_inner.addWidget(
                genre_label
            )

            genre_layout.addWidget(
                genre_card
            )

        self.content_layout.addWidget(
            genre_container
        )

        # ==================================================
        # BOTTOM MESSAGE
        # ==================================================

        bottom_text = QLabel(
            "More discoveries are coming soon ✦"
        )

        bottom_text.setAlignment(
            Qt.AlignCenter
        )

        bottom_text.setStyleSheet(
            """
            QLabel {
                color: #716889;
                font-size: 12px;
                padding: 20px;
                background: transparent;
            }
            """
        )

        self.content_layout.addWidget(
            bottom_text
        )

        # ==================================================
        # EXTRA BOTTOM SPACE
        # ==================================================
        #
        # This is intentionally large enough for the
        # floating player.
        #

        self.content_layout.addSpacing(
            120
        )

    # ==================================================
    # SECTION HEADER
    # ==================================================

    def create_section_header(
        self,
        title_text,
        action_text,
    ):

        header = QWidget()

        layout = QHBoxLayout(
            header
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            0
        )

        title = QLabel(
            title_text
        )

        title.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 23px;
                font-weight: 700;
                background: transparent;
            }
            """
        )

        action = QLabel(
            action_text
        )

        action.setAlignment(
            Qt.AlignRight |
            Qt.AlignVCenter
        )

        action.setStyleSheet(
            """
            QLabel {
                color: #9B7AFF;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
            }
            """
        )

        layout.addWidget(
            title
        )

        layout.addStretch()

        layout.addWidget(
            action
        )

        return header

    # ==================================================
    # MUSIC PLAY
    # ==================================================

    def handle_song_request(
        self,
        image_path,
        title,
        artist,
    ):

        print(
            f"Discover song selected: {title} - {artist}"
        )

        self.song_requested.emit(
            image_path,
            title,
            artist,
        )

    # ==================================================
    # BACKGROUND
    # ==================================================

    def paintEvent(
        self,
        event,
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # ==================================================
        # MAIN GRADIENT
        # ==================================================

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height(),
        )

        gradient.setColorAt(
            0.0,
            QColor("#0B0913"),
        )

        gradient.setColorAt(
            0.45,
            QColor("#151124"),
        )

        gradient.setColorAt(
            1.0,
            QColor("#09070F"),
        )

        painter.fillRect(
            rect,
            gradient,
        )

        # ==================================================
        # TOP PURPLE GLOW
        # ==================================================

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                124,
                58,
                237,
                24,
            )
        )

        painter.drawEllipse(
            -180,
            -180,
            500,
            400,
        )

        # ==================================================
        # RIGHT AMBIENT GLOW
        # ==================================================

        painter.setBrush(
            QColor(
                139,
                92,
                246,
                16,
            )
        )

        painter.drawEllipse(
            rect.width() - 420,
            120,
            500,
            500,
        )

        painter.end()

        super().paintEvent(
            event
        )