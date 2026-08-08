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


# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[3]

HEADPHONE_PATH = (
    BASE_DIR
    / "assets"
    / "images"
    / "hero"
    / "headphones.png"
)


class HeroBanner(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(300)

        self.setMaximumHeight(320)

        self.build_ui()

    # ==========================================
    # UI
    # ==========================================

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(
            38,
            32,
            38,
            32
        )

        root.setSpacing(30)

        # ==========================================
        # LEFT
        # ==========================================

        left = QVBoxLayout()

        left.setSpacing(10)

        greeting = QLabel("Good Evening 👋")

        greeting.setStyleSheet("""
        QLabel{

            color:#C9B9FF;

            font-size:14px;

            font-weight:600;

        }
        """)

        title = QLabel(
            "Lose Yourself\nIn Sound"
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
        QLabel{

            color:white;

            line-height:115%;

        }
        """)

        subtitle = QLabel(
            "Discover your perfect soundtrack.\n"
            "Millions of songs. One beautiful experience."
        )

        subtitle.setStyleSheet("""
        QLabel{

            color:#CFC7E8;

            font-size:15px;

            line-height:24px;

        }
        """)

        # ==========================================
        # BUTTONS
        # ==========================================

        buttons = QHBoxLayout()

        buttons.setSpacing(14)

        explore = QPushButton("Explore")

        explore.setCursor(Qt.PointingHandCursor)

        explore.setFixedHeight(46)

        explore.setStyleSheet("""
        QPushButton{

            background:#8B5CF6;

            color:white;

            border:none;

            border-radius:14px;

            padding:0 28px;

            font-size:15px;

            font-weight:700;

        }

        QPushButton:hover{

            background:#9F67FF;

        }

        QPushButton:pressed{

            background:#7443E8;

        }

        """)

        library = QPushButton("Library")

        library.setCursor(Qt.PointingHandCursor)

        library.setFixedHeight(46)

        library.setStyleSheet("""
        QPushButton{

            background:rgba(255,255,255,18);

            color:white;

            border:1px solid rgba(255,255,255,40);

            border-radius:14px;

            padding:0 28px;

            font-size:15px;

            font-weight:700;

        }

        QPushButton:hover{

            background:rgba(255,255,255,35);

        }

        """)

        buttons.addWidget(explore)

        buttons.addWidget(library)

        buttons.addStretch()

        left.addWidget(greeting)

        left.addWidget(title)

        left.addSpacing(6)

        left.addWidget(subtitle)

        left.addSpacing(18)

        left.addLayout(buttons)

        left.addStretch()

        root.addLayout(left, 3)

                # ==========================================
        # RIGHT
        # ==========================================

        right = QVBoxLayout()

        right.setAlignment(Qt.AlignCenter)

        # ------------------------------------------
        # Headphone Image
        # ------------------------------------------

        self.image = QLabel()

        self.image.setAlignment(Qt.AlignCenter)

        if HEADPHONE_PATH.exists():

            pix = QPixmap(str(HEADPHONE_PATH))

            self.image.setPixmap(
                pix.scaled(
                    265,
                    265,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        self.image.setStyleSheet("""
        QLabel{

            background:transparent;

            padding:8px;

        }
        """)

        # ------------------------------------------
        # Floating Music Notes
        # ------------------------------------------

        note1 = QLabel("♪")

        note1.setStyleSheet("""
        QLabel{

            color:rgba(220,200,255,170);

            font-size:22px;

            font-weight:700;

            background:transparent;

        }
        """)

        note1.setAlignment(Qt.AlignCenter)

        note2 = QLabel("♫")

        note2.setStyleSheet("""
        QLabel{

            color:rgba(200,180,255,140);

            font-size:18px;

            background:transparent;

        }
        """)

        note2.setAlignment(Qt.AlignCenter)

        right.addWidget(
            note1,
            alignment=Qt.AlignRight
        )

        right.addWidget(
            self.image,
            alignment=Qt.AlignCenter
        )

        right.addWidget(
            note2,
            alignment=Qt.AlignLeft
        )

        right.addStretch()

        root.addLayout(
            right,
            2
        )

            # ==========================================
    # PAINT
    # ==========================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # --------------------------------------
        # Rounded Background
        # --------------------------------------

        path = QPainterPath()

        path.addRoundedRect(
            rect.adjusted(1, 1, -1, -1),
            28,
            28
        )

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#18122B")
        )

        gradient.setColorAt(
            0.45,
            QColor("#2A1B46")
        )

        gradient.setColorAt(
            1.0,
            QColor("#5B21B6")
        )

        painter.fillPath(
            path,
            gradient
        )

        # --------------------------------------
        # Border
        # --------------------------------------

        pen = QPen(
            QColor(160, 120, 255, 120)
        )

        pen.setWidth(2)

        painter.setPen(pen)

        painter.drawPath(path)

        # --------------------------------------
        # Purple Glow
        # --------------------------------------

        painter.setPen(Qt.NoPen)

        painter.setBrush(
            QColor(168, 85, 247, 45)
        )

        painter.drawEllipse(
            rect.width() - 320,
            10,
            280,
            280
        )

        painter.setBrush(
            QColor(139, 92, 246, 28)
        )

        painter.drawEllipse(
            rect.width() - 250,
            65,
            180,
            180
        )

        painter.setBrush(
            QColor(124, 58, 237, 20)
        )

        painter.drawEllipse(
            rect.width() - 410,
            130,
            120,
            120
        )

        # --------------------------------------
        # Decorative Music Notes
        # --------------------------------------

        painter.setPen(
            QColor(235, 220, 255, 130)
        )

        font = QFont()

        font.setPointSize(18)

        painter.setFont(font)

        painter.drawText(
            rect.width() - 265,
            45,
            "♪"
        )

        painter.drawText(
            rect.width() - 180,
            90,
            "♫"
        )

        painter.drawText(
            rect.width() - 310,
            150,
            "♬"
        )

        painter.drawText(
            rect.width() - 125,
            180,
            "♪"
        )

        painter.end()