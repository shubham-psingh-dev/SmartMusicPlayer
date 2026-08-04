from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFrame,
)


class HomeScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(1200, 700)

        self.build_ui()

    def build_ui(self):

        # ==========================
        # Main Layout
        # ==========================

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(40, 25, 40, 30)

        self.main_layout.setSpacing(25)

        # ==========================
        # Welcome Section
        # ==========================

        welcome_layout = QVBoxLayout()

        title = QLabel("Good Evening 👋")

        title.setStyleSheet("""

        QLabel{

            color:white;

            font-size:32px;

            font-weight:700;

        }

        """)

        subtitle = QLabel("Lose Yourself in Sound")

        subtitle.setStyleSheet("""

        QLabel{

            color:#B8B8C8;

            font-size:15px;

        }

        """)

        welcome_layout.addWidget(title)

        welcome_layout.addWidget(subtitle)

        self.main_layout.addLayout(welcome_layout)

        # ==========================
        # Search Box
        # ==========================

        self.search = QLineEdit()

        self.search.setPlaceholderText("Search Songs, Albums, Artists...")

        self.search.setFixedHeight(42)

        self.search.setStyleSheet("""

        QLineEdit{

            background:#231A42;

            color:white;

            border:none;

            border-radius:20px;

            padding-left:18px;

            font-size:14px;

        }

        QLineEdit:focus{

            border:2px solid #7A5AF8;

        }

        """)

        self.main_layout.addWidget(self.search)

        # ==========================
        # Placeholder Card
        # ==========================

        card = QFrame()

        card.setMinimumHeight(260)

        card.setStyleSheet("""

        QFrame{

            background:#241B45;

            border-radius:18px;

        }

        """)

        card_layout = QVBoxLayout(card)

        heading = QLabel("🎵 Continue Listening")

        heading.setStyleSheet("""

        QLabel{

            color:white;

            font-size:22px;

            font-weight:600;

        }

        """)

        info = QLabel("Music cards will be added in the next task.")

        info.setStyleSheet("""

        QLabel{

            color:#A9A9C4;

            font-size:14px;

        }

        """)

        card_layout.addWidget(heading)

        card_layout.addWidget(info)

        card_layout.addStretch()

        self.main_layout.addWidget(card)

        self.main_layout.addStretch()

    # ==========================================
    # Background Gradient
    # ==========================================

    def paintEvent(self, event):

        painter = QPainter(self)

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(0.0, QColor("#171129"))
        gradient.setColorAt(0.5, QColor("#21163F"))
        gradient.setColorAt(1.0, QColor("#0B0915"))

        painter.fillRect(self.rect(), gradient)