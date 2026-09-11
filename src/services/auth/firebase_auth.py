from __future__ import annotations

import os
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from .auth_models import AuthResult, AuthUser


load_dotenv()


class FirebaseAuthService:

    def __init__(self):
        self.api_key = os.getenv("FIREBASE_API_KEY", "").strip()

        if not self.api_key:
            raise RuntimeError("FIREBASE_API_KEY is missing from .env")

        self.base_url = "https://identitytoolkit.googleapis.com/v1"
        self.timeout = 20

    # =========================================================
    # CREATE ACCOUNT
    # =========================================================

    def create_account(self, email: str, password: str) -> AuthResult:
        return self._auth_request(
            endpoint="accounts:signUp",
            payload={
                "email": email,
                "password": password,
                "returnSecureToken": True,
            },
            success_message="Account created successfully.",
        )

    # =========================================================
    # EMAIL / PASSWORD SIGN IN
    # =========================================================

    def sign_in(self, email: str, password: str) -> AuthResult:
        result = self._auth_request(
            endpoint="accounts:signInWithPassword",
            payload={
                "email": email,
                "password": password,
                "returnSecureToken": True,
            },
            success_message="Signed in successfully.",
        )

        if not result.success or not result.user:
            return result

        lookup = self.lookup_account(result.user.id_token)

        if lookup.success and lookup.user:
            lookup.user.refresh_token = result.user.refresh_token
            lookup.user.expires_in = result.user.expires_in
            return AuthResult(True, "Signed in successfully.", lookup.user)

        return result

    # =========================================================
    # GOOGLE -> FIREBASE
    # =========================================================

    def sign_in_with_google_id_token(self, google_id_token: str) -> AuthResult:
        google_id_token = str(google_id_token or "").strip()

        if not google_id_token:
            return AuthResult(False, "Google ID token is missing.")

        url = f"{self.base_url}/accounts:signInWithIdp?key={self.api_key}"

        post_body = urlencode(
            {
                "id_token": google_id_token,
                "providerId": "google.com",
            }
        )

        payload = {
            "postBody": post_body,
            "requestUri": "http://localhost",
            "returnIdpCredential": True,
            "returnSecureToken": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            data = response.json()
        except requests.RequestException as exc:
            return AuthResult(False, f"Network error: {exc}")
        except ValueError:
            return AuthResult(False, "Firebase returned an invalid response.")

        if not response.ok:
            return AuthResult(False, self._friendly_error(data))

        user = self._user_from_auth_payload(data)

        lookup = self.lookup_account(user.id_token)

        if lookup.success and lookup.user:
            lookup.user.refresh_token = user.refresh_token
            lookup.user.expires_in = user.expires_in
            lookup.user.display_name = lookup.user.display_name or user.display_name
            lookup.user.photo_url = lookup.user.photo_url or user.photo_url
            user = lookup.user
        else:
            # Google identity providers normally return a verified email.
            user.email_verified = True

        return AuthResult(True, "Google Sign-In successful.", user)

    # =========================================================
    # SEND EMAIL VERIFICATION
    # =========================================================

    def send_email_verification(self, id_token: str) -> AuthResult:
        id_token = str(id_token or "").strip()

        if not id_token:
            return AuthResult(False, "Firebase ID token is missing.")

        url = f"{self.base_url}/accounts:sendOobCode?key={self.api_key}"

        payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token,
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            data = response.json()
        except requests.RequestException as exc:
            return AuthResult(False, f"Network error: {exc}")
        except ValueError:
            return AuthResult(False, "Firebase returned an invalid response.")

        if not response.ok:
            return AuthResult(False, self._friendly_error(data))

        return AuthResult(True, "Verification email sent successfully.")

    # =========================================================
    # ACCOUNT LOOKUP / VERIFICATION STATUS
    # =========================================================

    def lookup_account(self, id_token: str) -> AuthResult:
        id_token = str(id_token or "").strip()

        if not id_token:
            return AuthResult(False, "Firebase ID token is missing.")

        url = f"{self.base_url}/accounts:lookup?key={self.api_key}"

        try:
            response = requests.post(
                url,
                json={"idToken": id_token},
                timeout=self.timeout,
            )
            data = response.json()
        except requests.RequestException as exc:
            return AuthResult(False, f"Network error: {exc}")
        except ValueError:
            return AuthResult(False, "Firebase returned an invalid response.")

        if not response.ok:
            return AuthResult(False, self._friendly_error(data))

        users = data.get("users") or []

        if not users:
            return AuthResult(False, "Firebase user could not be found.")

        raw = users[0]

        providers = raw.get("providerUserInfo") or []
        provider_display_name = ""
        provider_photo_url = ""

        for provider in providers:
            provider_display_name = provider_display_name or str(
                provider.get("displayName", "") or ""
            )
            provider_photo_url = provider_photo_url or str(
                provider.get("photoUrl", "") or ""
            )

        user = AuthUser(
            uid=str(raw.get("localId", "") or ""),
            email=str(raw.get("email", "") or ""),
            display_name=str(raw.get("displayName", "") or provider_display_name),
            photo_url=str(raw.get("photoUrl", "") or provider_photo_url),
            phone_number=str(raw.get("phoneNumber", "") or ""),
            id_token=id_token,
            refresh_token="",
            expires_in=3600,
            email_verified=bool(raw.get("emailVerified", False)),
        )

        return AuthResult(True, "Account status loaded.", user)

    # =========================================================
    # PASSWORD RESET
    # =========================================================

    def send_password_reset(self, email: str) -> AuthResult:
        url = f"{self.base_url}/accounts:sendOobCode?key={self.api_key}"

        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email,
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            data = response.json()
        except requests.RequestException as exc:
            return AuthResult(False, f"Network error: {exc}")
        except ValueError:
            return AuthResult(False, "Firebase returned an invalid response.")

        if not response.ok:
            return AuthResult(False, self._friendly_error(data))

        return AuthResult(True, "Password reset email sent.")

    # =========================================================
    # PHONE OTP -> FIREBASE
    # =========================================================

    def sign_in_with_phone_number(
        self,
        session_info: str,
        code: str,
    ) -> AuthResult:
        session_info = str(session_info or "").strip()
        code = str(code or "").strip()

        if not session_info:
            return AuthResult(False, "Phone verification session is missing.")

        if len(code) != 6 or not code.isdigit():
            return AuthResult(False, "Enter a valid 6-digit OTP.")

        result = self._auth_request(
            endpoint="accounts:signInWithPhoneNumber",
            payload={
                "sessionInfo": session_info,
                "code": code,
            },
            success_message="Phone verified successfully.",
        )

        if not result.success or not result.user:
            return result

        lookup = self.lookup_account(result.user.id_token)

        if lookup.success and lookup.user:
            lookup.user.refresh_token = result.user.refresh_token
            lookup.user.expires_in = result.user.expires_in
            lookup.user.phone_number = (
                lookup.user.phone_number
                or result.user.phone_number
            )
            return AuthResult(
                True,
                "Phone verified successfully.",
                lookup.user,
            )

        return result

    # =========================================================
    # REFRESH FIREBASE TOKEN
    # =========================================================

    def refresh_token(self, refresh_token: str) -> AuthResult:
        refresh_token = str(refresh_token or "").strip()

        if not refresh_token:
            return AuthResult(False, "Refresh token is missing.")

        url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        try:
            response = requests.post(url, data=payload, timeout=self.timeout)
            data = response.json()
        except requests.RequestException as exc:
            return AuthResult(False, f"Network error: {exc}")
        except ValueError:
            return AuthResult(False, "Firebase returned an invalid response.")

        if not response.ok:
            return AuthResult(False, self._friendly_error(data))

        user = AuthUser(
            uid=str(data.get("user_id", "") or ""),
            email="",
            display_name="",
            photo_url="",
            phone_number="",
            id_token=str(data.get("id_token", "") or ""),
            refresh_token=str(data.get("refresh_token", refresh_token) or refresh_token),
            expires_in=int(data.get("expires_in", 3600) or 3600),
            email_verified=False,
        )

        return AuthResult(True, "Session refreshed successfully.", user)

    # =========================================================
    # SHARED EMAIL AUTH REQUEST
    # =========================================================

    def _auth_request(
        self,
        endpoint: str,
        payload: dict,
        success_message: str,
    ) -> AuthResult:
        url = f"{self.base_url}/{endpoint}?key={self.api_key}"

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            data = response.json()
        except requests.RequestException as exc:
            return AuthResult(False, f"Network error: {exc}")
        except ValueError:
            return AuthResult(False, "Firebase returned an invalid response.")

        if not response.ok:
            return AuthResult(False, self._friendly_error(data))

        user = self._user_from_auth_payload(data)
        return AuthResult(True, success_message, user)

    def _user_from_auth_payload(self, data: dict) -> AuthUser:
        return AuthUser(
            uid=str(data.get("localId", "") or ""),
            email=str(data.get("email", "") or ""),
            display_name=str(data.get("displayName", "") or ""),
            photo_url=str(data.get("photoUrl", "") or ""),
            phone_number=str(data.get("phoneNumber", "") or ""),
            id_token=str(data.get("idToken", "") or ""),
            refresh_token=str(data.get("refreshToken", "") or ""),
            expires_in=int(data.get("expiresIn", 3600) or 3600),
            email_verified=bool(data.get("emailVerified", False)),
        )

    # =========================================================
    # FRIENDLY FIREBASE ERRORS
    # =========================================================

    def _friendly_error(self, data: dict) -> str:
        raw_message = str(
            data.get("error", {}).get("message", "AUTHENTICATION_FAILED")
        )
        code = raw_message.split(" : ")[0].strip()

        friendly = {
            "EMAIL_EXISTS": "An account with this email already exists.",
            "OPERATION_NOT_ALLOWED": "This sign-in method is not enabled in Firebase.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please try again later.",
            "EMAIL_NOT_FOUND": "Incorrect email or password.",
            "INVALID_PASSWORD": "Incorrect email or password.",
            "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
            "USER_DISABLED": "This account has been disabled.",
            "WEAK_PASSWORD": "Password is too weak.",
            "INVALID_EMAIL": "Enter a valid email address.",
            "MISSING_PASSWORD": "Enter your password.",
            "MISSING_EMAIL": "Enter your email address.",
            "INVALID_REFRESH_TOKEN": "Your saved session is no longer valid.",
            "TOKEN_EXPIRED": "Your session has expired.",
            "INVALID_ID_TOKEN": "Your session token is invalid or expired.",
            "USER_NOT_FOUND": "This account could not be found.",
            "FEDERATED_USER_ID_ALREADY_LINKED": "This Google account is already linked to another user.",
            "INVALID_IDP_RESPONSE": "Google authentication could not be verified.",
            "INVALID_PENDING_TOKEN": "Google authentication could not be verified.",
            "INVALID_PHONE_NUMBER": "Enter a valid phone number with country code.",
            "MISSING_PHONE_NUMBER": "Enter your phone number.",
            "INVALID_CODE": "The OTP is incorrect. Please try again.",
            "MISSING_CODE": "Enter the 6-digit OTP.",
            "SESSION_EXPIRED": "This OTP session expired. Request a new OTP.",
            "INVALID_SESSION_INFO": "This phone verification session is invalid. Request a new OTP.",
            "MISSING_SESSION_INFO": "Phone verification session is missing.",
            "QUOTA_EXCEEDED": "Firebase SMS quota has been exceeded. Try again later.",
            "CAPTCHA_CHECK_FAILED": "Firebase reCAPTCHA verification failed. Please try again.",
        }

        return friendly.get(code, raw_message.replace("_", " ").capitalize())
