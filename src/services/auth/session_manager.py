from PySide6.QtCore import QSettings

from .auth_models import AuthUser


class SessionManager:

    def __init__(self):
        self.settings = QSettings("LYRx", "LYRxDesktop")

    def save_user(self, user: AuthUser):
        self.settings.setValue("auth/uid", user.uid)
        self.settings.setValue("auth/email", user.email)
        self.settings.setValue("auth/display_name", user.display_name)
        self.settings.setValue("auth/photo_url", user.photo_url)
        self.settings.setValue("auth/phone_number", user.phone_number)
        self.settings.setValue("auth/id_token", user.id_token)
        self.settings.setValue("auth/refresh_token", user.refresh_token)
        self.settings.setValue("auth/expires_in", user.expires_in)
        self.settings.setValue("auth/email_verified", bool(user.email_verified))
        self.settings.setValue("auth/logged_in", True)
        self.settings.sync()

    def load_user(self):
        logged_in = self.settings.value("auth/logged_in", False, type=bool)

        if not logged_in:
            return None

        uid = str(self.settings.value("auth/uid", "") or "").strip()

        if not uid:
            return None

        return AuthUser(
            uid=uid,
            email=str(self.settings.value("auth/email", "") or ""),
            display_name=str(self.settings.value("auth/display_name", "") or ""),
            photo_url=str(self.settings.value("auth/photo_url", "") or ""),
            phone_number=str(self.settings.value("auth/phone_number", "") or ""),
            id_token=str(self.settings.value("auth/id_token", "") or ""),
            refresh_token=str(self.settings.value("auth/refresh_token", "") or ""),
            expires_in=int(self.settings.value("auth/expires_in", 3600) or 3600),
            email_verified=self.settings.value("auth/email_verified", False, type=bool),
        )

    def is_logged_in(self) -> bool:
        return self.load_user() is not None

    def clear(self):
        keys = (
            "auth/uid",
            "auth/email",
            "auth/display_name",
            "auth/photo_url",
            "auth/phone_number",
            "auth/id_token",
            "auth/refresh_token",
            "auth/expires_in",
            "auth/email_verified",
            "auth/logged_in",
        )

        for key in keys:
            self.settings.remove(key)

        self.settings.sync()
