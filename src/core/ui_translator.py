from PySide6.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit, QPlainTextEdit
from core.language_manager import language_manager, LITERAL_TRANSLATIONS

class UITranslator:
    @staticmethod
    def _known(text):
        return text in LITERAL_TRANSLATIONS.get("hi", {}) or text in LITERAL_TRANSLATIONS.get("fr", {})

    @classmethod
    def _text(cls, widget):
        try: current = widget.text()
        except Exception: return
        if not isinstance(current, str) or not current: return
        source = widget.property("_lyrx_i18n_original_text")
        if not source:
            if not cls._known(current): return
            source = current
            widget.setProperty("_lyrx_i18n_original_text", source)
        widget.setText(language_manager.translate_literal(source))

    @classmethod
    def _placeholder(cls, widget):
        try: current = widget.placeholderText()
        except Exception: return
        if not isinstance(current, str) or not current: return
        source = widget.property("_lyrx_i18n_original_placeholder")
        if not source:
            if not cls._known(current): return
            source = current
            widget.setProperty("_lyrx_i18n_original_placeholder", source)
        widget.setPlaceholderText(language_manager.translate_literal(source))

    @classmethod
    def translate_tree(cls, root):
        if root is None: return
        for typ in (QLabel, QPushButton):
            for w in root.findChildren(typ): cls._text(w)
        for typ in (QLineEdit, QTextEdit, QPlainTextEdit):
            for w in root.findChildren(typ): cls._placeholder(w)

ui_translator = UITranslator()
