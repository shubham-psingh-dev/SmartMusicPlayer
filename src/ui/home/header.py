from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class Header(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedHeight(80)

        self.build_ui()

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(15)

        # ==========================
        # LEFT SIDE
        # ==========================

        left = QVBoxLayout()

        welcome = QLabel("Good Evening 👋")

        welcome.setStyleSheet("""
        color:#B9B3D6;
        font-size:14px;
        """)

        title = QLabel("Welcome Back")

        title.setStyleSheet("""
        color:white;
        font-size:26px;
        font-weight:700;
        """)

        left.addWidget(welcome)
        left.addWidget(title)

        root.addLayout(left)

        root.addStretch()

        # ==========================
        # SEARCH BAR
        # ==========================

        self.search = QLineEdit()

        self.search.setPlaceholderText("Search music...")

        self.search.setFixedWidth(320)

        self.search.setFixedHeight(42)

        self.search.setStyleSheet("""
        QLineEdit{

            background:#221B38;

            color:white;

            border:2px solid #312850;

            border-radius:20px;

            padding-left:15px;

            font-size:14px;
        }

        QLineEdit:focus{

            border:2px solid #7C3AED;

        }
        """)

        root.addWidget(self.search)

        # ==========================
        # RIGHT SIDE
        # ==========================

        self.notification = QPushButton("🔔")

        self.notification.setFixedSize(42,42)

        self.notification.setStyleSheet("""
        QPushButton{

            background:#221B38;

            border:none;

            border-radius:21px;

            color:white;

            font-size:18px;

        }

        QPushButton:hover{

            background:#7C3AED;

        }
        """)

        root.addWidget(self.notification)

        # ==========================
        # PROFILE
        # ==========================

        self.profile = QPushButton("👤 Duggu")

        self.profile.setFixedHeight(42)

        self.profile.setStyleSheet("""
        QPushButton{

            background:#221B38;

            color:white;

            border:none;

            border-radius:20px;

            padding-left:15px;
            padding-right:15px;

            font-size:14px;

            font-weight:600;

        }

        QPushButton:hover{

            background:#7C3AED;

        }
        """)

        root.addWidget(self.profile)

        # ==========================
        # WINDOW BUTTONS
        # ==========================

        self.btn_minimize = QPushButton("—")
        self.btn_maximize = QPushButton("□")
        self.btn_close = QPushButton("✕")

        buttons = [
            self.btn_minimize,
            self.btn_maximize,
            self.btn_close
        ]

        for btn in buttons:

            btn.setFixedSize(36, 36)

            btn.setStyleSheet("""
            QPushButton{

                background:#221B38;

                color:white;

                border:none;

                border-radius:18px;

                font-size:14px;

                font-weight:bold;

            }

            QPushButton:hover{

                background:#7C3AED;

            }
            """)

            root.addWidget(btn)

        # ==========================
        # SIGNALS
        # ==========================

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