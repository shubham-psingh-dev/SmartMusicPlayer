from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class MusicCard(QWidget):

    def __init__(
        self,
        image_path,
        song_name,
        artist_name
    ):
        super().__init__()

        self.setFixedSize(190, 280)

        self.setStyleSheet("""
        QWidget{
            background:#2A1E4D;
            border-radius:18px;
        }

        QWidget:hover{
            border:2px solid #8B5CF6;
        }
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(12,12,12,12)
        layout.setSpacing(10)

        # -------------------------
        # Album Cover
        # -------------------------

        self.cover = QLabel()

        pix = QPixmap(image_path)

        self.cover.setPixmap(
            pix.scaled(
                165,
                165,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
        )

        self.cover.setFixedSize(165,165)

        layout.addWidget(
            self.cover,
            alignment=Qt.AlignCenter
        )

        # -------------------------
        # Song Name
        # -------------------------

        self.song = QLabel(song_name)

        self.song.setStyleSheet("""
        color:white;
        font-size:16px;
        font-weight:bold;
        background:transparent;
        """)

        layout.addWidget(self.song)

        # -------------------------
        # Artist
        # -------------------------

        self.artist = QLabel(artist_name)

        self.artist.setStyleSheet("""
        color:#B4A8D6;
        font-size:12px;
        background:transparent;
        """)

        layout.addWidget(self.artist)

        layout.addStretch()

        # -------------------------
        # Play Button
        # -------------------------

        self.play_btn = QPushButton("▶ Play")

        self.play_btn.setCursor(Qt.PointingHandCursor)

        self.play_btn.setStyleSheet("""
        QPushButton{

            background:#7C3AED;
            color:white;

            border:none;

            border-radius:12px;

            padding:10px;

            font-size:13px;

            font-weight:bold;

        }

        QPushButton:hover{

            background:#9F67FF;

        }
        """)

        layout.addWidget(self.play_btn)