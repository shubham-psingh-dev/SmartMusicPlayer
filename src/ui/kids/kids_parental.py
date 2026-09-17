import hashlib

from PySide6.QtCore import QSettings


class KidsParentalControls:
    """Persistent Kids Mode safety preferences.

    PINs are stored as SHA-256 digests rather than plain text. This is a
    lightweight local-app gate, not an operating-system security boundary.
    """

    ORG = "LYRx"
    APP = "LYRxKids"

    DEFAULTS = {
        "safe_search": True,
        "block_explicit": True,
        "block_harmful": True,
        "block_external_links": True,
        "exit_pin_enabled": False,
    }

    EXPLICIT_TERMS = (
        "explicit", "18+", "nsfw", "adult only", "sexual", "sex ",
        "porn", "erotic", "uncensored",
    )
    HARMFUL_TERMS = (
        "suicide", "self harm", "self-harm", "kill yourself",
        "weapon tutorial", "gun tutorial", "bomb tutorial",
        "drug tutorial", "scam tutorial", "malware tutorial",
    )
    UNSAFE_QUERY_TERMS = EXPLICIT_TERMS + HARMFUL_TERMS

    def __init__(self):
        self.settings = QSettings(self.ORG, self.APP)

    def get_bool(self, key):
        default = self.DEFAULTS.get(key, False)
        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("1", "true", "yes", "on")

    def set_bool(self, key, value):
        self.settings.setValue(key, bool(value))
        self.settings.sync()

    @property
    def safe_search(self):
        return self.get_bool("safe_search")

    @property
    def block_explicit(self):
        return self.get_bool("block_explicit")

    @property
    def block_harmful(self):
        return self.get_bool("block_harmful")

    @property
    def block_external_links(self):
        return self.get_bool("block_external_links")

    @property
    def exit_pin_enabled(self):
        return self.get_bool("exit_pin_enabled") and bool(
            self.settings.value("exit_pin_hash", "")
        )

    @staticmethod
    def _hash(pin):
        return hashlib.sha256(str(pin).encode("utf-8")).hexdigest()

    @staticmethod
    def valid_pin_format(pin):
        return str(pin).isdigit() and 4 <= len(str(pin)) <= 6

    def set_pin(self, pin):
        pin = str(pin)
        if not self.valid_pin_format(pin):
            raise ValueError("PIN must contain 4 to 6 digits.")
        self.settings.setValue("exit_pin_hash", self._hash(pin))
        self.settings.setValue("exit_pin_enabled", True)
        self.settings.sync()

    def verify_pin(self, pin):
        saved = str(self.settings.value("exit_pin_hash", "") or "")
        return bool(saved) and self._hash(str(pin)) == saved

    def remove_pin(self):
        self.settings.remove("exit_pin_hash")
        self.settings.setValue("exit_pin_enabled", False)
        self.settings.sync()

    def query_allowed(self, query):
        if not self.safe_search:
            return True
        text = f" {str(query).lower()} "
        return not any(term in text for term in self.UNSAFE_QUERY_TERMS)

    def song_allowed(self, song):
        text = " ".join(
            str(getattr(song, key, "") or "")
            for key in ("title", "artist", "album")
        ).lower()
        if self.block_explicit and any(term in text for term in self.EXPLICIT_TERMS):
            return False
        if self.block_harmful and any(term in text for term in self.HARMFUL_TERMS):
            return False
        return True
