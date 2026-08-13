import json
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import (
    QColor,
    QPainter,
    QLinearGradient,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
)


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()

# music_player_desktop/
PROJECT_DIR = FILE_DIR.parents[3]

# music_player_desktop/src/
SRC_DIR = FILE_DIR.parents[2]

# Persistent favorites file
FAVORITES_FILE = PROJECT_DIR / "favorites.json"


# ============================================================
# COVER LABEL
# ============================================================

class CoverLabel(QLabel):

    def __init__(self):
        super().__init__()

        self.setFixedSize(
            146,
            146
        )

        self.setAlignment(
            Qt.AlignCenter
        )

        # Keep the label transparent. The rounded background and image
        # are painted together below so the pixmap can never escape
        # the rounded corners.
        self.setStyleSheet("""
        QLabel {
            background: transparent;
            border: none;
        }
        """)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        rect = self.rect()

        # One single rounded clipping path for both the background
        # and the album artwork. This prevents square image corners
        # from appearing during hover or repaint events.
        path = QPainterPath()

        path.addRoundedRect(
            rect,
            18,
            18
        )

        painter.setClipPath(
            path
        )

        # Background inside the same clip.
        painter.fillPath(
            path,
            QColor("#211633")
        )

        pixmap = self.pixmap()

        if pixmap is not None and not pixmap.isNull():
            painter.drawPixmap(
                rect,
                pixmap
            )

        painter.end()


# ============================================================
# MUSIC CARD
# ============================================================

class MusicCard(QFrame):

    play_requested = Signal(
        str,
        str,
        str
    )

    favorite_changed = Signal(
        str,
        str,
        bool
    )

    def __init__(
        self,
        image_path,
        title,
        artist
    ):

        super().__init__()

        self.image_path = image_path
        self.title_text = title
        self.artist_text = artist

        # Actual track durations used by the current library / Next Up list.
        # A fallback keeps the card safe for future tracks.
        durations = {
            "Believer": "3:24",
            "Faded": "3:32",
            "Arcade": "3:03",
            "Let Her Go": "4:12",
        }

        self.duration_text = durations.get(
            self.title_text,
            "0:00"
        )

        self.is_hovered = False

        # ------------------------------------------------
        # FAVORITE STATE
        # ------------------------------------------------

        self.is_favorite = False

        # ------------------------------------------------
        # CARD SIZE
        # ------------------------------------------------

        self.setFixedWidth(
            158
        )

        self.setMinimumHeight(
            310
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setObjectName(
            "MusicCard"
        )

        self.build_ui()

        self.load_cover()

        self.load_favorite_state()

        self.setup_shadow()

    # ============================================================
    # UI
    # ============================================================

    def build_ui(self):

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            2,
            10,
            2,
            12
        )

        root.setSpacing(
            9
        )

        # ========================================================
        # COVER AREA
        # ========================================================

        self.cover_frame = QFrame()

        self.cover_frame.setFixedSize(
            150,
            150
        )

        self.cover_frame.setObjectName(
            "CoverFrame"
        )

        self.cover_frame.setStyleSheet("""
        QFrame#CoverFrame {

            background: #211633;

            border: 1px solid rgba(139, 92, 246, 45);

            border-radius: 20px;
        }
        """)

        cover_layout = QVBoxLayout(
            self.cover_frame
        )

        cover_layout.setContentsMargins(
            2,
            2,
            2,
            2
        )

        cover_layout.setSpacing(
            0
        )

        # ========================================================
        # COVER IMAGE
        # ========================================================

        self.cover = CoverLabel()

        cover_layout.addWidget(
            self.cover
        )

        # ========================================================
        # PLAY BUTTON
        # ========================================================

        self.play_btn = QPushButton(
            "▶"
        )

        self.play_btn.setFixedSize(
            54,
            54
        )

        self.play_btn.setCursor(
            Qt.PointingHandCursor
        )

        self.play_btn.setObjectName(
            "PlayButton"
        )

        self.play_btn.setStyleSheet("""
        QPushButton#PlayButton {

            background: #8B5CF6;

            color: white;

            border: 2px solid rgba(255,255,255,45);

            border-radius: 27px;

            font-size: 19px;

            font-weight: 700;

            padding-left: 3px;
        }

        QPushButton#PlayButton:hover {

            background: #A970FF;

            border: 2px solid rgba(255,255,255,90);
        }

        QPushButton#PlayButton:pressed {

            background: #6D28D9;
        }
        """)

        self.play_btn.hide()

        self.play_btn.setParent(
            self.cover_frame
        )

        self.play_btn.clicked.connect(
            self.request_play
        )

        # ========================================================
        # FAVORITE BUTTON
        # ========================================================

        self.favorite_btn = QPushButton(
            "♡"
        )

        self.favorite_btn.setFixedSize(
            34,
            34
        )

        self.favorite_btn.setCursor(
            Qt.PointingHandCursor
        )

        self.favorite_btn.setObjectName(
            "FavoriteButton"
        )

        self.favorite_btn.setStyleSheet("""
        QPushButton#FavoriteButton {

            background: rgba(15, 10, 25, 185);

            color: white;

            border: 1px solid rgba(255,255,255,55);

            border-radius: 17px;

            font-size: 20px;

            font-weight: 600;
        }

        QPushButton#FavoriteButton:hover {

            background: rgba(124, 58, 237, 220);

            border: 1px solid rgba(255,255,255,100);
        }
        """)

        self.favorite_btn.hide()

        self.favorite_btn.setParent(
            self.cover_frame
        )

        self.favorite_btn.clicked.connect(
            self.toggle_favorite
        )

        # ========================================================
        # TITLE
        # ========================================================

        self.title = QLabel(
            self.title_text
        )

        self.title.setWordWrap(
            False
        )

        self.title.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        self.title.setStyleSheet("""
        QLabel {

            color: #FFFFFF;

            font-size: 15px;

            font-weight: 700;

            background: transparent;

            border: none;

            padding: 0px;
        }
        """)

        # ========================================================
        # ARTIST
        # ========================================================

        self.artist = QLabel(
            self.artist_text
        )

        self.artist.setWordWrap(
            False
        )

        self.artist.setStyleSheet("""
        QLabel {

            color: #AFA4C8;

            font-size: 13px;

            background: transparent;

            border: none;

            padding: 0px;
        }
        """)

        # ========================================================
        # DURATION
        # ========================================================

        self.duration = QLabel(
            self.duration_text
        )

        self.duration.setStyleSheet("""
        QLabel {

            color: #756A91;

            font-size: 11px;

            background: transparent;

            border: none;

            padding: 0px;
        }
        """)

        # ========================================================
        # ADD TO LAYOUT
        # ========================================================

        root.addWidget(
            self.cover_frame,
            alignment=Qt.AlignCenter
        )

        root.addSpacing(
            2
        )

        root.addWidget(
            self.title
        )

        root.addWidget(
            self.artist
        )

        root.addWidget(
            self.duration
        )

        root.addStretch()

    # ============================================================
    # LOAD COVER
    # ============================================================

    def load_cover(self):

        possible_paths = [

            PROJECT_DIR / self.image_path,

            SRC_DIR / self.image_path,

            Path.cwd() / self.image_path,

            Path(self.image_path),
        ]

        image_file = None

        for path in possible_paths:

            try:

                if path.exists() and path.is_file():

                    image_file = path

                    break

            except Exception:

                continue

        # --------------------------------------------------------
        # IMAGE FOUND
        # --------------------------------------------------------

        if image_file:

            pixmap = QPixmap(
                str(image_file)
            )

            if not pixmap.isNull():

                scaled = pixmap.scaled(
                    146,
                    146,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                self.cover.setPixmap(
                    scaled
                )

                return

        # --------------------------------------------------------
        # IMAGE NOT FOUND
        # --------------------------------------------------------

        self.cover.setPixmap(
            QPixmap()
        )

        self.cover.setText(
            "♪"
        )

        self.cover.setStyleSheet("""
        QLabel {

            background: #211633;

            color: #8B5CF6;

            font-size: 42px;

            border-radius: 18px;
        }
        """)

    # ============================================================
    # FAVORITES
    # ============================================================

    def load_favorite_state(self):

        favorites = self.read_favorites()

        self.is_favorite = any(
            item.get("image_path") == self.image_path
            for item in favorites
            if isinstance(item, dict)
        )

        self.update_favorite_button()

    # ------------------------------------------------------------

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

                    return data

        except (
            json.JSONDecodeError,
            OSError,
            TypeError
        ):

            pass

        return []

    # ------------------------------------------------------------

    def write_favorites(
        self,
        favorites
    ):

        try:

            with open(
                FAVORITES_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    favorites,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except OSError as error:

            print(
                "Could not save favorites:",
                error
            )

    # ------------------------------------------------------------

    def toggle_favorite(self):

        favorites = self.read_favorites()

        # ========================================================
        # REMOVE FAVORITE
        # ========================================================

        if self.is_favorite:

            favorites = [
                item
                for item in favorites
                if not (
                    isinstance(item, dict)
                    and item.get("image_path")
                    == self.image_path
                )
            ]

            self.is_favorite = False

            print(
                f"Removed from favorites: "
                f"{self.title_text}"
            )

        # ========================================================
        # ADD FAVORITE
        # ========================================================

        else:

            favorite_item = {
                "image_path": self.image_path,
                "title": self.title_text,
                "artist": self.artist_text,
            }

            # Prevent duplicates
            already_exists = any(
                isinstance(item, dict)
                and item.get("image_path")
                == self.image_path
                for item in favorites
            )

            if not already_exists:

                favorites.append(
                    favorite_item
                )

            self.is_favorite = True

            print(
                f"Added to favorites: "
                f"{self.title_text}"
            )

        self.write_favorites(
            favorites
        )

        self.update_favorite_button()

        self.favorite_changed.emit(
            self.image_path,
            self.title_text,
            self.is_favorite
        )

    # ------------------------------------------------------------

    def update_favorite_button(self):

        if self.is_favorite:

            self.favorite_btn.setText(
                "♥"
            )

            self.favorite_btn.setStyleSheet("""
            QPushButton#FavoriteButton {

                background: rgba(124, 58, 237, 220);

                color: #FF7AC8;

                border: 1px solid rgba(255,255,255,100);

                border-radius: 17px;

                font-size: 20px;

                font-weight: 700;
            }

            QPushButton#FavoriteButton:hover {

                background: rgba(139, 92, 246, 240);

                color: #FF9AD8;
            }
            """)

        else:

            self.favorite_btn.setText(
                "♡"
            )

            self.favorite_btn.setStyleSheet("""
            QPushButton#FavoriteButton {

                background: rgba(15, 10, 25, 185);

                color: white;

                border: 1px solid rgba(255,255,255,55);

                border-radius: 17px;

                font-size: 20px;

                font-weight: 600;
            }

            QPushButton#FavoriteButton:hover {

                background: rgba(124, 58, 237, 220);

                border: 1px solid rgba(255,255,255,100);
            }
            """)

    # ============================================================
    # SHADOW
    # ============================================================

    def setup_shadow(self):

        self.shadow = QGraphicsDropShadowEffect(
            self
        )

        self.shadow.setBlurRadius(
            24
        )

        self.shadow.setOffset(
            0,
            8
        )

        self.shadow.setColor(
            QColor(
                124,
                58,
                237,
                55
            )
        )

        self.setGraphicsEffect(
            self.shadow
        )

    # ============================================================
    # POSITION PLAY BUTTON
    # ============================================================

    def position_play_button(self):

        x = (
            self.cover_frame.width()
            - self.play_btn.width()
        ) // 2

        y = (
            self.cover_frame.height()
            - self.play_btn.height()
        ) // 2

        self.play_btn.move(
            x,
            y
        )

    # ============================================================
    # POSITION FAVORITE BUTTON
    # ============================================================

    def position_favorite_button(self):

        margin = 8

        x = (
            self.cover_frame.width()
            - self.favorite_btn.width()
            - margin
        )

        y = margin

        self.favorite_btn.move(
            x,
            y
        )

    # ============================================================
    # RESIZE EVENT
    # ============================================================

    def resizeEvent(self, event):

        self.position_play_button()

        self.position_favorite_button()

        super().resizeEvent(
            event
        )

    # ============================================================
    # HOVER ENTER
    # ============================================================

    def enterEvent(self, event):

        self.is_hovered = True

        self.play_btn.show()

        self.favorite_btn.show()

        self.position_play_button()

        self.position_favorite_button()

        self.cover_frame.setStyleSheet("""
        QFrame#CoverFrame {

            background: #24163E;

            border: 2px solid #8B5CF6;

            border-radius: 20px;
        }
        """)

        self.shadow.setBlurRadius(
            34
        )

        self.shadow.setOffset(
            0,
            10
        )

        self.shadow.setColor(
            QColor(
                139,
                92,
                246,
                105
            )
        )

        super().enterEvent(
            event
        )

    # ============================================================
    # HOVER LEAVE
    # ============================================================

    def leaveEvent(self, event):

        self.is_hovered = False

        self.play_btn.hide()

        self.favorite_btn.hide()

        self.cover_frame.setStyleSheet("""
        QFrame#CoverFrame {

            background: #211633;

            border: 1px solid rgba(139, 92, 246, 45);

            border-radius: 20px;
        }
        """)

        self.shadow.setBlurRadius(
            24
        )

        self.shadow.setOffset(
            0,
            8
        )

        self.shadow.setColor(
            QColor(
                124,
                58,
                237,
                55
            )
        )

        super().leaveEvent(
            event
        )

    # ============================================================
    # PLAY REQUEST
    # ============================================================

    def request_play(self):

        self.play_requested.emit(
            self.image_path,
            self.title_text,
            self.artist_text
        )

    # ============================================================
    # PAINT EVENT
    # ============================================================

    def paintEvent(self, event):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # --------------------------------------------------------
        # CARD SHAPE
        # --------------------------------------------------------

        path = QPainterPath()

        path.addRoundedRect(
            rect.adjusted(
                1,
                1,
                -1,
                -1
            ),
            20,
            20
        )

        # --------------------------------------------------------
        # DARK PURPLE GRADIENT
        # --------------------------------------------------------

        gradient = QLinearGradient(
            0,
            0,
            0,
            rect.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#211633")
        )

        gradient.setColorAt(
            0.55,
            QColor("#191226")
        )

        gradient.setColorAt(
            1.0,
            QColor("#110D1B")
        )

        painter.fillPath(
            path,
            gradient
        )

        # --------------------------------------------------------
        # BORDER
        # --------------------------------------------------------

        if self.is_hovered:

            border_color = QColor(
                139,
                92,
                246,
                150
            )

        else:

            border_color = QColor(
                139,
                92,
                246,
                42
            )

        pen = QPen(
            border_color
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

        # --------------------------------------------------------
        # TOP PURPLE GLOW
        # --------------------------------------------------------

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                139,
                92,
                246,
                15
            )
        )

        painter.drawEllipse(
            rect.width() - 75,
            -30,
            100,
            100
        )

        # --------------------------------------------------------
        # BOTTOM GLOW
        # --------------------------------------------------------

        painter.setBrush(
            QColor(
                168,
                85,
                247,
                10
            )
        )

        painter.drawEllipse(
            -25,
            rect.height() - 70,
            90,
            90
        )

        painter.end()