from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout
)

from ui.kids.kids_favorites import KidsFavoritesStore
from ui.kids.kids_content_screen import KidsTrackCard


class KidsFavoritesScreen(QWidget):
    back_requested = Signal()
    song_requested = Signal(object, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.store = KidsFavoritesStore()
        self.songs = []
        self._build()

    def _build(self):
        self.setStyleSheet("background:#0D0A2B;")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 22)
        root.setSpacing(12)

        top = QHBoxLayout()
        back = QPushButton("←  Kids Home")
        back.setFixedHeight(38)
        back.clicked.connect(self.back_requested.emit)
        back.setStyleSheet(
            "QPushButton{color:white;background:#21185A;border:1px solid #6048D8;"
            "border-radius:12px;padding:0 14px;font-weight:850;}"
        )
        badge = QLabel("💜  SAVED FOR KIDS")
        badge.setStyleSheet(
            "color:#F1B6FF;background:#291441;border:1px solid #713A88;"
            "border-radius:12px;padding:8px 12px;font-size:9px;font-weight:900;"
        )
        top.addWidget(back)
        top.addStretch()
        top.addWidget(badge)
        root.addLayout(top)

        title = QLabel("💜  Kids Favorites")
        title.setStyleSheet("color:white;font-size:28px;font-weight:950;")
        subtitle = QLabel("A separate, persistent favorites shelf just for Kids Mode.")
        subtitle.setStyleSheet("color:#B8B2E2;font-size:11px;")
        root.addWidget(title)
        root.addWidget(subtitle)

        self.status = QLabel()
        self.status.setStyleSheet("color:#AAA4D6;font-size:10px;")
        root.addWidget(self.status)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.body = QWidget()
        self.grid = QGridLayout(self.body)
        self.grid.setSpacing(12)
        scroll.setWidget(self.body)
        root.addWidget(scroll, 1)

    def refresh(self):
        while self.grid.count():
            widget = self.grid.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        self.songs = self.store.songs()
        if not self.songs:
            self.status.setText("No Kids favorites yet")
            empty = QLabel(
                "💜\n\nTap the heart on a Kids Music, Story, Rhyme or Spiritual card.\n"
                "Saved items will appear here."
            )
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                "color:#AFA8D7;background:#15113C;border:1px dashed #4A4086;"
                "border-radius:20px;padding:55px;font-size:12px;"
            )
            self.grid.addWidget(empty, 0, 0, 1, 4)
            return

        self.status.setText(f"{len(self.songs)} saved Kids favorite(s)")
        for i, song in enumerate(self.songs):
            card = KidsTrackCard(song, self.body)
            card.play_requested.connect(
                lambda s, q=self.songs: self.song_requested.emit(s, list(q))
            )
            card.favorite_changed.connect(lambda *_: self.refresh())
            row, col = divmod(i, 4)
            self.grid.addWidget(card, row, col)
