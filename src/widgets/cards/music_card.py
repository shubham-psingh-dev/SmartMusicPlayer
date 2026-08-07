from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtGui import (
    QColor,
    QCursor,
    QPixmap,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
)


# ==========================================
# Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]


class MusicCard(QWidget):

    def __init__(
        self,
        image_path: str,
        song_name: str,
        artist_name: str
    ):
        super().__init__()

        self.image_path = image_path
        self.song_name = song_name
        self.artist_name = artist_name

        self.setup_card()

        self.build_ui()

        self.apply_shadow()

    # ==========================================
    # Card Styling
    # ==========================================

    def setup_card(self):

        self.setFixedSize(205, 360)

        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.setObjectName("musicCard")

        self.setStyleSheet("""
        QWidget#musicCard{

            background:qlineargradient(
                x1:0,
                y1:0,
                x2:0,
                y2:1,
                stop:0 #322153,
                stop:1 #22173C
            );

            border:1px solid #46306F;

            border-radius:20px;

        }

        QWidget#musicCard:hover{

            border:2px solid #8B5CF6;

            background:qlineargradient(
                x1:0,
                y1:0,
                x2:0,
                y2:1,
                stop:0 #3D2966,
                stop:1 #291A46
            );

        }
        """)

    # ==========================================
    # UI
    # ==========================================

    def build_ui(self):

        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        self.layout.setSpacing(12)

        # -------------------------
        # Album Cover
        # -------------------------

        self.cover = QLabel()

        self.cover.setFixedSize(175, 175)

        self.cover.setAlignment(Qt.AlignCenter)

        pix = QPixmap(self.image_path)

        if not pix.isNull():

            self.cover.setPixmap(
                pix.scaled(
                    175,
                    175,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

        self.cover.setStyleSheet("""
        QLabel{

            background:#1B1432;

            border-radius:16px;

        }
        """)

        self.layout.addWidget(
            self.cover,
            alignment=Qt.AlignCenter
        )

	
	        # -------------------------
        # Song Name
        # -------------------------

        self.song = QLabel(self.song_name)

        self.song.setWordWrap(True)

        self.song.setStyleSheet("""
        QLabel{

            color:white;

            background:transparent;

            font-size:16px;

            font-weight:700;

        }
        """)

        self.layout.addWidget(self.song)

        # -------------------------
        # Artist
        # -------------------------

        self.artist = QLabel(self.artist_name)

        self.artist.setStyleSheet("""
        QLabel{

            color:#B8AEDF;

            background:transparent;

            font-size:13px;

        }
        """)

        self.layout.addWidget(self.artist)

        self.layout.addStretch()

        # -------------------------
        # Play Button
        # -------------------------

        self.play_btn = QPushButton("▶  Play")

        self.play_btn.setCursor(
            QCursor(Qt.PointingHandCursor)
        )

        self.play_btn.setFixedHeight(42)

        self.play_btn.setStyleSheet("""
        QPushButton{

            background:#7C3AED;

            color:white;

            border:none;

            border-radius:12px;

            font-size:14px;

            font-weight:700;

        }

        QPushButton:hover{

            background:#9F67FF;

        }

        QPushButton:pressed{

            background:#6D28D9;

        }
        """)

        self.layout.addWidget(self.play_btn)

    # ==========================================
    # Shadow
    # ==========================================

    def apply_shadow(self):

        shadow = QGraphicsDropShadowEffect(self)

        shadow.setBlurRadius(38)

        shadow.setOffset(0, 10)

        shadow.setColor(
            QColor(124, 58, 237, 120)
        )

        self.setGraphicsEffect(shadow)
	
	    # ==========================================
    	    # Hover Events
    	    # ==========================================

    def enterEvent(self, event):

        self.setStyleSheet("""
        QWidget#musicCard{

            background:qlineargradient(
                x1:0,
                y1:0,
                x2:0,
                y2:1,
                stop:0 #45306E,
                stop:1 #2C1B49
            );

            border:2px solid #9F67FF;

            border-radius:20px;

        }
        """)

        effect = self.graphicsEffect()

        if effect:

            effect.setBlurRadius(55)

            effect.setColor(
                QColor(155, 92, 255, 180)
            )

        super().enterEvent(event)

    # ==========================================

    def leaveEvent(self, event):

        self.setStyleSheet("""
        QWidget#musicCard{

            background:qlineargradient(
                x1:0,
                y1:0,
                x2:0,
                y2:1,
                stop:0 #322153,
                stop:1 #22173C
            );

            border:1px solid #46306F;

            border-radius:20px;

        }
        """)

        effect = self.graphicsEffect()

        if effect:

            effect.setBlurRadius(38)

            effect.setColor(
                QColor(124, 58, 237, 120)
            )

        super().leaveEvent(event)