from pathlib import Path

from PySide6.QtCore import Qt, Signal, QUrl, QTimer, QRectF

from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
)

from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QBrush, QFont, QDesktopServices
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from core.language_manager import language_manager
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSlider, QScrollArea, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)


# ============================================================
# PATHS
# ============================================================

FILE_DIR = Path(__file__).resolve()
PROJECT_DIR = FILE_DIR.parents[3]
SRC_DIR = FILE_DIR.parents[2]


# ============================================================
# ASSET HELPER
# ============================================================

def find_asset(relative_path):
    candidates = [
        PROJECT_DIR / relative_path,
        SRC_DIR / relative_path,
        Path.cwd() / relative_path,
        Path(relative_path),
    ]

    for path in candidates:
        try:
            if path.exists() and path.is_file():
                return path
        except Exception:
            pass

    return None


# ============================================================
# TIME FORMATTER
# ============================================================

def format_duration(milliseconds):
    if milliseconds is None or milliseconds <= 0:
        return "0:00"

    total_seconds = milliseconds // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


# ============================================================
# NEXT SONG DURATION PROBE
# ============================================================

class DurationProbe:

    def __init__(self, parent):
        self.parent = parent
        self.players = []

    def load(self, audio_file, callback):
        player = QMediaPlayer(self.parent)

        player.durationChanged.connect(
            lambda duration, p=player, cb=callback: self.handle_duration(
                p, duration, cb
            )
        )

        player.setSource(
            QUrl.fromLocalFile(str(audio_file.resolve()))
        )

        self.players.append(player)

    def handle_duration(self, player, duration, callback):
        if duration <= 0:
            return

        # The Next Up widget can be rebuilt before this metadata callback
        # arrives. Never let a stale QLabel crash the application.
        try:
            callback(format_duration(duration))
        except RuntimeError:
            pass
        except Exception:
            pass

        # The metadata has been read; this probe no longer needs to stay alive.
        try:
            self.players.remove(player)
        except ValueError:
            pass

        try:
            player.stop()
            player.deleteLater()
        except RuntimeError:
            pass



# ============================================================
# DAY 27 - PREMIUM PLAYER CONTROLS
# ============================================================

class PlayerControlButton(QPushButton):
    """Blueprint-style circular control with a crisp vector-painted icon."""

    def __init__(self, kind, size=42, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.active = False
        self.hovered = False
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def set_active(self, active):
        self.active = bool(active)
        self.update()

    def enterEvent(self, event):
        self.hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        r = QRectF(2.5, 2.5, self.width() - 5, self.height() - 5)

        if self.active:
            bg = QColor(111, 57, 190, 118)
            border = QColor(173, 111, 255, 210)
            icon = QColor("#F3E9FF")
        elif self.hovered:
            bg = QColor(139, 92, 246, 40)
            border = QColor(139, 92, 246, 110)
            icon = QColor("#FFFFFF")
        else:
            bg = QColor(24, 16, 42, 125)
            border = QColor(111, 83, 151, 105)
            icon = QColor("#D8CCF5")

        painter.setPen(QPen(border, 1.0))
        painter.setBrush(QBrush(bg))
        painter.drawEllipse(r)

        pen = QPen(icon, 2.0)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QBrush(icon))

        cx = self.width() / 2
        cy = self.height() / 2

        if self.kind == "previous":
            painter.drawLine(cx - 8, cy - 8, cx - 8, cy + 8)
            path = QPainterPath()
            path.moveTo(cx + 7, cy - 9)
            path.lineTo(cx - 5, cy)
            path.lineTo(cx + 7, cy + 9)
            path.closeSubpath()
            painter.drawPath(path)

        elif self.kind == "next":
            painter.drawLine(cx + 8, cy - 8, cx + 8, cy + 8)
            path = QPainterPath()
            path.moveTo(cx - 7, cy - 9)
            path.lineTo(cx + 5, cy)
            path.lineTo(cx - 7, cy + 9)
            path.closeSubpath()
            painter.drawPath(path)

        elif self.kind == "shuffle":
            # Two clean crossing paths + arrow heads.
            p1 = QPainterPath()
            p1.moveTo(cx - 10, cy - 7)
            p1.cubicTo(cx - 2, cy - 7, cx + 1, cy + 7, cx + 9, cy + 7)
            painter.drawPath(p1)
            painter.drawLine(cx + 5, cy + 3, cx + 10, cy + 7)
            painter.drawLine(cx + 5, cy + 11, cx + 10, cy + 7)

            p2 = QPainterPath()
            p2.moveTo(cx - 10, cy + 7)
            p2.cubicTo(cx - 2, cy + 7, cx + 1, cy - 7, cx + 9, cy - 7)
            painter.drawPath(p2)
            painter.drawLine(cx + 5, cy - 11, cx + 10, cy - 7)
            painter.drawLine(cx + 5, cy - 3, cx + 10, cy - 7)

        elif self.kind == "repeat":
            p1 = QPainterPath()
            p1.moveTo(cx - 9, cy - 5)
            p1.cubicTo(cx - 4, cy - 11, cx + 6, cy - 10, cx + 9, cy - 4)
            painter.drawPath(p1)
            painter.drawLine(cx + 5, cy - 7, cx + 10, cy - 4)
            painter.drawLine(cx + 8, cy + 1, cx + 10, cy - 4)

            p2 = QPainterPath()
            p2.moveTo(cx + 9, cy + 5)
            p2.cubicTo(cx + 4, cy + 11, cx - 6, cy + 10, cx - 9, cy + 4)
            painter.drawPath(p2)
            painter.drawLine(cx - 5, cy + 7, cx - 10, cy + 4)
            painter.drawLine(cx - 8, cy - 1, cx - 10, cy + 4)




class MiniEqualizer(QWidget):
    """Subtle LYRx equalizer: animates only while playback is active."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self._phase = 0
        self._playing = False
        self._timer = QTimer(self)
        self._timer.setInterval(115)
        self._timer.timeout.connect(self._tick)

    def set_playing(self, playing):
        self._playing = bool(playing)
        if self._playing:
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def _tick(self):
        self._phase = (self._phase + 1) % 8
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        values = (8, 15, 22, 13, 19)
        for i, base in enumerate(values):
            if self._playing:
                height = 7 + ((base + self._phase * (i + 2)) % 18)
            else:
                height = 7 + (i % 3) * 3
            x = 3 + i * 5
            y = (self.height() - height) / 2
            gradient = QLinearGradient(0, y, 0, y + height)
            gradient.setColorAt(0, QColor("#E879F9"))
            gradient.setColorAt(1, QColor("#7C3AED"))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(QRectF(x, y, 3, height), 1.5, 1.5)


class LabeledPlayerControl(QWidget):
    """A premium circular player control with a small caption."""

    clicked = Signal()

    def __init__(self, kind, caption, size=44, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        self.button = PlayerControlButton(kind, size, self)
        self.caption = QLabel(caption)
        self.caption.setAlignment(Qt.AlignCenter)
        self.caption.setStyleSheet("""
            QLabel {
                color: #9F93BE;
                font-size: 10px;
                background: transparent;
            }
        """)

        layout.addWidget(self.button, 0, Qt.AlignCenter)
        layout.addWidget(self.caption)
        self.button.clicked.connect(self.clicked.emit)

    def set_active(self, active):
        self.button.set_active(active)
        self.caption.setStyleSheet("""
            QLabel {
                color: %s;
                font-size: 10px;
                font-weight: %s;
                background: transparent;
            }
        """ % ("#CDA8FF" if active else "#9F93BE",
               "700" if active else "400"))

    def setToolTip(self, text):
        super().setToolTip(text)
        self.button.setToolTip(text)


class GlowPlayButton(QPushButton):
    """Large blueprint-style Play/Pause button with a neon purple glow."""

    def __init__(self, size=62, parent=None):
        super().__init__(parent)
        self.playing = False
        self.hovered = False
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(30)
        glow.setOffset(0, 0)
        glow.setColor(QColor(150, 75, 255, 205))
        self.setGraphicsEffect(glow)

    def set_playing(self, playing):
        self.playing = bool(playing)
        self.update()

    # Compatibility with the existing player code, which historically
    # changed the play button with setText("▶"/"Ⅱ").
    def setText(self, text):
        self.set_playing(str(text).strip() in {"Ⅱ", "II", "❚❚", "⏸"})

    def enterEvent(self, event):
        self.hovered = True
        effect = self.graphicsEffect()
        if effect:
            effect.setBlurRadius(38)
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        effect = self.graphicsEffect()
        if effect:
            effect.setBlurRadius(30)
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(5, 5, self.width() - 10, self.height() - 10)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor("#B76CFF") if self.hovered else QColor("#9B5CF6"))
        gradient.setColorAt(0.55, QColor("#7C3AED"))
        gradient.setColorAt(1.0, QColor("#5B21B6"))

        painter.setPen(QPen(QColor(220, 190, 255, 225), 1.7))
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(rect)

        # Inner glossy highlight.
        highlight = QPen(QColor(255, 255, 255, 82), 1.0)
        painter.setPen(highlight)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(QRectF(9, 9, self.width() - 18, self.height() - 18), 35 * 16, 110 * 16)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FFFFFF"))

        cx = self.width() / 2
        cy = self.height() / 2

        if self.playing:
            painter.drawRoundedRect(QRectF(cx - 8, cy - 10, 5, 20), 2, 2)
            painter.drawRoundedRect(QRectF(cx + 3, cy - 10, 5, 20), 2, 2)
        else:
            path = QPainterPath()
            path.moveTo(cx - 6, cy - 11)
            path.lineTo(cx + 11, cy)
            path.lineTo(cx - 6, cy + 11)
            path.closeSubpath()
            painter.drawPath(path)


# ============================================================
# NOW PLAYING
# ============================================================

class NowPlaying(QWidget):

    next_requested = Signal()
    previous_requested = Signal()
    next_song_requested = Signal(str, str, str)
    song_finished = Signal()

    # Signals used by AppWindow to keep the floating player in sync.
    song_changed = Signal(str, str, str)
    play_state_changed = Signal(bool)
    progress_changed = Signal(int, str, str)

    # DAY 19 - sends the already-decoded album cover to other UI players.
    cover_pixmap_changed = Signal(object)

    def __init__(self):
        super().__init__()

        self.setObjectName("NowPlaying")
        self.setMinimumWidth(340)
        self.setMaximumWidth(390)
        self.setMinimumHeight(620)

        # ========================================================
        # PLAYER STATE
        # ========================================================

        self.is_playing = False
        self.is_shuffle = False
        self.is_repeat = False

        # ========================================================
        # DAY 25 - PLAYBACK SETTINGS
        # ========================================================

        self.autoplay_enabled = True
        self.gapless_enabled = True
        self.normalize_volume_enabled = True

        # DAY 25 - ONLINE AUDIO / DATA SAVER SETTINGS
        self.streaming_quality_preference = "Automatic"
        self.data_saver_enabled = False

        self.crossfade_seconds = 0

        # User-selected output level. Crossfade transitions temporarily
        # change QAudioOutput volume and then restore this value.
        self.user_volume = 0.75

        self._fade_mode = None
        self._fade_step = 0
        self._fade_total_steps = 1
        self._fade_started_for_track = False
        self._fade_in_pending = False
        self._transition_in_progress = False

        self.current_image_path = ""
        self.current_title = ""
        self.current_artist = ""

        self.queue = []
        self.queue_index = 0

        # ========================================================
        # DAY 19 - ONLINE QUEUE STATE
        # ========================================================

        self.online_queue = []

        self.online_queue_index = 0

        self.playback_source = "local"
        if hasattr(self, "quality_badge"):
            self.quality_badge.setText("♫  Local Audio  •  Offline")

        self.current_online_song = None

        # ========================================================
        # DAY 19 - ONLINE STREAM SAFETY
        # ========================================================

        # Some remote Jamendo streams can take a moment before the
        # Qt multimedia backend is ready. Keep enough state to retry
        # the same stream once without breaking the queue/UI.
        self.online_stream_url = ""
        self.online_autoplay_pending = False
        self.online_retry_count = 0
        self.online_retry_limit = 1
        self.current_online_duration_seconds = 0

        # ========================================================
        # AUDIO PLAYER
        # ========================================================

        self.audio_player = QMediaPlayer(self)
        self.audio_player.playbackStateChanged.connect(
            self._sync_premium_animation_state
        )
        self.audio_output = QAudioOutput(self)
        self.audio_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(self.user_volume)

        # DAY 25 - one lightweight timer handles fade-out/fade-in.
        # This gives LYRx a smooth crossfade-style transition while
        # keeping the existing single QMediaPlayer architecture intact.
        self.fade_timer = QTimer(self)
        self.fade_timer.setInterval(40)
        self.fade_timer.timeout.connect(
            self._process_fade_step
        )

        # ========================================================
        # ONLINE COVER ART NETWORK MANAGER
        # ========================================================

        self.cover_network = QNetworkAccessManager(
            self
        )

        self.cover_reply = None

        # Multiple remote Next Up thumbnails can load at the same time.
        self.thumbnail_replies = []

        # ========================================================
        # DURATION PROBE
        # ========================================================

        self.duration_probe = DurationProbe(self)

        # ========================================================
        # PLAYER SIGNALS
        # ========================================================

        self.audio_player.positionChanged.connect(self.update_progress)
        self.audio_player.durationChanged.connect(self.update_duration)
        self.audio_player.mediaStatusChanged.connect(self.handle_media_status)
        self.audio_player.playbackStateChanged.connect(
            self.handle_playback_state
        )
        self.audio_player.errorOccurred.connect(
            self.handle_player_error
        )

        self.build_ui()

        self.slider.sliderMoved.connect(self.seek_audio)
        self.volume_slider.valueChanged.connect(self.change_volume)

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)

        # ====================================================
        # BLUEPRINT HEADER
        # ====================================================
        header = QHBoxLayout()
        header.setSpacing(8)

        self.header_equalizer = MiniEqualizer(self)
        header.addWidget(self.header_equalizer)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)

        self.now_playing_heading = QLabel("NOW PLAYING")
        self.now_playing_heading.setStyleSheet("""
            QLabel {
                color: #F2ECFF;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 1px;
                background: transparent;
            }
        """)

        subtitle = QLabel("")
        subtitle.setStyleSheet("""
            QLabel {
                color: #8E82AE;
                font-size: 10px;
                background: transparent;
            }
        """)

        title_box.addWidget(self.now_playing_heading)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self.live_badge = QLabel("●  LIVE")
        self.live_badge.setAlignment(Qt.AlignCenter)
        self.live_badge.setStyleSheet("""
            QLabel {
                color: #C77DFF;
                font-size: 10px;
                font-weight: 800;
                background: rgba(126, 34, 206, 42);
                border: 1px solid rgba(168, 85, 247, 60);
                border-radius: 12px;
                padding: 5px 9px;
            }
        """)
        header.addWidget(self.live_badge)
        root.addLayout(header)

        # ====================================================
        # ALBUM ART - BLUEPRINT FRAME + SOFT GLOW
        # ====================================================
        self.album_frame = QFrame()
        self.album_frame.setFixedSize(212, 212)
        self.album_frame.setObjectName("AlbumFrame")
        self.album_frame.setStyleSheet("""
            QFrame#AlbumFrame {
                background: #171126;
                border: 1px solid #7C3AED;
                border-radius: 18px;
            }
        """)

        album_glow = QGraphicsDropShadowEffect(self.album_frame)
        album_glow.setBlurRadius(22)
        album_glow.setOffset(0, 0)
        album_glow.setColor(QColor(124, 58, 237, 80))
        self.album_frame.setGraphicsEffect(album_glow)

        album_layout = QVBoxLayout(self.album_frame)
        album_layout.setContentsMargins(3, 3, 3, 3)
        album_layout.setSpacing(0)

        self.album = QLabel()
        self.album.setFixedSize(206, 206)
        self.album.setAlignment(Qt.AlignCenter)
        self.album.setStyleSheet("""
            QLabel {
                background: #171126;
                border-radius: 15px;
            }
        """)

        default_art = find_asset("assets/album_art/believer.jpg")
        if default_art:
            pix = QPixmap(str(default_art))
            if not pix.isNull():
                scaled_local_cover = pix.scaled(
                    206, 206,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                self.album.setPixmap(scaled_local_cover)
                self.cover_pixmap_changed.emit(scaled_local_cover)

        album_layout.addWidget(self.album)
        root.addWidget(self.album_frame, 0, Qt.AlignHCenter)
        root.addSpacing(8)

        # ====================================================
        # SONG INFO
        # ====================================================
        self.song = QLabel("Believer")
        self.song.setAlignment(Qt.AlignCenter)
        self.song.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20px;
                font-weight: 800;
                background: transparent;
            }
        """)
        root.addWidget(self.song)

        self.artist = QLabel("Imagine Dragons")
        self.artist.setAlignment(Qt.AlignCenter)
        self.artist.setStyleSheet("""
            QLabel {
                color: #B8A9DC;
                font-size: 12px;
                background: transparent;
            }
        """)
        root.addWidget(self.artist)

        self.quality_badge = QLabel("♫  Online Audio")
        self.quality_badge.setAlignment(Qt.AlignCenter)
        self.quality_badge.setStyleSheet("""
            QLabel {
                color: #C084FC;
                font-size: 10px;
                font-weight: 700;
                background: rgba(126, 34, 206, 35);
                border: 1px solid rgba(168, 85, 247, 75);
                border-radius: 11px;
                padding: 4px 10px;
            }
        """)
        root.addWidget(self.quality_badge, 0, Qt.AlignHCenter)

        # ====================================================
        # PROGRESS + TIME
        # ====================================================
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(1, 0, 1, 0)

        self.current_time = QLabel("0:00")
        self.total_time = QLabel("0:00")

        for label in (self.current_time, self.total_time):
            label.setStyleSheet("""
                QLabel {
                    color: #A99BC9;
                    font-size: 10px;
                    background: transparent;
                }
            """)

        time_layout.addWidget(self.current_time)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time)
        root.addLayout(time_layout)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setFixedHeight(16)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 5px;
                background: #302747;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C3AED,
                    stop:0.55 #A855F7,
                    stop:1 #E879F9
                );
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 13px;
                height: 13px;
                margin: -4px 0;
                border-radius: 6px;
                background: white;
                border: 1px solid #E9D5FF;
            }
        """)
        root.addWidget(self.slider)

        # ====================================================
        # PREMIUM LABELED CONTROLS
        # ====================================================
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 1, 0, 1)
        controls.setSpacing(4)
        controls.setAlignment(Qt.AlignCenter)

        self.shuffle_btn = LabeledPlayerControl("shuffle", "Shuffle", 40, self)
        self.prev_btn = LabeledPlayerControl("previous", "Previous", 42, self)

        play_wrap = QWidget()
        play_layout = QVBoxLayout(play_wrap)
        play_layout.setContentsMargins(0, 0, 0, 0)
        play_layout.setSpacing(2)
        play_layout.setAlignment(Qt.AlignCenter)

        self.play_btn = GlowPlayButton(64, self)

        # Soft breathing glow. It is intentionally subtle and does not
        # interfere with playback state or button clicks.
        self._play_glow_growing = True
        self._play_glow_timer = QTimer(self)
        self._play_glow_timer.setInterval(90)
        self._play_glow_timer.timeout.connect(self._animate_play_glow)
        self.play_caption = QLabel("Pause")
        self.play_caption.setAlignment(Qt.AlignCenter)
        self.play_caption.setStyleSheet("""
            QLabel {
                color: #CDBEFF;
                font-size: 9px;
                font-weight: 700;
                background: transparent;
            }
        """)
        play_layout.addWidget(self.play_btn, 0, Qt.AlignCenter)
        play_layout.addWidget(self.play_caption)

        self.next_btn = LabeledPlayerControl("next", "Next", 42, self)
        self.repeat_btn = LabeledPlayerControl("repeat", "Repeat", 40, self)

        controls.addWidget(self.shuffle_btn)
        controls.addWidget(self.prev_btn)
        controls.addWidget(play_wrap)
        controls.addWidget(self.next_btn)
        controls.addWidget(self.repeat_btn)
        root.addLayout(controls)

        self.play_btn.clicked.connect(self.toggle_play)
        self.prev_btn.clicked.connect(self.previous_requested.emit)
        self.next_btn.clicked.connect(self.next_requested.emit)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.repeat_btn.clicked.connect(self.toggle_repeat)

        # ====================================================
        # VOLUME
        # ====================================================
        volume_layout = QHBoxLayout()
        volume_layout.setContentsMargins(3, 0, 3, 0)
        volume_layout.setSpacing(8)

        volume_icon = QLabel("♪")
        volume_icon.setFixedWidth(18)
        volume_icon.setAlignment(Qt.AlignCenter)
        volume_icon.setStyleSheet("""
            QLabel {
                color: #D8CCF5;
                font-size: 15px;
                font-weight: 800;
                background: transparent;
            }
        """)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #302747;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C3AED,
                    stop:1 #C084FC
                );
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 11px;
                height: 11px;
                margin: -4px 0;
                border-radius: 5px;
                background: #F3E8FF;
            }
        """)

        self.volume_value = QLabel("75%")
        self.volume_value.setFixedWidth(30)
        self.volume_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.volume_value.setStyleSheet("""
            QLabel {
                color: #A99BC9;
                font-size: 9px;
                background: transparent;
            }
        """)
        self.volume_slider.valueChanged.connect(
            lambda value: self.volume_value.setText(f"{value}%")
        )

        volume_layout.addWidget(volume_icon)
        volume_layout.addWidget(self.volume_slider, 1)
        volume_layout.addWidget(self.volume_value)
        root.addLayout(volume_layout)

        # ====================================================
        # QUICK ACTIONS
        # ====================================================
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 3, 0, 3)
        actions.setSpacing(6)

        self.queue_action_btn = QPushButton("☷  Queue")
        self.playlist_action_btn = QPushButton("♫  Playlist")
        self.share_action_btn = QPushButton("↗  Share")
        self.more_action_btn = QPushButton("•••")

        for action_btn in (
            self.queue_action_btn,
            self.playlist_action_btn,
            self.share_action_btn,
            self.more_action_btn,
        ):
            action_btn.setCursor(Qt.PointingHandCursor)
            action_btn.setMinimumHeight(34)
            action_btn.setStyleSheet("""
                QPushButton {
                    color: #BFB2DB;
                    background: rgba(45, 32, 69, 150);
                    border: 1px solid rgba(139, 92, 246, 65);
                    border-radius: 10px;
                    padding: 5px 7px;
                    font-size: 9px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    color: #FFFFFF;
                    background: rgba(124, 58, 237, 65);
                    border: 1px solid rgba(192, 132, 252, 130);
                }
                QPushButton:pressed {
                    background: rgba(109, 40, 217, 95);
                }
            """)

        self.queue_action_btn.clicked.connect(self._request_add_to_queue)
        self.playlist_action_btn.clicked.connect(self._request_add_to_playlist)
        self.share_action_btn.clicked.connect(self._share_current_song)
        self.more_action_btn.clicked.connect(self._show_more_hint)

        actions.addWidget(self.queue_action_btn, 1)
        actions.addWidget(self.playlist_action_btn, 1)
        actions.addWidget(self.share_action_btn, 1)
        actions.addWidget(self.more_action_btn, 0)

        root.addLayout(actions)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(
            "QFrame { background: rgba(151, 105, 255, 45); }"
        )
        root.addWidget(divider)

        # ====================================================
        # NEXT UP
        # ====================================================
        next_header = QHBoxLayout()
        next_header.setContentsMargins(1, 0, 1, 0)

        self.next_up_title = QLabel("☷  NEXT UP")
        self.next_up_title.setStyleSheet("""
            QLabel {
                color: #E0D5FF;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        next_header.addWidget(self.next_up_title)
        next_header.addStretch()

        self.queue_count = QLabel("0 songs")
        self.queue_count.setStyleSheet("""
            QLabel {
                color: #8E82AE;
                font-size: 9px;
                background: transparent;
            }
        """)
        next_header.addWidget(self.queue_count)
        root.addLayout(next_header)

        self.next_scroll = QScrollArea()
        self.next_scroll.setWidgetResizable(True)
        self.next_scroll.setFrameShape(QFrame.NoFrame)
        self.next_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.next_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.next_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                width: 5px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #6D45B7;
                border-radius: 2px;
                min-height: 28px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        next_content = QWidget()
        next_content.setStyleSheet("QWidget { background: transparent; }")

        next_layout = QVBoxLayout(next_content)
        next_layout.setContentsMargins(0, 0, 3, 3)
        next_layout.setSpacing(6)
        next_layout.addStretch()

        self.next_scroll.setWidget(next_content)
        self.next_scroll.setMinimumHeight(105)
        self.next_scroll.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        root.addWidget(self.next_scroll, 1)

        # Day 27: Now Playing participates in the same live EN/HI/FR
        # language system as the rest of LYRx.
        language_manager.language_changed.connect(
            self.retranslate_ui
        )
        self.retranslate_ui()

    # ========================================================
    # DAY 27 - NOW PLAYING LIVE LANGUAGE
    # ========================================================

    def _tr_literal(self, english_text):
        return language_manager.translate_literal(
            english_text
        )

    def _translated_queue_count(self, count):
        try:
            count = int(count)
        except (TypeError, ValueError):
            count = 0

        if language_manager.language == "hi":
            return (
                "1 गाना"
                if count == 1
                else f"{count} गाने"
            )

        if language_manager.language == "fr":
            return (
                "1 morceau"
                if count == 1
                else f"{count} morceaux"
            )

        return (
            "1 song"
            if count == 1
            else f"{count} songs"
        )

    def retranslate_ui(self, *_):
        """Refresh all static and dynamic Now Playing chrome live."""
        if hasattr(self, "now_playing_heading"):
            self.now_playing_heading.setText(
                self._tr_literal("NOW PLAYING")
            )

        if hasattr(self, "live_badge"):
            self.live_badge.setText(
                self._tr_literal("●  LIVE")
            )

        if hasattr(self, "quality_badge"):
            online = (
                self.playback_source == "online"
                or self.current_online_song is not None
            )
            self.quality_badge.setText(
                self._tr_literal(
                    "♫  Online Audio"
                    if online
                    else "♫  Local Audio  •  Offline"
                )
            )

        captions = (
            ("shuffle_btn", "Shuffle"),
            ("prev_btn", "Previous"),
            ("next_btn", "Next"),
            ("repeat_btn", "Repeat"),
        )

        for attr_name, source_text in captions:
            control = getattr(self, attr_name, None)
            if control is not None and hasattr(control, "caption"):
                control.caption.setText(
                    self._tr_literal(source_text)
                )

        if hasattr(self, "play_caption"):
            playing = (
                getattr(self, "audio_player", None) is not None
                and self.audio_player.playbackState()
                == QMediaPlayer.PlaybackState.PlayingState
            )
            self.play_caption.setText(
                self._tr_literal(
                    "Pause" if playing else "Play"
                )
            )

        actions = (
            ("queue_action_btn", "☷  Queue"),
            ("playlist_action_btn", "♫  Playlist"),
            ("share_action_btn", "↗  Share"),
            ("more_action_btn", "•••"),
        )

        for attr_name, source_text in actions:
            button = getattr(self, attr_name, None)
            if button is not None:
                button.setText(
                    self._tr_literal(source_text)
                )

        if hasattr(self, "next_up_title"):
            self.next_up_title.setText(
                self._tr_literal("☷  NEXT UP")
            )

        if hasattr(self, "queue_count"):
            count = len(
                getattr(self, "online_queue", [])
                or []
            )
            self.queue_count.setText(
                self._translated_queue_count(count)
            )

    # ========================================================
    # DAY 27 - PREMIUM MICRO INTERACTIONS / ACTIONS
    # ========================================================

    def _sync_premium_animation_state(self, state):
        """Sync premium animations with the real audio playback state."""
        playing = (
            state == QMediaPlayer.PlaybackState.PlayingState
        )

        if hasattr(self, "header_equalizer"):
            self.header_equalizer.set_playing(playing)

        if hasattr(self, "play_btn"):
            self.play_btn.set_playing(playing)

        if hasattr(self, "play_caption"):
            self.play_caption.setText(
                self._tr_literal(
                    "Pause" if playing else "Play"
                )
            )

        if hasattr(self, "_play_glow_timer"):
            if playing:
                if not self._play_glow_timer.isActive():
                    self._play_glow_timer.start()
            else:
                self._play_glow_timer.stop()

                if hasattr(self, "play_btn"):
                    effect = self.play_btn.graphicsEffect()
                    if effect is not None:
                        effect.setBlurRadius(24.0)

    def _animate_play_glow(self):
        """Softly pulse the Play/Pause glow without changing playback."""
        if not hasattr(self, "play_btn"):
            return

        effect = self.play_btn.graphicsEffect()
        if effect is None:
            return

        player = getattr(self, "audio_player", None)
        if player is None:
            return

        is_playing = (
            player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        )

        # Glow must be static while paused/stopped.
        if not is_playing:
            effect.setBlurRadius(24.0)
            return

        low, high = (24.0, 38.0)
        current = float(effect.blurRadius())

        if getattr(self, "_play_glow_growing", True):
            current += 1.4
            if current >= high:
                current = high
                self._play_glow_growing = False
        else:
            current -= 1.4
            if current <= low:
                current = low
                self._play_glow_growing = True

        effect.setBlurRadius(current)

    def _current_share_url(self):
        song = self.current_online_song
        if song is None:
            return ""

        for name in ("share_url", "shareurl", "web_url", "url"):
            value = self._song_value(song, name)
            if value:
                return str(value).strip()

        metadata = getattr(song, "metadata", None)
        if isinstance(metadata, dict):
            for name in ("share_url", "shareurl", "web_url", "url"):
                value = metadata.get(name)
                if value:
                    return str(value).strip()

        return ""

    def _request_add_to_queue(self):
        if self.current_online_song is None:
            self.queue_action_btn.setToolTip("No online song selected")
            return

        self.add_current_to_queue_requested.emit(
            self.current_online_song
        )
        self.queue_action_btn.setToolTip("Queue request sent")

    def _request_add_to_playlist(self):
        if self.current_online_song is None:
            self.playlist_action_btn.setToolTip("No online song selected")
            return

        self.add_current_to_playlist_requested.emit(
            self.current_online_song
        )
        self.playlist_action_btn.setToolTip("Playlist request sent")

    def _share_current_song(self):
        url = self._current_share_url()

        if not url:
            self.share_action_btn.setToolTip(
                "This source does not provide a share link"
            )
            return

        QDesktopServices.openUrl(
            QUrl(url)
        )

    def _show_more_hint(self):
        # Intentionally no fake menu. Provider/app actions can be
        # connected here later when real actions are available.
        self.more_action_btn.setToolTip(
            "More track actions will appear here as providers support them"
        )

    # ========================================================
    # SET QUEUE
    # ========================================================

    def set_queue(self, queue):
        self.queue = list(queue)
        self.refresh_next_up()

    # ========================================================
    # SET ONLINE QUEUE
    # ========================================================

    def set_online_queue(
        self,
        songs,
        current_song=None
    ):

        self.online_queue = list(
            songs or []
        )

        # ----------------------------------------------------
        # EMPTY
        # ----------------------------------------------------

        if not self.online_queue:

            self.online_queue_index = 0

            return

        # ----------------------------------------------------
        # FIND CURRENT SONG
        # ----------------------------------------------------

        if current_song is not None:

            current_id = str(
                getattr(
                    current_song,
                    "id",
                    ""
                )
            )

            found_index = None

            for index, song in enumerate(
                self.online_queue
            ):

                song_id = str(
                    getattr(
                        song,
                        "id",
                        ""
                    )
                )

                if (
                    current_id
                    and song_id
                    and current_id == song_id
                ):

                    found_index = index

                    break

            if found_index is not None:

                self.online_queue_index = (
                    found_index
                )

        self.playback_source = "online"

        self.refresh_next_up()


    # ========================================================
    # SET ONLINE INDEX
    # ========================================================

    def set_online_index(
        self,
        index
    ):

        if not self.online_queue:

            self.online_queue_index = 0

            return

        index = max(
            0,
            min(
                int(index),
                len(self.online_queue) - 1
            )
        )

        self.online_queue_index = index

        self.refresh_next_up()


    # ========================================================
    # ONLINE NEXT
    # ========================================================

    def play_online_next(self):

        if not self.online_queue:

            return

        total = len(
            self.online_queue
        )

        # ----------------------------------------------------
        # SHUFFLE
        # ----------------------------------------------------

        if self.is_shuffle:

            if total == 1:

                new_index = (
                    self.online_queue_index
                )

            else:

                import random

                indexes = [

                    index

                    for index in range(total)

                    if index
                    != self.online_queue_index
                ]

                new_index = random.choice(
                    indexes
                )

        # ----------------------------------------------------
        # NORMAL
        # ----------------------------------------------------

        else:

            new_index = (
                self.online_queue_index + 1
            ) % total

        self.online_queue_index = (
            new_index
        )

        song = self.online_queue[
            self.online_queue_index
        ]

        self.update_online_song(
            song,
            preserve_queue=True
        )

    # ========================================================
    # ONLINE PREVIOUS
    # ========================================================

    def play_online_previous(self):

        if not self.online_queue:

            return

        self.online_queue_index -= 1

        if self.online_queue_index < 0:

            self.online_queue_index = (
                len(self.online_queue) - 1
            )

        song = self.online_queue[
            self.online_queue_index
        ]

        self.update_online_song(
            song,
            preserve_queue=True
        )

    # ========================================================
    # SET CURRENT QUEUE INDEX
    # ========================================================

    def set_current_index(self, index):
        if not self.queue:
            self.queue_index = 0
            return

        index = max(0, min(index, len(self.queue) - 1))
        self.queue_index = index
        self.refresh_next_up()

    # ========================================================
    # REFRESH NEXT UP
    # ========================================================

    def refresh_next_up(self):

        if not hasattr(
            self,
            "next_scroll"
        ):

            return

        content = QWidget()

        content.setStyleSheet(
            "QWidget { background: transparent; }"
        )

        layout = QVBoxLayout(
            content
        )

        layout.setContentsMargins(
            0,
            0,
            4,
            4
        )

        layout.setSpacing(
            7
        )

        # ====================================================
        # ONLINE QUEUE
        # ====================================================

        if (
            self.playback_source == "online"
            and self.online_queue
        ):

            total = len(
                self.online_queue
            )

            for offset in range(
                1,
                total
            ):

                index = (
                    self.online_queue_index
                    + offset
                ) % total

                song = self.online_queue[
                    index
                ]

                layout.addWidget(
                    self.create_online_next_song(
                        song
                    )
                )

            remaining = max(
                0,
                total - 1
            )

        # ====================================================
        # LOCAL QUEUE
        # ====================================================

        elif self.queue:

            total = len(
                self.queue
            )

            for offset in range(
                1,
                total
            ):

                index = (
                    self.queue_index
                    + offset
                ) % total

                (
                    image_path,
                    title,
                    artist
                ) = self.queue[
                    index
                ]

                layout.addWidget(
                    self.create_next_song(
                        image_path,
                        title,
                        artist
                    )
                )

            remaining = max(
                0,
                total - 1
            )

        # ====================================================
        # EMPTY
        # ====================================================

        else:

            empty = QLabel(
                "No songs in queue"
            )

            empty.setStyleSheet(
                """
                QLabel {
                    color: #756A91;
                    font-size: 11px;
                    background: transparent;
                    padding: 12px;
                }
                """
            )

            layout.addWidget(
                empty
            )

            remaining = 0

        layout.addStretch()

        self.next_scroll.setWidget(
            content
        )

        self.queue_count.setText(
            f"{remaining} "
            f"{'song' if remaining == 1 else 'songs'}"
        )

    # ========================================================
    # CONTROL BUTTON
    # ========================================================

    # ========================================================
    # NEXT SONG ITEM
    # ========================================================

    def create_next_song(self, image_path, title, artist):
        item = QFrame()
        item.setFixedHeight(58)
        item.setObjectName("NextSong")
        item.setStyleSheet("""
        QFrame#NextSong {
            background: rgba(255,255,255,5);
            border: 1px solid transparent;
            border-radius: 12px;
        }
        QFrame#NextSong:hover {
            background: rgba(139,58,246,20);
            border: 1px solid rgba(139,92,246,55);
        }
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(7, 6, 8, 6)
        layout.setSpacing(9)

        # ====================================================
        # THUMBNAIL
        # ====================================================

        thumb = QLabel()
        thumb.setFixedSize(46, 46)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setStyleSheet("""
        QLabel {
            background: #24183D;
            border-radius: 9px;
        }
        """)

        image = find_asset(image_path)
        if image:
            pix = QPixmap(str(image))
            if not pix.isNull():
                thumb.setPixmap(
                    pix.scaled(
                        46, 46,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

        layout.addWidget(thumb)

        # ====================================================
        # SONG TEXT
        # ====================================================

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        song_title = QLabel(title)
        song_title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        }
        """)

        song_artist = QLabel(artist)
        song_artist.setStyleSheet("""
        QLabel {
            color: #81779B;
            font-size: 10px;
            background: transparent;
        }
        """)

        text_layout.addWidget(song_title)
        text_layout.addWidget(song_artist)
        layout.addLayout(text_layout, 1)

        # ====================================================
        # DURATION
        # ====================================================

        duration_label = QLabel("Loading...")
        duration_label.setStyleSheet("""
        QLabel {
            color: #756A91;
            font-size: 9px;
            background: transparent;
        }
        """)
        layout.addWidget(duration_label)

        # ====================================================
        # LOAD ACTUAL MP3 DURATION
        # ====================================================

        music_path = image_path.replace(
            "assets/album_art/",
            "assets/music/"
        )
        music_path = str(Path(music_path).with_suffix(".mp3"))
        audio_file = find_asset(music_path)

        if audio_file:

            def update_duration_label(duration):
                try:
                    duration_label.setText(duration)
                except RuntimeError:
                    # This item may already have been removed by refresh_next_up().
                    pass
                except Exception:
                    pass

            self.duration_probe.load(
                audio_file,
                update_duration_label
            )

        else:
            duration_label.setText("0:00")
            print(
                "Next Up audio not found:",
                music_path
            )

        # ====================================================
        # CLICK
        # ====================================================

        item.mousePressEvent = lambda event: (
            self.next_song_requested.emit(
                image_path,
                title,
                artist
            )
        )

        return item

    # ========================================================
    # ONLINE NEXT SONG ITEM
    # ========================================================

    def create_online_next_song(
        self,
        song
    ):

        item = QFrame()
        item.setFixedHeight(58)
        item.setObjectName("NextSong")
        item.setStyleSheet("""
        QFrame#NextSong {
            background: rgba(255,255,255,5);
            border: 1px solid transparent;
            border-radius: 12px;
        }
        QFrame#NextSong:hover {
            background: rgba(139,58,246,20);
            border: 1px solid rgba(139,92,246,55);
        }
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(7, 6, 8, 6)
        layout.setSpacing(9)

        # ONLINE THUMBNAIL
        thumb = QLabel("♫")
        thumb.setFixedSize(46, 46)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setScaledContents(False)
        thumb.setStyleSheet("""
        QLabel {
            background: #24183D;
            color: #A970FF;
            border-radius: 9px;
            font-size: 19px;
        }
        """)
        layout.addWidget(thumb)

        image_url = str(getattr(song, "image_url", "") or "").strip()
        if image_url:
            self.load_online_thumbnail(image_url, thumb)

        # TEXT
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        title = QLabel(song.display_title())
        title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        }
        """)

        artist = QLabel(song.display_artist())
        artist.setStyleSheet("""
        QLabel {
            color: #81779B;
            font-size: 10px;
            background: transparent;
        }
        """)

        text_layout.addWidget(title)
        text_layout.addWidget(artist)
        layout.addLayout(text_layout, 1)

        duration = QLabel(song.duration_text())
        duration.setStyleSheet("""
        QLabel {
            color: #756A91;
            font-size: 9px;
            background: transparent;
        }
        """)
        layout.addWidget(duration)

        item.mousePressEvent = (
            lambda event, selected_song=song:
            self.update_online_song(selected_song, preserve_queue=True)
        )

        return item

    # ========================================================
    # LOAD ONLINE NEXT-UP THUMBNAIL
    # ========================================================

    def load_online_thumbnail(self, image_url, label):

        if self.data_saver_enabled:
            return

        image_url = str(image_url or "").strip()
        if not image_url:
            return

        url = QUrl(image_url)
        if not url.isValid():
            print("Invalid Next Up cover URL:", image_url)
            return

        request = QNetworkRequest(url)
        request.setRawHeader(b"User-Agent", b"LYRx-Music-Player/0.2")

        reply = self.cover_network.get(request)
        self.thumbnail_replies.append(reply)

        reply.finished.connect(
            lambda r=reply, target=label:
            self.online_thumbnail_loaded(r, target)
        )

    # ========================================================
    # ONLINE NEXT-UP THUMBNAIL LOADED
    # ========================================================

    def online_thumbnail_loaded(self, reply, label):

        try:
            raw_data = bytes(reply.readAll())
            pixmap = QPixmap()

            if not pixmap.loadFromData(raw_data):
                return

            scaled = pixmap.scaled(
                46, 46,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            label.clear()
            label.setPixmap(scaled)

        except RuntimeError:
            pass
        except Exception as error:
            print("Next Up online cover error:", error)
        finally:
            try:
                self.thumbnail_replies.remove(reply)
            except (ValueError, RuntimeError):
                pass
            try:
                reply.deleteLater()
            except RuntimeError:
                pass

    # ========================================================
    # LOAD ONLINE COVER
    # ========================================================

    def load_online_cover(
        self,
        image_url
    ):

        if self.data_saver_enabled:

            self.album.clear()

            self.album.setText(
                "♫"
            )

            return

        image_url = str(
            image_url or ""
        ).strip()

        if not image_url:

            self.album.clear()

            self.album.setText(
                "♫"
            )

            return

        # ----------------------------------------------------
        # CANCEL OLD REQUEST
        # ----------------------------------------------------

        try:

            if (
                self.cover_reply is not None
                and
                self.cover_reply.isRunning()
            ):

                self.cover_reply.abort()

        except Exception:

            pass

        # ----------------------------------------------------
        # REQUEST
        # ----------------------------------------------------

        request = QNetworkRequest(
            QUrl(
                image_url
            )
        )

        request.setRawHeader(
            b"User-Agent",
            b"LYRx-Music-Player/0.2"
        )

        self.cover_reply = (
            self.cover_network.get(
                request
            )
        )

        self.cover_reply.finished.connect(
            self.online_cover_loaded
        )


    # ========================================================
    # ONLINE COVER LOADED
    # ========================================================

    def online_cover_loaded(self):

        reply = self.sender()

        if reply is None:

            return

        try:

            data = reply.readAll()

            pixmap = QPixmap()

            loaded = pixmap.loadFromData(
                bytes(data)
            )

            if loaded:

                scaled = pixmap.scaled(
                    232,
                    232,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                self.album.setText("")

                self.album.setPixmap(
                    scaled
                )

                self.cover_pixmap_changed.emit(
                    scaled
                )

            else:

                self.album.clear()

                self.album.setText(
                    "♫"
                )

        except Exception as error:

            print(
                "Online cover load error:",
                error
            )

        finally:

            try:

                reply.deleteLater()

            except Exception:

                pass

            if reply is self.cover_reply:

                self.cover_reply = None

    # ========================================================
    # UPDATE ONLINE SONG
    # ========================================================

    def update_online_song(
        self,
        song,
        preserve_queue=False
    ):

        if song is None:

            return

        self._prepare_new_track_transition()

        # ====================================================
        # ONLINE MODE
        # ====================================================

        self.playback_source = "online"

        self.current_online_song = song
        if hasattr(self, "quality_badge"):
            self.quality_badge.setText("♫  Online Audio")

        # ====================================================
        # BASIC DATA
        # ====================================================

        title = str(
            getattr(
                song,
                "title",
                ""
            )
            or "Unknown Track"
        )

        artist = str(
            getattr(
                song,
                "artist",
                ""
            )
            or "Unknown Artist"
        )

        image_url = str(
            getattr(
                song,
                "image_url",
                ""
            )
            or ""
        )

        # ====================================================
        # DAY 25 - PROVIDER-AWARE ONLINE STREAM SELECTION
        # ====================================================
        #
        # Streaming Quality:
        #     uses provider quality variants when exposed.
        #
        # Data Saver:
        #     prefers preview / low-bandwidth variants when available.
        #
        # Fallback:
        #     existing playable_url / audio_url / preview_url.
        # ====================================================

        audio_url = self._preferred_online_audio_url(
            song
        )

        # Keep the currently selected queue item compatible with
        # the older Day 19 playback layer.
        if audio_url:

            try:

                song.audio_url = (
                    audio_url
                )

            except Exception:

                pass

        duration_seconds = int(
            getattr(
                song,
                "duration",
                0
            )
            or 0
        )

        self.current_online_duration_seconds = (
            duration_seconds
        )

        # A newly selected track gets a fresh retry budget.
        self.online_retry_count = 0

        # ====================================================
        # SYNC ONLINE QUEUE INDEX
        # ====================================================

        if self.online_queue:

            song_id = str(
                getattr(
                    song,
                    "id",
                    ""
                )
            )

            for index, queue_song in enumerate(
                self.online_queue
            ):

                queue_id = str(
                    getattr(
                        queue_song,
                        "id",
                        ""
                    )
                )

                if (
                    song_id
                    and queue_id
                    and song_id == queue_id
                ):

                    self.online_queue_index = index

                    break

        # ====================================================
        # VALIDATE AUDIO
        # ====================================================

        if not audio_url:

            print(
                "Online song has no audio URL:",
                title
            )

            return

        print()
        print("=" * 60)

        print(
            "LYRx ONLINE PLAY"
        )

        print(
            "Title:",
            title
        )

        print(
            "Artist:",
            artist
        )

        print(
            "Audio:",
            audio_url
        )

        print("=" * 60)
        print()

        # ====================================================
        # STOP CURRENT SONG
        # ====================================================

        self.audio_player.stop()

        # ====================================================
        # CURRENT STATE
        # ====================================================

        self.current_image_path = (
            image_url
        )

        self.current_title = (
            title
        )

        self.current_artist = (
            artist
        )

        # ====================================================
        # UI
        # ====================================================

        self.song.setText(
            title
        )

        self.artist.setText(
            artist
        )

        # ====================================================
        # COVER
        # ====================================================

        self.album.clear()

        self.album.setText(
            "♫"
        )

        self.load_online_cover(
            image_url
        )

        # ====================================================
        # RESET PROGRESS
        # ====================================================

        self.slider.blockSignals(
            True
        )

        self.slider.setValue(
            0
        )

        self.slider.blockSignals(
            False
        )

        self.current_time.setText(
            "0:00"
        )

        # ----------------------------------------------------
        # API duration can be shown immediately
        # ----------------------------------------------------

        if duration_seconds > 0:

            minutes = (
                duration_seconds
                // 60
            )

            seconds = (
                duration_seconds
                % 60
            )

            self.total_time.setText(
                f"{minutes}:"
                f"{seconds:02d}"
            )

        else:

            self.total_time.setText(
                "0:00"
            )

        # ====================================================
        # FLOATING PLAYER SYNC
        # ====================================================

        self.song_changed.emit(
            image_url,
            title,
            artist
        )

        # ====================================================
        # ONLINE STREAM
        # ====================================================

        media_url = QUrl(
            audio_url
        )

        if not media_url.isValid():

            print(
                "Invalid online audio URL:",
                audio_url
            )

            return

        # ====================================================
        # SAFE ONLINE START
        # ====================================================

        self.start_online_stream(
            audio_url
        )

        self.refresh_next_up()

        print(
            "LYRx streaming request:",
            title,
            "-",
            artist
        )

    # ========================================================
    # START ONLINE STREAM
    # ========================================================

    def start_online_stream(
        self,
        audio_url
    ):

        audio_url = str(
            audio_url or ""
        ).strip()

        if not audio_url:

            return

        media_url = QUrl(
            audio_url
        )

        if not media_url.isValid():

            print(
                "Invalid online audio URL:",
                audio_url
            )

            return

        self.online_stream_url = (
            audio_url
        )

        self.online_autoplay_pending = (
            True
        )

        # Clear the previous source first. This helps Windows/Qt release
        # the previous remote decoder before opening another HTTP stream.
        self.audio_player.stop()

        self.audio_player.setSource(
            QUrl()
        )

        QTimer.singleShot(
            80,
            lambda url=media_url:
            self._set_online_source(
                url
            )
        )

    # ========================================================
    # SET ONLINE SOURCE
    # ========================================================

    def _set_online_source(
        self,
        media_url
    ):

        if (
            self.playback_source
            != "online"
        ):

            return

        self.audio_player.setSource(
            media_url
        )

        # Do not rely only on immediate play(). Some Windows multimedia
        # backends need a short event-loop cycle after setSource().
        QTimer.singleShot(
            140,
            self._play_online_source
        )

    # ========================================================
    # PLAY ONLINE SOURCE
    # ========================================================

    def _play_online_source(self):

        if (
            self.playback_source
            != "online"
        ):

            return

        if not self.online_autoplay_pending:

            return

        if self.audio_player.source().isEmpty():

            return

        self.audio_player.play()

    # ========================================================
    # RETRY ONLINE STREAM
    # ========================================================

    def retry_online_stream(self):

        if (
            self.playback_source
            != "online"
        ):

            return

        if not self.online_stream_url:

            return

        print(
            "Retrying online stream:",
            self.current_title
        )

        self.online_autoplay_pending = (
            True
        )

        media_url = QUrl(
            self.online_stream_url
        )

        self.audio_player.stop()

        self.audio_player.setSource(
            QUrl()
        )

        QTimer.singleShot(
            300,
            lambda url=media_url:
            self._set_online_source(
                url
            )
        )

    # ========================================================
    # PLAYER ERROR
    # ========================================================

    def handle_player_error(
        self,
        error,
        error_string=""
    ):

        # NoError can also be emitted while the backend resets.
        if (
            error
            == QMediaPlayer.Error.NoError
        ):

            return

        message = str(
            error_string or ""
        ).strip()

        print()
        print("=" * 60)
        print("LYRx PLAYER ERROR")
        print(
            "Source:",
            self.playback_source
        )
        print(
            "Song:",
            self.current_title
        )
        print(
            "Error:",
            error
        )
        print(
            "Message:",
            message
            if message
            else "No backend message"
        )
        print("=" * 60)
        print()

        if (
            self.playback_source == "online"
            and self.online_stream_url
            and self.online_retry_count
            < self.online_retry_limit
        ):

            self.online_retry_count += 1

            QTimer.singleShot(
                250,
                self.retry_online_stream
            )

            return

        self.online_autoplay_pending = (
            False
        )

        self.is_playing = False

        self.play_btn.setText(
            "▶"
        )

        self.play_state_changed.emit(
            False
        )

    # ========================================================
    # PLAYBACK STATE
    # ========================================================

    def handle_playback_state(
        self,
        state
    ):

        playing = (
            state
            == QMediaPlayer.PlaybackState.PlayingState
        )

        self.is_playing = (
            playing
        )

        self.play_btn.setText(
            "Ⅱ"
            if playing
            else "▶"
        )

        if playing:

            self.online_autoplay_pending = (
                False
            )

            self.online_retry_count = 0

            # If the previous song faded out into this one, bring the
            # new track smoothly back to the user's chosen volume.
            if self._fade_in_pending:
                self._fade_in_pending = False
                self._start_fade_in()

        self.play_state_changed.emit(
            playing
        )

    # ========================================================
    # UPDATE SONG
    # ========================================================

    def update_song(
        self,
        image_path,
        title,
        artist
    ):

        self._prepare_new_track_transition()

        self.playback_source = "local"

        self.current_online_song = None

        self.online_autoplay_pending = False
        self.online_stream_url = ""
        self.online_retry_count = 0
        self.current_online_duration_seconds = 0

        self.current_image_path = image_path
        self.current_title = title
        self.current_artist = artist

        self.audio_player.stop()

        self.song.setText(title)
        self.artist.setText(artist)

        image_file = find_asset(image_path)

        if image_file:
            pix = QPixmap(str(image_file))
            if not pix.isNull():
                self.album.setPixmap(
                    pix.scaled(
                        232, 232,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)

        self.current_time.setText("0:00")
        self.total_time.setText("0:00")

        # ====================================================
        # FLOATING PLAYER SYNC
        # ====================================================
        # Emit this before checking the MP3 path so the UI can still
        # reflect the selected song even if the audio file is missing.

        self.song_changed.emit(
            image_path,
            title,
            artist
        )

        # ====================================================
        # AUDIO FILE
        # ====================================================

        music_path = image_path.replace(
            "assets/album_art/",
            "assets/music/"
        )
        music_path = str(Path(music_path).with_suffix(".mp3"))
        audio_file = find_asset(music_path)

        if audio_file:
            self.audio_player.setSource(
                QUrl.fromLocalFile(
                    str(audio_file.resolve())
                )
            )

            self.audio_player.play()

            self.is_playing = True
            self.play_btn.setText("Ⅱ")
            self.play_caption.setText("Pause")
            if hasattr(self, "header_equalizer"):
                self.header_equalizer.set_playing(True)
            self.play_caption.setText("Pause")
            self.play_state_changed.emit(True)
            self.refresh_next_up()

        else:
            self.is_playing = False
            self.play_btn.setText("▶")
            self.play_caption.setText("Play")
            if hasattr(self, "header_equalizer"):
                self.header_equalizer.set_playing(False)
            self.play_caption.setText("Play")
            self.play_state_changed.emit(False)
            print(
                "Audio file not found:",
                music_path
            )

    # ========================================================
    # MEDIA STATUS
    # ========================================================

    def handle_media_status(
        self,
        status
    ):

        # ====================================================
        # ONLINE LOAD / BUFFER
        # ====================================================

        if (
            self.playback_source == "online"
            and self.online_autoplay_pending
            and status in (
                QMediaPlayer.MediaStatus.LoadedMedia,
                QMediaPlayer.MediaStatus.BufferedMedia,
            )
        ):

            self.audio_player.play()

        # ====================================================
        # INVALID MEDIA
        # ====================================================

        if (
            status
            == QMediaPlayer.MediaStatus.InvalidMedia
        ):

            print(
                "Invalid media:",
                self.current_title
            )

            return

        # ====================================================
        # END OF MEDIA
        # ====================================================

        if (
            status
            != QMediaPlayer.MediaStatus.EndOfMedia
        ):

            return

        print(
            "Song finished:",
            self.song.text()
        )

        self.song_finished.emit()

        if self.is_repeat:

            self.audio_player.setPosition(
                0
            )

            self.audio_player.play()

            return

        self.is_playing = False

        self.play_btn.setText(
            "▶"
        )

        self.play_state_changed.emit(
            False
        )

        # Autoplay OFF means the finished song simply stops.
        if not self.autoplay_enabled:
            self._cancel_fade(restore_volume=True)
            return

        # If a fade-out was already running and the backend reached
        # EndOfMedia first, finish the transition exactly once.
        if self._fade_mode == "out":
            self.fade_timer.stop()
            self._fade_mode = None
            self.audio_output.setVolume(0.0)
            self._fade_in_pending = (
                self.crossfade_seconds > 0
            )
            self._transition_in_progress = True
            self._request_next_track()
            return

        if self._transition_in_progress:
            return

        # Gapless ON advances immediately. With Gapless OFF we leave a
        # small intentional pause so the setting has real audible effect.
        if self.gapless_enabled:
            self._request_next_track()
        else:
            QTimer.singleShot(
                320,
                self._request_next_track
            )

    # ========================================================
    # PLAY / PAUSE
    # ========================================================

    def toggle_play(self):

        state = (
            self.audio_player
            .playbackState()
        )

        if (
            state
            == QMediaPlayer.PlaybackState.PlayingState
        ):

            self.online_autoplay_pending = (
                False
            )

            self.audio_player.pause()

        else:

            # If an online source failed to open and Qt has no active
            # source, rebuild it before trying Play again.
            if (
                self.playback_source == "online"
                and self.audio_player.source().isEmpty()
                and self.online_stream_url
            ):

                self.online_autoplay_pending = (
                    True
                )

                self.start_online_stream(
                    self.online_stream_url
                )

                return

            self.audio_player.play()

    # ========================================================
    # UPDATE DURATION
    # ========================================================

    def update_duration(
        self,
        duration
    ):

        if duration <= 0:

            # Remote streams can briefly report zero while opening.
            # Keep the duration supplied by the online catalog instead
            # of flashing back to 0:00.
            if (
                self.playback_source == "online"
                and self.current_online_duration_seconds > 0
            ):

                minutes = (
                    self.current_online_duration_seconds
                    // 60
                )

                seconds = (
                    self.current_online_duration_seconds
                    % 60
                )

                self.total_time.setText(
                    f"{minutes}:"
                    f"{seconds:02d}"
                )

                return

            self.total_time.setText(
                "0:00"
            )

            return

        self.total_time.setText(
            format_duration(
                duration
            )
        )

        self.slider.setRange(
            0,
            100
        )

    # ========================================================
    # UPDATE PROGRESS
    # ========================================================

    def update_progress(self, position):
        duration = self.audio_player.duration()

        if duration <= 0:
            return

        progress = int((position / duration) * 100)

        self.slider.blockSignals(True)
        self.slider.setValue(progress)
        self.slider.blockSignals(False)

        current = format_duration(position)
        total = format_duration(duration)

        self.current_time.setText(current)

        self.progress_changed.emit(
            progress,
            current,
            total
        )

        self._check_crossfade_transition(
            position,
            duration
        )

    # ========================================================
    # SEEK AUDIO
    # ========================================================

    def seek_audio(self, value):
        duration = self.audio_player.duration()

        if duration <= 0:
            return

        position = int((value / 100) * duration)
        self.audio_player.setPosition(position)

    # ========================================================
    # VOLUME
    # ========================================================

    def change_volume(self, value):
        self.user_volume = max(
            0.0,
            min(1.0, value / 100)
        )

        # Do not fight the fade timer while a transition is running.
        if self._fade_mode is None:
            self.audio_output.setVolume(
                self.user_volume
            )

    # ========================================================
    # DAY 25 - PLAYBACK SETTINGS API
    # ========================================================

    def set_playback_preferences(
        self,
        autoplay=True,
        gapless=True,
        normalize_volume=True,
        crossfade_seconds=0,
    ):
        self.autoplay_enabled = bool(autoplay)
        self.gapless_enabled = bool(gapless)
        self.normalize_volume_enabled = bool(
            normalize_volume
        )

        try:
            seconds = int(crossfade_seconds)
        except (TypeError, ValueError):
            seconds = 0

        self.crossfade_seconds = max(
            0,
            min(12, seconds)
        )

        if (
            not self.autoplay_enabled
            or self.crossfade_seconds <= 0
        ):
            self._cancel_fade(
                restore_volume=True
            )

        print(
            "LYRx playback settings:",
            f"autoplay={self.autoplay_enabled}",
            f"gapless={self.gapless_enabled}",
            f"crossfade={self.crossfade_seconds}s",
            f"normalize={self.normalize_volume_enabled}"
        )

    # ========================================================
    # DAY 25 - ONLINE AUDIO / DATA SAVER SETTINGS
    # ========================================================

    def set_network_preferences(
        self,
        streaming_quality="Automatic",
        data_saver=False,
    ):
        allowed = {
            "Automatic",
            "Low",
            "Normal",
            "High",
            "Very High",
        }

        quality = str(
            streaming_quality
            or "Automatic"
        ).strip()

        if quality not in allowed:
            quality = "Automatic"

        self.streaming_quality_preference = quality
        self.data_saver_enabled = bool(
            data_saver
        )

        print(
            "LYRx network settings:",
            f"quality={self.streaming_quality_preference}",
            f"data_saver={self.data_saver_enabled}",
        )

    def _song_value(
        self,
        song,
        name,
    ):
        try:
            if isinstance(
                song,
                dict
            ):
                return song.get(
                    name,
                    ""
                )

            return getattr(
                song,
                name,
                ""
            )
        except Exception:
            return ""

    def _preferred_online_audio_url(
        self,
        song,
    ):
        """
        Provider-aware stream selection.

        Existing LYRx providers often expose one playable URL only.
        If future/current Song objects expose quality variants, this
        method immediately honours the selected quality without
        changing the rest of the player.
        """

        quality = self.streaming_quality_preference

        quality_fields = {
            "Low": [
                "audio_url_low",
                "low_quality_url",
                "preview_url",
            ],
            "Normal": [
                "audio_url_normal",
                "audio_url_medium",
                "preview_url",
            ],
            "High": [
                "audio_url_high",
                "high_quality_url",
            ],
            "Very High": [
                "audio_url_very_high",
                "audio_url_lossless",
                "lossless_url",
            ],
        }

        # Data Saver always prefers the lightest / preview source
        # when one is available.
        if self.data_saver_enabled:
            candidates = [
                "audio_url_low",
                "low_quality_url",
                "preview_url",
                "audio_url",
            ]
        else:
            candidates = list(
                quality_fields.get(
                    quality,
                    []
                )
            )

        for field in candidates:
            value = str(
                self._song_value(
                    song,
                    field
                )
                or ""
            ).strip()

            if value:
                return value

        # Provider-defined playable_url remains the canonical fallback.
        try:
            if hasattr(
                song,
                "playable_url"
            ):
                value = str(
                    song.playable_url()
                    or ""
                ).strip()

                if value:
                    return value
        except Exception as error:
            print(
                "Preferred stream resolve error:",
                error
            )

        return str(
            self._song_value(
                song,
                "audio_url"
            )
            or
            self._song_value(
                song,
                "preview_url"
            )
            or
            ""
        ).strip()

    # ========================================================
    # DAY 25 - CROSSFADE-STYLE TRANSITION
    # ========================================================

    def _prepare_new_track_transition(self):
        # A manual song selection cancels any unfinished fade-out.
        # If this track was requested by the fade engine, keep the pending
        # fade-in flag so handle_playback_state() can restore volume smoothly.
        pending_fade_in = self._fade_in_pending

        self.fade_timer.stop()
        self._fade_mode = None
        self._fade_step = 0
        self._fade_started_for_track = False
        self._transition_in_progress = False
        self._fade_in_pending = pending_fade_in

        if pending_fade_in:
            self.audio_output.setVolume(0.0)
        else:
            self.audio_output.setVolume(
                self.user_volume
            )

    def _cancel_fade(
        self,
        restore_volume=True
    ):
        self.fade_timer.stop()
        self._fade_mode = None
        self._fade_step = 0
        self._fade_started_for_track = False
        self._fade_in_pending = False
        self._transition_in_progress = False

        if restore_volume:
            self.audio_output.setVolume(
                self.user_volume
            )

    def _check_crossfade_transition(
        self,
        position,
        duration
    ):
        if not self.autoplay_enabled:
            return

        if self.is_repeat:
            return

        if self.crossfade_seconds <= 0:
            return

        if self._fade_started_for_track:
            return

        if self._transition_in_progress:
            return

        if duration <= 0:
            return

        remaining = duration - position
        threshold = self.crossfade_seconds * 1000

        if (
            remaining > 0
            and remaining <= threshold
        ):
            self._fade_started_for_track = True
            self._start_fade_out()

    def _start_fade_out(self):
        duration_ms = max(
            200,
            self.crossfade_seconds * 1000
        )

        self._fade_mode = "out"
        self._fade_step = 0
        self._fade_total_steps = max(
            1,
            duration_ms // self.fade_timer.interval()
        )
        self.fade_timer.start()

    def _start_fade_in(self):
        duration_ms = max(
            200,
            self.crossfade_seconds * 1000
        )

        self._fade_mode = "in"
        self._fade_step = 0
        self._fade_total_steps = max(
            1,
            duration_ms // self.fade_timer.interval()
        )
        self.audio_output.setVolume(0.0)
        self.fade_timer.start()

    def _process_fade_step(self):
        if self._fade_mode not in (
            "out",
            "in",
        ):
            self.fade_timer.stop()
            return

        self._fade_step += 1

        ratio = min(
            1.0,
            self._fade_step / self._fade_total_steps
        )

        if self._fade_mode == "out":
            volume = self.user_volume * (1.0 - ratio)
        else:
            volume = self.user_volume * ratio

        self.audio_output.setVolume(
            max(0.0, min(1.0, volume))
        )

        if ratio < 1.0:
            return

        mode = self._fade_mode
        self.fade_timer.stop()
        self._fade_mode = None

        if mode == "out":
            self.audio_output.setVolume(0.0)
            self._fade_in_pending = True
            self._transition_in_progress = True
            self._request_next_track()
        else:
            self.audio_output.setVolume(
                self.user_volume
            )
            self._transition_in_progress = False
            self._fade_started_for_track = False

    def _request_next_track(self):
        if not self.autoplay_enabled:
            self._cancel_fade(
                restore_volume=True
            )
            return

        if (
            self.playback_source == "online"
            and self.online_queue
        ):
            self.play_online_next()
        else:
            self.next_requested.emit()

    # ========================================================
    # SHUFFLE
    # ========================================================

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        self.shuffle_btn.set_active(self.is_shuffle)
        self.shuffle_btn.setToolTip(
            "Shuffle on" if self.is_shuffle else "Shuffle off"
        )
        print(
            "Shuffle:",
            "ON" if self.is_shuffle else "OFF"
        )

    # ========================================================
    # REPEAT
    # ========================================================

    def toggle_repeat(self):
        self.is_repeat = not self.is_repeat
        self.repeat_btn.set_active(self.is_repeat)
        self.repeat_btn.setToolTip(
            "Repeat current track: on"
            if self.is_repeat
            else "Repeat current track: off"
        )
        print(
            "Repeat current track:",
            "ON" if self.is_repeat else "OFF"
        )

    # ========================================================
    # PAINT
    # ========================================================

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        path = QPainterPath()
        path.addRoundedRect(
            rect.adjusted(1, 1, -1, -1),
            24,
            24
        )

        gradient = QLinearGradient(
            0,
            0,
            rect.width(),
            rect.height()
        )

        gradient.setColorAt(0.0, QColor("#171125"))
        gradient.setColorAt(0.50, QColor("#211532"))
        gradient.setColorAt(1.0, QColor("#100C19"))

        painter.fillPath(path, gradient)

        pen = QPen(
            QColor(139, 92, 246, 85)
        )
        pen.setWidth(1)

        painter.setPen(pen)
        painter.drawPath(path)

        painter.setPen(Qt.NoPen)
        painter.setBrush(
            QColor(139, 92, 246, 28)
        )
        painter.drawEllipse(
            rect.width() - 130,
            -35,
            160,
            160
        )

        painter.setBrush(
            QColor(168, 85, 247, 14)
        )
        painter.drawEllipse(
            -35,
            rect.height() - 100,
            120,
            120
        )

        painter.end()
        super().paintEvent(event)
