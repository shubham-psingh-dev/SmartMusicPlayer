from PySide6.QtCore import Qt, Signal
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

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        super().__init__()

        self.current_is_dark = True

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

        message = (
            self.input_box
            .text()
            .strip()
        )

        if not message:

            return

        # ====================================================
        # USER BUBBLE
        # ====================================================

        self.add_user_message(
            message
        )

        self.input_box.clear()

        # ====================================================
        # COMMAND ENGINE
        # ====================================================

        response = self.handle_command(
            message
        )

        # ====================================================
        # AI BUBBLE
        # ====================================================

        if response:

            self.add_ai_message(
                response
            )

        # ====================================================
        # MESSAGE SIGNAL
        # ====================================================

        self.message_sent.emit(
            message
        )

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