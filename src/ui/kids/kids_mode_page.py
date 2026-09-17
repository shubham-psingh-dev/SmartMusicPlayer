from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QInputDialog, QLineEdit, QMessageBox
)
from PySide6.QtCore import Signal

from widgets.kids_sidebar import KidsSidebar
from ui.kids.kids_home_screen import KidsHomeScreen
from ui.kids.kids_content_screen import KidsContentScreen
from ui.kids.kids_player import KidsPlayerBar
from ui.kids.study_learn_screen import StudyLearnScreen
from ui.kids.kids_settings_screen import KidsSettingsScreen
from ui.kids.kids_parental import KidsParentalControls
from ui.kids.kids_favorites_screen import KidsFavoritesScreen


class KidsModePage(QWidget):
    exit_requested = Signal()
    minimize_requested = Signal()
    maximize_requested = Signal()
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = KidsSidebar(self)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        self.pages = QStackedWidget(self)

        self.home = KidsHomeScreen(self)
        self.pages.addWidget(self.home)
        self.route_pages = {"Kids Home": self.home}

        for route in ("Kids Music", "Stories", "Poems & Rhymes", "Spiritual"):
            page = KidsContentScreen(route, self)
            page.back_requested.connect(lambda: self.open("Kids Home"))
            page.song_requested.connect(self.play_song)
            self.route_pages[route] = page
            self.pages.addWidget(page)

        study = StudyLearnScreen(self)
        self.route_pages["Study & Learn"] = study
        self.pages.addWidget(study)

        self.favorites = KidsFavoritesScreen(self)
        self.favorites.back_requested.connect(lambda: self.open("Kids Home"))
        self.favorites.song_requested.connect(self.play_song)
        self.route_pages["Kids Favorites"] = self.favorites
        self.pages.addWidget(self.favorites)

        self.kids_settings = KidsSettingsScreen(self)
        self.route_pages["Kids Settings"] = self.kids_settings
        self.pages.addWidget(self.kids_settings)

        self.kids_player = KidsPlayerBar(self)
        self.kids_player.hide()

        right.addWidget(self.pages, 1)
        right.addWidget(self.kids_player)

        root.addWidget(self.sidebar)
        root.addLayout(right, 1)

        self.sidebar.exit_requested.connect(self.exit)
        self.sidebar.page_requested.connect(self.open)
        self.home.category_requested.connect(self.open)
        self.home.search_requested.connect(self.search_from_home)
        self.home.minimize_requested.connect(self.minimize_requested.emit)
        self.home.maximize_requested.connect(self.maximize_requested.emit)
        self.home.close_requested.connect(self.close_requested.emit)

    def search_from_home(self, query):
        page = self.route_pages["Kids Music"]
        self.open("Kids Music")
        page.search.setText(query)
        page.load_content(query)

    def play_song(self, song, queue):
        self.kids_player.show()
        self.kids_player.play_song(song, queue)

    def exit(self):
        controls = KidsParentalControls()
        if controls.exit_pin_enabled:
            pin, ok = QInputDialog.getText(
                self,
                "Parent PIN Required",
                "Enter the parent PIN to leave Kids Mode:",
                QLineEdit.Password,
            )
            if not ok:
                return
            if not controls.verify_pin(str(pin).strip()):
                QMessageBox.warning(
                    self,
                    "Incorrect PIN",
                    "That PIN is incorrect. Kids Mode will stay open.",
                )
                return

        self.kids_player.stop()
        self.kids_player.hide()
        self.exit_requested.emit()

    def open(self, route):
        page = self.route_pages.get(route)
        if not page:
            return

        self.pages.setCurrentWidget(page)
        for button in self.sidebar.buttons:
            button.setChecked(button.route == route)

        if isinstance(page, KidsContentScreen) and not page.songs:
            page.load_content()
        elif isinstance(page, KidsFavoritesScreen):
            page.refresh()
