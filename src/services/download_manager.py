from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote
from uuid import uuid4

from PySide6.QtCore import (
    QObject,
    Signal,
    QSettings,
    QStandardPaths,
    QFile,
    QIODevice,
    QUrl,
)
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply,
)


# ============================================================
# LYRx
# DAY 26 - OFFLINE DOWNLOAD MANAGER
#
# FILE:
# src/services/download_manager.py
#
# IMPORTANT:
# LYRx only downloads a track when the provider/song explicitly
# exposes a downloadable flag + download URL. A playable stream
# or preview URL is NOT automatically treated as downloadable.
# ============================================================


def _safe_text(value) -> str:
    return str(value or "").strip()


def _safe_filename(value: str) -> str:
    value = _safe_text(value)

    value = re.sub(
        r'[<>:"/\\|?*\x00-\x1F]',
        "_",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    ).strip(" .")

    return value or "LYRx Track"


def _human_bytes(size: int) -> str:
    size = max(0, int(size or 0))

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    ]

    value = float(size)

    for unit in units:

        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"

            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{size} B"


class DownloadManager(QObject):

    download_started = Signal(
        str,
        str,
    )

    download_progress = Signal(
        str,
        int,
        int,
        int,
    )

    download_finished = Signal(
        str,
        object,
    )

    download_failed = Signal(
        str,
        str,
    )

    download_cancelled = Signal(
        str,
    )

    library_changed = Signal()

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.settings = QSettings(
            "LYRx",
            "LYRxDesktop",
        )

        self.network = QNetworkAccessManager(
            self
        )

        self.tasks = {}

        self.manifest_path = (
            self._app_data_dir()
            / "downloads.json"
        )

        self.manifest_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.manifest_path.exists():

            self._save_entries(
                []
            )

    # ========================================================
    # PATHS
    # ========================================================

    def _app_data_dir(
        self,
    ) -> Path:

        location = QStandardPaths.writableLocation(
            QStandardPaths.AppDataLocation
        )

        if location:

            path = Path(
                location
            )

        else:

            path = (
                Path.home()
                / ".lyrx"
            )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def default_download_dir(
        self,
    ) -> Path:

        downloads = QStandardPaths.writableLocation(
            QStandardPaths.DownloadLocation
        )

        if downloads:

            path = (
                Path(downloads)
                / "LYRx"
            )

        else:

            path = (
                Path.home()
                / "Downloads"
                / "LYRx"
            )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def download_dir(
        self,
    ) -> Path:

        saved = _safe_text(
            self.settings.value(
                "settings/download_path",
                "",
            )
        )

        path = (
            Path(saved)
            if saved
            else self.default_download_dir()
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    # ========================================================
    # PROVIDER CAPABILITY
    # ========================================================

    def _metadata(
        self,
        song,
    ) -> dict:

        metadata = getattr(
            song,
            "metadata",
            {},
        )

        if isinstance(
            metadata,
            dict,
        ):
            return metadata

        return {}

    def _original_song(
        self,
        song,
    ):

        metadata = self._metadata(
            song
        )

        return metadata.get(
            "original_song"
        )

    def downloadable_info(
        self,
        song,
    ) -> dict:

        if song is None:

            return {
                "downloadable": False,
                "url": "",
                "reason": (
                    "No track is selected."
                ),
            }

        metadata = self._metadata(
            song
        )

        original = self._original_song(
            song
        )

        downloadable = bool(
            getattr(
                song,
                "downloadable",
                False,
            )
        )

        download_url = _safe_text(
            getattr(
                song,
                "download_url",
                "",
            )
        )

        # Some older Jamendo adapter versions preserved these
        # values inside metadata rather than as first-class fields.
        if not downloadable:

            downloadable = bool(
                metadata.get(
                    "downloadable",
                    False,
                )
            )

        if not download_url:

            download_url = _safe_text(
                metadata.get(
                    "download_url",
                    "",
                )
            )

        if original is not None:

            if not downloadable:

                downloadable = bool(
                    getattr(
                        original,
                        "downloadable",
                        False,
                    )
                )

            if not download_url:

                download_url = _safe_text(
                    getattr(
                        original,
                        "download_url",
                        "",
                    )
                )

        parsed = urlparse(
            download_url
        )

        valid_url = (
            parsed.scheme.lower()
            in (
                "http",
                "https",
            )
            and bool(parsed.netloc)
        )

        provider = _safe_text(
            getattr(
                song,
                "provider",
                "",
            )
            or getattr(
                song,
                "source",
                "",
            )
            or metadata.get(
                "source",
                "",
            )
        )

        if not downloadable:

            reason = (
                f"{provider or 'This provider'} does not expose "
                "this track as downloadable."
            )

        elif not valid_url:

            reason = (
                "The provider did not return a valid download URL."
            )

        else:

            reason = ""

        return {
            "downloadable": (
                downloadable
                and valid_url
            ),
            "url": (
                download_url
                if valid_url
                else ""
            ),
            "provider": (
                provider
                or "online"
            ),
            "reason": reason,
        }

    def can_download(
        self,
        song,
    ) -> bool:

        return bool(
            self.downloadable_info(
                song
            ).get(
                "downloadable",
                False,
            )
        )

    # ========================================================
    # MANIFEST
    # ========================================================

    def entries(
        self,
    ) -> list:

        try:

            if not self.manifest_path.exists():
                return []

            data = json.loads(
                self.manifest_path.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(
                data,
                list,
            ):
                return []

            cleaned = []

            for item in data:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                cleaned.append(
                    item
                )

            return cleaned

        except Exception as error:

            print(
                "LYRx downloads manifest read error:",
                error
            )

            return []

    def _save_entries(
        self,
        entries,
    ):

        try:

            self.manifest_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            temp = self.manifest_path.with_suffix(
                ".tmp"
            )

            temp.write_text(
                json.dumps(
                    list(
                        entries
                        or []
                    ),
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            temp.replace(
                self.manifest_path
            )

        except Exception as error:

            print(
                "LYRx downloads manifest write error:",
                error
            )

    def downloaded_storage_bytes(
        self,
    ) -> int:

        total = 0

        for item in self.entries():

            path = Path(
                _safe_text(
                    item.get(
                        "file_path",
                        "",
                    )
                )
            )

            try:

                if path.is_file():

                    total += path.stat().st_size

            except Exception:

                pass

        return total

    def downloaded_storage_text(
        self,
    ) -> str:

        return _human_bytes(
            self.downloaded_storage_bytes()
        )

    # ========================================================
    # FILE NAME
    # ========================================================

    def _extension_from_url(
        self,
        url: str,
    ) -> str:

        try:

            path = unquote(
                urlparse(
                    url
                ).path
            )

            suffix = Path(
                path
            ).suffix.lower()

            if (
                suffix
                and
                1 < len(suffix) <= 6
                and
                suffix
                in (
                    ".mp3",
                    ".m4a",
                    ".aac",
                    ".ogg",
                    ".wav",
                    ".flac",
                )
            ):

                return suffix

        except Exception:

            pass

        return ".mp3"

    def _target_file(
        self,
        song,
        url: str,
    ) -> Path:

        title = _safe_filename(
            getattr(
                song,
                "title",
                "",
            )
            or "Track"
        )

        artist = _safe_filename(
            getattr(
                song,
                "artist",
                "",
            )
            or "Unknown Artist"
        )

        extension = self._extension_from_url(
            url
        )

        stem = _safe_filename(
            f"{artist} - {title}"
        )

        directory = self.download_dir()

        candidate = (
            directory
            / f"{stem}{extension}"
        )

        if not candidate.exists():

            return candidate

        index = 2

        while True:

            candidate = (
                directory
                / f"{stem} ({index}){extension}"
            )

            if not candidate.exists():

                return candidate

            index += 1

    # ========================================================
    # START DOWNLOAD
    # ========================================================

    def start_download(
        self,
        song,
    ) -> str:

        info = self.downloadable_info(
            song
        )

        if not info.get(
            "downloadable",
            False,
        ):

            self.download_failed.emit(
                "",
                info.get(
                    "reason",
                    "This track cannot be downloaded.",
                ),
            )

            return ""

        url = _safe_text(
            info.get(
                "url",
                "",
            )
        )

        target = self._target_file(
            song,
            url,
        )

        partial = target.with_suffix(
            target.suffix
            + ".part"
        )

        task_id = uuid4().hex

        file = QFile(
            str(
                partial
            )
        )

        if not file.open(
            QIODevice.WriteOnly
        ):

            self.download_failed.emit(
                task_id,
                "LYRx could not create the download file.",
            )

            return ""

        request = QNetworkRequest(
            QUrl(
                url
            )
        )

        request.setRawHeader(
            b"User-Agent",
            b"LYRx/0.1",
        )

        reply = self.network.get(
            request
        )

        title = _safe_text(
            getattr(
                song,
                "title",
                "",
            )
            or "Track"
        )

        task = {
            "id": task_id,
            "song": song,
            "reply": reply,
            "file": file,
            "target": target,
            "partial": partial,
            "provider": (
                info.get(
                    "provider",
                    "online",
                )
                or "online"
            ),
            "cancelled": False,
        }

        self.tasks[
            task_id
        ] = task

        reply.readyRead.connect(
            lambda task_id=task_id:
            self._write_ready(
                task_id
            )
        )

        reply.downloadProgress.connect(
            lambda received, total, task_id=task_id:
            self._progress(
                task_id,
                received,
                total,
            )
        )

        reply.finished.connect(
            lambda task_id=task_id:
            self._finished(
                task_id
            )
        )

        self.download_started.emit(
            task_id,
            title,
        )

        print(
            "LYRx download started:",
            title,
            url,
        )

        return task_id

    # ========================================================
    # NETWORK CALLBACKS
    # ========================================================

    def _write_ready(
        self,
        task_id: str,
    ):

        task = self.tasks.get(
            task_id
        )

        if not task:
            return

        reply = task.get(
            "reply"
        )

        file = task.get(
            "file"
        )

        if (
            reply is None
            or file is None
        ):
            return

        try:

            data = reply.readAll()

            if data:

                file.write(
                    data
                )

        except Exception as error:

            print(
                "LYRx download write error:",
                error
            )

    def _progress(
        self,
        task_id: str,
        received: int,
        total: int,
    ):

        percent = 0

        if total > 0:

            percent = max(
                0,
                min(
                    100,
                    int(
                        received
                        * 100
                        / total
                    ),
                ),
            )

        self.download_progress.emit(
            task_id,
            percent,
            int(
                received
            ),
            int(
                total
            ),
        )

    def _finished(
        self,
        task_id: str,
    ):

        task = self.tasks.pop(
            task_id,
            None,
        )

        if not task:
            return

        reply = task.get(
            "reply"
        )

        file = task.get(
            "file"
        )

        partial = Path(
            task.get(
                "partial"
            )
        )

        target = Path(
            task.get(
                "target"
            )
        )

        song = task.get(
            "song"
        )

        cancelled = bool(
            task.get(
                "cancelled",
                False,
            )
        )

        try:

            # Consume any bytes that arrived between readyRead and finished.
            if (
                reply is not None
                and
                file is not None
            ):

                remaining = reply.readAll()

                if remaining:

                    file.write(
                        remaining
                    )

        except Exception:

            pass

        try:

            if file is not None:

                file.flush()
                file.close()

        except Exception:

            pass

        if cancelled:

            try:

                partial.unlink(
                    missing_ok=True
                )

            except Exception:

                pass

            try:

                reply.deleteLater()

            except Exception:

                pass

            self.download_cancelled.emit(
                task_id
            )

            return

        network_error = (
            reply.error()
            if reply is not None
            else QNetworkReply.UnknownNetworkError
        )

        status_code = None

        try:

            status_code = reply.attribute(
                QNetworkRequest.HttpStatusCodeAttribute
            )

        except Exception:

            pass

        if (
            network_error
            != QNetworkReply.NoError
            or
            (
                status_code is not None
                and
                int(status_code) >= 400
            )
        ):

            message = (
                reply.errorString()
                if reply is not None
                else "Download failed."
            )

            try:

                partial.unlink(
                    missing_ok=True
                )

            except Exception:

                pass

            try:

                reply.deleteLater()

            except Exception:

                pass

            self.download_failed.emit(
                task_id,
                message,
            )

            return

        try:

            if not partial.is_file():

                raise RuntimeError(
                    "The downloaded file was not created."
                )

            if partial.stat().st_size <= 0:

                raise RuntimeError(
                    "The provider returned an empty file."
                )

            partial.replace(
                target
            )

        except Exception as error:

            try:

                partial.unlink(
                    missing_ok=True
                )

            except Exception:

                pass

            try:

                reply.deleteLater()

            except Exception:

                pass

            self.download_failed.emit(
                task_id,
                str(
                    error
                ),
            )

            return

        entry = {
            "id": uuid4().hex,
            "song_id": _safe_text(
                getattr(
                    song,
                    "id",
                    "",
                )
            ),
            "title": _safe_text(
                getattr(
                    song,
                    "title",
                    "",
                )
                or "Unknown Track"
            ),
            "artist": _safe_text(
                getattr(
                    song,
                    "artist",
                    "",
                )
                or "Unknown Artist"
            ),
            "album": _safe_text(
                getattr(
                    song,
                    "album",
                    "",
                )
            ),
            "provider": _safe_text(
                task.get(
                    "provider",
                    "online",
                )
            ),
            "image_url": _safe_text(
                getattr(
                    song,
                    "image_url",
                    "",
                )
                or getattr(
                    song,
                    "artwork_url",
                    "",
                )
            ),
            "file_path": str(
                target.resolve()
            ),
            "file_name": target.name,
            "size_bytes": (
                target.stat().st_size
                if target.is_file()
                else 0
            ),
            "downloaded_at": (
                datetime.now()
                .astimezone()
                .isoformat(
                    timespec="seconds"
                )
            ),
        }

        entries = self.entries()

        # Keep one manifest row per physical file.
        entries = [
            item
            for item in entries
            if _safe_text(
                item.get(
                    "file_path",
                    "",
                )
            )
            != entry[
                "file_path"
            ]
        ]

        entries.insert(
            0,
            entry,
        )

        self._save_entries(
            entries
        )

        try:

            reply.deleteLater()

        except Exception:

            pass

        self.download_finished.emit(
            task_id,
            entry,
        )

        self.library_changed.emit()

        print(
            "LYRx download complete:",
            target
        )

    # ========================================================
    # CANCEL
    # ========================================================

    def cancel_download(
        self,
        task_id: str,
    ) -> bool:

        task = self.tasks.get(
            _safe_text(
                task_id
            )
        )

        if not task:

            return False

        task[
            "cancelled"
        ] = True

        reply = task.get(
            "reply"
        )

        try:

            if reply is not None:
                reply.abort()

        except Exception:

            pass

        return True

    # ========================================================
    # LIBRARY ACTIONS
    # ========================================================

    def remove_entry(
        self,
        entry_id: str,
        delete_file: bool = True,
    ) -> bool:

        entry_id = _safe_text(
            entry_id
        )

        entries = self.entries()

        target = None

        remaining = []

        for item in entries:

            if _safe_text(
                item.get(
                    "id",
                    "",
                )
            ) == entry_id:

                target = item

            else:

                remaining.append(
                    item
                )

        if target is None:

            return False

        if delete_file:

            file_path = Path(
                _safe_text(
                    target.get(
                        "file_path",
                        "",
                    )
                )
            )

            try:

                if file_path.is_file():

                    file_path.unlink()

            except Exception as error:

                print(
                    "LYRx downloaded file remove error:",
                    error
                )

                return False

        self._save_entries(
            remaining
        )

        self.library_changed.emit()

        return True

    def prune_missing(
        self,
    ):

        entries = self.entries()

        existing = []

        for item in entries:

            path = Path(
                _safe_text(
                    item.get(
                        "file_path",
                        "",
                    )
                )
            )

            if path.is_file():

                existing.append(
                    item
                )

        if len(
            existing
        ) != len(
            entries
        ):

            self._save_entries(
                existing
            )

            self.library_changed.emit()

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def human_bytes(
        size: int,
    ) -> str:

        return _human_bytes(
            size
        )
