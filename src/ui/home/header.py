from __future__ import annotations

from pathlib import Path
import requests

from services.auth.auth_service import AuthService

from PySide6.QtCore import (
    Qt,
    Signal,
    QSettings,
    QSize,
    QThread,
)

from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QPainterPath,
    QColor,
    QPen,
)

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QDialog,
    QFileDialog,
    QMessageBox,
    QStackedWidget,
    QCheckBox,
    QFrame,
    QComboBox,
    QScrollArea,
    QSizePolicy,
    QMenu,
)


# ============================================================
# LYRx
# DAY 24 - FIREBASE EMAIL + GOOGLE + REAL PHONE OTP AUTH
#
# PATH:
# src/ui/home/header.py
# ============================================================


# ============================================================
# LOCAL PROFILE STORE
# ============================================================

AVATAR_REMOVED_SENTINEL = "__LYRX_AVATAR_REMOVED__"


class LocalProfileStore:
    """
    UI/profile adapter for LYRx.

    Authentication is handled by Firebase through AuthService.
    Display name and local avatar path are stored per Firebase UID
    in QSettings so a user's chosen desktop profile photo survives
    sign-out and is restored after the same account signs in again.
    """

    def __init__(self):

        self.settings = QSettings(
            "LYRx",
            "LYRxDesktop"
        )

        self.auth = AuthService()

    # ========================================================
    # HELPERS
    # ========================================================

    def _current_user(self):

        return self.auth.current_user()

    def _uid(self) -> str:

        user = self._current_user()

        if not user:
            return ""

        return str(
            user.uid
            or ""
        ).strip()

    def _user_key(
        self,
        field: str
    ) -> str:

        uid = self._uid()

        if not uid:
            return ""

        return (
            f"profile/firebase_users/"
            f"{uid}/{field}"
        )

    def _ensure_user_profile(
        self,
        preferred_name: str = ""
    ):

        user = self._current_user()

        if not user:
            return

        uid = self._uid()

        if not uid:
            return

        name_key = self._user_key(
            "display_name"
        )

        avatar_key = self._user_key(
            "avatar_path"
        )

        current_name = str(
            self.settings.value(
                name_key,
                ""
            )
            or ""
        ).strip()

        if not current_name:

            # First authenticated migration:
            # use explicitly supplied name first, then Firebase/session
            # name, then the old local profile name if available.
            legacy_name = str(
                self.settings.value(
                    "profile/display_name",
                    ""
                )
                or ""
            ).strip()

            fallback_from_email = (
                str(user.email or "")
                .split("@")[0]
                .strip()
            )

            final_name = (
                str(preferred_name or "").strip()
                or str(user.display_name or "").strip()
                or legacy_name
                or fallback_from_email
                or "LYRx User"
            )

            self.settings.setValue(
                name_key,
                final_name
            )

        # Preserve the existing local DP once for the authenticated
        # Firebase account, if this account does not yet have one.
        current_avatar = str(
            self.settings.value(
                avatar_key,
                ""
            )
            or ""
        ).strip()

        if not current_avatar:

            legacy_avatar = str(
                self.settings.value(
                    "profile/avatar_path",
                    ""
                )
                or ""
            ).strip()

            if legacy_avatar:

                self.settings.setValue(
                    avatar_key,
                    legacy_avatar
                )

        self.settings.setValue(
            "profile/last_email",
            str(
                user.email
                or ""
            ).strip()
        )

        self.settings.sync()

    # ========================================================
    # NAME
    # ========================================================

    def display_name(self) -> str:

        if self.is_logged_in():

            self._ensure_user_profile()

            key = self._user_key(
                "display_name"
            )

            if key:

                name = str(
                    self.settings.value(
                        key,
                        ""
                    )
                    or ""
                ).strip()

                if name:
                    return name

            user = self._current_user()

            if user:

                firebase_name = str(
                    user.display_name
                    or ""
                ).strip()

                if firebase_name:
                    return firebase_name

                if user.email:

                    return (
                        str(user.email)
                        .split("@")[0]
                    )

        # Used only as a friendly create-account default while signed out.
        return str(
            self.settings.value(
                "profile/last_display_name",
                "Shubham"
            )
            or
            "Shubham"
        ).strip()

    def set_display_name(
        self,
        display_name: str
    ):

        if not self.is_logged_in():
            return

        display_name = str(
            display_name
            or ""
        ).strip()

        if not display_name:
            return

        key = self._user_key(
            "display_name"
        )

        if not key:
            return

        self.settings.setValue(
            key,
            display_name
        )

        self.settings.setValue(
            "profile/last_display_name",
            display_name
        )

        self.settings.sync()

        self.auth.update_local_profile(
            display_name=display_name,
            photo_url=None
        )

    # ========================================================
    # EMAIL
    # ========================================================

    def email(self) -> str:

        user = self._current_user()

        if (
            self.is_logged_in()
            and user
            and user.email
        ):

            return str(
                user.email
            ).strip()

        return str(
            self.settings.value(
                "profile/last_email",
                ""
            )
            or ""
        ).strip()

    # ========================================================
    # AVATAR
    # ========================================================

    def avatar_path(self) -> str:

        # Never expose a personal DP while signed out.
        if not self.is_logged_in():
            return ""

        self._ensure_user_profile()

        key = self._user_key(
            "avatar_path"
        )

        if not key:
            return ""

        value = str(
            self.settings.value(
                key,
                ""
            )
            or ""
        ).strip()

        if value == AVATAR_REMOVED_SENTINEL:
            return ""

        return value

    def set_avatar_path(
        self,
        avatar_path: str
    ):

        if not self.is_logged_in():
            return

        key = self._user_key(
            "avatar_path"
        )

        if not key:
            return

        avatar_path = str(
            avatar_path
            or ""
        ).strip()

        self.settings.setValue(
            key,
            avatar_path
        )

        removed_key = self._user_key(
            "avatar_removed"
        )

        if removed_key:
            self.settings.setValue(
                removed_key,
                False
            )

        self.settings.sync()

    def remove_avatar(self):

        if not self.is_logged_in():
            return

        key = self._user_key(
            "avatar_path"
        )

        if not key:
            return

        # Store an explicit sentinel instead of an empty value.
        # Empty used to trigger legacy-avatar migration again, which
        # made a removed photo instantly reappear.
        self.settings.setValue(
            key,
            AVATAR_REMOVED_SENTINEL
        )

        removed_key = self._user_key(
            "avatar_removed"
        )

        if removed_key:
            self.settings.setValue(
                removed_key,
                True
            )

        self.settings.sync()

    # ========================================================
    # AUTH STATE
    # ========================================================

    def is_logged_in(self) -> bool:

        return self.auth.is_logged_in()

    # ========================================================
    # REAL FIREBASE SIGN IN
    # ========================================================

    def authenticate(
        self,
        email: str,
        password: str
    ):

        result = self.auth.sign_in(
            email,
            password
        )

        if (
            result.success
            and result.user
        ):

            self._ensure_user_profile()

            self.settings.setValue(
                "profile/last_email",
                str(
                    result.user.email
                    or email
                ).strip()
            )

            self.settings.sync()

        return result

    # ========================================================
    # REAL FIREBASE CREATE ACCOUNT
    # ========================================================

    def create_account(
        self,
        display_name: str,
        email: str,
        password: str
    ):

        result = self.auth.create_account(
            email,
            password,
            display_name
        )

        # The Firebase account exists now, but LYRx intentionally
        # does not create an active app session until email verification.
        if result.user:

            self.settings.setValue(
                "profile/last_email",
                str(
                    result.user.email
                    or email
                ).strip()
            )

            self.settings.setValue(
                "profile/last_display_name",
                str(
                    display_name
                    or ""
                ).strip()
            )

            self.settings.sync()

        return result

    def resend_email_verification(
        self,
        user
    ):

        return self.auth.resend_email_verification(
            user
        )

    def check_email_verification(
        self,
        user,
        preferred_name: str = ""
    ):

        result = self.auth.check_email_verification(
            user
        )

        if (
            result.success
            and result.user
        ):

            self._ensure_user_profile(
                preferred_name=preferred_name
            )

            if preferred_name:

                self.set_display_name(
                    preferred_name
                )

            self.settings.setValue(
                "profile/last_email",
                str(
                    result.user.email
                    or ""
                ).strip()
            )

            self.settings.sync()

        return result

    # ========================================================
    # REAL GOOGLE + FIREBASE SIGN IN
    # ========================================================

    def sign_in_with_google(self):

        result = self.auth.sign_in_with_google()

        if (
            not result.success
            or
            not result.user
        ):

            return result

        self._ensure_user_profile(
            preferred_name=(
                result.user.display_name
                or ""
            )
        )

        if result.user.display_name:

            self.set_display_name(
                result.user.display_name
            )

        self.settings.setValue(
            "profile/last_email",
            str(
                result.user.email
                or ""
            ).strip()
        )

        if result.user.display_name:

            self.settings.setValue(
                "profile/last_display_name",
                str(
                    result.user.display_name
                ).strip()
            )

        self.settings.sync()

        # Download Google profile photo into LYRx local cache.
        # This keeps the existing avatar widget unchanged because
        # circular_avatar_icon() expects a local file path.
        if result.user.photo_url:

            self._cache_google_avatar(
                result.user.photo_url
            )

        return result

    def _cache_google_avatar(
        self,
        photo_url: str
    ):

        if not self.is_logged_in():
            return

        photo_url = str(
            photo_url
            or ""
        ).strip()

        if not photo_url:
            return

        uid = self._uid()

        if not uid:
            return

        try:

            cache_dir = (
                Path.home()
                / ".lyrx"
                / "profile_photos"
            )

            cache_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            target = (
                cache_dir
                / f"{uid}.jpg"
            )

            response = requests.get(
                photo_url,
                timeout=15
            )

            response.raise_for_status()

            content_type = str(
                response.headers.get(
                    "Content-Type",
                    ""
                )
            ).lower()

            if (
                "image" not in content_type
                and
                not response.content
            ):

                return

            target.write_bytes(
                response.content
            )

            self.set_avatar_path(
                str(target)
            )

        except Exception:

            # Google login must still succeed even if the optional
            # profile image cannot be downloaded.
            pass

    # ========================================================
    # REAL FIREBASE PASSWORD RESET
    # ========================================================

    def send_password_reset(
        self,
        email: str
    ):

        return self.auth.send_password_reset(
            email
        )

    # ========================================================
    # REAL FIREBASE PHONE OTP
    # ========================================================

    def request_phone_otp(
        self,
        phone_number: str
    ):

        return self.auth.request_phone_otp(
            phone_number
        )

    def verify_phone_otp(
        self,
        verification_id: str,
        otp: str,
        phone_number: str = ""
    ):

        result = self.auth.verify_phone_otp(
            verification_id,
            otp
        )

        if (
            result.success
            and
            result.user
        ):

            # Phone-only Firebase accounts do not have an email/name by
            # default, so give the desktop profile a clean fallback name.
            self._ensure_user_profile(
                preferred_name="LYRx User"
            )

            if phone_number:
                self.settings.setValue(
                    "profile/last_phone",
                    str(phone_number).strip()
                )
                self.settings.sync()

        return result

    # ========================================================
    # SIGN OUT
    # ========================================================

    def sign_out(self):

        self.auth.sign_out()


# ============================================================
# CIRCULAR AVATAR
# ============================================================

def circular_avatar_icon(
    path: str,
    size: int = 36
) -> QIcon:

    path = str(
        path
        or ""
    ).strip()

    if (
        not path
        or
        not Path(path).is_file()
    ):

        return QIcon()

    pixmap = QPixmap(
        path
    )

    if pixmap.isNull():

        return QIcon()

    source = pixmap.scaled(
        size,
        size,
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )

    output = QPixmap(
        size,
        size
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
        size
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
        size
    )

    painter.end()

    return QIcon(
        output
    )


# ============================================================
# PASSWORD FIELD
# ============================================================

class PasswordField(QWidget):

    return_pressed = Signal()

    def __init__(
        self,
        placeholder="Password",
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setFixedHeight(
            46
        )

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
            8
        )

        self.input = QLineEdit()

        self.input.setFixedHeight(
            44
        )

        self.input.setPlaceholderText(
            placeholder
        )

        self.input.setEchoMode(
            QLineEdit.Password
        )

        self.eye = QPushButton(
            "◉"
        )

        self.eye.setObjectName(
            "PasswordEye"
        )

        self.eye.setFixedSize(
            44,
            44
        )

        self.eye.setCursor(
            Qt.PointingHandCursor
        )

        self.eye.setToolTip(
            "Show / hide password"
        )

        self.eye.clicked.connect(
            self.toggle_password
        )

        self.input.returnPressed.connect(
            self.return_pressed.emit
        )

        root.addWidget(
            self.input,
            1
        )

        root.addWidget(
            self.eye
        )

    def toggle_password(self):

        if (
            self.input.echoMode()
            ==
            QLineEdit.Password
        ):

            self.input.setEchoMode(
                QLineEdit.Normal
            )

            self.eye.setText(
                "◎"
            )

        else:

            self.input.setEchoMode(
                QLineEdit.Password
            )

            self.eye.setText(
                "◉"
            )

    def text(self) -> str:

        return self.input.text()


# ============================================================
# PHONE OTP BROWSER WORKER
# ============================================================

class PhoneOtpRequestWorker(QThread):

    result_ready = Signal(object)

    def __init__(
        self,
        store: LocalProfileStore,
        phone_number: str,
        parent=None
    ):

        super().__init__(parent)
        self.store = store
        self.phone_number = phone_number

    def run(self):

        try:
            result = self.store.request_phone_otp(
                self.phone_number
            )
        except Exception as exc:
            from services.auth.phone_auth import PhoneVerificationResult

            result = PhoneVerificationResult(
                False,
                f"Phone verification failed: {exc}"
            )

        self.result_ready.emit(result)


# ============================================================
# ACCOUNT DIALOG
# ============================================================

class AccountDialog(QDialog):

    profile_changed = Signal()

    def __init__(
        self,
        store: LocalProfileStore,
        is_dark=True,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.store = store

        self.current_is_dark = bool(
            is_dark
        )

        self.otp_requested = False
        self.phone_verification_id = ""
        self.pending_phone_number = ""
        self.phone_worker = None

        # Pending Firebase email/password signup.
        # This stays in memory until the user verifies the email.
        self.pending_verification_user = None

        self.setWindowTitle(
            "LYRx Account"
        )

        self.setModal(
            True
        )

        self.resize(
            620,
            720
        )

        self.setMinimumSize(
            560,
            620
        )

        self.setMaximumWidth(
            660
        )

        self.build_ui()

        self.apply_theme()

        self.show_email_login()

    # ========================================================
    # BUILD
    # ========================================================

    def build_ui(self):

        outer = QVBoxLayout(
            self
        )

        outer.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # ====================================================
        # SCROLL
        # ====================================================

        self.scroll = QScrollArea()

        self.scroll.setObjectName(
            "AccountScroll"
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

        outer.addWidget(
            self.scroll
        )

        self.scroll_content = QWidget()

        self.scroll_content.setObjectName(
            "AccountScrollContent"
        )

        self.scroll.setWidget(
            self.scroll_content
        )

        root = QVBoxLayout(
            self.scroll_content
        )

        root.setContentsMargins(
            18,
            18,
            18,
            22
        )

        # ====================================================
        # PANEL
        # ====================================================

        self.panel = QFrame()

        self.panel.setObjectName(
            "AccountPanel"
        )

        self.panel.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        panel = QVBoxLayout(
            self.panel
        )

        panel.setContentsMargins(
            22,
            20,
            22,
            22
        )

        panel.setSpacing(
            14
        )

        # ====================================================
        # AVATAR
        # ====================================================

        avatar_row = QHBoxLayout()

        avatar_row.addStretch()

        self.avatar = QPushButton(
            "S"
        )

        self.avatar.setObjectName(
            "AccountAvatar"
        )

        self.avatar.setFixedSize(
            92,
            92
        )

        self.avatar.setCursor(
            Qt.PointingHandCursor
        )

        self.avatar.clicked.connect(
            self.choose_avatar
        )

        avatar_row.addWidget(
            self.avatar
        )

        avatar_row.addStretch()

        panel.addLayout(
            avatar_row
        )

        # ====================================================
        # PHOTO ACTIONS
        # ====================================================

        self.photo_actions_widget = QWidget()

        photo_actions = QHBoxLayout(
            self.photo_actions_widget
        )

        photo_actions.setContentsMargins(
            0,
            0,
            0,
            0
        )

        photo_actions.setSpacing(
            10
        )

        photo_actions.addStretch()

        self.change_photo_button = QPushButton(
            "Change Photo"
        )

        self.change_photo_button.setObjectName(
            "SmallActionButton"
        )

        self.change_photo_button.setCursor(
            Qt.PointingHandCursor
        )

        self.change_photo_button.clicked.connect(
            self.choose_avatar
        )

        self.remove_photo_button = QPushButton(
            "Remove Photo"
        )

        self.remove_photo_button.setObjectName(
            "SmallActionButton"
        )

        self.remove_photo_button.setCursor(
            Qt.PointingHandCursor
        )

        self.remove_photo_button.clicked.connect(
            self.remove_avatar
        )

        photo_actions.addWidget(
            self.change_photo_button
        )

        photo_actions.addWidget(
            self.remove_photo_button
        )

        photo_actions.addStretch()

        panel.addWidget(
            self.photo_actions_widget
        )

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel(
            "Welcome to LYRx"
        )

        title.setObjectName(
            "AccountTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        subtitle = QLabel(
            "Sign in to your LYRx account"
        )

        subtitle.setObjectName(
            "AccountSubtitle"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        panel.addWidget(
            title
        )

        panel.addWidget(
            subtitle
        )

        panel.addSpacing(
            4
        )

        # ====================================================
        # TABS
        # ====================================================

        tabs = QHBoxLayout()

        tabs.setSpacing(
            8
        )

        self.email_tab = QPushButton(
            "Email Login"
        )

        self.phone_tab = QPushButton(
            "Phone OTP"
        )

        self.create_tab = QPushButton(
            "Create Account"
        )

        for button in (
            self.email_tab,
            self.phone_tab,
            self.create_tab
        ):

            button.setObjectName(
                "AccountTab"
            )

            button.setFixedHeight(
                40
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            tabs.addWidget(
                button
            )

        self.email_tab.clicked.connect(
            self.show_email_login
        )

        self.phone_tab.clicked.connect(
            self.show_phone_login
        )

        self.create_tab.clicked.connect(
            self.show_create_account
        )

        panel.addLayout(
            tabs
        )

        # ====================================================
        # STACK
        # ====================================================

        self.stack = QStackedWidget()

        self.stack.setMinimumHeight(
            350
        )

        self.stack.addWidget(
            self.build_email_page()
        )

        self.stack.addWidget(
            self.build_phone_page()
        )

        self.stack.addWidget(
            self.build_create_page()
        )

        panel.addWidget(
            self.stack
        )

        panel.addSpacing(
            12
        )

        # ====================================================
        # DIVIDER
        # ====================================================

        divider = QHBoxLayout()

        divider.setSpacing(
            12
        )

        left_line = QFrame()

        left_line.setFrameShape(
            QFrame.HLine
        )

        right_line = QFrame()

        right_line.setFrameShape(
            QFrame.HLine
        )

        divider_text = QLabel(
            "or continue with"
        )

        divider_text.setObjectName(
            "DividerText"
        )

        divider.addWidget(
            left_line,
            1
        )

        divider.addWidget(
            divider_text
        )

        divider.addWidget(
            right_line,
            1
        )

        panel.addLayout(
            divider
        )

        # ====================================================
        # SOCIAL
        # ====================================================

        social = QHBoxLayout()

        social.setSpacing(
            12
        )

        self.google_button = QPushButton(
            "G  Continue with Google"
        )

        self.microsoft_button = QPushButton(
            "▦  Sign in with Microsoft"
        )

        for button in (
            self.google_button,
            self.microsoft_button
        ):

            button.setObjectName(
                "SocialButton"
            )

            button.setFixedHeight(
                46
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            social.addWidget(
                button
            )

        self.google_button.clicked.connect(
            self.google_oauth_info
        )

        self.microsoft_button.clicked.connect(
            self.microsoft_oauth_info
        )

        panel.addLayout(
            social
        )

        # ====================================================
        # SIGN OUT
        # ====================================================

        self.sign_out_button = QPushButton(
            "Sign Out"
        )

        self.sign_out_button.setObjectName(
            "FooterLink"
        )

        self.sign_out_button.setCursor(
            Qt.PointingHandCursor
        )

        self.sign_out_button.clicked.connect(
            self.sign_out
        )

        panel.addWidget(
            self.sign_out_button,
            alignment=Qt.AlignCenter
        )

        root.addWidget(
            self.panel
        )

        root.addStretch()

        self.refresh_account_state()

    # ========================================================
    # EMAIL PAGE
    # ========================================================

    def build_email_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            0,
            14,
            0,
            12
        )

        layout.setSpacing(
            13
        )

        self.email_login_input = QLineEdit(
            self.store.email()
        )

        self.email_login_input.setPlaceholderText(
            "Email address"
        )

        self.email_login_input.setFixedHeight(
            44
        )

        self.email_password = PasswordField(
            "Password"
        )

        option_row = QHBoxLayout()

        self.remember_me = QCheckBox(
            "Remember me"
        )

        self.forgot_button = QPushButton(
            "Forgot password?"
        )

        self.forgot_button.setObjectName(
            "TextLink"
        )

        self.forgot_button.clicked.connect(
            self.forgot_password
        )

        option_row.addWidget(
            self.remember_me
        )

        option_row.addStretch()

        option_row.addWidget(
            self.forgot_button
        )

        self.email_status = QLabel()

        self.email_status.setObjectName(
            "StatusLabel"
        )

        self.email_status.setWordWrap(
            True
        )

        self.email_status.setMinimumHeight(
            18
        )

        self.email_signin = QPushButton(
            "Sign In  →"
        )

        self.email_signin.setObjectName(
            "PrimaryButton"
        )

        self.email_signin.setFixedHeight(
            46
        )

        self.email_signin.clicked.connect(
            self.sign_in_email
        )

        self.email_password.return_pressed.connect(
            self.sign_in_email
        )

        layout.addWidget(
            self.email_login_input
        )

        layout.addWidget(
            self.email_password
        )

        layout.addLayout(
            option_row
        )

        layout.addWidget(
            self.email_status
        )

        layout.addSpacing(
            4
        )

        layout.addWidget(
            self.email_signin
        )

        layout.addStretch()

        return page

    # ========================================================
    # PHONE PAGE
    # ========================================================

    def build_phone_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            0,
            14,
            0,
            12
        )

        layout.setSpacing(
            12
        )

        title = QLabel(
            "Phone verification"
        )

        title.setObjectName(
            "SectionTitle"
        )

        info = QLabel(
            "Enter your mobile number. LYRx opens a secure browser "
            "window for Firebase reCAPTCHA before requesting the OTP."
        )

        info.setObjectName(
            "SectionInfo"
        )

        info.setWordWrap(
            True
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            info
        )

        phone_row = QHBoxLayout()

        phone_row.setSpacing(
            8
        )

        self.country_code = QComboBox()

        self.country_code.setObjectName(
            "CountryCode"
        )

        self.country_code.setFixedWidth(
            118
        )

        self.country_code.setFixedHeight(
            44
        )

        self.country_code.addItems(
            [
                "IN  +91",
                "US  +1",
                "CA  +1",
                "GB  +44",
                "AU  +61",
                "AE  +971",
                "SG  +65",
            ]
        )

        self.phone_input = QLineEdit()

        self.phone_input.setPlaceholderText(
            "98765 43210"
        )

        self.phone_input.setFixedHeight(
            44
        )

        self.phone_input.setMaxLength(
            15
        )

        phone_row.addWidget(
            self.country_code
        )

        phone_row.addWidget(
            self.phone_input,
            1
        )

        layout.addLayout(
            phone_row
        )

        self.send_otp_button = QPushButton(
            "Send OTP"
        )

        self.send_otp_button.setObjectName(
            "PrimaryButton"
        )

        self.send_otp_button.setFixedHeight(
            46
        )

        self.send_otp_button.clicked.connect(
            self.request_phone_otp
        )

        layout.addWidget(
            self.send_otp_button
        )

        # ====================================================
        # OTP HIDDEN INITIALLY
        # ====================================================

        self.otp_container = QWidget()

        otp_layout = QVBoxLayout(
            self.otp_container
        )

        otp_layout.setContentsMargins(
            0,
            6,
            0,
            0
        )

        otp_layout.setSpacing(
            10
        )

        otp_info = QLabel(
            "Enter the 6-digit OTP sent to your mobile number."
        )

        otp_info.setObjectName(
            "SectionInfo"
        )

        self.otp_input = QLineEdit()

        self.otp_input.setPlaceholderText(
            "6-digit OTP"
        )

        self.otp_input.setFixedHeight(
            44
        )

        self.otp_input.setMaxLength(
            6
        )

        self.verify_otp_button = QPushButton(
            "Verify OTP"
        )

        self.verify_otp_button.setObjectName(
            "SecondaryButton"
        )

        self.verify_otp_button.setFixedHeight(
            46
        )

        self.verify_otp_button.clicked.connect(
            self.verify_phone_otp
        )

        otp_layout.addWidget(
            otp_info
        )

        otp_layout.addWidget(
            self.otp_input
        )

        otp_layout.addWidget(
            self.verify_otp_button
        )

        self.otp_container.hide()

        layout.addWidget(
            self.otp_container
        )

        self.phone_status = QLabel()

        self.phone_status.setObjectName(
            "StatusLabel"
        )

        self.phone_status.setWordWrap(
            True
        )

        layout.addWidget(
            self.phone_status
        )

        layout.addStretch()

        return page

    # ========================================================
    # CREATE PAGE
    # ========================================================

    def build_create_page(self):

        page = QWidget()

        form = QFormLayout(
            page
        )

        form.setContentsMargins(
            0,
            14,
            0,
            12
        )

        form.setHorizontalSpacing(
            14
        )

        form.setVerticalSpacing(
            13
        )

        self.name_input = QLineEdit(
            self.store.display_name()
        )

        self.name_input.setFixedHeight(
            44
        )

        self.name_input.setPlaceholderText(
            "Display name"
        )

        self.create_email_input = QLineEdit(
            self.store.email()
        )

        self.create_email_input.setFixedHeight(
            44
        )

        self.create_email_input.setPlaceholderText(
            "Email address"
        )

        self.create_password = PasswordField(
            "Create password"
        )

        self.confirm_password = PasswordField(
            "Confirm password"
        )

        self.create_status = QLabel()

        self.create_status.setObjectName(
            "StatusLabel"
        )

        self.create_status.setWordWrap(
            True
        )

        self.create_status.setMinimumHeight(
            20
        )

        self.create_button = QPushButton(
            "Create / Save Account"
        )

        self.create_button.setObjectName(
            "PrimaryButton"
        )

        self.create_button.setFixedHeight(
            46
        )

        self.create_button.clicked.connect(
            self.save_account
        )

        # ----------------------------------------------------
        # EMAIL VERIFICATION CONTROLS
        # Hidden until Firebase successfully creates the account.
        # ----------------------------------------------------

        self.create_verification_widget = QWidget()

        verification_layout = QVBoxLayout(
            self.create_verification_widget
        )

        verification_layout.setContentsMargins(
            0,
            4,
            0,
            0
        )

        verification_layout.setSpacing(
            9
        )

        self.verification_info = QLabel(
            "Verification email sent. Open your inbox and click the Firebase verification link."
        )

        self.verification_info.setObjectName(
            "SectionInfo"
        )

        self.verification_info.setWordWrap(
            True
        )

        verification_buttons = QHBoxLayout()

        verification_buttons.setSpacing(
            10
        )

        self.check_verification_button = QPushButton(
            "I've Verified My Email"
        )

        self.check_verification_button.setObjectName(
            "SecondaryButton"
        )

        self.check_verification_button.setFixedHeight(
            44
        )

        self.check_verification_button.clicked.connect(
            self.check_create_verification
        )

        self.resend_verification_button = QPushButton(
            "Resend Email"
        )

        self.resend_verification_button.setObjectName(
            "SocialButton"
        )

        self.resend_verification_button.setFixedHeight(
            44
        )

        self.resend_verification_button.clicked.connect(
            self.resend_create_verification
        )

        verification_buttons.addWidget(
            self.check_verification_button,
            2
        )

        verification_buttons.addWidget(
            self.resend_verification_button,
            1
        )

        verification_layout.addWidget(
            self.verification_info
        )

        verification_layout.addLayout(
            verification_buttons
        )

        self.create_verification_widget.hide()

        form.addRow(
            "Name",
            self.name_input
        )

        form.addRow(
            "Email",
            self.create_email_input
        )

        form.addRow(
            "Password",
            self.create_password
        )

        form.addRow(
            "Confirm",
            self.confirm_password
        )

        form.addRow(
            self.create_status
        )

        form.addRow(
            self.create_button
        )

        form.addRow(
            self.create_verification_widget
        )

        return page

    # ========================================================
    # ACCOUNT STATE
    # ========================================================

    def refresh_account_state(self):

        logged_in = (
            self.store.is_logged_in()
        )

        # ----------------------------------------------------
        # Photo controls only when logged in.
        # ----------------------------------------------------

        self.photo_actions_widget.setVisible(
            logged_in
        )

        self.avatar.setEnabled(
            logged_in
        )

        self.sign_out_button.setVisible(
            logged_in
        )

        if logged_in:

            self.avatar.setToolTip(
                "Change profile photo"
            )

        else:

            self.avatar.setToolTip(
                "Sign in to manage your profile photo"
            )

        self.refresh_avatar()

    # ========================================================
    # AVATAR
    # ========================================================

    def refresh_avatar(self):

        name = (
            self.store.display_name()
            or
            "Shubham"
        )

        logged_in = (
            self.store.is_logged_in()
        )

        if not logged_in:

            self.avatar.setIcon(
                QIcon()
            )

            self.avatar.setText(
                name[:1].upper()
                if name
                else
                "S"
            )

            return

        avatar_path = (
            self.store.avatar_path()
        )

        icon = circular_avatar_icon(
            avatar_path,
            84
        )

        if icon.isNull():

            self.avatar.setIcon(
                QIcon()
            )

            self.avatar.setText(
                name[:1].upper()
                if name
                else
                "S"
            )

        else:

            self.avatar.setText(
                ""
            )

            self.avatar.setIcon(
                icon
            )

            self.avatar.setIconSize(
                QSize(
                    84,
                    84
                )
            )

    # ========================================================
    # CHANGE PHOTO
    # ========================================================

    def choose_avatar(self):

        if not self.store.is_logged_in():

            QMessageBox.information(
                self,
                "LYRx Profile",
                "Sign in first to change your profile photo."
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

        # ----------------------------------------------------
        # AUTO SAVE
        # ----------------------------------------------------

        self.store.set_avatar_path(
            path
        )

        self.refresh_avatar()

        self.profile_changed.emit()

    # ========================================================
    # REMOVE PHOTO
    # ========================================================

    def remove_avatar(self):

        if not self.store.is_logged_in():

            return

        self.store.remove_avatar()

        self.refresh_avatar()

        self.profile_changed.emit()

    # ========================================================
    # EMAIL LOGIN
    # ========================================================

    def sign_in_email(self):

        email = (
            self.email_login_input
            .text()
            .strip()
        )

        password = (
            self.email_password
            .text()
        )

        if not email:

            self.email_status.setText(
                "Enter your email address."
            )

            return

        if not password:

            self.email_status.setText(
                "Enter your password."
            )

            return

        self.email_status.setText(
            "Signing in securely with Firebase..."
        )

        self.email_signin.setEnabled(
            False
        )

        try:

            result = self.store.authenticate(
                email,
                password
            )

        except Exception as exc:

            self.email_status.setText(
                f"Authentication error: {exc}"
            )

            self.email_signin.setEnabled(
                True
            )

            return

        self.email_signin.setEnabled(
            True
        )

        if not result.success:

            self.email_status.setText(
                result.message
            )

            return

        self.email_password.input.clear()

        self.refresh_account_state()

        self.profile_changed.emit()

        self.accept()

    # ========================================================
    # CREATE / SAVE ACCOUNT
    # ========================================================

    def save_account(self):

        name = (
            self.name_input
            .text()
            .strip()
        )

        email = (
            self.create_email_input
            .text()
            .strip()
        )

        password = (
            self.create_password
            .text()
        )

        confirm = (
            self.confirm_password
            .text()
        )

        if not name:

            self.create_status.setText(
                "Enter your display name."
            )

            return

        if (
            not email
            or
            "@" not in email
            or
            "." not in email.split("@")[-1]
        ):

            self.create_status.setText(
                "Enter a valid email address."
            )

            return

        if len(password) < 6:

            self.create_status.setText(
                "Password must be at least 6 characters."
            )

            return

        if password != confirm:

            self.create_status.setText(
                "Passwords do not match."
            )

            return

        self.create_status.setText(
            "Creating your secure Firebase account..."
        )

        self.create_button.setEnabled(
            False
        )

        try:

            result = self.store.create_account(
                display_name=name,
                email=email,
                password=password
            )

        except Exception as exc:

            self.create_status.setText(
                f"Account creation error: {exc}"
            )

            self.create_button.setEnabled(
                True
            )

            return

        self.create_button.setEnabled(
            True
        )

        if not result.success:

            self.create_status.setText(
                result.message
            )

            return

        self.pending_verification_user = result.user

        self.create_password.input.clear()

        self.confirm_password.input.clear()

        self.create_button.setText(
            "Account Created ✓"
        )

        self.create_button.setEnabled(
            False
        )

        self.create_email_input.setEnabled(
            False
        )

        self.name_input.setEnabled(
            False
        )

        self.create_verification_widget.show()

        self.create_status.setText(
            "Account created. Verification email sent — check Inbox and Spam."
        )

    # ========================================================
    # EMAIL VERIFICATION - CREATE ACCOUNT
    # ========================================================

    def resend_create_verification(self):

        if not self.pending_verification_user:

            self.create_status.setText(
                "Create an account first."
            )

            return

        self.resend_verification_button.setEnabled(
            False
        )

        self.create_status.setText(
            "Resending verification email..."
        )

        try:

            result = self.store.resend_email_verification(
                self.pending_verification_user
            )

        except Exception as exc:

            self.resend_verification_button.setEnabled(
                True
            )

            self.create_status.setText(
                f"Verification email error: {exc}"
            )

            return

        self.resend_verification_button.setEnabled(
            True
        )

        self.create_status.setText(
            result.message
        )

        if result.success:

            QMessageBox.information(
                self,
                "LYRx Email Verification",
                (
                    "Verification email sent again.\n\n"
                    "Check your Inbox and Spam folder, open the Firebase email, "
                    "and click the verification link."
                )
            )

    def check_create_verification(self):

        if not self.pending_verification_user:

            self.create_status.setText(
                "Create an account first."
            )

            return

        self.check_verification_button.setEnabled(
            False
        )

        self.check_verification_button.setText(
            "Checking..."
        )

        self.create_status.setText(
            "Checking Firebase verification status..."
        )

        try:

            result = self.store.check_email_verification(
                self.pending_verification_user,
                preferred_name=(
                    self.name_input.text().strip()
                )
            )

        except Exception as exc:

            self.check_verification_button.setEnabled(
                True
            )

            self.check_verification_button.setText(
                "I've Verified My Email"
            )

            self.create_status.setText(
                f"Verification check error: {exc}"
            )

            return

        self.check_verification_button.setEnabled(
            True
        )

        self.check_verification_button.setText(
            "I've Verified My Email"
        )

        if not result.success:

            self.create_status.setText(
                result.message
            )

            return

        self.pending_verification_user = None

        self.create_status.setText(
            "Email verified. Your LYRx account is ready."
        )

        self.refresh_account_state()

        self.profile_changed.emit()

        QMessageBox.information(
            self,
            "Welcome to LYRx",
            "Email verified successfully. Your LYRx account is now active."
        )

        self.accept()

    # ========================================================
    # SIGN OUT
    # ========================================================

    def sign_out(self):

        # Firebase session is cleared locally.
        # The per-UID LYRx display name / avatar remains saved
        # and will be restored when the same account logs in again.

        self.store.sign_out()

        self.refresh_account_state()

        self.profile_changed.emit()

        self.accept()

    # ========================================================
    # OTP
    # ========================================================

    def request_phone_otp(self):

        phone = (
            self.phone_input
            .text()
            .strip()
        )

        digits = "".join(
            character
            for character in phone
            if character.isdigit()
        )

        if len(digits) < 7:

            self.phone_status.setText(
                "Enter a valid mobile number."
            )

            return

        code = (
            self.country_code
            .currentText()
            .split()[-1]
        )

        full_number = f"{code}{digits}"

        self.pending_phone_number = full_number
        self.phone_verification_id = ""
        self.otp_requested = False
        self.otp_container.hide()

        self.send_otp_button.setEnabled(False)
        self.send_otp_button.setText("Opening Firebase...")
        self.phone_status.setText(
            "Opening secure Firebase phone verification in your browser. "
            "Complete the reCAPTCHA there, then return to LYRx."
        )

        self.phone_worker = PhoneOtpRequestWorker(
            self.store,
            full_number,
            self
        )

        self.phone_worker.result_ready.connect(
            self._phone_otp_request_finished
        )

        self.phone_worker.finished.connect(
            self.phone_worker.deleteLater
        )

        self.phone_worker.start()

    def _phone_otp_request_finished(self, result):

        self.send_otp_button.setEnabled(True)
        self.send_otp_button.setText("Resend OTP")

        if not result.success:
            self.otp_requested = False
            self.phone_verification_id = ""
            self.otp_container.hide()
            self.phone_status.setText(result.message)
            return

        self.phone_verification_id = str(
            result.verification_id
            or ""
        ).strip()

        if not self.phone_verification_id:
            self.phone_status.setText(
                "Firebase did not return a phone verification session."
            )
            return

        self.otp_requested = True
        self.otp_container.show()
        self.stack.setMinimumHeight(420)

        self.phone_status.setText(
            f"Firebase accepted {self.pending_phone_number}. "
            "Enter the 6-digit OTP to finish sign-in."
        )

        self.otp_input.clear()
        self.otp_input.setFocus()

        self.scroll.ensureWidgetVisible(
            self.otp_container,
            0,
            30
        )

    def verify_phone_otp(self):

        otp = (
            self.otp_input
            .text()
            .strip()
        )

        if (
            not self.otp_requested
            or
            not self.phone_verification_id
            or
            len(otp) != 6
            or
            not otp.isdigit()
        ):

            self.phone_status.setText(
                "Enter a valid 6-digit OTP after requesting the code."
            )
            return

        self.verify_otp_button.setEnabled(False)
        self.verify_otp_button.setText("Verifying...")
        self.phone_status.setText(
            "Verifying OTP securely with Firebase..."
        )

        try:
            result = self.store.verify_phone_otp(
                self.phone_verification_id,
                otp,
                self.pending_phone_number
            )
        except Exception as exc:
            self.verify_otp_button.setEnabled(True)
            self.verify_otp_button.setText("Verify OTP")
            self.phone_status.setText(
                f"Phone verification error: {exc}"
            )
            return

        self.verify_otp_button.setEnabled(True)
        self.verify_otp_button.setText("Verify OTP")

        if not result.success:
            self.phone_status.setText(result.message)
            return

        self.phone_status.setText(
            "Phone verified. Signed in to LYRx successfully."
        )

        self.refresh_account_state()
        self.profile_changed.emit()

        QMessageBox.information(
            self,
            "LYRx Phone Verification",
            "Phone verification successful. Welcome to LYRx."
        )

        self.accept()

    # ========================================================
    # TABS
    # ========================================================

    def show_email_login(self):

        self.stack.setCurrentIndex(
            0
        )

        self.stack.setMinimumHeight(
            290
        )

        self.set_tab_states(
            0
        )

    def show_phone_login(self):

        self.stack.setCurrentIndex(
            1
        )

        self.stack.setMinimumHeight(
            420
            if self.otp_requested
            else
            310
        )

        self.set_tab_states(
            1
        )

    def show_create_account(self):

        self.stack.setCurrentIndex(
            2
        )

        self.stack.setMinimumHeight(
            330
        )

        self.set_tab_states(
            2
        )

    def set_tab_states(
        self,
        active_index
    ):

        buttons = (
            self.email_tab,
            self.phone_tab,
            self.create_tab
        )

        for index, button in enumerate(
            buttons
        ):

            button.setProperty(
                "active",
                index == active_index
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

    # ========================================================
    # INFO ACTIONS
    # ========================================================

    def forgot_password(self):

        email = (
            self.email_login_input
            .text()
            .strip()
        )

        if not email:

            QMessageBox.information(
                self,
                "LYRx Password Reset",
                "Enter your email address in the Email Login tab first."
            )

            self.email_login_input.setFocus()

            return

        self.email_status.setText(
            "Sending password reset email..."
        )

        self.forgot_button.setEnabled(
            False
        )

        try:

            result = self.store.send_password_reset(
                email
            )

        except Exception as exc:

            self.email_status.setText(
                f"Password reset error: {exc}"
            )

            self.forgot_button.setEnabled(
                True
            )

            return

        self.forgot_button.setEnabled(
            True
        )

        self.email_status.setText(
            result.message
        )

        if result.success:

            QMessageBox.information(
                self,
                "LYRx Password Reset",
                (
                    "Firebase password reset email sent.\n\n"
                    "Check your inbox and spam folder."
                )
            )

    def google_oauth_info(self):

        self.google_button.setEnabled(
            False
        )

        self.google_button.setText(
            "Opening Google..."
        )

        try:

            result = (
                self.store
                .sign_in_with_google()
            )

        except Exception as exc:

            self.google_button.setEnabled(
                True
            )

            self.google_button.setText(
                "G  Continue with Google"
            )

            QMessageBox.warning(
                self,
                "Google Sign-In",
                f"Google Sign-In failed:\n\n{exc}"
            )

            return

        self.google_button.setEnabled(
            True
        )

        self.google_button.setText(
            "G  Sign in with Google"
        )

        if not result.success:

            QMessageBox.warning(
                self,
                "Google Sign-In",
                result.message
            )

            return

        self.refresh_account_state()

        self.profile_changed.emit()

        QMessageBox.information(
            self,
            "Google Sign-In",
            (
                "Google Sign-In successful.\n\n"
                f"Welcome {self.store.display_name()}!"
            )
        )

        self.accept()

    def microsoft_oauth_info(self):

        QMessageBox.information(
            self,
            "Microsoft Sign-In",
            (
                "Microsoft Sign-In UI is ready.\n\n"
                "Official authentication requires "
                "Microsoft Entra / Azure registration."
            )
        )

    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(self):

        if self.current_is_dark:

            self.setStyleSheet(
                """
                QDialog {
                    background: #0F0B19;
                    color: white;
                }

                QScrollArea#AccountScroll,
                QWidget#AccountScrollContent {
                    background: #0F0B19;
                    border: none;
                }

                QScrollBar:vertical {
                    width: 9px;
                    background: transparent;
                    margin: 4px 2px;
                }

                QScrollBar::handle:vertical {
                    background: #6D3ED1;
                    border-radius: 4px;
                    min-height: 42px;
                }

                QScrollBar::handle:vertical:hover {
                    background: #8B5CF6;
                }

                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    height: 0px;
                }

                QScrollBar::add-page:vertical,
                QScrollBar::sub-page:vertical {
                    background: transparent;
                }

                QFrame#AccountPanel {
                    background: #151024;
                    border: 1px solid #342750;
                    border-radius: 20px;
                }

                QWidget {
                    background: transparent;
                }

                QLabel {
                    color: #D8D0E8;
                    background: transparent;
                }

                QLabel#AccountTitle {
                    color: white;
                    font-size: 21px;
                    font-weight: 800;
                }

                QLabel#AccountSubtitle {
                    color: #9488AA;
                    font-size: 13px;
                }

                QLabel#SectionTitle {
                    color: white;
                    font-size: 16px;
                    font-weight: 700;
                }

                QLabel#SectionInfo,
                QLabel#DividerText {
                    color: #9285A7;
                    font-size: 11px;
                }

                QLabel#StatusLabel {
                    color: #C5A8FF;
                    font-size: 11px;
                    font-weight: 600;
                }

                QLineEdit {
                    background: #211A35;
                    color: white;
                    border: 1px solid #3A2B58;
                    border-radius: 11px;
                    padding-left: 13px;
                    padding-right: 13px;
                    font-size: 12px;
                    selection-background-color: #7C3AED;
                }

                QLineEdit:focus {
                    border: 1px solid #8B5CF6;
                }

                QCheckBox {
                    color: #CFC6DE;
                    spacing: 7px;
                    font-size: 12px;
                }

                QComboBox#CountryCode {
                    background: #211A35;
                    color: white;
                    border: 1px solid #3A2B58;
                    border-radius: 11px;
                    padding-left: 10px;
                }

                QComboBox QAbstractItemView {
                    background: #211A35;
                    color: white;
                    selection-background-color: #7C3AED;
                }

                QPushButton#AccountAvatar {
                    background: #241A39;
                    color: white;
                    border: 2px solid #8B5CF6;
                    border-radius: 46px;
                    font-size: 26px;
                    font-weight: 800;
                }

                QPushButton#AccountAvatar:disabled {
                    color: #7C718C;
                    border: 2px solid #46365F;
                    background: #1C162A;
                }

                QPushButton#SmallActionButton {
                    background: transparent;
                    color: #B892FF;
                    border: 1px solid #41325D;
                    border-radius: 9px;
                    min-height: 28px;
                    padding-left: 12px;
                    padding-right: 12px;
                    font-size: 10px;
                    font-weight: 600;
                }

                QPushButton#SmallActionButton:hover {
                    background: #281D3D;
                    border: 1px solid #7C3AED;
                }

                QPushButton#AccountTab {
                    background: transparent;
                    color: #A89CB9;
                    border: none;
                    border-bottom: 2px solid transparent;
                    border-radius: 0px;
                    font-size: 12px;
                    font-weight: 600;
                }

                QPushButton#AccountTab[active="true"] {
                    color: #C7A8FF;
                    border-bottom: 2px solid #8B5CF6;
                    font-weight: 800;
                }

                QPushButton#PrimaryButton {
                    background: #7C3AED;
                    color: white;
                    border: 1px solid #9F67FF;
                    border-radius: 11px;
                    font-size: 12px;
                    font-weight: 800;
                }

                QPushButton#PrimaryButton:hover {
                    background: #8B5CF6;
                }

                QPushButton#SecondaryButton,
                QPushButton#SocialButton {
                    background: #1B152B;
                    color: #EEE8F7;
                    border: 1px solid #392B53;
                    border-radius: 11px;
                    font-size: 11px;
                    font-weight: 600;
                }

                QPushButton#SecondaryButton:hover,
                QPushButton#SocialButton:hover {
                    background: #281D3D;
                    border: 1px solid #7C3AED;
                }

                QPushButton#TextLink,
                QPushButton#FooterLink {
                    background: transparent;
                    color: #B892FF;
                    border: none;
                    font-size: 11px;
                    font-weight: 600;
                }

                QPushButton#PasswordEye {
                    background: #211A35;
                    color: #D5CCE3;
                    border: 1px solid #3A2B58;
                    border-radius: 11px;
                    font-size: 15px;
                    font-weight: 700;
                }

                QPushButton#PasswordEye:hover {
                    background: #30204F;
                    border: 1px solid #8B5CF6;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QDialog {
                    background: #F6F2F9;
                    color: #302744;
                }

                QScrollArea#AccountScroll,
                QWidget#AccountScrollContent {
                    background: #F6F2F9;
                    border: none;
                }

                QScrollBar:vertical {
                    width: 9px;
                    background: transparent;
                }

                QScrollBar::handle:vertical {
                    background: #9E7AC5;
                    border-radius: 4px;
                    min-height: 42px;
                }

                QFrame#AccountPanel {
                    background: white;
                    border: 1px solid #DCCFE6;
                    border-radius: 20px;
                }

                QWidget {
                    background: transparent;
                }

                QLabel {
                    color: #5C506B;
                    background: transparent;
                }

                QLabel#AccountTitle {
                    color: #302744;
                    font-size: 21px;
                    font-weight: 800;
                }

                QLabel#AccountSubtitle {
                    color: #7C6F8C;
                    font-size: 13px;
                }

                QLabel#SectionTitle {
                    color: #302744;
                    font-size: 16px;
                    font-weight: 700;
                }

                QLabel#SectionInfo,
                QLabel#DividerText {
                    color: #85778F;
                    font-size: 11px;
                }

                QLabel#StatusLabel {
                    color: #6D28D9;
                    font-size: 11px;
                    font-weight: 600;
                }

                QLineEdit {
                    background: #FBF9FD;
                    color: #302744;
                    border: 1px solid #D7CDE0;
                    border-radius: 11px;
                    padding-left: 13px;
                    padding-right: 13px;
                }

                QLineEdit:focus {
                    border: 1px solid #7C3AED;
                }

                QComboBox#CountryCode {
                    background: #FBF9FD;
                    color: #302744;
                    border: 1px solid #D7CDE0;
                    border-radius: 11px;
                    padding-left: 10px;
                }

                QPushButton#AccountAvatar {
                    background: #EFE7F6;
                    color: #4B3560;
                    border: 2px solid #8B5CF6;
                    border-radius: 46px;
                    font-size: 26px;
                    font-weight: 800;
                }

                QPushButton#SmallActionButton {
                    background: #F7F2FA;
                    color: #6D28D9;
                    border: 1px solid #D7CDE0;
                    border-radius: 9px;
                    min-height: 28px;
                    padding-left: 12px;
                    padding-right: 12px;
                    font-size: 10px;
                    font-weight: 600;
                }

                QPushButton#AccountTab {
                    background: transparent;
                    color: #756680;
                    border: none;
                    border-bottom: 2px solid transparent;
                    border-radius: 0px;
                    font-size: 12px;
                    font-weight: 600;
                }

                QPushButton#AccountTab[active="true"] {
                    color: #6D28D9;
                    border-bottom: 2px solid #7C3AED;
                    font-weight: 800;
                }

                QPushButton#PrimaryButton {
                    background: #7C3AED;
                    color: white;
                    border: 1px solid #8B5CF6;
                    border-radius: 11px;
                    font-weight: 800;
                }

                QPushButton#SecondaryButton,
                QPushButton#SocialButton {
                    background: #F8F4FB;
                    color: #4D3C59;
                    border: 1px solid #D9CDE2;
                    border-radius: 11px;
                    font-size: 11px;
                    font-weight: 600;
                }

                QPushButton#TextLink,
                QPushButton#FooterLink {
                    background: transparent;
                    color: #6D28D9;
                    border: none;
                    font-size: 11px;
                    font-weight: 600;
                }

                QPushButton#PasswordEye {
                    background: #FBF9FD;
                    color: #67557B;
                    border: 1px solid #D7CDE0;
                    border-radius: 11px;
                    font-size: 15px;
                    font-weight: 700;
                }
                """
            )


# ============================================================
# HEADER
# ============================================================

def glossy_bell_icon(is_dark=True):
    """Vector bell icon: crisp on Windows, no emoji/font clipping."""
    pix = QPixmap(30, 30)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    glow = QColor("#C4B5FD" if is_dark else "#7C3AED")
    pen = QPen(glow)
    pen.setWidthF(2.0)
    painter.setPen(pen)
    painter.setBrush(QColor("#8B5CF6"))

    # bell dome/body
    path = QPainterPath()
    path.moveTo(9, 20)
    path.lineTo(11, 17)
    path.lineTo(11, 12)
    path.cubicTo(11, 7, 19, 7, 19, 12)
    path.lineTo(19, 17)
    path.lineTo(21, 20)
    path.closeSubpath()
    painter.drawPath(path)

    # clapper + glossy highlight
    painter.drawEllipse(13, 21, 4, 3)
    painter.setPen(QPen(QColor(255, 255, 255, 185), 1.3))
    painter.drawArc(12, 9, 6, 7, 35 * 16, 105 * 16)
    painter.end()
    return QIcon(pix)


class Header(QWidget):

    search_changed = Signal(
        str
    )

    online_search_requested = Signal(
        str
    )

    profile_changed = Signal(
        str,
        str
    )

    notification_opened = Signal()

    def __init__(self):

        super().__init__()

        self.current_is_dark = True

        self.profile_store = (
            LocalProfileStore()
        )

        self.setFixedHeight(
            80
        )

        self.build_ui()

        self.refresh_profile()

        self.apply_theme()

    # =========================================================
    # BUILD
    # =========================================================

    def build_ui(self):

        root = QHBoxLayout(
            self
        )

        root.setContentsMargins(
            0,
            0,
            8,
            0
        )

        root.setSpacing(
            10
        )

        root.addStretch()

        # =====================================================
        # SEARCH
        # =====================================================

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search songs, artists or music online..."
        )

        self.search.setFixedWidth(
            340
        )

        self.search.setFixedHeight(
            42
        )

        self.search.setClearButtonEnabled(
            True
        )

        self.search.textChanged.connect(
            self.search_changed.emit
        )

        self.search.returnPressed.connect(
            self.request_online_search
        )

        root.addWidget(
            self.search
        )

        # =====================================================
        # AVATAR
        # =====================================================

        self.avatar_button = QPushButton(
            "👤"
        )

        self.avatar_button.setFixedSize(
            42,
            42
        )

        self.avatar_button.setCursor(
            Qt.PointingHandCursor
        )

        self.avatar_button.clicked.connect(
            self.open_account
        )

        root.addWidget(
            self.avatar_button
        )

        # =====================================================
        # PROFILE NAME
        # =====================================================

        self.profile = QPushButton(
            "•  Sign In"
        )

        self.profile.setFixedHeight(
            42
        )

        self.profile.setMinimumWidth(
            105
        )

        self.profile.setCursor(
            Qt.PointingHandCursor
        )

        self.profile.clicked.connect(
            self.open_account
        )

        root.addWidget(
            self.profile
        )

        # =====================================================
        # DAY 29.5 - NOTIFICATIONS
        # =====================================================

        self.notification_button = QPushButton()
        self.notification_button.setObjectName("NotificationButton")
        self.notification_button.setFixedSize(44, 44)
        self.notification_button.setIcon(glossy_bell_icon(True))
        self.notification_button.setIconSize(QSize(30, 30))
        self.notification_button.setCursor(Qt.PointingHandCursor)
        self.notification_button.setToolTip("Notifications")
        self.notification_button.clicked.connect(self.open_notifications)

        root.addWidget(self.notification_button)

        # =====================================================
        # WINDOW CONTROLS
        # =====================================================

        self.btn_minimize = QPushButton(
            "−"
        )

        self.btn_maximize = QPushButton(
            "□"
        )

        self.btn_close = QPushButton(
            "×"
        )

        for button in (
            self.btn_minimize,
            self.btn_maximize,
            self.btn_close
        ):

            button.setFixedSize(
                36,
                36
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            root.addWidget(
                button
            )

        self.btn_minimize.clicked.connect(
            lambda:
            self.window().showMinimized()
        )

        self.btn_maximize.clicked.connect(
            self.toggle_maximize
        )

        self.btn_close.clicked.connect(
            lambda:
            self.window().close()
        )

    # =========================================================
    # ACCOUNT
    # =========================================================

    def open_account(self):

        dialog = AccountDialog(
            self.profile_store,
            self.current_is_dark,
            self
        )

        dialog.profile_changed.connect(
            self.refresh_profile
        )

        dialog.exec()

        self.refresh_profile()

    # =========================================================
    # PROFILE
    # =========================================================

    def refresh_profile(self):

        logged_in = (
            self.profile_store
            .is_logged_in()
        )

        name = (
            self.profile_store
            .display_name()
            or
            "Shubham"
        )

        email = (
            self.profile_store
            .email()
        )

        # =====================================================
        # LOGGED IN
        # =====================================================

        if logged_in:

            self.profile.setText(
                f"•  {name}"
            )

            icon = circular_avatar_icon(
                self.profile_store.avatar_path(),
                36
            )

            if icon.isNull():

                self.avatar_button.setIcon(
                    QIcon()
                )

                self.avatar_button.setText(
                    name[:1].upper()
                )

            else:

                self.avatar_button.setText(
                    ""
                )

                self.avatar_button.setIcon(
                    icon
                )

                self.avatar_button.setIconSize(
                    QSize(
                        36,
                        36
                    )
                )

            tooltip = name

            if email:

                tooltip += (
                    f"\n{email}"
                )

            tooltip += (
                "\nSigned in"
            )

        # =====================================================
        # SIGNED OUT
        # =====================================================

        else:

            self.profile.setText(
                "•  Sign In"
            )

            self.avatar_button.setIcon(
                QIcon()
            )

            self.avatar_button.setText(
                "👤"
            )

            tooltip = (
                "LYRx Account\nSigned out"
            )

        self.profile.setToolTip(
            tooltip
        )

        self.avatar_button.setToolTip(
            tooltip
        )

        self.profile_changed.emit(
            name,
            email
        )

    # =========================================================
    # SEARCH
    # =========================================================

    def open_notifications(self):
        """Small real notification center anchored to the Home header."""
        menu = QMenu(self)
        menu.setObjectName("LYRxNotificationMenu")

        title = menu.addAction("Notifications")
        title.setEnabled(False)
        menu.addSeparator()

        notifications = self._notification_items()

        for text in notifications:
            action = menu.addAction(text)
            action.setEnabled(False)

        menu.addSeparator()

        clear_action = menu.addAction("✓  Mark all as read")
        selected = menu.exec(
            self.notification_button.mapToGlobal(
                self.notification_button.rect().bottomLeft()
            )
        )

        if selected == clear_action:
            self.profile_store.settings.setValue(
                "notifications/home_seen",
                True
            )
            self.profile_store.settings.sync()
            self.notification_button.setToolTip(
                "Notifications • All caught up"
            )

        self.notification_opened.emit()

    def _notification_items(self):
        seen = bool(
            self.profile_store.settings.value(
                "notifications/home_seen",
                False,
                type=bool,
            )
        )

        items = [
            "✨ LYRx AI is online and ready",
            "🎵 Local Music supports your own audio files",
            "🧒 Kids Mode is available from the sidebar",
        ]

        if not seen:
            self.notification_button.setToolTip(
                "Notifications • New updates"
            )

        return items

    def request_online_search(self):

        query = (
            self.search
            .text()
            .strip()
        )

        if not query:

            return

        self.online_search_requested.emit(
            query
        )

    def set_search_text(
        self,
        text
    ):

        self.search.setText(
            str(
                text
                or ""
            )
        )

    def clear_search(self):

        self.search.clear()

    def focus_search(self):

        self.search.setFocus(
            Qt.OtherFocusReason
        )

        self.search.selectAll()

    # =========================================================
    # THEME
    # =========================================================

    def set_theme_state(
        self,
        is_dark
    ):

        self.current_is_dark = bool(
            is_dark
        )

        self.apply_theme()

    def apply_theme(self):

        if self.current_is_dark:

            self.search.setStyleSheet(
                """
                QLineEdit {
                    background: #1D172F;
                    color: white;
                    border: 1px solid #312850;
                    border-radius: 21px;
                    padding-left: 18px;
                    padding-right: 18px;
                    font-size: 14px;
                    selection-background-color: #7C3AED;
                }

                QLineEdit:hover {
                    border: 1px solid #4A3970;
                    background: #211A35;
                }

                QLineEdit:focus {
                    border: 1px solid #7C3AED;
                    background: #211A35;
                }
                """
            )

            self.avatar_button.setStyleSheet(
                """
                QPushButton {
                    background: #211A35;
                    color: white;
                    border: 1px solid #3A2B58;
                    border-radius: 21px;
                    font-size: 14px;
                    font-weight: 800;
                    padding: 0px;
                }

                QPushButton:hover {
                    background: #30204F;
                    border: 1px solid #8B5CF6;
                }
                """
            )

            self.profile.setStyleSheet(
                """
                QPushButton {
                    background: #211A35;
                    color: white;
                    border: 1px solid #312850;
                    border-radius: 21px;
                    padding-left: 15px;
                    padding-right: 15px;
                    font-size: 14px;
                    font-weight: 600;
                }

                QPushButton:hover {
                    background: #30204F;
                    border: 1px solid #7C3AED;
                }
                """
            )

            window_style = """
                QPushButton {
                    background: #211A35;
                    color: #D8D2EA;
                    border: 1px solid #2C2445;
                    border-radius: 18px;
                    font-family: "Segoe UI Symbol";
                    font-size: 18px;
                    padding: 0px;
                }

                QPushButton:hover {
                    background: #30204F;
                    color: white;
                    border: 1px solid #7C3AED;
                }
            """

            close_style = """
                QPushButton {
                    background: #211A35;
                    color: #D8D2EA;
                    border: 1px solid #2C2445;
                    border-radius: 18px;
                    font-family: "Segoe UI Symbol";
                    font-size: 21px;
                    padding: 0px;
                }

                QPushButton:hover {
                    background: #BE123C;
                    color: white;
                    border: 1px solid #FB7185;
                }
            """

        else:

            self.search.setStyleSheet(
                """
                QLineEdit {
                    background: white;
                    color: #302744;
                    border: 1px solid #D8CEE2;
                    border-radius: 21px;
                    padding-left: 18px;
                    padding-right: 18px;
                    font-size: 14px;
                }

                QLineEdit:focus {
                    border: 1px solid #7C3AED;
                }
                """
            )

            self.avatar_button.setStyleSheet(
                """
                QPushButton {
                    background: white;
                    color: #4B3560;
                    border: 1px solid #D8CEE2;
                    border-radius: 21px;
                    font-size: 14px;
                    font-weight: 800;
                }

                QPushButton:hover {
                    background: #F3ECF8;
                    border: 1px solid #8B5CF6;
                }
                """
            )

            self.profile.setStyleSheet(
                """
                QPushButton {
                    background: white;
                    color: #3B2E4A;
                    border: 1px solid #D8CEE2;
                    border-radius: 21px;
                    padding-left: 15px;
                    padding-right: 15px;
                    font-size: 14px;
                    font-weight: 600;
                }

                QPushButton:hover {
                    background: #F3ECF8;
                    border: 1px solid #8B5CF6;
                }
                """
            )

            window_style = """
                QPushButton {
                    background: white;
                    color: #67567D;
                    border: 1px solid #D8CEE2;
                    border-radius: 18px;
                    font-family: "Segoe UI Symbol";
                    font-size: 18px;
                }

                QPushButton:hover {
                    background: #F3ECF8;
                    border: 1px solid #8B5CF6;
                }
            """

            close_style = """
                QPushButton {
                    background: white;
                    color: #67567D;
                    border: 1px solid #D8CEE2;
                    border-radius: 18px;
                    font-family: "Segoe UI Symbol";
                    font-size: 21px;
                }

                QPushButton:hover {
                    background: #BE123C;
                    color: white;
                    border: 1px solid #FB7185;
                }
            """

        self.notification_button.setIcon(
            glossy_bell_icon(self.current_is_dark)
        )
        if self.current_is_dark:
            self.notification_button.setStyleSheet("""
                QPushButton#NotificationButton {
                    border-radius: 22px;
                    border: 1px solid #4C3678;
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2B1B49, stop:0.55 #201531, stop:1 #171023
                    );
                }
                QPushButton#NotificationButton:hover {
                    border: 1px solid #A78BFA;
                    background: #342057;
                }
                QPushButton#NotificationButton:pressed {
                    background: #24153F;
                }
            """)
        else:
            self.notification_button.setStyleSheet("""
                QPushButton#NotificationButton {
                    border-radius: 22px;
                    border: 1px solid #D8C8F5;
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FFFFFF, stop:1 #F1E9FF
                    );
                }
                QPushButton#NotificationButton:hover {
                    border: 1px solid #8B5CF6;
                    background: #F4EEFF;
                }
            """)

        for button in (
            self.btn_minimize,
            self.btn_maximize
        ):

            button.setStyleSheet(
                window_style
            )

        self.btn_close.setStyleSheet(
            close_style
        )

    # =========================================================
    # MAXIMIZE
    # =========================================================

    def toggle_maximize(self):

        window = self.window()

        if window.isMaximized():

            window.showNormal()

            self.btn_maximize.setText(
                "□"
            )

        else:

            window.showMaximized()

            self.btn_maximize.setText(
                "❐"
            )