import json
from types import SimpleNamespace

from PySide6.QtCore import QSettings


class KidsFavoritesStore:
    ORG = "LYRx"
    APP = "LYRxKids"
    KEY = "kids_favorites_json"

    def __init__(self):
        self.settings = QSettings(self.ORG, self.APP)

    @staticmethod
    def key_for(song):
        sid = str(getattr(song, "id", "") or "").strip()
        if sid:
            return sid.lower()
        title = str(getattr(song, "title", "") or "").strip().lower()
        artist = str(getattr(song, "artist", "") or "").strip().lower()
        return f"{title}|{artist}"

    @staticmethod
    def serialize(song):
        data = {}
        for key in (
            "id", "title", "artist", "album", "audio_url", "preview_url",
            "image_url", "artwork_url", "provider", "source"
        ):
            value = getattr(song, key, "")
            if value is not None:
                data[key] = str(value)
        return data

    def _load_raw(self):
        raw = str(self.settings.value(self.KEY, "[]") or "[]")
        try:
            data = json.loads(raw)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_raw(self, rows):
        self.settings.setValue(self.KEY, json.dumps(rows, ensure_ascii=False))
        self.settings.sync()

    def contains(self, song):
        key = self.key_for(song)
        return any(row.get("_key") == key for row in self._load_raw())

    def add(self, song):
        rows = self._load_raw()
        key = self.key_for(song)
        if not key or any(row.get("_key") == key for row in rows):
            return False
        row = self.serialize(song)
        row["_key"] = key
        rows.insert(0, row)
        self._save_raw(rows)
        return True

    def remove(self, song):
        key = self.key_for(song)
        rows = self._load_raw()
        updated = [row for row in rows if row.get("_key") != key]
        if len(updated) == len(rows):
            return False
        self._save_raw(updated)
        return True

    def toggle(self, song):
        if self.contains(song):
            self.remove(song)
            return False
        self.add(song)
        return True

    def songs(self):
        songs = []
        for row in self._load_raw():
            data = {k: v for k, v in row.items() if k != "_key"}
            songs.append(SimpleNamespace(**data))
        return songs
