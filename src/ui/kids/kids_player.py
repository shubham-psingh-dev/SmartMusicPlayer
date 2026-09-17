from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider
)


def fmt(ms):
    sec = max(0, int(ms // 1000))
    return f"{sec//60}:{sec%60:02d}"


class KidsPlayerBar(QFrame):
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("KidsPlayerBar")
        self.queue = []
        self.index = -1

        self.audio = QAudioOutput(self)
        self.audio.setVolume(.75)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(10)

        icon = QLabel("🌟")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(48,48)
        icon.setStyleSheet("""
            background:qradialgradient(cx:.5,cy:.5,radius:.8,
                stop:0 #6E4DF0,stop:1 #261D65);
            border:1px solid #6F5BE0;border-radius:15px;font-size:24px;
        """)

        info = QVBoxLayout()
        info.setSpacing(2)
        self.title = QLabel("Nothing playing")
        self.title.setStyleSheet("color:white;font-size:12px;font-weight:900;")
        self.artist = QLabel("LYRx Kids")
        self.artist.setStyleSheet("color:#AAA4D6;font-size:9px;")
        info.addWidget(self.title)
        info.addWidget(self.artist)

        self.prev = QPushButton("◀")
        self.play = QPushButton("▶")
        self.next = QPushButton("▶|")
        for button in (self.prev,self.next):
            button.setObjectName("KidsTransport")
            button.setFixedSize(38,38)
            button.setCursor(Qt.PointingHandCursor)
        self.play.setObjectName("KidsPlay")
        self.play.setFixedSize(48,48)
        self.play.setCursor(Qt.PointingHandCursor)

        progress_box = QVBoxLayout()
        progress_box.setSpacing(2)
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0,0)
        times = QHBoxLayout()
        self.current = QLabel("0:00")
        self.duration = QLabel("0:00")
        for lab in (self.current,self.duration):
            lab.setStyleSheet("color:#8882B5;font-size:8px;")
        times.addWidget(self.current); times.addStretch(); times.addWidget(self.duration)
        progress_box.addWidget(self.progress)
        progress_box.addLayout(times)

        close = QPushButton("×")
        close.setObjectName("KidsClose")
        close.setFixedSize(34,34)
        close.setCursor(Qt.PointingHandCursor)

        root.addWidget(icon)
        root.addLayout(info, 1)
        root.addWidget(self.prev)
        root.addWidget(self.play)
        root.addWidget(self.next)
        root.addLayout(progress_box, 3)
        root.addWidget(close)

        self.play.clicked.connect(self.toggle)
        self.prev.clicked.connect(lambda:self.step(-1))
        self.next.clicked.connect(lambda:self.step(1))
        close.clicked.connect(self.close_player)
        self.progress.sliderMoved.connect(self.player.setPosition)
        self.player.positionChanged.connect(self._position)
        self.player.durationChanged.connect(self._duration)
        self.player.playbackStateChanged.connect(self._sync)

        self.setStyleSheet("""
            QFrame#KidsPlayerBar {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #100D31,stop:.5 #171043,stop:1 #100D31);
                border-top:1px solid #493C96;
            }
            QPushButton#KidsTransport {
                color:#EAE7FF;background:#2B2463;border:1px solid #41377F;
                border-radius:19px;font-size:12px;font-weight:900;
            }
            QPushButton#KidsTransport:hover { background:#45378E; }
            QPushButton#KidsPlay {
                color:white;
                background:qradialgradient(cx:.5,cy:.45,radius:.75,
                    stop:0 #B76CFF,stop:.55 #8051F4,stop:1 #5D36CE);
                border:1px solid #C18AFF;border-radius:24px;
                font-size:15px;font-weight:950;
            }
            QPushButton#KidsPlay:hover { border:2px solid white; }
            QPushButton#KidsClose {
                color:#FFD8E1;background:#51203A;border:1px solid #7B3555;
                border-radius:17px;font-size:20px;font-weight:900;
            }
            QPushButton#KidsClose:hover { background:#7A294C; }
            QSlider::groove:horizontal {
                height:5px;background:#342E62;border-radius:2px;
            }
            QSlider::sub-page:horizontal {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #7651F2,stop:1 #C064F7);border-radius:2px;
            }
            QSlider::handle:horizontal {
                background:white;width:11px;margin:-3px 0;border-radius:5px;
            }
        """)

    def url(self, song):
        try:
            fn = getattr(song,"playable_url",None)
            if callable(fn):
                u = str(fn() or "").strip()
                if u: return u
        except Exception:
            pass
        return str(
            getattr(song,"audio_url","")
            or getattr(song,"preview_url","")
            or ""
        ).strip()

    def play_song(self, song, queue):
        self.queue = list(queue or [song])
        try:
            self.index = self.queue.index(song)
        except ValueError:
            self.queue = [song]
            self.index = 0
        self.load(song)

    def load(self, song):
        u = self.url(song)
        if not u:
            return
        self.title.setText(str(getattr(song,"title","") or "Unknown Track"))
        self.artist.setText(str(getattr(song,"artist","") or "LYRx Kids"))
        self.player.setSource(QUrl.fromUserInput(u))
        self.player.play()

    def toggle(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def step(self, delta):
        if self.queue:
            self.index = (self.index + delta) % len(self.queue)
            self.load(self.queue[self.index])

    def _sync(self, state):
        self.play.setText(
            "Ⅱ" if state == QMediaPlayer.PlaybackState.PlayingState else "▶"
        )

    def _position(self, value):
        if not self.progress.isSliderDown():
            self.progress.setValue(value)
        self.current.setText(fmt(value))

    def _duration(self, value):
        self.progress.setRange(0, max(0,value))
        self.duration.setText(fmt(value))

    def close_player(self):
        self.player.stop()
        self.hide()
        self.closed.emit()

    def stop(self):
        self.player.stop()
