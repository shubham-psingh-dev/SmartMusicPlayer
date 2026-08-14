from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QFrame,
)


class AssistantScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.build_ui()

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            36,
            30,
            36,
            30,
        )

        main_layout.setSpacing(20)

        # ==================================================
        # HEADER
        # ==================================================

        header = QVBoxLayout()

        title = QLabel("LYRx AI Assistant")

        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 30px;
                font-weight: 700;
                background: transparent;
            }
        """)

        subtitle = QLabel(
            "Your personal music companion."
        )

        subtitle.setStyleSheet("""
            QLabel {
                color: #A79FD2;
                font-size: 14px;
                background: transparent;
            }
        """)

        header.addWidget(title)
        header.addWidget(subtitle)

        main_layout.addLayout(header)

        # ==================================================
        # CHAT CARD
        # ==================================================

        chat_card = QFrame()

        chat_card.setStyleSheet("""
            QFrame {
                background: #151026;
                border: 1px solid #33265A;
                border-radius: 18px;
            }
        """)

        chat_layout = QVBoxLayout(chat_card)

        chat_layout.setContentsMargins(
            22,
            22,
            22,
            22,
        )

        chat_layout.setSpacing(14)

        # ------------------------------
        # Conversation
        # ------------------------------

        self.chat_area = QTextEdit()

        self.chat_area.setReadOnly(True)

        self.chat_area.setPlaceholderText(
            "Your conversation with LYRx AI will appear here..."
        )

        self.chat_area.setStyleSheet("""
            QTextEdit {
                color: #E9E5FF;
                background: #0F0B1C;
                border: 1px solid #2B2148;
                border-radius: 14px;
                padding: 14px;
                font-size: 14px;
            }
        """)

        chat_layout.addWidget(
            self.chat_area,
            1,
        )

        # ==================================================
        # INPUT AREA
        # ==================================================

        input_layout = QHBoxLayout()

        input_layout.setSpacing(10)

        self.input_box = QLineEdit()

        self.input_box.setPlaceholderText(
            "Ask LYRx anything..."
        )

        self.input_box.setMinimumHeight(48)

        self.input_box.setStyleSheet("""
            QLineEdit {
                color: white;
                background: #0F0B1C;
                border: 1px solid #3B2A66;
                border-radius: 14px;
                padding: 0 16px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 1px solid #8B5CF6;
            }
        """)

        self.send_button = QPushButton("Send")

        self.send_button.setMinimumSize(
            90,
            48,
        )

        self.send_button.setCursor(
            Qt.PointingHandCursor
        )

        self.send_button.setStyleSheet("""
            QPushButton {
                color: white;
                background: #7C3AED;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #8B5CF6;
            }

            QPushButton:pressed {
                background: #6D28D9;
            }
        """)

        input_layout.addWidget(
            self.input_box,
            1,
        )

        input_layout.addWidget(
            self.send_button
        )

        chat_layout.addLayout(
            input_layout
        )

        main_layout.addWidget(
            chat_card,
            1,
        )

        # ==================================================
        # TEMPORARY LOCAL RESPONSE
        # ==================================================

        self.send_button.clicked.connect(
            self.send_message
        )

        self.input_box.returnPressed.connect(
            self.send_message
        )

    # ==================================================
    # MESSAGE HANDLER
    # ==================================================

    def send_message(self):

        message = self.input_box.text().strip()

        if not message:
            return

        self.chat_area.append(
            f"<b style='color:#A855F7;'>You:</b> "
            f"{message}"
        )

        self.chat_area.append(
            "<b style='color:#8B5CF6;'>LYRx AI:</b> "
            "I'm ready to help you with your music."
        )

        self.input_box.clear()