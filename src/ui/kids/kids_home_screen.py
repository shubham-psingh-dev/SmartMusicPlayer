from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QSizePolicy, QGridLayout, QLineEdit
)


class KidsCategoryCard(QFrame):
    requested = Signal(str)

    def __init__(self, route, emoji, title, subtitle, accent_a, accent_b, parent=None):
        super().__init__(parent)
        self.route = route
        self.setObjectName("KidsCategoryCard")
        self.setFixedHeight(150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame#KidsCategoryCard {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {accent_a},stop:1 {accent_b});
                border:1px solid rgba(255,255,255,45);border-radius:21px;
            }}
            QFrame#KidsCategoryCard:hover {{
                border:2px solid rgba(255,255,255,130);
            }}
            QLabel {{ background:transparent;color:white; }}
        """)
        box = QVBoxLayout(self)
        box.setContentsMargins(17, 13, 17, 13)

        top = QHBoxLayout()
        icon = QLabel(emoji)
        icon.setStyleSheet("font-size:31px;")
        arrow = QLabel("›")
        arrow.setAlignment(Qt.AlignCenter)
        arrow.setFixedSize(34, 34)
        arrow.setStyleSheet(
            "background:rgba(255,255,255,35);border-radius:17px;"
            "font-size:24px;font-weight:900;"
        )
        top.addWidget(icon)
        top.addStretch()
        top.addWidget(arrow)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size:18px;font-weight:950;")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size:10px;font-weight:650;")

        box.addLayout(top)
        box.addStretch()
        box.addWidget(title_label)
        box.addWidget(subtitle_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.requested.emit(self.route)
        super().mousePressEvent(event)


class KidsPreviewCard(QFrame):
    requested = Signal(str)

    def __init__(self, route, emoji, title, meta, parent=None):
        super().__init__(parent)
        self.route = route
        self.setObjectName("KidsPreviewCard")
        self.setFixedHeight(142)
        self.setCursor(Qt.PointingHandCursor)

        box = QVBoxLayout(self)
        box.setContentsMargins(10, 10, 10, 10)
        box.setSpacing(5)

        art = QLabel(emoji)
        art.setAlignment(Qt.AlignCenter)
        art.setFixedHeight(76)
        art.setStyleSheet("""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #292267,stop:1 #49358E);
            border:1px solid #5545A3;border-radius:13px;font-size:34px;
        """)
        name = QLabel(title)
        name.setStyleSheet("color:white;font-size:11px;font-weight:900;")
        info = QLabel(meta)
        info.setStyleSheet("color:#9F99CA;font-size:9px;")

        box.addWidget(art)
        box.addWidget(name)
        box.addWidget(info)
        self.setStyleSheet("""
            QFrame#KidsPreviewCard {
                background:#15113C;border:1px solid #2E2862;border-radius:16px;
            }
            QFrame#KidsPreviewCard:hover {
                border-color:#7B63E9;background:#1C174D;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.requested.emit(self.route)
        super().mousePressEvent(event)


class KidsHomeScreen(QWidget):
    category_requested = Signal(str)
    search_requested = Signal(str)
    minimize_requested = Signal()
    maximize_requested = Signal()
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("KidsHomeScreen")
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        content = QWidget()
        content.setObjectName("KidsContent")
        scroll.setWidget(content)
        root = QVBoxLayout(content)
        root.setContentsMargins(28, 20, 28, 24)
        root.setSpacing(14)

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("KidsHomeSearch")
        self.search.setPlaceholderText("Search kids songs, rhymes, stories...")
        self.search.setClearButtonEnabled(True)
        self.search.setFixedHeight(46)
        self.search.returnPressed.connect(self._submit_search)

        search_btn = QPushButton("⌕  Search")
        search_btn.setObjectName("HomeSearchButton")
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setFixedHeight(46)
        search_btn.clicked.connect(self._submit_search)

        safe = QLabel("🛡️  SAFE")
        safe.setObjectName("SafeBadge")
        safe.setAlignment(Qt.AlignCenter)

        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("□")
        self.close_btn = QPushButton("✕")
        for button in (self.min_btn, self.max_btn, self.close_btn):
            button.setObjectName("KidsWindowButton")
            button.setFixedSize(38, 38)
            button.setCursor(Qt.PointingHandCursor)
        self.close_btn.setObjectName("KidsWindowClose")
        self.min_btn.clicked.connect(self.minimize_requested.emit)
        self.max_btn.clicked.connect(self.maximize_requested.emit)
        self.close_btn.clicked.connect(self.close_requested.emit)

        top.addWidget(self.search, 1)
        top.addWidget(search_btn)
        top.addWidget(safe)
        top.addWidget(self.min_btn)
        top.addWidget(self.max_btn)
        top.addWidget(self.close_btn)
        root.addLayout(top)

        # Hero: artwork is intentionally integrated directly into the gradient.
        # No separate dark box around kids_banner.png.
        hero = QFrame()
        hero.setObjectName("KidsHero")
        hero.setFixedHeight(238)
        hero_box = QHBoxLayout(hero)
        hero_box.setContentsMargins(30, 20, 18, 18)
        hero_box.setSpacing(10)

        copy = QVBoxLayout()
        copy.setSpacing(7)
        eyebrow = QLabel("⭐  SAFE • POSITIVE • JUST FOR YOU")
        eyebrow.setObjectName("HeroEyebrow")
        title = QLabel("Hi, Little Dreamer!")
        title.setObjectName("HeroTitle")
        text = QLabel(
            "Explore a happy world of music, stories,\n"
            "rhymes, imagination and playful learning."
        )
        text.setObjectName("HeroText")
        ribbon = QLabel("Listen  •  Learn  •  Imagine  •  Grow  💜")
        ribbon.setObjectName("HeroRibbon")
        copy.addWidget(eyebrow)
        copy.addWidget(title)
        copy.addWidget(text)
        copy.addStretch()
        copy.addWidget(ribbon, 0, Qt.AlignLeft)
        hero_box.addLayout(copy, 5)

        self.hero_image = QLabel()
        self.hero_image.setObjectName("HeroImage")
        self.hero_image.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
        self.hero_image.setMinimumWidth(400)

        banner_path = (
            Path(__file__).resolve().parents[3]
            / "assets" / "icons" / "logo" / "kids_banner.png"
        )
        pixmap = QPixmap(str(banner_path))
        if not pixmap.isNull():
            self.hero_image.setPixmap(
                pixmap.scaled(430, 218, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.hero_image.setText("🎧  🌟  📚")
            self.hero_image.setStyleSheet("font-size:50px;background:transparent;")
        hero_box.addWidget(self.hero_image, 4)
        root.addWidget(hero)

        head = QHBoxLayout()
        section = QLabel("Explore Kids Mode")
        section.setObjectName("SectionTitle")
        phase = QLabel("LYRx KIDS • LEARN • LISTEN • GROW")
        phase.setObjectName("MicroLabel")
        head.addWidget(section)
        head.addStretch()
        head.addWidget(phase)
        root.addLayout(head)

        cards = QGridLayout()
        cards.setHorizontalSpacing(12)
        cards.setVerticalSpacing(12)
        categories = [
            ("Kids Music", "🎧", "Kids Music", "Happy songs & sing-alongs", "#674AF0", "#9B3CF1"),
            ("Stories", "📚", "Stories", "Audible stories & moral tales", "#E86B2A", "#FF9631"),
            ("Poems & Rhymes", "🎶", "Poems & Rhymes", "Rhymes, poems & little verses", "#D93C91", "#F044AE"),
            ("Spiritual", "🪷", "Spiritual", "Peaceful & devotional listening", "#239B68", "#36BF7D"),
            ("Study & Learn", "🎓", "Study & Learn", "ABC, numbers, languages & math", "#267FC8", "#399FE5"),
        ]
        for i, args in enumerate(categories):
            card = KidsCategoryCard(*args, self)
            card.requested.connect(self.category_requested.emit)
            row, col = divmod(i, 3)
            cards.addWidget(card, row, col)
        root.addLayout(cards)

        pop_head = QHBoxLayout()
        popular = QLabel("⭐  Popular for Kids")
        popular.setObjectName("SectionTitle")
        hint = QLabel("TAP A CARD TO EXPLORE")
        hint.setObjectName("MicroLabel")
        pop_head.addWidget(popular)
        pop_head.addStretch()
        pop_head.addWidget(hint)
        root.addLayout(pop_head)

        shelf = QHBoxLayout()
        shelf.setSpacing(10)
        popular_items = [
            ("Kids Music", "🌙🧸", "Lullaby Time", "Gentle listening"),
            ("Stories", "🐰📖", "Moral Stories", "Story time"),
            ("Poems & Rhymes", "🌟🎶", "Fun Rhymes", "Sing & learn"),
            ("Study & Learn", "🧒📚", "Learning Time", "Study & play"),
            ("Kids Music", "🦒🦁", "Animal Songs", "Kids music"),
            ("Stories", "🌼😊", "Good Habits", "Little lessons"),
        ]
        for item in popular_items:
            card = KidsPreviewCard(*item, self)
            card.requested.connect(self.category_requested.emit)
            shelf.addWidget(card)
        root.addLayout(shelf)

        footer = QLabel("🌈  Listen • Learn • Imagine • Grow   💜   LYRx Kids")
        footer.setObjectName("KidsFooter")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFixedHeight(46)
        root.addWidget(footer)

    def _submit_search(self):
        query = self.search.text().strip()
        if query:
            self.search_requested.emit(query)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#KidsHomeScreen, QWidget#KidsContent { background:#0D0A2B; }
            QLineEdit#KidsHomeSearch {
                color:white;background:#1B164F;border:1px solid #5143A3;
                border-radius:15px;padding:0 17px;font-size:11px;
            }
            QLineEdit#KidsHomeSearch:focus { border-color:#8C6BFF; }
            QPushButton#HomeSearchButton {
                color:white;background:#6D4DEB;border:none;border-radius:15px;
                padding:0 17px;font-size:10px;font-weight:900;
            }
            QPushButton#HomeSearchButton:hover { background:#8261F4; }
            QPushButton#KidsWindowButton {
                color:white;background:#211A56;border:1px solid #4B3B9B;
                border-radius:11px;font-size:14px;font-weight:900;
            }
            QPushButton#KidsWindowButton:hover { background:#5D45D2; }
            QPushButton#KidsWindowClose {
                color:white;background:#35162D;border:1px solid #71304F;
                border-radius:11px;font-size:13px;font-weight:900;
            }
            QPushButton#KidsWindowClose:hover { background:#C43A62; }
            QLabel#SafeBadge {
                color:#72F1CF;background:#102B38;border:1px solid #176D68;
                border-radius:15px;padding:8px 12px;font-size:10px;font-weight:900;
            }
            QFrame#KidsHero {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #2454E2,stop:.34 #5543EC,stop:.68 #8A3EEA,stop:1 #D13CC2);
                border:1px solid rgba(255,255,255,55);border-radius:27px;
            }
            QLabel#HeroImage { background:transparent;border:none; }
            QLabel#HeroEyebrow {
                color:#FFE76B;font-size:10px;font-weight:950;background:transparent;
            }
            QLabel#HeroTitle {
                color:white;font-size:34px;font-weight:950;background:transparent;
            }
            QLabel#HeroText {
                color:#F5F2FF;font-size:13px;font-weight:650;background:transparent;
            }
            QLabel#HeroRibbon {
                color:#27123C;background:#FFE16A;border-radius:14px;
                padding:8px 14px;font-size:10px;font-weight:950;
            }
            QLabel#SectionTitle { color:white;font-size:20px;font-weight:950; }
            QLabel#MicroLabel { color:#AAA4D6;font-size:8px;font-weight:900; }
            QLabel#KidsFooter {
                color:#DCD8FF;background:#171342;border:1px solid #342D70;
                border-radius:14px;font-size:11px;font-weight:850;
            }
            QScrollArea { border:none;background:transparent; }
            QScrollBar:vertical {
                background:transparent;width:8px;margin:4px;
            }
            QScrollBar::handle:vertical {
                background:#514A91;border-radius:4px;min-height:35px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height:0; }
        """)
