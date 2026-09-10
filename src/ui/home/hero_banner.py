from pathlib import Path

from PySide6.QtCore import Qt, Signal
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

    # =====================================================
    # DAY 23 - NAVIGATION SIGNALS
    # =====================================================

    explore_requested = Signal()
    library_requested = Signal()

    def __init__(self):
        super().__init__()

        self.current_is_dark = True

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

        self.eyebrow = QLabel(
            "YOUR SOUND • YOUR MOMENT"
        )

        # -------------------------------------------------
        # MAIN TITLE
        # -------------------------------------------------

        self.title = QLabel(
            "What do you want\n"
            "to hear today?"
        )

        self.title.setWordWrap(True)

        self.title.setFont(
            QFont(
                "Segoe UI",
                30,
                QFont.Bold
            )
        )

        # -------------------------------------------------
        # FREQUENCY LINE
        # -------------------------------------------------

        self.frequency = QLabel(
            "Find Your Frequency  ✦"
        )

        # -------------------------------------------------
        # SUBTITLE
        # -------------------------------------------------

        self.subtitle = QLabel(
            "Discover your soul,\n"
            "Millions of beats, one experience."
        )

        self.subtitle.setWordWrap(True)

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

        self.explore_button = QPushButton(
            "Explore Music  →"
        )

        self.explore_button.setCursor(
            Qt.PointingHandCursor
        )

        self.explore_button.setFixedHeight(44)

        self.explore_button.clicked.connect(
            self.explore_requested.emit
        )

        # -------------------------------------------------
        # LIBRARY BUTTON
        # -------------------------------------------------

        self.library_button = QPushButton(
            "Open Library"
        )

        self.library_button.setCursor(
            Qt.PointingHandCursor
        )

        self.library_button.setFixedHeight(44)

        self.library_button.clicked.connect(
            self.library_requested.emit
        )

        buttons.addWidget(
            self.explore_button
        )

        buttons.addWidget(
            self.library_button
        )

        buttons.addStretch()

        # =================================================
        # ADD LEFT CONTENT
        # =================================================

        left.addWidget(
            self.eyebrow
        )

        left.addSpacing(6)

        left.addWidget(
            self.title
        )

        left.addSpacing(2)

        left.addWidget(
            self.frequency
        )

        left.addSpacing(2)

        left.addWidget(
            self.subtitle
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

        self.image = QLabel()

        self.image.setAlignment(
            Qt.AlignCenter
        )

        self.image.setMinimumSize(
            280,
            230
        )

        self.image.setStyleSheet(
            """
            QLabel {
                background: transparent;
                border: none;
            }
            """
        )

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

        self.apply_theme()

    # =====================================================
    # THEME
    # =====================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.current_is_dark = bool(
            is_dark
        )

        self.apply_theme()
        self.update()

    def apply_theme(self):

        if self.current_is_dark:

            self.eyebrow.setStyleSheet(
                """
                QLabel {
                    color: #CDBBFF;
                    background: transparent;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 1px;
                }
                """
            )

            self.title.setStyleSheet(
                """
                QLabel {
                    color: white;
                    background: transparent;
                }
                """
            )

            self.frequency.setStyleSheet(
                """
                QLabel {
                    color: #B993FF;
                    background: transparent;
                    font-size: 14px;
                    font-weight: 700;
                }
                """
            )

            self.subtitle.setStyleSheet(
                """
                QLabel {
                    color: #D7D0E9;
                    background: transparent;
                    font-size: 13px;
                }
                """
            )

            self.library_button.setStyleSheet(
                """
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
                """
            )

        else:

            self.eyebrow.setStyleSheet(
                """
                QLabel {
                    color: #6D3EB3;
                    background: transparent;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 1px;
                }
                """
            )

            self.title.setStyleSheet(
                """
                QLabel {
                    color: #2D2140;
                    background: transparent;
                }
                """
            )

            self.frequency.setStyleSheet(
                """
                QLabel {
                    color: #6D3EB3;
                    background: transparent;
                    font-size: 14px;
                    font-weight: 700;
                }
                """
            )

            self.subtitle.setStyleSheet(
                """
                QLabel {
                    color: #655B73;
                    background: transparent;
                    font-size: 13px;
                }
                """
            )

            self.library_button.setStyleSheet(
                """
                QPushButton {
                    color: #4D3568;
                    background: rgba(255,255,255,150);
                    border: 1px solid rgba(104,64,160,65);
                    border-radius: 13px;
                    padding: 0 22px;
                    font-size: 13px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: rgba(255,255,255,210);
                    border: 1px solid rgba(124,58,237,120);
                }

                QPushButton:pressed {
                    background: rgba(235,226,246,235);
                }
                """
            )

        self.explore_button.setStyleSheet(
            """
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
            """
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

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        if self.current_is_dark:

            colors = [
                (0.0, QColor("#171128")),
                (0.35, QColor("#241642")),
                (0.72, QColor("#432477")),
                (1.0, QColor("#642CC1")),
            ]

        else:

            colors = [
                (0.0, QColor("#F3ECFA")),
                (0.35, QColor("#E9DDF8")),
                (0.72, QColor("#D7C2F1")),
                (1.0, QColor("#C49CEB")),
            ]

        for stop, color in colors:
            gradient.setColorAt(
                stop,
                color
            )

        painter.fillPath(
            path,
            gradient
        )

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
