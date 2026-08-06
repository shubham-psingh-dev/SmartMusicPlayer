from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
)

from PySide6.QtGui import (
    QPixmap,
    QCursor,
    QColor,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
)


BASE_DIR = Path(__file__).resolve().parents[2]

ALBUM_DIR = (
    BASE_DIR
    / "assets"
    / "album_art"
)


class MusicCard(QWidget):

    def __init__(
        self,
        song,
        song_name,
        artist_name
    ):
        super().__init__()

        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.setFixedSize(195, 340)

        self.setStyleSheet("""
        QWidget{

            background:qlineargradient(
                x1:0,y1:0,
                x2:0,y2:1,
                stop:0 #332255,
                stop:1 #24163F
            );

            border:1px solid #3F2A68;

            border-radius:18px;

        }

        QWidget:hover{

            border:2px solid #8B5CF6;

            background:qlineargradient(
                x1:0,y1:0,
                x2:0,y2:1,
                stop:0 #402B67,
                stop:1 #291943
            );

        }
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        

        # ==========================
        # Album Cover
        # ==========================

        self.cover = QLabel()

        cover = Path(song)

        pix = QPixmap(str(cover))

        self.cover.setPixmap(
            pix.scaled(
                170,
                170,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
        )

        self.cover.setFixedSize(170, 170)

        self.cover.setStyleSheet("""
        QLabel{
            background:transparent;
            border-radius:16px;
        }
        """)

        layout.addWidget(
            self.cover,
            alignment=Qt.AlignCenter
        )

        # ==========================
        # Song Name
        # ==========================

        self.song = QLabel(song_name)

        self.song.setStyleSheet("""
        color:white;
        font-size:16px;
        font-weight:bold;
        background:transparent;
        """)

        layout.addWidget(self.song)

        # ==========================
        # Artist
        # ==========================

        self.artist = QLabel(artist_name)

        self.artist.setStyleSheet("""
        color:#B4A8D6;
        font-size:12px;
        background:transparent;
        """)

        layout.addWidget(self.artist)

        layout.addSpacing(8)

        # ==========================
        # Play Button
        # ==========================

        self.play_btn = QPushButton("▶ Play")

        self.play_btn.setCursor(Qt.PointingHandCursor)

        self.play_btn.setStyleSheet("""
        QPushButton{

            background:#7C3AED;

            color:white;

            border:none;

            border-radius:14px;

            padding:10px;

            font-size:13px;

            font-weight:700;

        }

        QPushButton:hover{

            background:#9F67FF;

        }

        QPushButton:pressed{

            background:#6D28D9;

        }
        """)

        layout.addWidget(self.play_btn)

        layout.addStretch()

        # ==========================
        # Shadow
        # ==========================

        shadow = QGraphicsDropShadowEffect(self)

        shadow.setBlurRadius(40)

        shadow.setOffset(0, 12)

        shadow.setColor(QColor(124, 58, 237, 120))

        self.setGraphicsEffect(shadow)

        # ==========================
        # Hover Animation
        # ==========================

        self.anim = QPropertyAnimation(self, b"geometry")

        self.anim.setDuration(170)

        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):

        self.anim.stop()

        self.anim.setStartValue(self.geometry())

        self.anim.setEndValue(
            QRect(
                self.x(),
                self.y() - 8,
                self.width(),
                self.height()
            )
        )

        self.anim.start()

        super().enterEvent(event)


    def leaveEvent(self, event):

        self.anim.stop()

        self.anim.setStartValue(self.geometry())

        self.anim.setEndValue(
            QRect(
                self.x(),
                self.y() + 8,
                self.width(),
                self.height()
            )
        )

        self.anim.start()

        super().leaveEvent(event)    