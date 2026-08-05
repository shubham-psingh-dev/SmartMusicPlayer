from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)


BASE_DIR = Path(__file__).resolve().parents[2]
LOGO_PATH = BASE_DIR / "assets" / "icons" / "logo" / "nirvana_logo.png"


class NavButton(QPushButton):

    clicked_name = Signal(str)

    def __init__(self, text: str):
        super().__init__(text)

        self.page_name = text

        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setMinimumHeight(48)

        self.setStyleSheet("""
        QPushButton{

            color:#CFCBEB;

            background:transparent;

            border:none;

            border-radius:14px;

            text-align:left;

            padding-left:18px;

            font-size:15px;

            font-weight:600;

        }

        QPushButton:hover{

            background:#2D2352;

            color:white;

        }

        QPushButton:checked{

            background:#7C3AED;

            color:white;

        }
        """)

        self.clicked.connect(
            lambda: self.clicked_name.emit(self.page_name)
        )


class Sidebar(QWidget):

    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedWidth(240)

        self.setStyleSheet("""
        QWidget{

            background:#141021;

            border-right:1px solid #2A2344;

        }
        """)

        self.buttons = []

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(18,20,18,20)

        layout.setSpacing(12)

        # ----------------------
        # Logo
        # ----------------------

        logo = QLabel()

        logo.setAlignment(Qt.AlignCenter)

        if LOGO_PATH.exists():

            pix = QPixmap(str(LOGO_PATH))

            logo.setPixmap(
                pix.scaled(
                    120,
                    120,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        title = QLabel("NirVANA")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""

        color:white;

        font-size:24px;

        font-weight:700;

        """)

        subtitle = QLabel("Lose Yourself in Sound")

        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setStyleSheet("""

        color:#A79FD2;

        font-size:12px;

        """)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # ----------------------
        # Navigation
        # ----------------------

        menu = [
            "🏠  Home",
            "🔎  Discover",
            "🎵  Library",
            "❤  Favorites",
            "📂  Playlists",
            "⚙  Settings",
        ]

        for item in menu:

            button = NavButton(item)

            button.clicked_name.connect(self.change_page)

            layout.addWidget(button)

            self.buttons.append(button)

        self.buttons[0].setChecked(True)

        layout.addStretch()

        # ----------------------
        # Footer
        # ----------------------

        version = QLabel("NirVANA v0.1")

        version.setAlignment(Qt.AlignCenter)

        version.setStyleSheet("""
        color:#7F78A8;
        font-size:11px;
        padding-top:12px;
        """)

        layout.addWidget(version)

    # ---------------------------------------
    # Navigation Logic
    # ---------------------------------------

    def change_page(self, page_name: str):

        sender = self.sender()

        for button in self.buttons:

            if button != sender:
                button.setChecked(False)

        self.page_changed.emit(page_name)

        print(f"Navigate to: {page_name}")        