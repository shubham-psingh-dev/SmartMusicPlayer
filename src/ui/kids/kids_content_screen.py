from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QGridLayout, QSizePolicy, QLineEdit
)

from services.provider_registry import ProviderRegistry
from ui.kids.kids_catalog import KIDS_SECTIONS, matches_kids_section, playable_url
from ui.kids.kids_parental import KidsParentalControls
from ui.kids.kids_favorites import KidsFavoritesStore


class KidsCatalogWorker(QThread):
    loaded = Signal(list, str)
    failed = Signal(str)

    def __init__(self, route, limit=24, query="", parent=None):
        super().__init__(parent)
        self.route = route
        self.limit = limit
        self.query = query.strip()

    def run(self):
        section = KIDS_SECTIONS[self.route]
        controls = KidsParentalControls()
        try:
            if self.query and not controls.query_allowed(self.query):
                self.failed.emit("Safe Search blocked this query in Kids Mode.")
                return

            registry = ProviderRegistry()
            if not registry.has_available_provider():
                self.failed.emit("No online provider is available.")
                return

            queries = (
                (f"{self.query} kids {section.queries[0]}",)
                if self.query else section.queries
            )
            songs, seen = [], set()

            for query in queries:
                result = registry.search(query, limit=max(30, self.limit * 2))
                for song in list(getattr(result, "songs", []) or []):
                    if not matches_kids_section(song, self.route):
                        continue
                    url = playable_url(song)
                    if not url:
                        continue
                    key = str(
                        getattr(song, "id", "")
                        or f"{getattr(song,'title','')}|{getattr(song,'artist','')}"
                    ).lower()
                    if not key or key in seen:
                        continue
                    seen.add(key)
                    try:
                        song.audio_url = url
                    except Exception:
                        pass
                    songs.append(song)
                    if len(songs) >= self.limit:
                        break
                if len(songs) >= self.limit:
                    break

            self.loaded.emit(songs, self.query)
        except Exception as exc:
            self.failed.emit(str(exc))


class KidsTrackCard(QFrame):
    play_requested = Signal(object)
    favorite_changed = Signal(object, bool)

    def __init__(self, song, parent=None):
        super().__init__(parent)
        self.song = song
        self.store = KidsFavoritesStore()
        self.setObjectName("KidsTrackCard")
        self.setFixedHeight(178)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        box = QVBoxLayout(self)
        box.setContentsMargins(12, 11, 12, 11)
        box.setSpacing(6)

        top = QHBoxLayout()
        art = QLabel("♫")
        art.setAlignment(Qt.AlignCenter)
        art.setFixedHeight(60)
        art.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        art.setStyleSheet(
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #2D266C,stop:1 #41318B);border:1px solid #5749AA;"
            "border-radius:13px;color:#C7BBFF;font-size:28px;font-weight:900;"
        )

        self.heart = QPushButton()
        self.heart.setObjectName("KidsHeart")
        self.heart.setFixedSize(36, 36)
        self.heart.setCursor(Qt.PointingHandCursor)
        self.heart.clicked.connect(self._toggle_favorite)
        top.addWidget(art, 1)
        top.addWidget(self.heart)
        box.addLayout(top)

        title_text = str(getattr(song, "title", "") or "Unknown Track")
        title = QLabel()
        title.setFixedHeight(20)
        title.setToolTip(title_text)
        title.setStyleSheet("color:white;font-size:11px;font-weight:900;")
        title.setText(title.fontMetrics().elidedText(title_text, Qt.ElideRight, 220))

        artist_text = str(getattr(song, "artist", "") or "Unknown Artist")
        artist = QLabel()
        artist.setFixedHeight(18)
        artist.setToolTip(artist_text)
        artist.setStyleSheet("color:#AFA9D9;font-size:9px;")
        artist.setText(artist.fontMetrics().elidedText(artist_text, Qt.ElideRight, 220))

        play = QPushButton("▶  Play")
        play.setObjectName("KidsPlay")
        play.setFixedHeight(31)
        play.setCursor(Qt.PointingHandCursor)
        play.clicked.connect(lambda: self.play_requested.emit(self.song))

        box.addWidget(title)
        box.addWidget(artist)
        box.addWidget(play)
        self._sync_heart()

        self.setStyleSheet("""
            QFrame#KidsTrackCard {
                background:#171342;border:1px solid #302A66;border-radius:17px;
            }
            QFrame#KidsTrackCard:hover {
                background:#1C1749;border-color:#6554C8;
            }
            QPushButton#KidsPlay {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #6247E8,stop:1 #8A4EF0);
                color:white;border:none;border-radius:10px;
                font-size:10px;font-weight:900;
            }
            QPushButton#KidsPlay:hover { background:#8A62F4; }
            QPushButton#KidsHeart {
                color:#E9E4FF;background:#28205F;border:1px solid #51449A;
                border-radius:12px;font-size:16px;font-weight:900;
            }
            QPushButton#KidsHeart:hover { background:#51358B; }
        """)

    def _sync_heart(self):
        saved = self.store.contains(self.song)
        self.heart.setText("♥" if saved else "♡")
        self.heart.setToolTip(
            "Remove from Kids Favorites" if saved else "Add to Kids Favorites"
        )
        self.heart.setStyleSheet(
            "color:#FF8DCE;" if saved else "color:#E9E4FF;"
        )

    def _toggle_favorite(self):
        saved = self.store.toggle(self.song)
        self._sync_heart()
        self.favorite_changed.emit(self.song, saved)


class KidsContentScreen(QWidget):
    back_requested = Signal()
    song_requested = Signal(object, list)

    def __init__(self, route, parent=None):
        super().__init__(parent)
        self.route = route
        self.section = KIDS_SECTIONS[route]
        self.songs = []
        self.worker = None
        self.build()

    def build(self):
        self.setStyleSheet("background:#0D0A2B;")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 22)
        root.setSpacing(11)

        top = QHBoxLayout()
        back = QPushButton("←  Kids Home")
        back.setFixedHeight(36)
        back.clicked.connect(self.back_requested.emit)
        back.setStyleSheet(
            "QPushButton{color:white;background:#21185A;border:1px solid #6048D8;"
            "border-radius:12px;padding:0 14px;font-weight:800;}"
        )
        safe = QLabel("🛡  KIDS DISCOVERY")
        safe.setStyleSheet(
            "color:#72F1CF;background:#102B38;border:1px solid #176D68;"
            "border-radius:12px;padding:8px 12px;font-size:9px;font-weight:900;"
        )
        top.addWidget(back)
        top.addStretch()
        top.addWidget(safe)
        root.addLayout(top)

        heading = QLabel(f"{self.section.emoji}  {self.section.title}")
        heading.setStyleSheet("color:white;font-size:27px;font-weight:950;")
        desc = QLabel(self.section.description)
        desc.setStyleSheet("color:#B8B2E2;font-size:11px;")
        root.addWidget(heading)
        root.addWidget(desc)

        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(f"Search inside {self.section.title}…")
        self.search.setClearButtonEnabled(True)
        self.search.setFixedHeight(42)
        self.search.returnPressed.connect(self.search_now)
        self.search.setStyleSheet(
            "QLineEdit{color:white;background:#171342;border:1px solid #403681;"
            "border-radius:13px;padding:0 14px;font-size:11px;}"
        )
        search_button = QPushButton("⌕  Search")
        search_button.setFixedHeight(42)
        search_button.clicked.connect(self.search_now)
        search_button.setStyleSheet(
            "QPushButton{color:white;background:#6D4DEB;border:none;"
            "border-radius:13px;padding:0 16px;font-weight:850;}"
        )
        search_row.addWidget(self.search, 1)
        search_row.addWidget(search_button)
        root.addLayout(search_row)

        action_row = QHBoxLayout()
        self.status = QLabel("Ready")
        self.status.setStyleSheet("color:#AAA4D6;font-size:9px;")
        refresh = QPushButton("↻  Refresh")
        refresh.clicked.connect(self.load_content)
        action_row.addWidget(self.status)
        action_row.addStretch()
        action_row.addWidget(refresh)
        root.addLayout(action_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.body = QWidget()
        self.grid = QGridLayout(self.body)
        self.grid.setSpacing(12)
        scroll.setWidget(self.body)
        root.addWidget(scroll, 1)
        self.message("Loading child-oriented results…")

    def clear(self):
        while self.grid.count():
            widget = self.grid.takeAt(0).widget()
            if widget:
                widget.deleteLater()

    def message(self, text):
        self.clear()
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("color:#8F89B7;padding:45px;")
        self.grid.addWidget(label, 0, 0, 1, 4)

    def search_now(self):
        self.load_content(self.search.text().strip())

    def load_content(self, query=""):
        if isinstance(query, bool):
            query = ""
        if self.worker and self.worker.isRunning():
            return
        self.status.setText("Finding child-oriented playable content…")
        self.message("✨  Searching LYRx providers…")
        self.worker = KidsCatalogWorker(self.route, 24, query, self)
        self.worker.loaded.connect(self.show_songs)
        self.worker.failed.connect(self.show_error)
        self.worker.start()

    def show_songs(self, songs, query):
        self.clear()
        self.songs = list(songs or [])
        if not self.songs:
            self.status.setText("No matching Kids results")
            self.message("No child-oriented playable results matched this search.")
            return

        self.status.setText(f"{len(self.songs)} playable Kids results")
        for i, song in enumerate(self.songs):
            card = KidsTrackCard(song, self.body)
            card.play_requested.connect(
                lambda s, q=self.songs: self.song_requested.emit(s, list(q))
            )
            row, col = divmod(i, 4)
            self.grid.addWidget(card, row, col)

    def show_error(self, error):
        self.status.setText("Could not load content")
        self.message(str(error))
