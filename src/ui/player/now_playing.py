from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
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
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QScrollArea,
    QFrame,
    QSizePolicy,
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
# DEFAULT ART
# ============================================================

DEFAULT_ART = find_asset(
    "assets/album_art/believer.jpg"
)


# ============================================================
# NOW PLAYING
# ============================================================

class NowPlaying(QWidget):

    def __init__(self):

        super().__init__()

        self.setObjectName(
            "NowPlaying"
        )

        self.setMinimumWidth(
            310
        )

        self.setMaximumWidth(
            350
        )

        self.setMinimumHeight(
            620
        )

        self.is_playing = False
        self.is_shuffle = False
        self.is_repeat = False

        self.build_ui()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        root = QVBoxLayout(self)

        root.setContentsMargins(
            18,
            18,
            18,
            18
        )

        root.setSpacing(
            12
        )

        # ====================================================
        # TOP HEADER
        # ====================================================

        header = QHBoxLayout()

        header.setContentsMargins(
            2,
            0,
            2,
            0
        )

        heading = QLabel(
            "NOW PLAYING"
        )

        heading.setStyleSheet("""
        QLabel {

            color: #CDBEFF;

            font-size: 12px;

            font-weight: 700;

            letter-spacing: 1px;

            background: transparent;

        }
        """)

        header.addWidget(
            heading
        )

        header.addStretch()

        live = QLabel(
            "●  LIVE"
        )

        live.setStyleSheet("""
        QLabel {

            color: #9B7AFF;

            font-size: 10px;

            font-weight: 700;

            background: transparent;

        }
        """)

        header.addWidget(
            live
        )

        root.addLayout(
            header
        )

        # ====================================================
        # ALBUM ART
        # ====================================================

        self.album_frame = QFrame()

        self.album_frame.setFixedSize(
            238,
            238
        )

        self.album_frame.setObjectName(
            "AlbumFrame"
        )

        self.album_frame.setStyleSheet("""
        QFrame#AlbumFrame {

            background: #211633;

            border: 1px solid rgba(139,92,246,80);

            border-radius: 22px;

        }
        """)

        album_layout = QVBoxLayout(
            self.album_frame
        )

        album_layout.setContentsMargins(
            3,
            3,
            3,
            3
        )

        album_layout.setSpacing(
            0
        )

        self.album = QLabel()

        self.album.setFixedSize(
            232,
            232
        )

        self.album.setAlignment(
            Qt.AlignCenter
        )

        self.album.setStyleSheet("""
        QLabel {

            background: #211633;

            border-radius: 19px;

        }
        """)

        if DEFAULT_ART:

            pix = QPixmap(
                str(DEFAULT_ART)
            )

            if not pix.isNull():

                self.album.setPixmap(
                    pix.scaled(
                        232,
                        232,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

        album_layout.addWidget(
            self.album
        )

        root.addWidget(
            self.album_frame,
            alignment=Qt.AlignCenter
        )

        # ====================================================
        # SONG INFO
        # ====================================================

        self.song = QLabel(
            "Believer"
        )

        self.song.setAlignment(
            Qt.AlignCenter
        )

        self.song.setStyleSheet("""
        QLabel {

            color: white;

            font-size: 19px;

            font-weight: 700;

            background: transparent;

        }
        """)

        root.addWidget(
            self.song
        )

        self.artist = QLabel(
            "Imagine Dragons"
        )

        self.artist.setAlignment(
            Qt.AlignCenter
        )

        self.artist.setStyleSheet("""
        QLabel {

            color: #AFA3CF;

            font-size: 13px;

            background: transparent;

        }
        """)

        root.addWidget(
            self.artist
        )

        # ====================================================
        # PROGRESS
        # ====================================================

        self.slider = QSlider(
            Qt.Horizontal
        )

        self.slider.setRange(
            0,
            100
        )

        self.slider.setValue(
            35
        )

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

        root.addWidget(
            self.slider
        )

        # ====================================================
        # TIME
        # ====================================================

        time_layout = QHBoxLayout()

        current = QLabel(
            "1:24"
        )

        total = QLabel(
            "3:45"
        )

        for label in (
            current,
            total
        ):

            label.setStyleSheet("""
            QLabel {

                color: #82779F;

                font-size: 10px;

                background: transparent;

            }
            """)

        time_layout.addWidget(
            current
        )

        time_layout.addStretch()

        time_layout.addWidget(
            total
        )

        root.addLayout(
            time_layout
        )

        # ====================================================
        # PLAYER CONTROLS
        # ====================================================

        controls = QHBoxLayout()

        controls.setSpacing(
            8
        )

        controls.setAlignment(
            Qt.AlignCenter
        )

        self.shuffle_btn = self.create_control_button(
            "⤨",
            38
        )

        self.prev_btn = self.create_control_button(
            "⏮",
            40
        )

        self.play_btn = self.create_control_button(
            "▶",
            54,
            primary=True
        )

        self.next_btn = self.create_control_button(
            "⏭",
            40
        )

        self.repeat_btn = self.create_control_button(
            "↻",
            38
        )

        controls.addWidget(
            self.shuffle_btn
        )

        controls.addWidget(
            self.prev_btn
        )

        controls.addWidget(
            self.play_btn
        )

        controls.addWidget(
            self.next_btn
        )

        controls.addWidget(
            self.repeat_btn
        )

        root.addLayout(
            controls
        )

        # ====================================================
        # CONTROL SIGNALS
        # ====================================================

        self.play_btn.clicked.connect(
            self.toggle_play
        )

        self.shuffle_btn.clicked.connect(
            self.toggle_shuffle
        )

        self.repeat_btn.clicked.connect(
            self.toggle_repeat
        )

        # ====================================================
        # VOLUME
        # ====================================================

        volume_layout = QHBoxLayout()

        volume_layout.setSpacing(
            8
        )

        volume_icon = QLabel(
            "🔊"
        )

        volume_icon.setFixedWidth(
            22
        )

        volume_icon.setAlignment(
            Qt.AlignCenter
        )

        volume_icon.setStyleSheet("""
        QLabel {

            color: #BBADE0;

            font-size: 14px;

            background: transparent;

        }
        """)

        self.volume_slider = QSlider(
            Qt.Horizontal
        )

        self.volume_slider.setRange(
            0,
            100
        )

        self.volume_slider.setValue(
            75
        )

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

        volume_layout.addWidget(
            volume_icon
        )

        volume_layout.addWidget(
            self.volume_slider
        )

        root.addLayout(
            volume_layout
        )

        # ====================================================
        # DIVIDER
        # ====================================================

        divider = QFrame()

        divider.setFixedHeight(
            1
        )

        divider.setStyleSheet("""
        QFrame {

            background: rgba(255,255,255,15);

        }
        """)

        root.addWidget(
            divider
        )

        # ====================================================
        # NEXT UP HEADER
        # ====================================================

        next_header = QHBoxLayout()

        next_title = QLabel(
            "NEXT UP"
        )

        next_title.setStyleSheet("""
        QLabel {

            color: #CDBEFF;

            font-size: 12px;

            font-weight: 700;

            letter-spacing: 1px;

            background: transparent;

        }
        """)

        next_header.addWidget(
            next_title
        )

        next_header.addStretch()

        queue_count = QLabel(
            "3 songs"
        )

        queue_count.setStyleSheet("""
        QLabel {

            color: #756A91;

            font-size: 10px;

            background: transparent;

        }
        """)

        next_header.addWidget(
            queue_count
        )

        root.addLayout(
            next_header
        )

        # ====================================================
        # NEXT UP SCROLL
        # ====================================================

        self.next_scroll = QScrollArea()

        self.next_scroll.setWidgetResizable(
            True
        )

        self.next_scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.next_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.next_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

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

        next_content.setStyleSheet("""
        QWidget {

            background: transparent;

        }
        """)

        next_layout = QVBoxLayout(
            next_content
        )

        next_layout.setContentsMargins(
            0,
            0,
            4,
            4
        )

        next_layout.setSpacing(
            7
        )

        next_songs = [

            (
                "assets/album_art/faded.jpg",
                "Faded",
                "Alan Walker",
                "3:32"
            ),

            (
                "assets/album_art/arcade.jpg",
                "Arcade",
                "Duncan Laurence",
                "3:05"
            ),

            (
                "assets/album_art/lethergo.jpg",
                "Let Her Go",
                "Passenger",
                "4:12"
            ),

            (
                "assets/album_art/believer.jpg",
                "Thunder",
                "Imagine Dragons",
                "3:07"
            ),

            (
                "assets/album_art/faded.jpg",
                "On My Way",
                "Alan Walker",
                "3:37"
            ),

        ]

        for (
            image_path,
            title,
            artist,
            duration
        ) in next_songs:

            item = self.create_next_song(
                image_path,
                title,
                artist,
                duration
            )

            next_layout.addWidget(
                item
            )

        next_layout.addStretch()

        self.next_scroll.setWidget(
            next_content
        )

        self.next_scroll.setMinimumHeight(
            135
        )

        self.next_scroll.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.next_scroll,
            1
        )

    # ========================================================
    # CONTROL BUTTON
    # ========================================================

    def create_control_button(
        self,
        text,
        size,
        primary=False
    ):

        button = QPushButton(
            text
        )

        button.setFixedSize(
            size,
            size
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

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

    def create_next_song(
        self,
        image_path,
        title,
        artist,
        duration
    ):

        item = QFrame()

        item.setFixedHeight(
            58
        )

        item.setObjectName(
            "NextSong"
        )

        item.setStyleSheet("""
        QFrame#NextSong {

            background: rgba(255,255,255,5);

            border: 1px solid transparent;

            border-radius: 12px;

        }

        QFrame#NextSong:hover {

            background: rgba(139,92,246,20);

            border: 1px solid rgba(139,92,246,55);

        }
        """)

        layout = QHBoxLayout(
            item
        )

        layout.setContentsMargins(
            7,
            6,
            8,
            6
        )

        layout.setSpacing(
            9
        )

        # ----------------------------------------------------
        # THUMBNAIL
        # ----------------------------------------------------

        thumb = QLabel()

        thumb.setFixedSize(
            46,
            46
        )

        thumb.setAlignment(
            Qt.AlignCenter
        )

        thumb.setStyleSheet("""
        QLabel {

            background: #24183D;

            border-radius: 9px;

        }
        """)

        image = find_asset(
            image_path
        )

        if image:

            pix = QPixmap(
                str(image)
            )

            if not pix.isNull():

                thumb.setPixmap(
                    pix.scaled(
                        46,
                        46,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

        layout.addWidget(
            thumb
        )

        # ----------------------------------------------------
        # SONG TEXT
        # ----------------------------------------------------

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        text_layout.setSpacing(
            1
        )

        song_title = QLabel(
            title
        )

        song_title.setStyleSheet("""
        QLabel {

            color: white;

            font-size: 12px;

            font-weight: 600;

            background: transparent;

        }
        """)

        song_artist = QLabel(
            artist
        )

        song_artist.setStyleSheet("""
        QLabel {

            color: #81779B;

            font-size: 10px;

            background: transparent;

        }
        """)

        text_layout.addWidget(
            song_title
        )

        text_layout.addWidget(
            song_artist
        )

        layout.addLayout(
            text_layout,
            1
        )

        # ----------------------------------------------------
        # DURATION
        # ----------------------------------------------------

        duration_label = QLabel(
            duration
        )

        duration_label.setStyleSheet("""
        QLabel {

            color: #756A91;

            font-size: 9px;

            background: transparent;

        }
        """)

        layout.addWidget(
            duration_label
        )

        return item

    # ========================================================
    # PLAY / PAUSE
    # ========================================================

    def toggle_play(self):

        self.is_playing = not self.is_playing

        if self.is_playing:

            self.play_btn.setText(
                "Ⅱ"
            )

        else:

            self.play_btn.setText(
                "▶"
            )

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

    # ========================================================
    # PAINT
    # ========================================================

    def paintEvent(self, event):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        path = QPainterPath()

        path.addRoundedRect(
            rect.adjusted(
                1,
                1,
                -1,
                -1
            ),
            24,
            24
        )

        # ----------------------------------------------------
        # BACKGROUND
        # ----------------------------------------------------

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#171125")
        )

        gradient.setColorAt(
            0.50,
            QColor("#211532")
        )

        gradient.setColorAt(
            1.0,
            QColor("#100C19")
        )

        painter.fillPath(
            path,
            gradient
        )

        # ----------------------------------------------------
        # BORDER
        # ----------------------------------------------------

        pen = QPen(
            QColor(
                139,
                92,
                246,
                85
            )
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

        # ----------------------------------------------------
        # AMBIENT GLOW
        # ----------------------------------------------------

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                139,
                92,
                246,
                28
            )
        )

        painter.drawEllipse(
            rect.width() - 130,
            -35,
            160,
            160
        )

        painter.setBrush(
            QColor(
                168,
                85,
                247,
                14
            )
        )

        painter.drawEllipse(
            -35,
            rect.height() - 100,
            120,
            120
        )

        painter.end()

        super().paintEvent(
            event
        )