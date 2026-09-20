from __future__ import annotations

import os
from pathlib import Path

import requests
from PySide6.QtCore import QThread, Signal

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


def _load_project_env():
    if load_dotenv is None:
        return

    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",
        Path(__file__).resolve().parents[3] / ".env",
    ]

    for path in candidates:
        if path.exists():
            load_dotenv(path, override=False)
            return

    load_dotenv(override=False)


_load_project_env()


class GeminiChatWorker(QThread):
    """Gemini chat worker for LYRx. Normal chat uses no Search grounding."""

    reply_ready = Signal(str, object)
    error_ready = Signal(str)

    def __init__(self, message, history=None, parent=None):
        super().__init__(parent)
        self.message = str(message or "").strip()
        self.history = list(history or [])
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = (
            os.getenv("LYRX_AI_MODEL", "gemini-3.6-flash").strip()
            or "gemini-3.6-flash"
        )

    def run(self):
        if not self.api_key:
            self.error_ready.emit(
                "LYRx AI is ready, but GEMINI_API_KEY is not configured.\n\n"
                "Create a .env file in the project root and add:\n"
                "GEMINI_API_KEY=your_key_here\n\n"
                "Never commit the real .env file to GitHub."
            )
            return

        if not self.message:
            self.error_ready.emit("Please type a message for LYRx AI.")
            return

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )

        contents = []

        for item in self.history[-12:]:
            role = str(item.get("role", "user")).strip().lower()
            text = str(item.get("text", "")).strip()

            if not text:
                continue

            contents.append({
                "role": "model" if role == "model" else "user",
                "parts": [{"text": text}],
            })

        contents.append({
            "role": "user",
            "parts": [{"text": self.message}],
        })

        payload = {
            "systemInstruction": {
                "parts": [{
                    "text": (
                        "You are LYRx AI, the conversational assistant built "
                        "into the LYRx desktop music application. Be friendly, "
                        "concise, helpful and natural. You can answer general "
                        "knowledge, technology, coding, study, music and everyday "
                        "questions; you are not limited to music. Reply in the "
                        "user's language when clear. Hinglish is welcome when "
                        "the user writes Hinglish. Playback actions are handled "
                        "separately by LYRx, so never pretend you executed them. "
                        "Live web/search lookup is not enabled in this build. "
                        "If a question truly requires current live information, "
                        "say that live lookup is not enabled rather than inventing "
                        "current facts or sources."
                    )
                }]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.65,
                "maxOutputTokens": 900,
            },
        }

        try:
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key,
                },
                json=payload,
                timeout=45,
            )

            if response.status_code != 200:
                self._emit_http_error(response)
                return

            data = response.json()
            candidates = data.get("candidates") or []

            if not candidates:
                self.error_ready.emit(
                    "LYRx AI couldn't generate a response. "
                    "Please try rephrasing it."
                )
                return

            candidate = candidates[0]
            parts = candidate.get("content", {}).get("parts", [])

            reply_parts = []
            for part in parts:
                text = part.get("text")
                if text:
                    reply_parts.append(str(text))

            reply = "\n".join(reply_parts).strip()

            if not reply:
                self.error_ready.emit(
                    "LYRx AI returned no readable text. Please try again."
                )
                return

            # Keep assistant_screen.py's existing (reply, sources) contract.
            self.reply_ready.emit(reply, [])

        except requests.Timeout:
            self.error_ready.emit(
                "LYRx AI timed out while contacting Gemini. "
                "Check your internet connection and try again."
            )
        except requests.ConnectionError:
            self.error_ready.emit(
                "LYRx AI couldn't reach Gemini. "
                "Check your internet connection and try again."
            )
        except Exception as error:
            print("LYRx AI online error:", error)
            self.error_ready.emit(
                "Something went wrong while contacting LYRx AI. "
                "Please try again."
            )

    def _emit_http_error(self, response):
        code = response.status_code

        try:
            detail = str(
                response.json().get("error", {}).get("message", "")
            ).strip()
        except Exception:
            detail = ""

        lower_detail = detail.lower()

        if code in (401, 403):
            message = (
                "Gemini rejected the API key or project permission. "
                "Check GEMINI_API_KEY in .env and restart LYRx."
            )
        elif code == 404 or "not found" in lower_detail:
            message = (
                f"The Gemini model '{self.model}' is not available for this "
                "API/project. Update LYRX_AI_MODEL in .env to an available "
                "model and restart LYRx."
            )
        elif code == 429:
            message = (
                "Gemini returned a quota/rate-limit response for this project. "
                "LYRx is using normal AI chat without Google Search grounding. "
                "If this continues, check the project's actual Gemini API "
                "usage/quota in Google AI Studio."
            )
        elif code == 400:
            message = (
                "Gemini couldn't process that request."
                + (f"\n\n{detail}" if detail else "")
            )
        else:
            message = (
                f"LYRx AI service returned error {code}."
                + (f"\n\n{detail}" if detail else "")
            )

        self.error_ready.emit(message)
