from __future__ import annotations

import os
import secrets
import threading
import time
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from dotenv import load_dotenv


load_dotenv()


@dataclass
class PhoneVerificationResult:
    success: bool
    message: str
    verification_id: str = ""


class PhoneAuthService:
    """
    Starts Firebase Web phone verification in the user's browser.

    The browser page performs Firebase reCAPTCHA + SMS request and returns
    only the short-lived Firebase verification ID to a loopback HTTP server.
    The 6-digit OTP is entered inside LYRx and verified by Firebase REST.
    """

    def __init__(self):
        self.api_key = os.getenv("FIREBASE_API_KEY", "").strip()
        self.project_id = os.getenv("FIREBASE_PROJECT_ID", "").strip()
        self.web_url = os.getenv("PHONE_AUTH_WEB_URL", "").strip()
        self.timeout_seconds = 180

    def is_configured(self) -> bool:
        return bool(self.api_key and self.project_id and self.web_url)

    def start_verification(self, phone_number: str) -> PhoneVerificationResult:
        phone_number = str(phone_number or "").strip()

        if not phone_number.startswith("+"):
            return PhoneVerificationResult(
                False,
                "Phone number must include a country code."
            )

        if not self.api_key:
            return PhoneVerificationResult(
                False,
                "FIREBASE_API_KEY is missing from .env."
            )

        if not self.project_id:
            return PhoneVerificationResult(
                False,
                "FIREBASE_PROJECT_ID is missing from .env."
            )

        if not self.web_url:
            return PhoneVerificationResult(
                False,
                "PHONE_AUTH_WEB_URL is missing from .env."
            )

        state = secrets.token_urlsafe(24)
        callback_data = {
            "verification_id": "",
            "error": "",
            "done": False,
        }
        done_event = threading.Event()

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)

                if parsed.path != "/callback":
                    self.send_response(404)
                    self.end_headers()
                    return

                query = parse_qs(parsed.query)
                returned_state = (query.get("state") or [""])[0]

                if returned_state != state:
                    callback_data["error"] = "Security state check failed."
                else:
                    callback_data["verification_id"] = (
                        (query.get("verification_id") or [""])[0]
                    )
                    callback_data["error"] = (
                        (query.get("error") or [""])[0]
                    )

                callback_data["done"] = True
                done_event.set()

                success = bool(callback_data["verification_id"])
                title = "LYRx Phone Verification"
                body = (
                    "Verification request received. You can close this tab and return to LYRx."
                    if success
                    else
                    "Phone verification could not be started. Return to LYRx for details."
                )

                html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>{title}</title>
<style>body{{font-family:Arial,sans-serif;background:#0f0b18;color:#fff;display:grid;place-items:center;min-height:100vh;margin:0}}.card{{max-width:560px;padding:32px;border-radius:20px;background:#1a1228;text-align:center}}h1{{margin-top:0}}p{{color:#cfc7db;line-height:1.6}}</style></head>
<body><div class='card'><h1>{title}</h1><p>{body}</p></div></body></html>"""

                encoded = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, format, *args):
                return

        try:
            server = ThreadingHTTPServer(("127.0.0.1", 0), CallbackHandler)
        except OSError as exc:
            return PhoneVerificationResult(
                False,
                f"Could not start local verification callback: {exc}"
            )

        port = server.server_address[1]
        callback_url = f"http://127.0.0.1:{port}/callback"

        query = urlencode({
            "phone": phone_number,
            "apiKey": self.api_key,
            "projectId": self.project_id,
            "authDomain": f"{self.project_id}.firebaseapp.com",
            "callback": callback_url,
            "state": state,
        })

        separator = "&" if "?" in self.web_url else "?"
        verification_url = f"{self.web_url}{separator}{query}"

        server_thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )
        server_thread.start()

        try:
            opened = webbrowser.open(verification_url, new=1, autoraise=True)
            if not opened:
                return PhoneVerificationResult(
                    False,
                    "Could not open the verification page in your browser."
                )

            deadline = time.time() + self.timeout_seconds
            while time.time() < deadline:
                if done_event.wait(timeout=0.25):
                    break

            if not callback_data["done"]:
                return PhoneVerificationResult(
                    False,
                    "Phone verification timed out. Click Send OTP and try again."
                )

            if callback_data["error"]:
                return PhoneVerificationResult(
                    False,
                    callback_data["error"]
                )

            verification_id = str(
                callback_data["verification_id"] or ""
            ).strip()

            if not verification_id:
                return PhoneVerificationResult(
                    False,
                    "Firebase did not return a verification session."
                )

            return PhoneVerificationResult(
                True,
                "OTP requested successfully.",
                verification_id=verification_id,
            )

        finally:
            server.shutdown()
            server.server_close()
