from pathlib import Path

from PySide6.QtCore import Qt, Signal, QUrl, QTimer

from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
)

from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSlider, QScrollArea, QFrame, QSizePolicy
)


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()
PROJECT_DIR = FILE_DIR.parents[3]
SRC_DIR = FILE_DIR.parents[2]


# ============================================================
# ASSET HELPER
# ============================================================

def find_asset(relative_path):
    candidates = [
        PROJECT_DIR / relative_path,
        SRC_DIR / relative_path,
        Path.cwd() / relative_path,
        Path(relative_path),
    ]

    for path in candidates:
        try:
            if path.exists() and path.is_file():
                return path
        except Exception:
            pass

    return None


# ============================================================
# TIME FORMATTER
# ============================================================

def format_duration(milliseconds):
    if milliseconds is None or milliseconds <= 0:
        return "0:00"

    total_seconds = milliseconds // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


# ============================================================
# NEXT SONG DURATION PROBE
# ============================================================

class DurationProbe:

    def __init__(self, parent):
        self.parent = parent
        self.players = []

    def load(self, audio_file, callback):
        player = QMediaPlayer(self.parent)

        player.durationChanged.connect(
            lambda duration, p=player, cb=callback: self.handle_duration(
                p, duration, cb
            )
        )

        player.setSource(
            QUrl.fromLocalFile(str(audio_file.resolve()))
        )

        self.players.append(player)

    def handle_duration(self, player, duration, callback):
        if duration <= 0:
            return

        # The Next Up widget can be rebuilt before this metadata callback
        # arrives. Never let a stale QLabel crash the application.
        try:
            callback(format_duration(duration))
        except RuntimeError:
            pass
        except Exception:
            pass

        # The metadata has been read; this probe no longer needs to stay alive.
        try:
            self.players.remove(player)
        except ValueError:
            pass

        try:
            player.stop()
            player.deleteLater()
        except RuntimeError:
            pass


# ============================================================
# NOW PLAYING
# ============================================================

class NowPlaying(QWidget):

    next_requested = Signal()
    previous_requested = Signal()
    next_song_requested = Signal(str, str, str)
    song_finished = Signal()

    # Signals used by AppWindow to keep the floating player in sync.
    song_changed = Signal(str, str, str)
    play_state_changed = Signal(bool)
    progress_changed = Signal(int, str, str)

    # DAY 19 - sends the already-decoded album cover to other UI players.
    cover_pixmap_changed = Signal(object)

    def __init__(self):
        super().__init__()

        self.setObjectName("NowPlaying")
        self.setMinimumWidth(310)
        self.setMaximumWidth(350)
        self.setMinimumHeight(620)

        # ========================================================
        # PLAYER STATE
        # ========================================================

        self.is_playing = False
        self.is_shuffle = False
        self.is_repeat = False

        self.current_image_path = ""
        self.current_title = ""
        self.current_artist = ""

        self.queue = []
        self.queue_index = 0

        # ========================================================
        # DAY 19 - ONLINE QUEUE STATE
        # ========================================================

        self.online_queue = []

        self.online_queue_index = 0

        self.playback_source = "local"

        self.current_online_song = None

        # ========================================================
        # DAY 19 - ONLINE STREAM SAFETY
        # ========================================================

        # Some remote Jamendo streams can take a moment before the
        # Qt multimedia backend is ready. Keep enough state to retry
        # the same stream once without breaking the queue/UI.
        self.online_stream_url = ""
        self.online_autoplay_pending = False
        self.online_retry_count = 0
        self.online_retry_limit = 1
        self.current_online_duration_seconds = 0

        # ========================================================
        # AUDIO PLAYER
        # ========================================================

        self.audio_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.audio_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.75)

        # ========================================================
        # ONLINE COVER ART NETWORK MANAGER
        # ========================================================

        self.cover_network = QNetworkAccessManager(
            self
        )

        self.cover_reply = None

        # Multiple remote Next Up thumbnails can load at the same time.
        self.thumbnail_replies = []

        # ========================================================
        # DURATION PROBE
        # ========================================================

        self.duration_probe = DurationProbe(self)

        # ========================================================
        # PLAYER SIGNALS
        # ========================================================

        self.audio_player.positionChanged.connect(self.update_progress)
        self.audio_player.durationChanged.connect(self.update_duration)
        self.audio_player.mediaStatusChanged.connect(self.handle_media_status)
        self.audio_player.playbackStateChanged.connect(
            self.handle_playback_state
        )
        self.audio_player.errorOccurred.connect(
            self.handle_player_error
        )

        self.build_ui()

        self.slider.sliderMoved.connect(self.seek_audio)
        self.volume_slider.valueChanged.connect(self.change_volume)

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # ====================================================
        # TOP HEADER
        # ====================================================

        header = QHBoxLayout()
        header.setContentsMargins(2, 0, 2, 0)

        heading = QLabel("NOW PLAYING")
        heading.setStyleSheet("""
        QLabel {
            color: #CDBEFF;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
        }
        """)
        header.addWidget(heading)
        header.addStretch()

        live = QLabel("●  LIVE")
        live.setStyleSheet("""
        QLabel {
            color: #9B7AFF;
            font-size: 10px;
            font-weight: 700;
            background: transparent;
        }
        """)
        header.addWidget(live)
        root.addLayout(header)

        # ====================================================
        # ALBUM ART
        # ====================================================

        self.album_frame = QFrame()
        self.album_frame.setFixedSize(238, 238)
        self.album_frame.setObjectName("AlbumFrame")
        self.album_frame.setStyleSheet("""
        QFrame#AlbumFrame {
            background: #211633;
            border: 1px solid rgba(139,92,246,80);
            border-radius: 22px;
        }
        """)

        album_layout = QVBoxLayout(self.album_frame)
        album_layout.setContentsMargins(3, 3, 3, 3)
        album_layout.setSpacing(0)

        self.album = QLabel()
        self.album.setFixedSize(232, 232)
        self.album.setAlignment(Qt.AlignCenter)
        self.album.setStyleSheet("""
        QLabel {
            background: #211633;
            border-radius: 19px;
        }
        """)

        default_art = find_asset("assets/album_art/believer.jpg")
        if default_art:
            pix = QPixmap(str(default_art))
            if not pix.isNull():
                scaled_local_cover = pix.scaled(
                    232,
                    232,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                self.album.setPixmap(
                    scaled_local_cover
                )

                self.cover_pixmap_changed.emit(
                    scaled_local_cover
                )

        album_layout.addWidget(self.album)
        root.addWidget(self.album_frame, alignment=Qt.AlignCenter)

        # ====================================================
        # SONG INFO
        # ====================================================

        self.song = QLabel("Believer")
        self.song.setAlignment(Qt.AlignCenter)
        self.song.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 19px;
            font-weight: 700;
            background: transparent;
        }
        """)
        root.addWidget(self.song)

        self.artist = QLabel("Imagine Dragons")
        self.artist.setAlignment(Qt.AlignCenter)
        self.artist.setStyleSheet("""
        QLabel {
            color: #AFA3CF;
            font-size: 13px;
            background: transparent;
        }
        """)
        root.addWidget(self.artist)

        # ====================================================
        # PROGRESS
        # ====================================================

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 4px;
            background: #3C305A;
            border-radius: 2px;
        }
        QSlider::sub-page:horizontal {
            background: #8B5CF6;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            width: 12px;
            height: 12px;
            margin: -4px 0;
            border-radius: 6px;
            background: white;
        }
        QSlider::handle:horizontal:hover {
            background: #B58AFF;
        }
        """)
        root.addWidget(self.slider)

        # ====================================================
        # TIME
        # ====================================================

        time_layout = QHBoxLayout()
        self.current_time = QLabel("0:00")
        self.total_time = QLabel("0:00")

        for label in (self.current_time, self.total_time):
            label.setStyleSheet("""
            QLabel {
                color: #82779F;
                font-size: 10px;
                background: transparent;
            }
            """)

        time_layout.addWidget(self.current_time)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time)
        root.addLayout(time_layout)

        # ====================================================
        # CONTROLS
        # ====================================================

        controls = QHBoxLayout()
        controls.setSpacing(8)
        controls.setAlignment(Qt.AlignCenter)

        self.shuffle_btn = self.create_control_button("⤨", 38)
        self.prev_btn = self.create_control_button("⏮", 40)
        self.play_btn = self.create_control_button("▶", 54, primary=True)
        self.next_btn = self.create_control_button("⏭", 40)
        self.repeat_btn = self.create_control_button("↻", 38)

        controls.addWidget(self.shuffle_btn)
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.next_btn)
        controls.addWidget(self.repeat_btn)
        root.addLayout(controls)

        self.play_btn.clicked.connect(self.toggle_play)
        self.prev_btn.clicked.connect(self.previous_requested.emit)
        self.next_btn.clicked.connect(self.next_requested.emit)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.repeat_btn.clicked.connect(self.toggle_repeat)

        # ====================================================
        # VOLUME
        # ====================================================

        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(8)

        volume_icon = QLabel("🔊")
        volume_icon.setFixedWidth(22)
        volume_icon.setAlignment(Qt.AlignCenter)
        volume_icon.setStyleSheet("""
        QLabel {
            color: #BBADE0;
            font-size: 14px;
            background: transparent;
        }
        """)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 3px;
            background: #3C305A;
            border-radius: 2px;
        }
        QSlider::sub-page:horizontal {
            background: #7250C9;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            width: 10px;
            height: 10px;
            margin: -4px 0;
            border-radius: 5px;
            background: #D8CCFF;
        }
        """)

        volume_layout.addWidget(volume_icon)
        volume_layout.addWidget(self.volume_slider)
        root.addLayout(volume_layout)

        # ====================================================
        # DIVIDER
        # ====================================================

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("""
        QFrame {
            background: rgba(255,255,255,15);
        }
        """)
        root.addWidget(divider)

        # ====================================================
        # NEXT UP HEADER
        # ====================================================

        next_header = QHBoxLayout()

        next_title = QLabel("NEXT UP")
        next_title.setStyleSheet("""
        QLabel {
            color: #CDBEFF;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
        }
        """)
        next_header.addWidget(next_title)
        next_header.addStretch()

        self.queue_count = QLabel("0 songs")
        self.queue_count.setStyleSheet("""
        QLabel {
            color: #756A91;
            font-size: 10px;
            background: transparent;
        }
        """)
        next_header.addWidget(self.queue_count)
        root.addLayout(next_header)

        # ====================================================
        # NEXT UP SCROLL
        # ====================================================

        self.next_scroll = QScrollArea()
        self.next_scroll.setWidgetResizable(True)
        self.next_scroll.setFrameShape(QFrame.NoFrame)
        self.next_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.next_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.next_scroll.setStyleSheet("""
        QScrollArea {
            background: transparent;
            border: none;
        }
        QScrollArea > QWidget > QWidget {
            background: transparent;
        }
        QScrollBar:vertical {
            width: 6px;
            background: transparent;
        }
        QScrollBar::handle:vertical {
            background: #6243A6;
            border-radius: 3px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #8B5CF6;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }
        """)

        next_content = QWidget()
        next_content.setStyleSheet("QWidget { background: transparent; }")

        next_layout = QVBoxLayout(next_content)
        next_layout.setContentsMargins(0, 0, 4, 4)
        next_layout.setSpacing(7)
        next_layout.addStretch()

        self.next_scroll.setWidget(next_content)
        self.next_scroll.setMinimumHeight(135)
        self.next_scroll.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        root.addWidget(self.next_scroll, 1)

    # ========================================================
    # SET QUEUE
    # ========================================================

    def set_queue(self, queue):
        self.queue = list(queue)
        self.refresh_next_up()

    # ========================================================
    # SET ONLINE QUEUE
    # ========================================================

    def set_online_queue(
        self,
        songs,
        current_song=None
    ):

        self.online_queue = list(
            songs or []
        )

        # ----------------------------------------------------
        # EMPTY
        # ----------------------------------------------------

        if not self.online_queue:

            self.online_queue_index = 0

            return

        # ----------------------------------------------------
        # FIND CURRENT SONG
        # ----------------------------------------------------

        if current_song is not None:

            current_id = str(
                getattr(
                    current_song,
                    "id",
                    ""
                )
            )

            found_index = None

            for index, song in enumerate(
                self.online_queue
            ):

                song_id = str(
                    getattr(
                        song,
                        "id",
                        ""
                    )
                )

                if (
                    current_id
                    and song_id
                    and current_id == song_id
                ):

                    found_index = index

                    break

            if found_index is not None:

                self.online_queue_index = (
                    found_index
                )

        self.playback_source = "online"

        self.refresh_next_up()


    # ========================================================
    # SET ONLINE INDEX
    # ========================================================

    def set_online_index(
        self,
        index
    ):

        if not self.online_queue:

            self.online_queue_index = 0

            return

        index = max(
            0,
            min(
                int(index),
                len(self.online_queue) - 1
            )
        )

        self.online_queue_index = index

        self.refresh_next_up()


    # ========================================================
    # ONLINE NEXT
    # ========================================================

    def play_online_next(self):

        if not self.online_queue:

            return

        total = len(
            self.online_queue
        )

        # ----------------------------------------------------
        # SHUFFLE
        # ----------------------------------------------------

        if self.is_shuffle:

            if total == 1:

                new_index = (
                    self.online_queue_index
                )

            else:

                import random

                indexes = [

                    index

                    for index in range(total)

                    if index
                    != self.online_queue_index
                ]

                new_index = random.choice(
                    indexes
                )

        # ----------------------------------------------------
        # NORMAL
        # ----------------------------------------------------

        else:

            new_index = (
                self.online_queue_index + 1
            ) % total

        self.online_queue_index = (
            new_index
        )

        song = self.online_queue[
            self.online_queue_index
        ]

        self.update_online_song(
            song,
            preserve_queue=True
        )

    # ========================================================
    # ONLINE PREVIOUS
    # ========================================================

    def play_online_previous(self):

        if not self.online_queue:

            return

        self.online_queue_index -= 1

        if self.online_queue_index < 0:

            self.online_queue_index = (
                len(self.online_queue) - 1
            )

        song = self.online_queue[
            self.online_queue_index
        ]

        self.update_online_song(
            song,
            preserve_queue=True
        )

    # ========================================================
    # SET CURRENT QUEUE INDEX
    # ========================================================

    def set_current_index(self, index):
        if not self.queue:
            self.queue_index = 0
            return

        index = max(0, min(index, len(self.queue) - 1))
        self.queue_index = index
        self.refresh_next_up()

    # ========================================================
    # REFRESH NEXT UP
    # ========================================================

    def refresh_next_up(self):

        if not hasattr(
            self,
            "next_scroll"
        ):

            return

        content = QWidget()

        content.setStyleSheet(
            "QWidget { background: transparent; }"
        )

        layout = QVBoxLayout(
            content
        )

        layout.setContentsMargins(
            0,
            0,
            4,
            4
        )

        layout.setSpacing(
            7
        )

        # ====================================================
        # ONLINE QUEUE
        # ====================================================

        if (
            self.playback_source == "online"
            and self.online_queue
        ):

            total = len(
                self.online_queue
            )

            for offset in range(
                1,
                total
            ):

                index = (
                    self.online_queue_index
                    + offset
                ) % total

                song = self.online_queue[
                    index
                ]

                layout.addWidget(
                    self.create_online_next_song(
                        song
                    )
                )

            remaining = max(
                0,
                total - 1
            )

        # ====================================================
        # LOCAL QUEUE
        # ====================================================

        elif self.queue:

            total = len(
                self.queue
            )

            for offset in range(
                1,
                total
            ):

                index = (
                    self.queue_index
                    + offset
                ) % total

                (
                    image_path,
                    title,
                    artist
                ) = self.queue[
                    index
                ]

                layout.addWidget(
                    self.create_next_song(
                        image_path,
                        title,
                        artist
                    )
                )

            remaining = max(
                0,
                total - 1
            )

        # ====================================================
        # EMPTY
        # ====================================================

        else:

            empty = QLabel(
                "No songs in queue"
            )

            empty.setStyleSheet(
                """
                QLabel {
                    color: #756A91;
                    font-size: 11px;
                    background: transparent;
                    padding: 12px;
                }
                """
            )

            layout.addWidget(
                empty
            )

            remaining = 0

        layout.addStretch()

        self.next_scroll.setWidget(
            content
        )

        self.queue_count.setText(
            f"{remaining} "
            f"{'song' if remaining == 1 else 'songs'}"
        )

    # ========================================================
    # CONTROL BUTTON
    # ========================================================

    def create_control_button(self, text, size, primary=False):
        button = QPushButton(text)
        button.setFixedSize(size, size)
        button.setCursor(Qt.PointingHandCursor)

        if primary:
            button.setStyleSheet("""
            QPushButton {
                background: #8B5CF6;
                color: white;
                border: 2px solid rgba(255,255,255,40);
                border-radius: 27px;
                font-size: 19px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #A970FF;
            }
            QPushButton:pressed {
                background: #6D28D9;
            }
            """)
        else:
            button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #AFA3CF;
                border: none;
                border-radius: 19px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(139,92,246,35);
                color: white;
            }
            QPushButton:pressed {
                background: rgba(139,92,246,70);
                color: white;
            }
            """)

        return button

    # ========================================================
    # NEXT SONG ITEM
    # ========================================================

    def create_next_song(self, image_path, title, artist):
        item = QFrame()
        item.setFixedHeight(58)
        item.setObjectName("NextSong")
        item.setStyleSheet("""
        QFrame#NextSong {
            background: rgba(255,255,255,5);
            border: 1px solid transparent;
            border-radius: 12px;
        }
        QFrame#NextSong:hover {
            background: rgba(139,58,246,20);
            border: 1px solid rgba(139,92,246,55);
        }
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(7, 6, 8, 6)
        layout.setSpacing(9)

        # ====================================================
        # THUMBNAIL
        # ====================================================

        thumb = QLabel()
        thumb.setFixedSize(46, 46)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setStyleSheet("""
        QLabel {
            background: #24183D;
            border-radius: 9px;
        }
        """)

        image = find_asset(image_path)
        if image:
            pix = QPixmap(str(image))
            if not pix.isNull():
                thumb.setPixmap(
                    pix.scaled(
                        46, 46,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

        layout.addWidget(thumb)

        # ====================================================
        # SONG TEXT
        # ====================================================

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        song_title = QLabel(title)
        song_title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        }
        """)

        song_artist = QLabel(artist)
        song_artist.setStyleSheet("""
        QLabel {
            color: #81779B;
            font-size: 10px;
            background: transparent;
        }
        """)

        text_layout.addWidget(song_title)
        text_layout.addWidget(song_artist)
        layout.addLayout(text_layout, 1)

        # ====================================================
        # DURATION
        # ====================================================

        duration_label = QLabel("Loading...")
        duration_label.setStyleSheet("""
        QLabel {
            color: #756A91;
            font-size: 9px;
            background: transparent;
        }
        """)
        layout.addWidget(duration_label)

        # ====================================================
        # LOAD ACTUAL MP3 DURATION
        # ====================================================

        music_path = image_path.replace(
            "assets/album_art/",
            "assets/music/"
        )
        music_path = str(Path(music_path).with_suffix(".mp3"))
        audio_file = find_asset(music_path)

        if audio_file:

            def update_duration_label(duration):
                try:
                    duration_label.setText(duration)
                except RuntimeError:
                    # This item may already have been removed by refresh_next_up().
                    pass
                except Exception:
                    pass

            self.duration_probe.load(
                audio_file,
                update_duration_label
            )

        else:
            duration_label.setText("0:00")
            print(
                "Next Up audio not found:",
                music_path
            )

        # ====================================================
        # CLICK
        # ====================================================

        item.mousePressEvent = lambda event: (
            self.next_song_requested.emit(
                image_path,
                title,
                artist
            )
        )

        return item

    # ========================================================
    # ONLINE NEXT SONG ITEM
    # ========================================================

    def create_online_next_song(
        self,
        song
    ):

        item = QFrame()
        item.setFixedHeight(58)
        item.setObjectName("NextSong")
        item.setStyleSheet("""
        QFrame#NextSong {
            background: rgba(255,255,255,5);
            border: 1px solid transparent;
            border-radius: 12px;
        }
        QFrame#NextSong:hover {
            background: rgba(139,58,246,20);
            border: 1px solid rgba(139,92,246,55);
        }
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(7, 6, 8, 6)
        layout.setSpacing(9)

        # ONLINE THUMBNAIL
        thumb = QLabel("♫")
        thumb.setFixedSize(46, 46)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setScaledContents(False)
        thumb.setStyleSheet("""
        QLabel {
            background: #24183D;
            color: #A970FF;
            border-radius: 9px;
            font-size: 19px;
        }
        """)
        layout.addWidget(thumb)

        image_url = str(getattr(song, "image_url", "") or "").strip()
        if image_url:
            self.load_online_thumbnail(image_url, thumb)

        # TEXT
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        title = QLabel(song.display_title())
        title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        }
        """)

        artist = QLabel(song.display_artist())
        artist.setStyleSheet("""
        QLabel {
            color: #81779B;
            font-size: 10px;
            background: transparent;
        }
        """)

        text_layout.addWidget(title)
        text_layout.addWidget(artist)
        layout.addLayout(text_layout, 1)

        duration = QLabel(song.duration_text())
        duration.setStyleSheet("""
        QLabel {
            color: #756A91;
            font-size: 9px;
            background: transparent;
        }
        """)
        layout.addWidget(duration)

        item.mousePressEvent = (
            lambda event, selected_song=song:
            self.update_online_song(selected_song, preserve_queue=True)
        )

        return item

    # ========================================================
    # LOAD ONLINE NEXT-UP THUMBNAIL
    # ========================================================

    def load_online_thumbnail(self, image_url, label):

        image_url = str(image_url or "").strip()
        if not image_url:
            return

        url = QUrl(image_url)
        if not url.isValid():
            print("Invalid Next Up cover URL:", image_url)
            return

        request = QNetworkRequest(url)
        request.setRawHeader(b"User-Agent", b"LYRx-Music-Player/0.2")

        reply = self.cover_network.get(request)
        self.thumbnail_replies.append(reply)

        reply.finished.connect(
            lambda r=reply, target=label:
            self.online_thumbnail_loaded(r, target)
        )

    # ========================================================
    # ONLINE NEXT-UP THUMBNAIL LOADED
    # ========================================================

    def online_thumbnail_loaded(self, reply, label):

        try:
            raw_data = bytes(reply.readAll())
            pixmap = QPixmap()

            if not pixmap.loadFromData(raw_data):
                return

            scaled = pixmap.scaled(
                46, 46,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            label.clear()
            label.setPixmap(scaled)

        except RuntimeError:
            pass
        except Exception as error:
            print("Next Up online cover error:", error)
        finally:
            try:
                self.thumbnail_replies.remove(reply)
            except (ValueError, RuntimeError):
                pass
            try:
                reply.deleteLater()
            except RuntimeError:
                pass

    # ========================================================
    # LOAD ONLINE COVER
    # ========================================================

    def load_online_cover(
        self,
        image_url
    ):

        image_url = str(
            image_url or ""
        ).strip()

        if not image_url:

            self.album.clear()

            self.album.setText(
                "♫"
            )

            return

        # ----------------------------------------------------
        # CANCEL OLD REQUEST
        # ----------------------------------------------------

        try:

            if (
                self.cover_reply is not None
                and
                self.cover_reply.isRunning()
            ):

                self.cover_reply.abort()

        except Exception:

            pass

        # ----------------------------------------------------
        # REQUEST
        # ----------------------------------------------------

        request = QNetworkRequest(
            QUrl(
                image_url
            )
        )

        request.setRawHeader(
            b"User-Agent",
            b"LYRx-Music-Player/0.2"
        )

        self.cover_reply = (
            self.cover_network.get(
                request
            )
        )

        self.cover_reply.finished.connect(
            self.online_cover_loaded
        )


    # ========================================================
    # ONLINE COVER LOADED
    # ========================================================

    def online_cover_loaded(self):

        reply = self.sender()

        if reply is None:

            return

        try:

            data = reply.readAll()

            pixmap = QPixmap()

            loaded = pixmap.loadFromData(
                bytes(data)
            )

            if loaded:

                scaled = pixmap.scaled(
                    232,
                    232,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                self.album.setText("")

                self.album.setPixmap(
                    scaled
                )

                self.cover_pixmap_changed.emit(
                    scaled
                )

            else:

                self.album.clear()

                self.album.setText(
                    "♫"
                )

        except Exception as error:

            print(
                "Online cover load error:",
                error
            )

        finally:

            try:

                reply.deleteLater()

            except Exception:

                pass

            if reply is self.cover_reply:

                self.cover_reply = None

    # ========================================================
    # UPDATE ONLINE SONG
    # ========================================================

    def update_online_song(
        self,
        song,
        preserve_queue=False
    ):

        if song is None:

            return

        # ====================================================
        # ONLINE MODE
        # ====================================================

        self.playback_source = "online"

        self.current_online_song = song

        # ====================================================
        # BASIC DATA
        # ====================================================

        title = str(
            getattr(
                song,
                "title",
                ""
            )
            or "Unknown Track"
        )

        artist = str(
            getattr(
                song,
                "artist",
                ""
            )
            or "Unknown Artist"
        )

        image_url = str(
            getattr(
                song,
                "image_url",
                ""
            )
            or ""
        )

        # ====================================================
        # DAY 21 - UNIFIED ONLINE PLAYABLE URL
        # ====================================================
        #
        # Jamendo songs normally expose:
        #     song.audio_url
        #
        # iTunes songs normally expose:
        #     song.preview_url
        #
        # Provider Song objects may expose:
        #     song.playable_url()
        #
        # IMPORTANT:
        # A song clicked directly in Discover was already normalized
        # by AppWindow. Songs selected later from Next Up / Next /
        # Previous were not, so iTunes queue items could have an
        # empty audio_url even though preview_url was valid. Resolve
        # the playable source here as the final playback boundary.
        # ====================================================

        audio_url = ""

        try:

            if hasattr(
                song,
                "playable_url"
            ):

                audio_url = str(
                    song.playable_url()
                    or ""
                ).strip()

        except Exception as error:

            print(
                "NowPlaying playable URL resolve error:",
                error
            )

            audio_url = ""

        if not audio_url:

            audio_url = str(
                getattr(
                    song,
                    "audio_url",
                    ""
                )
                or
                getattr(
                    song,
                    "preview_url",
                    ""
                )
                or
                ""
            ).strip()

        # Keep the currently selected queue item compatible with
        # the older Day 19 playback layer.
        if audio_url:

            try:

                song.audio_url = (
                    audio_url
                )

            except Exception:

                pass

        duration_seconds = int(
            getattr(
                song,
                "duration",
                0
            )
            or 0
        )

        self.current_online_duration_seconds = (
            duration_seconds
        )

        # A newly selected track gets a fresh retry budget.
        self.online_retry_count = 0

        # ====================================================
        # SYNC ONLINE QUEUE INDEX
        # ====================================================

        if self.online_queue:

            song_id = str(
                getattr(
                    song,
                    "id",
                    ""
                )
            )

            for index, queue_song in enumerate(
                self.online_queue
            ):

                queue_id = str(
                    getattr(
                        queue_song,
                        "id",
                        ""
                    )
                )

                if (
                    song_id
                    and queue_id
                    and song_id == queue_id
                ):

                    self.online_queue_index = index

                    break

        # ====================================================
        # VALIDATE AUDIO
        # ====================================================

        if not audio_url:

            print(
                "Online song has no audio URL:",
                title
            )

            return

        print()
        print("=" * 60)

        print(
            "LYRx ONLINE PLAY"
        )

        print(
            "Title:",
            title
        )

        print(
            "Artist:",
            artist
        )

        print(
            "Audio:",
            audio_url
        )

        print("=" * 60)
        print()

        # ====================================================
        # STOP CURRENT SONG
        # ====================================================

        self.audio_player.stop()

        # ====================================================
        # CURRENT STATE
        # ====================================================

        self.current_image_path = (
            image_url
        )

        self.current_title = (
            title
        )

        self.current_artist = (
            artist
        )

        # ====================================================
        # UI
        # ====================================================

        self.song.setText(
            title
        )

        self.artist.setText(
            artist
        )

        # ====================================================
        # COVER
        # ====================================================

        self.album.clear()

        self.album.setText(
            "♫"
        )

        self.load_online_cover(
            image_url
        )

        # ====================================================
        # RESET PROGRESS
        # ====================================================

        self.slider.blockSignals(
            True
        )

        self.slider.setValue(
            0
        )

        self.slider.blockSignals(
            False
        )

        self.current_time.setText(
            "0:00"
        )

        # ----------------------------------------------------
        # API duration can be shown immediately
        # ----------------------------------------------------

        if duration_seconds > 0:

            minutes = (
                duration_seconds
                // 60
            )

            seconds = (
                duration_seconds
                % 60
            )

            self.total_time.setText(
                f"{minutes}:"
                f"{seconds:02d}"
            )

        else:

            self.total_time.setText(
                "0:00"
            )

        # ====================================================
        # FLOATING PLAYER SYNC
        # ====================================================

        self.song_changed.emit(
            image_url,
            title,
            artist
        )

        # ====================================================
        # ONLINE STREAM
        # ====================================================

        media_url = QUrl(
            audio_url
        )

        if not media_url.isValid():

            print(
                "Invalid online audio URL:",
                audio_url
            )

            return

        # ====================================================
        # SAFE ONLINE START
        # ====================================================

        self.start_online_stream(
            audio_url
        )

        self.refresh_next_up()

        print(
            "LYRx streaming request:",
            title,
            "-",
            artist
        )

    # ========================================================
    # START ONLINE STREAM
    # ========================================================

    def start_online_stream(
        self,
        audio_url
    ):

        audio_url = str(
            audio_url or ""
        ).strip()

        if not audio_url:

            return

        media_url = QUrl(
            audio_url
        )

        if not media_url.isValid():

            print(
                "Invalid online audio URL:",
                audio_url
            )

            return

        self.online_stream_url = (
            audio_url
        )

        self.online_autoplay_pending = (
            True
        )

        # Clear the previous source first. This helps Windows/Qt release
        # the previous remote decoder before opening another HTTP stream.
        self.audio_player.stop()

        self.audio_player.setSource(
            QUrl()
        )

        QTimer.singleShot(
            80,
            lambda url=media_url:
            self._set_online_source(
                url
            )
        )

    # ========================================================
    # SET ONLINE SOURCE
    # ========================================================

    def _set_online_source(
        self,
        media_url
    ):

        if (
            self.playback_source
            != "online"
        ):

            return

        self.audio_player.setSource(
            media_url
        )

        # Do not rely only on immediate play(). Some Windows multimedia
        # backends need a short event-loop cycle after setSource().
        QTimer.singleShot(
            140,
            self._play_online_source
        )

    # ========================================================
    # PLAY ONLINE SOURCE
    # ========================================================

    def _play_online_source(self):

        if (
            self.playback_source
            != "online"
        ):

            return

        if not self.online_autoplay_pending:

            return

        if self.audio_player.source().isEmpty():

            return

        self.audio_player.play()

    # ========================================================
    # RETRY ONLINE STREAM
    # ========================================================

    def retry_online_stream(self):

        if (
            self.playback_source
            != "online"
        ):

            return

        if not self.online_stream_url:

            return

        print(
            "Retrying online stream:",
            self.current_title
        )

        self.online_autoplay_pending = (
            True
        )

        media_url = QUrl(
            self.online_stream_url
        )

        self.audio_player.stop()

        self.audio_player.setSource(
            QUrl()
        )

        QTimer.singleShot(
            300,
            lambda url=media_url:
            self._set_online_source(
                url
            )
        )

    # ========================================================
    # PLAYER ERROR
    # ========================================================

    def handle_player_error(
        self,
        error,
        error_string=""
    ):

        # NoError can also be emitted while the backend resets.
        if (
            error
            == QMediaPlayer.Error.NoError
        ):

            return

        message = str(
            error_string or ""
        ).strip()

        print()
        print("=" * 60)
        print("LYRx PLAYER ERROR")
        print(
            "Source:",
            self.playback_source
        )
        print(
            "Song:",
            self.current_title
        )
        print(
            "Error:",
            error
        )
        print(
            "Message:",
            message
            if message
            else "No backend message"
        )
        print("=" * 60)
        print()

        if (
            self.playback_source == "online"
            and self.online_stream_url
            and self.online_retry_count
            < self.online_retry_limit
        ):

            self.online_retry_count += 1

            QTimer.singleShot(
                250,
                self.retry_online_stream
            )

            return

        self.online_autoplay_pending = (
            False
        )

        self.is_playing = False

        self.play_btn.setText(
            "▶"
        )

        self.play_state_changed.emit(
            False
        )

    # ========================================================
    # PLAYBACK STATE
    # ========================================================

    def handle_playback_state(
        self,
        state
    ):

        playing = (
            state
            == QMediaPlayer.PlaybackState.PlayingState
        )

        self.is_playing = (
            playing
        )

        self.play_btn.setText(
            "Ⅱ"
            if playing
            else "▶"
        )

        if playing:

            self.online_autoplay_pending = (
                False
            )

            self.online_retry_count = 0

        self.play_state_changed.emit(
            playing
        )

    # ========================================================
    # UPDATE SONG
    # ========================================================

    def update_song(
        self,
        image_path,
        title,
        artist
    ):

        self.playback_source = "local"

        self.current_online_song = None

        self.online_autoplay_pending = False
        self.online_stream_url = ""
        self.online_retry_count = 0
        self.current_online_duration_seconds = 0

        self.current_image_path = image_path
        self.current_title = title
        self.current_artist = artist

        self.audio_player.stop()

        self.song.setText(title)
        self.artist.setText(artist)

        image_file = find_asset(image_path)

        if image_file:
            pix = QPixmap(str(image_file))
            if not pix.isNull():
                self.album.setPixmap(
                    pix.scaled(
                        232, 232,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)

        self.current_time.setText("0:00")
        self.total_time.setText("0:00")

        # ====================================================
        # FLOATING PLAYER SYNC
        # ====================================================
        # Emit this before checking the MP3 path so the UI can still
        # reflect the selected song even if the audio file is missing.

        self.song_changed.emit(
            image_path,
            title,
            artist
        )

        # ====================================================
        # AUDIO FILE
        # ====================================================

        music_path = image_path.replace(
            "assets/album_art/",
            "assets/music/"
        )
        music_path = str(Path(music_path).with_suffix(".mp3"))
        audio_file = find_asset(music_path)

        if audio_file:
            self.audio_player.setSource(
                QUrl.fromLocalFile(
                    str(audio_file.resolve())
                )
            )

            self.audio_player.play()

            self.is_playing = True
            self.play_btn.setText("Ⅱ")
            self.play_state_changed.emit(True)
            self.refresh_next_up()

        else:
            self.is_playing = False
            self.play_btn.setText("▶")
            self.play_state_changed.emit(False)
            print(
                "Audio file not found:",
                music_path
            )

    # ========================================================
    # MEDIA STATUS
    # ========================================================

    def handle_media_status(
        self,
        status
    ):

        # ====================================================
        # ONLINE LOAD / BUFFER
        # ====================================================

        if (
            self.playback_source == "online"
            and self.online_autoplay_pending
            and status in (
                QMediaPlayer.MediaStatus.LoadedMedia,
                QMediaPlayer.MediaStatus.BufferedMedia,
            )
        ):

            self.audio_player.play()

        # ====================================================
        # INVALID MEDIA
        # ====================================================

        if (
            status
            == QMediaPlayer.MediaStatus.InvalidMedia
        ):

            print(
                "Invalid media:",
                self.current_title
            )

            return

        # ====================================================
        # END OF MEDIA
        # ====================================================

        if (
            status
            != QMediaPlayer.MediaStatus.EndOfMedia
        ):

            return

        print(
            "Song finished:",
            self.song.text()
        )

        self.song_finished.emit()

        if self.is_repeat:

            self.audio_player.setPosition(
                0
            )

            self.audio_player.play()

            return

        self.is_playing = False

        self.play_btn.setText(
            "▶"
        )

        self.play_state_changed.emit(
            False
        )

        # ====================================================
        # NEXT SONG BASED ON ACTIVE SOURCE
        # ====================================================

        if (
            self.playback_source == "online"
            and self.online_queue
        ):

            self.play_online_next()

        else:

            self.next_requested.emit()

    # ========================================================
    # PLAY / PAUSE
    # ========================================================

    def toggle_play(self):

        state = (
            self.audio_player
            .playbackState()
        )

        if (
            state
            == QMediaPlayer.PlaybackState.PlayingState
        ):

            self.online_autoplay_pending = (
                False
            )

            self.audio_player.pause()

        else:

            # If an online source failed to open and Qt has no active
            # source, rebuild it before trying Play again.
            if (
                self.playback_source == "online"
                and self.audio_player.source().isEmpty()
                and self.online_stream_url
            ):

                self.online_autoplay_pending = (
                    True
                )

                self.start_online_stream(
                    self.online_stream_url
                )

                return

            self.audio_player.play()

    # ========================================================
    # UPDATE DURATION
    # ========================================================

    def update_duration(
        self,
        duration
    ):

        if duration <= 0:

            # Remote streams can briefly report zero while opening.
            # Keep the duration supplied by the online catalog instead
            # of flashing back to 0:00.
            if (
                self.playback_source == "online"
                and self.current_online_duration_seconds > 0
            ):

                minutes = (
                    self.current_online_duration_seconds
                    // 60
                )

                seconds = (
                    self.current_online_duration_seconds
                    % 60
                )

                self.total_time.setText(
                    f"{minutes}:"
                    f"{seconds:02d}"
                )

                return

            self.total_time.setText(
                "0:00"
            )

            return

        self.total_time.setText(
            format_duration(
                duration
            )
        )

        self.slider.setRange(
            0,
            100
        )

    # ========================================================
    # UPDATE PROGRESS
    # ========================================================

    def update_progress(self, position):
        duration = self.audio_player.duration()

        if duration <= 0:
            return

        progress = int((position / duration) * 100)

        self.slider.blockSignals(True)
        self.slider.setValue(progress)
        self.slider.blockSignals(False)

        current = format_duration(position)
        total = format_duration(duration)

        self.current_time.setText(current)

        self.progress_changed.emit(
            progress,
            current,
            total
        )

    # ========================================================
    # SEEK AUDIO
    # ========================================================

    def seek_audio(self, value):
        duration = self.audio_player.duration()

        if duration <= 0:
            return

        position = int((value / 100) * duration)
        self.audio_player.setPosition(position)

    # ========================================================
    # VOLUME
    # ========================================================

    def change_volume(self, value):
        self.audio_output.setVolume(value / 100)

    # ========================================================
    # SHUFFLE
    # ========================================================

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle

        if self.is_shuffle:
            self.shuffle_btn.setStyleSheet("""
            QPushButton {
                background: rgba(139,92,246,65);
                color: #CDBEFF;
                border: 1px solid rgba(139,92,246,100);
                border-radius: 19px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(139,92,246,100);
                color: white;
            }
            """)
            print("Shuffle: ON")
        else:
            self.shuffle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #AFA3CF;
                border: none;
                border-radius: 19px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(139,92,246,35);
                color: white;
            }
            """)
            print("Shuffle: OFF")

    # ========================================================
    # REPEAT
    # ========================================================

    def toggle_repeat(self):
        self.is_repeat = not self.is_repeat

        if self.is_repeat:
            self.repeat_btn.setStyleSheet("""
            QPushButton {
                background: rgba(139,92,246,65);
                color: #CDBEFF;
                border: 1px solid rgba(139,92,246,100);
                border-radius: 19px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(139,92,246,100);
                color: white;
            }
            """)
            print("Repeat: ON")
        else:
            self.repeat_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #AFA3CF;
                border: none;
                border-radius: 19px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(139,92,246,35);
                color: white;
            }
            """)
            print("Repeat: OFF")

    # ========================================================
    # PAINT
    # ========================================================

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        path = QPainterPath()
        path.addRoundedRect(
            rect.adjusted(1, 1, -1, -1),
            24,
            24
        )

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        gradient.setColorAt(0.0, QColor("#171125"))
        gradient.setColorAt(0.50, QColor("#211532"))
        gradient.setColorAt(1.0, QColor("#100C19"))

        painter.fillPath(path, gradient)

        pen = QPen(
            QColor(139, 92, 246, 85)
        )
        pen.setWidth(1)

        painter.setPen(pen)
        painter.drawPath(path)

        painter.setPen(Qt.NoPen)
        painter.setBrush(
            QColor(139, 92, 246, 28)
        )
        painter.drawEllipse(
            rect.width() - 130,
            -35,
            160,
            160
        )

        painter.setBrush(
            QColor(168, 85, 247, 14)
        )
        painter.drawEllipse(
            -35,
            rect.height() - 100,
            120,
            120
        )

        painter.end()
        super().paintEvent(event)
