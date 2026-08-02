import sys
import os
import json
import vlc
import yt_dlp

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QSlider,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QLineEdit,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer


class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StreamWave Music Player 🎵")
        self.resize(1000, 650)

        # VLC player
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # Timer for progress bar
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_progress)

        root_layout = QHBoxLayout(self)

        sidebar = QVBoxLayout()

        self.home_btn = QPushButton("🏠 Home")
        self.library_btn = QPushButton("🎵 Library")
        self.fav_btn = QPushButton("❤ Favorites")

        for btn in [self.home_btn, self.library_btn, self.fav_btn]:
            btn.setFixedHeight(50)
            sidebar.addWidget(btn)
        
        sidebar.addStretch()

        # ===== Stacked Pages =====
        self.pages = QStackedWidget()

        self.home_page = self.create_home_page()
        self.library_page = self.create_library_page()
        self.favorites_page = self.create_favorites_page()

        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.library_page)
        self.pages.addWidget(self.favorites_page)

        player_bar = self.create_player_bar()

        content_layout = QVBoxLayout()
        content_layout.addWidget(self.pages)
        content_layout.addLayout(player_bar)

        root_layout.addLayout(sidebar, 1)
        root_layout.addLayout(content_layout, 4)

        self.home_btn.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.library_btn.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.fav_btn.clicked.connect(lambda: self.pages.setCurrentIndex(2))

        self.apply_dark_theme()

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Welcome to Your Music App")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search song (online)...")

        self.search_btn = QPushButton("🔍 Search & Play")
        self.search_btn.clicked.connect(self.search_online)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(self.search_box)
        layout.addWidget(self.search_btn)
        layout.addStretch()

        return  page
    
    def create_library_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.open_button = QPushButton("📂 Open Local Music")
        self.open_button.clicked.connect(self.open_file)

        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_selected)

        layout.addWidget(self.open_button)
        layout.addWidget(self.playlist)

        return page
    
    def create_favorites_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self.play_favorite)

        self.remove_fav_btn = QPushButton("🗑 Remove Favorite")
        self.remove_fav_btn.clicked.connect(self.remove_favorite)

        layout.addWidget(QLabel("Your Favorites"))
        layout.addWidget(self.favorites_list)
        layout.addWidget(self.remove_fav_btn)

        self.refresh_favorites_ui()

        return page
    
    def create_player_bar(self):
        layout = QVBoxLayout()

        self.now_playing = QLabel("No song playing")
        self.now_playing.setAlignment(Qt.AlignCenter)
        self.now_playing.setWordWrap(True)

        self.progress = QSlider(Qt.Horizontal)
        self.progress.sliderMoved.connect(self.seek)
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignRight)

        controls = QHBoxLayout()

        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.stop_btn = QPushButton("⏹")
        self.fav_add_btn = QPushButton("❤")

        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)
        self.stop_btn.clicked.connect(self.player.stop)
        self.fav_add_btn.clicked.connect(self.add_to_favorites)

        for b in [self.play_btn, self.pause_btn, self.stop_btn, self.fav_add_btn]:
            controls.addWidget(b)

        # ===== UI =====

        self.label = QLabel("No song selected")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Theme toggle
        self.theme_button = QPushButton("🌙 Toggle Theme")
        self.dark_mode = True

        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.player.audio_set_volume)

        layout.addWidget(self.now_playing)
        layout.addWidget(self.progress)
        layout.addLayout(controls)
        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.volume_slider)

        return layout

    # ===== Online Search (YouTube) =====

    def search_online(self):
        query = self.search_box.text().strip()
        if not query:
            return

        self.label.setText(f"Searching: {query}...")

        ydl_opts = {
            "format": "bestaudio",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            url = info["url"]
            title = info.get("title", query)

        # IMPORTANT: save URL for favorites
        self.current_song_path = url

        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.label.setText(title)
        self.player.play()

        self.current_song = {
            "title": title,
            "path": url,
        }

        self.now_playing.setText(title)
        self.timer.start(500)

        except Exception as e:
        self.now_playing.setText(f"Streaming error: {e}") # type: ignore

    # ===== Playlist (Local Files) =====

    def open_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Audio Files",
            "",
            "Audio Files (*.mp3 *.wav *.flac)"
        )

        for file_path in files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.UserRole, file_path)
            self.playlist.addItem(item)

    def play_selected(self):
        current_item = self.playlist.currentItem()
        if current_item:
            file_path = current_item.data(Qt.UserRole)
            self.play_song(file_path)

    # ===== Core Playback =====

    def play_song(self, path):

        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.now_playing.setText(os.path.basename(path))
        self.current_song = path
        self.timer.start(500)

    def play_music(self):
        self.play_selected()

    def pause_music(self):
        self.player.pause()

    def stop_music(self):
        self.player.stop()

    def change_volume(self, value):
        self.player.audio_set_volume(value)

    # ===== Seek / Timestamp =====

    def update_progress(self):
        if self.player.is_playing():
            length = self.player.get_length()
            pos = self.player.get_time()
            if length > 0:
                self.progress.setValue(int(pos / length * 1000))

    def seek(self, value):
        length = self.player.get_length()
        self.player.set_time(int(length * value / 1000))

    def format_time(self, ms):
        seconds = ms // 1000
        m, s = divmod(seconds, 60)
        return f"{m:02}:{s:02}"

    # ===== Favorites System =====

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            with open(self.favorites_file, "r") as f:
                return json.load(f)
        return []
    
    def save_favorites(self):
        with open(self.favorites_file, "w") as f:
            json.dump(self.favorites, f, indent=2)

    def add_to_favorites(self):
        if hasattr(self, "current_song") and self.current_song not in self.favorites:
            self.favorites.append(self.current_song)
            self.save_favorites()
            self.refresh_favorites_ui()

    def remove_favorite(self):
        row = self.favorites_list.currentRow()
        if row >= 0:
            self.favorites.pop(row)
            self.save_favorites()
            self.refresh_favorites_ui()

    def refresh_favorites_ui(self):
        self.favorites_list.clear()
        for song in self.favorites:
            self.favorites_list.addItem(os.path.basename(song))

    def play_favorite(self, item):
        index = self.favorites_list.row(item)
        song_path = self.favorites[index]
        self.play_song(song_path)

    # ===== Theme System =====

    def toggle_theme(self):
        if self.dark_mode:
            self.apply_light_theme()
        else:
            self.apply_dark_theme()
        self.dark_mode = not self.dark_mode

    def apply_dark_theme(self):
        # Warm black + gothic grape + frost white + peach orange
        self.setStyleSheet("""
            QWidget {
                background-color: #1A171B;  /* warm black */
                color: #F5F7FA;  /* frost white */
                font-size: 15px;
            }
            QPushButton {
                background-color: #A8E6A3;
                color: #1A171B;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QListWidget,
            QLineEdit {
                background-color: #221E24;
                padding: 6px;
            }
        """)

    def apply_light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFF6EC;  /* soft peach */
                color: #1A171B;
                font-size: 15px;
            }
            QPushButton {
                background-color: #A8E6A3;
                color: #1A171B;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QListWidget,
            QLineEdit {
                background-color: #FFFFFF;
                padding: 6px;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec())