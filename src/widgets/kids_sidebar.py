from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from core.paths import asset_path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)


class KidsNavButton(QPushButton):
    requested = Signal(str)

    def __init__(self, route, label, emoji, parent=None):
        super().__init__(parent)
        self.route = route
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(52)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 0, 12, 0)
        row.setSpacing(12)

        icon = QLabel(emoji)
        icon.setObjectName("KidsNavIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedWidth(30)

        text = QLabel(label)
        text.setObjectName("KidsNavText")

        row.addWidget(icon)
        row.addWidget(text, 1)
        self.clicked.connect(lambda: self.requested.emit(self.route))


class KidsSidebar(QWidget):
    page_requested = Signal(str)
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("KidsSidebar")
        self.setFixedWidth(240)
        self.buttons = []
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 18, 16, 18)
        root.setSpacing(7)

        self.brand = QLabel()
        self.brand.setObjectName("KidsBrandImage")
        self.brand.setAlignment(Qt.AlignCenter)
        logo = QPixmap(str(asset_path("icons", "logo", "LYRx_wordmark.png")))
        if not logo.isNull():
            self.brand.setPixmap(
                logo.scaled(126, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.brand.setText("LYRx")
        self.brand.setFixedHeight(62)
        root.addWidget(self.brand)

        badge = QLabel("⭐  KIDS MODE  ⭐")
        badge.setObjectName("KidsModeBadge")
        badge.setAlignment(Qt.AlignCenter)
        root.addWidget(badge)

        tagline = QLabel("Safe • Fun • Learn • Grow")
        tagline.setObjectName("KidsTagline")
        tagline.setAlignment(Qt.AlignCenter)
        root.addWidget(tagline)
        root.addSpacing(14)

        menu = QLabel("KIDS SPACE")
        menu.setObjectName("KidsMenuLabel")
        root.addWidget(menu)

        items = [
            ("Kids Home", "Home", "🏠"),
            ("Kids Music", "Kids Music", "🎵"),
            ("Stories", "Stories", "📚"),
            ("Poems & Rhymes", "Poems & Rhymes", "🎶"),
            ("Spiritual", "Spiritual", "🪷"),
            ("Study & Learn", "Study & Learn", "🎓"),
            ("Kids Favorites", "Favorites", "💜"),
            ("Kids Settings", "Kids Settings", "⚙️"),
        ]

        for route, label, emoji in items:
            button = KidsNavButton(route, label, emoji, self)
            button.requested.connect(self._on_page_requested)
            root.addWidget(button)
            self.buttons.append(button)

        self.buttons[0].setChecked(True)
        root.addStretch(1)

        safety = QFrame()
        safety.setObjectName("KidsSafetyCard")
        safety_layout = QVBoxLayout(safety)
        safety_layout.setContentsMargins(12, 10, 12, 10)
        safety_layout.setSpacing(3)
        title = QLabel("🛡️  Kids Privacy")
        title.setObjectName("KidsSafetyTitle")
        text = QLabel("Safe Search • content filters\nParent Exit PIN • persistent settings")
        text.setObjectName("KidsSafetyText")
        safety_layout.addWidget(title)
        safety_layout.addWidget(text)
        root.addWidget(safety)

        exit_button = QPushButton("←  Back to LYRx")
        exit_button.setObjectName("ExitKidsButton")
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.setFixedHeight(44)
        exit_button.clicked.connect(self.exit_requested.emit)
        root.addWidget(exit_button)

    def _on_page_requested(self, route):
        for button in self.buttons:
            button.setChecked(button.route == route)
        self.page_requested.emit(route)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#KidsSidebar {
                background:#0B0824;
                border-right:1px solid rgba(115,103,255,70);
            }
            QLabel#KidsBrandImage { background:transparent; }
            QLabel#KidsModeBadge {
                color:#FFD75A;font-size:12px;font-weight:900;background:transparent;
            }
            QLabel#KidsTagline {
                color:#8DE8FF;font-size:10px;font-weight:650;background:transparent;
            }
            QLabel#KidsMenuLabel {
                color:#7771B4;font-size:9px;font-weight:900;
                padding:8px 0 3px 9px;background:transparent;
            }
            QPushButton {
                border:none;border-radius:14px;background:transparent;
            }
            QPushButton:hover { background:rgba(112,82,235,28); }
            QPushButton:checked {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #6654F5,stop:1 #C33BFA);
            }
            QLabel#KidsNavIcon {
                color:white;background:transparent;font-size:20px;
            }
            QLabel#KidsNavText {
                color:#E9E7FF;background:transparent;font-size:14px;font-weight:850;
            }
            QPushButton:checked QLabel#KidsNavText { color:white; }
            QFrame#KidsSafetyCard {
                background:rgba(43,214,170,18);
                border:1px solid rgba(43,214,170,75);border-radius:14px;
            }
            QLabel#KidsSafetyTitle {
                color:#72F1CF;font-size:12px;font-weight:850;background:transparent;
            }
            QLabel#KidsSafetyText {
                color:#9B96C9;font-size:9px;background:transparent;
            }
            QPushButton#ExitKidsButton {
                color:white;background:rgba(255,255,255,12);
                border:1px solid rgba(255,255,255,25);
                font-size:11px;font-weight:800;
            }
            QPushButton#ExitKidsButton:hover {
                background:rgba(255,255,255,23);border-color:#6554C8;
            }
        """)
