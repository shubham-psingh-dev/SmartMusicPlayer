from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[3]

HEADPHONE_PATH = (
    BASE_DIR
    / "assets"
    / "images"
    / "hero"
    / "headphones.png"
)


# =========================================================
# HERO BANNER
# =========================================================

class HeroBanner(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(300)
        self.setMaximumHeight(320)

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(
            38,
            28,
            38,
            28
        )

        root.setSpacing(20)

        # =================================================
        # LEFT CONTENT
        # =================================================

        left = QVBoxLayout()

        left.setContentsMargins(
            0,
            0,
            0,
            0
        )

        left.setSpacing(8)

        # -------------------------------------------------
        # SMALL LABEL
        # -------------------------------------------------

        eyebrow = QLabel(
            "YOUR SOUND • YOUR MOMENT"
        )

        eyebrow.setStyleSheet("""
        QLabel {
            color: #CDBBFF;
            background: transparent;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        }
        """)

        # -------------------------------------------------
        # MAIN TITLE
        # -------------------------------------------------

        title = QLabel(
            "What do you want\n"
            "to hear today?"
        )

        title.setWordWrap(True)

        title.setFont(
            QFont(
                "Segoe UI",
                30,
                QFont.Bold
            )
        )

        title.setStyleSheet("""
        QLabel {
            color: white;
            background: transparent;
            line-height: 115%;
        }
        """)

        # -------------------------------------------------
        # FREQUENCY LINE
        # -------------------------------------------------

        frequency = QLabel(
            "Find Your Frequency  ✦"
        )

        frequency.setStyleSheet("""
        QLabel {
            color: #B993FF;
            background: transparent;
            font-size: 14px;
            font-weight: 700;
        }
        """)

        # -------------------------------------------------
        # SUBTITLE
        # -------------------------------------------------

        subtitle = QLabel(
            "Discover your soul,\n"
            "Millions of beats, one experience."
        )

        subtitle.setWordWrap(True)

        subtitle.setStyleSheet("""
        QLabel {
            color: #D7D0E9;
            background: transparent;
            font-size: 13px;
            line-height: 150%;
        }
        """)

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        buttons.setContentsMargins(
            0,
            4,
            0,
            0
        )

        buttons.setSpacing(12)

        # -------------------------------------------------
        # EXPLORE BUTTON
        # -------------------------------------------------

        explore = QPushButton(
            "Explore Music  →"
        )

        explore.setCursor(
            Qt.PointingHandCursor
        )

        explore.setFixedHeight(44)

        explore.setStyleSheet("""
        QPushButton {

            color: white;

            background:
                qlineargradient(
                    x1:0,
                    y1:0,
                    x2:1,
                    y2:1,
                    stop:0 #A66BFF,
                    stop:0.45 #8B5CF6,
                    stop:1 #7138D4
                );

            border: 1px solid rgba(214,190,255,120);

            border-radius: 13px;

            padding: 0 22px;

            font-size: 13px;

            font-weight: 700;

        }

        QPushButton:hover {

            background:
                qlineargradient(
                    x1:0,
                    y1:0,
                    x2:1,
                    y2:1,
                    stop:0 #B985FF,
                    stop:0.5 #9F67FF,
                    stop:1 #7C3AED
                );

            border: 1px solid rgba(235,220,255,180);

        }

        QPushButton:pressed {

            background: #6D35C9;

        }
        """)

        # -------------------------------------------------
        # LIBRARY BUTTON
        # -------------------------------------------------

        library = QPushButton(
            "Open Library"
        )

        library.setCursor(
            Qt.PointingHandCursor
        )

        library.setFixedHeight(44)

        library.setStyleSheet("""
        QPushButton {

            color: #F3EEFF;

            background: rgba(255,255,255,18);

            border: 1px solid rgba(210,190,255,65);

            border-radius: 13px;

            padding: 0 22px;

            font-size: 13px;

            font-weight: 700;

        }

        QPushButton:hover {

            background: rgba(155,110,255,35);

            border: 1px solid rgba(190,155,255,120);

        }

        QPushButton:pressed {

            background: rgba(120,75,210,45);

        }
        """)

        buttons.addWidget(
            explore
        )

        buttons.addWidget(
            library
        )

        buttons.addStretch()

        # =================================================
        # ADD LEFT CONTENT
        # =================================================

        left.addWidget(
            eyebrow
        )

        left.addSpacing(6)

        left.addWidget(
            title
        )

        left.addSpacing(2)

        left.addWidget(
            frequency
        )

        left.addSpacing(2)

        left.addWidget(
            subtitle
        )

        left.addSpacing(12)

        left.addLayout(
            buttons
        )

        left.addStretch()

        root.addLayout(
            left,
            3
        )

        # =================================================
        # RIGHT IMAGE AREA
        # =================================================

        right = QVBoxLayout()

        right.setContentsMargins(
            0,
            0,
            0,
            0
        )

        right.setAlignment(
            Qt.AlignCenter
        )

        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        self.image = QLabel()

        self.image.setAlignment(
            Qt.AlignCenter
        )

        self.image.setMinimumSize(
            280,
            230
        )

        self.image.setStyleSheet("""
        QLabel {
            background: transparent;
            border: none;
        }
        """)

        if HEADPHONE_PATH.exists():

            pix = QPixmap(
                str(HEADPHONE_PATH)
            )

            if not pix.isNull():

                self.image.setPixmap(
                    pix.scaled(
                        275,
                        275,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )

        right.addWidget(
            self.image,
            alignment=Qt.AlignCenter
        )

        root.addLayout(
            right,
            2
        )

    # =====================================================
    # PAINT
    # =====================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # =================================================
        # MAIN HERO SHAPE
        # =================================================

        hero_rect = rect.adjusted(
            1,
            1,
            -1,
            -1
        )

        path = QPainterPath()

        path.addRoundedRect(
            hero_rect,
            28,
            28
        )

        # =================================================
        # PREMIUM BACKGROUND
        # =================================================

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#171128")
        )

        gradient.setColorAt(
            0.35,
            QColor("#241642")
        )

        gradient.setColorAt(
            0.72,
            QColor("#432477")
        )

        gradient.setColorAt(
            1.0,
            QColor("#642CC1")
        )

        painter.fillPath(
            path,
            gradient
        )

        # =================================================
        # SOFT INNER GLOW
        # =================================================

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                182,
                132,
                255,
                22
            )
        )

        painter.drawEllipse(
            rect.width() - 370,
            -50,
            400,
            390
        )

        # =================================================
        # LIGHT GREY / LAVENDER IMAGE BACKDROP
        # =================================================

        image_glow = QLinearGradient(
            rect.width() - 360,
            0,
            rect.width() - 70,
            rect.height()
        )

        image_glow.setColorAt(
            0.0,
            QColor(
                230,
                225,
                240,
                20
            )
        )

        image_glow.setColorAt(
            0.45,
            QColor(
                210,
                204,
                225,
                38
            )
        )

        image_glow.setColorAt(
            1.0,
            QColor(
                170,
                125,
                235,
                18
            )
        )

        painter.setBrush(
            image_glow
        )

        painter.drawEllipse(
            rect.width() - 335,
            15,
            300,
            275
        )

        # =================================================
        # INNER PURPLE IMAGE RING
        # =================================================

        painter.setBrush(
            QColor(
                133,
                76,
                220,
                32
            )
        )

        painter.drawEllipse(
            rect.width() - 295,
            42,
            220,
            220
        )

        # =================================================
        # SOUND WAVES
        # =================================================

        painter.setBrush(
            Qt.NoBrush
        )

        wave_colors = [
            QColor(211, 184, 255, 48),
            QColor(194, 158, 255, 65),
            QColor(230, 210, 255, 32),
        ]

        wave_offsets = [
            0,
            14,
            28,
        ]

        for index, offset in enumerate(
            wave_offsets
        ):

            wave = QPainterPath()

            start_x = rect.width() - 470
            start_y = 115 + offset

            wave.moveTo(
                start_x,
                start_y
            )

            wave.cubicTo(
                rect.width() - 390,
                start_y - 65,
                rect.width() - 340,
                start_y + 65,
                rect.width() - 270,
                start_y
            )

            wave.cubicTo(
                rect.width() - 205,
                start_y - 60,
                rect.width() - 145,
                start_y + 60,
                rect.width() - 70,
                start_y
            )

            pen = QPen(
                wave_colors[index]
            )

            pen.setWidth(
                2
            )

            painter.setPen(
                pen
            )

            painter.drawPath(
                wave
            )

        # =================================================
        # SMALL SOUND WAVES
        # =================================================

        for y, alpha in [
            (74, 55),
            (228, 45),
            (258, 35),
        ]:

            wave = QPainterPath()

            wave.moveTo(
                rect.width() - 420,
                y
            )

            wave.cubicTo(
                rect.width() - 385,
                y - 25,
                rect.width() - 350,
                y + 25,
                rect.width() - 315,
                y
            )

            wave.cubicTo(
                rect.width() - 280,
                y - 22,
                rect.width() - 245,
                y + 22,
                rect.width() - 210,
                y
            )

            pen = QPen(
                QColor(
                    225,
                    207,
                    255,
                    alpha
                )
            )

            pen.setWidth(
                1
            )

            painter.setPen(
                pen
            )

            painter.drawPath(
                wave
            )

        # =================================================
        # MUSIC NOTES
        # =================================================

        painter.setPen(
            QColor(
                235,
                220,
                255,
                130
            )
        )

        note_font = QFont(
            "Segoe UI Symbol",
            17
        )

        painter.setFont(
            note_font
        )

        painter.drawText(
            rect.width() - 285,
            52,
            "♪"
        )

        painter.drawText(
            rect.width() - 170,
            85,
            "♫"
        )

        painter.drawText(
            rect.width() - 330,
            245,
            "♬"
        )

        painter.drawText(
            rect.width() - 105,
            215,
            "♪"
        )

        # =================================================
        # PREMIUM BORDER
        # =================================================

        border_pen = QPen(
            QColor(
                180,
                140,
                255,
                125
            )
        )

        border_pen.setWidth(
            1
        )

        painter.setPen(
            border_pen
        )

        painter.setBrush(
            Qt.NoBrush
        )

        painter.drawPath(
            path
        )

        painter.end()

        super().paintEvent(
            event
        )