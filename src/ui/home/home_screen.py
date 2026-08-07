from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QSizePolicy,
)

from widgets.sidebar import Sidebar
from ui.home.header import Header
from ui.home.hero_banner import HeroBanner
from widgets.cards.music_card import MusicCard
from ui.player.now_playing import NowPlaying


class HomeScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("🎵 LYRx")

        self.resize(1450, 900)

        self.setMinimumSize(1280, 760)

        self.build_ui()

    # ==================================================
    # BUILD UI
    # ==================================================

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(0)

        # ============================================
        # SIDEBAR
        # ============================================

        self.sidebar = Sidebar()

        root.addWidget(self.sidebar)

        # ============================================
        # MAIN CONTAINER
        # ============================================

        self.main = QWidget()

        root.addWidget(self.main, 1)

        self.main_layout = QVBoxLayout(self.main)

        self.main_layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        self.main_layout.setSpacing(24)

        # ============================================
        # HEADER
        # ============================================

        self.header = Header()

        self.main_layout.addWidget(self.header)

        # ============================================
        # HERO
        # ============================================

        self.hero = HeroBanner()

        self.hero.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.main_layout.addWidget(self.hero)

        # ============================================
        # BODY
        # ============================================

        self.body = QWidget()

        self.main_layout.addWidget(
            self.body,
            1
        )

        self.body_layout = QHBoxLayout(self.body)

        self.body_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.body_layout.setSpacing(25)

                # ============================================
        # LEFT SIDE
        # ============================================

        self.left = QWidget()

        self.left.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.body_layout.addWidget(
            self.left,
            1
        )

        self.left_layout = QVBoxLayout(self.left)

        self.left_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.left_layout.setSpacing(20)

        # ============================================
        # LEFT SCROLL AREA
        # ============================================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(True)

        self.scroll.setFrameShape(QFrame.NoFrame)

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setStyleSheet("""

        QScrollArea{

            background:transparent;

            border:none;

        }

        QScrollBar:vertical{

            width:9px;

            background:transparent;

            margin:2px;

        }

        QScrollBar::handle:vertical{

            background:#7C3AED;

            border-radius:4px;

            min-height:55px;

        }

        QScrollBar::handle:vertical:hover{

            background:#9F67FF;

        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical{

            height:0px;

        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical{

            background:transparent;

        }

        """)

        self.left_layout.addWidget(
            self.scroll
        )

        # ============================================
        # SCROLL CONTENT
        # ============================================

        self.scroll_content = QWidget()

        self.scroll.setWidget(
            self.scroll_content
        )

        self.scroll_layout = QVBoxLayout(
            self.scroll_content
        )

        self.scroll_layout.setContentsMargins(
            0,
            0,
            12,
            20
        )

        self.scroll_layout.setSpacing(26)

        self.scroll_layout.setAlignment(
            Qt.AlignTop
        )

        self.scroll_content.setStyleSheet("""
        QWidget{
            background:transparent;
        }
        """)

        # ============================================
        # RIGHT SIDE
        # ============================================

        self.right = QWidget()

        self.right.setMinimumWidth(300)
        self.right.setMaximumWidth(340)

        self.body_layout.addWidget(
            self.right
        )

        self.right_layout = QVBoxLayout(self.right)

        self.right_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.right_layout.setSpacing(18)

        self.right_layout.setAlignment(
            Qt.AlignTop
        )

                # ============================================
        # CONTINUE LISTENING
        # ============================================

        section = QLabel("Continue Listening")

        section.setStyleSheet("""
        QLabel{

            color:white;

            font-size:26px;

            font-weight:700;

        }
        """)

        self.scroll_layout.addWidget(section)

        # ============================================
        # MUSIC CARDS ROW
        # ============================================

        cards_container = QWidget()

        cards_layout = QHBoxLayout(cards_container)

        cards_layout.setContentsMargins(0, 0, 0, 0)

        cards_layout.setSpacing(20)

        self.scroll_layout.addWidget(cards_container)

        cards_container.setStyleSheet("""
        QWidget{
            background:transparent;
        }
        """)

        # ============================================
        # CARDS
        # ============================================

        cards = [

            (
                "assets/album_art/believer.jpg",
                "Believer",
                "Imagine Dragons"
            ),

            (
                "assets/album_art/faded.jpg",
                "Faded",
                "Alan Walker"
            ),

            (
                "assets/album_art/arcade.jpg",
                "Arcade",
                "Duncan Laurence"
            ),

            (
                "assets/album_art/lethergo.jpg",
                "Let Her Go",
                "Passenger"
            ),

        ]

        for image, title, artist in cards:

            card = MusicCard(
                image,
                title,
                artist
            )

            cards_layout.addWidget(card)

        cards_layout.addStretch()

        # ============================================
        # FUTURE SECTIONS
        # ============================================

        self.scroll_layout.addSpacing(15)

        placeholder = QLabel(
            "Mood • Recently Played • Playlist\n"
            "(Coming in upcoming days)"
        )

        placeholder.setAlignment(Qt.AlignCenter)

        placeholder.setStyleSheet("""
        QLabel{

            color:#8177B5;

            font-size:15px;

            padding:40px;

            border:1px dashed #43335F;

            border-radius:16px;

            background:#161122;

        }
        """)

        self.scroll_layout.addWidget(placeholder)

        self.scroll_layout.addStretch()

                # ============================================
        # NOW PLAYING PANEL
        # ============================================

        self.now_playing = NowPlaying()

        self.now_playing.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        self.right_layout.addWidget(
            self.now_playing
        )

        self.right_layout.addStretch()

        # ============================================
        # WINDOW STRETCH
        # ============================================

        self.main_layout.setStretch(
            0,
            0
        )  # Header

        self.main_layout.setStretch(
            1,
            0
        )  # Hero

        self.main_layout.setStretch(
            2,
            1
        )  # Body

            # ============================================
    # PREMIUM BACKGROUND
    # ============================================

    def paintEvent(self, event):

        painter = QPainter(self)

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#0D0B16")
        )

        gradient.setColorAt(
            0.45,
            QColor("#171428")
        )

        gradient.setColorAt(
            1.0,
            QColor("#09070F")
        )

        painter.fillRect(
            self.rect(),
            gradient
        )

        super().paintEvent(event)