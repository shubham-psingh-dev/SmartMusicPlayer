from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QLinearGradient,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
)


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()

# music_player_desktop/
PROJECT_DIR = FILE_DIR.parents[3]

# music_player_desktop/src/
SRC_DIR = FILE_DIR.parents[2]


class CoverLabel(QLabel):

    def __init__(self):
        super().__init__()

        self.setFixedSize(172, 172)
        self.setAlignment(Qt.AlignCenter)

        self.setStyleSheet("""
        QLabel {
            background: #211633;
            border: none;
            border-radius: 18px;
        }
        """)

    def paintEvent(self, event):

        if self.pixmap() is None:
            super().paintEvent(event)
            return

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        path = QPainterPath()

        path.addRoundedRect(
            self.rect(),
            18,
            18
        )

        painter.setClipPath(path)

        painter.drawPixmap(
            self.rect(),
            self.pixmap()
        )

        painter.end()


class MusicCard(QFrame):

    def __init__(
        self,
        image_path,
        title,
        artist
    ):

        super().__init__()

        self.image_path = image_path
        self.title_text = title
        self.artist_text = artist

        self.is_hovered = False

        # ------------------------------------------------
        # CARD SIZE
        # ------------------------------------------------

        self.setFixedWidth(196)
        self.setMinimumHeight(326)

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setObjectName(
            "MusicCard"
        )

        self.build_ui()

        self.load_cover()

        self.setup_shadow()

    # ============================================================
    # UI
    # ============================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(
            10,
            10,
            10,
            12
        )

        root.setSpacing(9)

        # ========================================================
        # COVER AREA
        # ========================================================

        self.cover_frame = QFrame()

        self.cover_frame.setFixedSize(
            176,
            176
        )

        self.cover_frame.setObjectName(
            "CoverFrame"
        )

        self.cover_frame.setStyleSheet("""
        QFrame#CoverFrame {
            background: #211633;
            border: 1px solid rgba(139, 92, 246, 45);
            border-radius: 20px;
        }
        """)

        cover_layout = QVBoxLayout(
            self.cover_frame
        )

        cover_layout.setContentsMargins(
            2,
            2,
            2,
            2
        )

        cover_layout.setSpacing(0)

        # ========================================================
        # COVER IMAGE
        # ========================================================

        self.cover = CoverLabel()

        cover_layout.addWidget(
            self.cover
        )

        # ========================================================
        # PLAY BUTTON
        # ========================================================

        self.play_btn = QPushButton(
            "▶"
        )

        self.play_btn.setFixedSize(
            54,
            54
        )

        self.play_btn.setCursor(
            Qt.PointingHandCursor
        )

        self.play_btn.setObjectName(
            "PlayButton"
        )

        self.play_btn.setStyleSheet("""
        QPushButton#PlayButton {

            background: #8B5CF6;

            color: white;

            border: 2px solid rgba(255,255,255,45);

            border-radius: 27px;

            font-size: 19px;

            font-weight: 700;

            padding-left: 3px;

        }

        QPushButton#PlayButton:hover {

            background: #A970FF;

            border: 2px solid rgba(255,255,255,90);

        }

        QPushButton#PlayButton:pressed {

            background: #6D28D9;

        }
        """)

        self.play_btn.hide()

        # Important:
        # button stays inside cover_frame
        self.play_btn.setParent(
            self.cover_frame
        )

        # ========================================================
        # TITLE
        # ========================================================

        self.title = QLabel(
            self.title_text
        )

        self.title.setWordWrap(
            False
        )

        self.title.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        self.title.setStyleSheet("""
        QLabel {

            color: #FFFFFF;

            font-size: 15px;

            font-weight: 700;

            background: transparent;

            border: none;

            padding: 0px;

        }
        """)

        # ========================================================
        # ARTIST
        # ========================================================

        self.artist = QLabel(
            self.artist_text
        )

        self.artist.setWordWrap(
            False
        )

        self.artist.setStyleSheet("""
        QLabel {

            color: #AFA4C8;

            font-size: 13px;

            background: transparent;

            border: none;

            padding: 0px;

        }
        """)

        # ========================================================
        # DURATION
        # ========================================================

        self.duration = QLabel(
            "3:45"
        )

        self.duration.setStyleSheet("""
        QLabel {

            color: #756A91;

            font-size: 11px;

            background: transparent;

            border: none;

            padding: 0px;

        }
        """)

        # ========================================================
        # ADD TO LAYOUT
        # ========================================================

        root.addWidget(
            self.cover_frame,
            alignment=Qt.AlignCenter
        )

        root.addSpacing(2)

        root.addWidget(
            self.title
        )

        root.addWidget(
            self.artist
        )

        root.addWidget(
            self.duration
        )

        root.addStretch()

    # ============================================================
    # LOAD COVER
    # ============================================================

    def load_cover(self):

        possible_paths = [

            # Given path relative to project
            PROJECT_DIR / self.image_path,

            # Given path relative to src
            SRC_DIR / self.image_path,

            # Current working directory
            Path.cwd() / self.image_path,

            # Absolute path, if supplied
            Path(self.image_path),

        ]

        image_file = None

        for path in possible_paths:

            try:

                if path.exists() and path.is_file():

                    image_file = path
                    break

            except Exception:
                continue

        # --------------------------------------------------------
        # IMAGE FOUND
        # --------------------------------------------------------

        if image_file:

            pixmap = QPixmap(
                str(image_file)
            )

            if not pixmap.isNull():

                scaled = pixmap.scaled(
                    172,
                    172,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                self.cover.setPixmap(
                    scaled
                )

                return

        # --------------------------------------------------------
        # IMAGE NOT FOUND
        # --------------------------------------------------------

        self.cover.setPixmap(
            QPixmap()
        )

        self.cover.setText(
            "♪"
        )

        self.cover.setStyleSheet("""
        QLabel {

            background: #211633;

            color: #8B5CF6;

            font-size: 42px;

            border-radius: 18px;

        }
        """)

    # ============================================================
    # SHADOW
    # ============================================================

    def setup_shadow(self):

        self.shadow = QGraphicsDropShadowEffect(
            self
        )

        self.shadow.setBlurRadius(
            24
        )

        self.shadow.setOffset(
            0,
            8
        )

        self.shadow.setColor(
            QColor(
                124,
                58,
                237,
                55
            )
        )

        self.setGraphicsEffect(
            self.shadow
        )

    # ============================================================
    # POSITION PLAY BUTTON
    # ============================================================

    def position_play_button(self):

        x = (
            self.cover_frame.width()
            - self.play_btn.width()
        ) // 2

        y = (
            self.cover_frame.height()
            - self.play_btn.height()
        ) // 2

        self.play_btn.move(
            x,
            y
        )

    # ============================================================
    # RESIZE EVENT
    # ============================================================

    def resizeEvent(self, event):

        self.position_play_button()

        super().resizeEvent(
            event
        )

    # ============================================================
    # HOVER ENTER
    # ============================================================

    def enterEvent(self, event):

        self.is_hovered = True

        self.play_btn.show()

        self.position_play_button()

        self.cover_frame.setStyleSheet("""
        QFrame#CoverFrame {

            background: #24163E;

            border: 2px solid #8B5CF6;

            border-radius: 20px;

        }
        """)

        self.shadow.setBlurRadius(
            34
        )

        self.shadow.setOffset(
            0,
            10
        )

        self.shadow.setColor(
            QColor(
                139,
                92,
                246,
                105
            )
        )

        super().enterEvent(
            event
        )

    # ============================================================
    # HOVER LEAVE
    # ============================================================

    def leaveEvent(self, event):

        self.is_hovered = False

        self.play_btn.hide()

        self.cover_frame.setStyleSheet("""
        QFrame#CoverFrame {

            background: #211633;

            border: 1px solid rgba(139, 92, 246, 45);

            border-radius: 20px;

        }
        """)

        self.shadow.setBlurRadius(
            24
        )

        self.shadow.setOffset(
            0,
            8
        )

        self.shadow.setColor(
            QColor(
                124,
                58,
                237,
                55
            )
        )

        super().leaveEvent(
            event
        )

    # ============================================================
    # PAINT EVENT
    # ============================================================

    def paintEvent(self, event):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # --------------------------------------------------------
        # CARD SHAPE
        # --------------------------------------------------------

        path = QPainterPath()

        path.addRoundedRect(
            rect.adjusted(
                1,
                1,
                -1,
                -1
            ),
            20,
            20
        )

        # --------------------------------------------------------
        # DARK PURPLE GRADIENT
        # --------------------------------------------------------

        gradient = QLinearGradient(
            0,
            0,
            0,
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#211633")
        )

        gradient.setColorAt(
            0.55,
            QColor("#191226")
        )

        gradient.setColorAt(
            1.0,
            QColor("#110D1B")
        )

        painter.fillPath(
            path,
            gradient
        )

        # --------------------------------------------------------
        # BORDER
        # --------------------------------------------------------

        if self.is_hovered:

            border_color = QColor(
                139,
                92,
                246,
                150
            )

        else:

            border_color = QColor(
                139,
                92,
                246,
                42
            )

        pen = QPen(
            border_color
        )

        pen.setWidth(
            1
        )

        painter.setPen(
            pen
        )

        painter.drawPath(
            path
        )

        # --------------------------------------------------------
        # TOP PURPLE GLOW
        # --------------------------------------------------------

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                139,
                92,
                246,
                15
            )
        )

        painter.drawEllipse(
            rect.width() - 75,
            -30,
            100,
            100
        )

        # --------------------------------------------------------
        # BOTTOM GLOW
        # --------------------------------------------------------

        painter.setBrush(
            QColor(
                168,
                85,
                247,
                10
            )
        )

        painter.drawEllipse(
            -25,
            rect.height() - 70,
            90,
            90
        )

        painter.end()