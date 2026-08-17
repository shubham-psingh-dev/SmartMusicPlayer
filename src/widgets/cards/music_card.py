import json
from pathlib import Path

from PySide6.QtCore import Qt, Signal
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

        self.setStyleSheet("""
        QLabel {
            background: #211633;
            border: none;
            border-radius: 18px;
        }
        """)

    def paintEvent(self, event):

        if self.pixmap() is None:

            super().paintEvent(event)

            return

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        path = QPainterPath()

        path.addRoundedRect(
            self.rect(),
            18,
            18
        )

        painter.setClipPath(
            path
        )

        painter.drawPixmap(
            self.rect(),
            self.pixmap()
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

        self.is_hovered = False
        self.current_is_dark = True

        # ----------------------------------------------------
        # FAVORITE STATE
        # ----------------------------------------------------

        self.is_favorite = False

        # ----------------------------------------------------
        # CARD SIZE
        # ----------------------------------------------------

        # IMPORTANT:
        # 150 cover + 10 left + 10 right = 170
        # So 168 was too small.
        self.setFixedWidth(
            176
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

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            10,
            10,
            10,
            12
        )

        root.setSpacing(
            8
        )

        # ====================================================
        # COVER AREA
        # ====================================================

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

        # ====================================================
        # COVER IMAGE
        # ====================================================

        self.cover = CoverLabel()

        cover_layout.addWidget(
            self.cover
        )

        # ====================================================
        # PLAY BUTTON
        # ====================================================

        self.play_btn = QPushButton(
            "▶"
        )

        self.play_btn.setFixedSize(
            50,
            50
        )

        self.play_btn.setCursor(
            Qt.PointingHandCursor
        )

        self.play_btn.setObjectName(
            "PlayButton"
        )

        self.play_btn.setFocusPolicy(
            Qt.NoFocus
        )

        self.play_btn.setStyleSheet("""
        QPushButton#PlayButton {

            background: #8B5CF6;

            color: white;

            border: 2px solid rgba(255,255,255,80);

            border-radius: 25px;

            font-family: "Segoe UI Symbol";

            font-size: 18px;

            font-weight: 700;

            padding: 0px;

            margin: 0px;
        }

        QPushButton#PlayButton:hover {

            background: #A970FF;

            border: 2px solid rgba(255,255,255,140);
        }

        QPushButton#PlayButton:pressed {

            background: #6D28D9;

            padding-top: 1px;
        }
        """)

        self.play_btn.hide()

        # IMPORTANT:
        # Direct child of cover_frame.
        self.play_btn.setParent(
            self.cover_frame
        )

        self.play_btn.clicked.connect(
            self.request_play
        )

        # ====================================================
        # FAVORITE BUTTON
        # ====================================================

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

        self.favorite_btn.setFocusPolicy(
            Qt.NoFocus
        )

        self.favorite_btn.setStyleSheet("""
        QPushButton#FavoriteButton {

            background: rgba(15, 10, 25, 210);

            color: white;

            border: 1px solid rgba(255,255,255,70);

            border-radius: 17px;

            font-family: "Segoe UI Symbol";

            font-size: 21px;

            font-weight: 400;

            padding: 0px;

            margin: 0px;
        }

        QPushButton#FavoriteButton:hover {

            background: rgba(124, 58, 237, 230);

            color: white;

            border: 1px solid rgba(255,255,255,130);
        }

        QPushButton#FavoriteButton:pressed {

            background: rgba(109, 40, 217, 240);
        }
        """)

        self.favorite_btn.hide()

        self.favorite_btn.setParent(
            self.cover_frame
        )

        self.favorite_btn.clicked.connect(
            self.toggle_favorite
        )

        # ====================================================
        # TITLE
        # ====================================================

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

        # ====================================================
        # ARTIST
        # ====================================================

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

        # ====================================================
        # DURATION
        # ====================================================

        self.duration = QLabel(
            "3:45"
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

        # ====================================================
        # ADD TO LAYOUT
        # ====================================================

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

        # Make sure overlay buttons stay above cover.
        self.play_btn.raise_()
        self.favorite_btn.raise_()

    # ========================================================
    # LOAD COVER
    # ========================================================

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

        # ----------------------------------------------------
        # IMAGE FOUND
        # ----------------------------------------------------

        if image_file:

            pixmap = QPixmap(
                str(image_file)
            )

            if not pixmap.isNull():

                scaled = pixmap.scaled(
                    146,
                    146,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                self.cover.setPixmap(
                    scaled
                )

                return

        # ----------------------------------------------------
        # IMAGE NOT FOUND
        # ----------------------------------------------------

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

            font-family: "Segoe UI Symbol";

            font-size: 42px;

            border-radius: 18px;
        }
        """)

    # ========================================================
    # FAVORITES
    # ========================================================

    def load_favorite_state(self):

        favorites = self.read_favorites()

        self.is_favorite = any(
            item.get("image_path") == self.image_path
            for item in favorites
            if isinstance(item, dict)
        )

        self.update_favorite_button()

    # --------------------------------------------------------

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

    # --------------------------------------------------------

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

    # --------------------------------------------------------

    def toggle_favorite(self):

        favorites = self.read_favorites()

        # ====================================================
        # REMOVE
        # ====================================================

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

        # ====================================================
        # ADD
        # ====================================================

        else:

            favorite_item = {
                "image_path": self.image_path,
                "title": self.title_text,
                "artist": self.artist_text,
            }

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

    # --------------------------------------------------------

    def update_favorite_button(self):

        if self.is_favorite:

            self.favorite_btn.setText(
                "♥"
            )

            if self.current_is_dark:

                self.favorite_btn.setStyleSheet("""
                QPushButton#FavoriteButton {

                    background: rgba(124, 58, 237, 225);

                    color: #FF7AC8;

                    border: 1px solid rgba(255,255,255,110);

                    border-radius: 17px;

                    font-family: "Segoe UI Symbol";

                    font-size: 21px;

                    font-weight: 700;

                    padding: 0px;

                    margin: 0px;
                }

                QPushButton#FavoriteButton:hover {

                    background: rgba(139, 92, 246, 245);

                    color: #FF9AD8;

                    border: 1px solid rgba(255,255,255,150);
                }

                QPushButton#FavoriteButton:pressed {

                    background: rgba(109, 40, 217, 250);
                }
                """)

            else:

                self.favorite_btn.setStyleSheet("""
                QPushButton#FavoriteButton {

                    background: rgba(124, 58, 237, 220);

                    color: #FF4FA3;

                    border: 1px solid rgba(124,58,237,100);

                    border-radius: 17px;

                    font-family: "Segoe UI Symbol";

                    font-size: 21px;

                    font-weight: 700;

                    padding: 0px;

                    margin: 0px;
                }

                QPushButton#FavoriteButton:hover {

                    background: rgba(139,92,246,235);

                    color: #FF78B8;
                }

                QPushButton#FavoriteButton:pressed {

                    background: rgba(109,40,217,245);
                }
                """)

        else:

            self.favorite_btn.setText(
                "♡"
            )

            if self.current_is_dark:

                self.favorite_btn.setStyleSheet("""
                QPushButton#FavoriteButton {

                    background: rgba(15,10,25,210);

                    color: white;

                    border: 1px solid rgba(255,255,255,70);

                    border-radius: 17px;

                    font-family: "Segoe UI Symbol";

                    font-size: 21px;

                    font-weight: 400;

                    padding: 0px;

                    margin: 0px;
                }

                QPushButton#FavoriteButton:hover {

                    background: rgba(124,58,237,230);

                    color: white;

                    border: 1px solid rgba(255,255,255,130);
                }

                QPushButton#FavoriteButton:pressed {

                    background: rgba(109,40,217,240);
                }
                """)

            else:

                self.favorite_btn.setStyleSheet("""
                QPushButton#FavoriteButton {

                    background: rgba(255,255,255,220);

                    color: #67567D;

                    border: 1px solid rgba(124,58,237,55);

                    border-radius: 17px;

                    font-family: "Segoe UI Symbol";

                    font-size: 21px;

                    font-weight: 400;

                    padding: 0px;

                    margin: 0px;
                }

                QPushButton#FavoriteButton:hover {

                    background: rgba(124,58,237,225);

                    color: white;

                    border: 1px solid rgba(124,58,237,120);
                }

                QPushButton#FavoriteButton:pressed {

                    background: rgba(109,40,217,240);
                }
                """)

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
            artist_color = "#AFA4C8"
            duration_color = "#756A91"
            cover_bg = "#211633"

        else:

            title_color = "#302744"
            artist_color = "#766783"
            duration_color = "#8A7899"
            cover_bg = "#E5DCEB"

        self.title.setStyleSheet(
            f"""
            QLabel {{

                color: {title_color};

                font-size: 15px;

                font-weight: 700;

                background: transparent;

                border: none;

                padding: 0px;
            }}
            """
        )

        self.artist.setStyleSheet(
            f"""
            QLabel {{

                color: {artist_color};

                font-size: 13px;

                background: transparent;

                border: none;

                padding: 0px;
            }}
            """
        )

        self.duration.setStyleSheet(
            f"""
            QLabel {{

                color: {duration_color};

                font-size: 11px;

                background: transparent;

                border: none;

                padding: 0px;
            }}
            """
        )

        self.cover_frame.setStyleSheet(
            f"""
            QFrame#CoverFrame {{

                background: {cover_bg};

                border: 1px solid rgba(139,92,246,45);

                border-radius: 20px;
            }}
            """
        )

        self.cover.setStyleSheet(
            f"""
            QLabel {{

                background: {cover_bg};

                border: none;

                border-radius: 18px;
            }}
            """
        )

        self.update_favorite_button()

        self.update()

    # ========================================================
    # SHADOW
    # ========================================================

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

    # ========================================================
    # POSITION PLAY BUTTON
    # ========================================================

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

        self.play_btn.raise_()

    # ========================================================
    # POSITION FAVORITE BUTTON
    # ========================================================

    def position_favorite_button(self):

        margin = 7

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

        self.favorite_btn.raise_()

    # ========================================================
    # RESIZE EVENT
    # ========================================================

    def resizeEvent(
        self,
        event
    ):

        self.position_play_button()

        self.position_favorite_button()

        super().resizeEvent(
            event
        )

    # ========================================================
    # HOVER ENTER
    # ========================================================

    def enterEvent(
        self,
        event
    ):

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

    # ========================================================
    # HOVER LEAVE
    # ========================================================

    def leaveEvent(
        self,
        event
    ):

        self.is_hovered = False

        self.play_btn.hide()

        self.favorite_btn.hide()

        if self.current_is_dark:

            bg = "#211633"

        else:

            bg = "#E5DCEB"

        self.cover_frame.setStyleSheet(
            f"""
            QFrame#CoverFrame {{

                background: {bg};

                border: 1px solid rgba(139,92,246,45);

                border-radius: 20px;
            }}
            """
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

        super().leaveEvent(
            event
        )

    # ========================================================
    # PLAY REQUEST
    # ========================================================

    def request_play(self):

        self.play_requested.emit(
            self.image_path,
            self.title_text,
            self.artist_text
        )

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

        # ----------------------------------------------------
        # CARD SHAPE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # GRADIENT
        # ----------------------------------------------------

        gradient = QLinearGradient(
            0,
            0,
            0,
            rect.height()
        )

        if self.current_is_dark:

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

        else:

            gradient.setColorAt(
                0.0,
                QColor("#F4EEF8")
            )

            gradient.setColorAt(
                0.55,
                QColor("#ECE4F2")
            )

            gradient.setColorAt(
                1.0,
                QColor("#E3D9EA")
            )

        painter.fillPath(
            path,
            gradient
        )

        # ----------------------------------------------------
        # BORDER
        # ----------------------------------------------------

        if self.is_hovered:

            border_color = QColor(
                139,
                               92,
                246,
                150
            )

        else:

            border_color = QColor(
                124,
                58,
                237,
                42 if self.current_is_dark else 35
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

        # ----------------------------------------------------
        # TOP GLOW
        # ----------------------------------------------------

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                139,
                92,
                246,
                15 if self.current_is_dark else 9
            )
        )

        painter.drawEllipse(
            rect.width() - 75,
            -30,
            100,
            100
        )

        # ----------------------------------------------------
        # BOTTOM GLOW
        # ----------------------------------------------------

        painter.setBrush(
            QColor(
                168,
                85,
                247,
                10 if self.current_is_dark else 7
            )
        )

        painter.drawEllipse(
            -25,
            rect.height() - 70,
            90,
            90
        )

        painter.end()