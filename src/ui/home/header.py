from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class Header(QWidget):

    # =========================================================
    # SIGNALS
    # =========================================================

    # Existing signal:
    # Used by HomeScreen for instant/local filtering.
    search_changed = Signal(str)

    # =========================================================
    # DAY 20 - GLOBAL ONLINE SEARCH
    # =========================================================

    # Emitted ONLY when user presses Enter/Return.
    #
    # Example:
    #
    # Arijit Singh + Enter
    # Shape of You + Enter
    # Hindi romantic + Enter
    #
    # AppWindow will later receive this request and send it
    # to the online music search flow.
    online_search_requested = Signal(str)

    # =========================================================
    # INIT
    # =========================================================

    def __init__(self):

        super().__init__()

        self.setFixedHeight(
            80
        )

        self.build_ui()

    # =========================================================
    # BUILD UI
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

        # =====================================================
        # LEFT SPACE
        # =====================================================

        root.addStretch()

        # =====================================================
        # SEARCH BAR
        # =====================================================

        self.search = QLineEdit()

        # Day 20:
        # Make it clear this can search the online catalog too.
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

        self.search.setToolTip(
            "Type to filter local music.\n"
            "Press Enter to search the LYRx online catalog."
        )

        root.addWidget(
            self.search
        )

        # =====================================================
        # LOCAL SEARCH SIGNAL
        # =====================================================

        # IMPORTANT:
        #
        # We keep this existing behavior.
        #
        # Typing:
        #     Believer
        #
        # still lets HomeScreen filter its local cards.
        #
        self.search.textChanged.connect(
            self.search_changed.emit
        )

        # =====================================================
        # DAY 20 - ONLINE SEARCH SIGNAL
        # =====================================================

        # QLineEdit.returnPressed fires when the user presses:
        #
        # Enter
        # Return
        #
        # We do NOT call MusicService directly from Header.
        #
        # Header = UI
        # AppWindow/Discover = routing
        # MusicService = API
        #
        # This keeps the architecture clean.
        self.search.returnPressed.connect(
            self.request_online_search
        )

        # =====================================================
        # NOTIFICATION
        # =====================================================

        self.notification = QPushButton(
            "♧"
        )

        self.notification.setFixedSize(
            42,
            42
        )

        self.notification.setCursor(
            Qt.PointingHandCursor
        )

        self.notification.setStyleSheet(
            """
            QPushButton {

                background: #211A35;

                color: #CFC7EA;

                border: 1px solid #312850;

                border-radius: 21px;

                font-size: 17px;

                padding: 0px;
            }

            QPushButton:hover {

                background: #30204F;

                color: white;

                border: 1px solid #7C3AED;
            }

            QPushButton:pressed {

                background: #7C3AED;

                color: white;
            }
            """
        )

        root.addWidget(
            self.notification
        )

        # =====================================================
        # PROFILE
        # =====================================================

        self.profile = QPushButton(
            "•  Duggu"
        )

        self.profile.setFixedHeight(
            42
        )

        self.profile.setCursor(
            Qt.PointingHandCursor
        )

        self.profile.setStyleSheet(
            """
            QPushButton {

                background: #211A35;

                color: white;

                border: 1px solid #312850;

                border-radius: 21px;

                padding-left: 16px;
                padding-right: 16px;

                font-size: 14px;

                font-weight: 600;
            }

            QPushButton:hover {

                background: #30204F;

                border: 1px solid #7C3AED;
            }

            QPushButton:pressed {

                background: #7C3AED;
            }
            """
        )

        root.addWidget(
            self.profile
        )

        # =====================================================
        # WINDOW BUTTONS
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

        buttons = [

            self.btn_minimize,
            self.btn_maximize,
            self.btn_close,

        ]

        for btn in buttons:

            btn.setFixedSize(
                36,
                36
            )

            btn.setCursor(
                Qt.PointingHandCursor
            )

            btn.setStyleSheet(
                """
                QPushButton {

                    background: #211A35;

                    color: #D8D2EA;

                    border: 1px solid #2C2445;

                    border-radius: 18px;

                    font-family: "Segoe UI Symbol";

                    font-size: 18px;

                    font-weight: 400;

                    padding: 0px;

                    margin: 0px;
                }

                QPushButton:hover {

                    background: #30204F;

                    color: white;

                    border: 1px solid #7C3AED;
                }

                QPushButton:pressed {

                    background: #7C3AED;

                    color: white;

                    border: 1px solid #8B5CF6;
                }
                """
            )

            root.addWidget(
                btn
            )

        # =====================================================
        # CLOSE BUTTON SPECIAL STYLE
        # =====================================================

        self.btn_close.setStyleSheet(
            """
            QPushButton {

                background: #211A35;

                color: #D8D2EA;

                border: 1px solid #2C2445;

                border-radius: 18px;

                font-family: "Segoe UI Symbol";

                font-size: 21px;

                font-weight: 400;

                padding: 0px;

                margin: 0px;
            }

            QPushButton:hover {

                background: #BE123C;

                color: white;

                border: 1px solid #FB7185;
            }

            QPushButton:pressed {

                background: #9F1239;

                color: white;

                border: 1px solid #FB7185;
            }
            """
        )

        # =====================================================
        # WINDOW SIGNALS
        # =====================================================

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
    # DAY 20 - REQUEST ONLINE SEARCH
    # =========================================================

    def request_online_search(self):

        query = (
            self.search
            .text()
            .strip()
        )

        # -----------------------------------------------------
        # IGNORE EMPTY SEARCH
        # -----------------------------------------------------

        if not query:

            return

        print()
        print(
            "=" * 60
        )

        print(
            "LYRx DAY 20 ONLINE SEARCH REQUEST"
        )

        print(
            "Query:",
            query
        )

        print(
            "=" * 60
        )

        print()

        # -----------------------------------------------------
        # SEND QUERY UPWARD
        # -----------------------------------------------------

        self.online_search_requested.emit(
            query
        )

    # =========================================================
    # SET SEARCH TEXT
    # =========================================================

    def set_search_text(
        self,
        text
    ):

        self.search.setText(
            str(
                text or ""
            )
        )

    # =========================================================
    # CLEAR SEARCH
    # =========================================================

    def clear_search(self):

        self.search.clear()

    # =========================================================
    # FOCUS SEARCH
    # =========================================================

    def focus_search(self):

        self.search.setFocus(
            Qt.OtherFocusReason
        )

        self.search.selectAll()

    # =========================================================
    # MAXIMIZE / RESTORE
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