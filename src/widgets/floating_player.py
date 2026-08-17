from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)


class FloatingPlayer(QFrame):

    # ==================================================
    # SIGNALS
    # ==================================================

    previous_requested = Signal()
    next_requested = Signal()
    close_requested = Signal()

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
            /* ==================================================
               FLOATING PLAYER
            ================================================== */

            QFrame#FloatingPlayer {

                background: #171127;

                border: 1px solid #3B2860;

                border-radius: 20px;
            }


            /* ==================================================
               LABELS
            ================================================== */

            QLabel {

                background: transparent;

                border: none;
            }


            /* ==================================================
               NORMAL BUTTONS
            ================================================== */

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

            QPushButton:pressed {

                background: #3B2860;
            }


            /* ==================================================
               PLAY BUTTON
            ================================================== */

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

            QPushButton#playButton:pressed {

                background: #6D28D9;
            }


            /* ==================================================
               FAVORITE
            ================================================== */

            QPushButton#favoriteButton {

                font-size: 21px;

                color: #B9ADD6;
            }

            QPushButton#favoriteButton:hover {

                color: #F472B6;

                background: #2A1D45;
            }


            /* ==================================================
               CLOSE BUTTON
            ================================================== */

            QPushButton#floatingCloseButton {

                background: transparent;

                color: #8F84A8;

                border: 1px solid transparent;

                border-radius: 15px;

                font-family: "Segoe UI";

                font-size: 22px;

                font-weight: 400;

                padding: 0px;

                margin: 0px;
            }

            QPushButton#floatingCloseButton:hover {

                background: #7F1D3A;

                color: white;

                border: 1px solid #BE123C;
            }

            QPushButton#floatingCloseButton:pressed {

                background: #BE123C;

                color: white;
            }


            /* ==================================================
               SONG TITLE
            ================================================== */

            QLabel#songTitle {

                color: white;

                font-size: 14px;

                font-weight: 700;
            }


            /* ==================================================
               ARTIST
            ================================================== */

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
            10,
            10
        )

        layout.setSpacing(
            10
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

                border: none;

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

        self.favorite_button.setCursor(
            Qt.PointingHandCursor
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

        self.previous_button.setCursor(
            Qt.PointingHandCursor
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

        self.play_button.setCursor(
            Qt.PointingHandCursor
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

        self.next_button.setCursor(
            Qt.PointingHandCursor
        )

        self.next_button.clicked.connect(
            self.next_requested.emit
        )

        layout.addWidget(
            self.next_button
        )

        # ==================================================
        # CLOSE BUTTON
        # ==================================================

        self.close_button = QPushButton(
            "×"
        )

        self.close_button.setObjectName(
            "floatingCloseButton"
        )

        self.close_button.setFixedSize(
            32,
            32
        )

        self.close_button.setCursor(
            Qt.PointingHandCursor
        )

        self.close_button.setToolTip(
            "Close player"
        )

        self.close_button.clicked.connect(
            self.close_requested.emit
        )

        layout.addWidget(
            self.close_button
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

        # ==================================================
        # ALBUM ART
        # ==================================================

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

        # ==================================================
        # TEXT
        # ==================================================

        self.song_title.setText(
            title
        )

        self.artist_name.setText(
            artist
        )

        # ==================================================
        # PLAY STATE
        # ==================================================

        self.is_playing = True

        self.play_button.setText(
            "Ⅱ"
        )

        # ==================================================
        # SHOW
        # ==================================================

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

    # ==================================================
    # SET PLAYING
    # ==================================================

    def set_playing(
        self,
        playing
    ):

        self.is_playing = playing

        if playing:

            self.play_button.setText(
                "Ⅱ"
            )

        else:

            self.play_button.setText(
                "▶"
            )

    # ==================================================
    # CLOSE PLAYER
    # ==================================================

    def close_player(self):

        self.hide()

        self.close_requested.emit()