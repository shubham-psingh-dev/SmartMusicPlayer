from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
)

from ui.home.home_screen import HomeScreen
from ui.favorites.favorites_screen import FavoritesScreen


class AppWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # ==================================================
        # WINDOW SETTINGS
        # ==================================================

        self.setWindowTitle(
            "🎵 LYRx"
        )

        self.resize(
            1400,
            850
        )

        self.setMinimumSize(
            1200,
            700
        )

        self.setWindowFlags(
            Qt.FramelessWindowHint
        )

        # ==================================================
        # PAGE CONTAINER
        # ==================================================

        self.pages = QStackedWidget()

        self.setCentralWidget(
            self.pages
        )

        # ==================================================
        # HOME
        # ==================================================

        self.home = HomeScreen()

        self.pages.addWidget(
            self.home
        )

        # ==================================================
        # FAVORITES
        # ==================================================

        self.favorites = FavoritesScreen()

        self.pages.addWidget(
            self.favorites
        )

        # ==================================================
        # SIDEBAR NAVIGATION
        # ==================================================

        self.home.sidebar.page_changed.connect(
            self.handle_page_change
        )

        self.favorites.sidebar.page_changed.connect(
            self.handle_page_change
        )

        # ==================================================
        # FAVORITE PLAY
        # ==================================================

        self.favorites.play_requested.connect(
            self.play_favorite_song
        )

        # ==================================================
        # START HOME
        # ==================================================

        self.pages.setCurrentWidget(
            self.home
        )

    # ==================================================
    # PAGE NAVIGATION
    # ==================================================

    def handle_page_change(
        self,
        page_name: str
    ):

        # --------------------------------------------------
        # HOME
        # --------------------------------------------------

        if page_name == "Home":

            self.pages.setCurrentWidget(
                self.home
            )

        # --------------------------------------------------
        # FAVORITES
        # --------------------------------------------------

        elif page_name == "Favorites":

            self.favorites.reload_favorites()

            self.pages.setCurrentWidget(
                self.favorites
            )

        # --------------------------------------------------
        # UPDATE SIDEBAR STATES
        # --------------------------------------------------

        self.update_sidebar_states(
            page_name
        )

        print(
            f"Page changed: {page_name}"
        )

    # ==================================================
    # SIDEBAR STATE
    # ==================================================

    def update_sidebar_states(
        self,
        page_name
    ):

        for button in self.home.sidebar.buttons:

            button.setChecked(
                button.page_name == page_name
            )

        for button in self.favorites.sidebar.buttons:

            button.setChecked(
                button.page_name == page_name
            )

    # ==================================================
    # PLAY FAVORITE
    # ==================================================

    def play_favorite_song(
        self,
        image_path,
        title,
        artist
    ):

        self.home.play_selected_song(
            image_path,
            title,
            artist
        )

        self.pages.setCurrentWidget(
            self.home
        )

        self.update_sidebar_states(
            "Home"
        )