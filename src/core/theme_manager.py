from PySide6.QtCore import QObject, Signal


class ThemeManager(QObject):

    DARK = "dark"
    LIGHT = "light"

    theme_changed = Signal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.current_theme = self.DARK

    # ============================================================
    # TOGGLE
    # ============================================================

    def toggle(self):

        if self.current_theme == self.DARK:

            self.current_theme = self.LIGHT

        else:

            self.current_theme = self.DARK

        self.theme_changed.emit(
            self.current_theme
        )

    # ============================================================
    # SET THEME
    # ============================================================

    def set_theme(self, theme):

        if theme not in (
            self.DARK,
            self.LIGHT
        ):

            return

        if self.current_theme == theme:

            return

        self.current_theme = theme

        self.theme_changed.emit(
            self.current_theme
        )

    # ============================================================
    # IS DARK
    # ============================================================

    def is_dark(self):

        return (
            self.current_theme
            == self.DARK
        )

    # ============================================================
    # GLOBAL APPLICATION STYLE
    # ============================================================

    def get_stylesheet(self):

        if self.is_dark():

            return self.dark_stylesheet()

        return self.light_stylesheet()

    # ============================================================
    # DARK
    # ============================================================

    def dark_stylesheet(self):

        return """

        /* ======================================================
           GLOBAL APPLICATION
           ====================================================== */

        QWidget {

            font-family:
                "Segoe UI",
                "Inter",
                "Arial";

        }

        QMainWindow {

            background: #0F0B1A;

        }

        QStackedWidget {

            background: #0F0B1A;

            border: none;

        }

        /* ======================================================
           PAGE BACKGROUND
           ====================================================== */

        QWidget#PageRoot {

            background: #0F0B1A;

        }

        QWidget#PageMain {

            background: #0F0B1A;

        }

        /* ======================================================
           MAIN CONTENT
           ====================================================== */

        QLabel#PageTitle {

            color: #FFFFFF;

            font-size: 25px;

            font-weight: 800;

        }

        QLabel#SectionTitle {

            color: #FFFFFF;

            font-size: 22px;

            font-weight: 800;

        }

        QLabel#PageSubtitle {

            color: #A79BBE;

            font-size: 13px;

            font-weight: 500;

        }

        /* ======================================================
           SEARCH
           ====================================================== */

        QLineEdit {

            color: #F5F0FF;

            background: #19132A;

            border: 1px solid #342650;

            border-radius: 14px;

            padding:
                9px
                14px;

            font-size: 13px;

            selection-background-color: #7C3AED;

        }

        QLineEdit:focus {

            border:
                1px solid #8B5CF6;

            background: #1D1630;

        }

        /* ======================================================
           GENERIC BUTTON
           ====================================================== */

        QPushButton {

            color: #D8D0E8;

            background: #1B152B;

            border:
                1px solid #33254D;

            border-radius: 11px;

            padding:
                8px
                14px;

            font-size: 13px;

            font-weight: 600;

        }

        QPushButton:hover {

            color: white;

            background: #281B40;

            border:
                1px solid #6941A5;

        }

        QPushButton:pressed {

            background: #352054;

        }

        /* ======================================================
           CARDS
           ====================================================== */

        QFrame#MusicCard {

            background: #19132A;

            border:
                1px solid #2F2345;

            border-radius: 16px;

        }

        QFrame#MusicCard:hover {

            background: #211832;

            border:
                1px solid #65419A;

        }

        /* ======================================================
           SCROLLBAR
           ====================================================== */

        QScrollBar:vertical {

            background: transparent;

            width: 8px;

            margin: 3px;

        }

        QScrollBar::handle:vertical {

            background: #5D477B;

            border-radius: 4px;

            min-height: 35px;

        }

        QScrollBar::handle:vertical:hover {

            background: #8B5CF6;

        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {

            height: 0px;

        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {

            background: transparent;

        }

        /* ======================================================
           SEPARATOR
           ====================================================== */

        QFrame#SidebarSeparator {

            background: #3A2856;

            border: none;

            min-width: 1px;

            max-width: 1px;

        }

        """

    # ============================================================
    # LIGHT
    # ============================================================

    def light_stylesheet(self):

        return """

        /* ======================================================
           GLOBAL APPLICATION
           ====================================================== */

        QWidget {

            font-family:
                "Segoe UI",
                "Inter",
                "Arial";

        }

        QMainWindow {

            background: #F7F3FB;

        }

        QStackedWidget {

            background: #F7F3FB;

            border: none;

        }

        /* ======================================================
           PAGE BACKGROUND
           ====================================================== */

        QWidget#PageRoot {

            background: #F7F3FB;

        }

        QWidget#PageMain {

            background: #F7F3FB;

        }

        /* ======================================================
           MAIN CONTENT
           ====================================================== */

        QLabel#PageTitle {

            color: #30243F;

            font-size: 25px;

            font-weight: 800;

        }

        QLabel#SectionTitle {

            color: #30243F;

            font-size: 22px;

            font-weight: 800;

        }

        QLabel#PageSubtitle {

            color: #766685;

            font-size: 13px;

            font-weight: 500;

        }

        /* ======================================================
           SEARCH
           ====================================================== */

        QLineEdit {

            color: #3A2C4C;

            background: #FFFFFF;

            border:
                1px solid #D9CBE8;

            border-radius: 14px;

            padding:
                9px
                14px;

            font-size: 13px;

            selection-background-color: #7C3AED;

        }

        QLineEdit:focus {

            border:
                1px solid #8B5CF6;

            background: #FFFFFF;

        }

        /* ======================================================
           GENERIC BUTTON
           ====================================================== */

        QPushButton {

            color: #514362;

            background: #FFFFFF;

            border:
                1px solid #DDD0EA;

            border-radius: 11px;

            padding:
                8px
                14px;

            font-size: 13px;

            font-weight: 600;

        }

        QPushButton:hover {

            color: #4B2875;

            background: #F3ECFA;

            border:
                1px solid #B99BDA;

        }

        QPushButton:pressed {

            background: #E8DDF3;

        }

        /* ======================================================
           CARDS
           ====================================================== */

        QFrame#MusicCard {

            background: #FFFFFF;

            border:
                1px solid #E0D4EA;

            border-radius: 16px;

        }

        QFrame#MusicCard:hover {

            background: #FBF8FE;

            border:
                1px solid #BCA0D8;

        }

        /* ======================================================
           SCROLLBAR
           ====================================================== */

        QScrollBar:vertical {

            background: transparent;

            width: 8px;

            margin: 3px;

        }

        QScrollBar::handle:vertical {

            background: #B9A4CA;

            border-radius: 4px;

            min-height: 35px;

        }

        QScrollBar::handle:vertical:hover {

            background: #8B5CF6;

        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {

            height: 0px;

        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {

            background: transparent;

        }

        /* ======================================================
           SEPARATOR
           ====================================================== */

        QFrame#SidebarSeparator {

            background: #D4C5E1;

            border: none;

            min-width: 1px;

            max-width: 1px;

        }

        """