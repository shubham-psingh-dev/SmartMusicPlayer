from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow


load_dotenv()


@dataclass
class GoogleOAuthResult:
    success: bool
    message: str
    id_token: str = ""
    access_token: str = ""


class GoogleAuthService:

    SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    def __init__(self):

        self.client_id = os.getenv(
            "GOOGLE_CLIENT_ID",
            ""
        ).strip()

        self.client_secret = os.getenv(
            "GOOGLE_CLIENT_SECRET",
            ""
        ).strip()

    def is_configured(self) -> bool:

        return bool(
            self.client_id
            and
            self.client_secret
        )

    def sign_in(self) -> GoogleOAuthResult:

        if not self.client_id:

            return GoogleOAuthResult(
                False,
                "GOOGLE_CLIENT_ID is missing from .env."
            )

        if not self.client_secret:

            return GoogleOAuthResult(
                False,
                "GOOGLE_CLIENT_SECRET is missing from .env."
            )

        client_config = {
            "installed": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": (
                    "https://accounts.google.com/o/oauth2/auth"
                ),
                "token_uri": (
                    "https://oauth2.googleapis.com/token"
                ),
                "auth_provider_x509_cert_url": (
                    "https://www.googleapis.com/oauth2/v1/certs"
                ),
                "redirect_uris": [
                    "http://localhost"
                ],
            }
        }

        try:

            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes=self.SCOPES
            )

            credentials = flow.run_local_server(
                host="127.0.0.1",
                port=0,
                authorization_prompt_message=(
                    "Opening Google Sign-In..."
                ),
                success_message=(
                    "LYRx Google Sign-In successful. "
                    "You can close this browser window "
                    "and return to LYRx."
                ),
                open_browser=True
            )

            google_id_token = str(
                credentials.id_token
                or ""
            ).strip()

            access_token = str(
                credentials.token
                or ""
            ).strip()

            if not google_id_token:

                return GoogleOAuthResult(
                    False,
                    "Google did not return an ID token."
                )

            return GoogleOAuthResult(
                True,
                "Google authentication successful.",
                id_token=google_id_token,
                access_token=access_token
            )

        except Exception as exc:

            return GoogleOAuthResult(
                False,
                f"Google Sign-In failed: {exc}"
            )
