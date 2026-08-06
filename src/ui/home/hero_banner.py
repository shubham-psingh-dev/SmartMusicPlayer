from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)


BASE_DIR = Path(__file__).resolve().parents[3]

HEADPHONE_PATH = (
    BASE_DIR
    / "assets"
    / "images"
    / "hero"
    / "headphones.png"
)


class HeroBanner(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(280)
        self.setMaximumHeight(300)

        self.build_ui()

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(35, 28, 35, 28)

        root.setSpacing(30)

        # ============================
        # LEFT
        # ============================

        left = QVBoxLayout()

        left.setSpacing(8)

        greeting = QLabel("Good Evening 👋")

        greeting.setStyleSheet("""
        color:#C7BDF7;
        font-size:14px;
        """)

        title = QLabel(
            "What do you want\n"
            "to hear today?"
        )

        title.setWordWrap(True)

        title.setFont(
            QFont(
                "Segoe UI",
                26,
                QFont.Bold
            )
        )

        title.setStyleSheet("""
        color:white;
        """)

        subtitle = QLabel(
            "Discover millions of songs\n"
            "crafted for your mood."
        )

        subtitle.setStyleSheet("""
        color:#C6C1E4;
        font-size:15px;
        line-height:22px;
        """)

        left.addWidget(greeting)
        left.addWidget(title)
        left.addSpacing(8)
        left.addWidget(subtitle)
        left.addStretch()

        root.addLayout(left, 2)

        # ============================
        # RIGHT
        # ============================

        right = QVBoxLayout()

        right.setAlignment(Qt.AlignCenter)

        self.image = QLabel()

        self.image.setAlignment(Qt.AlignCenter)

        if HEADPHONE_PATH.exists():

            pix = QPixmap(str(HEADPHONE_PATH))

            self.image.setPixmap(
                pix.scaled(
                    260,
                    260,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        self.image.setStyleSheet("""
        QLabel{

            background:transparent;

            padding:10px;

        }
        """)

        right.addStretch()
        right.addWidget(self.image, alignment=Qt.AlignCenter)
        right.addStretch()

        root.addLayout(right, 1)

    # =====================================
    # PAINT BACKGROUND
    # =====================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        # Rounded Shape
        path = QPainterPath()

        path.addRoundedRect(
            rect.adjusted(1, 1, -1, -1),
            26,
            26
        )

        # Background Gradient
        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#1A1430")
        )

        gradient.setColorAt(
            0.45,
            QColor("#2A1E4B")
        )

        gradient.setColorAt(
            1.0,
            QColor("#4C1D95")
        )

        painter.fillPath(
            path,
            gradient
        )

        # Border
        pen = QPen(
            QColor(124, 58, 237, 120)
        )

        pen.setWidth(2)

        painter.setPen(pen)

        painter.drawPath(path)

        # =============================
        # PURPLE GLOW
        # =============================

        painter.setPen(Qt.NoPen)

        glow = QColor(139, 92, 246, 45)

        painter.setBrush(glow)

        painter.drawEllipse(
            rect.width() - 320,
            25,
            260,
            260
        )

        painter.setBrush(
            QColor(168, 85, 247, 30)
        )

        painter.drawEllipse(
            rect.width() - 250,
            60,
            170,
            170
        )

        painter.setBrush(
            QColor(124, 58, 237, 20)
        )

        painter.drawEllipse(
            rect.width() - 420,
            120,
            120,
            120
        )

        # =============================
        # MUSIC NOTES
        # =============================

        painter.setPen(
            QColor(190, 160, 255, 120)
        )

        font = QFont()

        font.setPointSize(18)

        painter.setFont(font)

        painter.drawText(
            rect.width() - 250,
            55,
            "♪"
        )

        painter.drawText(
            rect.width() - 170,
            90,
            "♫"
        )

        painter.drawText(
            rect.width() - 310,
            135,
            "♬"
        )

        painter.drawText(
            rect.width() - 120,
            165,
            "♪"
        )

        painter.end()