from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from ui.home.home_screen import HomeScreen


class AppWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Window Settings
        self.setWindowTitle("🎵 NirVANA")

        self.resize(1400, 850)

        self.setMinimumSize(1200, 700)

        # Remove Windows Title Bar
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Home Screen
        self.home = HomeScreen()

        self.setCentralWidget(self.home)