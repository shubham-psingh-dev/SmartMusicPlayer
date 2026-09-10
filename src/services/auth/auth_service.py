from __future__ import annotations

from typing import Optional

from .auth_models import AuthResult, AuthUser
from .firebase_auth import FirebaseAuthService
from .google_auth import GoogleAuthService
from .session_manager import SessionManager


class AuthService:

    def __init__(self):
        self.firebase = FirebaseAuthService()
        self.google = GoogleAuthService()
        self.session = SessionManager()

    # =========================================================
    # CREATE ACCOUNT + SEND VERIFICATION EMAIL
    # =========================================================

    def create_account(
        self,
        email: str,
        password: str,
        display_name: str = "",
    ) -> AuthResult:
        result = self.firebase.create_account(email, password)

        if not result.success or not result.user:
            return result

        result.user.display_name = str(display_name or "").strip()
        result.user.email_verified = False

        verify_result = self.firebase.send_email_verification(
            result.user.id_token
        )

        if not verify_result.success:
            return AuthResult(
                False,
                (
                    "Account was created, but the verification email could not be sent. "
                    + verify_result.message
                ),
                result.user,
            )

        # IMPORTANT:
        # Do not create an active LYRx session yet. The account becomes
        # active only after the user clicks the Firebase verification link.
        return AuthResult(
            True,
            "Account created. Verification email sent.",
            result.user,
        )

    # =========================================================
    # RESEND EMAIL VERIFICATION
    # =========================================================

    def resend_email_verification(self, user: AuthUser) -> AuthResult:
        if not user or not user.id_token:
            return AuthResult(False, "No pending verification session was found.")

        return self.firebase.send_email_verification(user.id_token)

    # =========================================================
    # CHECK VERIFICATION + ACTIVATE SESSION
    # =========================================================

    def check_email_verification(self, user: AuthUser) -> AuthResult:
        if not user or not user.id_token:
            return AuthResult(False, "No pending verification session was found.")

        result = self.firebase.lookup_account(user.id_token)

        if not result.success or not result.user:
            return result

        result.user.display_name = (
            user.display_name
            or result.user.display_name
        )
        result.user.refresh_token = user.refresh_token
        result.user.expires_in = user.expires_in

        if not result.user.email_verified:
            return AuthResult(
                False,
                "Email is not verified yet. Open the email from Firebase and click the verification link.",
                result.user,
            )

        self.session.save_user(result.user)

        return AuthResult(
            True,
            "Email verified successfully. Welcome to LYRx.",
            result.user,
        )

    # =========================================================
    # EMAIL SIGN IN
    # =========================================================

    def sign_in(self, email: str, password: str) -> AuthResult:
        result = self.firebase.sign_in(email, password)

        if not result.success or not result.user:
            return result

        if not result.user.email_verified:
            # Do not keep an unverified email/password account signed in.
            return AuthResult(
                False,
                "Your email is not verified yet. Verify it from your inbox, then sign in again.",
                result.user,
            )

        self.session.save_user(result.user)

        return AuthResult(
            True,
            "Signed in successfully.",
            result.user,
        )

    # =========================================================
    # GOOGLE SIGN IN
    # =========================================================

    def sign_in_with_google(self) -> AuthResult:
        google_result = self.google.sign_in()

        if not google_result.success:
            return AuthResult(False, google_result.message)

        firebase_result = self.firebase.sign_in_with_google_id_token(
            google_result.id_token
        )

        if not firebase_result.success or not firebase_result.user:
            return firebase_result

        # Google handles identity verification during OAuth.
        firebase_result.user.email_verified = True
        self.session.save_user(firebase_result.user)

        return AuthResult(
            True,
            "Google Sign-In successful.",
            firebase_result.user,
        )

    # =========================================================
    # PASSWORD RESET
    # =========================================================

    def send_password_reset(self, email: str) -> AuthResult:
        return self.firebase.send_password_reset(email)

    # =========================================================
    # CURRENT USER
    # =========================================================

    def current_user(self) -> Optional[AuthUser]:
        return self.session.load_user()

    def is_logged_in(self) -> bool:
        return self.session.is_logged_in()

    # =========================================================
    # UPDATE LOCAL SESSION PROFILE
    # =========================================================

    def update_local_profile(self, display_name=None, photo_url=None):
        user = self.session.load_user()

        if not user:
            return

        if display_name is not None:
            user.display_name = str(display_name or "").strip()

        if photo_url is not None:
            user.photo_url = str(photo_url or "").strip()

        self.session.save_user(user)

    # =========================================================
    # SIGN OUT
    # =========================================================

    def sign_out(self):
        self.session.clear()
