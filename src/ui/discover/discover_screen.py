from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter
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
from widgets.cards.music_card import MusicCard

from data.discover_data import (
    TRENDING_SONGS,
    MOODS,
    GENRES,
)


class DiscoverScreen(QWidget):

    # ==================================================
    # SIGNALS
    # ==================================================

    song_requested = Signal(str, str, str)

    # ==================================================
    # INIT
    # ==================================================

    def __init__(self):

        super().__init__()

        # --------------------------------------------------
        # THEME STATE
        # --------------------------------------------------

        self.is_dark = True

        # --------------------------------------------------
        # COLLECTIONS
        # --------------------------------------------------

        self.music_cards = []
        self.mood_cards = []
        self.mood_icons = []
        self.mood_names = []
        self.genre_cards = []
        self.genre_labels = []

        # --------------------------------------------------
        # WIDGET REFERENCES
        # --------------------------------------------------

        self.title_label = None
        self.subtitle_label = None

        self.banner = None
        self.banner_title = None
        self.banner_subtitle = None
        self.banner_icon = None

        self.section_titles = []
        self.section_actions = []

        self.bottom_text = None

        # --------------------------------------------------
        # BUILD
        # --------------------------------------------------

        self.build_ui()

        # --------------------------------------------------
        # INITIAL THEME
        # --------------------------------------------------

        self.set_theme_state(True)

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
            0,
        )

        root.setSpacing(0)

        # ==================================================
        # SIDEBAR
        # ==================================================

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding,
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

        self.main.setObjectName(
            "DiscoverMain"
        )

        root.addWidget(
            self.main,
            1,
        )

        # ==================================================
        # SCROLL AREA
        # ==================================================

        self.scroll = QScrollArea()

        self.scroll.setObjectName(
            "DiscoverScroll"
        )

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        root.addWidget(
            self.main,
            1,
        )

        # --------------------------------------------------
        # MAIN LAYOUT
        # --------------------------------------------------

        main_layout = QVBoxLayout(
            self.main
        )

        main_layout.setContentsMargins(
            30,
            26,
            22,
            26,
        )

        main_layout.setSpacing(0)

        main_layout.addWidget(
            self.scroll
        )

        # ==================================================
        # CONTENT
        # ==================================================

        self.content = QWidget()

        self.content.setObjectName(
            "DiscoverContent"
        )

        self.content.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.scroll.setWidget(
            self.content
        )

        self.content_layout = QVBoxLayout(
            self.content
        )

        # Bottom space intentionally preserved
        # for floating player.

        self.content_layout.setContentsMargins(
            0,
            0,
            8,
            150,
        )

        self.content_layout.setSpacing(
            24
        )

        self.content_layout.setAlignment(
            Qt.AlignTop
        )

        # ==================================================
        # HEADER
        # ==================================================

        self.title_label = QLabel(
            "Discover"
        )

        self.content_layout.addWidget(
            self.title_label
        )

        self.subtitle_label = QLabel(
            "Explore new sounds, moods and music."
        )

        self.content_layout.addWidget(
            self.subtitle_label
        )

        # ==================================================
        # FEATURE BANNER
        # ==================================================

        self.banner = QFrame()

        self.banner.setObjectName(
            "DiscoverBanner"
        )

        self.banner.setMinimumHeight(
            170
        )

        banner_layout = QHBoxLayout(
            self.banner
        )

        banner_layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        # --------------------------------------------------
        # BANNER TEXT
        # --------------------------------------------------

        banner_text = QVBoxLayout()

        self.banner_title = QLabel(
            "Find Your Next Favorite"
        )

        self.banner_subtitle = QLabel(
            "Discover music made for every mood and moment."
        )

        banner_text.addWidget(
            self.banner_title
        )

        banner_text.addSpacing(
            8
        )

        banner_text.addWidget(
            self.banner_subtitle
        )

        banner_text.addStretch()

        banner_layout.addLayout(
            banner_text
        )

        banner_layout.addStretch()

        # --------------------------------------------------
        # BANNER ICON
        # --------------------------------------------------

        self.banner_icon = QLabel(
            "♫"
        )

        self.banner_icon.setAlignment(
            Qt.AlignCenter
        )

        banner_layout.addWidget(
            self.banner_icon
        )

        self.content_layout.addWidget(
            self.banner
        )

        # ==================================================
        # TRENDING SECTION
        # ==================================================

        trending_header = self.create_section_header(
            "Trending Now",
            "See All  ›",
        )

        self.content_layout.addWidget(
            trending_header
        )

        # ==================================================
        # TRENDING CARDS
        # ==================================================

        trending_container = QWidget()

        trending_container.setAttribute(
            Qt.WA_TranslucentBackground
        )

        trending_layout = QHBoxLayout(
            trending_container
        )

        trending_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        trending_layout.setSpacing(
            16
        )

        # --------------------------------------------------
        # DATA
        # --------------------------------------------------

        for song in TRENDING_SONGS:

            image_path = song["image"]
            song_title = song["title"]
            artist = song["artist"]

            card = MusicCard(
                image_path,
                song_title,
                artist,
            )

            card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )

            card.play_requested.connect(
                self.handle_song_request
            )

            trending_layout.addWidget(
                card
            )

            self.music_cards.append(
                card
            )

        self.content_layout.addWidget(
            trending_container
        )

        # ==================================================
        # MOOD SECTION
        # ==================================================

        mood_header = self.create_section_header(
            "Browse by Mood",
            "View All  ›",
        )

        self.content_layout.addWidget(
            mood_header
        )

        # ==================================================
        # MOOD CARDS
        # ==================================================

        mood_container = QWidget()

        mood_container.setAttribute(
            Qt.WA_TranslucentBackground
        )

        mood_layout = QHBoxLayout(
            mood_container
        )

        mood_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        mood_layout.setSpacing(
            14
        )

        # --------------------------------------------------
        # DATA
        # --------------------------------------------------

        for mood in MOODS:

            mood_name = mood["name"]
            mood_icon = mood["icon"]

            mood_card = QFrame()

            mood_card.setObjectName(
                "MoodCard"
            )

            mood_card.setMinimumHeight(
                105
            )

            mood_card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )

            mood_inner = QVBoxLayout(
                mood_card
            )

            mood_inner.setContentsMargins(
                12,
                12,
                12,
                12,
            )

            mood_inner.setAlignment(
                Qt.AlignCenter
            )

            # --------------------------------------------------
            # ICON
            # --------------------------------------------------

            icon = QLabel(
                mood_icon
            )

            icon.setObjectName(
                "MoodIcon"
            )

            icon.setAlignment(
                Qt.AlignCenter
            )

            # --------------------------------------------------
            # NAME
            # --------------------------------------------------

            name = QLabel(
                mood_name
            )

            name.setObjectName(
                "MoodName"
            )

            name.setAlignment(
                Qt.AlignCenter
            )

            mood_inner.addWidget(
                icon
            )

            mood_inner.addWidget(
                name
            )

            mood_layout.addWidget(
                mood_card
            )

            self.mood_cards.append(
                mood_card
            )

            self.mood_icons.append(
                icon
            )

            self.mood_names.append(
                name
            )

        self.content_layout.addWidget(
            mood_container
        )

        # ==================================================
        # GENRES SECTION
        # ==================================================

        genre_header = self.create_section_header(
            "Explore Genres",
            "View All  ›",
        )

        self.content_layout.addWidget(
            genre_header
        )

        # ==================================================
        # GENRE CARDS
        # ==================================================

        genre_container = QWidget()

        genre_container.setAttribute(
            Qt.WA_TranslucentBackground
        )

        genre_layout = QHBoxLayout(
            genre_container
        )

        genre_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        genre_layout.setSpacing(
            14
        )

        # --------------------------------------------------
        # DATA
        # --------------------------------------------------

        for genre in GENRES:

            genre_name = genre["name"]
            background = genre["background"]

            genre_card = QFrame()

            genre_card.setObjectName(
                "GenreCard"
            )

            genre_card.setProperty(
                "genre_background",
                background
            )

            genre_card.setMinimumHeight(
                90
            )

            genre_card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )

            genre_layout_inner = QVBoxLayout(
                genre_card
            )

            genre_layout_inner.setAlignment(
                Qt.AlignCenter
            )

            genre_label = QLabel(
                genre_name
            )

            genre_label.setObjectName(
                "GenreLabel"
            )

            genre_label.setAlignment(
                Qt.AlignCenter
            )

            genre_layout_inner.addWidget(
                genre_label
            )

            genre_layout.addWidget(
                genre_card
            )

            self.genre_cards.append(
                genre_card
            )

            self.genre_labels.append(
                genre_label
            )

        self.content_layout.addWidget(
            genre_container
        )

        # ==================================================
        # BOTTOM MESSAGE
        # ==================================================

        self.bottom_text = QLabel(
            "More discoveries are coming soon ✦"
        )

        self.bottom_text.setAlignment(
            Qt.AlignCenter
        )

        self.content_layout.addWidget(
            self.bottom_text
        )

        # ==================================================
        # EXTRA BOTTOM SPACE
        # ==================================================

        self.content_layout.addSpacing(
            120
        )

    # ==================================================
    # SECTION HEADER
    # ==================================================

    def create_section_header(
        self,
        title_text,
        action_text,
    ):

        header = QWidget()

        header.setAttribute(
            Qt.WA_TranslucentBackground
        )

        layout = QHBoxLayout(
            header
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            0
        )

        title = QLabel(
            title_text
        )

        title.setObjectName(
            "SectionTitle"
        )

        action = QLabel(
            action_text
        )

        action.setObjectName(
            "SectionAction"
        )

        action.setAlignment(
            Qt.AlignRight |
            Qt.AlignVCenter
        )

        layout.addWidget(
            title
        )

        layout.addStretch()

        layout.addWidget(
            action
        )

        self.section_titles.append(
            title
        )

        self.section_actions.append(
            action
        )

        return header

    # ==================================================
    # THEME STATE
    # ==================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.is_dark = bool(
            is_dark
        )

        # --------------------------------------------------
        # SIDEBAR
        # --------------------------------------------------

        try:

            self.sidebar.set_theme_state(
                self.is_dark
            )

        except Exception as error:

            print(
                "Discover sidebar theme error:",
                error
            )

        # --------------------------------------------------
        # MAIN / SCROLL
        # --------------------------------------------------

        self.apply_scroll_theme()

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        if self.is_dark:

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #FFFFFF;
                    font-size: 34px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

            self.subtitle_label.setStyleSheet(
                """
                QLabel {
                    color: #AFA4C8;
                    font-size: 14px;
                    background: transparent;
                }
                """
            )

        else:

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #241B35;
                    font-size: 34px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

            self.subtitle_label.setStyleSheet(
                """
                QLabel {
                    color: #766A89;
                    font-size: 14px;
                    background: transparent;
                }
                """
            )

        # --------------------------------------------------
        # BANNER
        # --------------------------------------------------

        self.apply_banner_theme()

        # --------------------------------------------------
        # SECTION HEADERS
        # --------------------------------------------------

        for title in self.section_titles:

            if self.is_dark:

                title.setStyleSheet(
                    """
                    QLabel {
                        color: #FFFFFF;
                        font-size: 23px;
                        font-weight: 700;
                        background: transparent;
                    }
                    """
                )

            else:

                title.setStyleSheet(
                    """
                    QLabel {
                        color: #2A203B;
                        font-size: 23px;
                        font-weight: 700;
                        background: transparent;
                    }
                    """
                )

        for action in self.section_actions:

            if self.is_dark:

                action.setStyleSheet(
                    """
                    QLabel {
                        color: #A78BFA;
                        font-size: 13px;
                        font-weight: 600;
                        background: transparent;
                    }
                    """
                )

            else:

                action.setStyleSheet(
                    """
                    QLabel {
                        color: #7440D9;
                        font-size: 13px;
                        font-weight: 600;
                        background: transparent;
                    }
                    """
                )

        # --------------------------------------------------
        # MOOD CARDS
        # --------------------------------------------------

        self.apply_mood_theme()

        # --------------------------------------------------
        # GENRE CARDS
        # --------------------------------------------------

        self.apply_genre_theme()

        # --------------------------------------------------
        # BOTTOM TEXT
        # --------------------------------------------------

        if self.is_dark:

            self.bottom_text.setStyleSheet(
                """
                QLabel {
                    color: #716889;
                    font-size: 12px;
                    padding: 20px;
                    background: transparent;
                }
                """
            )

        else:

            self.bottom_text.setStyleSheet(
                """
                QLabel {
                    color: #8B7D9E;
                    font-size: 12px;
                    padding: 20px;
                    background: transparent;
                }
                """
            )

        # --------------------------------------------------
        # MUSIC CARDS
        # --------------------------------------------------

        for card in self.music_cards:

            try:

                if hasattr(
                    card,
                    "set_theme_state"
                ):

                    card.set_theme_state(
                        self.is_dark
                    )

            except Exception as error:

                print(
                    "Discover MusicCard theme error:",
                    error
                )

        # --------------------------------------------------
        # REPAINT
        # --------------------------------------------------

        self.update()
        self.main.update()
        self.content.update()

        self.scroll.viewport().update()

    # ==================================================
    # SCROLL THEME
    # ==================================================

    def apply_scroll_theme(self):

        if self.is_dark:

            self.scroll.setStyleSheet(
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

        else:

            self.scroll.setStyleSheet(
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
                    background: #8B5CF6;
                    border-radius: 4px;
                    min-height: 55px;
                }

                QScrollBar::handle:vertical:hover {
                    background: #7040D4;
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

    # ==================================================
    # BANNER THEME
    # ==================================================

    def apply_banner_theme(self):

        if self.is_dark:

            self.banner.setStyleSheet(
                """
                QFrame#DiscoverBanner {
                    background: #18122A;
                    border: 1px solid #30224B;
                    border-radius: 24px;
                }

                QFrame#DiscoverBanner:hover {
                    border: 1px solid #53358A;
                }
                """
            )

            self.banner_title.setStyleSheet(
                """
                QLabel {
                    color: #FFFFFF;
                    font-size: 25px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

            self.banner_subtitle.setStyleSheet(
                """
                QLabel {
                    color: #AAA0C5;
                    font-size: 14px;
                    background: transparent;
                }
                """
            )

            self.banner_icon.setStyleSheet(
                """
                QLabel {
                    color: #A970FF;
                    font-size: 72px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

        else:

            self.banner.setStyleSheet(
                """
                QFrame#DiscoverBanner {
                    background: #EDE6FA;
                    border: 1px solid #D3C5EA;
                    border-radius: 24px;
                }

                QFrame#DiscoverBanner:hover {
                    border: 1px solid #B99BEA;
                }
                """
            )

            self.banner_title.setStyleSheet(
                """
                QLabel {
                    color: #281B3B;
                    font-size: 25px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

            self.banner_subtitle.setStyleSheet(
                """
                QLabel {
                    color: #756785;
                    font-size: 14px;
                    background: transparent;
                }
                """
            )

            self.banner_icon.setStyleSheet(
                """
                QLabel {
                    color: #7C3AED;
                    font-size: 72px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

    # ==================================================
    # MOOD THEME
    # ==================================================

    def apply_mood_theme(self):

        if self.is_dark:

            card_style = """
                QFrame#MoodCard {
                    background: #181329;
                    border: 1px solid #30224B;
                    border-radius: 18px;
                }

                QFrame#MoodCard:hover {
                    background: #24183D;
                    border: 1px solid #7048C7;
                }
            """

            icon_style = """
                QLabel#MoodIcon {
                    color: #FFFFFF;
                    font-size: 25px;
                    background: transparent;
                }
            """

            name_style = """
                QLabel#MoodName {
                    color: #D9D3EA;
                    font-size: 13px;
                    font-weight: 600;
                    background: transparent;
                }
            """

        else:

            card_style = """
                QFrame#MoodCard {
                    background: #F1EBFA;
                    border: 1px solid #D7CBE8;
                    border-radius: 18px;
                }

                QFrame#MoodCard:hover {
                    background: #E8DDF7;
                    border: 1px solid #A98AD7;
                }
            """

            icon_style = """
                QLabel#MoodIcon {
                    color: #49366A;
                    font-size: 25px;
                    background: transparent;
                }
            """

            name_style = """
                QLabel#MoodName {
                    color: #594B6E;
                    font-size: 13px;
                    font-weight: 600;
                    background: transparent;
                }
            """

        for card in self.mood_cards:

            card.setStyleSheet(
                card_style
            )

        for icon in self.mood_icons:

            icon.setStyleSheet(
                icon_style
            )

        for name in self.mood_names:

            name.setStyleSheet(
                name_style
            )

    # ==================================================
    # GENRE THEME
    # ==================================================

    def apply_genre_theme(self):

        for card in self.genre_cards:

            original_background = card.property(
                "genre_background"
            )

            if original_background is None:
                original_background = "#30224B"

            if self.is_dark:

                card.setStyleSheet(
                    f"""
                    QFrame#GenreCard {{
                        background: {original_background};
                        border-radius: 18px;
                        border: 1px solid rgba(255,255,255,20);
                    }}

                    QFrame#GenreCard:hover {{
                        border: 1px solid #A970FF;
                    }}
                    """
                )

            else:

                card.setStyleSheet(
                    f"""
                    QFrame#GenreCard {{
                        background: {original_background};
                        border-radius: 18px;
                        border: 1px solid rgba(70,50,100,45);
                    }}

                    QFrame#GenreCard:hover {{
                        border: 1px solid #7C3AED;
                    }}
                    """
                )

        for label in self.genre_labels:

            label.setStyleSheet(
                """
                QLabel#GenreLabel {
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

    # ==================================================
    # MUSIC PLAY
    # ==================================================

    def handle_song_request(
        self,
        image_path,
        title,
        artist,
    ):

        print(
            f"Discover song selected: {title} - {artist}"
        )

        self.song_requested.emit(
            image_path,
            title,
            artist,
        )

    # ==================================================
    # BACKGROUND
    # ==================================================

    def paintEvent(
        self,
        event,
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # ==================================================
        # DARK MODE
        # ==================================================

        if self.is_dark:

            gradient = QLinearGradient(
                0,
                0,
                rect.width(),
                rect.height(),
            )

            gradient.setColorAt(
                0.0,
                QColor("#0B0913"),
            )

            gradient.setColorAt(
                0.45,
                QColor("#151124"),
            )

            gradient.setColorAt(
                1.0,
                QColor("#09070F"),
            )

            painter.fillRect(
                rect,
                gradient,
            )

            # ------------------------------------------------
            # TOP PURPLE GLOW
            # ------------------------------------------------

            painter.setPen(
                Qt.NoPen
            )

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    24,
                )
            )

            painter.drawEllipse(
                -180,
                -180,
                500,
                400,
            )

            # ------------------------------------------------
            # RIGHT AMBIENT GLOW
            # ------------------------------------------------

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    16,
                )
            )

            painter.drawEllipse(
                rect.width() - 420,
                120,
                500,
                500,
            )

        # ==================================================
        # LIGHT MODE
        # ==================================================

        else:

            gradient = QLinearGradient(
                0,
                0,
                rect.width(),
                rect.height(),
            )

            gradient.setColorAt(
                0.0,
                QColor("#F4F0FA"),
            )

            gradient.setColorAt(
                0.45,
                QColor("#EDE7F5"),
            )

            gradient.setColorAt(
                1.0,
                QColor("#E8E1F1"),
            )

            painter.fillRect(
                rect,
                gradient,
            )

            # ------------------------------------------------
            # TOP SOFT PURPLE GLOW
            # ------------------------------------------------

            painter.setPen(
                Qt.NoPen
            )

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    15,
                )
            )

            painter.drawEllipse(
                -180,
                -180,
                500,
                400,
            )

            # ------------------------------------------------
            # RIGHT SOFT GLOW
            # ------------------------------------------------

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    10,
                )
            )

            painter.drawEllipse(
                rect.width() - 420,
                120,
                500,
                500,
            )

        painter.end()

        super().paintEvent(
            event
        )