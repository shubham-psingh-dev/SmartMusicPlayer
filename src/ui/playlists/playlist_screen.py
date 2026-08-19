from pathlib import Path
import random

from PySide6.QtCore import (
    Qt,
    Signal,
)

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
    QGridLayout,
    QFrame,
    QLabel,
    QPushButton,
    QToolButton,
    QScrollArea,
    QSizePolicy,
    QLineEdit,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
)

from widgets.sidebar import Sidebar
from ui.player.now_playing import NowPlaying

from data.playlist_store import (
    playlist_store,
    DEFAULT_QUEUE,
)


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()

PROJECT_DIR = FILE_DIR.parents[2]
SRC_DIR = FILE_DIR.parents[1]


# ============================================================
# ASSET FINDER
# ============================================================

def find_asset(relative_path):

    if not relative_path:
        return None

    relative_path = Path(relative_path)

    candidates = [

        PROJECT_DIR / relative_path,

        SRC_DIR / relative_path,

        Path.cwd() / relative_path,

        Path.cwd() / "src" / relative_path,

        FILE_DIR.parent / relative_path,

        FILE_DIR.parent.parent / relative_path,

        FILE_DIR.parent.parent.parent / relative_path,

        PROJECT_DIR
        / "assets"
        / relative_path.name,

        SRC_DIR
        / "assets"
        / relative_path.name,

        PROJECT_DIR
        / "src"
        / relative_path,

        PROJECT_DIR
        / "src"
        / "assets"
        / relative_path,

        SRC_DIR
        / "assets"
        / "album_art"
        / relative_path.name,

        PROJECT_DIR
        / "assets"
        / "album_art"
        / relative_path.name,

        Path.cwd()
        / "assets"
        / "album_art"
        / relative_path.name,

        Path.cwd()
        / "src"
        / "assets"
        / "album_art"
        / relative_path.name,
    ]

    unique_candidates = []

    for candidate in candidates:

        try:
            candidate = candidate.resolve()

        except Exception:
            continue

        if candidate not in unique_candidates:
            unique_candidates.append(candidate)

    for candidate in unique_candidates:

        try:

            if candidate.is_file():
                return candidate

        except Exception:
            pass

    print(
        "Asset not found:",
        relative_path
    )

    return None


# ============================================================
# CREATE PLAYLIST DIALOG
# ============================================================

class CreatePlaylistDialog(QDialog):

    def __init__(
        self,
        parent=None,
        is_dark=True,
    ):

        super().__init__(parent)

        self.is_dark = is_dark

        self.setWindowTitle(
            "Create Playlist"
        )

        self.setFixedWidth(
            430
        )

        self.build_ui()
        self.apply_theme()

    # ========================================================
    # BUILD
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            28,
            26,
            28,
            24
        )

        layout.setSpacing(
            18
        )

        title = QLabel(
            "Create New Playlist"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: 800;
                color: white;
                background: transparent;
            }
            """
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "Give your playlist a name and description."
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #9C92B8;
                background: transparent;
            }
            """
        )

        layout.addWidget(subtitle)

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "Playlist name"
        )

        self.name_input.setMinimumHeight(
            42
        )

        layout.addWidget(
            self.name_input
        )

        self.description_input = QLineEdit()

        self.description_input.setPlaceholderText(
            "Description (optional)"
        )

        self.description_input.setMinimumHeight(
            42
        )

        layout.addWidget(
            self.description_input
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel
            |
            QDialogButtonBox.Ok
        )

        buttons.accepted.connect(
            self.validate_and_accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(buttons)

        self.ok_button = buttons.button(
            QDialogButtonBox.Ok
        )

        if self.ok_button:

            self.ok_button.setText(
                "Create Playlist"
            )

    # ========================================================
    # VALIDATE
    # ========================================================

    def validate_and_accept(self):

        name = (
            self.name_input
            .text()
            .strip()
        )

        if not name:

            QMessageBox.warning(
                self,
                "Playlist Name",
                "Please enter a playlist name."
            )

            self.name_input.setFocus()

            return

        self.accept()

    # ========================================================
    # RESULT
    # ========================================================

    def playlist_name(self):

        return (
            self.name_input
            .text()
            .strip()
        )

    def playlist_description(self):

        return (
            self.description_input
            .text()
            .strip()
        )

    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(self):

        if self.is_dark:

            self.setStyleSheet(
                """
                QDialog {
                    background: #171126;
                }

                QLineEdit {
                    background: #110C1D;
                    border: 1px solid #332650;
                    border-radius: 11px;
                    padding: 0 13px;
                    color: white;
                    font-size: 13px;
                }

                QLineEdit:focus {
                    border: 1px solid #7C3AED;
                }

                QDialogButtonBox QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 9px;
                    padding: 9px 18px;
                    font-weight: 700;
                }

                QDialogButtonBox QPushButton:hover {
                    background: #8B5CF6;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QDialog {
                    background: #EEE9F4;
                }

                QLineEdit {
                    background: white;
                    border: 1px solid #D4C9E3;
                    border-radius: 11px;
                    padding: 0 13px;
                    color: #302744;
                    font-size: 13px;
                }

                QLineEdit:focus {
                    border: 1px solid #7C3AED;
                }

                QDialogButtonBox QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 9px;
                    padding: 9px 18px;
                    font-weight: 700;
                }

                QDialogButtonBox QPushButton:hover {
                    background: #8B5CF6;
                }
                """
            )


# ============================================================
# ADD TO PLAYLIST DIALOG
# ============================================================

class AddToPlaylistDialog(QDialog):

    playlist_selected = Signal(str)

    def __init__(
        self,
        playlists,
        song_title,
        parent=None,
        is_dark=True,
    ):

        super().__init__(parent)

        self.playlists = playlists
        self.song_title = song_title
        self.is_dark = is_dark

        self.selected_playlist_id = None

        self.setWindowTitle(
            "Add to Playlist"
        )

        self.setFixedWidth(
            440
        )

        self.build_ui()
        self.apply_theme()

    # ========================================================
    # BUILD
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            26,
            24,
            26,
            22
        )

        layout.setSpacing(
            14
        )

        title = QLabel(
            "Add to Playlist"
        )

        title.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 21px;
                font-weight: 800;
                background: transparent;
            }
            """
        )

        layout.addWidget(title)

        subtitle = QLabel(
            f'Select a playlist for "{self.song_title}"'
        )

        subtitle.setWordWrap(True)

        subtitle.setStyleSheet(
            """
            QLabel {
                color: #9C92B8;
                font-size: 12px;
                background: transparent;
            }
            """
        )

        layout.addWidget(subtitle)

        self.playlist_buttons = []

        for playlist in self.playlists:

            button = QPushButton()

            name = playlist.get(
                "name",
                "Playlist"
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

            button.setText(
                f"♫  {name}   •   {count} {word}"
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.setMinimumHeight(
                46
            )

            playlist_id = str(
                playlist.get(
                    "id",
                    ""
                )
            )

            button.clicked.connect(
                lambda checked=False,
                pid=playlist_id:
                self.select_playlist(pid)
            )

            layout.addWidget(button)

            self.playlist_buttons.append(
                button
            )

        if not self.playlists:

            empty = QLabel(
                "No playlists available."
            )

            empty.setAlignment(
                Qt.AlignCenter
            )

            empty.setMinimumHeight(
                70
            )

            layout.addWidget(empty)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(buttons)

    # ========================================================
    # SELECT
    # ========================================================

    def select_playlist(
        self,
        playlist_id
    ):

        self.selected_playlist_id = str(
            playlist_id
        )

        self.playlist_selected.emit(
            self.selected_playlist_id
        )

        self.accept()

    # ========================================================
    # RESULT
    # ========================================================

    def selected_id(self):

        return self.selected_playlist_id

    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(self):

        if self.is_dark:

            self.setStyleSheet(
                """
                QDialog {
                    background: #171126;
                }

                QPushButton {
                    background: #211735;
                    color: #F3EEFC;
                    border: 1px solid #3B2C55;
                    border-radius: 11px;
                    padding: 8px 12px;
                    text-align: left;
                    font-size: 12px;
                    font-weight: 650;
                }

                QPushButton:hover {
                    background: #30204C;
                    border: 1px solid #7C3AED;
                }

                QDialogButtonBox QPushButton {
                    background: #211735;
                    color: #B8ABC9;
                    border: 1px solid #3B2C55;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QDialog {
                    background: #EEE9F4;
                }

                QPushButton {
                    background: white;
                    color: #302744;
                    border: 1px solid #D4C9E3;
                    border-radius: 11px;
                    padding: 8px 12px;
                    text-align: left;
                    font-size: 12px;
                    font-weight: 650;
                }

                QPushButton:hover {
                    background: #F5F0FA;
                    border: 1px solid #7C3AED;
                }

                QDialogButtonBox QPushButton {
                    background: #F3EEF8;
                    color: #5B4D6B;
                    border: 1px solid #D4C9E3;
                }
                """
            )


# ============================================================
# PLAYLIST CARD
# ============================================================

class PlaylistCard(QFrame):

    play_requested = Signal(dict)
    open_requested = Signal(dict)
    delete_requested = Signal(str)

    def __init__(
        self,
        playlist_data,
        is_dark=True,
        parent=None,
    ):

        super().__init__(parent)

        self.playlist_data = playlist_data
        self.is_dark = is_dark

        self.setObjectName(
            "PlaylistCard"
        )

        self.setMinimumHeight(
            365
        )

        self.setMinimumWidth(
            210
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.build_ui()
        self.apply_theme()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        layout.setSpacing(
            8
        )

        self.thumbnail = QLabel()

        self.thumbnail.setFixedHeight(
            178
        )

        self.thumbnail.setAlignment(
            Qt.AlignCenter
        )

        self.thumbnail.setScaledContents(
            False
        )

        self.load_thumbnail()

        layout.addWidget(
            self.thumbnail
        )

        self.name_label = QLabel(
            self.playlist_data.get(
                "name",
                "Playlist"
            )
        )

        self.name_label.setWordWrap(True)

        layout.addWidget(
            self.name_label
        )

        self.description_label = QLabel(
            self.playlist_data.get(
                "description",
                ""
            )
        )

        self.description_label.setWordWrap(True)

        self.description_label.setMinimumHeight(
            34
        )

        layout.addWidget(
            self.description_label
        )

        self.count_label = QLabel(
            self.song_count_text()
        )

        layout.addWidget(
            self.count_label
        )

        button_row = QHBoxLayout()

        button_row.setContentsMargins(
            0,
            3,
            0,
            0
        )

        button_row.setSpacing(
            8
        )

        self.play_button = QPushButton(
            "▶  Play"
        )

        self.play_button.setCursor(
            Qt.PointingHandCursor
        )

        self.play_button.setMinimumHeight(
            36
        )

        self.play_button.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.play_button.clicked.connect(
            self.on_play_clicked
        )

        button_row.addWidget(
            self.play_button
        )

        self.open_button = QPushButton(
            "Open"
        )

        self.open_button.setCursor(
            Qt.PointingHandCursor
        )

        self.open_button.setFixedHeight(
            36
        )

        self.open_button.setMinimumWidth(
            58
        )

        self.open_button.clicked.connect(
            self.on_open_clicked
        )

        button_row.addWidget(
            self.open_button
        )

        self.delete_button = QToolButton()

        self.delete_button.setText(
            "×"
        )

        self.delete_button.setToolTip(
            "Delete playlist"
        )

        self.delete_button.setCursor(
            Qt.PointingHandCursor
        )

        self.delete_button.setFixedSize(
            36,
            36
        )

        self.delete_button.clicked.connect(
            self.on_delete_clicked
        )

        button_row.addWidget(
            self.delete_button
        )

        layout.addLayout(
            button_row
        )

    # ========================================================
    # THUMBNAIL
    # ========================================================

    def load_thumbnail(self):

        relative_path = (
            self.playlist_data.get(
                "thumbnail",
                ""
            )
        )

        if not relative_path:

            self.show_placeholder()

            return

        image_path = find_asset(
            relative_path
        )

        if image_path is None:

            self.show_placeholder()

            return

        pixmap = QPixmap(
            str(image_path)
        )

        if pixmap.isNull():

            self.show_placeholder()

            return

        scaled = pixmap.scaled(
            178,
            178,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        self.thumbnail.setPixmap(
            scaled
        )

        self.thumbnail.setText("")

    # ========================================================
    # PLACEHOLDER
    # ========================================================

    def show_placeholder(self):

        self.thumbnail.setPixmap(
            QPixmap()
        )

        self.thumbnail.setText(
            "♫"
        )

    # ========================================================
    # COUNT
    # ========================================================

    def song_count_text(self):

        count = len(
            self.playlist_data.get(
                "songs",
                []
            )
        )

        word = (
            "song"
            if count == 1
            else "songs"
        )

        return f"{count} {word}"

    # ========================================================
    # PLAY
    # ========================================================

    def on_play_clicked(self):

        self.play_requested.emit(
            self.playlist_data
        )

    # ========================================================
    # OPEN
    # ========================================================

    def on_open_clicked(self):

        self.open_requested.emit(
            self.playlist_data
        )

    # ========================================================
    # DELETE
    # ========================================================

    def on_delete_clicked(self):

        playlist_id = (
            self.playlist_data.get("id")
        )

        if not playlist_id:
            return

        self.delete_requested.emit(
            str(playlist_id)
        )

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.is_dark = bool(
            is_dark
        )

        self.apply_theme()

    # ========================================================
    # STYLE
    # ========================================================

    def apply_theme(self):

        if self.is_dark:

            self.setStyleSheet(
                """
                QFrame#PlaylistCard {
                    background: #151024;
                    border: 1px solid #30234A;
                    border-radius: 18px;
                }

                QFrame#PlaylistCard:hover {
                    background: #1B1430;
                    border: 1px solid #6741A8;
                }
                """
            )

            self.thumbnail.setStyleSheet(
                """
                QLabel {
                    background: #211735;
                    border-radius: 14px;
                    color: #A970FF;
                    font-size: 44px;
                    font-weight: 700;
                }
                """
            )

            self.name_label.setStyleSheet(
                """
                QLabel {
                    color: #FFFFFF;
                    font-size: 15px;
                    font-weight: 750;
                    background: transparent;
                }
                """
            )

            self.description_label.setStyleSheet(
                """
                QLabel {
                    color: #9186AB;
                    font-size: 11px;
                    background: transparent;
                }
                """
            )

            self.count_label.setStyleSheet(
                """
                QLabel {
                    color: #82769F;
                    font-size: 11px;
                    background: transparent;
                }
                """
            )

            self.play_button.setStyleSheet(
                """
                QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 9px;
                    font-size: 11px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #8B5CF6;
                }

                QPushButton:pressed {
                    background: #6D28D9;
                }
                """
            )

            self.open_button.setStyleSheet(
                """
                QPushButton {
                    background: #211735;
                    color: #D9D0E8;
                    border: 1px solid #3B2C55;
                    border-radius: 9px;
                    font-size: 11px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #30204C;
                    color: white;
                    border: 1px solid #6741A8;
                }
                """
            )

            self.delete_button.setStyleSheet(
                """
                QToolButton {
                    background: #211735;
                    color: #A99BC3;
                    border: 1px solid #3B2C55;
                    border-radius: 9px;
                    font-size: 16px;
                    font-weight: 700;
                }

                QToolButton:hover {
                    background: #3A1827;
                    color: #FF7A9A;
                    border: 1px solid #8A3855;
                }

                QToolButton:pressed {
                    background: #512238;
                    color: white;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QFrame#PlaylistCard {
                    background: #F8F5FB;
                    border: 1px solid #D8CEE5;
                    border-radius: 18px;
                }

                QFrame#PlaylistCard:hover {
                    background: #FFFFFF;
                    border: 1px solid #A982D8;
                }
                """
            )

            self.thumbnail.setStyleSheet(
                """
                QLabel {
                    background: #EEE8F5;
                    border-radius: 14px;
                    color: #7C3AED;
                    font-size: 44px;
                    font-weight: 700;
                }
                """
            )

            self.name_label.setStyleSheet(
                """
                QLabel {
                    color: #302744;
                    font-size: 15px;
                    font-weight: 750;
                    background: transparent;
                }
                """
            )

            self.description_label.setStyleSheet(
                """
                QLabel {
                    color: #756A88;
                    font-size: 11px;
                    background: transparent;
                }
                """
            )

            self.count_label.setStyleSheet(
                """
                QLabel {
                    color: #81748F;
                    font-size: 11px;
                    background: transparent;
                }
                """
            )

            self.play_button.setStyleSheet(
                """
                QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 9px;
                    font-size: 11px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #8B5CF6;
                }
                """
            )

            self.open_button.setStyleSheet(
                """
                QPushButton {
                    background: #EEE8F5;
                    color: #554668;
                    border: 1px solid #D4C8E2;
                    border-radius: 9px;
                    font-size: 11px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #F5EFFA;
                    color: #302744;
                    border: 1px solid #A982D8;
                }
                """
            )

            self.delete_button.setStyleSheet(
                """
                QToolButton {
                    background: #EEE8F5;
                    color: #6D607C;
                    border: 1px solid #D4C8E2;
                    border-radius: 9px;
                    font-size: 16px;
                    font-weight: 700;
                }

                QToolButton:hover {
                    background: #FBE8EE;
                    color: #C23D68;
                    border: 1px solid #D47A98;
                }
                """
            )


# ============================================================
# PLAYLIST SONG ROW
# ============================================================

class PlaylistSongRow(QFrame):

    play_requested = Signal(int)
    remove_requested = Signal(int)

    def __init__(
        self,
        song,
        index,
        is_dark=True,
        parent=None
    ):

        super().__init__(parent)

        self.song = song
        self.index = index
        self.is_dark = is_dark

        self.setObjectName(
            "PlaylistSongRow"
        )

        self.setMinimumHeight(
            76
        )

        self.build_ui()
        self.apply_theme()

    # ========================================================
    # BUILD
    # ========================================================

    def build_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            12,
            8,
            12,
            8
        )

        layout.setSpacing(
            12
        )

        self.art = QLabel()

        self.art.setFixedSize(
            58,
            58
        )

        self.art.setAlignment(
            Qt.AlignCenter
        )

        image_path = find_asset(
            self.song.get(
                "image",
                ""
            )
        )

        if image_path:

            pixmap = QPixmap(
                str(image_path)
            )

            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    58,
                    58,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                self.art.setPixmap(
                    pixmap
                )

        if self.art.pixmap() is None:

            self.art.setText(
                "♫"
            )

        layout.addWidget(
            self.art
        )

        info = QVBoxLayout()

        info.setSpacing(
            3
        )

        self.title_label = QLabel(
            self.song.get(
                "title",
                "Unknown Song"
            )
        )

        self.artist_label = QLabel(
            self.song.get(
                "artist",
                "Unknown Artist"
            )
        )

        info.addWidget(
            self.title_label
        )

        info.addWidget(
            self.artist_label
        )

        layout.addLayout(
            info,
            1
        )

        self.play_button = QPushButton(
            "▶"
        )

        self.play_button.setFixedSize(
            38,
            38
        )

        self.play_button.setCursor(
            Qt.PointingHandCursor
        )

        self.play_button.clicked.connect(
            lambda:
            self.play_requested.emit(
                self.index
            )
        )

        layout.addWidget(
            self.play_button
        )

        self.remove_button = QToolButton()

        self.remove_button.setText(
            "×"
        )

        self.remove_button.setToolTip(
            "Remove from playlist"
        )

        self.remove_button.setFixedSize(
            34,
            34
        )

        self.remove_button.setCursor(
            Qt.PointingHandCursor
        )

        self.remove_button.clicked.connect(
            lambda:
            self.remove_requested.emit(
                self.index
            )
        )

        layout.addWidget(
            self.remove_button
        )

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.is_dark = bool(
            is_dark
        )

        self.apply_theme()

    # ========================================================
    # STYLE
    # ========================================================

    def apply_theme(self):

        if self.is_dark:

            self.setStyleSheet(
                """
                QFrame#PlaylistSongRow {
                    background: #151024;
                    border: 1px solid #30234A;
                    border-radius: 14px;
                }

                QFrame#PlaylistSongRow:hover {
                    background: #1B1430;
                    border: 1px solid #4D3670;
                }
                """
            )

            self.art.setStyleSheet(
                """
                QLabel {
                    background: #211735;
                    border-radius: 10px;
                    color: #A970FF;
                    font-size: 20px;
                    font-weight: 700;
                }
                """
            )

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #FFFFFF;
                    font-size: 13px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            self.artist_label.setStyleSheet(
                """
                QLabel {
                    color: #8F84A6;
                    font-size: 11px;
                    background: transparent;
                }
                """
            )

            self.play_button.setStyleSheet(
                """
                QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 19px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #8B5CF6;
                }
                """
            )

            self.remove_button.setStyleSheet(
                """
                QToolButton {
                    background: #211735;
                    color: #A99BC3;
                    border: 1px solid #3B2C55;
                    border-radius: 9px;
                    font-size: 16px;
                    font-weight: 700;
                }

                QToolButton:hover {
                    background: #3A1827;
                    color: #FF7A9A;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QFrame#PlaylistSongRow {
                    background: #F8F5FB;
                    border: 1px solid #D8CEE5;
                    border-radius: 14px;
                }

                QFrame#PlaylistSongRow:hover {
                    background: white;
                    border: 1px solid #B89AD7;
                }
                """
            )

            self.art.setStyleSheet(
                """
                QLabel {
                    background: #EEE8F5;
                    border-radius: 10px;
                    color: #7C3AED;
                    font-size: 20px;
                    font-weight: 700;
                }
                """
            )

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #302744;
                    font-size: 13px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            self.artist_label.setStyleSheet(
                """
                QLabel {
                    color: #756A88;
                    font-size: 11px;
                    background: transparent;
                }
                """
            )

            self.play_button.setStyleSheet(
                """
                QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 19px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #8B5CF6;
                }
                """
            )

            self.remove_button.setStyleSheet(
                """
                QToolButton {
                    background: #EEE8F5;
                    color: #6D607C;
                    border: 1px solid #D4C8E2;
                    border-radius: 9px;
                    font-size: 16px;
                    font-weight: 700;
                }

                QToolButton:hover {
                    background: #FBE8EE;
                    color: #C23D68;
                }
                """
            )


# ============================================================
# PLAYLIST DETAIL VIEW
# ============================================================

class PlaylistDetailView(QWidget):

    back_requested = Signal()

    song_play_requested = Signal(
        dict,
        int
    )

    song_remove_requested = Signal(int)

    play_all_requested = Signal()

    def __init__(
        self,
        playlist,
        is_dark=True,
        parent=None
    ):

        super().__init__(parent)

        self.playlist = playlist
        self.is_dark = is_dark
        self.rows = []

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.build_ui()
        self.apply_theme()
        self.rebuild_songs()

    # ========================================================
    # BUILD
    # ========================================================

    def build_ui(self):

        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.layout.setSpacing(
            16
        )

        top = QHBoxLayout()

        self.back_button = QPushButton(
            "←  Back"
        )

        self.back_button.setCursor(
            Qt.PointingHandCursor
        )

        self.back_button.setFixedHeight(
            38
        )

        self.back_button.clicked.connect(
            self.back_requested.emit
        )

        top.addWidget(
            self.back_button
        )

        top.addStretch()

        self.play_all_button = QPushButton(
            "▶  Play Playlist"
        )

        self.play_all_button.setCursor(
            Qt.PointingHandCursor
        )

        self.play_all_button.setFixedHeight(
            40
        )

        self.play_all_button.clicked.connect(
            self.play_all_requested.emit
        )

        top.addWidget(
            self.play_all_button
        )

        self.layout.addLayout(top)

        header = QHBoxLayout()

        self.cover = QLabel()

        self.cover.setFixedSize(
            150,
            150
        )

        self.cover.setAlignment(
            Qt.AlignCenter
        )

        header.addWidget(
            self.cover
        )

        info = QVBoxLayout()

        info.setSpacing(
            6
        )

        self.title_label = QLabel(
            self.playlist.get(
                "name",
                "Playlist"
            )
        )

        self.description_label = QLabel(
            self.playlist.get(
                "description",
                ""
            )
        )

        self.count_label = QLabel()

        self.description_label.setWordWrap(
            True
        )

        info.addWidget(
            self.title_label
        )

        info.addWidget(
            self.description_label
        )

        info.addSpacing(4)

        info.addWidget(
            self.count_label
        )

        info.addStretch()

        header.addLayout(
            info,
            1
        )

        self.layout.addLayout(header)

        self.section_label = QLabel(
            "Songs in this playlist"
        )

        self.layout.addWidget(
            self.section_label
        )

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

        self.layout.addWidget(
            self.scroll,
            1
        )

        self.scroll_content = QWidget()

        self.scroll_content.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.scroll.setWidget(
            self.scroll_content
        )

        self.songs_layout = QVBoxLayout(
            self.scroll_content
        )

        self.songs_layout.setContentsMargins(
            0,
            0,
            6,
            20
        )

        self.songs_layout.setSpacing(
            9
        )

    # ========================================================
    # COVER
    # ========================================================

    def load_cover(self):

        image = self.playlist.get(
            "thumbnail",
            ""
        )

        image_path = find_asset(image)

        if image_path:

            pixmap = QPixmap(
                str(image_path)
            )

            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    150,
                    150,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                self.cover.setPixmap(
                    pixmap
                )

                self.cover.setText("")

                return

        self.cover.setPixmap(
            QPixmap()
        )

        self.cover.setText(
            "♫"
        )

    # ========================================================
    # SONGS
    # ========================================================

    def rebuild_songs(self):

        while self.songs_layout.count():

            item = self.songs_layout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.setParent(None)
                widget.deleteLater()

        self.rows.clear()

        songs = self.playlist.get(
            "songs",
            []
        )

        self.count_label.setText(
            f"{len(songs)} "
            f"{'song' if len(songs) == 1 else 'songs'}"
        )

        self.load_cover()

        if not songs:

            empty = QLabel(
                "♫\n\n"
                "No songs in this playlist yet.\n"
                "Add songs from Home."
            )

            empty.setAlignment(
                Qt.AlignCenter
            )

            empty.setMinimumHeight(
                220
            )

            empty.setObjectName(
                "PlaylistEmpty"
            )

            self.songs_layout.addWidget(
                empty
            )

            self.songs_layout.addStretch()

            return

        for index, song in enumerate(songs):

            row = PlaylistSongRow(
                song,
                index,
                self.is_dark,
                self.scroll_content
            )

            row.play_requested.connect(
                lambda row_index:
                self.on_song_play(row_index)
            )

            row.remove_requested.connect(
                lambda row_index:
                self.song_remove_requested.emit(row_index)
            )

            self.songs_layout.addWidget(
                row
            )

            self.rows.append(
                row
            )

        self.songs_layout.addStretch()

    # ========================================================
    # PLAY SONG
    # ========================================================

    def on_song_play(
        self,
        index
    ):

        songs = self.playlist.get(
            "songs",
            []
        )

        if (
            index < 0
            or index >= len(songs)
        ):
            return

        self.song_play_requested.emit(
            songs[index],
            index
        )

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.is_dark = bool(is_dark)

        self.apply_theme()
        self.rebuild_songs()

    # ========================================================
    # STYLE
    # ========================================================

    def apply_theme(self):

        if self.is_dark:

            self.back_button.setStyleSheet(
                """
                QPushButton {
                    background: #211735;
                    color: #CFC4DE;
                    border: 1px solid #3B2C55;
                    border-radius: 10px;
                    padding: 0 14px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #30204C;
                    color: white;
                }
                """
            )

            self.play_all_button.setStyleSheet(
                """
                QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0 15px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #8B5CF6;
                }
                """
            )

            self.cover.setStyleSheet(
                """
                QLabel {
                    background: #211735;
                    border-radius: 18px;
                    color: #A970FF;
                    font-size: 42px;
                    font-weight: 700;
                }
                """
            )

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: white;
                    font-size: 29px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

            self.description_label.setStyleSheet(
                """
                QLabel {
                    color: #9186AB;
                    font-size: 12px;
                    background: transparent;
                }
                """
            )

            self.count_label.setStyleSheet(
                """
                QLabel {
                    color: #A970FF;
                    font-size: 12px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            self.section_label.setStyleSheet(
                """
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: 750;
                    background: transparent;
                }
                """
            )

        else:

            self.back_button.setStyleSheet(
                """
                QPushButton {
                    background: #EEE8F5;
                    color: #554668;
                    border: 1px solid #D4C8E2;
                    border-radius: 10px;
                    padding: 0 14px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: white;
                    color: #302744;
                }
                """
            )

            self.play_all_button.setStyleSheet(
                """
                QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0 15px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #8B5CF6;
                }
                """
            )

            self.cover.setStyleSheet(
                """
                QLabel {
                    background: #EEE8F5;
                    border-radius: 18px;
                    color: #7C3AED;
                    font-size: 42px;
                    font-weight: 700;
                }
                """
            )

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #302744;
                    font-size: 29px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

            self.description_label.setStyleSheet(
                """
                QLabel {
                    color: #756A88;
                    font-size: 12px;
                    background: transparent;
                }
                """
            )

            self.count_label.setStyleSheet(
                """
                QLabel {
                    color: #7C3AED;
                    font-size: 12px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            self.section_label.setStyleSheet(
                """
                QLabel {
                    color: #302744;
                    font-size: 16px;
                    font-weight: 750;
                    background: transparent;
                }
                """
            )

        self.scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea > QWidget {
                background: transparent;
            }

            QScrollArea > QWidget > QWidget {
                background: transparent;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 7px;
            }

            QScrollBar::handle:vertical {
                background: #3A2A55;
                border-radius: 3px;
                min-height: 40px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            """

        )

        if hasattr(self.scroll, "viewport"):

            self.scroll.viewport().setAttribute(
                Qt.WA_TranslucentBackground
            )


# ============================================================
# PLAYLIST SCREEN
# ============================================================

class PlaylistScreen(QWidget):

    page_changed = Signal(str)

    song_added_to_playlist = Signal(
        str,
        str
    )

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Playlists - LYRx"
        )

        self.current_is_dark = True

        # ----------------------------------------------------
        # IMPORTANT BACKGROUND FIX
        # ----------------------------------------------------

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            False
        )

        self.setAutoFillBackground(
            False
        )

        # ----------------------------------------------------
        # SHARED DATA
        # ----------------------------------------------------

        self.store = playlist_store

        self.playlists = (
            self.store.get_playlists()
        )

        self.player_queue = list(
            DEFAULT_QUEUE
        )

        self.current_index = 0

        self.current_playlist = None

        self.playlist_cards = []

        self.detail_view = None

        self.build_ui()

        self.apply_theme()

    # ========================================================
    # BUILD
    # ========================================================

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(0)

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.sidebar
        )

        # ----------------------------------------------------
        # MAIN
        # ----------------------------------------------------

        self.main = QWidget()

        self.main.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.main.setAutoFillBackground(
            False
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

        self.main_layout.setSpacing(0)

        # ----------------------------------------------------
        # CONTENT
        # ----------------------------------------------------

        self.content_area = QWidget()

        self.content_area.setObjectName(
            "PlaylistContentArea"
        )

        self.content_area.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.content_area.setAutoFillBackground(
            False
        )

        self.content_area.setStyleSheet(
            """
            QWidget#PlaylistContentArea {
                background: transparent;
            }
            """
        )

        self.main_layout.addWidget(
            self.content_area,
            1
        )

        self.content_layout = QVBoxLayout(
            self.content_area
        )

        self.content_layout.setContentsMargins(
            30,
            25,
            22,
            25
        )

        self.content_layout.setSpacing(
            18
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = QHBoxLayout()

        self.header_icon = QLabel(
            "♫"
        )

        self.header_icon.setFixedWidth(
            38
        )

        header.addWidget(
            self.header_icon
        )

        title_area = QVBoxLayout()

        title_area.setSpacing(2)

        self.title_label = QLabel(
            "Your Playlists"
        )

        self.subtitle_label = QLabel(
            "Create, organize and enjoy your music."
        )

        title_area.addWidget(
            self.title_label
        )

        title_area.addWidget(
            self.subtitle_label
        )

        header.addLayout(
            title_area
        )

        header.addStretch()

        self.new_playlist_button = QPushButton(
            "＋  New Playlist"
        )

        self.new_playlist_button.setCursor(
            Qt.PointingHandCursor
        )

        self.new_playlist_button.setFixedSize(
            145,
            45
        )

        self.new_playlist_button.clicked.connect(
            self.create_playlist
        )

        header.addWidget(
            self.new_playlist_button
        )

        self.content_layout.addLayout(
            header
        )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Search your playlists..."
        )

        self.search_input.setMinimumHeight(
            44
        )

        self.search_input.textChanged.connect(
            self.filter_playlists
        )

        self.content_layout.addWidget(
            self.search_input
        )

        # ----------------------------------------------------
        # SCROLL
        # ----------------------------------------------------

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

        self.scroll.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.scroll.setAutoFillBackground(
            False
        )

        self.content_layout.addWidget(
            self.scroll,
            1
        )

        # ----------------------------------------------------
        # SCROLL CONTENT
        # ----------------------------------------------------

        self.scroll_content = QWidget()

        self.scroll_content.setObjectName(
            "PlaylistScrollContent"
        )

        self.scroll_content.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.scroll_content.setAutoFillBackground(
            False
        )

        self.scroll_content.setStyleSheet(
            """
            QWidget#PlaylistScrollContent {
                background: transparent;
            }
            """
        )

        self.scroll.setWidget(
            self.scroll_content
        )

        # ----------------------------------------------------
        # VIEWPORT BACKGROUND FIX
        # ----------------------------------------------------

        self.scroll.viewport().setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.scroll.viewport().setAutoFillBackground(
            False
        )

        self.scroll.viewport().setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            """
        )

        self.cards_layout = QVBoxLayout(
            self.scroll_content
        )

        self.cards_layout.setContentsMargins(
            0,
            2,
            6,
            25
        )

        self.cards_layout.setSpacing(
            18
        )

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        self.grid_container = QWidget()

        self.grid_container.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.grid_container.setAutoFillBackground(
            False
        )

        self.grid_container.setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            """
        )

        self.grid_layout = QGridLayout(
            self.grid_container
        )

        self.grid_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.grid_layout.setHorizontalSpacing(
            16
        )

        self.grid_layout.setVerticalSpacing(
            18
        )

        self.cards_layout.addWidget(
            self.grid_container
        )

        # ----------------------------------------------------
        # NO RESULTS
        # ----------------------------------------------------

        self.no_results = QLabel(
            "♫  No playlists found"
        )

        self.no_results.setAlignment(
            Qt.AlignCenter
        )

        self.no_results.setMinimumHeight(
            160
        )

        self.no_results.hide()

        self.cards_layout.addWidget(
            self.no_results
        )

        # ----------------------------------------------------
        # CARDS
        # ----------------------------------------------------

        self.rebuild_playlist_cards()

        # ----------------------------------------------------
        # RIGHT PLAYER
        # ----------------------------------------------------

        self.right_area = QWidget()

        self.right_area.setObjectName(
            "RightPlayerArea"
        )

        self.right_area.setFixedWidth(
            330
        )

        self.right_area.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.right_area.setAutoFillBackground(
            False
        )

        self.right_area.setStyleSheet(
            """
            QWidget#RightPlayerArea {
                background: transparent;
            }
            """
        )

        self.main_layout.addWidget(
            self.right_area
        )

        self.right_layout = QVBoxLayout(
            self.right_area
        )

        self.right_layout.setContentsMargins(
            0,
            24,
            20,
            24
        )

        self.right_layout.setSpacing(0)

        self.now_playing = NowPlaying()

        self.now_playing.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.now_playing.previous_requested.connect(
            self.play_previous
        )

        self.now_playing.next_requested.connect(
            self.play_next
        )

        self.now_playing.next_song_requested.connect(
            self.play_selected_song
        )

        self.now_playing.set_queue(
            self.player_queue
        )

        self.right_layout.addWidget(
            self.now_playing
        )

    # ========================================================
    # REBUILD CARDS
    # ========================================================

    def rebuild_playlist_cards(self):

        while self.grid_layout.count():

            item = self.grid_layout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.setParent(None)
                widget.deleteLater()

        self.playlist_cards.clear()

        search = (
            self.search_input
            .text()
            .strip()
            .lower()
        )

        visible_playlists = []

        for playlist in self.playlists:

            searchable = (
                playlist.get(
                    "name",
                    ""
                )
                + " "
                + playlist.get(
                    "description",
                    ""
                )
            ).lower()

            if (
                not search
                or search in searchable
            ):

                visible_playlists.append(
                    playlist
                )

        if not visible_playlists:

            self.no_results.show()

        else:

            self.no_results.hide()

        for index, playlist in enumerate(
            visible_playlists
        ):

            card = PlaylistCard(
                playlist,
                self.current_is_dark,
                self.grid_container
            )

            card.play_requested.connect(
                self.play_playlist
            )

            card.open_requested.connect(
                self.open_playlist
            )

            card.delete_requested.connect(
                self.delete_playlist
            )

            row = index // 3
            column = index % 3

            self.grid_layout.addWidget(
                card,
                row,
                column
            )

            self.playlist_cards.append(
                card
            )

        for column in range(3):

            self.grid_layout.setColumnStretch(
                column,
                1
            )

        self.update_card_widths()

        self.grid_container.adjustSize()
        self.scroll_content.adjustSize()

    # ========================================================
    # CARD WIDTH
    # ========================================================

    def update_card_widths(self):

        if not self.playlist_cards:
            return

        available_width = (
            self.grid_container.width()
        )

        if available_width <= 0:
            return

        spacing = 16

        card_width = (
            available_width
            - (spacing * 2)
        ) // 3

        card_width = max(
            205,
            min(
                card_width,
                280
            )
        )

        for card in self.playlist_cards:

            card.setFixedWidth(
                card_width
            )

    # ========================================================
    # CREATE PLAYLIST
    # ========================================================

    def create_playlist(self):

        dialog = CreatePlaylistDialog(
            self,
            self.current_is_dark
        )

        result = dialog.exec()

        if result != QDialog.Accepted:
            return

        name = dialog.playlist_name()

        description = (
            dialog.playlist_description()
        )

        new_playlist = (
            self.store.create_playlist(
                name,
                description
            )
        )

        if new_playlist is None:

            QMessageBox.warning(
                self,
                "Playlist Exists",
                "A playlist with this name already exists."
            )

            return

        self.playlists = (
            self.store.get_playlists()
        )

        self.rebuild_playlist_cards()

    # ========================================================
    # ADD SONG TO PLAYLIST
    # ========================================================

    def add_song_to_playlist(
        self,
        image_path,
        title,
        artist
    ):

        if not self.playlists:

            QMessageBox.information(
                self,
                "No Playlists",
                "Create a playlist first."
            )

            return False

        dialog = AddToPlaylistDialog(
            self.playlists,
            title,
            self,
            self.current_is_dark
        )

        result = dialog.exec()

        if result != QDialog.Accepted:
            return False

        playlist_id = dialog.selected_id()

        if not playlist_id:
            return False

        success, message = (
            self.store.add_song(
                playlist_id,
                image_path,
                title,
                artist
            )
        )

        if success:

            self.playlists = (
                self.store.get_playlists()
            )

            self.rebuild_playlist_cards()

            self.song_added_to_playlist.emit(
                title,
                playlist_id
            )

            QMessageBox.information(
                self,
                "Added",
                message
            )

            return True

        QMessageBox.information(
            self,
            "Already Added",
            message
        )

        return False

    # ========================================================
    # OPEN PLAYLIST
    # ========================================================

    def open_playlist(
        self,
        playlist
    ):

        playlist_id = playlist.get(
            "id"
        )

        current = self.store.get_playlist(
            playlist_id
        )

        if current is None:
            return

        self.current_playlist = current

        self.grid_container.hide()
        self.no_results.hide()
        self.search_input.hide()
        self.new_playlist_button.hide()

        self.detail_view = PlaylistDetailView(
            current,
            self.current_is_dark,
            self.content_area
        )

        self.detail_view.back_requested.connect(
            self.close_playlist_detail
        )

        self.detail_view.play_all_requested.connect(
            self.play_current_playlist
        )

        self.detail_view.song_play_requested.connect(
            self.play_detail_song
        )

        self.detail_view.song_remove_requested.connect(
            self.remove_song_from_current_playlist
        )

        self.scroll.hide()

        self.content_layout.addWidget(
            self.detail_view,
            1
        )

    # ========================================================
    # CLOSE DETAIL
    # ========================================================

    def close_playlist_detail(self):

        if self.detail_view:

            self.content_layout.removeWidget(
                self.detail_view
            )

            self.detail_view.deleteLater()

            self.detail_view = None

        self.current_playlist = None

        self.scroll.show()
        self.search_input.show()
        self.new_playlist_button.show()
        self.grid_container.show()

        self.rebuild_playlist_cards()

    # ========================================================
    # PLAY CURRENT PLAYLIST
    # ========================================================

    def play_current_playlist(self):

        if self.current_playlist is None:
            return

        self.play_playlist(
            self.current_playlist
        )

    # ========================================================
    # PLAY PLAYLIST
    # ========================================================

    def play_playlist(
        self,
        playlist
    ):

        playlist_id = playlist.get(
            "id"
        )

        songs = self.store.playlist_queue(
            playlist_id
        )

        if not songs:

            QMessageBox.information(
                self,
                "Empty Playlist",
                "This playlist has no songs yet."
            )

            return

        self.player_queue = songs
        self.current_index = 0

        self.now_playing.set_queue(
            self.player_queue
        )

        self._play_queue_index(0)

        print(
            "Playing playlist:",
            playlist.get(
                "name",
                "Playlist"
            )
        )

    # ========================================================
    # PLAY SONG FROM DETAIL
    # ========================================================

    def play_detail_song(
        self,
        song,
        index
    ):

        if self.current_playlist is None:
            return

        playlist_id = (
            self.current_playlist.get(
                "id"
            )
        )

        songs = self.store.playlist_queue(
            playlist_id
        )

        if not songs:
            return

        self.player_queue = songs

        self.now_playing.set_queue(
            self.player_queue
        )

        self.current_index = index

        self._play_queue_index(
            index
        )

    # ========================================================
    # REMOVE SONG
    # ========================================================

    def remove_song_from_current_playlist(
        self,
        song_index
    ):

        if self.current_playlist is None:
            return

        playlist_id = (
            self.current_playlist.get(
                "id"
            )
        )

        removed = self.store.remove_song(
            playlist_id,
            song_index
        )

        if removed is None:
            return

        self.current_playlist = (
            self.store.get_playlist(
                playlist_id
            )
        )

        self.playlists = (
            self.store.get_playlists()
        )

        if self.detail_view:

            self.detail_view.playlist = (
                self.current_playlist
            )

            self.detail_view.rebuild_songs()

        self.rebuild_playlist_cards()

        print(
            "Removed:",
            removed.get(
                "title",
                "song"
            )
        )

    # ========================================================
    # DELETE PLAYLIST
    # ========================================================

    def delete_playlist(
        self,
        playlist_id
    ):

        playlist_id = str(
            playlist_id
        )

        target = self.store.get_playlist(
            playlist_id
        )

        if target is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete Playlist",
            (
                f'Delete "{target.get("name", "Playlist")}"?\n\n'
                "This action cannot be undone."
            ),
            QMessageBox.Yes
            |
            QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        self.store.delete_playlist(
            playlist_id
        )

        self.playlists = (
            self.store.get_playlists()
        )

        if (
            self.current_playlist
            and
            str(
                self.current_playlist.get(
                    "id",
                    ""
                )
            )
            == playlist_id
        ):

            self.close_playlist_detail()

        else:

            self.rebuild_playlist_cards()

        print(
            "Playlist deleted:",
            target.get(
                "name",
                "Playlist"
            )
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def filter_playlists(
        self,
        text
    ):

        self.rebuild_playlist_cards()

    # ========================================================
    # PLAY NEXT
    # ========================================================

    def play_next(self):

        if not self.player_queue:
            return

        shuffle = getattr(
            self.now_playing,
            "is_shuffle",
            False
        )

        if shuffle:

            if len(self.player_queue) == 1:

                next_index = (
                    self.current_index
                )

            else:

                available = [
                    index
                    for index in range(
                        len(
                            self.player_queue
                        )
                    )
                    if index != self.current_index
                ]

                next_index = random.choice(
                    available
                )

            self.current_index = (
                next_index
            )

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

    # ========================================================
    # PLAY PREVIOUS
    # ========================================================

    def play_previous(self):

        if not self.player_queue:
            return

        self.current_index -= 1

        if self.current_index < 0:

            self.current_index = (
                len(
                    self.player_queue
                )
                - 1
            )

        self._play_queue_index(
            self.current_index
        )

    # ========================================================
    # SELECTED SONG
    # ========================================================

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

    # ========================================================
    # QUEUE PLAY
    # ========================================================

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

        image_path, title, artist = (
            self.player_queue[index]
        )

        self.now_playing.set_current_index(
            self.current_index
        )

        self.now_playing.update_song(
            image_path,
            title,
            artist
        )

    # ========================================================
    # THEME STATE
    # ========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.current_is_dark = bool(
            is_dark
        )

        if hasattr(
            self,
            "sidebar"
        ):

            self.sidebar.set_theme_state(
                self.current_is_dark
            )

        if hasattr(
            self,
            "now_playing"
        ):

            if hasattr(
                self.now_playing,
                "set_theme_state"
            ):

                self.now_playing.set_theme_state(
                    self.current_is_dark
                )

        for card in self.playlist_cards:

            card.set_theme_state(
                self.current_is_dark
            )

        if self.detail_view:

            self.detail_view.set_theme_state(
                self.current_is_dark
            )

        self.apply_theme()

        self.update()

    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(self):

        # ----------------------------------------------------
        # GLOBAL TRANSPARENT CONTAINERS
        # ----------------------------------------------------

        transparent_style = """
        QWidget {
            background: transparent;
        }
        """

        if hasattr(self, "main"):

            self.main.setStyleSheet(
                transparent_style
            )

        if hasattr(self, "content_area"):

            self.content_area.setStyleSheet(
                """
                QWidget#PlaylistContentArea {
                    background: transparent;
                    border: none;
                }
                """
            )

        if hasattr(self, "scroll"):

            self.scroll.setStyleSheet(
                """
                QScrollArea {
                    background: transparent;
                    border: none;
                }

                QScrollArea > QWidget {
                    background: transparent;
                    border: none;
                }

                QScrollArea > QWidget > QWidget {
                    background: transparent;
                    border: none;
                }

                QScrollBar:vertical {
                    background: transparent;
                    width: 7px;
                }

                QScrollBar::handle:vertical {
                    background: #3A2A55;
                    border-radius: 3px;
                    min-height: 40px;
                }

                QScrollBar::handle:vertical:hover {
                    background: #5A3A82;
                }

                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                """
            )

            self.scroll.viewport().setStyleSheet(
                """
                QWidget {
                    background: transparent;
                    border: none;
                }
                """
            )

            self.scroll.viewport().setAttribute(
                Qt.WA_TranslucentBackground
            )

            self.scroll.viewport().setAutoFillBackground(
                False
            )

        if hasattr(
            self,
            "scroll_content"
        ):

            self.scroll_content.setStyleSheet(
                """
                QWidget#PlaylistScrollContent {
                    background: transparent;
                    border: none;
                }
                """
            )

        if hasattr(
            self,
            "grid_container"
        ):

            self.grid_container.setStyleSheet(
                """
                QWidget {
                    background: transparent;
                    border: none;
                }
                """
            )

        if hasattr(
            self,
            "right_area"
        ):

            self.right_area.setStyleSheet(
                """
                QWidget#RightPlayerArea {
                    background: transparent;
                    border: none;
                }
                """
            )

        # ----------------------------------------------------
        # DARK THEME
        # ----------------------------------------------------

        if self.current_is_dark:

            self.search_input.setStyleSheet(
                """
                QLineEdit {
                    background: rgba(16, 11, 26, 235);
                    color: #EEE9F8;
                    border: 1px solid #30234A;
                    border-radius: 12px;
                    padding: 0 14px;
                    font-size: 12px;
                }

                QLineEdit:focus {
                    border: 1px solid #7C3AED;
                    background: rgba(17, 12, 29, 245);
                }

                QLineEdit::placeholder {
                    color: #746985;
                }
                """
            )

            self.new_playlist_button.setStyleSheet(
                """
                QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #8B5CF6;
                }

                QPushButton:pressed {
                    background: #6D28D9;
                }
                """
            )

            self.header_icon.setStyleSheet(
                """
                QLabel {
                    color: #A970FF;
                    font-size: 31px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #FFFFFF;
                    font-size: 29px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

            self.subtitle_label.setStyleSheet(
                """
                QLabel {
                    color: #9287AB;
                    font-size: 12px;
                    background: transparent;
                }
                """
            )

            self.no_results.setStyleSheet(
                """
                QLabel {
                    color: #9B91B2;
                    background: rgba(21, 16, 36, 190);
                    border: 1px solid #30234A;
                    border-radius: 16px;
                    font-size: 14px;
                    font-weight: 600;
                }
                """
            )

        # ----------------------------------------------------
        # LIGHT THEME
        # ----------------------------------------------------

        else:

            self.search_input.setStyleSheet(
                """
                QLineEdit {
                    background: rgba(250, 248, 252, 245);
                    color: #302744;
                    border: 1px solid #D6CBDF;
                    border-radius: 12px;
                    padding: 0 14px;
                    font-size: 12px;
                }

                QLineEdit:focus {
                    border: 1px solid #7C3AED;
                    background: white;
                }

                QLineEdit::placeholder {
                    color: #8B8095;
                }
                """
            )

            self.new_playlist_button.setStyleSheet(
                """
                QPushButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 700;
                }

                QPushButton:hover {
                    background: #8B5CF6;
                }

                QPushButton:pressed {
                    background: #6D28D9;
                }
                """
            )

            self.header_icon.setStyleSheet(
                """
                QLabel {
                    color: #7C3AED;
                    font-size: 31px;
                    font-weight: 700;
                    background: transparent;
                }
                """
            )

            self.title_label.setStyleSheet(
                """
                QLabel {
                    color: #302744;
                    font-size: 29px;
                    font-weight: 800;
                    background: transparent;
                }
                """
            )

            self.subtitle_label.setStyleSheet(
                """
                QLabel {
                    color: #756A88;
                    font-size: 12px;
                    background: transparent;
                }
                """
            )

            self.no_results.setStyleSheet(
                """
                QLabel {
                    color: #71667D;
                    background: rgba(248, 245, 251, 220);
                    border: 1px solid #D8CEE5;
                    border-radius: 16px;
                    font-size: 14px;
                    font-weight: 600;
                }
                """
            )

    # ========================================================
    # RESIZE
    # ========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(event)

        self.update_card_widths()

    # ========================================================
    # PAINT
    # ========================================================

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # ----------------------------------------------------
        # BASE GRADIENT
        # ----------------------------------------------------

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        if self.current_is_dark:

            # Deep blue/purple LYRx background
            gradient.setColorAt(
                0.00,
                QColor("#080A18")
            )

            gradient.setColorAt(
                0.22,
                QColor("#0D0B20")
            )

            gradient.setColorAt(
                0.48,
                QColor("#17102B")
            )

            gradient.setColorAt(
                0.72,
                QColor("#120D22")
            )

            gradient.setColorAt(
                1.00,
                QColor("#070813")
            )

        else:

            gradient.setColorAt(
                0.00,
                QColor("#E9E4F5")
            )

            gradient.setColorAt(
                0.28,
                QColor("#EDE5F5")
            )

            gradient.setColorAt(
                0.55,
                QColor("#E7DEF0")
            )

            gradient.setColorAt(
                0.78,
                QColor("#F0EAF5")
            )

            gradient.setColorAt(
                1.00,
                QColor("#EAE4F1")
            )

        painter.fillRect(
            rect,
            gradient
        )

        painter.setPen(
            Qt.NoPen
        )

        # ----------------------------------------------------
        # LEFT PURPLE GLOW
        # ----------------------------------------------------

        if self.current_is_dark:

            painter.setBrush(
                QColor(
                    124,
                    58,
                    237,
                    34
                )
            )

            painter.drawEllipse(
                -190,
                -180,
                520,
                420
            )

            painter.setBrush(
                QColor(
                    91,
                    33,
                    182,
                    20
                )
            )

            painter.drawEllipse(
                -70,
                120,
                430,
                400
            )

            # ------------------------------------------------
            # RIGHT BLUE/PURPLE GLOW
            # ------------------------------------------------

            painter.setBrush(
                QColor(
                    99,
                    102,
                    241,
                    19
                )
            )

            painter.drawEllipse(
                rect.width() - 430,
                -80,
                520,
                500
            )

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    20
                )
            )

            painter.drawEllipse(
                rect.width() - 520,
                rect.height() - 390,
                560,
                500
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
                -170,
                -150,
                440,
                350
            )

            painter.setBrush(
                QColor(
                    139,
                    92,
                    246,
                    10
                )
            )

            painter.drawEllipse(
                rect.width() - 430,
                40,
                500,
                500
            )

        painter.end()