from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)

from widgets.sidebar import Sidebar


class BasicPage(QWidget):
    """Lightweight Day-14 page used until the full feature UI is built."""

    def __init__(self, title, subtitle, icon="✦"):
        super().__init__()

        self.page_title = title

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Keep the existing Sidebar component so every page can navigate.
        self.sidebar = Sidebar()
        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding,
        )
        root.addWidget(self.sidebar)

        self.main = QWidget()
        self.main.setAttribute(Qt.WA_TranslucentBackground)
        self.main.setStyleSheet("QWidget { background: transparent; }")
        root.addWidget(self.main, 1)

        layout = QVBoxLayout(self.main)
        layout.setContentsMargins(42, 38, 42, 38)
        layout.setSpacing(0)

        # Header
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            QLabel {
                color: #A970FF;
                font-size: 30px;
                background: transparent;
            }
        """)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: 800;
                background: transparent;
            }
        """)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #AFA4C8;
                font-size: 14px;
                background: transparent;
            }
        """)

        layout.addWidget(icon_label)
        layout.addSpacing(8)
        layout.addWidget(title_label)
        layout.addSpacing(6)
        layout.addWidget(subtitle_label)
        layout.addSpacing(28)

        # Temporary feature card
        card = QFrame()
        card.setMinimumHeight(210)
        card.setStyleSheet("""
            QFrame {
                background: #151024;
                border: 1px solid #2D2348;
                border-radius: 22px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 26, 28, 26)
        card_layout.setAlignment(Qt.AlignCenter)

        card_icon = QLabel(icon)
        card_icon.setAlignment(Qt.AlignCenter)
        card_icon.setStyleSheet("""
            QLabel {
                color: #8B5CF6;
                font-size: 42px;
                background: transparent;
            }
        """)

        card_title = QLabel(f"{title} is ready for Day 14")
        card_title.setAlignment(Qt.AlignCenter)
        card_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 19px;
                font-weight: 700;
                background: transparent;
            }
        """)

        card_text = QLabel(
            "Navigation is connected. The full feature UI will be built next."
        )
        card_text.setAlignment(Qt.AlignCenter)
        card_text.setStyleSheet("""
            QLabel {
                color: #8F86AA;
                font-size: 13px;
                background: transparent;
            }
        """)

        card_layout.addWidget(card_icon)
        card_layout.addSpacing(10)
        card_layout.addWidget(card_title)
        card_layout.addSpacing(6)
        card_layout.addWidget(card_text)

        layout.addWidget(card)
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height(),
        )

        gradient.setColorAt(0.0, QColor("#0B0913"))
        gradient.setColorAt(0.45, QColor("#151124"))
        gradient.setColorAt(1.0, QColor("#09070F"))

        painter.fillRect(rect, gradient)

        painter.setPen(Qt.NoPen)

        painter.setBrush(QColor(124, 58, 237, 24))
        painter.drawEllipse(-180, -180, 500, 400)

        painter.setBrush(QColor(139, 92, 246, 16))
        painter.drawEllipse(
            rect.width() - 420,
            120,
            500,
            500,
        )

        painter.end()
