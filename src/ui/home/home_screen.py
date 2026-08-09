from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtGui import (
    QColor, 
    QLinearGradient, 
    QPainter,
    QPixmap,
)

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
)

from widgets.sidebar import Sidebar
from ui.home.header import Header
from ui.home.hero_banner import HeroBanner
from ui.home.mood_section import MoodSection
from widgets.cards.music_card import MusicCard
from ui.player.now_playing import NowPlaying


class HomeScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("🎵 LYRx")

        self.resize(1450, 900)

        self.setMinimumSize(1200, 720)

        self.build_ui()

    # ==================================================
    # BUILD UI
    # ==================================================

    def build_ui(self):

        # ==================================================
        # ROOT
        # ==================================================

        root = QHBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(0)

        # ==================================================
        # SIDEBAR
        # ==================================================

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        root.addWidget(self.sidebar)

        # ==================================================
        # MAIN AREA
        # ==================================================

        self.main = QWidget()

        self.main.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.main.setStyleSheet("""
        QWidget {
            background: transparent;
        }
        """)

        root.addWidget(
            self.main,
            1
        )

        self.main_layout = QHBoxLayout(
            self.main
        )

        self.main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.main_layout.setSpacing(0)


        # ==================================================
        # LEFT CONTENT AREA
        # ==================================================

        self.left = QWidget()

        self.left.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.left.setStyleSheet("""
        QWidget {
            background: transparent;
        }
        """)

        self.left.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.main_layout.addWidget(
            self.left,
            1
        )

        self.left_layout = QVBoxLayout(
            self.left
        )

        self.left_layout.setContentsMargins(
            28,
            22,
            22,
            22
        )

        self.left_layout.setSpacing(22)

        # ==================================================
        # RIGHT PLAYER AREA
        # ==================================================

        self.right_area = QWidget()

        self.right_area.setFixedWidth(330)

        self.right_area.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        self.main_layout.addWidget(
            self.right_area
        )

        self.right_layout = QVBoxLayout(
            self.right_area
        )

        self.right_layout.setContentsMargins(
            0,
            22,
            22,
            22
        )

        self.right_layout.setSpacing(18)

        # ==================================================
        # HEADER
        # ==================================================

        self.header = Header()

        self.header.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.left_layout.addWidget(
            self.header
        )

        # ==================================================
        # LEFT CONTENT SCROLL
        # ==================================================

        self.content_scroll = QScrollArea()

        self.content_scroll.setWidgetResizable(
            True
        )

        self.content_scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.content_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.content_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.content_scroll.setStyleSheet("""
        QScrollArea{

            background:transparent;

            border:none;

        }

        QScrollArea > QWidget > QWidget {
            background: transparent;

        }

        QScrollBar:vertical{

            width:9px;

            background:transparent;

            margin: 2px;

        }

        QScrollBar::handle:vertical{

            background:#7C3AED;

            border-radius:4px;

            min-height:55px;

        }

        QScrollBar::handle:vertical:hover{

            background:#9F67FF;

        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical{

            height:0px;

        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical{

            background:transparent;

        }
        """)

        self.left_layout.addWidget(
            self.content_scroll,
            1
        )

        # ==================================================
        # SCROLL CONTENT
        # ==================================================

        self.content = QWidget()

        self.content.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.content.setStyleSheet("""
        QWidget {
            background: transparent;
        }
        """)

        self.content.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.content_scroll.setWidget(
            self.content
        )

        self.content_layout = QVBoxLayout(
            self.content
        )

        self.content_layout.setContentsMargins(
            0,
            0,
            8,
            30
        )

        self.content_layout.setSpacing(
            24
        )

        self.content_layout.setAlignment(
            Qt.AlignTop
        )

        # ==================================================
        # HERO BANNER
        # ==================================================

        self.hero = HeroBanner()

        self.hero.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.content_layout.addWidget(
            self.hero
        )

        # ==================================================
        # RIGHT PANEL
        # ==================================================

        self.now_playing = NowPlaying()

        self.now_playing.previous_requested.connect(
            self.play_previous
        )

        self.now_playing.next_requested.connect(
            self.play_next
        )

        self.now_playing.next_song_requested.connect(
            self.play_selected_song
        )

        self.now_playing.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.right_layout.addWidget(
            self.now_playing
        )

        # ==================================================
        # RIGHT PANEL SPACER
        # ==================================================

        self.right_layout.addStretch()

        # ==================================================
        # RIGHT PANEL BACKGROUND
        # ==================================================

        self.right_area.setStyleSheet("""
        QWidget{

            background:transparent;

        }
        """)

        # ==================================================
        # CONTINUE LISTENING SECTION
        # ==================================================

        self.continue_header = QWidget()

        continue_header_layout = QHBoxLayout(
            self.continue_header
        )

        continue_header_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        continue_header_layout.setSpacing(10)

        self.continue_title = QLabel(
            "Continue Listening"
        )

        self.continue_title.setStyleSheet("""
        QLabel{

            color:white;

            font-size:24px;

            font-weight:700;

        }
        """)

        self.more_button = QLabel(
            "More  ›"
        )

        self.more_button.setAlignment(
            Qt.AlignRight |
            Qt.AlignVCenter
        )

        self.more_button.setStyleSheet("""
        QLabel{

            color:#9B7AFF;

            font-size:13px;

            font-weight:600;

        }
        """)

        continue_header_layout.addWidget(
            self.continue_title
        )

        continue_header_layout.addStretch()

        continue_header_layout.addWidget(
            self.more_button
        )

        self.content_layout.addWidget(
            self.continue_header
        )

        # ==================================================
        # MUSIC CARDS CONTAINER
        # ==================================================

        self.cards_container = QWidget()

        self.cards_container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.cards_layout = QHBoxLayout(
            self.cards_container
        )

        self.cards_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.cards_layout.setSpacing(
            16
        )

        self.content_layout.addWidget(
            self.cards_container
        )

        # ==================================================
        # MUSIC CARDS
        # ==================================================

        cards = [

            (
                "assets/album_art/believer.jpg",
                "Believer",
                "Imagine Dragons"
            ),

            (
                "assets/album_art/faded.jpg",
                "Faded",
                "Alan Walker"
            ),

            (
                "assets/album_art/arcade.jpg",
                "Arcade",
                "Duncan Laurence"
            ),

            (
                "assets/album_art/lethergo.jpg",
                "Let Her Go",
                "Passenger"
            ),

        ]

        for image_path, title, artist in cards:

            card = MusicCard(
                image_path,
                title,
                artist
            )

            card.setSizePolicy(
                QSizePolicy.Fixed,
                QSizePolicy.Fixed
            )

            card.play_requested.connect(
                self.handle_play_request
            )

            self.cards_layout.addWidget(
                card
            )

        self.cards_layout.addStretch()

        # ==================================================
        # PLAYER QUEUE
        # ==================================================

        self.player_queue = cards

        self.current_index = 0

        # ==================================================
        # YOUR VIBE / MOOD SECTION
        # ==================================================

        self.mood_section = MoodSection()

        self.mood_section.mood_selected.connect(
            self.handle_mood_selected
        )

        self.mood_section.see_all_clicked.connect(
            self.handle_mood_see_all
        )

        self.content_layout.addWidget(
            self.mood_section
        )

        # ==================================================
        # PLAYLIST SECTION
        # ==================================================

        playlist_header = QWidget()

        playlist_header_layout = QHBoxLayout(
            playlist_header
        )

        playlist_header_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        playlist_title = QLabel(
            "Playlists for You"
        )

        playlist_title.setStyleSheet("""
        QLabel{

            color:white;

            font-size:24px;

            font-weight:700;

        }
        """)

        playlist_more = QLabel(
            "View All  ›"
        )

        playlist_more.setStyleSheet("""
        QLabel{

            color:#9B7AFF;

            font-size:13px;

            font-weight:600;

        }
        """)

        playlist_header_layout.addWidget(
            playlist_title
        )

        playlist_header_layout.addStretch()

        playlist_header_layout.addWidget(
            playlist_more
        )

        self.content_layout.addWidget(
            playlist_header
        )

        # ==================================================
        # PLAYLIST CARDS
        # ==================================================

        playlist_container = QWidget()

        playlist_layout = QHBoxLayout(
            playlist_container
        )

        playlist_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        playlist_layout.setSpacing(
            16
        )

        playlists = [
            (
                "assets/album_art/believer.jpg",
                "Daily Mix"
            ),
            (
                "assets/album_art/faded.jpg",
                "Late Night"
            ),
            (
                "assets/album_art/arcade.jpg",
                "Emotional"
            ),
        ]

        for image_path, name in playlists:

            playlist = QFrame()

            playlist.setFixedHeight(
                105
            )

            playlist.setMinimumWidth(
                180
            )

            playlist.setStyleSheet("""
            QFrame{

                background:#191329;

                border:1px solid #30224B;

                border-radius:16px;

            }

            QFrame:hover{

                background:#24183D;

                border:1px solid #7048C7;

            }
            """)

            playlist_layout_inner = QHBoxLayout(
                playlist
            )

            playlist_layout_inner.setContentsMargins(
                10,
                10,
                10,
                10
            )

            cover = QLabel()

            cover.setFixedSize(
                78,
                78
            )

            pix = QPixmap(
                str(
                    Path(image_path)
                )
            )

            if not pix.isNull():

                cover.setPixmap(
                    pix.scaled(
                        78,
                        78,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

            cover.setStyleSheet("""
            QLabel{

                border-radius:12px;

                background:#251A3A;

            }
            """)

            playlist_name = QLabel(
                name
            )

            playlist_name.setWordWrap(
                True
            )

            playlist_name.setStyleSheet("""
            QLabel{

                color:white;

                font-size:14px;

                font-weight:600;

                background:transparent;

            }
            """)

            playlist_layout_inner.addWidget(
                cover
            )

            playlist_layout_inner.addWidget(
                playlist_name
            )

            playlist_layout_inner.addStretch()

            playlist_layout.addWidget(
                playlist
            )

        playlist_layout.addStretch()

        self.content_layout.addWidget(
            playlist_container
        )

        # ==================================================
        # BOTTOM SPACE
        # ==================================================

        self.content_layout.addSpacing(
            20
        )

        self.content_layout.addStretch()

    # ==================================================
    # HANDLE MUSIC CARD PLAY
    # ==================================================

    def handle_play_request(
        self,
        image_path,
        title,
        artist
    ):

        for index, song in enumerate(
            self.player_queue
        ):

            if song[0] == image_path:

                self.current_index = index
                break

        self.now_playing.update_song(
            image_path,
            title,
            artist
        )

    # ==================================================
    # PLAY NEXT
    # ==================================================

    def play_next(self):

        if not self.player_queue:
            return

        self.current_index += 1

        if self.current_index >= len(
            self.player_queue
        ):

            self.current_index = 0

        image_path, title, artist = (
            self.player_queue[
                self.current_index
            ]
        )

        self.now_playing.update_song(
            image_path,
            title,
            artist
        )

    # ==================================================
    # PLAY PREVIOUS
    # ==================================================

    def play_previous(self):

        if not self.player_queue:
            return

        self.current_index -= 1

        if self.current_index < 0:

            self.current_index = (
                len(self.player_queue) - 1
            )

        image_path, title, artist = (
            self.player_queue[
                self.current_index
            ]
        )

        self.now_playing.update_song(
            image_path,
            title,
            artist
        )

    def play_selected_song(
        self,
        image_path,
        title,
        artist
    ):

        for index, song in enumerate(
            self.player_queue
        ):

            if song[0] == image_path:

                self.current_index = index
                break

        self.now_playing.update_song(
            image_path,
            title,
            artist
        )

    # ==================================================
    # MOOD HANDLERS
    # ==================================================

    def handle_mood_selected(
        self,
        mood_name
    ):

        print(
            "Mood selected:",
            mood_name
        )


    def handle_mood_see_all(
        self
    ):

        print(
            "See All moods clicked"
        )

    # ==================================================
    # PAINT EVENT
    # ==================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # ==================================================
        # MAIN BACKGROUND
        # ==================================================

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#0B0913")
        )

        gradient.setColorAt(
            0.45,
            QColor("#151124")
        )

        gradient.setColorAt(
            1.0,
            QColor("#09070F")
        )

        painter.fillRect(
            rect,
            gradient
        )

        # ==================================================
        # TOP PURPLE AMBIENT GLOW
        # ==================================================

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                124,
                58,
                237,
                24
            )
        )

        painter.drawEllipse(
            -180,
            -180,
            500,
            400
        )

        # ==================================================
        # RIGHT AMBIENT GLOW
        # ==================================================

        painter.setBrush(
            QColor(
                139,
                92,
                246,
                16
            )
        )

        painter.drawEllipse(
            rect.width() - 420,
            120,
            500,
            500
        )

        painter.end()

        super().paintEvent(event)