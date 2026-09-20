from PySide6.QtCore import Qt, Signal, QThread, QTimer, QFile, QIODevice
import re
import os
import base64
import tempfile
import wave
import requests
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PySide6.QtMultimedia import QAudioSource, QAudioFormat, QMediaDevices
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
)

from widgets.sidebar import Sidebar
from core.ai_service import GeminiChatWorker


def _microphone_icon():
    """Draw a crisp microphone icon without depending on emoji fonts."""
    pix = QPixmap(28, 28)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor("#F4EEFF"))
    pen.setWidthF(2.0)
    painter.setPen(pen)
    painter.setBrush(QColor("#8B5CF6"))
    painter.drawRoundedRect(10, 4, 8, 13, 4, 4)
    painter.setBrush(Qt.NoBrush)
    painter.drawArc(7, 9, 14, 12, 180 * 16, 180 * 16)
    painter.drawLine(14, 21, 14, 24)
    painter.drawLine(10, 24, 18, 24)
    painter.end()
    return QIcon(pix)


class VoiceTranscriptionWorker(QThread):
    """Transcribe recorded LYRx voice audio using the configured Gemini API."""
    recognized = Signal(str)
    failed = Signal(str)

    def __init__(self, wav_path, parent=None):
        super().__init__(parent)
        self.wav_path = str(wav_path)

    def run(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model = os.getenv("LYRX_AI_MODEL", "gemini-3.6-flash").strip() or "gemini-3.6-flash"

        if not api_key:
            self.failed.emit("Voice needs the same GEMINI_API_KEY already used by LYRx AI.")
            return

        try:
            audio_bytes = Path(self.wav_path).read_bytes()
            if len(audio_bytes) < 1500:
                self.failed.emit("I didn't receive enough microphone audio. Please try again.")
                return

            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent"
            )
            payload = {
                "contents": [{
                    "role": "user",
                    "parts": [
                        {"text": (
                            "Transcribe this voice command exactly as spoken. "
                            "The speaker may use English, Hindi, or Hinglish. "
                            "Return ONLY the transcription, with no label, quotes, "
                            "markdown or explanation."
                        )},
                        {"inlineData": {
                            "mimeType": "audio/wav",
                            "data": base64.b64encode(audio_bytes).decode("ascii"),
                        }},
                    ],
                }],
                "generationConfig": {"temperature": 0.0, "maxOutputTokens": 120},
            }

            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
                json=payload,
                timeout=45,
            )

            if response.status_code != 200:
                try:
                    detail = response.json().get("error", {}).get("message", "")
                except Exception:
                    detail = ""
                self.failed.emit(
                    "Voice transcription couldn't connect to LYRx AI."
                    + (f" {detail[:140]}" if detail else "")
                )
                return

            candidates = response.json().get("candidates") or []
            if not candidates:
                self.failed.emit("I couldn't understand that voice command. Please try again.")
                return

            parts = candidates[0].get("content", {}).get("parts", [])
            text = " ".join(
                str(part.get("text", "")).strip()
                for part in parts if part.get("text")
            ).strip().strip("`").strip()
            text = re.sub(r"(?i)^transcription\\s*:\\s*", "", text).strip()

            if text:
                self.recognized.emit(text)
            else:
                self.failed.emit("I couldn't understand that voice command. Please try again.")

        except requests.RequestException:
            self.failed.emit("Voice transcription needs an internet connection.")
        except Exception as error:
            self.failed.emit(f"Voice transcription error: {error}")


# ============================================================
# AI ASSISTANT SCREEN
# ============================================================

class AssistantScreen(QWidget):

    # ========================================================
    # CHAT
    # ========================================================

    message_sent = Signal(str)

    # ========================================================
    # PLAYER COMMANDS
    # ========================================================

    play_song_requested = Signal(
        str,
        str,
        str,
    )

    pause_requested = Signal()

    resume_requested = Signal()

    stop_requested = Signal()

    next_requested = Signal()

    previous_requested = Signal()

    # ========================================================
    # PLAYLIST COMMAND
    # ========================================================

    create_playlist_requested = Signal(
        str,
        str,
        object
    )

    # Day 29.5 - real online music action bridge.
    # action: "play" or "search"; query: provider search text.
    online_music_action_requested = Signal(str, str)

    # Real provider-backed playlist request: query, count, playlist name.
    online_playlist_requested = Signal(str, int, str)

    favorite_action_requested = Signal(str)

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        super().__init__()

        self.current_is_dark = True

        # Day 29.4 - real conversational AI state.
        # App/player commands stay local and instant; normal conversation
        # goes to Gemini in a background thread so the PySide UI never freezes.
        self.ai_history = []
        self.ai_worker = None
        self.ai_busy = False
        self.voice_worker = None
        self.voice_busy = False
        self.voice_audio_source = None
        self.voice_raw_file = None
        self.voice_raw_path = ""
        self.voice_wav_path = ""
        self.voice_timer = QTimer(self)
        self.voice_timer.setSingleShot(True)
        self.voice_timer.timeout.connect(self.stop_voice_input)

        self.setObjectName(
            "AssistantScreen"
        )

        # ====================================================
        # LOCAL SONG CATALOG
        # ====================================================
        #
        # For now LYRx has four local songs.
        #
        # Later this can be replaced by:
        #
        # Spotify / online catalog / API / database.
        #
        # ====================================================

        self.available_songs = [

            {
                "image": "assets/album_art/believer.jpg",
                "title": "Believer",
                "artist": "Imagine Dragons",
            },

            {
                "image": "assets/album_art/faded.jpg",
                "title": "Faded",
                "artist": "Alan Walker",
            },

            {
                "image": "assets/album_art/arcade.jpg",
                "title": "Arcade",
                "artist": "Duncan Laurence",
            },

            {
                "image": "assets/album_art/lethergo.jpg",
                "title": "Let Her Go",
                "artist": "Passenger",
            },

        ]

        # ====================================================
        # BUILD
        # ====================================================

        self.build_ui()

        self.apply_theme(
            True
        )

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        # ====================================================
        # ROOT
        # ====================================================

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
            0
        )

        # ====================================================
        # SIDEBAR
        # ====================================================

        self.sidebar = Sidebar()

        self.sidebar.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Expanding
        )

        root.addWidget(
            self.sidebar
        )

        # ====================================================
        # MAIN
        # ====================================================

        self.main = QWidget()

        self.main.setObjectName(
            "AssistantMain"
        )

        self.main.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        root.addWidget(
            self.main,
            1
        )

        self.main_layout = QVBoxLayout(
            self.main
        )

        self.main_layout.setContentsMargins(
            34,
            28,
            34,
            28
        )

        self.main_layout.setSpacing(
            18
        )

        # ====================================================
        # HEADER
        # ====================================================

        header_layout = QHBoxLayout()

        header_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        header_layout.setSpacing(
            14
        )

        # ----------------------------------------------------
        # AI ICON
        # ----------------------------------------------------

        self.ai_icon = QLabel(
            "✦"
        )

        self.ai_icon.setObjectName(
            "AssistantIcon"
        )

        self.ai_icon.setFixedSize(
            48,
            48
        )

        self.ai_icon.setAlignment(
            Qt.AlignCenter
        )

        header_layout.addWidget(
            self.ai_icon
        )

        # ----------------------------------------------------
        # HEADER TEXT
        # ----------------------------------------------------

        header_text = QVBoxLayout()

        header_text.setSpacing(
            2
        )

        self.title_label = QLabel(
            "LYRx AI Assistant"
        )

        self.title_label.setObjectName(
            "AssistantTitle"
        )

        self.subtitle_label = QLabel(
            "Your personal music companion."
        )

        self.subtitle_label.setObjectName(
            "AssistantSubtitle"
        )

        header_text.addWidget(
            self.title_label
        )

        header_text.addWidget(
            self.subtitle_label
        )

        header_layout.addLayout(
            header_text
        )

        header_layout.addStretch()

        # ====================================================
        # CLEAR CHAT
        # ====================================================

        self.clear_button = QPushButton(
            "Clear Chat"
        )

        self.clear_button.setObjectName(
            "ClearChatButton"
        )

        self.clear_button.setCursor(
            Qt.PointingHandCursor
        )

        self.clear_button.setFixedHeight(
            34
        )

        self.clear_button.clicked.connect(
            self.clear_chat
        )

        header_layout.addWidget(
            self.clear_button
        )

        # ====================================================
        # STATUS
        # ====================================================

        self.status_label = QLabel(
            "●  Ready"
        )

        self.status_label.setObjectName(
            "AssistantStatus"
        )

        header_layout.addWidget(
            self.status_label
        )

        self.main_layout.addLayout(
            header_layout
        )

        # ====================================================
        # CHAT CARD
        # ====================================================

        self.chat_card = QFrame()

        self.chat_card.setObjectName(
            "AssistantChatCard"
        )

        chat_card_layout = QVBoxLayout(
            self.chat_card
        )

        chat_card_layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        chat_card_layout.setSpacing(
            14
        )

        # ====================================================
        # SCROLL AREA
        # ====================================================

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll_area.setFrameShape(
            QFrame.NoFrame
        )

        # ====================================================
        # CHAT CONTAINER
        # ====================================================

        self.chat_container = QWidget()

        self.chat_container.setObjectName(
            "AssistantChatContainer"
        )

        self.chat_layout = QVBoxLayout(
            self.chat_container
        )

        self.chat_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        self.chat_layout.setSpacing(
            12
        )

        # Always keep one stretch at bottom.
        self.chat_layout.addStretch()

        self.scroll_area.setWidget(
            self.chat_container
        )

        chat_card_layout.addWidget(
            self.scroll_area,
            1
        )

        # ====================================================
        # QUICK PROMPTS
        # ====================================================

        self.quick_title = QLabel(
            "QUICK PROMPTS"
        )

        self.quick_title.setObjectName(
            "QuickPromptTitle"
        )

        chat_card_layout.addWidget(
            self.quick_title
        )

        quick_layout = QHBoxLayout()

        quick_layout.setSpacing(
            8
        )

        self.quick_buttons = []

        quick_prompts = [

            (
                "🎵  Recommend songs",
                "Recommend songs"
            ),

            (
                "🎧  Make a playlist",
                "Make me a playlist"
            ),

            (
                "💜  My mood",
                "Suggest music for my mood"
            ),

            (
                "🔥  What should I play?",
                "What should I play?"
            ),

        ]

        for (
            button_text,
            prompt
        ) in quick_prompts:

            button = QPushButton(
                button_text
            )

            button.setObjectName(
                "QuickPromptButton"
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.setMinimumHeight(
                38
            )

            button.clicked.connect(
                lambda checked=False,
                value=prompt:
                self.handle_quick_prompt(
                    value
                )
            )

            quick_layout.addWidget(
                button
            )

            self.quick_buttons.append(
                button
            )

        chat_card_layout.addLayout(
            quick_layout
        )

        # ====================================================
        # INPUT AREA
        # ====================================================

        input_layout = QHBoxLayout()

        input_layout.setSpacing(
            10
        )

        # ----------------------------------------------------
        # INPUT
        # ----------------------------------------------------

        self.input_box = QLineEdit()

        self.input_box.setObjectName(
            "AssistantInput"
        )

        self.input_box.setPlaceholderText(
            "Ask LYRx anything about music..."
        )

        self.input_box.setMinimumHeight(
            50
        )

        self.input_box.returnPressed.connect(
            self.send_message
        )

        input_layout.addWidget(
            self.input_box,
            1
        )

        # ----------------------------------------------------
        # VOICE INPUT
        # ----------------------------------------------------

        self.voice_button = QPushButton()
        self.voice_button.setObjectName("AssistantVoiceButton")
        self.voice_button.setIcon(_microphone_icon())
        self.voice_button.setIconSize(QPixmap(28, 28).size())
        self.voice_button.setFixedSize(50, 50)
        self.voice_button.setCursor(Qt.PointingHandCursor)
        self.voice_button.setToolTip("Voice input • Speak to LYRx AI")
        self.voice_button.clicked.connect(self.start_voice_input)
        self.voice_button.setStyleSheet("""
            QPushButton#AssistantVoiceButton {
                border-radius: 25px;
                border: 1px solid rgba(167, 139, 250, 150);
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #9B6CFF, stop:0.52 #7C3AED, stop:1 #5B21B6
                );
            }
            QPushButton#AssistantVoiceButton:hover {
                border: 1px solid #D8B4FE;
                background: #8B5CF6;
            }
            QPushButton#AssistantVoiceButton:pressed {
                background: #6D28D9;
            }
        """)
        input_layout.addWidget(self.voice_button)

        # ----------------------------------------------------
        # SEND
        # ----------------------------------------------------

        self.send_button = QPushButton(
            "Send  ➤"
        )

        self.send_button.setObjectName(
            "AssistantSendButton"
        )

        self.send_button.setMinimumSize(
            105,
            50
        )

        self.send_button.setCursor(
            Qt.PointingHandCursor
        )

        self.send_button.clicked.connect(
            self.send_message
        )

        input_layout.addWidget(
            self.send_button
        )

        chat_card_layout.addLayout(
            input_layout
        )

        self.main_layout.addWidget(
            self.chat_card,
            1
        )

        # ====================================================
        # WELCOME
        # ====================================================

        self.add_welcome_message()

    # ========================================================
    # WELCOME MESSAGE
    # ========================================================

    def add_welcome_message(self):

        self.add_ai_message(
            "Hey! I'm LYRx AI. 🎧\n\n"
            "I can help you discover music, recommend songs, "
            "find music for your mood, build playlist ideas, "
            "control playback, or decide what to play next."
        )

    # ========================================================
    # CLEAR CHAT
    # ========================================================

    def clear_chat(self):

        # Start a genuinely fresh AI conversation too.
        self.ai_history = []

        # ====================================================
        # REMOVE EVERYTHING EXCEPT BOTTOM STRETCH
        # ====================================================

        while self.chat_layout.count() > 1:

            item = self.chat_layout.takeAt(
                0
            )

            # ------------------------------------------------
            # WIDGET
            # ------------------------------------------------

            widget = item.widget()

            if widget is not None:

                widget.setParent(
                    None
                )

                widget.deleteLater()

                continue

            # ------------------------------------------------
            # CHILD LAYOUT
            # ------------------------------------------------

            child_layout = item.layout()

            if child_layout is not None:

                self.clear_layout(
                    child_layout
                )

                child_layout.deleteLater()

        # ====================================================
        # ADD CLEAN WELCOME
        # ====================================================

        self.add_ai_message(
            "Chat cleared. ✨\n\n"
            "What would you like to listen to?"
        )

        self.input_box.clear()

        self.input_box.setFocus()

    # ========================================================
    # CLEAR LAYOUT RECURSIVELY
    # ========================================================

    def clear_layout(
        self,
        layout
    ):

        while layout.count():

            item = layout.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.setParent(
                    None
                )

                widget.deleteLater()

            child_layout = item.layout()

            if child_layout is not None:

                self.clear_layout(
                    child_layout
                )

    # ========================================================
    # VOICE INPUT
    # ========================================================

    def start_voice_input(self):
        if self.voice_busy or self.ai_busy:
            return

        device = QMediaDevices.defaultAudioInput()
        if device.isNull():
            self.add_ai_message(
                "No microphone was detected. Enable a Windows microphone and try again."
            )
            return

        audio_format = QAudioFormat()
        audio_format.setSampleRate(16000)
        audio_format.setChannelCount(1)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        if not device.isFormatSupported(audio_format):
            self.add_ai_message(
                "Your current microphone doesn't support the LYRx voice recording format."
            )
            return

        temp_dir = Path(tempfile.gettempdir()) / "lyrx_voice"
        temp_dir.mkdir(parents=True, exist_ok=True)
        self.voice_raw_path = str(temp_dir / "command.raw")
        self.voice_wav_path = str(temp_dir / "command.wav")

        try:
            Path(self.voice_raw_path).unlink(missing_ok=True)
            Path(self.voice_wav_path).unlink(missing_ok=True)
        except Exception:
            pass

        self.voice_raw_file = QFile(self.voice_raw_path)
        if not self.voice_raw_file.open(QIODevice.OpenModeFlag.WriteOnly):
            self.add_ai_message("LYRx couldn't open its temporary voice recording.")
            self.voice_raw_file = None
            return

        self.voice_audio_source = QAudioSource(device, audio_format, self)
        self.voice_audio_source.start(self.voice_raw_file)

        self.voice_busy = True
        self.voice_button.setEnabled(False)
        self.voice_button.setToolTip("Listening…")
        self.input_box.setPlaceholderText("Listening… speak now")
        self.voice_button.setStyleSheet("""
            QPushButton#AssistantVoiceButton {
                border-radius: 25px;
                border: 2px solid #F0ABFC;
                background: #A855F7;
            }
        """)
        self.voice_timer.start(6000)

    def stop_voice_input(self):
        if not self.voice_busy:
            return

        try:
            if self.voice_audio_source is not None:
                self.voice_audio_source.stop()
            if self.voice_raw_file is not None:
                self.voice_raw_file.close()
        except Exception:
            pass

        self.voice_audio_source = None
        self.voice_raw_file = None

        try:
            raw = Path(self.voice_raw_path).read_bytes()
            if len(raw) < 1000:
                self._voice_failed(
                    "I couldn't hear enough audio. Check the Windows microphone input level."
                )
                self._voice_finished()
                return

            with wave.open(self.voice_wav_path, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(raw)
        except Exception as error:
            self._voice_failed(f"LYRx couldn't prepare the voice recording: {error}")
            self._voice_finished()
            return

        self.input_box.setPlaceholderText("Understanding your voice…")
        self.voice_worker = VoiceTranscriptionWorker(self.voice_wav_path, self)
        self.voice_worker.recognized.connect(self._voice_recognized)
        self.voice_worker.failed.connect(self._voice_failed)
        self.voice_worker.finished.connect(self._voice_finished)
        self.voice_worker.start()

    def _voice_recognized(self, text):
        text = str(text or "").strip()
        if not text:
            return
        self.input_box.setText(text)
        self.send_message()

    def _voice_failed(self, message):
        self.add_ai_message(message)

    def _voice_finished(self):
        self.voice_timer.stop()
        self.voice_busy = False
        self.voice_button.setEnabled(True)
        self.voice_button.setToolTip("Voice input • Speak to LYRx AI")
        self.voice_button.setStyleSheet("""
            QPushButton#AssistantVoiceButton {
                border-radius: 25px;
                border: 1px solid rgba(167, 139, 250, 150);
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #9B6CFF, stop:0.52 #7C3AED, stop:1 #5B21B6
                );
            }
            QPushButton#AssistantVoiceButton:hover {
                border: 1px solid #D8B4FE;
                background: #8B5CF6;
            }
            QPushButton#AssistantVoiceButton:pressed {
                background: #6D28D9;
            }
        """)
        if not self.ai_busy:
            self.input_box.setPlaceholderText("Ask LYRx AI anything...")

        worker = self.voice_worker
        self.voice_worker = None
        if worker is not None:
            worker.deleteLater()

        try:
            Path(self.voice_raw_path).unlink(missing_ok=True)
            Path(self.voice_wav_path).unlink(missing_ok=True)
        except Exception:
            pass

    # ========================================================
    # QUICK PROMPT
    # ========================================================

    def handle_quick_prompt(
        self,
        prompt
    ):

        self.input_box.setText(
            prompt
        )

        self.send_message()

    # ========================================================
    # SEND MESSAGE
    # ========================================================

    def send_message(self):

        message = self.input_box.text().strip()

        if not message or self.ai_busy:
            return

        self.add_user_message(message)
        self.input_box.clear()

        favorite_action = self._extract_favorite_action(message)
        if favorite_action is not None:
            self.favorite_action_requested.emit(favorite_action)
            return

        # Day 29.5.1: provider-backed playlist creation must be
        # resolved before the legacy hard-coded playlist command.
        playlist_action = self._extract_online_playlist_action(message)

        if playlist_action is not None:
            query, count, playlist_name = playlist_action
            self.online_playlist_requested.emit(query, count, playlist_name)
            self.add_ai_message(
                f'Building "{playlist_name}" from real LYRx provider '
                f'results for "{query}"... 🎧'
            )
            return

        # LYRx actions remain deterministic and local:
        # pause/resume/next/previous/play known demo track/create playlist.
        # Greetings, recommendations, knowledge questions and everything
        # else are handled by the real online assistant.
        if self._is_local_app_action(message):
            response = self.handle_command(message)

            if response:
                self.add_ai_message(response)

            self.message_sent.emit(message)
            return

        # Day 29.5: commands for songs/artists/moods that are not part
        # of the old four-track local catalog are routed into LYRx Discover.
        online_action = self._extract_online_music_action(message)

        if online_action is not None:
            action, query = online_action
            self.online_music_action_requested.emit(action, query)

            if action == "play":
                self.add_ai_message(
                    f'Searching LYRx providers for "{query}" and playing '
                    "the first playable result... 🎵"
                )
            else:
                self.add_ai_message(
                    f'Searching LYRx providers for "{query}"... 🔎'
                )
            return

        self.message_sent.emit(message)
        self._ask_online_ai(message)

    def _extract_favorite_action(self, message):
        """Recognize natural English/Hinglish Favorites commands before Gemini chat."""
        raw = str(message or "").strip()
        text = re.sub(r"[^a-z0-9 ]+", " ", raw.lower())
        text = re.sub(r"\\s+", " ", text).strip()

        favorite_word = any(
            word in text
            for word in ("favorite", "favorites", "favourite", "favourites", "fav", "favs")
        )
        if not favorite_word:
            return None

        # Examples:
        # add this song to my favorites
        # add current track in favourites
        # favorite this song
        if (
            ("add" in text and any(word in text for word in ("song", "track", "current", "this")))
            or text.startswith("favorite this")
            or text.startswith("favourite this")
        ):
            return "add_current"

        # Examples:
        # play a song from my favorites
        # play from favourites
        # play my fav songs
        if "play" in text:
            return "play_random"

        return None

    def _extract_online_playlist_action(self, message):
        raw = str(message or "").strip()
        text = raw.lower()

        if "playlist" not in text:
            return None

        if not any(word in text for word in ("make", "create", "build")):
            return None

        count_match = re.search(r"\b(\d{1,2})\b", text)
        count = int(count_match.group(1)) if count_match else 10
        count = max(1, min(count, 25))

        query = raw

        patterns = [
            r"(?i)^.*?playlist\s+(?:for|of|with)\s+",
            r"(?i)^.*?playlist\s+",
        ]
        for pattern in patterns:
            cleaned = re.sub(pattern, "", query, count=1).strip()
            if cleaned != query:
                query = cleaned
                break

        query = re.sub(r"(?i)\btop\s+\d+\s+(?:songs?|tracks?)\s+(?:of|by|from)\s+", "", query)
        query = re.sub(r"(?i)\b\d+\s+(?:songs?|tracks?)\s+(?:of|by|from)\s+", "", query)
        query = re.sub(r"(?i)\b(?:top\s+)?\d+\s+(?:songs?|tracks?)\b", "", query)
        query = re.sub(r"(?i)\b(?:songs?|tracks?)\s+(?:of|by|from)\s+", "", query)
        query = query.strip(" .!?-")

        if not query:
            query = "popular music"

        nice = re.sub(r"(?i)\b(songs?|music|tracks?)\b", "", query).strip()
        nice = " ".join(word.capitalize() for word in nice.split()) or "AI"
        playlist_name = f"{nice} Mix"

        return query, count, playlist_name

    def _extract_online_music_action(self, message):
        """Turn natural play/search wording into a real LYRx provider action."""
        raw = str(message or "").strip()
        text = raw.lower().strip()

        if not text:
            return None

        # Playlist creation stays with the existing LYRx playlist engine.
        if "playlist" in text:
            return None

        play_prefixes = (
            "play me ",
            "play some ",
            "play ",
            "listen to ",
            "start ",
        )

        search_prefixes = (
            "search for ",
            "search ",
            "find songs by ",
            "find music by ",
            "find ",
        )

        for prefix in play_prefixes:
            if text.startswith(prefix):
                query = raw[len(prefix):].strip(" .!?")
                if query and query.lower() not in {
                    "music", "song", "songs"
                }:
                    return ("play", query)

        # Natural mood wording: "play relaxing music", etc. is already
        # captured above and becomes the provider query "relaxing music".

        for prefix in search_prefixes:
            if text.startswith(prefix):
                query = raw[len(prefix):].strip(" .!?")
                if query:
                    return ("search", query)

        return None

    def _is_local_app_action(self, message):

        text = message.strip().lower()

        exact_actions = {
            "stop", "stop song", "stop music", "stop the song",
            "stop the music", "band karo", "music band karo",
            "song band karo", "pause", "pause song", "pause music",
            "pause the song", "pause the music", "music pause",
            "song pause", "resume", "resume song", "resume music",
            "continue", "continue song", "continue music",
            "continue playing", "play again", "next", "next song",
            "play next", "skip", "skip song", "skip this song",
            "previous", "previous song", "play previous", "last song",
            "go back song", "play", "play music", "play song",
            "start music",
        }

        if text in exact_actions:
            return True

        # Preserve existing in-app playlist creation.
        if (
            ("playlist" in text or "make me" in text)
            and any(
                word in text
                for word in ("create", "make", "build", "playlist")
            )
        ):
            return True

        # Preserve direct playback of tracks that the current LYRx command
        # engine actually knows how to execute.
        song = self.find_song_in_message(text)

        if song is not None and any(
            word in text
            for word in ("play", "listen", "start")
        ):
            return True

        return False

    def _ask_online_ai(self, message):

        self.ai_busy = True
        self._set_ai_input_enabled(False)

        self.ai_worker = GeminiChatWorker(
            message=message,
            history=list(self.ai_history),
        )

        self.ai_worker.reply_ready.connect(
            self._handle_online_ai_reply
        )

        self.ai_worker.error_ready.connect(
            self._handle_online_ai_error
        )

        self.ai_worker.finished.connect(
            self._online_ai_finished
        )

        self.ai_worker.start()

    def _handle_online_ai_reply(self, reply, sources):

        reply = (reply or "").strip()

        if not reply:
            reply = (
                "I received an empty response. Please try that again."
            )

        # Keep a compact rolling context instead of sending an unlimited
        # conversation back to the API.
        self.ai_history.append({
            "role": "user",
            "text": getattr(self.ai_worker, "message", ""),
        })

        self.ai_history.append({
            "role": "model",
            "text": reply,
        })

        self.ai_history = self.ai_history[-12:]

        if sources:
            source_lines = []
            seen = set()

            for source in sources[:4]:
                title = str(source.get("title", "")).strip()
                url = str(source.get("url", "")).strip()

                if not url or url in seen:
                    continue

                seen.add(url)
                source_lines.append(
                    f"• {title or 'Web source'}\\n  {url}"
                )

            if source_lines:
                reply += (
                    "\\n\\nWeb sources:\\n"
                    + "\\n".join(source_lines)
                )

        self.add_ai_message(reply)

    def _handle_online_ai_error(self, message):

        self.add_ai_message(message)

    def _online_ai_finished(self):

        self.ai_busy = False
        self._set_ai_input_enabled(True)

        worker = self.ai_worker
        self.ai_worker = None

        if worker is not None:
            worker.deleteLater()

        self.input_box.setFocus()

    def _set_ai_input_enabled(self, enabled):

        self.input_box.setEnabled(enabled)
        self.send_button.setEnabled(enabled)

        for button in getattr(self, "quick_buttons", []):
            button.setEnabled(enabled)

        if enabled:
            self.input_box.setPlaceholderText(
                "Ask LYRx AI anything..."
            )
            self.send_button.setText("Send")
        else:
            self.input_box.setPlaceholderText(
                "LYRx AI is thinking..."
            )
            self.send_button.setText("...")

    # ========================================================
    # MAIN COMMAND ENGINE
    # ========================================================

    def handle_command(
        self,
        message
    ):

        text = (
            message
            .strip()
            .lower()
        )

        # ====================================================
        # IMPORTANT
        # ====================================================
        #
        # Player commands MUST be checked before generic
        # words such as "song", "music", "recommend".
        #
        # Otherwise:
        #
        # "pause song"
        #
        # gets mistaken for:
        #
        # "recommend songs"
        #
        # ====================================================

        # ====================================================
        # STOP
        # ====================================================

        stop_phrases = [

            "stop",
            "stop song",
            "stop music",
            "stop the song",
            "stop the music",
            "band karo",
            "music band karo",
            "song band karo",

        ]

        if any(
            phrase == text
            for phrase in stop_phrases
        ):

            self.stop_requested.emit()

            return (
                "Stopped. ⏹\n\n"
                "Playback has been stopped."
            )

        # ====================================================
        # PAUSE
        # ====================================================

        pause_words = [
            "pause",
            "pause song",
            "pause music",
            "pause the song",
            "pause the music",
            "music pause",
            "song pause",
        ]

        if any(
            phrase == text
            for phrase in pause_words
        ):

            self.pause_requested.emit()

            return (
                "Paused. ⏸\n\n"
                "Your music is paused."
            )

        # ====================================================
        # RESUME
        # ====================================================

        resume_words = [

            "resume",
            "resume song",
            "resume music",
            "continue",
            "continue song",
            "continue music",
            "continue playing",
            "play again",

        ]

        if any(
            phrase == text
            for phrase in resume_words
        ):

            self.resume_requested.emit()

            return (
                "Resuming playback. ▶\n\n"
                "Enjoy the music."
            )

        # ====================================================
        # NEXT
        # ====================================================

        next_words = [

            "next",
            "next song",
            "play next",
            "skip",
            "skip song",
            "skip this song",

        ]

        if any(
            phrase == text
            for phrase in next_words
        ):

            self.next_requested.emit()

            return (
                "Skipping to the next track. ⏭"
            )

        # ====================================================
        # PREVIOUS
        # ====================================================

        previous_words = [

            "previous",
            "previous song",
            "play previous",
            "last song",
            "go back song",

        ]

        if any(
            phrase == text
            for phrase in previous_words
        ):

            self.previous_requested.emit()

            return (
                "Going back to the previous track. ⏮"
            )

        # ====================================================
        # PLAY SPECIFIC SONG
        # ====================================================

        matched_song = self.find_song_in_message(
            text
        )

        if matched_song is not None:

            # ------------------------------------------------
            # Require play-like intent
            # ------------------------------------------------

            play_intent = (

                "play" in text
                or
                "listen" in text
                or
                "start" in text

            )

            if play_intent:

                self.play_song_requested.emit(

                    matched_song[
                        "image"
                    ],

                    matched_song[
                        "title"
                    ],

                    matched_song[
                        "artist"
                    ],

                )

                return (
                    "Sure. 🎵\n\n"
                    f'Playing {matched_song["title"]} '
                    f'by {matched_song["artist"]}.'
                )

        # ====================================================
        # HELLO
        # ====================================================

        greetings = [

            "hi",
            "hello",
            "hey",
            "hii",
            "hey lyrx",
            "hello lyrx",

        ]

        if text in greetings:

            return (
                "Hey! 👋\n\n"
                "I'm ready. Tell me what kind of music "
                "you're in the mood for."
            )

        # ====================================================
        # SAD MOOD
        # ====================================================

        if (
            "sad" in text
            or
            "emotional" in text
            or
            "heartbreak" in text
        ):

            return (
                "Sounds like you're in a softer mood. 💜\n\n"
                "I'd suggest:\n\n"
                "💜 Arcade — Duncan Laurence\n"
                "🎸 Let Her Go — Passenger\n"
                "🌙 Faded — Alan Walker\n\n"
                'You can say "Play Arcade".'
            )

        # ====================================================
        # ENERGETIC
        # ====================================================

        if (
            "energetic" in text
            or
            "energy" in text
            or
            "workout" in text
            or
            "gym" in text
        ):

            return (
                "Let's raise the energy. 🔥\n\n"
                "My pick from your current LYRx library is:\n\n"
                "🔥 Believer — Imagine Dragons\n\n"
                'Say "Play Believer" and I\'ll start it.'
            )

        # ====================================================
        # MOOD
        # ====================================================

        if (
            "mood" in text
            or
            "feeling" in text
        ):

            return (
                "Tell me how you're feeling. 💜\n\n"
                "You can say:\n\n"
                "• sad\n"
                "• energetic\n"
                "• chill\n"
                "• emotional\n\n"
                "I'll pick from the music currently "
                "available inside LYRx."
            )

        # ====================================================
        # CREATE PLAYLIST
        # ====================================================

        if (
            "playlist" in text
            or
            "make me" in text
        ):

            # =================================================
            # SAD / EMOTIONAL
            # =================================================

            if (
                "sad" in text
                or
                "emotional" in text
                or
                "heartbreak" in text
            ):

                playlist_name = (
                    "AI Emotional Mix"
                )

                description = (
                    "A softer emotional mix created by LYRx AI."
                )

                songs = [

                    {
                        "image": "assets/album_art/arcade.jpg",
                        "title": "Arcade",
                        "artist": "Duncan Laurence",
                    },

                    {
                        "image": "assets/album_art/lethergo.jpg",
                        "title": "Let Her Go",
                        "artist": "Passenger",
                    },

                    {
                        "image": "assets/album_art/faded.jpg",
                        "title": "Faded",
                        "artist": "Alan Walker",
                    },

                ]

            # =================================================
            # ENERGY / WORKOUT
            # =================================================

            elif (
                "gym" in text
                or
                "workout" in text
                or
                "energy" in text
                or
                "energetic" in text
            ):

                playlist_name = (
                    "AI Energy Mix"
                )

                description = (
                    "An energetic playlist created by LYRx AI."
                )


                songs = [

                    {
                        "image": "assets/album_art/believer.jpg",
                        "title": "Believer",
                        "artist": "Imagine Dragons",
                    },

                    {
                        "image": "assets/album_art/faded.jpg",
                        "title": "Faded",
                        "artist": "Alan Walker",
                    },

                ]

            # =================================================
            # CHILL / NIGHT
            # =================================================

            elif (
                "chill" in text
                or
                "night" in text
                or
                "relax" in text
                or
                "calm" in text
            ):

                playlist_name = (
                    "AI Chill Mix"
                )

                description = (
                    "A calm playlist created by LYRx AI."
                )

                songs = [

                    {
                        "image": "assets/album_art/faded.jpg",
                        "title": "Faded",
                        "artist": "Alan Walker",
                    },

                    {
                        "image": "assets/album_art/arcade.jpg",
                        "title": "Arcade",
                        "artist": "Duncan Laurence",
                    },

                    {
                        "image": "assets/album_art/lethergo.jpg",
                        "title": "Let Her Go",
                        "artist": "Passenger",
                    },

                ]

            # =================================================
            # DEFAULT AI MIX
            # =================================================

            else:

                playlist_name = (
                    "AI Daily Mix"
                )

                description = (
                    "A playlist created for you by LYRx AI."
                )

                songs = [

                    {
                        "image": "assets/album_art/believer.jpg",
                        "title": "Believer",
                        "artist": "Imagine Dragons",
                    },

                    {
                        "image": "assets/album_art/faded.jpg",
                        "title": "Faded",
                        "artist": "Alan Walker",
                    },

                    {
                        "image": "assets/album_art/arcade.jpg",
                        "title": "Arcade",
                        "artist": "Duncan Laurence",
                    },

                    {
                        "image": "assets/album_art/lethergo.jpg",
                        "title": "Let Her Go",
                        "artist": "Passenger",
                    },

                ]

            # =================================================
            # REQUEST ACTUAL PLAYLIST CREATION
            # =================================================

            self.create_playlist_requested.emit(
                playlist_name,
                description,
                songs
            )

            return (
                "Working on it. ✨\n\n"
                f'Creating "{playlist_name}" '
                "inside your LYRx playlists..."
            )

        # ====================================================
        # AVAILABLE TRACKS / RECOMMEND
        # ====================================================

        if (
            "recommend" in text
            or
            "suggest" in text
            or
            "songs" in text
            or
            "tracks" in text
            or
            "what should i play" in text
            or
            "what should i listen" in text
        ):

            return (
                "Here are the tracks currently available "
                "inside LYRx: 🎧\n\n"
                "🔥 Believer — Imagine Dragons\n"
                "🌙 Faded — Alan Walker\n"
                "💜 Arcade — Duncan Laurence\n"
                "🎸 Let Her Go — Passenger\n\n"
                "Tell me your mood and I'll narrow it down."
            )

        # ====================================================
        # GENERIC PLAY
        # ====================================================

        if text in (
            "play",
            "play music",
            "play song",
            "start music",
        ):

            return (
                "Which track should I play? 🎵\n\n"
                "You can say:\n\n"
                "• Play Believer\n"
                "• Play Faded\n"
                "• Play Arcade\n"
                "• Play Let Her Go"
            )

        # ====================================================
        # DEFAULT
        # ====================================================

        return (
            "I'm listening. 🎧\n\n"
            "Try asking me to:\n\n"
            "• Play Faded\n"
            "• Pause music\n"
            "• Resume music\n"
            "• Stop music\n"
            "• Play next\n"
            "• Recommend songs\n"
            "• Suggest sad music"
        )

    # ========================================================
    # FIND SONG
    # ========================================================

    def find_song_in_message(
        self,
        text
    ):

        normalized = (
            text
            .lower()
            .replace(
                "-",
                " "
            )
            .strip()
        )

        for song in self.available_songs:

            title = (
                song[
                    "title"
                ]
                .lower()
            )

            if title in normalized:

                return song

        # ====================================================
        # COMMON ALIAS
        # ====================================================

        if (
            "let her go" in normalized
            or
            "lethergo" in normalized
        ):

            for song in self.available_songs:

                if (
                    song[
                        "title"
                    ].lower()
                    ==
                    "let her go"
                ):

                    return song

        return None

    # ========================================================
    # USER MESSAGE
    # ========================================================

    def add_user_message(
        self,
        message
    ):

        row = QHBoxLayout()

        row.setContentsMargins(
            20,
            0,
            8,
            0
        )

        row.addStretch()

        bubble = QFrame()

        bubble.setObjectName(
            "UserMessageBubble"
        )

        bubble.setMaximumWidth(
            560
        )

        bubble_layout = QVBoxLayout(
            bubble
        )

        bubble_layout.setContentsMargins(
            16,
            11,
            16,
            11
        )

        label = QLabel(
            message
        )

        label.setWordWrap(
            True
        )

        label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        bubble_layout.addWidget(
            label
        )

        row.addWidget(
            bubble
        )

        self.chat_layout.insertLayout(
            self.chat_layout.count() - 1,
            row
        )

        self.scroll_to_bottom()

    # ========================================================
    # AI MESSAGE
    # ========================================================

    def add_ai_message(
        self,
        message
    ):

        row = QHBoxLayout()

        row.setContentsMargins(
            8,
            0,
            20,
            0
        )

        bubble = QFrame()

        bubble.setObjectName(
            "AIMessageBubble"
        )

        bubble.setMaximumWidth(
            620
        )

        bubble_layout = QVBoxLayout(
            bubble
        )

        bubble_layout.setContentsMargins(
            16,
            12,
            16,
            12
        )

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        ai_label = QLabel(
            "✦  LYRx AI"
        )

        ai_label.setObjectName(
            "AIMessageName"
        )

        bubble_layout.addWidget(
            ai_label
        )

        # ----------------------------------------------------
        # MESSAGE
        # ----------------------------------------------------

        label = QLabel(
            message
        )

        label.setWordWrap(
            True
        )

        label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        label.setObjectName(
            "AIMessageText"
        )

        bubble_layout.addWidget(
            label
        )

        row.addWidget(
            bubble
        )

        row.addStretch()

        self.chat_layout.insertLayout(
            self.chat_layout.count() - 1,
            row
        )

        self.scroll_to_bottom()

    # ========================================================
    # SCROLL
    # ========================================================

    def scroll_to_bottom(
        self
    ):

        bar = (
            self.scroll_area
            .verticalScrollBar()
        )

        bar.setValue(
            bar.maximum()
        )

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

        # ====================================================
        # SIDEBAR
        # ====================================================

        if hasattr(
            self,
            "sidebar"
        ):

            self.sidebar.set_theme_state(
                self.current_is_dark
            )

        self.apply_theme(
            self.current_is_dark
        )

    # ========================================================
    # APPLY THEME
    # ========================================================

    def apply_theme(
        self,
        is_dark
    ):

        # ====================================================
        # DARK
        # ====================================================

        if is_dark:

            self.setStyleSheet(
                """
                QWidget#AssistantScreen {
                    background: transparent;
                }

                QWidget#AssistantMain {
                    background:
                        qlineargradient(
                            x1:0,
                            y1:0,
                            x2:1,
                            y2:1,
                            stop:0 #0B0915,
                            stop:0.45 #120D21,
                            stop:1 #18102B
                        );
                }

                QWidget#AssistantChatContainer {
                    background: transparent;
                }

                QLabel {
                    background: transparent;
                }

                QLabel#AssistantIcon {
                    background: #8B5CF6;
                    color: white;
                    border-radius: 24px;
                    font-size: 24px;
                    font-weight: 700;
                }

                QLabel#AssistantTitle {
                    color: #F5F1FF;
                    font-family: "Segoe UI";
                    font-size: 29px;
                    font-weight: 700;
                }

                QLabel#AssistantSubtitle {
                    color: #9D91B9;
                    font-size: 13px;
                }

                QLabel#AssistantStatus {
                    color: #A78BFA;
                    font-size: 12px;
                    font-weight: 600;
                }

                QPushButton#ClearChatButton {
                    color: #AFA3C8;
                    background: rgba(139, 92, 246, 12);
                    border: 1px solid rgba(139, 92, 246, 38);
                    border-radius: 10px;
                    padding: 0px 13px;
                    font-size: 11px;
                    font-weight: 600;
                }

                QPushButton#ClearChatButton:hover {
                    color: white;
                    background: rgba(139, 92, 246, 30);
                    border: 1px solid rgba(167, 139, 250, 75);
                }

                QPushButton#ClearChatButton:pressed {
                    background: rgba(124, 58, 237, 55);
                }

                QFrame#AssistantChatCard {
                    background: rgba(22, 15, 39, 245);
                    border: 1px solid rgba(139, 92, 246, 55);
                    border-radius: 22px;
                }

                QScrollArea {
                    background: transparent;
                    border: none;
                }

                QWidget#qt_scrollarea_viewport {
                    background: transparent;
                    border: none;
                }

                QScrollBar:vertical {
                    background: transparent;
                    width: 7px;
                    margin: 4px;
                }

                QScrollBar::handle:vertical {
                    background: #3D3157;
                    border-radius: 3px;
                    min-height: 40px;
                }

                QScrollBar::handle:vertical:hover {
                    background: #624A8D;
                }

                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    height: 0px;
                }

                QLabel#QuickPromptTitle {
                    color: #75698D;
                    font-size: 10px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    padding-left: 4px;
                }

                QPushButton#QuickPromptButton {
                    color: #BDB1D5;
                    background: rgba(139, 92, 246, 15);
                    border: 1px solid rgba(139, 92, 246, 35);
                    border-radius: 12px;
                    padding: 8px 12px;
                    font-size: 11px;
                    font-weight: 600;
                }

                QPushButton#QuickPromptButton:hover {
                    color: white;
                    background: rgba(139, 92, 246, 35);
                    border: 1px solid rgba(167, 139, 250, 80);
                }

                QPushButton#QuickPromptButton:pressed {
                    background: rgba(124, 58, 237, 60);
                }

                QLineEdit#AssistantInput {
                    color: #F4F0FF;
                    background: #0F0B1C;
                    border: 1px solid #352758;
                    border-radius: 15px;
                    padding: 0px 17px;
                    font-size: 14px;
                }

                QLineEdit#AssistantInput:focus {
                    border: 1px solid #8B5CF6;
                    background: #110D20;
                }

                QPushButton#AssistantSendButton {
                    color: white;
                    background: #7C3AED;
                    border: none;
                    border-radius: 15px;
                    font-size: 13px;
                    font-weight: 700;
                }

                QPushButton#AssistantSendButton:hover {
                    background: #8B5CF6;
                }

                QPushButton#AssistantSendButton:pressed {
                    background: #6D28D9;
                }

                QFrame#UserMessageBubble {
                    background:
                        qlineargradient(
                            x1:0,
                            y1:0,
                            x2:1,
                            y2:0,
                            stop:0 #6D28D9,
                            stop:1 #8B5CF6
                        );

                    border-radius: 16px;
                }

                QFrame#UserMessageBubble QLabel {
                    color: white;
                    font-size: 13px;
                }

                QFrame#AIMessageBubble {
                    background: #1B1430;
                    border: 1px solid #33265A;
                    border-radius: 16px;
                }

                QLabel#AIMessageName {
                    color: #A78BFA;
                    font-size: 11px;
                    font-weight: 700;
                }

                QLabel#AIMessageText {
                    color: #DCD5EC;
                    font-size: 13px;
                }
                """
            )

        # ====================================================
        # LIGHT
        # ====================================================

        else:

            self.setStyleSheet(
                """
                QWidget#AssistantScreen {
                    background: transparent;
                }

                QWidget#AssistantMain {
                    background:
                        qlineargradient(
                            x1:0,
                            y1:0,
                            x2:1,
                            y2:1,
                            stop:0 #F8F5FC,
                            stop:0.5 #F0EAF8,
                            stop:1 #E8DDF5
                        );
                }

                QWidget#AssistantChatContainer {
                    background: transparent;
                }

                QLabel {
                    background: transparent;
                }

                QLabel#AssistantIcon {
                    background: #7C3AED;
                    color: white;
                    border-radius: 24px;
                    font-size: 24px;
                    font-weight: 700;
                }

                QLabel#AssistantTitle {
                    color: #30203F;
                    font-family: "Segoe UI";
                    font-size: 29px;
                    font-weight: 700;
                }

                QLabel#AssistantSubtitle {
                    color: #776786;
                    font-size: 13px;
                }

                QLabel#AssistantStatus {
                    color: #6D28D9;
                    font-size: 12px;
                    font-weight: 600;
                }

                QPushButton#ClearChatButton {
                    color: #695878;
                    background: rgba(124, 58, 237, 10);
                    border: 1px solid rgba(124, 58, 237, 35);
                    border-radius: 10px;
                    padding: 0px 13px;
                    font-size: 11px;
                    font-weight: 600;
                }

                QPushButton#ClearChatButton:hover {
                    color: #4B2875;
                    background: rgba(124, 58, 237, 22);
                    border: 1px solid rgba(124, 58, 237, 65);
                }

                QFrame#AssistantChatCard {
                    background: rgba(255, 255, 255, 220);
                    border: 1px solid rgba(124, 58, 237, 55);
                    border-radius: 22px;
                }

                QScrollArea {
                    background: transparent;
                    border: none;
                }

                QWidget#qt_scrollarea_viewport {
                    background: transparent;
                    border: none;
                }

                QScrollBar:vertical {
                    background: transparent;
                    width: 7px;
                    margin: 4px;
                }

                QScrollBar::handle:vertical {
                    background: #C5B6D7;
                    border-radius: 3px;
                    min-height: 40px;
                }

                QScrollBar::handle:vertical:hover {
                    background: #9E87B7;
                }

                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    height: 0px;
                }

                QLabel#QuickPromptTitle {
                    color: #8A769B;
                    font-size: 10px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    padding-left: 4px;
                }

                QPushButton#QuickPromptButton {
                    color: #5D4771;
                    background: rgba(124, 58, 237, 12);
                    border: 1px solid rgba(124, 58, 237, 35);
                    border-radius: 12px;
                    padding: 8px 12px;
                    font-size: 11px;
                    font-weight: 600;
                }

                QPushButton#QuickPromptButton:hover {
                    color: #4B2875;
                    background: rgba(124, 58, 237, 25);
                    border: 1px solid rgba(124, 58, 237, 65);
                }

                QLineEdit#AssistantInput {
                    color: #342442;
                    background: #FFFFFF;
                    border: 1px solid #D2C4DF;
                    border-radius: 15px;
                    padding: 0px 17px;
                    font-size: 14px;
                }

                QLineEdit#AssistantInput:focus {
                    border: 1px solid #7C3AED;
                }

                QPushButton#AssistantSendButton {
                    color: white;
                    background: #7C3AED;
                    border: none;
                    border-radius: 15px;
                    font-size: 13px;
                    font-weight: 700;
                }

                QPushButton#AssistantSendButton:hover {
                    background: #8B5CF6;
                }

                QPushButton#AssistantSendButton:pressed {
                    background: #6D28D9;
                }

                QFrame#UserMessageBubble {
                    background:
                        qlineargradient(
                            x1:0,
                            y1:0,
                            x2:1,
                            y2:0,
                            stop:0 #7C3AED,
                            stop:1 #8B5CF6
                        );

                    border-radius: 16px;
                }

                QFrame#UserMessageBubble QLabel {
                    color: white;
                    font-size: 13px;
                }

                QFrame#AIMessageBubble {
                    background: #F2ECF8;
                    border: 1px solid #D9CCE4;
                    border-radius: 16px;
                }

                QLabel#AIMessageName {
                    color: #6D28D9;
                    font-size: 11px;
                    font-weight: 700;
                }

                QLabel#AIMessageText {
                    color: #463650;
                    font-size: 13px;
                }
                """
            )

        self.update()

    # ========================================================
    # RESIZE
    # ========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        self.scroll_to_bottom()