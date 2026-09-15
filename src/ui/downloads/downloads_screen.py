from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import (
    Qt,
    Signal,
    QUrl,
)

from PySide6.QtGui import (
    QDesktopServices,
)

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QSizePolicy,
)

from widgets.sidebar import Sidebar


# ============================================================
# LYRx
# DAY 26 - DOWNLOADED MUSIC
#
# FILE:
# src/ui/downloads/downloads_screen.py
# ============================================================


class DownloadRow(QFrame):

    play_requested = Signal(object)
    remove_requested = Signal(object)
    folder_requested = Signal(object)

    def __init__(
        self,
        entry: dict,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.entry = dict(
            entry
            or {}
        )

        self.setObjectName(
            "DownloadRow"
        )

        root = QHBoxLayout(
            self
        )

        root.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        root.setSpacing(
            14
        )

        icon = QLabel(
            "♫"
        )

        icon.setObjectName(
            "DownloadIcon"
        )

        icon.setFixedSize(
            44,
            44,
        )

        icon.setAlignment(
            Qt.AlignCenter
        )

        root.addWidget(
            icon
        )

        info = QVBoxLayout()

        info.setSpacing(
            3
        )

        title = QLabel(
            str(
                self.entry.get(
                    "title",
                    "Unknown Track",
                )
                or
                "Unknown Track"
            )
        )

        title.setObjectName(
            "DownloadTitle"
        )

        artist = QLabel(
            str(
                self.entry.get(
                    "artist",
                    "Unknown Artist",
                )
                or
                "Unknown Artist"
            )
        )

        artist.setObjectName(
            "DownloadArtist"
        )

        provider = str(
            self.entry.get(
                "provider",
                "online",
            )
            or
            "online"
        )

        size = int(
            self.entry.get(
                "size_bytes",
                0,
            )
            or
            0
        )

        meta = QLabel(
            f"{provider.title()}  •  {self.human_bytes(size)}"
        )

        meta.setObjectName(
            "DownloadMeta"
        )

        info.addWidget(
            title
        )

        info.addWidget(
            artist
        )

        info.addWidget(
            meta
        )

        root.addLayout(
            info,
            1,
        )

        play = QPushButton(
            "▶  Play"
        )

        play.setObjectName(
            "DownloadsPrimaryButton"
        )

        play.setCursor(
            Qt.PointingHandCursor
        )

        play.clicked.connect(
            lambda:
            self.play_requested.emit(
                self.entry
            )
        )

        root.addWidget(
            play
        )

        folder = QPushButton(
            "Open Folder"
        )

        folder.setObjectName(
            "DownloadsSecondaryButton"
        )

        folder.setCursor(
            Qt.PointingHandCursor
        )

        folder.clicked.connect(
            lambda:
            self.folder_requested.emit(
                self.entry
            )
        )

        root.addWidget(
            folder
        )

        remove = QPushButton(
            "Remove"
        )

        remove.setObjectName(
            "DownloadsDangerButton"
        )

        remove.setCursor(
            Qt.PointingHandCursor
        )

        remove.clicked.connect(
            lambda:
            self.remove_requested.emit(
                self.entry
            )
        )

        root.addWidget(
            remove
        )

    @staticmethod
    def human_bytes(
        size,
    ):

        size = max(
            0,
            int(
                size
                or 0
            ),
        )

        value = float(
            size
        )

        for unit in (
            "B",
            "KB",
            "MB",
            "GB",
        ):

            if (
                value < 1024
                or
                unit == "GB"
            ):

                if unit == "B":

                    return (
                        f"{int(value)} {unit}"
                    )

                return (
                    f"{value:.1f} {unit}"
                )

            value /= 1024

        return f"{size} B"


class DownloadsScreen(QWidget):

    back_requested = Signal()
    play_requested = Signal(object)

    def __init__(
        self,
        manager,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.manager = manager

        self.current_is_dark = True

        self.build_ui()

        self.manager.library_changed.connect(
            self.refresh_downloads
        )

        self.refresh_downloads()

        self.set_theme_state(
            True
        )

    # ========================================================
    # UI
    # ========================================================

    def build_ui(
        self,
    ):

        root = QHBoxLayout(
            self
        )

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root.setSpacing(
            0
        )

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding,
        )

        root.addWidget(
            self.sidebar
        )

        self.main = QWidget()

        self.main.setObjectName(
            "DownloadsMain"
        )

        root.addWidget(
            self.main,
            1,
        )

        layout = QVBoxLayout(
            self.main
        )

        layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        layout.setSpacing(
            12
        )

        back = QPushButton(
            "←  Downloads & Storage"
        )

        back.setObjectName(
            "DownloadsBackButton"
        )

        back.setCursor(
            Qt.PointingHandCursor
        )

        back.clicked.connect(
            self.back_requested.emit
        )

        layout.addWidget(
            back,
            0,
            Qt.AlignLeft,
        )

        title = QLabel(
            "Downloaded Music"
        )

        title.setObjectName(
            "DownloadsPageTitle"
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            (
                "Tracks saved by LYRx for offline playback. "
                "Only provider-approved downloadable sources appear here."
            )
        )

        subtitle.setObjectName(
            "DownloadsPageSubtitle"
        )

        subtitle.setWordWrap(
            True
        )

        layout.addWidget(
            subtitle
        )

        self.summary = QLabel(
            ""
        )

        self.summary.setObjectName(
            "DownloadsSummary"
        )

        layout.addWidget(
            self.summary
        )

        self.scroll = QScrollArea()

        self.scroll.setObjectName(
            "DownloadsScroll"
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

        self.content = QWidget()

        self.content.setObjectName(
            "DownloadsContent"
        )

        self.rows = QVBoxLayout(
            self.content
        )

        self.rows.setContentsMargins(
            0,
            4,
            8,
            24,
        )

        self.rows.setSpacing(
            10
        )

        self.scroll.setWidget(
            self.content
        )

        layout.addWidget(
            self.scroll,
            1,
        )

    # ========================================================
    # REFRESH
    # ========================================================

    def clear_rows(
        self,
    ):

        while self.rows.count():

            item = self.rows.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

    def refresh_downloads(
        self,
    ):

        self.manager.prune_missing()

        self.clear_rows()

        entries = self.manager.entries()

        total_bytes = sum(
            int(
                item.get(
                    "size_bytes",
                    0,
                )
                or 0
            )
            for item in entries
        )

        self.summary.setText(
            (
                f"{len(entries)} downloaded "
                f"{'track' if len(entries) == 1 else 'tracks'}"
                f"  •  "
                f"{self.manager.human_bytes(total_bytes)}"
            )
        )

        if not entries:

            empty = QFrame()

            empty.setObjectName(
                "DownloadsEmptyCard"
            )

            empty_layout = QVBoxLayout(
                empty
            )

            empty_layout.setContentsMargins(
                24,
                34,
                24,
                34,
            )

            empty_layout.setSpacing(
                8
            )

            icon = QLabel(
                "⇩"
            )

            icon.setObjectName(
                "DownloadsEmptyIcon"
            )

            icon.setAlignment(
                Qt.AlignCenter
            )

            empty_layout.addWidget(
                icon
            )

            heading = QLabel(
                "No offline music yet"
            )

            heading.setObjectName(
                "DownloadsEmptyTitle"
            )

            heading.setAlignment(
                Qt.AlignCenter
            )

            empty_layout.addWidget(
                heading
            )

            body = QLabel(
                (
                    "Play a provider-supported downloadable track "
                    "and use the Download button in Now Playing."
                )
            )

            body.setObjectName(
                "DownloadsEmptyText"
            )

            body.setWordWrap(
                True
            )

            body.setAlignment(
                Qt.AlignCenter
            )

            empty_layout.addWidget(
                body
            )

            self.rows.addWidget(
                empty
            )

            self.rows.addStretch()

            return

        for entry in entries:

            row = DownloadRow(
                entry
            )

            row.play_requested.connect(
                self.play_requested.emit
            )

            row.folder_requested.connect(
                self.open_entry_folder
            )

            row.remove_requested.connect(
                self.remove_entry
            )

            self.rows.addWidget(
                row
            )

        self.rows.addStretch()

    # ========================================================
    # ACTIONS
    # ========================================================

    def open_entry_folder(
        self,
        entry,
    ):

        path = Path(
            str(
                entry.get(
                    "file_path",
                    "",
                )
                or ""
            )
        )

        folder = (
            path.parent
            if path.parent.exists()
            else self.manager.download_dir()
        )

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(
                    folder.resolve()
                )
            )
        )

    def remove_entry(
        self,
        entry,
    ):

        entry_id = str(
            entry.get(
                "id",
                "",
            )
            or ""
        )

        if not entry_id:

            return

        # Keep this action direct and reversible only by re-downloading.
        # A custom confirm dialog can be added in the polish phase.
        self.manager.remove_entry(
            entry_id,
            delete_file=True,
        )

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_state(
        self,
        is_dark,
    ):

        self.current_is_dark = bool(
            is_dark
        )

        try:

            self.sidebar.set_theme_state(
                self.current_is_dark
            )

        except Exception:

            pass

        self.apply_theme()

    def apply_theme(
        self,
    ):

        if self.current_is_dark:

            self.setStyleSheet(
                """
                QWidget#DownloadsMain,
                QWidget#DownloadsContent,
                QScrollArea#DownloadsScroll {
                    background: #0E0916;
                    border: none;
                }

                QLabel#DownloadsPageTitle {
                    color: #FFFFFF;
                    font-size: 30px;
                    font-weight: 800;
                }

                QLabel#DownloadsPageSubtitle {
                    color: #A99DB8;
                    font-size: 13px;
                }

                QLabel#DownloadsSummary {
                    color: #A875F5;
                    font-size: 12px;
                    font-weight: 700;
                    padding: 4px 0 8px 0;
                }

                QPushButton#DownloadsBackButton {
                    background: transparent;
                    color: #B27BF3;
                    border: none;
                    padding: 4px 2px;
                    font-size: 12px;
                    font-weight: 700;
                    text-align: left;
                }

                QPushButton#DownloadsBackButton:hover {
                    color: #FFFFFF;
                }

                QFrame#DownloadRow,
                QFrame#DownloadsEmptyCard {
                    background: #171023;
                    border: 1px solid #302043;
                    border-radius: 15px;
                }

                QFrame#DownloadRow:hover {
                    background: #1C1328;
                    border: 1px solid #4D3266;
                }

                QLabel#DownloadIcon {
                    background: #28163D;
                    border: 1px solid #4D2B6D;
                    border-radius: 12px;
                    color: #C58EFF;
                    font-size: 18px;
                    font-weight: 800;
                }

                QLabel#DownloadTitle {
                    color: #FFFFFF;
                    font-size: 14px;
                    font-weight: 800;
                }

                QLabel#DownloadArtist {
                    color: #C1B4CF;
                    font-size: 11px;
                }

                QLabel#DownloadMeta {
                    color: #847591;
                    font-size: 10px;
                }

                QPushButton#DownloadsPrimaryButton {
                    background: #8438F4;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 9px;
                    padding: 8px 13px;
                    font-weight: 700;
                }

                QPushButton#DownloadsSecondaryButton {
                    background: #21162E;
                    color: #EEE6F7;
                    border: 1px solid #3D2A52;
                    border-radius: 9px;
                    padding: 8px 12px;
                    font-weight: 600;
                }

                QPushButton#DownloadsDangerButton {
                    background: transparent;
                    color: #F29AA8;
                    border: 1px solid #613341;
                    border-radius: 9px;
                    padding: 8px 12px;
                    font-weight: 600;
                }

                QPushButton#DownloadsDangerButton:hover {
                    background: #351722;
                }

                QLabel#DownloadsEmptyIcon {
                    color: #A461FF;
                    font-size: 36px;
                    font-weight: 800;
                }

                QLabel#DownloadsEmptyTitle {
                    color: #FFFFFF;
                    font-size: 18px;
                    font-weight: 800;
                }

                QLabel#DownloadsEmptyText {
                    color: #988CA6;
                    font-size: 12px;
                }

                QScrollBar:vertical {
                    background: transparent;
                    width: 8px;
                }

                QScrollBar::handle:vertical {
                    background: #49365D;
                    min-height: 30px;
                    border-radius: 4px;
                }

                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    height: 0;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QWidget#DownloadsMain,
                QWidget#DownloadsContent,
                QScrollArea#DownloadsScroll {
                    background: #F6F1FA;
                    border: none;
                }

                QLabel#DownloadsPageTitle {
                    color: #261C2D;
                    font-size: 30px;
                    font-weight: 800;
                }

                QLabel#DownloadsPageSubtitle {
                    color: #75687E;
                    font-size: 13px;
                }

                QLabel#DownloadsSummary {
                    color: #6D28D9;
                    font-size: 12px;
                    font-weight: 700;
                }

                QPushButton#DownloadsBackButton {
                    background: transparent;
                    color: #6D28D9;
                    border: none;
                    font-size: 12px;
                    font-weight: 700;
                }

                QFrame#DownloadRow,
                QFrame#DownloadsEmptyCard {
                    background: #FFFFFF;
                    border: 1px solid #DDD2E5;
                    border-radius: 15px;
                }

                QLabel#DownloadIcon {
                    background: #F0E6FA;
                    border: 1px solid #D8C4EB;
                    border-radius: 12px;
                    color: #6D28D9;
                    font-size: 18px;
                    font-weight: 800;
                }

                QLabel#DownloadTitle {
                    color: #2B2131;
                    font-size: 14px;
                    font-weight: 800;
                }

                QLabel#DownloadArtist {
                    color: #75677F;
                    font-size: 11px;
                }

                QLabel#DownloadMeta {
                    color: #8C7E95;
                    font-size: 10px;
                }

                QPushButton#DownloadsPrimaryButton {
                    background: #7C3AED;
                    color: white;
                    border: none;
                    border-radius: 9px;
                    padding: 8px 13px;
                    font-weight: 700;
                }

                QPushButton#DownloadsSecondaryButton {
                    background: #F6F1FA;
                    color: #4F3D59;
                    border: 1px solid #D7CBE0;
                    border-radius: 9px;
                    padding: 8px 12px;
                    font-weight: 600;
                }

                QPushButton#DownloadsDangerButton {
                    background: #FFF7F8;
                    color: #B33D55;
                    border: 1px solid #EAC4CB;
                    border-radius: 9px;
                    padding: 8px 12px;
                    font-weight: 600;
                }

                QLabel#DownloadsEmptyIcon {
                    color: #7C3AED;
                    font-size: 36px;
                }

                QLabel#DownloadsEmptyTitle {
                    color: #2B2131;
                    font-size: 18px;
                    font-weight: 800;
                }

                QLabel#DownloadsEmptyText {
                    color: #7F7287;
                    font-size: 12px;
                }
                """
            )
