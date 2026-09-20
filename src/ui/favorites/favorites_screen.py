import json
from pathlib import Path

from PySide6.QtCore import (
    Qt,
    Signal,
    QUrl
)

from PySide6.QtGui import (
    QColor,
    QPainter,
    QLinearGradient,
    QPixmap,
)


from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
)

from data.youtube_favorites_store import (
    youtube_favorites_store
)

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QSizePolicy,
)

from widgets.sidebar import Sidebar
from widgets.cards.music_card import MusicCard


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()

# music_player_desktop/
PROJECT_DIR = FILE_DIR.parents[3]

FAVORITES_FILE = PROJECT_DIR / "favorites.json"


# ============================================================
# FAVORITES SCREEN
# ============================================================

class FavoritesScreen(QWidget):

    play_requested = Signal(
        str,
        str,
        str
    )

    youtube_play_requested = Signal(
    object
    )

    item_play_requested = Signal(object)

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "🎵 LYRx - Favorites"
        )

        self.youtube_cards = []

        self.youtube_network = (
            QNetworkAccessManager(
            self
            )
        )

        self.youtube_replies = []

        self.favorite_cards = []

        self.current_is_dark = True

        self.build_ui()

        self.reload_favorites()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

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

        # ====================================================
        # SIDEBAR
        # ====================================================

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.sidebar
        )

        # ====================================================
        # MAIN AREA
        # ====================================================

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

        self.main_layout = QVBoxLayout(
            self.main
        )

        self.main_layout.setContentsMargins(
            34,
            30,
            34,
            30
        )

        self.main_layout.setSpacing(
            18
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = QWidget()

        header_layout = QVBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        header_layout.setSpacing(
            6
        )

        self.title = QLabel(
            "Favorites"
        )

        self.title.setStyleSheet("""
        QLabel {

            color: white;

            font-size: 32px;

            font-weight: 800;

            background: transparent;

            border: none;
        }
        """)

        self.subtitle = QLabel(
            "Your favorite songs, all in one place."
        )

        self.subtitle.setStyleSheet("""
        QLabel {

            color: #AFA4C8;

            font-size: 14px;

            background: transparent;

            border: none;
        }
        """)

        header_layout.addWidget(
            self.title
        )

        header_layout.addWidget(
            self.subtitle
        )

        self.main_layout.addWidget(
            header
        )

        # ====================================================
        # FAVORITES COUNT
        # ====================================================

        self.count_label = QLabel(
            "0 songs"
        )

        self.count_label.setStyleSheet("""
        QLabel {

            color: #9B7AFF;

            font-size: 13px;

            font-weight: 600;

            background: transparent;

            border: none;
        }
        """)

        self.main_layout.addWidget(
            self.count_label
        )

        # ====================================================
        # SCROLL AREA
        # ====================================================

        self.scroll = QScrollArea()

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

        self.scroll.setStyleSheet("""
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
        """)

        self.main_layout.addWidget(
            self.scroll,
            1
        )

        # ====================================================
        # SCROLL CONTENT
        # ====================================================

        self.content = QWidget()

        self.content.setStyleSheet("""
        QWidget {

            background: transparent;
        }
        """)

        self.content_layout = QVBoxLayout(
            self.content
        )

        self.content_layout.setContentsMargins(
            0,
            0,
            10,
            30
        )

        self.content_layout.setSpacing(
            20
        )

        self.content_layout.setAlignment(
            Qt.AlignTop
        )

        self.scroll.setWidget(
            self.content
        )

        # ====================================================
        # EMPTY STATE
        # ====================================================

        self.empty_state = QFrame()

        self.empty_state.setMinimumHeight(
            260
        )

        self.empty_state.setObjectName(
            "EmptyState"
        )

        empty_layout = QVBoxLayout(
            self.empty_state
        )

        empty_layout.setAlignment(
            Qt.AlignCenter
        )

        empty_icon = QLabel(
            "♡"
        )

        empty_icon.setAlignment(
            Qt.AlignCenter
        )

        empty_icon.setStyleSheet("""
        QLabel {

            color: #8B5CF6;

            font-family: "Segoe UI Symbol";

            font-size: 52px;

            background: transparent;

            border: none;
        }
        """)

        self.empty_title = QLabel(
            "No favorites yet"
        )

        self.empty_title.setAlignment(
            Qt.AlignCenter
        )

        self.empty_title.setStyleSheet("""
        QLabel {

            color: white;

            font-size: 20px;

            font-weight: 700;

            background: transparent;

            border: none;
        }
        """)

        self.empty_text = QLabel(
            "Songs you favorite will appear here."
        )

        self.empty_text.setAlignment(
            Qt.AlignCenter
        )

        self.empty_text.setStyleSheet("""
        QLabel {

            color: #8F86AA;

            font-size: 13px;

            background: transparent;

            border: none;
        }
        """)

        empty_layout.addWidget(
            empty_icon
        )

        empty_layout.addSpacing(
            8
        )

        empty_layout.addWidget(
            self.empty_title
        )

        empty_layout.addSpacing(
            4
        )

        empty_layout.addWidget(
            self.empty_text
        )

        self.content_layout.addWidget(
            self.empty_state
        )

        self.empty_state.hide()

    # ========================================================
    # READ FAVORITES
    # ========================================================

    def read_favorites(self):

        try:

            if not FAVORITES_FILE.exists():

                return []

            with open(
                FAVORITES_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, list):

                    return [
                        item
                        for item in data
                        if isinstance(item, dict)
                    ]

        except (
            json.JSONDecodeError,
            OSError,
            TypeError
        ):

            print(
                "Could not read favorites.json"
            )

        return []

    # ========================================================
    # CLEAR OLD CARDS
    # ========================================================

    def clear_cards(self):

        for card in self.favorite_cards:

            try:
                card.deleteLater()

            except Exception:
                pass

        self.favorite_cards.clear()

        for card in self.youtube_cards:

            try:
                card.deleteLater()

            except Exception:
                pass

        self.youtube_cards.clear()

    # ========================================================
    # RELOAD FAVORITES
    # ========================================================

    def reload_favorites(self):

        self.clear_cards()

        # ========================================================
        # LOCAL FAVORITES
        # ========================================================

        favorites = (
            self.read_favorites()
        )

        # ========================================================
        # YOUTUBE FAVORITES
        # ========================================================

        youtube_favorites = (
            youtube_favorites_store
            .get_favorites()
        )

        total_count = (
            len(favorites)
            +
            len(youtube_favorites)
        )

        self.count_label.setText(
            f"{total_count} "
            f"{'song' if total_count == 1 else 'songs'}"
        )

        # ========================================================
        # EMPTY
        # ========================================================

        if total_count == 0:

            self.empty_state.show()

            return

        self.empty_state.hide()

        # ========================================================
        # LOCAL FAVORITES
        # ========================================================

        for item in favorites:

            image_path = item.get(
                "image_path",
                ""
            )

            title = item.get(
                "title",
                "Unknown Song"
            )

            artist = item.get(
                "artist",
                "Unknown Artist"
            )

            if not image_path:

                continue

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
                lambda _image, _title, _artist, favorite_item=dict(item):
                self.item_play_requested.emit(favorite_item)
            )

            card.favorite_changed.connect(
                self.handle_favorite_changed
            )

            try:

                card.set_theme_state(
                    self.current_is_dark
                )

            except Exception:

                pass

            self.content_layout.addWidget(
                card,
                alignment=Qt.AlignLeft
            )

            self.favorite_cards.append(
                card
            )

        # ========================================================
        # YOUTUBE FAVORITES
        # ========================================================

        for item in youtube_favorites:

            card = self.create_youtube_card(
                item
            )

            self.content_layout.addWidget(
                card,
                alignment=Qt.AlignLeft
            )

            self.youtube_cards.append(
                card
            )

    # ========================================================
    # YOUTUBE FAVORITE CARD
    # ========================================================

    def create_youtube_card(
        self,
        item
    ):

        card = QFrame()

        card.setObjectName(
            "YouTubeFavoriteCard"
        )

        card.setFixedHeight(
            108
        )

        card.setMinimumWidth(
            560
        )

        card.setMaximumWidth(
            760
        )

        row = QHBoxLayout(
            card
        )

        row.setContentsMargins(
            12,
            10,
            14,
            10
        )

        row.setSpacing(
            14
        )

        # ====================================================
        # COVER
        # ====================================================

        cover = QLabel(
            "▶"
        )

        cover.setFixedSize(
            88,
            88
        )

        cover.setAlignment(
            Qt.AlignCenter
        )

        cover.setStyleSheet("""
        QLabel {
            background: #211633;
            color: #A970FF;
            border-radius: 12px;
            font-size: 24px;
        }
        """)

        row.addWidget(
            cover
        )

        thumbnail = str(
            item.get(
                "thumbnail_url",
                ""
            )
            or ""
        )

        if thumbnail:

            self.load_youtube_thumbnail(
                thumbnail,
                cover
            )

        # ====================================================
        # TEXT
        # ====================================================

        info = QVBoxLayout()

        info.setSpacing(
            4
        )

        title = QLabel(
            str(
                item.get(
                    "title",
                    "YouTube Track"
                )
            )
        )

        title.setWordWrap(
            True
        )

        channel = QLabel(
            str(
                item.get(
                    "channel",
                    "YouTube"
                )
            )
        )

        duration_seconds = int(
            item.get(
                "duration",
                0
            )
            or 0
        )

        minutes = (
            duration_seconds
            // 60
        )

        seconds = (
            duration_seconds
            % 60
        )

        duration = QLabel(
            f"YouTube  •  "
            f"{minutes}:{seconds:02d}"
        )

        title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        }
        """)

        channel.setStyleSheet("""
        QLabel {
            color: #AFA4C8;
            font-size: 11px;
            background: transparent;
        }
        """)

        duration.setStyleSheet("""
        QLabel {
            color: #8B5CF6;
            font-size: 10px;
            font-weight: 600;
            background: transparent;
        }
        """)

        info.addWidget(
            title
        )

        info.addWidget(
            channel
        )

        info.addWidget(
            duration
        )

        info.addStretch()

        row.addLayout(
            info,
            1
        )

        # ====================================================
        # PLAY
        # ====================================================

        play_button = QLabel(
            "▶  Play"
        )

        play_button.setFixedSize(
            76,
            36
        )

        play_button.setAlignment(
            Qt.AlignCenter
        )

        play_button.setCursor(
            Qt.PointingHandCursor
        )

        play_button.setStyleSheet("""
        QLabel {
            color: white;
            background: #7C3AED;
            border-radius: 18px;
            font-size: 11px;
            font-weight: 700;
        }

        QLabel:hover {
            background: #8B5CF6;
        }
        """)

        play_button.mousePressEvent = (
            lambda event,
            selected=dict(item):
            self.handle_youtube_play(
                selected
            )
        )

        row.addWidget(
            play_button
        )

        # ====================================================
        # REMOVE FAVORITE
        # ====================================================

        remove_button = QLabel(
            "♥"
        )

        remove_button.setFixedSize(
            38,
            38
        )

        remove_button.setAlignment(
            Qt.AlignCenter
        )

        remove_button.setCursor(
            Qt.PointingHandCursor
        )

        remove_button.setStyleSheet("""
        QLabel {
            color: #C084FC;
            background: rgba(124,58,237,22);
            border: 1px solid rgba(139,92,246,80);
            border-radius: 19px;
            font-size: 17px;
        }

        QLabel:hover {
            color: white;
            background: rgba(124,58,237,60);
        }
        """)

        remove_button.mousePressEvent = (
            lambda event,
            selected=dict(item):
            self.remove_youtube_favorite(
                selected
            )
        )

        row.addWidget(
            remove_button
        )

        # ====================================================
        # CARD THEME
        # ====================================================

        if self.current_is_dark:

            card.setStyleSheet("""
            QFrame#YouTubeFavoriteCard {
                background: #151024;
                border: 1px solid #2D2348;
                border-radius: 18px;
            }

            QFrame#YouTubeFavoriteCard:hover {
                border: 1px solid #7C3AED;
                background: #19112B;
            }
            """)

        else:

            card.setStyleSheet("""
            QFrame#YouTubeFavoriteCard {
                background: #F4EEF8;
                border: 1px solid #DCCEF0;
                border-radius: 18px;
            }

            QFrame#YouTubeFavoriteCard:hover {
                border: 1px solid #8B5CF6;
                background: #EEE5F6;
            }
            """)

        return card


    # ========================================================
    # PLAY YOUTUBE FAVORITE
    # ========================================================

    def handle_youtube_play(
        self,
        item
    ):

        self.youtube_play_requested.emit(
            item
        )

    # ========================================================
    # REMOVE YOUTUBE FAVORITE
    # ========================================================

    def remove_youtube_favorite(
        self,
        item
    ):

        youtube_favorites_store.remove(
            item
        )

        self.reload_favorites()

    # ========================================================
    # LOAD YOUTUBE THUMBNAIL
    # ========================================================

    def load_youtube_thumbnail(
        self,
        image_url,
        label
    ):

        url = QUrl(
            str(
                image_url
                or ""
            )
        )

        if not url.isValid():

            return

        request = QNetworkRequest(
            url
        )

        request.setRawHeader(
            b"User-Agent",
            b"Mozilla/5.0 LYRx"
        )

        reply = (
            self.youtube_network.get(
                request
            )
        )

        self.youtube_replies.append(
            reply
        )

        reply.finished.connect(
            lambda r=reply,
            target=label:
            self.youtube_thumbnail_loaded(
                r,
                target
            )
        )

    # ========================================================
    # YOUTUBE THUMBNAIL LOADED
    # ========================================================

    def youtube_thumbnail_loaded(
        self,
        reply,
        label
    ):

        try:

            data = bytes(
                reply.readAll()
            )

            pixmap = QPixmap()

            if not pixmap.loadFromData(
                data
            ):

                return

            pixmap = pixmap.scaled(
                88,
                88,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            label.clear()

            label.setPixmap(
                pixmap
            )

        except RuntimeError:

            pass

        except Exception as error:

            print(
                "YT favorite thumbnail error:",
                error
            )

        finally:

            try:

                self.youtube_replies.remove(
                    reply
                )

            except Exception:

                pass

            try:

                reply.deleteLater()

            except Exception:

                pass

    # ========================================================
    # PLAY FAVORITE
    # ========================================================

    def handle_play_request(
        self,
        image_path,
        title,
        artist
    ):

        self.play_requested.emit(
            image_path,
            title,
            artist
        )

    # ========================================================
    # FAVORITE CHANGED
    # ========================================================

    def handle_favorite_changed(
        self,
        image_path,
        title,
        is_favorite
    ):

        if not is_favorite:

            self.reload_favorites()

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.current_is_dark = bool(
            is_dark
        )

        if self.current_is_dark:

            title_color = "#FFFFFF"
            subtitle_color = "#AFA4C8"
            count_color = "#9B7AFF"

            empty_bg = "#151024"
            empty_border = "#2D2348"

            empty_title_color = "#FFFFFF"
            empty_text_color = "#8F86AA"

        else:

            title_color = "#302744"
            subtitle_color = "#766783"
            count_color = "#7C3AED"

            empty_bg = "#F4EEF8"
            empty_border = "#DCCEF0"

            empty_title_color = "#302744"
            empty_text_color = "#81728F"

        self.title.setStyleSheet(
            f"""
            QLabel {{

                color: {title_color};

                font-size: 32px;

                font-weight: 800;

                background: transparent;

                border: none;
            }}
            """
        )

        self.subtitle.setStyleSheet(
            f"""
            QLabel {{

                color: {subtitle_color};

                font-size: 14px;

                background: transparent;

                border: none;
            }}
            """
        )

        self.count_label.setStyleSheet(
            f"""
            QLabel {{

                color: {count_color};

                font-size: 13px;

                font-weight: 600;

                background: transparent;

                border: none;
            }}
            """
        )

        self.empty_state.setStyleSheet(
            f"""
            QFrame#EmptyState {{

                background: {empty_bg};

                border: 1px solid {empty_border};

                border-radius: 22px;
            }}
            """
        )

        self.empty_title.setStyleSheet(
            f"""
            QLabel {{

                color: {empty_title_color};

                font-size: 20px;

                font-weight: 700;

                background: transparent;

                border: none;
            }}
            """
        )

        self.empty_text.setStyleSheet(
            f"""
            QLabel {{

                color: {empty_text_color};

                font-size: 13px;

                background: transparent;

                border: none;
            }}
            """
        )

        # Update existing cards
        for card in self.favorite_cards:

            try:

                card.set_theme_state(
                    self.current_is_dark
                )

            except Exception as error:

                print(
                    "Favorite card theme error:",
                    error
                )

        self.update()

    # ========================================================
    # PAINT EVENT
    # ========================================================

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

        # ====================================================
        # BACKGROUND
        # ====================================================

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
                QColor("#F7F4FB")
            )

            gradient.setColorAt(
                0.45,
                QColor("#F0EAF7")
            )

            gradient.setColorAt(
                1.0,
                QColor("#E9E1F1")
            )

        painter.fillRect(
            rect,
            gradient
        )

        # ====================================================
        # TOP PURPLE GLOW
        # ====================================================

        painter.setPen(
            Qt.NoPen
        )

        if self.current_is_dark:

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    24
                )
            )

        else:

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    14
                )
            )

        painter.drawEllipse(
            -180,
            -180,
            500,
            400
        )

        # ====================================================
        # RIGHT GLOW
        # ====================================================

        if self.current_is_dark:

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    16
                )
            )

        else:

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    10
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