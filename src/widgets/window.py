from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from ui.home.home_screen import HomeScreen
from widgets.title_bar import TitleBar


class AppWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Window Settings
        self.setWindowTitle("🎵 NirVANA")
        self.resize(1400, 850)
        self.setMinimumSize(1200, 700)

        # Remove Windows Title Bar
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Main Home Screen
        self.home = HomeScreen()

        # Set Home Screen
        self.setCentralWidget(self.home)

        # Create Custom Title Bar
        self.title_bar = TitleBar(self)

        # Add Title Bar to Home Layout
        self.home.main_layout.insertWidget(0, self.title_bar)