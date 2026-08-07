from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QPushButton,
    QSlider,
)

BASE_DIR = Path(__file__).resolve().parents[2]

ALBUM_DIR = (
    BASE_DIR
    / "assets"
    / "album_art"
)


class NowPlaying(QWidget):

    def __init__(self):
        super().__init__()

        self.build_ui()

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()

        card.setFixedWidth(320)

        card.setStyleSheet("""
        QFrame{

            background:#21183A;

            border:1px solid #3E2A67;

            border-radius:22px;

        }
        """)

        layout = QVBoxLayout(card)

        layout.setContentsMargins(22,22,22,22)

        layout.setSpacing(18)

        root.addWidget(card)

        # ======================
        # TITLE
        # ======================

        title = QLabel("NOW PLAYING")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
        color:#C8BFFF;
        font-size:13px;
        font-weight:700;
        """)

        layout.addWidget(title)

                # ======================
        # ALBUM ART
        # ======================

        self.album_art = QLabel()

        self.album_art.setFixedSize(220, 220)

        self.album_art.setAlignment(Qt.AlignCenter)

        self.album_art.setStyleSheet("""
        QLabel{

            background:#2D2050;

            border-radius:110px;

        }
        """)

        default_art = ALBUM_DIR / "believer.jpg"

        if default_art.exists():

            pix = QPixmap(str(default_art))

            self.album_art.setPixmap(
                pix.scaled(
                    190,
                    190,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        layout.addWidget(
            self.album_art,
            alignment=Qt.AlignCenter
        )

        # ======================
        # SONG NAME
        # ======================

        self.song_name = QLabel("Believer")

        self.song_name.setAlignment(Qt.AlignCenter)

        self.song_name.setStyleSheet("""
        QLabel{

            color:white;

            font-size:22px;

            font-weight:700;

        }
        """)

        layout.addWidget(self.song_name)

        # ======================
        # ARTIST
        # ======================

        self.artist_name = QLabel("Imagine Dragons")

        self.artist_name.setAlignment(Qt.AlignCenter)

        self.artist_name.setStyleSheet("""
        QLabel{

            color:#A89DD5;

            font-size:14px;

        }
        """)

        layout.addWidget(self.artist_name)

                # ======================
        # PROGRESS
        # ======================

        self.progress = QSlider(Qt.Horizontal)

        self.progress.setValue(35)

        self.progress.setStyleSheet("""
        QSlider::groove:horizontal{

            height:6px;

            background:#3A2B61;

            border-radius:3px;

        }

        QSlider::sub-page:horizontal{

            background:#8B5CF6;

            border-radius:3px;

        }

        QSlider::handle:horizontal{

            background:white;

            width:14px;

            margin:-5px 0;

            border-radius:7px;

        }
        """)

        layout.addWidget(self.progress)

        # ======================
        # TIME
        # ======================

        time_layout = QHBoxLayout()

        current = QLabel("1:14")

        total = QLabel("3:45")

        current.setStyleSheet("color:#A89DD5; font-size:12px;")
        total.setStyleSheet("color:#A89DD5; font-size:12px;")

        time_layout.addWidget(current)

        time_layout.addStretch()

        time_layout.addWidget(total)

        layout.addLayout(time_layout)

        # ======================
        # CONTROLS
        # ======================

        controls = QHBoxLayout()

        controls.setSpacing(18)

        self.prev_btn = QPushButton("⏮")

        self.play_btn = QPushButton("▶")

        self.next_btn = QPushButton("⏭")

        for btn in (
            self.prev_btn,
            self.play_btn,
            self.next_btn,
        ):

            btn.setFixedSize(52, 52)

            btn.setCursor(Qt.PointingHandCursor)

            btn.setStyleSheet("""
            QPushButton{

                background:#7C3AED;

                color:white;

                border:none;

                border-radius:26px;

                font-size:18px;

                font-weight:bold;

            }

            QPushButton:hover{

                background:#9F67FF;

            }
            """)

            controls.addWidget(btn)

        layout.addLayout(controls)

        layout.addStretch()