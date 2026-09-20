from pathlib import Path
import sys

from PySide6.QtCore import (
    Qt,
    QUrl,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    Signal,
    QRect,
)
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink


class _VideoFrameWidget(QWidget):
    """Lightweight raster video surface.

    Keeping the current frame as QImage avoids the per-frame QPixmap conversion
    and resize work that made the previous V3 implementation stutter on
    Windows. QPainter draws the decoded frame directly into the splash surface.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = QImage()
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAutoFillBackground(False)

    def set_image(self, image: QImage):
        if image.isNull():
            return
        self._image = image
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        if self._image.isNull():
            return

        target = self.rect()
        source_ratio = self._image.width() / max(1, self._image.height())
        target_ratio = target.width() / max(1, target.height())

        # Cover the complete screen while preserving the 16:9 intro framing.
        if source_ratio > target_ratio:
            draw_h = target.height()
            draw_w = int(draw_h * source_ratio)
        else:
            draw_w = target.width()
            draw_h = int(draw_w / source_ratio)

        x = (target.width() - draw_w) // 2
        y = (target.height() - draw_h) // 2
        painter.drawImage(QRect(x, y, draw_w, draw_h), self._image)


class SplashScreen(QWidget):
    """LYRx cinematic intro with a low-overhead QVideoSink renderer."""

    finished = Signal()

    VIDEO_RELATIVE_PATH = Path("assets") / "splash" / "lyrx_intro.mp4"
    FIRST_FRAME_RELATIVE_PATH = Path("assets") / "splash" / "lyrx_intro_first.png"
    LAST_FRAME_RELATIVE_PATH = Path("assets") / "splash" / "lyrx_intro_last.png"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._closing = False
        self._video_started = False
        self._video_path = self._resolve_asset(self.VIDEO_RELATIVE_PATH)
        self._first_frame_path = self._resolve_asset(self.FIRST_FRAME_RELATIVE_PATH)
        self._last_frame_path = self._resolve_asset(self.LAST_FRAME_RELATIVE_PATH)

        self.setObjectName("LYRxSplash")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._build_ui()
        self._build_player()

    def _resolve_asset(self, relative_path: Path) -> Path:
        candidates = []
        cwd = Path.cwd()
        candidates.append(cwd / relative_path)

        src_dir = Path(__file__).resolve().parents[2]
        project_root = src_dir.parent
        candidates.append(project_root / relative_path)

        bundled_root = Path(getattr(sys, "_MEIPASS", project_root))
        candidates.append(bundled_root / relative_path)

        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()
        return candidates[1].resolve()

    def _build_ui(self):
        self.video_surface = _VideoFrameWidget(self)
        self.video_surface.setGeometry(self.rect())

        # The supplied LYRx frame is displayed immediately, before FFmpeg has
        # decoded anything. This removes the startup black flash.
        first = QImage(str(self._first_frame_path))
        if not first.isNull():
            self.video_surface.set_image(first)
        else:
            self.video_surface.set_image(QImage(1280, 720, QImage.Format.Format_RGB32))

        self._last_image = QImage(str(self._last_frame_path))

    def _build_player(self):
        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(1.0)

        self.video_sink = QVideoSink(self)
        self.video_sink.videoFrameChanged.connect(self._on_video_frame)

        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoSink(self.video_sink)
        self.player.mediaStatusChanged.connect(self._on_media_status)
        self.player.errorOccurred.connect(self._on_error)
        self.player.setSource(QUrl.fromLocalFile(str(self._video_path)))

    def start(self):
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

        if not self._video_path.is_file():
            QTimer.singleShot(50, self._finish)
            return

        # Give the first-frame surface one paint pass before media decoding.
        QTimer.singleShot(30, self._start_media)

    def _start_media(self):
        if self._closing:
            return
        self.player.play()

    def _on_video_frame(self, frame):
        if self._closing or not frame.isValid():
            return

        image = frame.toImage()
        if image.isNull():
            return

        self._video_started = True
        # Do not convert to QPixmap and resize on every frame. The custom
        # raster widget paints this QImage directly, which is much lighter.
        self.video_surface.set_image(image)

    def _on_media_status(self, status):
        if self._closing:
            return

        if status == QMediaPlayer.MediaStatus.InvalidMedia:
            self._finish()
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._finish()

    def _on_error(self, error, error_string):
        if self._closing:
            return
        if error != QMediaPlayer.Error.NoError:
            print(f"LYRx splash video error: {error_string}")
            self._finish()

    def _finish(self):
        if self._closing:
            return
        self._closing = True

        self.player.stop()

        # Hold the exact final PNG while the already-rendered main window is
        # revealed underneath. This avoids a decoder-to-window handoff frame.
        if not self._last_image.isNull():
            self.video_surface.set_image(self._last_image)

        self.finished.emit()

        effect = QGraphicsOpacityEffect(self.video_surface)
        effect.setOpacity(1.0)
        self.video_surface.setGraphicsEffect(effect)
        self._fade_effect = effect

        self._fade_animation = QPropertyAnimation(effect, b"opacity", self)
        self._fade_animation.setDuration(420)
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._fade_animation.finished.connect(self.close)
        self._fade_animation.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.video_surface.setGeometry(self.rect())
        self.video_surface.update()

    def closeEvent(self, event):
        self._closing = True
        try:
            self.player.stop()
        except Exception:
            pass
        super().closeEvent(event)
