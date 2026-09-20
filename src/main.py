import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ui.splash.splash_screen import SplashScreen
from widgets.window import AppWindow


app = QApplication(sys.argv)

# Build the real LYRx window before the intro. It is shown behind the splash
# once the splash has painted, so Windows never has to construct/render the
# main window during the final dissolve.
main_window = AppWindow()
main_window.hide()

splash = SplashScreen()


def prepare_main_window():
    if not main_window.isVisible():
        main_window.show()
    main_window.raise_()
    splash.raise_()
    splash.activateWindow()


splash.start()
# The splash is already on screen. Render the main window underneath it while
# the intro is playing; the user still sees only the cinematic splash.
QTimer.singleShot(0, prepare_main_window)

sys.exit(app.exec())
