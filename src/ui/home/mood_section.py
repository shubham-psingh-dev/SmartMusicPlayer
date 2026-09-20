from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QSizePolicy,
)


class MoodCard(QFrame):

    clicked = Signal(str)

    def __init__(
        self,
        mood_name,
        icon,
        subtitle
    ):

        super().__init__()

        self.mood_name = mood_name

        self.setObjectName(
            "MoodCard"
        )

        self.setFixedHeight(
            86
        )

        self.setMinimumWidth(
            105
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setStyleSheet("""
        QFrame#MoodCard {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:1,

                stop:0 #211638,
                stop:0.55 #181127,
                stop:1 #120D1E
            );

            border: 1px solid rgba(139,92,246,55);

            border-radius: 16px;
        }

        QFrame#MoodCard:hover {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:1,

                stop:0 #38205F,
                stop:0.55 #24143D,
                stop:1 #171022
            );

            border: 1px solid rgba(167,120,255,150);
        }
        """)

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            10,
            8,
            10,
            8
        )

        layout.setSpacing(
            2
        )

        # ==================================================
        # ICON
        # ==================================================

        icon_label = QLabel(
            icon
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setStyleSheet("""
        QLabel {

            color: #DCCBFF;

            background: transparent;

            font-size: 21px;

        }
        """)

        # ==================================================
        # MOOD NAME
        # ==================================================

        name_label = QLabel(
            mood_name
        )

        name_label.setAlignment(
            Qt.AlignCenter
        )

        name_label.setStyleSheet("""
        QLabel {

            color: white;

            background: transparent;

            font-size: 12px;

            font-weight: 700;

        }
        """)

        # ==================================================
        # SUBTITLE
        # ==================================================

        subtitle_label = QLabel(
            subtitle
        )

        subtitle_label.setAlignment(
            Qt.AlignCenter
        )

        subtitle_label.setStyleSheet("""
        QLabel {

            color: #8F83AA;

            background: transparent;

            font-size: 9px;

        }
        """)

        layout.addWidget(
            icon_label
        )

        layout.addWidget(
            name_label
        )

        layout.addWidget(
            subtitle_label
        )

    def mousePressEvent(
        self,
        event
    ):

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self.mood_name
            )

        super().mousePressEvent(
            event
        )


class MoodSection(QWidget):

    mood_selected = Signal(str)
    see_all_clicked = Signal()

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.build_ui()

    # ==================================================
    # BUILD UI
    # ==================================================

    def build_ui(self):

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)

        title = QLabel("Your Vibe")
        title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 23px;
            font-weight: 700;
            background: transparent;
        }
        """)
        header.addWidget(title)
        header.addStretch()

        self.see_all = QLabel("See All  →")
        self.see_all.setCursor(Qt.PointingHandCursor)
        self.see_all.setStyleSheet("""
        QLabel {
            color: #A978FF;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        }
        QLabel:hover { color: #D0B7FF; }
        """)
        header.addWidget(self.see_all)
        root.addLayout(header)

        # First six remain exactly the familiar Home row.
        self.primary_moods = [
            ("Chill", "🌙", "Relax & unwind"),
            ("Focus", "🎧", "Stay productive"),
            ("Happy", "☀️", "Good vibes"),
            ("Workout", "⚡", "Power up"),
            ("Sleep", "✨", "Drift away"),
            ("Rainy Day", "🌧️", "Cozy moments"),
        ]

        # Day 29: real additional moods revealed by See All.
        self.extra_moods = [
            ("Romantic", "💜", "Love songs"),
            ("Party", "🎉", "Turn it up"),
            ("Travel", "🚗", "Road trip"),
            ("Acoustic", "🎸", "Unplug & breathe"),
            ("Motivation", "🔥", "Feel unstoppable"),
            ("Peaceful", "🕊️", "Slow & calm"),
        ]

        self.primary_row = self._build_mood_row(self.primary_moods)
        root.addLayout(self.primary_row)

        self.extra_container = QWidget()
        self.extra_container.setAttribute(Qt.WA_TranslucentBackground)
        extra_row = QHBoxLayout(self.extra_container)
        extra_row.setContentsMargins(0, 0, 0, 0)
        extra_row.setSpacing(12)
        self._populate_row(extra_row, self.extra_moods)
        self.extra_container.hide()
        root.addWidget(self.extra_container)

        self.see_all.mousePressEvent = self.handle_see_all

    def _build_mood_row(self, moods):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        self._populate_row(row, moods)
        return row

    def _populate_row(self, row, moods):
        for mood_name, icon, subtitle in moods:
            card = MoodCard(mood_name, icon, subtitle)
            card.clicked.connect(self.mood_selected.emit)
            row.addWidget(card)

    def handle_see_all(self, event):
        if event.button() != Qt.LeftButton:
            return

        expanded = not self.extra_container.isVisible()
        self.extra_container.setVisible(expanded)
        self.see_all.setText("Show Less  ↑" if expanded else "See All  →")
        self.see_all_clicked.emit()
