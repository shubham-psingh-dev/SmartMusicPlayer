from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class Header(QWidget):

    # ==================================
    # SIGNALS
    # ==================================

    search_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedHeight(80)

        self.build_ui()

    # ==================================
    # UI
    # ==================================

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            8,
            0
        )

        root.setSpacing(10)

        # ==================================
        # LEFT SPACE
        # ==================================

        root.addStretch()

        # ==================================
        # SEARCH BAR
        # ==================================

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search your music..."
        )

        self.search.setFixedWidth(320)

        self.search.setFixedHeight(42)

        self.search.setStyleSheet("""
        QLineEdit {

            background: #1D172F;

            color: white;

            border: 1px solid #312850;

            border-radius: 21px;

            padding-left: 18px;
            padding-right: 18px;

            font-size: 14px;

            selection-background-color: #7C3AED;
        }

        QLineEdit:hover {

            border: 1px solid #4A3970;

            background: #211A35;
        }

        QLineEdit:focus {

            border: 1px solid #7C3AED;

            background: #211A35;
        }
        """)

        root.addWidget(
            self.search
        )

        # ==================================
        # SEARCH SIGNAL
        # ==================================

        self.search.textChanged.connect(
            self.search_changed.emit
        )

        # ==================================
        # NOTIFICATION
        # ==================================

        self.notification = QPushButton("♧")

        self.notification.setFixedSize(
            42,
            42
        )

        self.notification.setCursor(
            Qt.PointingHandCursor
        )

        self.notification.setStyleSheet("""
        QPushButton {

            background: #211A35;

            color: #CFC7EA;

            border: 1px solid #312850;

            border-radius: 21px;

            font-size: 17px;

        }

        QPushButton:hover {

            background: #30204F;

            color: white;

            border: 1px solid #7C3AED;
        }

        QPushButton:pressed {

            background: #7C3AED;
        }
        """)

        root.addWidget(
            self.notification
        )

        # ==================================
        # PROFILE
        # ==================================

        self.profile = QPushButton(
            "•  Duggu"
        )

        self.profile.setFixedHeight(42)

        self.profile.setCursor(
            Qt.PointingHandCursor
        )

        self.profile.setStyleSheet("""
        QPushButton {

            background: #211A35;

            color: white;

            border: 1px solid #312850;

            border-radius: 21px;

            padding-left: 16px;
            padding-right: 16px;

            font-size: 14px;

            font-weight: 600;
        }

        QPushButton:hover {

            background: #30204F;

            border: 1px solid #7C3AED;
        }

        QPushButton:pressed {

            background: #7C3AED;
        }
        """)

        root.addWidget(
            self.profile
        )

        # ==================================
        # WINDOW BUTTONS
        # ==================================

        self.btn_minimize = QPushButton("—")
        self.btn_maximize = QPushButton("□")
        self.btn_close = QPushButton("✕")

        buttons = [
            self.btn_minimize,
            self.btn_maximize,
            self.btn_close
        ]

        for btn in buttons:

            btn.setFixedSize(
                36,
                36
            )

            btn.setCursor(
                Qt.PointingHandCursor
            )

            btn.setStyleSheet("""
            QPushButton {

                background: #211A35;

                color: #D8D2EA;

                border: 1px solid #2C2445;

                border-radius: 18px;

                font-size: 14px;

                font-weight: bold;
            }

            QPushButton:hover {

                background: #30204F;

                color: white;

                border: 1px solid #7C3AED;
            }
            """)

            root.addWidget(btn)

        # ==================================
        # CLOSE BUTTON SPECIAL STYLE
        # ==================================

        self.btn_close.setStyleSheet("""
        QPushButton {

            background: #211A35;

            color: #D8D2EA;

            border: 1px solid #2C2445;

            border-radius: 18px;

            font-size: 14px;

            font-weight: bold;
        }

        QPushButton:hover {

            background: #7F1D3A;

            color: white;

            border: 1px solid #BE123C;
        }
        """)

        # ==================================
        # WINDOW SIGNALS
        # ==================================

        self.btn_minimize.clicked.connect(
            lambda: self.window().showMinimized()
        )

        self.btn_maximize.clicked.connect(
            self.toggle_maximize
        )

        self.btn_close.clicked.connect(
            lambda: self.window().close()
        )

    # ==================================
    # MAXIMIZE / RESTORE
    # ==================================

    def toggle_maximize(self):

        window = self.window()

        if window.isMaximized():

            window.showNormal()

        else:

            window.showMaximized()