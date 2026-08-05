from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
)

from widgets.sidebar import Sidebar
from ui.home.hero_banner import HeroBanner
from widgets.cards.music_card import MusicCard
from ui.home.header import Header


class HomeScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("🎵 NirVANA")

        self.resize(1400, 850)

        self.setMinimumSize(1200, 700)

        self.build_ui()

    def build_ui(self):

        # ===============================
        # ROOT LAYOUT
        # ===============================

        root = QHBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(0)

        # ===============================
        # SIDEBAR
        # ===============================

        self.sidebar = Sidebar()

        root.addWidget(self.sidebar)

        # ===============================
        # CONTENT AREA
        # ===============================

        self.content = QWidget()

        self.content_layout = QVBoxLayout(self.content)

        self.content_layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        self.content_layout.setSpacing(25)

        root.addWidget(
            self.content,
            1
        )

        # ===============================
        # HEADER
        # ===============================

        self.header = Header()

        self.content_layout.addWidget(self.header)

        # ===============================
        # HERO
        # ===============================

        self.hero = HeroBanner()

        self.content_layout.addWidget(self.hero)

        # ===============================
        # SECTION TITLE
        # ===============================

        from PySide6.QtWidgets import QLabel

        title = QLabel(
            "Continue Listening"
        )

        title.setStyleSheet("""

        color:white;

        font-size:26px;

        font-weight:700;

        """)

        self.content_layout.addWidget(title)

        # ===============================
        # MUSIC CARDS
        # ===============================

        cards_container = QFrame()

        cards_container.setStyleSheet("""
        QFrame{
            background:transparent;
        }
        """)

        cards_layout = QHBoxLayout(cards_container)

        cards_layout.setContentsMargins(0, 0, 0, 0)

        cards_layout.setSpacing(20)

        # -------------------------------
        # Card 1
        # -------------------------------

        card1 = MusicCard(
            "assets/album_art/believer.jpg",
            "Believer",
            "Imagine Dragons"
        )

        # -------------------------------
        # Card 2
        # -------------------------------

        card2 = MusicCard(
            "assets/album_art/faded.jpg",
            "Faded",
            "Alan Walker"
        )

        # -------------------------------
        # Card 3
        # -------------------------------

        card3 = MusicCard(
            "assets/album_art/arcade.jpg",
            "Arcade",
            "Duncan Laurence"
        )

        # -------------------------------
        # Card 4
        # -------------------------------

        card4 = MusicCard(
            "assets/album_art/lethergo.jpg",
            "Let Her Go",
            "Passenger"
        )

        cards_layout.addWidget(card1)
        cards_layout.addWidget(card2)
        cards_layout.addWidget(card3)
        cards_layout.addWidget(card4)

        cards_layout.addStretch()

        self.content_layout.addWidget(cards_container)

        # ===============================
        # FUTURE PLACEHOLDERS
        # ===============================

        # Day 7
        # Mood Section

        # Day 8
        # Recently Played

        # Day 9
        # Right Playing Panel

        self.content_layout.addStretch()

    # =====================================
    # PREMIUM BACKGROUND
    # =====================================

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
            QColor("#0B0913")
        )

        painter.fillRect(
            self.rect(),
            gradient
        )

        super().paintEvent(event)