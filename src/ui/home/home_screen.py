import random
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

# IMPORTANT:
# Same shared store used by PlaylistScreen.
from data.playlist_store import playlist_store


class HomeScreen(QWidget):

    def __init__(self):

        super().__init__()

        # ==================================================
        # WINDOW
        # ==================================================

        self.setWindowTitle(
            "🎵 LYRx"
        )

        self.resize(
            1450,
            900
        )

        self.setMinimumSize(
            1200,
            720
        )

        # ==================================================
        # THEME
        # ==================================================

        self.current_is_dark = True

        # ==================================================
        # MUSIC DATA
        # ==================================================

        self.player_queue = [

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

        self.current_index = 0

        # ==================================================
        # SHARED PLAYLIST STORE
        # ==================================================

        self.playlist_store = playlist_store

        self.playlists = (
            self.playlist_store.get_playlists()
        )

        # ==================================================
        # MUSIC CARDS
        # ==================================================

        # Stores:
        #
        # (
        #     card,
        #     title,
        #     artist
        # )
        #
        self.music_cards = []

        # ==================================================
        # PLAYLIST PREVIEW CARDS
        # ==================================================

        self.playlist_preview_cards = []

        # ==================================================
        # BUILD
        # ==================================================

        self.build_ui()

        # ==================================================
        # APPLY INITIAL THEME
        # ==================================================

        self.set_theme_state(
            self.current_is_dark
        )

        # ==================================================
        # LOAD PLAYLIST PREVIEW
        # ==================================================

        self.refresh_playlist_preview()

    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):

        # ==================================================
        # ROOT
        # ==================================================

        root = QHBoxLayout(
            self
        )

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(
            0
        )

        # ==================================================
        # SIDEBAR
        # ==================================================

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.sidebar
        )

        # ==================================================
        # MAIN AREA
        # ==================================================

        self.main = QWidget()

        self.main.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.main.setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            """
        )

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

        self.main_layout.setSpacing(
            0
        )

        # ==================================================
        # LEFT CONTENT
        # ==================================================

        self.left = QWidget()

        self.left.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.left.setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            """
        )

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

        self.left_layout.setSpacing(
            22
        )

        # ==================================================
        # RIGHT PLAYER
        # ==================================================

        self.right_area = QWidget()

        self.right_area.setFixedWidth(
            330
        )

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

        self.right_layout.setSpacing(
            18
        )

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
        # SEARCH
        # ==================================================

        self.header.search_changed.connect(
            self.filter_music_cards
        )

        # ==================================================
        # CONTENT SCROLL
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

        self.content_scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea > QWidget > QWidget {
                background: transparent;
            }

            QScrollBar:vertical {
                width: 9px;
                background: transparent;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #7C3AED;
                border-radius: 4px;
                min-height: 55px;
            }

            QScrollBar::handle:vertical:hover {
                background: #9F67FF;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

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

        self.content.setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            """
        )

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
        # HERO
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
        # NOW PLAYING
        # ==================================================

        self.now_playing = NowPlaying()

        # ==================================================
        # PLAYER CONNECTIONS
        # ==================================================

        self.now_playing.previous_requested.connect(
            self.play_previous
        )

        self.now_playing.next_requested.connect(
            self.play_next
        )

        self.now_playing.next_song_requested.connect(
            self.play_selected_song
        )

        # ==================================================
        # MASTER QUEUE
        # ==================================================

        self.now_playing.set_queue(
            self.player_queue
        )

        self.now_playing.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.right_layout.addWidget(
            self.now_playing
        )

        self.right_layout.addStretch()

        self.right_area.setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            """
        )

        # ==================================================
        # CONTINUE LISTENING HEADER
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

        continue_header_layout.setSpacing(
            10
        )

        self.continue_title = QLabel(
            "Continue Listening"
        )

        continue_header_layout.addWidget(
            self.continue_title
        )

        continue_header_layout.addStretch()

        self.more_button = QLabel(
            "More  ›"
        )

        self.more_button.setAlignment(
            Qt.AlignRight |
            Qt.AlignVCenter
        )

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

        for (
            image_path,
            title,
            artist
        ) in self.player_queue:

            card = MusicCard(
                image_path,
                title,
                artist
            )

            card.setSizePolicy(
                QSizePolicy.Fixed,
                QSizePolicy.Fixed
            )

            # --------------------------------------------------
            # PLAY
            # --------------------------------------------------

            card.play_requested.connect(
                self.handle_play_request
            )

            # --------------------------------------------------
            # FAVORITE
            # --------------------------------------------------

            card.favorite_changed.connect(
                self.handle_favorite_changed
            )

            self.cards_layout.addWidget(
                card
            )

            self.music_cards.append(
                (
                    card,
                    title,
                    artist
                )
            )

        self.cards_layout.setAlignment(
            Qt.AlignLeft
        )

        # ==================================================
        # NO RESULTS
        # ==================================================

        self.no_results = QLabel(
            "🎵  No music found"
        )

        self.no_results.setAlignment(
            Qt.AlignCenter
        )

        self.no_results.setMinimumHeight(
            150
        )

        self.no_results.hide()

        self.content_layout.addWidget(
            self.no_results
        )

        # ==================================================
        # YOUR VIBE
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
        # PLAYLIST HEADER
        # ==================================================

        self.playlist_header = QWidget()

        playlist_header_layout = QHBoxLayout(
            self.playlist_header
        )

        playlist_header_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        playlist_header_layout.setSpacing(
            10
        )

        self.playlist_title = QLabel(
            "Playlists for You"
        )

        playlist_header_layout.addWidget(
            self.playlist_title
        )

        playlist_header_layout.addStretch()

        self.playlist_more = QLabel(
            "View All  ›"
        )

        self.playlist_more.setAlignment(
            Qt.AlignRight |
            Qt.AlignVCenter
        )

        playlist_header_layout.addWidget(
            self.playlist_more
        )

        self.content_layout.addWidget(
            self.playlist_header
        )

        # ==================================================
        # PLAYLIST CONTAINER
        # ==================================================

        self.playlist_container = QWidget()

        self.playlist_container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.playlist_layout = QHBoxLayout(
            self.playlist_container
        )

        self.playlist_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.playlist_layout.setSpacing(
            16
        )

        self.content_layout.addWidget(
            self.playlist_container
        )

        # ==================================================
        # BOTTOM SPACE
        # ==================================================

        self.content_layout.addSpacing(
            20
        )

        self.update_card_sizes()

    # =========================================================
    # REFRESH PLAYLIST PREVIEW
    # =========================================================

    def refresh_playlist_preview(self):

        if not hasattr(
            self,
            "playlist_layout"
        ):
            return

        # ==================================================
        # REMOVE OLD CARDS
        # ==================================================

        while self.playlist_layout.count():

            item = self.playlist_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

        self.playlist_preview_cards = []

        # ==================================================
        # GET LATEST STORE DATA
        # ==================================================

        self.playlists = (
            self.playlist_store.get_playlists()
        )

        # ==================================================
        # EMPTY STATE
        # ==================================================

        if not self.playlists:

            empty = QLabel(
                "No playlists yet.\n"
                "Create one from the Playlists page."
            )

            empty.setAlignment(
                Qt.AlignCenter
            )

            empty.setMinimumHeight(
                105
            )

            empty.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            self.playlist_layout.addWidget(
                empty
            )

            self.playlist_preview_cards.append(
                empty
            )

            self.apply_playlist_theme(
                empty
            )

            return

        # ==================================================
        # SHOW MAX 3 PLAYLISTS
        # ==================================================

        preview_playlists = (
            self.playlists[:3]
        )

        for playlist in preview_playlists:

            card = self.create_playlist_preview(
                playlist
            )

            self.playlist_layout.addWidget(
                card
            )

            self.playlist_preview_cards.append(
                card
            )

        # ==================================================
        # FILL REMAINING SPACE
        # ==================================================

        self.playlist_layout.addStretch()

    # =========================================================
    # CREATE PLAYLIST PREVIEW CARD
    # =========================================================

    def create_playlist_preview(
        self,
        playlist
    ):

        card = QFrame()

        card.setMinimumWidth(
            180
        )

        card.setMinimumHeight(
            108
        )

        card.setMaximumHeight(
            118
        )

        card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        layout.setSpacing(
            12
        )

        # ==================================================
        # COVER
        # ==================================================

        cover = QLabel()

        cover.setFixedSize(
            78,
            78
        )

        cover.setAlignment(
            Qt.AlignCenter
        )

        thumbnail = playlist.get(
            "thumbnail",
            ""
        )

        pix = self.load_asset_pixmap(
            thumbnail
        )

        if pix and not pix.isNull():

            cover.setPixmap(
                pix.scaled(
                    78,
                    78,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

        else:

            cover.setText(
                "♫"
            )

        layout.addWidget(
            cover
        )

        # ==================================================
        # INFO
        # ==================================================

        info = QVBoxLayout()

        info.setContentsMargins(
            0,
            3,
            0,
            3
        )

        info.setSpacing(
            5
        )

        name = QLabel(
            playlist.get(
                "name",
                "Playlist"
            )
        )

        name.setWordWrap(
            True
        )

        description = QLabel(
            playlist.get(
                "description",
                "Your playlist"
            )
        )

        description.setWordWrap(
            True
        )

        count = len(
            playlist.get(
                "songs",
                []
            )
        )

        word = (
            "song"
            if count == 1
            else "songs"
        )

        count_label = QLabel(
            f"{count} {word}"
        )

        info.addWidget(
            name
        )

        info.addWidget(
            description
        )

        info.addWidget(
            count_label
        )

        info.addStretch()

        layout.addLayout(
            info,
            1
        )

        # ==================================================
        # THEME
        # ==================================================

        self.apply_playlist_card_theme(
            card,
            cover,
            name,
            description,
            count_label
        )

        return card

    # =========================================================
    # LOAD ASSET
    # =========================================================

    def load_asset_pixmap(
        self,
        relative_path
    ):

        if not relative_path:

            return None

        path = Path(
            relative_path
        )

        candidates = [

            path,

            Path.cwd() / relative_path,

            Path(__file__).resolve().parents[2]
            / relative_path,

            Path(__file__).resolve().parents[1]
            / relative_path,

        ]

        for candidate in candidates:

            try:

                candidate = candidate.resolve()

            except Exception:

                continue

            try:

                if candidate.is_file():

                    pixmap = QPixmap(
                        str(candidate)
                    )

                    if not pixmap.isNull():

                        return pixmap

            except Exception:

                pass

        return None

    # =========================================================
    # RESPONSIVE MUSIC CARD SIZING
    # =========================================================

    def update_card_sizes(self):

        if not hasattr(
            self,
            "cards_container"
        ):
            return

        available_width = (
            self.cards_container.width()
        )

        if available_width <= 0:

            return

        card_count = len(
            self.music_cards
        )

        if card_count == 0:

            return

        spacing = (
            self.cards_layout.spacing()
        )

        total_spacing = (
            spacing *
            (card_count - 1)
        )

        card_width = (
            available_width -
            total_spacing
        ) // card_count

        card_width = max(
            150,
            min(
                card_width,
                196
            )
        )

        for (
            card,
            title,
            artist
        ) in self.music_cards:

            card.setFixedWidth(
                card_width
            )

    # =========================================================
    # RESIZE EVENT
    # =========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        self.update_card_sizes()

    # =========================================================
    # FAVORITE
    # =========================================================

    def handle_favorite_changed(
        self,
        image_path,
        title,
        is_favorite
    ):

        state = (
            "added to"
            if is_favorite
            else "removed from"
        )

        print(
            f"{title} {state} favorites"
        )

    # =========================================================
    # SEARCH
    # =========================================================

    def filter_music_cards(
        self,
        search_text: str
    ):

        search_text = (
            search_text
            .strip()
            .lower()
        )

        visible_count = 0

        # ==================================================
        # FILTER
        # ==================================================

        for (
            card,
            title,
            artist
        ) in self.music_cards:

            searchable_text = (
                f"{title} {artist}"
            ).lower()

            matches = (
                not search_text
                or
                search_text in searchable_text
            )

            card.setVisible(
                matches
            )

            if matches:

                visible_count += 1

        # ==================================================
        # NORMAL
        # ==================================================

        if not search_text:

            self.continue_title.setText(
                "Continue Listening"
            )

            self.more_button.setText(
                "More  ›"
            )

            self.no_results.hide()

            return

        # ==================================================
        # RESULTS
        # ==================================================

        if visible_count > 0:

            track_word = (
                "track"
                if visible_count == 1
                else "tracks"
            )

            self.continue_title.setText(
                f"Search Results · "
                f"{visible_count} {track_word}"
            )

            self.more_button.setText(
                "Clear  ×"
            )

            self.no_results.hide()

        # ==================================================
        # NO RESULTS
        # ==================================================

        else:

            self.continue_title.setText(
                "Search Results"
            )

            self.more_button.setText(
                "Clear  ×"
            )

            self.no_results.setText(
                "🎵  No music found\n\n"
                "Try searching for another song "
                "or artist."
            )

            self.no_results.show()

    # =========================================================
    # HANDLE PLAY REQUEST
    # =========================================================

    def handle_play_request(
        self,
        image_path,
        title,
        artist
    ):

        for index, song in enumerate(
            self.player_queue
        ):

            if (
                song[0] == image_path
                and
                song[1] == title
                and
                song[2] == artist
            ):

                self.current_index = index

                break

        self.now_playing.set_current_index(
            self.current_index
        )

        self.now_playing.update_song(
            image_path,
            title,
            artist
        )

    # =========================================================
    # PLAY NEXT
    # =========================================================

    def play_next(self):

        # ==================================================
        # DAY 19 - ONLINE QUEUE
        # ==================================================

        if (
            getattr(
                self.now_playing,
                "playback_source",
                "local"
            )
            == "online"
        ):

            self.now_playing.play_online_next()

            return
        
        if not self.player_queue:

            return

        # ==================================================
        # SHUFFLE
        # ==================================================

        if self.now_playing.is_shuffle:

            if len(
                self.player_queue
            ) == 1:

                next_index = (
                    self.current_index
                )

            else:

                available_indexes = [

                    index

                    for index in range(
                        len(
                            self.player_queue
                        )
                    )

                    if index !=
                    self.current_index
                ]

                next_index = random.choice(
                    available_indexes
                )

            self.current_index = (
                next_index
            )

        # ==================================================
        # NORMAL
        # ==================================================

        else:

            self.current_index += 1

            if (
                self.current_index
                >=
                len(
                    self.player_queue
                )
            ):

                self.current_index = 0

        self._play_queue_index(
            self.current_index
        )

    # =========================================================
    # PLAY PREVIOUS
    # =========================================================

    def play_previous(self):

        # ==================================================
        # DAY 19 - ONLINE QUEUE
        # ==================================================

        if (
            getattr(
                self.now_playing,
                "playback_source",
                "local"
            )
            == "online"
        ):

            self.now_playing.play_online_previous()

            return
        
        if not self.player_queue:

            return

        self.current_index -= 1

        if self.current_index < 0:

            self.current_index = (
                len(
                    self.player_queue
                ) - 1
            )

        self._play_queue_index(
            self.current_index
        )

    # =========================================================
    # PLAY SELECTED SONG
    # =========================================================

    def play_selected_song(
        self,
        image_path,
        title,
        artist
    ):

        for index, song in enumerate(
            self.player_queue
        ):

            if (
                song[0] == image_path
                and
                song[1] == title
                and
                song[2] == artist
            ):

                self.current_index = index

                break

        self._play_queue_index(
            self.current_index
        )

    # =========================================================
    # PLAY QUEUE INDEX
    # =========================================================

    def _play_queue_index(
        self,
        index
    ):

        if not self.player_queue:

            return

        if (
            index < 0
            or
            index >= len(
                self.player_queue
            )
        ):

            return

        self.current_index = index

        (
            image_path,
            title,
            artist
        ) = self.player_queue[
            index
        ]

        # ==================================================
        # SYNC PLAYER INDEX
        # ==================================================

        self.now_playing.set_current_index(
            self.current_index
        )

        # ==================================================
        # UPDATE PLAYER
        # ==================================================

        self.now_playing.update_song(
            image_path,
            title,
            artist
        )

        print(
            f"Queue playing: "
            f"{title} - {artist}"
        )

    # =========================================================
    # MOOD
    # =========================================================

    def handle_mood_selected(
        self,
        mood_name
    ):

        print(
            "Mood selected:",
            mood_name
        )

    # =========================================================
    # MOOD SEE ALL
    # =========================================================

    def handle_mood_see_all(
        self
    ):

        print(
            "See All moods clicked"
        )

    # =========================================================
    # THEME STATE
    # =========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.current_is_dark = bool(
            is_dark
        )

        # ==================================================
        # SIDEBAR
        # ==================================================

        if hasattr(
            self,
            "sidebar"
        ):

            try:

                self.sidebar.set_theme_state(
                    self.current_is_dark
                )

            except Exception as error:

                print(
                    "Sidebar theme error:",
                    error
                )

        # ==================================================
        # NOW PLAYING
        # ==================================================

        if hasattr(
            self,
            "now_playing"
        ):

            try:

                if hasattr(
                    self.now_playing,
                    "set_theme_state"
                ):

                    self.now_playing.set_theme_state(
                        self.current_is_dark
                    )

            except Exception as error:

                print(
                    "Player theme error:",
                    error
                )

        # ==================================================
        # MUSIC CARDS
        # ==================================================

        for (
            card,
            title,
            artist
        ) in getattr(
            self,
            "music_cards",
            []
        ):

            try:

                if hasattr(
                    card,
                    "set_theme_state"
                ):

                    card.set_theme_state(
                        self.current_is_dark
                    )

            except Exception as error:

                print(
                    "Music card theme error:",
                    error
                )

        # ==================================================
        # TEXT COLORS
        # ==================================================

        if hasattr(
            self,
            "continue_title"
        ):

            self.continue_title.setStyleSheet(
                f"""
                QLabel {{
                    color: {
                        "#FFFFFF"
                        if self.current_is_dark
                        else "#302744"
                    };

                    font-size: 24px;
                    font-weight: 700;
                    background: transparent;
                }}
                """
            )

        if hasattr(
            self,
            "more_button"
        ):

            self.more_button.setStyleSheet(
                f"""
                QLabel {{
                    color: {
                        "#9B7AFF"
                        if self.current_is_dark
                        else "#7C3AED"
                    };

                    font-size: 13px;
                    font-weight: 600;
                    background: transparent;
                }}
                """
            )

        if hasattr(
            self,
            "playlist_title"
        ):

            self.playlist_title.setStyleSheet(
                f"""
                QLabel {{
                    color: {
                        "#FFFFFF"
                        if self.current_is_dark
                        else "#302744"
                    };

                    font-size: 24px;
                    font-weight: 700;
                    background: transparent;
                }}
                """
            )

        if hasattr(
            self,
            "playlist_more"
        ):

            self.playlist_more.setStyleSheet(
                f"""
                QLabel {{
                    color: {
                        "#9B7AFF"
                        if self.current_is_dark
                        else "#7C3AED"
                    };

                    font-size: 13px;
                    font-weight: 600;
                    background: transparent;
                }}
                """
            )

        # ==================================================
        # NO RESULTS
        # ==================================================

        if hasattr(
            self,
            "no_results"
        ):

            if self.current_is_dark:

                self.no_results.setStyleSheet(
                    """
                    QLabel {
                        color: #B9AFD5;
                        background: #151024;
                        border: 1px solid #2D2348;
                        border-radius: 18px;
                        font-size: 16px;
                        font-weight: 600;
                        padding: 30px;
                    }
                    """
                )

            else:

                self.no_results.setStyleSheet(
                    """
                    QLabel {
                        color: #756A88;
                        background: #F8F4FB;
                        border: 1px solid #D9CDE7;
                        border-radius: 18px;
                        font-size: 16px;
                        font-weight: 600;
                        padding: 30px;
                    }
                    """
                )

        # ==================================================
        # REFRESH PLAYLIST PREVIEW
        # ==================================================

        if hasattr(
            self,
            "playlist_container"
        ):

            self.refresh_playlist_preview()

        self.update()

    # =========================================================
    # PLAYLIST CARD THEME
    # =========================================================

    def apply_playlist_card_theme(
        self,
        card,
        cover,
        name,
        description,
        count
    ):

        if self.current_is_dark:

            card.setStyleSheet(
                """
                QFrame {
                    background: #191329;
                    border: 1px solid #30224B;
                    border-radius: 16px;
                }

                QFrame:hover {
                    background: #24183D;
                    border: 1px solid #7048C7;
                }
                """
            )

            cover.setStyleSheet(
                """
                QLabel {
                    background: #251A3A;
                    border-radius: 12px;
                    color: #A970FF;
                    font-size: 28px;
                    font-weight: 700;
                }
                """
            )

            name.setStyleSheet(
                """
                QLabel {
                    color: white;
                    font-size: 14px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            description.setStyleSheet(
                """
                QLabel {
                    color: #9589AA;
                    font-size: 11px;
                    background: transparent;
                }
                """
            )

            count.setStyleSheet(
                """
                QLabel {
                    color: #9B7AFF;
                    font-size: 11px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

        else:

            card.setStyleSheet(
                """
                QFrame {
                    background: #FAF8FC;
                    border: 1px solid #DED3E8;
                    border-radius: 16px;
                }

                QFrame:hover {
                    background: #F5F0FA;
                    border: 1px solid #9B70E8;
                }
                """
            )

            cover.setStyleSheet(
                """
                QLabel {
                    background: #EEE8F5;
                    border-radius: 12px;
                    color: #7C3AED;
                    font-size: 28px;
                    font-weight: 700;
                }
                """
            )

            name.setStyleSheet(
                """
                QLabel {
                    color: #302744;
                    font-size: 14px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            description.setStyleSheet(
                """
                QLabel {
                    color: #756A88;
                    font-size: 11px;
                    background: transparent;
                }
                """
            )

            count.setStyleSheet(
                """
                QLabel {
                    color: #7C3AED;
                    font-size: 11px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

    # =========================================================
    # EMPTY PLAYLIST THEME
    # =========================================================

    def apply_playlist_theme(
        self,
        widget
    ):

        if self.current_is_dark:

            widget.setStyleSheet(
                """
                QLabel {
                    color: #9B91B2;
                    background: #151024;
                    border: 1px solid #30234A;
                    border-radius: 16px;
                    font-size: 13px;
                    font-weight: 600;
                }
                """
            )

        else:

            widget.setStyleSheet(
                """
                QLabel {
                    color: #756A88;
                    background: #FAF8FC;
                    border: 1px solid #DED3E8;
                    border-radius: 16px;
                    font-size: 13px;
                    font-weight: 600;
                }
                """
            )

    # =========================================================
    # PAINT EVENT
    # =========================================================

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # ==================================================
        # BACKGROUND GRADIENT
        # ==================================================

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        if self.current_is_dark:

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

        else:

            gradient.setColorAt(
                0.0,
                QColor("#EEE9F4")
            )

            gradient.setColorAt(
                0.45,
                QColor("#E8E0F0")
            )

            gradient.setColorAt(
                1.0,
                QColor("#F2EDF6")
            )

        painter.fillRect(
            rect,
            gradient
        )

        # ==================================================
        # TOP PURPLE GLOW
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
                if self.current_is_dark
                else 12
            )
        )

        painter.drawEllipse(
            -180,
            -180,
            500,
            400
        )

        # ==================================================
        # RIGHT PURPLE GLOW
        # ==================================================

        painter.setBrush(
            QColor(
                139,
                92,
                246,
                16
                if self.current_is_dark
                else 9
            )
        )

        painter.drawEllipse(
            rect.width() - 420,
            120,
            500,
            500
        )

        painter.end()

        super().paintEvent(
            event
        )