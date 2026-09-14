from __future__ import annotations

from pathlib import Path
import shutil

from PySide6.QtCore import (
    Qt,
    Signal,
    QSettings,
    QSize,
    QRectF,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QDate,
    QStandardPaths,
    QUrl,
    QTimer,
)

from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QPainterPath,
    QColor,
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
    QComboBox,
    QSlider,
    QFileDialog,
    QStackedWidget,
    QAbstractButton,
    QLineEdit,
    QDateEdit,
    QDialog,
    QSystemTrayIcon,
)

from widgets.sidebar import Sidebar


# ============================================================
# LYRx
# DAY 25 - PROFESSIONAL SETTINGS
#
# FILE:
# src/ui/settings/settings_screen.py
# ============================================================



# ============================================================
# STORAGE HELPERS
# ============================================================

def lyrx_cache_dir() -> Path:
    """Return a real per-user LYRx cache directory."""
    base = str(
        QStandardPaths.writableLocation(
            QStandardPaths.CacheLocation
        )
        or ""
    ).strip()

    if base:
        path = Path(base) / "LYRx"
    else:
        path = Path.home() / ".lyrx" / "cache"

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def directory_size(path: Path) -> int:
    total = 0

    try:
        for item in path.rglob("*"):
            try:
                if item.is_file():
                    total += item.stat().st_size
            except Exception:
                pass
    except Exception:
        pass

    return total


def format_bytes(size: int) -> str:
    value = float(max(0, int(size or 0)))

    units = [
        "B",
        "KB",
        "MB",
        "GB",
    ]

    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"

            return f"{value:.1f} {unit}"

        value /= 1024

    return "0 B"


# ============================================================
# AVATAR
# ============================================================

def circular_avatar(
    path: str,
    size: int = 76,
) -> QIcon:

    path = str(path or "").strip()

    if (
        not path
        or
        not Path(path).is_file()
    ):
        return QIcon()

    pixmap = QPixmap(path)

    if pixmap.isNull():
        return QIcon()

    source = pixmap.scaled(
        size,
        size,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation,
    )

    output = QPixmap(
        size,
        size,
    )

    output.fill(
        Qt.transparent
    )

    painter = QPainter(
        output
    )

    painter.setRenderHint(
        QPainter.Antialiasing
    )

    clip = QPainterPath()

    clip.addEllipse(
        0,
        0,
        size,
        size,
    )

    painter.setClipPath(
        clip
    )

    x = (
        source.width()
        - size
    ) // 2

    y = (
        source.height()
        - size
    ) // 2

    painter.drawPixmap(
        0,
        0,
        source,
        x,
        y,
        size,
        size,
    )

    painter.end()

    return QIcon(
        output
    )


# ============================================================
# CUSTOM LYRx TOGGLE
# ============================================================

class ToggleSwitch(QAbstractButton):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.setCheckable(
            True
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.setFixedSize(
            48,
            26,
        )

        self._offset = 3.0

        self.animation = QPropertyAnimation(
            self,
            b"offset",
            self,
        )

        self.animation.setDuration(
            180
        )

        self.animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.toggled.connect(
            self.animate_toggle
        )

    # --------------------------------------------------------

    def get_offset(
        self
    ):

        return self._offset

    # --------------------------------------------------------

    def set_offset(
        self,
        value,
    ):

        self._offset = float(
            value
        )

        self.update()

    # --------------------------------------------------------

    offset = Property(
        float,
        get_offset,
        set_offset,
    )

    # --------------------------------------------------------

    def knob_end_position(
        self,
        checked
    ):

        knob_size = (
            self.height()
            - 6
        )

        if checked:

            return (
                self.width()
                - knob_size
                - 3
            )

        return 3

    # --------------------------------------------------------

    def animate_toggle(
        self,
        checked
    ):

        self.animation.stop()

        # DAY 25 STEP 5:
        # Accessibility -> Reduce Motion now has real behavior.
        # When enabled, LYRx switches the custom toggle instantly
        # instead of running the knob animation.
        reduce_motion = QSettings(
            "LYRx",
            "LYRxDesktop",
        ).value(
            "settings/reduce_motion",
            False,
            type=bool,
        )

        end_position = float(
            self.knob_end_position(
                checked
            )
        )

        if reduce_motion:

            self.set_offset(
                end_position
            )

            return

        self.animation.setStartValue(
            self._offset
        )

        self.animation.setEndValue(
            end_position
        )

        self.animation.start()

    # --------------------------------------------------------

    def sync_position(
        self
    ):

        self._offset = float(
            self.knob_end_position(
                self.isChecked()
            )
        )

        self.update()

    # --------------------------------------------------------

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

        painter.setPen(
            Qt.NoPen
        )

        if self.isChecked():

            track_color = QColor(
                "#8B5CF6"
            )

        else:

            track_color = QColor(
                "#3A3046"
            )

        painter.setBrush(
            track_color
        )

        painter.drawRoundedRect(
            QRectF(
                0,
                0,
                self.width(),
                self.height(),
            ),
            13,
            13,
        )

        knob_size = (
            self.height()
            - 6
        )

        painter.setBrush(
            QColor(
                "#FFFFFF"
            )
        )

        painter.drawEllipse(
            QRectF(
                self._offset,
                3,
                knob_size,
                knob_size,
            )
        )

        painter.end()


# ============================================================
# CATEGORY CARD
# ============================================================

class CategoryCard(QFrame):

    clicked = Signal(
        str
    )

    def __init__(
        self,
        key,
        icon,
        title,
        subtitle,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.key = key

        self.setObjectName(
            "SettingsCategoryCard"
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        root = QHBoxLayout(
            self
        )

        root.setContentsMargins(
            18,
            15,
            18,
            15,
        )

        root.setSpacing(
            15
        )

        # ====================================================
        # ICON
        # ====================================================

        icon_label = QLabel(
            icon
        )

        icon_label.setObjectName(
            "SettingsCategoryIcon"
        )

        icon_label.setFixedSize(
            42,
            42,
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        root.addWidget(
            icon_label
        )

        # ====================================================
        # TEXT
        # ====================================================

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            3
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "SettingsCategoryTitle"
        )

        subtitle_label = QLabel(
            subtitle
        )

        subtitle_label.setObjectName(
            "SettingsCategorySubtitle"
        )

        subtitle_label.setWordWrap(
            True
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            subtitle_label
        )

        root.addLayout(
            text_layout,
            1,
        )

        # ====================================================
        # ARROW
        # ====================================================

        arrow = QLabel(
            "›"
        )

        arrow.setObjectName(
            "SettingsCategoryArrow"
        )

        arrow.setAlignment(
            Qt.AlignCenter
        )

        root.addWidget(
            arrow
        )

    # --------------------------------------------------------

    def mousePressEvent(
        self,
        event
    ):

        if (
            event.button()
            == Qt.LeftButton
        ):

            self.clicked.emit(
                self.key
            )

        super().mousePressEvent(
            event
        )


# ============================================================
# SETTING ROW
# ============================================================

class SettingRow(QFrame):

    def __init__(
        self,
        title,
        description="",
        control=None,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.setObjectName(
            "SettingRow"
        )

        root = QHBoxLayout(
            self
        )

        root.setContentsMargins(
            18,
            15,
            18,
            15,
        )

        root.setSpacing(
            18
        )

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            3
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "SettingRowTitle"
        )

        text_layout.addWidget(
            title_label
        )

        if description:

            description_label = QLabel(
                description
            )

            description_label.setObjectName(
                "SettingRowDescription"
            )

            description_label.setWordWrap(
                True
            )

            text_layout.addWidget(
                description_label
            )

        root.addLayout(
            text_layout,
            1,
        )

        if control is not None:

            root.addWidget(
                control,
                0,
                Qt.AlignRight
                | Qt.AlignVCenter,
            )


# ============================================================
# PROFILE PHOTO SENTINEL
# ============================================================

AVATAR_REMOVED_SENTINEL = "__LYRX_AVATAR_REMOVED__"


# ============================================================
# LYRx MODERN DIALOG
# ============================================================

class LYRxDialog(QDialog):

    def __init__(
        self,
        parent=None,
        title: str = "LYRx",
        message: str = "",
        confirm_text: str = "OK",
        cancel_text: str = "",
        destructive: bool = False,
        is_dark: bool = True,
    ):
        super().__init__(parent)

        self.accepted_action = False

        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(430)
        self.setWindowFlags(
            Qt.Dialog
            | Qt.FramelessWindowHint
        )
        self.setAttribute(
            Qt.WA_TranslucentBackground,
            True,
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)

        card = QFrame()
        card.setObjectName("LYRxDialogCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        top = QHBoxLayout()
        top.setSpacing(12)

        icon = QLabel("L")
        icon.setObjectName("LYRxDialogIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(44, 44)
        top.addWidget(icon)

        text = QVBoxLayout()
        text.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("LYRxDialogTitle")
        text.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setObjectName("LYRxDialogMessage")
        message_label.setWordWrap(True)
        text.addWidget(message_label)

        top.addLayout(text, 1)
        layout.addLayout(top)

        actions = QHBoxLayout()
        actions.addStretch()

        if cancel_text:
            cancel = QPushButton(cancel_text)
            cancel.setObjectName("LYRxDialogSecondary")
            cancel.setCursor(Qt.PointingHandCursor)
            cancel.clicked.connect(self.reject)
            actions.addWidget(cancel)

        confirm = QPushButton(confirm_text)
        confirm.setObjectName(
            "LYRxDialogDanger"
            if destructive
            else "LYRxDialogPrimary"
        )
        confirm.setCursor(Qt.PointingHandCursor)
        confirm.clicked.connect(self._accept_action)
        actions.addWidget(confirm)

        layout.addLayout(actions)
        outer.addWidget(card)

        if is_dark:
            self.setStyleSheet("""
                QFrame#LYRxDialogCard {
                    background: #171023;
                    border: 1px solid #4B2A68;
                    border-radius: 20px;
                }
                QLabel#LYRxDialogIcon {
                    background: #2A1740;
                    color: #FFFFFF;
                    border: 1px solid #6E3BA4;
                    border-radius: 14px;
                    font-size: 20px;
                    font-weight: 900;
                }
                QLabel#LYRxDialogTitle {
                    color: #FFFFFF;
                    font-size: 17px;
                    font-weight: 800;
                }
                QLabel#LYRxDialogMessage {
                    color: #B9ACC7;
                    font-size: 12px;
                }
                QPushButton#LYRxDialogPrimary,
                QPushButton#LYRxDialogSecondary,
                QPushButton#LYRxDialogDanger {
                    min-height: 34px;
                    padding: 0 16px;
                    border-radius: 10px;
                    font-weight: 700;
                }
                QPushButton#LYRxDialogPrimary {
                    background: #8438F4;
                    color: #FFFFFF;
                    border: 1px solid #9956FF;
                }
                QPushButton#LYRxDialogPrimary:hover {
                    background: #9850FF;
                }
                QPushButton#LYRxDialogSecondary {
                    background: #21162E;
                    color: #E9DFF3;
                    border: 1px solid #45305B;
                }
                QPushButton#LYRxDialogSecondary:hover {
                    background: #2A1C39;
                }
                QPushButton#LYRxDialogDanger {
                    background: #4A1B28;
                    color: #FFD8DF;
                    border: 1px solid #8E3A50;
                }
                QPushButton#LYRxDialogDanger:hover {
                    background: #632638;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#LYRxDialogCard {
                    background: #FFFFFF;
                    border: 1px solid #D8C8E5;
                    border-radius: 20px;
                }
                QLabel#LYRxDialogIcon {
                    background: #F0E6FA;
                    color: #6D28D9;
                    border: 1px solid #D6C0E8;
                    border-radius: 14px;
                    font-size: 20px;
                    font-weight: 900;
                }
                QLabel#LYRxDialogTitle {
                    color: #2B2131;
                    font-size: 17px;
                    font-weight: 800;
                }
                QLabel#LYRxDialogMessage {
                    color: #75677F;
                    font-size: 12px;
                }
                QPushButton#LYRxDialogPrimary,
                QPushButton#LYRxDialogSecondary,
                QPushButton#LYRxDialogDanger {
                    min-height: 34px;
                    padding: 0 16px;
                    border-radius: 10px;
                    font-weight: 700;
                }
                QPushButton#LYRxDialogPrimary {
                    background: #7C3AED;
                    color: #FFFFFF;
                    border: 1px solid #8B5CF6;
                }
                QPushButton#LYRxDialogSecondary {
                    background: #F7F2FA;
                    color: #4F3D59;
                    border: 1px solid #D8CDE0;
                }
                QPushButton#LYRxDialogDanger {
                    background: #FFF3F5;
                    color: #B33D55;
                    border: 1px solid #E5B8C1;
                }
            """)

    def _accept_action(self):
        self.accepted_action = True
        self.accept()


# ============================================================
# SETTINGS SCREEN
# ============================================================

class SettingsScreen(QWidget):

    account_requested = Signal()

    theme_requested = Signal(
        bool
    )

    settings_changed = Signal()

    # DAY 25 - profile editor
    profile_updated = Signal()

    MENU = "menu"

    PROFILE = "profile"

    APPEARANCE = "appearance"

    PLAYBACK = "playback"

    AUDIO = "audio"

    STORAGE = "storage"

    PRIVACY = "privacy"

    NOTIFICATIONS = "notifications"

    LANGUAGE = "language"

    ACCESSIBILITY = "accessibility"

    ABOUT = "about"

    # ========================================================

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.current_is_dark = True

        self.settings = QSettings(
            "LYRx",
            "LYRxDesktop",
        )

        self.pages = {}

        self.setWindowTitle(
            "🎵 LYRx - Settings"
        )

        self.build_ui()

        self.load_settings()

        self.refresh_profile()

        self.set_theme_state(
            True
        )

    # ========================================================
    # BUILD
    # ========================================================

    def build_ui(
        self
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

        # ====================================================
        # SIDEBAR
        # ====================================================

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding,
        )

        root.addWidget(
            self.sidebar
        )

        # ====================================================
        # MAIN
        # ====================================================

        self.main = QWidget()

        self.main.setObjectName(
            "SettingsMain"
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
            22,
            28,
            20,
        )

        layout.setSpacing(
            0
        )

        # ====================================================
        # INTERNAL PAGE STACK
        # ====================================================

        self.stack = QStackedWidget()

        self.stack.setObjectName(
            "SettingsStack"
        )

        layout.addWidget(
            self.stack
        )

        # ====================================================
        # PAGES
        # ====================================================

        self.build_menu_page()

        self.build_profile_page()

        self.build_appearance_page()

        self.build_playback_page()

        self.build_audio_page()

        self.build_storage_page()

        self.build_privacy_page()

        self.build_notifications_page()

        self.build_language_page()

        self.build_accessibility_page()

        self.build_about_page()

        self.show_page(
            self.MENU
        )

    # ========================================================
    # REGISTER PAGE
    # ========================================================

    def register_page(
        self,
        key,
        page
    ):

        index = self.stack.addWidget(
            page
        )

        self.pages[key] = index

    # ========================================================
    # SHOW PAGE
    # ========================================================

    def show_page(
        self,
        key
    ):

        index = self.pages.get(
            key
        )

        if index is None:
            return

        self.stack.setCurrentIndex(
            index
        )

        if key == self.PROFILE:

            self.refresh_profile()

            self.load_profile_details()

    # ========================================================
    # CREATE STANDARD PAGE
    # ========================================================

    def create_page(
        self,
        title,
        subtitle,
        back=True,
    ):

        page = QWidget()

        page.setObjectName(
            "SettingsPage"
        )

        root = QVBoxLayout(
            page
        )

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        root.setSpacing(
            10
        )

        # ====================================================
        # BACK
        # ====================================================

        if back:

            button = QPushButton(
                "←  Settings"
            )

            button.setObjectName(
                "SettingsBackButton"
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.clicked.connect(
                lambda:
                self.show_page(
                    self.MENU
                )
            )

            root.addWidget(
                button,
                0,
                Qt.AlignLeft,
            )

        # ====================================================
        # TITLE
        # ====================================================

        page_title = QLabel(
            title
        )

        page_title.setObjectName(
            "SettingsPageTitle"
        )

        root.addWidget(
            page_title
        )

        page_subtitle = QLabel(
            subtitle
        )

        page_subtitle.setObjectName(
            "SettingsPageSubtitle"
        )

        page_subtitle.setWordWrap(
            True
        )

        root.addWidget(
            page_subtitle
        )

        # ====================================================
        # SCROLL
        # ====================================================

        scroll = QScrollArea()

        scroll.setObjectName(
            "SettingsScroll"
        )

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        content.setObjectName(
            "SettingsContent"
        )

        scroll.setWidget(
            content
        )

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            0,
            8,
            8,
            28,
        )

        content_layout.setSpacing(
            13
        )

        root.addWidget(
            scroll,
            1,
        )

        return (
            page,
            content_layout,
        )

    # ========================================================
    # SMALL BUTTON
    # ========================================================

    def action_button(
        self,
        text,
        callback,
    ):

        button = QPushButton(
            text
        )

        button.setObjectName(
            "SettingsSecondaryButton"
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        button.clicked.connect(
            callback
        )

        return button

    # ========================================================
    # MENU
    # ========================================================

    def build_menu_page(
        self
    ):

        page, content = self.create_page(
            "Settings",
            "Manage your LYRx experience.",
            back=False,
        )

        # ====================================================
        # PROFILE PREVIEW
        # ====================================================

        self.menu_profile = QFrame()

        self.menu_profile.setObjectName(
            "SettingsProfileCard"
        )

        profile_layout = QHBoxLayout(
            self.menu_profile
        )

        profile_layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        profile_layout.setSpacing(
            14
        )

        self.menu_avatar = QPushButton(
            "👤"
        )

        self.menu_avatar.setObjectName(
            "SettingsAvatar"
        )

        self.menu_avatar.setFixedSize(
            68,
            68,
        )

        self.menu_avatar.setCursor(
            Qt.PointingHandCursor
        )

        self.menu_avatar.clicked.connect(
            lambda:
            self.show_page(
                self.PROFILE
            )
        )

        profile_layout.addWidget(
            self.menu_avatar
        )

        info = QVBoxLayout()

        info.setSpacing(
            3
        )

        self.menu_name = QLabel(
            "LYRx User"
        )

        self.menu_name.setObjectName(
            "SettingsProfileName"
        )

        self.menu_identity = QLabel(
            "Not signed in"
        )

        self.menu_identity.setObjectName(
            "SettingsProfileEmail"
        )

        self.menu_status = QLabel(
            "Account"
        )

        self.menu_status.setObjectName(
            "SettingsProfileStatus"
        )

        info.addWidget(
            self.menu_name
        )

        info.addWidget(
            self.menu_identity
        )

        info.addWidget(
            self.menu_status
        )

        profile_layout.addLayout(
            info,
            1,
        )

        open_profile = QPushButton(
            "›"
        )

        open_profile.setObjectName(
            "SettingsProfileArrow"
        )

        open_profile.setFixedSize(
            38,
            38,
        )

        open_profile.setCursor(
            Qt.PointingHandCursor
        )

        open_profile.clicked.connect(
            lambda:
            self.show_page(
                self.PROFILE
            )
        )

        profile_layout.addWidget(
            open_profile
        )

        content.addWidget(
            self.menu_profile
        )

        label = QLabel(
            "PREFERENCES"
        )

        label.setObjectName(
            "SettingsMenuSection"
        )

        content.addWidget(
            label
        )

        # ====================================================
        # CATEGORIES
        # ====================================================

        categories = [

            (
                self.APPEARANCE,
                "◐",
                "Appearance",
                "Theme, layout and visual preferences.",
            ),

            (
                self.PLAYBACK,
                "▶",
                "Playback",
                "Autoplay, volume and crossfade controls.",
            ),

            (
                self.AUDIO,
                "♫",
                "Audio Quality",
                "Streaming quality and data usage.",
            ),

            (
                self.STORAGE,
                "▣",
                "Downloads & Storage",
                "Download location and cache management.",
            ),

            (
                self.PRIVACY,
                "⌁",
                "Privacy & Security",
                "Private listening and authentication.",
            ),

            (
                self.NOTIFICATIONS,
                "◉",
                "Notifications",
                "Music and application alerts.",
            ),

            (
                self.LANGUAGE,
                "文",
                "Language & Region",
                "Language and regional preferences.",
            ),

            (
                self.ACCESSIBILITY,
                "A",
                "Accessibility",
                "Motion and text accessibility.",
            ),

            (
                self.ABOUT,
                "i",
                "About LYRx",
                "Version and project information.",
            ),
        ]

        for (
            key,
            icon,
            title,
            subtitle,
        ) in categories:

            card = CategoryCard(
                key,
                icon,
                title,
                subtitle,
            )

            card.clicked.connect(
                self.show_page
            )

            content.addWidget(
                card
            )

        content.addStretch()

        self.register_page(
            self.MENU,
            page
        )

    # ========================================================
    # PROFILE & ACCOUNT
    # ========================================================

    def build_profile_page(
        self
    ):

        page, content = self.create_page(
            "Profile & Account",
            "Manage your LYRx identity and account information.",
        )

        # ====================================================
        # PROFILE HERO
        # ====================================================

        profile = QFrame()

        profile.setObjectName(
            "SettingsProfileCard"
        )

        layout = QVBoxLayout(
            profile
        )

        layout.setContentsMargins(
            22,
            20,
            22,
            20,
        )

        layout.setSpacing(
            16
        )

        top = QHBoxLayout()

        top.setSpacing(
            18
        )

        # ----------------------------------------------------
        # AVATAR
        # ----------------------------------------------------

        self.avatar_button = QPushButton(
            "👤"
        )

        self.avatar_button.setObjectName(
            "SettingsAvatarLarge"
        )

        self.avatar_button.setFixedSize(
            96,
            96,
        )

        self.avatar_button.setCursor(
            Qt.PointingHandCursor
        )

        self.avatar_button.clicked.connect(
            self.change_profile_photo
        )

        top.addWidget(
            self.avatar_button
        )

        # ----------------------------------------------------
        # PROFILE INFO
        # ----------------------------------------------------

        info = QVBoxLayout()

        info.setSpacing(
            5
        )

        self.profile_name = QLabel(
            "LYRx User"
        )

        self.profile_name.setObjectName(
            "SettingsProfileNameLarge"
        )

        self.profile_email = QLabel(
            "Not signed in"
        )

        self.profile_email.setObjectName(
            "SettingsProfileEmail"
        )

        self.profile_status = QLabel(
            "Signed out"
        )

        self.profile_status.setObjectName(
            "SettingsProfileStatus"
        )

        info.addWidget(
            self.profile_name
        )

        info.addWidget(
            self.profile_email
        )

        info.addWidget(
            self.profile_status
        )

        info.addStretch()

        top.addLayout(
            info,
            1
        )

        layout.addLayout(
            top
        )

        # ====================================================
        # PHOTO ACTIONS
        # ====================================================

        photo_actions = QHBoxLayout()

        photo_actions.setSpacing(
            10
        )

        self.change_photo_button = QPushButton(
            "Change Photo"
        )

        self.change_photo_button.setObjectName(
            "SettingsSecondaryButton"
        )

        self.change_photo_button.setCursor(
            Qt.PointingHandCursor
        )

        self.change_photo_button.clicked.connect(
            self.change_profile_photo
        )

        photo_actions.addWidget(
            self.change_photo_button
        )

        self.remove_photo_button = QPushButton(
            "Remove Photo"
        )

        self.remove_photo_button.setObjectName(
            "SettingsDangerButton"
        )

        self.remove_photo_button.setCursor(
            Qt.PointingHandCursor
        )

        self.remove_photo_button.clicked.connect(
            self.remove_profile_photo
        )

        photo_actions.addWidget(
            self.remove_photo_button
        )

        photo_actions.addStretch()

        layout.addLayout(
            photo_actions
        )

        content.addWidget(
            profile
        )

        # ====================================================
        # PERSONAL INFORMATION TITLE
        # ====================================================

        personal_title = QLabel(
            "Personal information"
        )

        personal_title.setObjectName(
            "SettingsSubHeading"
        )

        content.addWidget(
            personal_title
        )

        # ====================================================
        # FIRST NAME
        # ====================================================

        self.first_name_input = QLineEdit()

        self.first_name_input.setObjectName(
            "SettingsInput"
        )

        self.first_name_input.setPlaceholderText(
            "First name"
        )

        self.first_name_input.setFixedWidth(
            260
        )

        content.addWidget(
            SettingRow(
                "First name",
                "Your first name shown across LYRx.",
                self.first_name_input,
            )
        )

        # ====================================================
        # LAST NAME
        # ====================================================

        self.last_name_input = QLineEdit()

        self.last_name_input.setObjectName(
            "SettingsInput"
        )

        self.last_name_input.setPlaceholderText(
            "Last name"
        )

        self.last_name_input.setFixedWidth(
            260
        )

        content.addWidget(
            SettingRow(
                "Last name",
                "Your surname or family name.",
                self.last_name_input,
            )
        )

        # ====================================================
        # DOB
        # ====================================================

        self.dob_input = QDateEdit()

        self.dob_input.setObjectName(
            "SettingsDateInput"
        )

        self.dob_input.setCalendarPopup(
            True
        )

        self.dob_input.setDisplayFormat(
            "dd MMM yyyy"
        )

        self.dob_input.setDateRange(
            QDate(
                1900,
                1,
                1
            ),
            QDate.currentDate()
        )

        self.dob_input.setFixedWidth(
            180
        )

        content.addWidget(
            SettingRow(
                "Date of birth",
                "Used only as part of your local LYRx profile.",
                self.dob_input,
            )
        )

        # ====================================================
        # GENDER
        # ====================================================

        self.gender_input = QComboBox()

        self.gender_input.setObjectName(
            "SettingsCombo"
        )

        self.gender_input.addItems(
            [
                "Prefer not to say",
                "Male",
                "Female",
                "Non-binary",
                "Other",
            ]
        )

        self.gender_input.setFixedWidth(
            180
        )

        content.addWidget(
            SettingRow(
                "Gender",
                "Optional profile information.",
                self.gender_input,
            )
        )

        # ====================================================
        # ACCOUNT INFORMATION
        # ====================================================

        account_title = QLabel(
            "Account information"
        )

        account_title.setObjectName(
            "SettingsSubHeading"
        )

        content.addWidget(
            account_title
        )

        self.profile_phone = QLabel(
            "Not linked"
        )

        self.profile_phone.setObjectName(
            "SettingsValueLabel"
        )

        content.addWidget(
            SettingRow(
                "Phone number",
                "Phone number linked through Firebase Phone OTP.",
                self.profile_phone,
            )
        )

        self.profile_email_value = QLabel(
            "Not linked"
        )

        self.profile_email_value.setObjectName(
            "SettingsValueLabel"
        )

        content.addWidget(
            SettingRow(
                "Email address",
                "Email linked to your Firebase account.",
                self.profile_email_value,
            )
        )

        # ====================================================
        # SAVE
        # ====================================================

        save_row = QHBoxLayout()

        self.save_profile_button = QPushButton(
            "Save Changes"
        )

        self.save_profile_button.setObjectName(
            "SettingsPrimaryButton"
        )

        self.save_profile_button.setCursor(
            Qt.PointingHandCursor
        )

        self.save_profile_button.clicked.connect(
            self.save_profile_details
        )

        save_row.addWidget(
            self.save_profile_button
        )

        save_row.addStretch()

        content.addLayout(
            save_row
        )

        # ====================================================
        # AUTH
        # ====================================================

        auth_title = QLabel(
            "Security"
        )

        auth_title.setObjectName(
            "SettingsSubHeading"
        )

        content.addWidget(
            auth_title
        )

        content.addWidget(
            SettingRow(
                "Authentication",
                "Manage Email, Google and Phone OTP authentication.",
                self.action_button(
                    "Manage Account",
                    self.account_requested.emit,
                ),
            )
        )

        content.addStretch()

        self.register_page(
            self.PROFILE,
            page
        )

    # ========================================================
    # APPEARANCE
    # ========================================================

    def build_appearance_page(
        self
    ):

        page, content = self.create_page(
            "Appearance",
            "Personalize how LYRx looks on your desktop.",
        )

        self.dark_mode = ToggleSwitch()

        self.dark_mode.toggled.connect(
            self.dark_mode_changed
        )

        content.addWidget(
            SettingRow(
                "Dark mode",
                "Use the signature LYRx dark-purple interface.",
                self.dark_mode,
            )
        )

        self.compact_mode = ToggleSwitch()

        self.compact_mode.toggled.connect(
            self.save_settings
        )

        content.addWidget(
            SettingRow(
                "Compact layout",
                "Reduce spacing for a denser desktop layout.",
                self.compact_mode,
            )
        )

        content.addStretch()

        self.register_page(
            self.APPEARANCE,
            page
        )

    # ========================================================
    # PLAYBACK
    # ========================================================

    def build_playback_page(
        self
    ):

        page, content = self.create_page(
            "Playback",
            "Choose how music behaves during listening sessions.",
        )

        self.autoplay = ToggleSwitch()

        self.autoplay.toggled.connect(
            self.save_settings
        )

        content.addWidget(
            SettingRow(
                "Autoplay",
                "Continue playing related music when your queue ends.",
                self.autoplay,
            )
        )

        self.gapless = ToggleSwitch()

        self.gapless.toggled.connect(
            self.save_settings
        )

        content.addWidget(
            SettingRow(
                "Gapless playback",
                "Reduce silence between compatible tracks.",
                self.gapless,
            )
        )

        self.normalize_volume = ToggleSwitch()

        self.normalize_volume.toggled.connect(
            self.save_settings
        )

        content.addWidget(
            SettingRow(
                "Normalize volume",
                "Keep playback levels more consistent between songs.",
                self.normalize_volume,
            )
        )

        self.crossfade = QSlider(
            Qt.Horizontal
        )

        self.crossfade.setRange(
            0,
            12,
        )

        self.crossfade.setFixedWidth(
            190
        )

        self.crossfade.valueChanged.connect(
            self.crossfade_changed
        )

        self.crossfade_label = QLabel(
            "0 sec"
        )

        self.crossfade_label.setObjectName(
            "SettingsValueLabel"
        )

        control = QWidget()

        control_layout = QHBoxLayout(
            control
        )

        control_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        control_layout.addWidget(
            self.crossfade
        )

        control_layout.addWidget(
            self.crossfade_label
        )

        content.addWidget(
            SettingRow(
                "Crossfade",
                "Blend the end of one track into the next.",
                control,
            )
        )

        content.addStretch()

        self.register_page(
            self.PLAYBACK,
            page
        )

    # ========================================================
    # AUDIO
    # ========================================================

    def build_audio_page(
        self
    ):

        page, content = self.create_page(
            "Audio Quality",
            "Control provider-aware streaming preferences and network usage.",
        )

        self.streaming_quality = QComboBox()

        self.streaming_quality.addItems(
            [
                "Automatic",
                "Low",
                "Normal",
                "High",
                "Very High",
            ]
        )

        self.streaming_quality.currentTextChanged.connect(
            self.audio_preferences_changed
        )

        content.addWidget(
            SettingRow(
                "Streaming quality",
                (
                    "LYRx prefers this stream quality when a provider exposes "
                    "multiple playable variants. Providers with one stream "
                    "continue using their available source."
                ),
                self.streaming_quality,
            )
        )

        self.data_saver = ToggleSwitch()

        self.data_saver.toggled.connect(
            self.audio_preferences_changed
        )

        content.addWidget(
            SettingRow(
                "Data saver",
                (
                    "Prefer preview / lower-bandwidth playable sources when "
                    "available and skip non-essential online artwork downloads."
                ),
                self.data_saver,
            )
        )

        self.audio_effective_label = QLabel(
            "Automatic provider selection"
        )

        self.audio_effective_label.setObjectName(
            "SettingsValueLabel"
        )

        content.addWidget(
            SettingRow(
                "Effective network mode",
                "Shows how LYRx will currently handle online playback requests.",
                self.audio_effective_label,
            )
        )

        content.addStretch()

        self.register_page(
            self.AUDIO,
            page
        )

    # ========================================================
    # STORAGE
    # ========================================================

    def build_storage_page(
        self
    ):

        page, content = self.create_page(
            "Downloads & Storage",
            "Manage future offline content and LYRx temporary files.",
        )

        self.download_path_label = QLabel(
            "Default"
        )

        self.download_path_label.setObjectName(
            "SettingsValueLabel"
        )

        change_button = self.action_button(
            "Change",
            self.choose_download_folder,
        )

        open_download_button = self.action_button(
            "Open",
            self.open_download_folder,
        )

        control = QWidget()

        control_layout = QHBoxLayout(
            control
        )

        control_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        control_layout.setSpacing(
            8
        )

        control_layout.addWidget(
            self.download_path_label
        )

        control_layout.addWidget(
            open_download_button
        )

        control_layout.addWidget(
            change_button
        )

        content.addWidget(
            SettingRow(
                "Download location",
                (
                    "Folder reserved for future offline downloads and "
                    "exported LYRx content."
                ),
                control,
            )
        )

        self.cache_size_label = QLabel(
            "Calculating…"
        )

        self.cache_size_label.setObjectName(
            "SettingsValueLabel"
        )

        cache_control = QWidget()

        cache_layout = QHBoxLayout(
            cache_control
        )

        cache_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        cache_layout.setSpacing(
            8
        )

        cache_layout.addWidget(
            self.cache_size_label
        )

        cache_layout.addWidget(
            self.action_button(
                "Open",
                self.open_cache_folder,
            )
        )

        cache_layout.addWidget(
            self.action_button(
                "Clear Cache",
                self.clear_cache,
            )
        )

        content.addWidget(
            SettingRow(
                "Application cache",
                (
                    "Temporary LYRx files stored in your user cache directory. "
                    "Clearing them does not remove your profile or playlists."
                ),
                cache_control,
            )
        )

        self.cache_path_label = QLabel(
            ""
        )

        self.cache_path_label.setObjectName(
            "SettingsDetailMuted"
        )

        self.cache_path_label.setWordWrap(
            True
        )

        content.addWidget(
            self.cache_path_label
        )

        content.addStretch()

        self.register_page(
            self.STORAGE,
            page
        )

    # ========================================================
    # PRIVACY
    # ========================================================

    def build_privacy_page(
        self
    ):

        page, content = self.create_page(
            "Privacy & Security",
            "Control private listening and account security.",
        )

        self.private_session = ToggleSwitch()

        self.private_session.toggled.connect(
            self.private_session_changed
        )

        content.addWidget(
            SettingRow(
                "Private listening session",
                (
                    "Keep the current session private from future "
                    "LYRx recommendation/history signals."
                ),
                self.private_session,
            )
        )

        self.private_session_status = QLabel(
            "Private session is off."
        )

        self.private_session_status.setObjectName(
            "SettingsInfoText"
        )

        self.private_session_status.setWordWrap(
            True
        )

        content.addWidget(
            self.private_session_status
        )

        content.addWidget(
            SettingRow(
                "Authentication",
                (
                    "Manage Firebase email/password, Google Sign-In "
                    "and Phone OTP access."
                ),
                self.action_button(
                    "Account Security",
                    self.account_requested.emit,
                ),
            )
        )

        privacy_button = self.action_button(
            "Open Privacy Policy",
            lambda: self.open_web_link(
                "https://shubham-psingh-dev.github.io/lyrx-website/privacy.html"
            ),
        )

        content.addWidget(
            SettingRow(
                "Privacy policy",
                "Read how the LYRx portfolio build handles account information.",
                privacy_button,
            )
        )

        content.addStretch()

        self.register_page(
            self.PRIVACY,
            page
        )

    # ========================================================
    # NOTIFICATIONS
    # ========================================================

    def build_notifications_page(
        self
    ):

        page, content = self.create_page(
            "Notifications",
            "Choose which LYRx desktop alerts you want to receive.",
        )

        self.music_notifications = ToggleSwitch()

        self.music_notifications.toggled.connect(
            self.notifications_changed
        )

        content.addWidget(
            SettingRow(
                "Music recommendations",
                (
                    "Allow future discovery and recommendation "
                    "notifications when those services are active."
                ),
                self.music_notifications,
            )
        )

        self.app_notifications = ToggleSwitch()

        self.app_notifications.toggled.connect(
            self.notifications_changed
        )

        content.addWidget(
            SettingRow(
                "Application updates",
                "Receive LYRx feature and application update notices.",
                self.app_notifications,
            )
        )

        self.notification_status = QLabel(
            ""
        )

        self.notification_status.setObjectName(
            "SettingsInfoText"
        )

        self.notification_status.setWordWrap(
            True
        )

        content.addWidget(
            self.notification_status
        )

        test_button = self.action_button(
            "Send Test Notification",
            self.test_desktop_notification,
        )

        content.addWidget(
            SettingRow(
                "Test desktop notification",
                (
                    "Send one Windows notification so you can verify "
                    "that desktop alerts are available."
                ),
                test_button,
            )
        )

        content.addStretch()

        self.register_page(
            self.NOTIFICATIONS,
            page
        )

    # ========================================================
    # LANGUAGE
    # ========================================================

    def build_language_page(
        self
    ):

        page, content = self.create_page(
            "Language & Region",
            "Choose interface and regional preferences.",
        )

        # The current UI copy is English-only.
        # Do not expose a fake Hindi translation switch.
        self.language = QComboBox()

        self.language.addItems(
            [
                "English",
            ]
        )

        self.language.currentTextChanged.connect(
            self.save_settings
        )

        content.addWidget(
            SettingRow(
                "Interface language",
                (
                    "English is the supported language in the current "
                    "portfolio build. Hindi localization is planned."
                ),
                self.language,
            )
        )

        self.region = QComboBox()

        self.region.addItems(
            [
                "India",
                "United States",
                "Canada",
                "United Kingdom",
                "Australia",
                "Other",
            ]
        )

        self.region.currentTextChanged.connect(
            self.region_changed
        )

        content.addWidget(
            SettingRow(
                "Region",
                (
                    "Saved locally for future regional recommendations, "
                    "content and account preferences."
                ),
                self.region,
            )
        )

        self.language_status = QLabel(
            "Current build language: English"
        )

        self.language_status.setObjectName(
            "SettingsInfoText"
        )

        content.addWidget(
            self.language_status
        )

        content.addStretch()

        self.register_page(
            self.LANGUAGE,
            page
        )

    # ========================================================
    # ACCESSIBILITY
    # ========================================================

    def build_accessibility_page(
        self
    ):

        page, content = self.create_page(
            "Accessibility",
            "Make LYRx more comfortable to use.",
        )

        self.reduce_motion = ToggleSwitch()

        self.reduce_motion.toggled.connect(
            self.accessibility_changed
        )

        content.addWidget(
            SettingRow(
                "Reduce motion",
                (
                    "Disable animated movement in supported LYRx "
                    "controls, including Settings toggles."
                ),
                self.reduce_motion,
            )
        )

        self.large_text = ToggleSwitch()

        self.large_text.toggled.connect(
            self.accessibility_changed
        )

        content.addWidget(
            SettingRow(
                "Larger text",
                (
                    "Increase text size across the Settings experience "
                    "for easier reading."
                ),
                self.large_text,
            )
        )

        self.accessibility_status = QLabel(
            ""
        )

        self.accessibility_status.setObjectName(
            "SettingsInfoText"
        )

        self.accessibility_status.setWordWrap(
            True
        )

        content.addWidget(
            self.accessibility_status
        )

        content.addStretch()

        self.register_page(
            self.ACCESSIBILITY,
            page
        )

    # ========================================================
    # ABOUT
    # ========================================================

    def build_about_page(
        self
    ):

        page, content = self.create_page(
            "About LYRx",
            "Project information, links and current build details.",
        )

        version = QLabel(
            "v0.1 • Day 25"
        )

        version.setObjectName(
            "SettingsValueLabel"
        )

        content.addWidget(
            SettingRow(
                "Version",
                "Current LYRx desktop portfolio build.",
                version,
            )
        )

        technology = QLabel(
            "Python • PySide6 • Firebase"
        )

        technology.setObjectName(
            "SettingsValueLabel"
        )

        content.addWidget(
            SettingRow(
                "Technology",
                "Core technologies used by the current build.",
                technology,
            )
        )

        project = QLabel(
            "Active Development"
        )

        project.setObjectName(
            "SettingsValueLabel"
        )

        content.addWidget(
            SettingRow(
                "Project status",
                "LYRx is an independently developed portfolio project.",
                project,
            )
        )

        content.addWidget(
            SettingRow(
                "LYRx website",
                "Open the public LYRx project website.",
                self.action_button(
                    "Open Website",
                    lambda: self.open_web_link(
                        "https://shubham-psingh-dev.github.io/lyrx-website/"
                    ),
                ),
            )
        )

        content.addWidget(
            SettingRow(
                "Privacy",
                "View the public LYRx Privacy Policy.",
                self.action_button(
                    "Privacy Policy",
                    lambda: self.open_web_link(
                        "https://shubham-psingh-dev.github.io/lyrx-website/privacy.html"
                    ),
                ),
            )
        )

        content.addWidget(
            SettingRow(
                "Terms",
                "View the public LYRx Terms of Service.",
                self.action_button(
                    "Terms of Service",
                    lambda: self.open_web_link(
                        "https://shubham-psingh-dev.github.io/lyrx-website/terms.html"
                    ),
                ),
            )
        )

        content.addStretch()

        self.register_page(
            self.ABOUT,
            page
        )

    # ========================================================
    # STEP 5 - PRIVACY / NOTIFICATIONS / ACCESSIBILITY HELPERS
    # ========================================================

    def private_session_changed(
        self,
        *_,
    ):

        self.save_settings()
        self.update_private_session_status()

    def update_private_session_status(
        self,
    ):

        enabled = self.private_session.isChecked()

        if enabled:

            self.private_session_status.setText(
                "Private session is ON. New listening signals will be "
                "treated as private where LYRx stores or uses them."
            )

        else:

            self.private_session_status.setText(
                "Private session is OFF. Normal LYRx listening behavior is active."
            )

    def notifications_changed(
        self,
        *_,
    ):

        self.save_settings()
        self.update_notification_status()

    def update_notification_status(
        self,
    ):

        enabled = []

        if self.music_notifications.isChecked():
            enabled.append(
                "music recommendations"
            )

        if self.app_notifications.isChecked():
            enabled.append(
                "application updates"
            )

        if enabled:

            self.notification_status.setText(
                "Enabled: "
                + ", ".join(enabled)
                + "."
            )

        else:

            self.notification_status.setText(
                "All LYRx notification categories are disabled."
            )

    def _notification_icon(
        self,
    ) -> QIcon:

        window_icon = self.window().windowIcon()

        if not window_icon.isNull():
            return window_icon

        pixmap = QPixmap(
            64,
            64,
        )

        pixmap.fill(
            QColor("#7C3AED")
        )

        painter = QPainter(
            pixmap
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setPen(
            QColor("#FFFFFF")
        )

        font = painter.font()
        font.setBold(True)
        font.setPointSize(28)
        painter.setFont(font)

        painter.drawText(
            pixmap.rect(),
            Qt.AlignCenter,
            "L",
        )

        painter.end()

        return QIcon(
            pixmap
        )

    def test_desktop_notification(
        self,
    ):

        if not QSystemTrayIcon.isSystemTrayAvailable():

            self.show_lyrx_message(
                "Notifications",
                (
                    "Windows system-tray notifications are not available "
                    "in this session. Your LYRx notification preferences "
                    "are still saved."
                ),
            )

            return

        try:

            if getattr(
                self,
                "_test_tray",
                None,
            ) is not None:

                try:
                    self._test_tray.hide()
                    self._test_tray.deleteLater()
                except Exception:
                    pass

            self._test_tray = QSystemTrayIcon(
                self._notification_icon(),
                self,
            )

            self._test_tray.setToolTip(
                "LYRx"
            )

            self._test_tray.show()

            self._test_tray.showMessage(
                "LYRx",
                "Desktop notifications are working. 💜",
                QSystemTrayIcon.Information,
                3500,
            )

            # Keep the tray icon alive long enough for Windows to
            # display the toast, then remove it.
            QTimer.singleShot(
                5000,
                self._hide_test_tray,
            )

        except Exception as error:

            print(
                "LYRx notification test error:",
                error
            )

            self.show_lyrx_message(
                "Notifications",
                "LYRx could not send the test desktop notification.",
            )

    def _hide_test_tray(
        self,
    ):

        tray = getattr(
            self,
            "_test_tray",
            None,
        )

        if tray is None:
            return

        try:
            tray.hide()
            tray.deleteLater()
        except Exception:
            pass

        self._test_tray = None

    def region_changed(
        self,
        *_,
    ):

        self.save_settings()

    def accessibility_changed(
        self,
        *_,
    ):

        self.save_settings()
        self.apply_accessibility_preferences()

    def apply_accessibility_preferences(
        self,
    ):

        large_text = self.large_text.isChecked()
        reduce_motion = self.reduce_motion.isChecked()

        if large_text:

            self.main.setStyleSheet(
                """
                QLabel#SettingsPageTitle {
                    font-size: 34px;
                }

                QLabel#SettingsPageSubtitle {
                    font-size: 15px;
                }

                QLabel#SettingsCategoryTitle {
                    font-size: 16px;
                }

                QLabel#SettingsCategorySubtitle {
                    font-size: 13px;
                }

                QLabel#SettingRowTitle {
                    font-size: 15px;
                }

                QLabel#SettingRowDescription {
                    font-size: 13px;
                }

                QLabel#SettingsValueLabel,
                QLabel#SettingsInfoText {
                    font-size: 13px;
                }
                """
            )

        else:

            self.main.setStyleSheet(
                ""
            )

        states = []

        if large_text:
            states.append(
                "larger text"
            )

        if reduce_motion:
            states.append(
                "reduced motion"
            )

        if states:

            self.accessibility_status.setText(
                "Active accessibility options: "
                + ", ".join(states)
                + "."
            )

        else:

            self.accessibility_status.setText(
                "Default accessibility presentation is active."
            )

    def open_web_link(
        self,
        url: str,
    ):

        opened = QDesktopServices.openUrl(
            QUrl(
                str(url)
            )
        )

        if not opened:

            self.show_lyrx_message(
                "LYRx",
                "The requested link could not be opened.",
            )

    # ========================================================
    # LYRx MODERN MESSAGE
    # ========================================================

    def show_lyrx_message(
        self,
        title: str,
        message: str,
    ):

        dialog = LYRxDialog(
            self,
            title=title,
            message=message,
            confirm_text="OK",
            is_dark=self.current_is_dark,
        )

        dialog.exec()

    # ========================================================
    # DAY 25 - USER PROFILE KEYS
    # ========================================================

    def current_uid(
        self
    ):

        return str(
            self.settings.value(
                "auth/uid",
                "",
            )
            or ""
        ).strip()

    def profile_key(
        self,
        field
    ):

        uid = self.current_uid()

        if not uid:
            return ""

        return (
            f"profile/firebase_users/"
            f"{uid}/{field}"
        )

    # ========================================================
    # CHANGE PROFILE PHOTO
    # ========================================================

    def change_profile_photo(
        self
    ):

        uid = self.current_uid()

        if not uid:

            self.show_lyrx_message(
                "LYRx Profile",
                "Sign in first to change your profile photo.",
            )

            return

        path, _ = QFileDialog.getOpenFileName(

            self,

            "Choose LYRx Profile Photo",

            str(
                Path.home()
            ),

            (
                "Images "
                "(*.png *.jpg *.jpeg *.webp *.bmp)"
            )
        )

        if not path:
            return

        avatar_key = self.profile_key(
            "avatar_path"
        )

        if not avatar_key:
            return

        self.settings.setValue(
            avatar_key,
            path
        )

        self.settings.setValue(
            self.profile_key("avatar_removed"),
            False,
        )

        self.settings.sync()

        self.refresh_profile()

        self.profile_updated.emit()

    # ========================================================
    # REMOVE PROFILE PHOTO
    # ========================================================

    def remove_profile_photo(
        self
    ):

        uid = self.current_uid()

        if not uid:
            self.show_lyrx_message(
                "LYRx Profile",
                "Sign in first to manage your profile photo.",
            )
            return

        avatar_key = self.profile_key(
            "avatar_path"
        )

        if not avatar_key:
            return

        # Even when the current photo originally came from the old
        # legacy profile, removing it should suppress that fallback.
        dialog = LYRxDialog(
            self,
            title="Remove Profile Photo",
            message=(
                "Remove your current LYRx profile photo? "
                "Your initials will be shown instead."
            ),
            confirm_text="Remove",
            cancel_text="Keep Photo",
            destructive=True,
            is_dark=self.current_is_dark,
        )

        dialog.exec()

        if not dialog.accepted_action:
            return

        self.settings.setValue(
            avatar_key,
            AVATAR_REMOVED_SENTINEL,
        )

        # Also mark this UID as explicitly having removed its avatar.
        self.settings.setValue(
            self.profile_key("avatar_removed"),
            True,
        )

        self.settings.sync()

        self.refresh_profile()
        self.profile_updated.emit()

    # ========================================================
    # LOAD PERSONAL PROFILE
    # ========================================================

    def load_profile_details(
        self
    ):

        uid = self.current_uid()

        logged_in = self.settings.value(
            "auth/logged_in",
            False,
            type=bool,
        )

        for control in (
            self.first_name_input,
            self.last_name_input,
            self.dob_input,
            self.gender_input,
            self.save_profile_button,
            self.change_photo_button,
            self.remove_photo_button,
        ):

            control.setEnabled(
                logged_in
                and bool(uid)
            )

        if not logged_in or not uid:

            self.first_name_input.clear()

            self.last_name_input.clear()

            self.gender_input.setCurrentIndex(
                0
            )

            self.dob_input.setDate(
                QDate(
                    2000,
                    1,
                    1
                )
            )

            return

        first_name = str(
            self.settings.value(
                self.profile_key(
                    "first_name"
                ),
                "",
            )
            or ""
        ).strip()

        last_name = str(
            self.settings.value(
                self.profile_key(
                    "last_name"
                ),
                "",
            )
            or ""
        ).strip()

        # ----------------------------------------------------
        # MIGRATE EXISTING DISPLAY NAME
        # ----------------------------------------------------

        if (
            not first_name
            and
            not last_name
        ):

            existing_name = str(
                self.settings.value(
                    self.profile_key(
                        "display_name"
                    ),
                    "",
                )
                or ""
            ).strip()

            if existing_name:

                parts = existing_name.split(
                    " ",
                    1
                )

                first_name = (
                    parts[0]
                    if parts
                    else ""
                )

                last_name = (
                    parts[1]
                    if len(parts) > 1
                    else ""
                )

        self.first_name_input.setText(
            first_name
        )

        self.last_name_input.setText(
            last_name
        )

        # ----------------------------------------------------
        # DOB
        # ----------------------------------------------------

        dob_text = str(
            self.settings.value(
                self.profile_key(
                    "date_of_birth"
                ),
                "",
            )
            or ""
        ).strip()

        dob = QDate.fromString(
            dob_text,
            "yyyy-MM-dd"
        )

        if dob.isValid():

            self.dob_input.setDate(
                dob
            )

        else:

            self.dob_input.setDate(
                QDate(
                    2000,
                    1,
                    1
                )
            )

        # ----------------------------------------------------
        # GENDER
        # ----------------------------------------------------

        gender = str(
            self.settings.value(
                self.profile_key(
                    "gender"
                ),
                "Prefer not to say",
            )
            or
            "Prefer not to say"
        )

        index = self.gender_input.findText(
            gender
        )

        self.gender_input.setCurrentIndex(
            index
            if index >= 0
            else 0
        )

    # ========================================================
    # SAVE PERSONAL PROFILE
    # ========================================================

    def save_profile_details(
        self
    ):

        uid = self.current_uid()

        if not uid:

            self.show_lyrx_message(
                "LYRx Profile",
                "Sign in first to edit your profile.",
            )

            return

        first_name = (
            self.first_name_input
            .text()
            .strip()
        )

        last_name = (
            self.last_name_input
            .text()
            .strip()
        )

        if not first_name:

            self.show_lyrx_message(
                "LYRx Profile",
                "Please enter your first name.",
            )

            return

        display_name = " ".join(
            item
            for item in (
                first_name,
                last_name,
            )
            if item
        )

        self.settings.setValue(
            self.profile_key(
                "first_name"
            ),
            first_name
        )

        self.settings.setValue(
            self.profile_key(
                "last_name"
            ),
            last_name
        )

        # Existing Header / LocalProfileStore already
        # reads this key.
        self.settings.setValue(
            self.profile_key(
                "display_name"
            ),
            display_name
        )

        self.settings.setValue(
            "profile/last_display_name",
            display_name
        )

        self.settings.setValue(
            self.profile_key(
                "date_of_birth"
            ),
            self.dob_input
            .date()
            .toString(
                "yyyy-MM-dd"
            )
        )

        self.settings.setValue(
            self.profile_key(
                "gender"
            ),
            self.gender_input.currentText()
        )

        self.settings.sync()

        self.refresh_profile()

        self.profile_updated.emit()

        self.show_lyrx_message(
            "Profile Updated",
            "Your LYRx profile has been saved successfully.",
        )    

    # ========================================================
    # PROFILE REFRESH
    # ========================================================

    def refresh_profile(
        self
    ):

        logged_in = self.settings.value(
            "auth/logged_in",
            False,
            type=bool,
        )

        uid = str(
            self.settings.value(
                "auth/uid",
                "",
            )
            or ""
        ).strip()

        email = str(
            self.settings.value(
                "auth/email",
                "",
            )
            or ""
        ).strip()

        phone = str(
            self.settings.value(
                "auth/phone_number",
                "",
            )
            or ""
        ).strip()

        firebase_name = str(
            self.settings.value(
                "auth/display_name",
                "",
            )
            or ""
        ).strip()

        display_name = firebase_name

        avatar_path = ""

        if uid:

            name_key = (
                f"profile/firebase_users/"
                f"{uid}/display_name"
            )

            avatar_key = (
                f"profile/firebase_users/"
                f"{uid}/avatar_path"
            )

            local_name = str(
                self.settings.value(
                    name_key,
                    "",
                )
                or ""
            ).strip()

            avatar_path = str(
                self.settings.value(
                    avatar_key,
                    "",
                )
                or ""
            ).strip()

            if avatar_path == AVATAR_REMOVED_SENTINEL:
                avatar_path = ""

            if local_name:

                display_name = local_name

        if not display_name:

            if email:

                display_name = (
                    email.split("@")[0]
                )

            elif phone:

                display_name = (
                    "LYRx Listener"
                )

            else:

                display_name = (
                    "LYRx User"
                )

        identity = (
            email
            or phone
            or "Not signed in"
        )

        if logged_in:

            if (
                phone
                and
                not email
            ):

                status = (
                    "Phone OTP • Signed in"
                )

            else:

                status = (
                    "Firebase Account • Signed in"
                )

        else:

            status = (
                "Signed out"
            )

        # ====================================================
        # MENU PROFILE
        # ====================================================

        self.menu_name.setText(
            display_name
        )

        self.menu_identity.setText(
            identity
        )

        self.menu_status.setText(
            status
        )

        # ====================================================
        # PROFILE PAGE
        # ====================================================

        self.profile_name.setText(
            display_name
        )

        self.profile_email.setText(
            identity
        )

        self.profile_status.setText(
            status
        )

        self.profile_phone.setText(
            phone
            or "Not linked"
        )

        self.profile_email_value.setText(
            email
            or "Not linked"
        )

        # ====================================================
        # AVATARS
        # ====================================================

        avatar_targets = [

            (
                self.menu_avatar,
                68,
            ),

            (
                self.avatar_button,
                90,
            ),
        ]

        for (
            target,
            size,
        ) in avatar_targets:

            icon = circular_avatar(
                avatar_path,
                size,
            )

            if icon.isNull():

                target.setIcon(
                    QIcon()
                )

                target.setText(
                    display_name[:1].upper()
                    if display_name
                    else "👤"
                )

            else:

                target.setText(
                    ""
                )

                target.setIcon(
                    icon
                )

                target.setIconSize(
                    QSize(
                        size,
                        size,
                    )
                )

        # Keep editable personal-information fields in sync
        # whenever authentication/profile state changes.
        try:
            self.load_profile_details()
        except Exception as error:
            print(
                "Settings profile form refresh error:",
                error
            )

    # ========================================================
    # DARK MODE
    # ========================================================

    def dark_mode_changed(
        self,
        checked
    ):

        self.settings.setValue(
            "settings/dark_mode",
            bool(
                checked
            ),
        )

        self.settings.sync()

        self.theme_requested.emit(
            bool(
                checked
            )
        )

        self.settings_changed.emit()

    # ========================================================
    # CROSSFADE
    # ========================================================

    def crossfade_changed(
        self,
        value
    ):

        self.crossfade_label.setText(
            f"{value} sec"
        )

        self.save_settings()

    # ========================================================
    # AUDIO / DATA SAVER
    # ========================================================

    def audio_preferences_changed(
        self,
        *_
    ):

        self.update_audio_effective_label()

        self.save_settings()

    def update_audio_effective_label(
        self
    ):

        if not hasattr(
            self,
            "audio_effective_label"
        ):
            return

        quality = (
            self.streaming_quality.currentText()
            if hasattr(
                self,
                "streaming_quality"
            )
            else "Automatic"
        )

        saver = bool(
            self.data_saver.isChecked()
            if hasattr(
                self,
                "data_saver"
            )
            else False
        )

        if saver:
            text = (
                "Data Saver • lowest / preview source preferred • "
                "online artwork reduced"
            )
        elif quality == "Automatic":
            text = "Automatic • provider selects the playable source"
        else:
            text = (
                f"{quality} preference • provider fallback enabled"
            )

        self.audio_effective_label.setText(
            text
        )

    # ========================================================
    # DOWNLOAD FOLDER
    # ========================================================

    def default_download_folder(
        self
    ) -> Path:

        downloads = str(
            QStandardPaths.writableLocation(
                QStandardPaths.DownloadLocation
            )
            or ""
        ).strip()

        if downloads:
            path = Path(downloads) / "LYRx"
        else:
            path = Path.home() / "Downloads" / "LYRx"

        return path

    def current_download_folder(
        self
    ) -> Path:

        saved = str(
            self.settings.value(
                "settings/download_path",
                "",
            )
            or ""
        ).strip()

        if saved:
            return Path(saved)

        return self.default_download_folder()

    def choose_download_folder(
        self
    ):

        current = self.current_download_folder()

        selected = QFileDialog.getExistingDirectory(
            self,
            "Choose LYRx Download Folder",
            str(current),
        )

        if not selected:
            return

        selected_path = Path(selected)

        try:
            selected_path.mkdir(
                parents=True,
                exist_ok=True,
            )
        except Exception:
            pass

        self.settings.setValue(
            "settings/download_path",
            str(selected_path),
        )

        self.settings.sync()

        self.download_path_label.setText(
            str(selected_path)
        )

        self.settings_changed.emit()

    def open_download_folder(
        self
    ):

        folder = self.current_download_folder()

        try:
            folder.mkdir(
                parents=True,
                exist_ok=True,
            )
        except Exception:
            pass

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(folder.resolve())
            )
        )

    # ========================================================
    # CACHE
    # ========================================================

    def refresh_storage_info(
        self
    ):

        cache_dir = lyrx_cache_dir()

        if hasattr(
            self,
            "cache_size_label"
        ):
            self.cache_size_label.setText(
                format_bytes(
                    directory_size(
                        cache_dir
                    )
                )
            )

        if hasattr(
            self,
            "cache_path_label"
        ):
            self.cache_path_label.setText(
                f"Cache location: {cache_dir}"
            )

        if hasattr(
            self,
            "download_path_label"
        ):
            self.download_path_label.setText(
                str(
                    self.current_download_folder()
                )
            )

    def open_cache_folder(
        self
    ):

        cache_dir = lyrx_cache_dir()

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(cache_dir.resolve())
            )
        )

    def clear_cache(
        self
    ):

        cache_dir = lyrx_cache_dir()

        current_size = format_bytes(
            directory_size(
                cache_dir
            )
        )

        dialog = LYRxDialog(
            self,
            title="Clear LYRx Cache",
            message=(
                f"Remove {current_size} of temporary LYRx files?\n\n"
                "Your profile, authentication, playlists and settings "
                "will not be removed."
            ),
            confirm_text="Clear Cache",
            cancel_text="Cancel",
            destructive=True,
            is_dark=self.current_is_dark,
        )

        dialog.exec()

        if not dialog.accepted_action:
            return

        removed_files = 0

        for item in list(
            cache_dir.iterdir()
        ):
            try:
                if item.is_dir():
                    shutil.rmtree(
                        item,
                        ignore_errors=True,
                    )
                else:
                    item.unlink(
                        missing_ok=True
                    )

                removed_files += 1
            except Exception:
                pass

        cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.settings.remove(
            "cache"
        )

        self.settings.sync()

        self.refresh_storage_info()

        self.settings_changed.emit()

        done = LYRxDialog(
            self,
            title="Cache Cleared",
            message=(
                "Temporary LYRx cache has been cleared successfully."
            ),
            confirm_text="Done",
            is_dark=self.current_is_dark,
        )

        dialog.exec()

    # ========================================================
    # LOAD SETTINGS
    # ========================================================

    def load_settings(
        self
    ):

        controls = [

            self.dark_mode,

            self.compact_mode,

            self.autoplay,

            self.gapless,

            self.normalize_volume,

            self.crossfade,

            self.streaming_quality,

            self.data_saver,

            self.private_session,

            self.music_notifications,

            self.app_notifications,

            self.language,

            self.region,

            self.reduce_motion,

            self.large_text,
        ]

        for control in controls:

            control.blockSignals(
                True
            )

        # ====================================================
        # APPEARANCE
        # ====================================================

        self.dark_mode.setChecked(

            self.settings.value(
                "settings/dark_mode",
                True,
                type=bool,
            )
        )

        self.compact_mode.setChecked(

            self.settings.value(
                "settings/compact_mode",
                False,
                type=bool,
            )
        )

        # ====================================================
        # PLAYBACK
        # ====================================================

        self.autoplay.setChecked(

            self.settings.value(
                "settings/autoplay",
                True,
                type=bool,
            )
        )

        self.gapless.setChecked(

            self.settings.value(
                "settings/gapless",
                True,
                type=bool,
            )
        )

        self.normalize_volume.setChecked(

            self.settings.value(
                "settings/normalize_volume",
                True,
                type=bool,
            )
        )

        self.crossfade.setValue(

            int(
                self.settings.value(
                    "settings/crossfade",
                    0,
                )
                or 0
            )
        )

        self.crossfade_label.setText(
            f"{self.crossfade.value()} sec"
        )

        # ====================================================
        # AUDIO
        # ====================================================

        quality = str(
            self.settings.value(
                "settings/streaming_quality",
                "Automatic",
            )
            or "Automatic"
        )

        quality_index = (
            self.streaming_quality
            .findText(
                quality
            )
        )

        if quality_index >= 0:

            self.streaming_quality.setCurrentIndex(
                quality_index
            )

        self.data_saver.setChecked(

            self.settings.value(
                "settings/data_saver",
                False,
                type=bool,
            )
        )

        self.update_audio_effective_label()

        # ====================================================
        # STORAGE
        # ====================================================

        download_path = str(
            self.settings.value(
                "settings/download_path",
                "",
            )
            or ""
        ).strip()

        self.download_path_label.setText(
            download_path
            or str(
                self.default_download_folder()
            )
        )

        self.refresh_storage_info()

        # ====================================================
        # PRIVACY
        # ====================================================

        self.private_session.setChecked(

            self.settings.value(
                "settings/private_session",
                False,
                type=bool,
            )
        )

        # ====================================================
        # NOTIFICATIONS
        # ====================================================

        self.music_notifications.setChecked(

            self.settings.value(
                "settings/music_notifications",
                True,
                type=bool,
            )
        )

        self.app_notifications.setChecked(

            self.settings.value(
                "settings/app_notifications",
                True,
                type=bool,
            )
        )

        # ====================================================
        # LANGUAGE
        # ====================================================

        language = str(
            self.settings.value(
                "settings/language",
                "English",
            )
            or "English"
        )

        language_index = (
            self.language.findText(
                language
            )
        )

        if language_index >= 0:

            self.language.setCurrentIndex(
                language_index
            )

        region = str(
            self.settings.value(
                "settings/region",
                "India",
            )
            or "India"
        )

        region_index = self.region.findText(
            region
        )

        if region_index >= 0:

            self.region.setCurrentIndex(
                region_index
            )

        # ====================================================
        # ACCESSIBILITY
        # ====================================================

        self.reduce_motion.setChecked(

            self.settings.value(
                "settings/reduce_motion",
                False,
                type=bool,
            )
        )

        self.large_text.setChecked(

            self.settings.value(
                "settings/large_text",
                False,
                type=bool,
            )
        )

        # ====================================================
        # SYNC CUSTOM TOGGLE POSITIONS
        # ====================================================

        for toggle in (

            self.dark_mode,

            self.compact_mode,

            self.autoplay,

            self.gapless,

            self.normalize_volume,

            self.data_saver,

            self.private_session,

            self.music_notifications,

            self.app_notifications,

            self.reduce_motion,

            self.large_text,

        ):

            toggle.sync_position()

        self.update_private_session_status()
        self.update_notification_status()
        self.apply_accessibility_preferences()

        # ====================================================
        # RESTORE SIGNALS
        # ====================================================

        for control in controls:

            control.blockSignals(
                False
            )

    # ========================================================
    # SAVE
    # ========================================================

    def save_settings(
        self,
        *_,
    ):

        self.settings.setValue(
            "settings/compact_mode",
            self.compact_mode.isChecked(),
        )

        self.settings.setValue(
            "settings/autoplay",
            self.autoplay.isChecked(),
        )

        self.settings.setValue(
            "settings/gapless",
            self.gapless.isChecked(),
        )

        self.settings.setValue(
            "settings/normalize_volume",
            self.normalize_volume.isChecked(),
        )

        self.settings.setValue(
            "settings/crossfade",
            self.crossfade.value(),
        )

        self.settings.setValue(
            "settings/streaming_quality",
            self.streaming_quality.currentText(),
        )

        self.settings.setValue(
            "settings/data_saver",
            self.data_saver.isChecked(),
        )

        self.settings.setValue(
            "settings/private_session",
            self.private_session.isChecked(),
        )

        self.settings.setValue(
            "settings/music_notifications",
            self.music_notifications.isChecked(),
        )

        self.settings.setValue(
            "settings/app_notifications",
            self.app_notifications.isChecked(),
        )

        self.settings.setValue(
            "settings/language",
            self.language.currentText(),
        )

        self.settings.setValue(
            "settings/region",
            self.region.currentText(),
        )

        self.settings.setValue(
            "settings/reduce_motion",
            self.reduce_motion.isChecked(),
        )

        self.settings.setValue(
            "settings/large_text",
            self.large_text.isChecked(),
        )

        self.settings.sync()

        self.settings_changed.emit()

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

        self.dark_mode.blockSignals(
            True
        )

        self.dark_mode.setChecked(
            self.current_is_dark
        )

        self.dark_mode.sync_position()

        self.dark_mode.blockSignals(
            False
        )

        try:

            self.sidebar.set_theme_state(
                self.current_is_dark
            )

        except Exception:

            pass

        self.apply_theme()

    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(
        self
    ):

        if self.current_is_dark:

            self.setStyleSheet(
                """

                QWidget#SettingsMain,
                QWidget#SettingsPage,
                QWidget#SettingsContent,
                QScrollArea#SettingsScroll,
                QStackedWidget#SettingsStack {

                    background: #0E0916;
                    border: none;

                }


                QLabel#SettingsPageTitle {

                    color: white;

                    font-size: 30px;

                    font-weight: 800;

                }


                QLabel#SettingsPageSubtitle {

                    color: #A99DB8;

                    font-size: 13px;

                }


                QLabel#SettingsMenuSection {

                    color: #8F7EA7;

                    font-size: 10px;

                    font-weight: 800;

                    letter-spacing: 1px;

                    padding-top: 7px;

                }


                QFrame#SettingsCategoryCard,
                QFrame#SettingsProfileCard,
                QFrame#SettingRow {

                    background: #171023;

                    border: 1px solid #302043;

                    border-radius: 15px;

                }


                QFrame#SettingsCategoryCard:hover {

                    background: #1D132B;

                    border: 1px solid #68458E;

                }


                QFrame#SettingRow:hover {

                    background: #1B1229;

                    border: 1px solid #493063;

                }


                QLabel#SettingsCategoryIcon {

                    background: #28163D;

                    color: #BF8DFF;

                    border: 1px solid #4C2A6C;

                    border-radius: 12px;

                    font-size: 17px;

                    font-weight: 800;

                }


                QLabel#SettingsCategoryTitle {

                    color: white;

                    font-size: 14px;

                    font-weight: 800;

                }


                QLabel#SettingsCategorySubtitle {

                    color: #9B8FAB;

                    font-size: 11px;

                }


                QLabel#SettingsCategoryArrow {

                    color: #9C6BDA;

                    font-size: 28px;

                }


                QLabel#SettingsProfileName {

                    color: white;

                    font-size: 18px;

                    font-weight: 800;

                }


                QLabel#SettingsProfileNameLarge {

                    color: white;

                    font-size: 23px;

                    font-weight: 800;

                }


                QLabel#SettingsProfileEmail {

                    color: #BFB1CE;

                    font-size: 12px;

                }


                QLabel#SettingsProfileStatus {

                    color: #A45CFF;

                    font-size: 11px;

                    font-weight: 700;

                }


                QLabel#SettingRowTitle {

                    color: white;

                    font-size: 13px;

                    font-weight: 700;

                }


                QLabel#SettingRowDescription {

                    color: #9E91AC;

                    font-size: 11px;

                }


                QLabel#SettingsValueLabel {

                    color: #C7B4DF;

                    font-size: 11px;

                    font-weight: 600;

                }


                QLabel#SettingsInfoText {

                    color: #9D8CAF;

                    font-size: 11px;

                    background: transparent;

                    padding: 4px 2px;

                }


                QPushButton#SettingsAvatar {

                    background: #28163D;

                    color: white;

                    border: 1px solid #60368F;

                    border-radius: 34px;

                    font-size: 23px;

                    font-weight: 800;

                }


                QPushButton#SettingsAvatarLarge {

                    background: #28163D;

                    color: white;

                    border: 1px solid #60368F;

                    border-radius: 45px;

                    font-size: 28px;

                    font-weight: 800;

                }


                QPushButton#SettingsProfileArrow {

                    background: #21162E;

                    color: #C18CFF;

                    border: 1px solid #402957;

                    border-radius: 19px;

                    font-size: 24px;

                }


                QPushButton#SettingsProfileArrow:hover {

                    background: #2A1B3B;

                    border: 1px solid #744AA0;

                }


                QPushButton#SettingsBackButton {

                    background: transparent;

                    color: #B27BF3;

                    border: none;

                    padding: 4px 2px;

                    font-size: 12px;

                    font-weight: 700;

                    text-align: left;

                }


                QPushButton#SettingsBackButton:hover {

                    color: white;

                }


                QPushButton#SettingsPrimaryButton {

                    background: #8438F4;

                    color: white;

                    border: none;

                    border-radius: 10px;

                    padding: 10px 16px;

                    font-weight: 700;

                }


                QPushButton#SettingsPrimaryButton:hover {

                    background: #984DFF;

                }


                QPushButton#SettingsSecondaryButton {

                    background: #21162E;

                    color: #EEE6F7;

                    border: 1px solid #3D2A52;

                    border-radius: 9px;

                    padding: 8px 13px;

                    font-weight: 600;

                }


                QPushButton#SettingsSecondaryButton:hover {

                    background: #291B39;

                    border: 1px solid #73499B;

                }


                QLabel#SettingsSubHeading {
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: 800;
                    padding-top: 10px;
                }

                QLineEdit#SettingsInput,
                QDateEdit#SettingsDateInput {
                    background: #21162E;
                    color: #FFFFFF;
                    border: 1px solid #3B2850;
                    border-radius: 9px;
                    padding: 8px 10px;
                    min-height: 20px;
                }

                QLineEdit#SettingsInput:focus,
                QDateEdit#SettingsDateInput:focus {
                    border: 1px solid #8B5CF6;
                }

                QPushButton#SettingsDangerButton {
                    background: transparent;
                    color: #F29AA8;
                    border: 1px solid #613341;
                    border-radius: 9px;
                    padding: 8px 13px;
                    font-weight: 600;
                }

                QPushButton#SettingsDangerButton:hover {
                    background: #351722;
                    color: #FFFFFF;
                    border: 1px solid #A34A60;
                }

                QComboBox {

                    background: #21162E;

                    color: white;

                    border: 1px solid #3B2850;

                    border-radius: 9px;

                    padding: 7px 10px;

                    min-width: 135px;

                }


                QComboBox QAbstractItemView {

                    background: #1B1227;

                    color: white;

                    selection-background-color: #7C3AED;

                }


                QSlider::groove:horizontal {

                    height: 4px;

                    background: #3A2C49;

                    border-radius: 2px;

                }


                QSlider::sub-page:horizontal {

                    background: #8B45F7;

                    border-radius: 2px;

                }


                QSlider::handle:horizontal {

                    background: white;

                    width: 14px;

                    height: 14px;

                    margin: -5px 0;

                    border-radius: 7px;

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

                    height: 0px;

                }

                """
            )

        else:

            self.setStyleSheet(
                """

                QWidget#SettingsMain,
                QWidget#SettingsPage,
                QWidget#SettingsContent,
                QScrollArea#SettingsScroll,
                QStackedWidget#SettingsStack {

                    background: #F6F1FA;

                    border: none;

                }


                QLabel#SettingsPageTitle {

                    color: #261C2D;

                    font-size: 30px;

                    font-weight: 800;

                }


                QLabel#SettingsPageSubtitle {

                    color: #75687E;

                    font-size: 13px;

                }


                QLabel#SettingsMenuSection {

                    color: #806D91;

                    font-size: 10px;

                    font-weight: 800;

                    letter-spacing: 1px;

                }


                QFrame#SettingsCategoryCard,
                QFrame#SettingsProfileCard,
                QFrame#SettingRow {

                    background: white;

                    border: 1px solid #DDD2E5;

                    border-radius: 15px;

                }


                QFrame#SettingsCategoryCard:hover {

                    background: #FCF9FE;

                    border: 1px solid #BDA4D3;

                }


                QLabel#SettingsCategoryIcon {

                    background: #F0E6FA;

                    color: #6D28D9;

                    border: 1px solid #D8C4EB;

                    border-radius: 12px;

                    font-size: 17px;

                    font-weight: 800;

                }


                QLabel#SettingsCategoryTitle {

                    color: #2B2131;

                    font-size: 14px;

                    font-weight: 800;

                }


                QLabel#SettingsCategorySubtitle {

                    color: #7F7287;

                    font-size: 11px;

                }


                QLabel#SettingsCategoryArrow {

                    color: #8F61C8;

                    font-size: 28px;

                }


                QLabel#SettingsProfileName,
                QLabel#SettingsProfileNameLarge {

                    color: #251B2B;

                    font-size: 18px;

                    font-weight: 800;

                }


                QLabel#SettingsProfileNameLarge {

                    font-size: 23px;

                }


                QLabel#SettingsProfileEmail {

                    color: #75677F;

                    font-size: 12px;

                }


                QLabel#SettingsProfileStatus {

                    color: #7C3AED;

                    font-size: 11px;

                    font-weight: 700;

                }


                QLabel#SettingRowTitle {

                    color: #2B2131;

                    font-size: 13px;

                    font-weight: 700;

                }


                QLabel#SettingRowDescription {

                    color: #7F7287;

                    font-size: 11px;

                }


                QLabel#SettingsValueLabel {

                    color: #655571;

                    font-size: 11px;

                    font-weight: 600;

                }


                QLabel#SettingsInfoText {

                    color: #776982;

                    font-size: 11px;

                    background: transparent;

                    padding: 4px 2px;

                }


                QPushButton#SettingsAvatar {

                    background: #EEE4F7;

                    color: #6D28D9;

                    border: 1px solid #D1BCE4;

                    border-radius: 34px;

                    font-size: 23px;

                    font-weight: 800;

                }


                QPushButton#SettingsAvatarLarge {

                    background: #EEE4F7;

                    color: #6D28D9;

                    border: 1px solid #D1BCE4;

                    border-radius: 45px;

                    font-size: 28px;

                    font-weight: 800;

                }


                QPushButton#SettingsProfileArrow {

                    background: #F7F2FA;

                    color: #6D28D9;

                    border: 1px solid #D7CDE0;

                    border-radius: 19px;

                    font-size: 24px;

                }


                QPushButton#SettingsBackButton {

                    background: transparent;

                    color: #6D28D9;

                    border: none;

                    padding: 4px 2px;

                    font-size: 12px;

                    font-weight: 700;

                    text-align: left;

                }


                QPushButton#SettingsPrimaryButton {

                    background: #7C3AED;

                    color: white;

                    border: none;

                    border-radius: 10px;

                    padding: 10px 16px;

                    font-weight: 700;

                }


                QPushButton#SettingsSecondaryButton {

                    background: #F6F1FA;

                    color: #4F3D59;

                    border: 1px solid #D7CBE0;

                    border-radius: 9px;

                    padding: 8px 13px;

                    font-weight: 600;

                }


                QLabel#SettingsSubHeading {
                    color: #2B2131;
                    font-size: 16px;
                    font-weight: 800;
                    padding-top: 10px;
                }

                QLineEdit#SettingsInput,
                QDateEdit#SettingsDateInput {
                    background: #F9F6FB;
                    color: #33273A;
                    border: 1px solid #D6CADE;
                    border-radius: 9px;
                    padding: 8px 10px;
                    min-height: 20px;
                }

                QLineEdit#SettingsInput:focus,
                QDateEdit#SettingsDateInput:focus {
                    border: 1px solid #7C3AED;
                }

                QPushButton#SettingsDangerButton {
                    background: #FFF7F8;
                    color: #B33D55;
                    border: 1px solid #EAC4CB;
                    border-radius: 9px;
                    padding: 8px 13px;
                    font-weight: 600;
                }

                QPushButton#SettingsDangerButton:hover {
                    background: #FDECEF;
                    color: #8F2E43;
                    border: 1px solid #D99AA8;
                }

                QComboBox {

                    background: #F9F6FB;

                    color: #33273A;

                    border: 1px solid #D6CADE;

                    border-radius: 9px;

                    padding: 7px 10px;

                    min-width: 135px;

                }


                QSlider::groove:horizontal {

                    height: 4px;

                    background: #D9CDE2;

                    border-radius: 2px;

                }


                QSlider::sub-page:horizontal {

                    background: #7C3AED;

                    border-radius: 2px;

                }


                QSlider::handle:horizontal {

                    background: #7C3AED;

                    width: 14px;

                    height: 14px;

                    margin: -5px 0;

                    border-radius: 7px;

                }


                QScrollBar:vertical {

                    background: transparent;

                    width: 8px;

                }


                QScrollBar::handle:vertical {

                    background: #C6B5D4;

                    min-height: 30px;

                    border-radius: 4px;

                }

                """
            )