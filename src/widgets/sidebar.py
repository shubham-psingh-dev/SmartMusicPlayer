from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SYMBOL_PATH = (
    BASE_DIR
    / "assets"
    / "icons"
    / "logo"
    / "LYRx_symbol.png"
)

WORDMARK_PATH = (
    BASE_DIR
    / "assets"
    / "icons"
    / "logo"
    / "LYRx_wordmark.png"
)

NAV_ICON_PATH = (
    BASE_DIR
    / "assets"
    / "icons"
    / "navigation"
)


# ============================================================
# NAV BUTTON
# ============================================================

class NavButton(QPushButton):

    clicked_name = Signal(str)

    def __init__(self, text: str, icon_name: str):
        super().__init__(text)

        self.page_name = text

        # ----------------------------------------------------
        # ICON
        # ----------------------------------------------------

        icon_file = NAV_ICON_PATH / icon_name

        if icon_file.exists():
            self.setIcon(QIcon(str(icon_file)))
            self.setIconSize(QSize(19, 19))

        # ----------------------------------------------------
        # BASIC BUTTON SETTINGS
        # ----------------------------------------------------

        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)

        self.setMinimumHeight(46)
        self.setMaximumHeight(48)

        # ----------------------------------------------------
        # BUTTON STYLE
        # ----------------------------------------------------

        self.setStyleSheet("""
        QPushButton {
            color: #BEB7D8;

            background: transparent;

            border: 1px solid transparent;
            border-radius: 13px;

            text-align: left;

            padding-left: 15px;
            padding-right: 14px;

            font-size: 16px;
            font-weight: 600;
        }

        /* ==================================================
           HOVER
        ================================================== */

        QPushButton:hover {
            color: #FFFFFF;

            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 0,

                stop: 0 #34245A,
                stop: 0.45 #432A70,
                stop: 1 #32214F
            );

            border: 1px solid rgba(168, 85, 247, 80);
        }

        /* ==================================================
           ACTIVE
        ================================================== */

        QPushButton:checked {
            color: #FFFFFF;

            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 0,

                stop: 0 #7138D8,
                stop: 0.45 #8748EA,
                stop: 1 #6935C4
            );

            border: 1px solid rgba(201, 170, 255, 110);
        }

        /* ==================================================
           ACTIVE + HOVER
        ================================================== */

        QPushButton:checked:hover {
            color: #FFFFFF;

            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 0,

                stop: 0 #8246E8,
                stop: 0.5 #9655F5,
                stop: 1 #7440D1
            );

            border: 1px solid rgba(225, 210, 255, 150);
        }

        /* ==================================================
           PRESSED
        ================================================== */

        QPushButton:pressed {
            color: #FFFFFF;

            background: #5F2DAF;

            border: 1px solid rgba(210, 190, 255, 130);
        }
        """)

        # ----------------------------------------------------
        # SIGNAL
        # ----------------------------------------------------

        self.clicked.connect(
            lambda: self.clicked_name.emit(self.page_name)
        )


# ============================================================
# SIDEBAR
# ============================================================

class Sidebar(QWidget):

    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        # ====================================================
        # OBJECT
        # ====================================================

        self.setObjectName("Sidebar")

        # ====================================================
        # SIZE
        # ====================================================

        self.setFixedWidth(240)

        # ====================================================
        # SIDEBAR BACKGROUND
        # ====================================================

        self.setStyleSheet("""
        QWidget#Sidebar {
            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 1,

                stop: 0 #171027,
                stop: 0.55 #120D20,
                stop: 1 #0F0B18
            );

            border-right: 1px solid rgba(139, 92, 246, 35);
        }
        """)

        # ====================================================
        # STATE
        # ====================================================

        self.buttons = []

        # ====================================================
        # BUILD
        # ====================================================

        self.build_ui()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            18,
            16,
            16
        )

        layout.setSpacing(0)

        # ====================================================
        # BRANDING
        # ====================================================

        symbol = QLabel()
        symbol.setAlignment(Qt.AlignCenter)
        symbol.setFixedHeight(48)

        if SYMBOL_PATH.exists():

            pix = QPixmap(str(SYMBOL_PATH))

            if not pix.isNull():

                symbol.setPixmap(
                    pix.scaled(
                        48,
                        48,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )

        symbol.setStyleSheet("""
        QLabel {
            background: transparent;
            border: none;
        }
        """)

        layout.addWidget(symbol)

        layout.addSpacing(5)

        # ====================================================
        # WORDMARK
        # ====================================================

        wordmark = QLabel()
        wordmark.setAlignment(Qt.AlignCenter)
        wordmark.setFixedHeight(34)

        if WORDMARK_PATH.exists():

            pix = QPixmap(str(WORDMARK_PATH))

            if not pix.isNull():

                wordmark.setPixmap(
                    pix.scaled(
                        118,
                        32,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )

        wordmark.setStyleSheet("""
        QLabel {
            background: transparent;
            border: none;
        }
        """)

        layout.addWidget(wordmark)

        layout.addSpacing(2)

        # ====================================================
        # SUBTITLE
        # ====================================================

        subtitle = QLabel(
            "Lose Yourself in Sound"
        )

        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setStyleSheet("""
        QLabel {
            color: #81779F;

            font-size: 10px;
            font-weight: 500;

            background: transparent;
            border: none;

            letter-spacing: 0.4px;
        }
        """)

        layout.addWidget(subtitle)

        layout.addSpacing(25)

        # ====================================================
        # MENU LABEL
        # ====================================================

        menu_header = QLabel("MENU")

        menu_header.setStyleSheet("""
        QLabel {
            color: #6F658C;

            font-size: 10px;
            font-weight: 700;

            letter-spacing: 1.6px;

            padding-left: 14px;
            padding-bottom: 8px;

            background: transparent;
            border: none;
        }
        """)

        layout.addWidget(menu_header)

        # ====================================================
        # NAVIGATION MENU
        # ====================================================

        menu = [
            ("Home", "home.svg"),
            ("Discover", "discover.svg"),
            ("Library", "library.svg"),
            ("Favorites", "favorites.svg"),
            ("Playlists", "playlist.svg"),
            ("AI Assistant", "sparkles.svg"),
            ("Settings", "settings.svg"),
        ]

        for text, icon in menu:

            button = NavButton(
                text,
                icon
            )

            button.clicked_name.connect(
                self.change_page
            )

            layout.addWidget(button)

            self.buttons.append(button)

            # Small separation before Settings
            if text == "AI Assistant":
                layout.addSpacing(4)

        # ====================================================
        # DEFAULT ACTIVE PAGE
        # ====================================================

        if self.buttons:
            self.buttons[0].setChecked(True)

        # ====================================================
        # FLEXIBLE SPACE
        # ====================================================

        layout.addStretch(1)

        # ====================================================
        # FOOTER DIVIDER
        # ====================================================

        divider = QWidget()
        divider.setFixedHeight(1)

        divider.setStyleSheet("""
        QWidget {
            background: rgba(255, 255, 255, 12);
        }
        """)

        layout.addWidget(divider)

        layout.addSpacing(10)

        # ====================================================
        # VERSION
        # ====================================================

        version = QLabel(
            "LYRx  •  v0.1"
        )

        version.setAlignment(Qt.AlignCenter)

        version.setStyleSheet("""
        QLabel {
            color: #625A79;

            font-size: 10px;
            font-weight: 500;

            background: transparent;
            border: none;
        }
        """)

        layout.addWidget(version)

    # ========================================================
    # NAVIGATION LOGIC
    # ========================================================

    def change_page(self, page_name: str):

        sender = self.sender()

        # ----------------------------------------------------
        # Update active button
        # ----------------------------------------------------

        for button in self.buttons:

            if button != sender:
                button.setChecked(False)

        # ----------------------------------------------------
        # Notify AppWindow / parent
        # ----------------------------------------------------

        self.page_changed.emit(page_name)

        # ----------------------------------------------------
        # Debug
        # ----------------------------------------------------

        print(
            f"Navigate to: {page_name}"
        )