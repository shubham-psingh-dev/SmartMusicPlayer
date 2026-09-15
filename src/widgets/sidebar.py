from pathlib import Path

from core.language_manager import language_manager, tr

from PySide6.QtCore import (
    Qt,
    Signal,
    QSize,
    QVariantAnimation,
    QEasingCurve,
)

from PySide6.QtGui import (
    QPixmap,
    QIcon,
    QPainter,
    QColor,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QHBoxLayout,
    QCheckBox,
)


BASE_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# ASSETS
# ============================================================

SYMBOL_PATH = (
    BASE_DIR
    / "assets"
    / "icons"
    / "logo"
    / "LYRx_symbol.png"
)

WORDMARK_PATH = (
    BASE_DIR
    / "assets"
    / "icons"
    / "logo"
    / "LYRx_wordmark.png"
)

NAV_ICON_PATH = (
    BASE_DIR
    / "assets"
    / "icons"
    / "navigation"
)


# ============================================================
# SWIFT STYLE TOGGLE SWITCH
# ============================================================

class ToggleSwitch(QCheckBox):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(parent)

        # ----------------------------------------------------
        # SIZE
        # ----------------------------------------------------

        self.setFixedSize(
            46,
            24,
        )

        self.setCursor(
            Qt.PointingHandCursor,
        )

        self.setStyleSheet(
            """
            QCheckBox {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            """
        )

        # ----------------------------------------------------
        # ANIMATION
        # ----------------------------------------------------

        self._position = 25.0

        self.animation = QVariantAnimation(
            self,
        )

        self.animation.setDuration(
            180,
        )

        self.animation.setEasingCurve(
            QEasingCurve.OutCubic,
        )

        self.animation.valueChanged.connect(
            self._animation_value_changed,
        )

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.stateChanged.connect(
            self._state_changed,
        )

    # ========================================================
    # STATE CHANGED
    # ========================================================

    def _state_changed(
        self,
        state,
    ):

        checked = (
            state == Qt.Checked
        )

        start_position = self._position

        end_position = (
            25.0
            if checked
            else 3.0
        )

        self.animation.stop()

        self.animation.setStartValue(
            start_position,
        )

        self.animation.setEndValue(
            end_position,
        )

        self.animation.start()

        self.update()

    # ========================================================
    # ANIMATION
    # ========================================================

    def _animation_value_changed(
        self,
        value,
    ):

        self._position = float(
            value,
        )

        self.update()

    # ========================================================
    # SET CHECKED
    # ========================================================

    def setChecked(
        self,
        checked,
    ):

        super().setChecked(
            checked,
        )

        if self.signalsBlocked():

            self._position = (
                25.0
                if checked
                else 3.0
            )

            self.update()

    # ========================================================
    # MOUSE
    # ========================================================

    def mousePressEvent(
        self,
        event,
    ):

        if event.button() == Qt.LeftButton:

            self.setChecked(
                not self.isChecked(),
            )

            event.accept()

            return

        super().mousePressEvent(
            event,
        )

    # ========================================================
    # PAINT
    # ========================================================

    def paintEvent(
        self,
        event,
    ):

        painter = QPainter(
            self,
        )

        painter.setRenderHint(
            QPainter.Antialiasing,
        )

        # ----------------------------------------------------
        # TRACK
        # ----------------------------------------------------

        if self.isChecked():

            track_color = QColor(
                "#7C3AED",
            )

            track_border = QColor(
                "#A06BFF",
            )

        else:

            track_color = QColor(
                "#302A3F",
            )

            track_border = QColor(
                "#514765",
            )

        painter.setBrush(
            track_color,
        )

        painter.setPen(
            track_border,
        )

        painter.drawRoundedRect(
            1,
            1,
            44,
            22,
            11,
            11,
        )

        # ----------------------------------------------------
        # KNOB SHADOW
        # ----------------------------------------------------

        painter.setBrush(
            QColor(
                0,
                0,
                0,
                65,
            )
        )

        painter.setPen(
            Qt.NoPen,
        )

        painter.drawEllipse(
            int(self._position + 1),
            4,
            17,
            17,
        )

        # ----------------------------------------------------
        # KNOB
        # ----------------------------------------------------

        painter.setBrush(
            QColor("#FFFFFF"),
        )

        painter.drawEllipse(
            int(self._position),
            3,
            18,
            18,
        )

        # ----------------------------------------------------
        # HIGHLIGHT
        # ----------------------------------------------------

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                45,
            )
        )

        painter.drawEllipse(
            int(self._position + 3),
            6,
            6,
            6,
        )

        painter.end()


# ============================================================
# NAV BUTTON
# ============================================================

class NavButton(QPushButton):

    clicked_name = Signal(str)

    def __init__(
        self,
        text: str,
        icon_name: str,
    ):

        super().__init__(
            text,
        )

        # page_name remains the canonical English route key.
        # Visible text may change language without breaking navigation.
        self.page_name = text

        # ----------------------------------------------------
        # ICON
        # ----------------------------------------------------

        icon_file = (
            NAV_ICON_PATH
            / icon_name
        )

        if icon_file.exists():

            self.setIcon(
                QIcon(
                    str(icon_file),
                )
            )

            self.setIconSize(
                QSize(
                    20,
                    20,
                )
            )

        # ----------------------------------------------------
        # BASIC
        # ----------------------------------------------------

        self.setCursor(
            Qt.PointingHandCursor,
        )

        self.setCheckable(
            True,
        )

        self.setMinimumHeight(
            46,
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.clicked.connect(
            self._emit_page,
        )

        self.set_theme_style(
            True,
        )

    # ========================================================
    # PAGE SIGNAL
    # ========================================================

    def _emit_page(
        self,
    ):

        self.clicked_name.emit(
            self.page_name,
        )

    # ========================================================
    # THEME
    # ========================================================

    def set_theme_style(
        self,
        is_dark,
    ):

        if is_dark:

            self.setStyleSheet(
                """
                QPushButton {

                    color: #CFC8E5;

                    background: transparent;

                    border: none;

                    border-radius: 13px;

                    text-align: left;

                    padding-left: 16px;

                    padding-right: 14px;

                    font-size: 15px;

                    font-weight: 600;

                }

                QPushButton:hover {

                    background: rgba(
                        139,
                        92,
                        246,
                        30
                    );

                    color: #FFFFFF;

                }

                QPushButton:checked {

                    background: #7C3AED;

                    color: #FFFFFF;

                }

                QPushButton:pressed {

                    background: #6D28D9;

                    color: #FFFFFF;

                }

                """
            )

        else:

            self.setStyleSheet(
                """
                QPushButton {

                    color: #4A3D60;

                    background: transparent;

                    border: none;

                    border-radius: 13px;

                    text-align: left;

                    padding-left: 16px;

                    padding-right: 14px;

                    font-size: 15px;

                    font-weight: 600;

                }

                QPushButton:hover {

                    background: rgba(
                        124,
                        58,
                        237,
                        18
                    );

                    color: #382650;

                }

                QPushButton:checked {

                    background: #7C3AED;

                    color: #FFFFFF;

                }

                QPushButton:pressed {

                    background: #6D28D9;

                    color: #FFFFFF;

                }

                """
            )


# ============================================================
# SIDEBAR
# ============================================================

class Sidebar(QWidget):

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    page_changed = Signal(str)

    # Existing architecture — KEEP
    theme_toggle_requested = Signal()

    # New clean theme signal
    theme_changed = Signal(bool)

    def __init__(
        self,
        initial_dark=True,
    ):

        super().__init__()

        # ----------------------------------------------------
        # SIZE
        # ----------------------------------------------------

        self.setFixedWidth(
            240,
        )

        self.setObjectName(
            "LYRxSidebar",
        )

        self.setAttribute(
            Qt.WA_StyledBackground,
            True,
        )

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.buttons = []

        self.current_is_dark = (
            bool(initial_dark)
        )

        # ----------------------------------------------------
        # BUILD
        # ----------------------------------------------------

        self.build_ui()

        language_manager.language_changed.connect(
            self.retranslate_ui
        )
        self.retranslate_ui()

        self.update_theme_ui(
            self.current_is_dark,
        )

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        layout.setSpacing(
            10,
        )

        # ====================================================
        # BRANDING
        # ====================================================

        self.symbol = QLabel()

        self.symbol.setAlignment(
            Qt.AlignCenter,
        )

        if SYMBOL_PATH.exists():

            pix = QPixmap(
                str(SYMBOL_PATH),
            )

            if not pix.isNull():

                self.symbol.setPixmap(
                    pix.scaled(
                        88,
                        88,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )

        self.symbol.setStyleSheet(
            """
            QLabel {
                background: transparent;
            }
            """
        )

        layout.addWidget(
            self.symbol,
        )

        layout.addSpacing(
            0,
        )

        # ====================================================
        # WORDMARK
        # ====================================================

        self.wordmark = QLabel()

        self.wordmark.setAlignment(
            Qt.AlignCenter,
        )

        if WORDMARK_PATH.exists():

            pix = QPixmap(
                str(WORDMARK_PATH),
            )

            if not pix.isNull():

                self.wordmark.setPixmap(
                    pix.scaled(
                        142,
                        40,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )

        self.wordmark.setStyleSheet(
            """
            QLabel {
                background: transparent;
            }
            """
        )

        layout.addWidget(
            self.wordmark,
        )

        layout.addSpacing(
            0,
        )

        # ====================================================
        # SUBTITLE
        # ====================================================

        self.subtitle = QLabel(
            "Lose Yourself in Sound",
        )

        self.subtitle.setAlignment(
            Qt.AlignCenter,
        )

        layout.addWidget(
            self.subtitle,
        )

        layout.addSpacing(
            16,
        )

        # ====================================================
        # MENU LABEL
        # ====================================================

        self.menu_label = QLabel(
            "MENU",
        )

        layout.addWidget(
            self.menu_label,
        )

        layout.addSpacing(
            4,
        )

        # ====================================================
        # NAVIGATION
        # ====================================================
        #
        # DAY 21:
        #
        # YT BOX added between AI Assistant and Settings.
        #
        # Existing page_changed architecture remains untouched.
        #
        # If youtube.svg does not exist yet, NavButton simply
        # renders without an icon. Navigation still works.
        # ====================================================

        menu = [

            (
                "Home",
                "home.svg",
            ),

            (
                "Discover",
                "discover.svg",
            ),

            (
                "Library",
                "library.svg",
            ),

            (
                "Favorites",
                "favorites.svg",
            ),

            (
                "Playlists",
                "playlist.svg",
            ),

            (
                "AI Assistant",
                "sparkles.svg",
            ),

            # =================================================
            # DAY 21 - YT BOX
            # =================================================

            (
                "YT BOX",
                "youtube.svg",
            ),

            (
                "Settings",
                "settings.svg",
            ),

        ]

        # ====================================================
        # CREATE NAV BUTTONS
        # ====================================================

        for text, icon in menu:

            button = NavButton(
                text,
                icon,
            )

            button.clicked_name.connect(
                self.change_page,
            )

            layout.addWidget(
                button,
            )

            self.buttons.append(
                button,
            )

        # ----------------------------------------------------
        # DEFAULT HOME
        # ----------------------------------------------------

        if self.buttons:

            self.buttons[0].setChecked(
                True,
            )

        # ====================================================
        # FLEXIBLE SPACE
        # ====================================================

        layout.addStretch()

        # ====================================================
        # APPEARANCE LABEL
        # ====================================================

        self.appearance_title = QLabel(
            "APPEARANCE",
        )

        layout.addWidget(
            self.appearance_title,
        )

        # ====================================================
        # THEME ROW
        # ====================================================

        self.theme_row = QWidget()

        self.theme_row.setObjectName(
            "ThemeRow",
        )

        theme_layout = QHBoxLayout(
            self.theme_row,
        )

        theme_layout.setContentsMargins(
            12,
            8,
            10,
            8,
        )

        theme_layout.setSpacing(
            8,
        )

        # ====================================================
        # THEME ICON
        # ====================================================

        self.theme_icon = QLabel(
            "☾",
        )

        self.theme_icon.setFixedWidth(
            22,
        )

        self.theme_icon.setAlignment(
            Qt.AlignCenter,
        )

        theme_layout.addWidget(
            self.theme_icon,
        )

        # ====================================================
        # THEME TEXT
        # ====================================================

        theme_text = QVBoxLayout()

        theme_text.setSpacing(
            1,
        )

        self.theme_title = QLabel(
            "Dark Mode",
        )

        self.theme_status = QLabel(
            "On",
        )

        theme_text.addWidget(
            self.theme_title,
        )

        theme_text.addWidget(
            self.theme_status,
        )

        theme_layout.addLayout(
            theme_text,
            1,
        )

        # ====================================================
        # TOGGLE
        # ====================================================

        self.theme_toggle = ToggleSwitch()

        self.theme_toggle.setChecked(
            True,
        )

        theme_layout.addWidget(
            self.theme_toggle,
        )

        self.theme_toggle.stateChanged.connect(
            self.on_theme_toggle,
        )

        layout.addWidget(
            self.theme_row,
        )

        # ====================================================
        # FOOTER
        # ====================================================

        self.version_label = QLabel(
            "LYRx v0.1",
        )

        self.version_label.setAlignment(
            Qt.AlignCenter,
        )

        layout.addWidget(
            self.version_label,
        )

    # ========================================================
    # DARK STYLE
    # ========================================================

    def apply_dark_style(self):

        self.setStyleSheet(
            """
            QWidget#LYRxSidebar {

                background: #171126;

                border: none;

            }

            QWidget#ThemeRow {

                background: rgba(
                    139,
                    92,
                    246,
                    16
                );

                border: 1px solid rgba(
                    139,
                    92,
                    246,
                    30
                );

                border-radius: 13px;

            }

            QWidget#ThemeRow:hover {

                background: rgba(
                    139,
                    92,
                    246,
                    25
                );

                border: 1px solid rgba(
                    167,
                    139,
                    250,
                    65
                );

            }

            """
        )

    # ========================================================
    # LIGHT STYLE
    # ========================================================

    def apply_light_style(self):

        self.setStyleSheet(
            """
            QWidget#LYRxSidebar {

                background: #E8E0F2;

                border: none;

            }

            QWidget#ThemeRow {

                background: rgba(
                    255,
                    255,
                    255,
                    85
                );

                border: 1px solid rgba(
                    124,
                    58,
                    237,
                    30
                );

                border-radius: 13px;

            }

            QWidget#ThemeRow:hover {

                background: rgba(
                    255,
                    255,
                    255,
                    125
                );

                border: 1px solid rgba(
                    124,
                    58,
                    237,
                    55
                );

            }

            """
        )

    # ========================================================
    # THEME TOGGLE
    # ========================================================

    def on_theme_toggle(
        self,
        state,
    ):

        is_dark = (
            state == Qt.Checked
        )

        self.current_is_dark = (
            is_dark
        )

        # Update sidebar immediately
        self.update_theme_ui(
            is_dark,
        )

        # Existing signal
        self.theme_toggle_requested.emit()

        # New proper signal
        self.theme_changed.emit(
            is_dark,
        )

    # ========================================================
    # UPDATE THEME UI
    # ========================================================

    def update_theme_ui(
        self,
        is_dark,
    ):

        self.current_is_dark = (
            bool(is_dark)
        )

        # ====================================================
        # DARK MODE
        # ====================================================

        if is_dark:

            self.theme_title.setText(
                tr("theme.dark"),
            )

            self.theme_status.setText(
                tr("theme.on"),
            )

            self.theme_icon.setText(
                "☾",
            )

            self.apply_dark_style()

            # ------------------------------------------------
            # SUBTITLE
            # ------------------------------------------------

            self.subtitle.setStyleSheet(
                """
                QLabel {
                    color: #A79FD2;
                    font-size: 11px;
                    font-weight: 500;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # MENU LABEL
            # ------------------------------------------------

            self.menu_label.setStyleSheet(
                """
                QLabel {
                    color: #746B91;
                    font-size: 10px;
                    font-weight: 700;
                    letter-spacing: 1.2px;
                    padding-left: 8px;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # APPEARANCE
            # ------------------------------------------------

            self.appearance_title.setStyleSheet(
                """
                QLabel {
                    color: #746B91;
                    font-size: 10px;
                    font-weight: 700;
                    letter-spacing: 1.2px;
                    padding-left: 8px;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # THEME ICON
            # ------------------------------------------------

            self.theme_icon.setStyleSheet(
                """
                QLabel {
                    color: #C0A8F4;
                    font-size: 17px;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            self.theme_title.setStyleSheet(
                """
                QLabel {
                    color: #E7DFF6;
                    font-size: 12px;
                    font-weight: 600;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            self.theme_status.setStyleSheet(
                """
                QLabel {
                    color: #857A9F;
                    font-size: 10px;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # FOOTER
            # ------------------------------------------------

            self.version_label.setStyleSheet(
                """
                QLabel {
                    color: #655D7D;
                    font-size: 10px;
                    padding-top: 10px;
                    background: transparent;
                }
                """
            )

        # ====================================================
        # LIGHT MODE
        # ====================================================

        else:

            self.theme_title.setText(
                tr("theme.light"),
            )

            self.theme_status.setText(
                tr("theme.on"),
            )

            self.theme_icon.setText(
                "☀",
            )

            self.apply_light_style()

            # ------------------------------------------------
            # SUBTITLE
            # ------------------------------------------------

            self.subtitle.setStyleSheet(
                """
                QLabel {
                    color: #756481;
                    font-size: 11px;
                    font-weight: 500;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # MENU LABEL
            # ------------------------------------------------

            self.menu_label.setStyleSheet(
                """
                QLabel {
                    color: #877692;
                    font-size: 10px;
                    font-weight: 700;
                    letter-spacing: 1.2px;
                    padding-left: 8px;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # APPEARANCE
            # ------------------------------------------------

            self.appearance_title.setStyleSheet(
                """
                QLabel {
                    color: #877692;
                    font-size: 10px;
                    font-weight: 700;
                    letter-spacing: 1.2px;
                    padding-left: 8px;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # THEME ICON
            # ------------------------------------------------

            self.theme_icon.setStyleSheet(
                """
                QLabel {
                    color: #8054B8;
                    font-size: 17px;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            self.theme_title.setStyleSheet(
                """
                QLabel {
                    color: #433457;
                    font-size: 12px;
                    font-weight: 600;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            self.theme_status.setStyleSheet(
                """
                QLabel {
                    color: #88799B;
                    font-size: 10px;
                    background: transparent;
                }
                """
            )

            # ------------------------------------------------
            # FOOTER
            # ------------------------------------------------

            self.version_label.setStyleSheet(
                """
                QLabel {
                    color: #8E7BA3;
                    font-size: 10px;
                    padding-top: 10px;
                    background: transparent;
                }
                """
            )

        # ====================================================
        # NAV BUTTONS
        # ====================================================

        for button in self.buttons:

            button.set_theme_style(
                is_dark,
            )

        # Force repaint
        self.update()

    # ========================================================
    # EXTERNAL THEME CONTROL
    # ========================================================

    def set_theme_state(
        self,
        is_dark,
    ):

        self.theme_toggle.blockSignals(
            True,
        )

        self.theme_toggle.setChecked(
            is_dark,
        )

        self.theme_toggle.blockSignals(
            False,
        )

        self.theme_toggle._position = (
            25.0
            if is_dark
            else 3.0
        )

        self.update_theme_ui(
            is_dark,
        )

    # ========================================================
    # ALIAS
    # ========================================================

    def set_theme(
        self,
        is_dark,
    ):

        self.set_theme_state(
            is_dark,
        )

    # ========================================================
    # DAY 27 - LIVE LANGUAGE
    # ========================================================

    def retranslate_ui(self, *_):
        self.subtitle.setText(tr("sidebar.tagline"))
        self.menu_label.setText(tr("sidebar.menu"))
        self.appearance_title.setText(tr("sidebar.appearance"))

        keys = {
            "Home": "nav.home",
            "Discover": "nav.discover",
            "Library": "nav.library",
            "Favorites": "nav.favorites",
            "Playlists": "nav.playlists",
            "AI Assistant": "nav.assistant",
            "YT BOX": "nav.ytbox",
            "Settings": "nav.settings",
        }
        for button in self.buttons:
            button.setText(tr(keys.get(button.page_name, button.page_name)))

        # Theme wording is normally refreshed by update_theme_ui; calling it
        # here keeps the visible label in sync immediately after language change.
        self.update_theme_ui(self.current_is_dark)

    # ========================================================
    # NAVIGATION
    # ========================================================

    def change_page(
        self,
        page_name: str,
    ):

        sender = self.sender()

        for button in self.buttons:

            if button != sender:

                button.setChecked(
                    False,
                )

        # ----------------------------------------------------
        # Ensure clicked button remains selected.
        # ----------------------------------------------------

        if isinstance(
            sender,
            NavButton,
        ):

            sender.setChecked(
                True,
            )

        # ----------------------------------------------------
        # Existing generic navigation signal.
        #
        # YT BOX will emit exactly:
        #
        #       "YT BOX"
        #
        # AppWindow will route it in File 4.
        # ----------------------------------------------------

        self.page_changed.emit(
            page_name,
        )

        print(
            f"Navigate to: {page_name}"
        )