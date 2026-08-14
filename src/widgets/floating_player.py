from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)


class FloatingPlayer(QFrame):

    # ==================================================
    # SIGNALS
    # ==================================================

    previous_requested = Signal()
    next_requested = Signal()

    # ==================================================
    # INIT
    # ==================================================

    def __init__(self, parent=None):

        super().__init__(parent)

        self.current_image = ""
        self.current_title = ""
        self.current_artist = ""

        self.is_playing = True

        self.setObjectName(
            "FloatingPlayer"
        )

        self.setFixedHeight(
            82
        )

        self.setMinimumWidth(
            650
        )

        self.setMaximumWidth(
            950
        )

        self.setStyleSheet(
            """
            QFrame#FloatingPlayer {

                background: #171127;

                border: 1px solid #3B2860;

                border-radius: 20px;
            }

            QLabel {

                background: transparent;
            }

            QPushButton {

                background: transparent;

                border: none;

                color: #B9ADD6;

                font-size: 18px;

                border-radius: 12px;
            }

            QPushButton:hover {

                background: #2A1D45;

                color: white;
            }

            QPushButton#playButton {

                background: #7C3AED;

                color: white;

                font-size: 19px;

                font-weight: 700;

                border-radius: 22px;
            }

            QPushButton#playButton:hover {

                background: #8B5CF6;
            }

            QPushButton#favoriteButton {

                font-size: 19px;
            }

            QLabel#songTitle {

                color: white;

                font-size: 14px;

                font-weight: 700;
            }

            QLabel#artistName {

                color: #9E94B9;

                font-size: 12px;
            }
            """
        )

        self.build_ui()

        self.hide()

    # ==================================================
    # BUILD UI
    # ==================================================

    def build_ui(self):

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            12,
            10,
            14,
            10
        )

        layout.setSpacing(
            12
        )

        # ==================================================
        # ALBUM ART
        # ==================================================

        self.cover = QLabel()

        self.cover.setFixedSize(
            58,
            58
        )

        self.cover.setAlignment(
            Qt.AlignCenter
        )

        self.cover.setStyleSheet(
            """
            QLabel {

                background: #251A3A;

                border-radius: 12px;
            }
            """
        )

        layout.addWidget(
            self.cover
        )

        # ==================================================
        # SONG INFORMATION
        # ==================================================

        info = QVBoxLayout()

        info.setContentsMargins(
            0,
            4,
            0,
            4
        )

        info.setSpacing(
            3
        )

        self.song_title = QLabel(
            "Nothing Playing"
        )

        self.song_title.setObjectName(
            "songTitle"
        )

        self.artist_name = QLabel(
            "Select a song to start listening"
        )

        self.artist_name.setObjectName(
            "artistName"
        )

        info.addWidget(
            self.song_title
        )

        info.addWidget(
            self.artist_name
        )

        info.addStretch()

        layout.addLayout(
            info,
            1
        )

        # ==================================================
        # FAVORITE
        # ==================================================

        self.favorite_button = QPushButton(
            "♡"
        )

        self.favorite_button.setObjectName(
            "favoriteButton"
        )

        self.favorite_button.setFixedSize(
            38,
            38
        )

        layout.addWidget(
            self.favorite_button
        )

        # ==================================================
        # PREVIOUS
        # ==================================================

        self.previous_button = QPushButton(
            "⏮"
        )

        self.previous_button.setFixedSize(
            38,
            38
        )

        self.previous_button.clicked.connect(
            self.previous_requested.emit
        )

        layout.addWidget(
            self.previous_button
        )

        # ==================================================
        # PLAY / PAUSE
        # ==================================================

        self.play_button = QPushButton(
            "▶"
        )

        self.play_button.setObjectName(
            "playButton"
        )

        self.play_button.setFixedSize(
            44,
            44
        )

        self.play_button.clicked.connect(
            self.toggle_play
        )

        layout.addWidget(
            self.play_button
        )

        # ==================================================
        # NEXT
        # ==================================================

        self.next_button = QPushButton(
            "⏭"
        )

        self.next_button.setFixedSize(
            38,
            38
        )

        self.next_button.clicked.connect(
            self.next_requested.emit
        )

        layout.addWidget(
            self.next_button
        )

        # ==================================================
        # VOLUME
        # ==================================================

        self.volume_button = QPushButton(
            "🔊"
        )

        self.volume_button.setFixedSize(
            38,
            38
        )

        layout.addWidget(
            self.volume_button
        )

    # ==================================================
    # UPDATE SONG
    # ==================================================

    def update_song(
        self,
        image_path,
        title,
        artist
    ):

        self.current_image = image_path
        self.current_title = title
        self.current_artist = artist

        # --------------------------------------------------
        # Album art
        # --------------------------------------------------

        pixmap = QPixmap(
            str(image_path)
        )

        if not pixmap.isNull():

            self.cover.setPixmap(
                pixmap.scaled(
                    58,
                    58,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

        else:

            self.cover.clear()

        # --------------------------------------------------
        # Text
        # --------------------------------------------------

        self.song_title.setText(
            title
        )

        self.artist_name.setText(
            artist
        )

        # --------------------------------------------------
        # Start player
        # --------------------------------------------------

        self.is_playing = True

        self.play_button.setText(
            "Ⅱ"
        )

        self.show()

        self.raise_()

    # ==================================================
    # PLAY / PAUSE
    # ==================================================

    def toggle_play(self):

        self.is_playing = not self.is_playing

        if self.is_playing:

            self.play_button.setText(
                "Ⅱ"
            )

        else:

            self.play_button.setText(
                "▶"
            )