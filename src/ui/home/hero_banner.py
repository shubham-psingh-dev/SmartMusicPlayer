from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
)


class HeroBanner(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedHeight(260)

        self.setStyleSheet("""
        QWidget{
            background:qlineargradient(
                x1:0,y1:0,
                x2:1,y2:1,
                stop:0 #31215E,
                stop:1 #181327
            );

            border-radius:24px;
        }
        """)

        self.build_ui()

    def build_ui(self):

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(35, 30, 35, 30)

        # -----------------------
        # LEFT SIDE
        # -----------------------

        left = QVBoxLayout()

        greeting = QLabel("Good Evening 👋")

        greeting.setStyleSheet("""
        color:#CFC8FF;
        font-size:16px;
        background:transparent;
        """)

        title = QLabel("What do you want\n to hear today?")

        title.setStyleSheet("""
        color:white;
        font-size:34px;
        font-weight:700;
        background:transparent;
        """)

        subtitle = QLabel(
            "Discover millions of songs\ncrafted for your mood."
        )

        subtitle.setStyleSheet("""
        color:#B8B3D6;
        font-size:15px;
        background:transparent;
        """)

        left.addWidget(greeting)
        left.addSpacing(10)
        left.addWidget(title)
        left.addSpacing(12)
        left.addWidget(subtitle)
        left.addStretch()

        # -----------------------
        # RIGHT SIDE
        # -----------------------

        image_placeholder = QFrame()

        image_placeholder.setFixedSize(260, 200)

        image_placeholder.setStyleSheet("""
        QFrame{

            background:#2D2352;

            border-radius:20px;

            border:2px dashed #7C3AED;

        }
        """)

        image_text = QLabel("🎧")

        image_text.setAlignment(Qt.AlignCenter)

        image_text.setStyleSheet("""
        font-size:72px;
        background:transparent;
        color:white;
        """)

        img_layout = QVBoxLayout(image_placeholder)

        img_layout.addStretch()
        img_layout.addWidget(image_text)
        img_layout.addStretch()

        main_layout.addLayout(left, 3)

        main_layout.addWidget(
            image_placeholder,
            alignment=Qt.AlignRight
        )