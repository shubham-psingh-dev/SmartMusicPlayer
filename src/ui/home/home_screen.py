from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
)

from widgets.cards.music_card import MusicCard


class HomeScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("🎵 NirVANA")
        self.resize(1400, 850)
        self.setMinimumSize(1200, 700)

        self.build_ui()

    def build_ui(self):

        # -----------------------------
        # Main Layout
        # -----------------------------

        self.main_layout = QVBoxLayout()

        self.main_layout.setContentsMargins(40, 30, 40, 30)

        self.main_layout.setSpacing(20)

        self.setLayout(self.main_layout)

        # -----------------------------
        # Welcome
        # -----------------------------

        title = QLabel("Good Evening 👋")

        title.setStyleSheet("""
            color:white;
            font-size:28px;
            font-weight:bold;
            background:transparent;
        """)

        subtitle = QLabel("Lose Yourself in Sound")

        subtitle.setStyleSheet("""
            color:#B9B2D8;
            font-size:14px;
            background:transparent;
        """)

        self.main_layout.addWidget(title)

        self.main_layout.addWidget(subtitle)

        # -----------------------------
        # Search Bar
        # -----------------------------

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search Songs, Albums, Artists..."
        )

        self.search.setFixedHeight(45)

        self.search.setStyleSheet("""
        QLineEdit{

            background:#2A1E4D;

            border:2px solid #7C3AED;

            border-radius:22px;

            padding-left:20px;

            color:white;

            font-size:14px;

        }
        """)

        self.main_layout.addWidget(self.search)

        # -----------------------------
        # Continue Listening
        # -----------------------------

        heading = QLabel("🎵 Continue Listening")

        heading.setStyleSheet("""
            color:white;
            font-size:24px;
            font-weight:bold;
            background:transparent;
        """)

        self.main_layout.addWidget(heading)

        # -----------------------------
        # Cards Layout
        # -----------------------------

        cards_layout = QHBoxLayout()

        cards_layout.setSpacing(20)

        card1 = MusicCard(
            "assets/album_art/believer.jpg",
            "Believer",
            "Imagine Dragons"
        )

        card2 = MusicCard(
            "assets/album_art/faded.jpg",
            "Faded",
            "Alan Walker"
        )

        card3 = MusicCard(
            "assets/album_art/arcade.jpg",
            "Arcade",
            "Duncan Laurence"
        )

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

        self.main_layout.addLayout(cards_layout)

        self.main_layout.addStretch()

    def paintEvent(self, event):

        painter = QPainter(self)

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(0.0, QColor("#1B1433"))
        gradient.setColorAt(0.5, QColor("#24153F"))
        gradient.setColorAt(1.0, QColor("#0D0B16"))

        painter.fillRect(
            self.rect(),
            gradient
        )