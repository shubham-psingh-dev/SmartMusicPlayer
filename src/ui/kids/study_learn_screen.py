import random

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout, QStackedWidget, QScrollArea, QSizePolicy
)


class StudyCategoryCard(QFrame):
    requested = Signal(int)

    def __init__(self, index, emoji, title, subtitle, accent, parent=None):
        super().__init__(parent)
        self.index = index
        self.setObjectName("StudyCategoryCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(150)
        self.setStyleSheet(f"""
            QFrame#StudyCategoryCard {{
                background:#15113C;border:1px solid #332C6C;border-radius:20px;
            }}
            QFrame#StudyCategoryCard:hover {{
                background:#1C174B;border:2px solid {accent};
            }}
            QLabel {{ background:transparent; }}
        """)
        box = QVBoxLayout(self)
        box.setContentsMargins(18, 16, 18, 16)
        icon = QLabel(emoji)
        icon.setStyleSheet("font-size:32px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("color:white;font-size:17px;font-weight:950;")
        sub = QLabel(subtitle)
        sub.setWordWrap(True)
        sub.setStyleSheet("color:#AAA4D6;font-size:10px;")
        go = QLabel("Explore  →")
        go.setStyleSheet(f"color:{accent};font-size:10px;font-weight:900;")
        box.addWidget(icon)
        box.addStretch()
        box.addWidget(title_label)
        box.addWidget(sub)
        box.addWidget(go)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.requested.emit(self.index)
        super().mousePressEvent(event)


class LearningDeck(QWidget):
    def __init__(self, subtitle, items, columns=9, mode="default", parent=None):
        super().__init__(parent)
        self.items = items
        self.columns = columns
        self.mode = mode

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        stage = QFrame()
        stage.setObjectName("LearningStage")
        stage.setMinimumHeight(215)
        stage_box = QHBoxLayout(stage)
        stage_box.setContentsMargins(26, 20, 26, 20)
        stage_box.setSpacing(22)

        self.symbol = QLabel()
        self.symbol.setAlignment(Qt.AlignCenter)
        self.symbol.setFixedSize(150, 150)
        self.symbol.setObjectName("BigSymbol")

        center = QVBoxLayout()
        center.setSpacing(7)
        self.word = QLabel()
        self.word.setObjectName("LearningWord")
        self.word.setWordWrap(True)
        self.desc = QLabel(subtitle)
        self.desc.setObjectName("LearningDescription")
        self.desc.setWordWrap(True)
        center.addStretch()
        center.addWidget(self.word)
        center.addWidget(self.desc)
        center.addStretch()

        self.visual = QLabel()
        self.visual.setObjectName("LearningVisual")
        self.visual.setAlignment(Qt.AlignCenter)
        self.visual.setFixedSize(220, 170)
        self.visual.setWordWrap(True)

        stage_box.addWidget(self.symbol)
        stage_box.addLayout(center, 1)
        stage_box.addWidget(self.visual)
        root.addWidget(stage)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setMinimumHeight(250)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        body = QWidget()
        grid = QGridLayout(body)
        grid.setContentsMargins(0, 2, 0, 2)
        grid.setHorizontalSpacing(9)
        grid.setVerticalSpacing(8)

        self.buttons = []
        for i, (symbol, _, _) in enumerate(items):
            button = QPushButton(symbol)
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(46)
            button.clicked.connect(lambda _, x=i: self.pick(x))
            grid.addWidget(button, i // columns, i % columns)
            self.buttons.append(button)

        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        self.setStyleSheet("""
            QFrame#LearningStage {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #244CB7,stop:1 #7042D4);
                border:1px solid #6655C9;border-radius:24px;
            }
            QLabel#BigSymbol {
                background:#7150EE;color:white;border-radius:34px;
                font-size:58px;font-weight:950;padding:5px;
            }
            QLabel#LearningWord {
                color:white;font-size:25px;font-weight:950;background:transparent;
            }
            QLabel#LearningDescription {
                color:#DED9FA;font-size:12px;background:transparent;
            }
            QLabel#LearningVisual {
                color:white;background:rgba(255,255,255,24);
                border:1px solid rgba(255,255,255,25);border-radius:25px;
                font-size:42px;padding:10px;
            }
            QPushButton {
                color:white;background:#1B1747;border:1px solid #393173;
                border-radius:12px;font-size:12px;font-weight:900;
            }
            QPushButton:hover { background:#3C2C8D;border-color:#725DE0; }
            QPushButton:checked {
                background:#704EF0;border-color:#A58FFF;color:white;
            }
            QScrollArea { background:transparent;border:none; }
            QScrollBar:vertical { background:transparent;width:8px; }
            QScrollBar::handle:vertical {
                background:#514A91;border-radius:4px;min-height:30px;
            }
        """)
        self.pick(0)

    def pick(self, index):
        symbol, word, visual = self.items[index]
        self.symbol.setText(symbol)
        self.word.setText(word)
        self.visual.setText(visual)

        # Avoid long labels such as GREEN/ORANGE clipping inside the symbol tile.
        length = len(symbol)
        if length >= 6:
            size = 31
        elif length >= 4:
            size = 39
        else:
            size = 58
        self.symbol.setStyleSheet(
            "background:#7150EE;color:white;border-radius:34px;"
            f"font-size:{size}px;font-weight:950;padding:8px;"
        )

        for i, button in enumerate(self.buttons):
            button.setChecked(i == index)


class MathPlayground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.score = 0
        self.total = 0
        self.op = "+"
        self.op_buttons = []
        self._build()
        self.set_op("+")

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(15)

        ops = QHBoxLayout()
        for text, op in (
            ("➕  Addition", "+"),
            ("➖  Subtraction", "-"),
            ("✖  Multiplication", "×"),
            ("➗  Division", "÷"),
        ):
            button = QPushButton(text)
            button.setCheckable(True)
            button.setFixedHeight(46)
            button.clicked.connect(lambda _, x=op: self.set_op(x))
            ops.addWidget(button)
            self.op_buttons.append((button, op))
        root.addLayout(ops)

        card = QFrame()
        card.setObjectName("MathCard")
        box = QVBoxLayout(card)
        box.setContentsMargins(34, 28, 34, 28)
        box.setSpacing(14)

        self.score_label = QLabel("⭐  Score: 0 / 0")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size:13px;font-weight:900;")

        self.question = QLabel()
        self.question.setAlignment(Qt.AlignCenter)
        self.question.setStyleSheet(
            "font-size:44px;font-weight:950;color:white;"
        )

        self.feedback = QLabel("Pick the correct answer!")
        self.feedback.setAlignment(Qt.AlignCenter)
        self.feedback.setStyleSheet("font-size:12px;")

        self.answers = QHBoxLayout()
        self.answers.setSpacing(12)

        box.addWidget(self.score_label)
        box.addWidget(self.question)
        box.addWidget(self.feedback)
        box.addLayout(self.answers)
        root.addWidget(card)
        root.addStretch()

        self.setStyleSheet("""
            QFrame#MathCard {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #2347A8,stop:1 #703AD1);
                border:1px solid #6555C5;border-radius:24px;
            }
            QLabel { color:#E9E6FF;background:transparent; }
            QPushButton {
                color:white;background:#211B55;border:1px solid #5143A3;
                border-radius:12px;padding:10px;font-size:12px;font-weight:900;
            }
            QPushButton:hover, QPushButton:checked { background:#6D4DEB; }
        """)

    def set_op(self, op):
        self.op = op
        for button, value in self.op_buttons:
            button.setChecked(value == op)
        self.new_question()

    def new_question(self):
        if self.op == "+":
            a, b = random.randint(1, 50), random.randint(1, 50)
            answer = a + b
        elif self.op == "-":
            a, b = random.randint(1, 100), random.randint(1, 50)
            a, b = max(a, b), min(a, b)
            answer = a - b
        elif self.op == "×":
            a, b = random.randint(1, 12), random.randint(1, 12)
            answer = a * b
        else:
            b = random.randint(1, 12)
            answer = random.randint(1, 12)
            a = b * answer

        self.correct = answer
        self.question.setText(f"{a}  {self.op}  {b}  =  ?")
        self.feedback.setText("Pick the correct answer!")

        while self.answers.count():
            widget = self.answers.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        values = {answer}
        while len(values) < 4:
            values.add(max(0, answer + random.randint(-10, 10)))
        values = list(values)
        random.shuffle(values)

        for value in values:
            button = QPushButton(str(value))
            button.setFixedHeight(54)
            button.clicked.connect(lambda _, x=value: self.answer(x))
            self.answers.addWidget(button)

    def answer(self, value):
        self.total += 1
        if value == self.correct:
            self.score += 1
            self.feedback.setText("🌟 Correct! Great job!")
            QTimer.singleShot(650, self.new_question)
        else:
            self.feedback.setText("💜 Try again!")
        self.score_label.setText(f"⭐  Score: {self.score} / {self.total}")


class StudyLearnScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_data()
        self._build_ui()
        self.show_hub()

    def _build_data(self):
        letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        words = [
            "Apple","Ball","Cat","Dog","Elephant","Fish","Grapes","House",
            "Ice Cream","Juice","Kite","Lion","Moon","Nest","Orange","Parrot",
            "Queen","Rainbow","Star","Tree","Umbrella","Van","Whale",
            "Xylophone","Yo-Yo","Zebra"
        ]
        pics = [
            "🍎","⚽","🐱","🐶","🐘","🐟","🍇","🏠","🍦","🧃","🪁","🦁",
            "🌙","🪺","🍊","🦜","👑","🌈","⭐","🌳","☂️","🚐","🐋","🎼","🪀","🦓"
        ]
        self.eng = [(l, f"{l} is for {w}", p) for l, w, p in zip(letters, words, pics)]

        # Compact base-ten pictorial reference.
        # We deliberately do NOT draw N repeated objects: 4-100 would crowd/clip.
        # Instead children see a stable visual model: ones, tens + ones, or 100.
        self.nums = []
        for number in range(1, 101):
            visual = self.number_visual(number)
            self.nums.append(
                (str(number), f"{number} • {self.number_word(number)}", visual)
            )

        self.hindi = [
            ("अ","अ से अनार","🍎"),("आ","आ से आम","🥭"),("इ","इ से इमली","🌿"),
            ("ई","ई से ईख","🎋"),("उ","उ से उल्लू","🦉"),("ऊ","ऊ से ऊन","🧶"),
            ("ऋ","ऋ से ऋषि","🧘"),("ए","ए से एड़ी","🦶"),("ऐ","ऐ से ऐनक","👓"),
            ("ओ","ओ से ओखली","🥣"),("औ","औ से औरत","👩"),("अं","अं से अंगूर","🍇"),
            ("अः","अः","✨"),("क","क से कबूतर","🕊️"),("ख","ख से खरगोश","🐰"),
            ("ग","ग से गमला","🪴"),("घ","घ से घर","🏠"),("ङ","ङ","🔤"),
            ("च","च से चम्मच","🥄"),("छ","छ से छतरी","☂️"),("ज","ज से जहाज","✈️"),
            ("झ","झ से झंडा","🚩"),("ञ","ञ","🔤"),("ट","ट से टमाटर","🍅"),
            ("ठ","ठ से ठेला","🛒"),("ड","ड से डमरू","🥁"),("ढ","ढ से ढक्कन","⭕"),
            ("ण","ण","🔤"),("त","त से तरबूज","🍉"),("थ","थ से थर्मस","🧴"),
            ("द","द से दवात","🖋️"),("ध","ध से धनुष","🏹"),("न","न से नल","🚰"),
            ("प","प से पतंग","🪁"),("फ","फ से फल","🍎"),("ब","ब से बकरी","🐐"),
            ("भ","भ से भालू","🐻"),("म","म से मछली","🐟"),("य","य से यज्ञ","🔥"),
            ("र","र से रथ","🛞"),("ल","ल से लड्डू","🍬"),("व","व से वन","🌳"),
            ("श","श से शेर","🦁"),("ष","ष से षट्कोण","⬡"),("स","स से सेब","🍎"),
            ("ह","ह से हाथी","🐘"),("क्ष","क्ष से क्षत्रिय","🛡️"),
            ("त्र","त्र से त्रिशूल","🔱"),("ज्ञ","ज्ञ से ज्ञान","📚")
        ]

        french_words = [
            "Avion","Ballon","Chat","Dauphin","Étoile","Fleur","Girafe","Hibou",
            "Île","Jardin","Kiwi","Lion","Maison","Nuage","Orange","Poisson",
            "Quatre","Robot","Soleil","Tortue","Uniforme","Vélo","Wagon",
            "Xylophone","Yo-yo","Zèbre"
        ]
        french_pics = [
            "✈️","🎈","🐱","🐬","⭐","🌸","🦒","🦉","🏝️","🌳","🥝","🦁",
            "🏠","☁️","🍊","🐟","4️⃣","🤖","☀️","🐢","👕","🚲","🚃","🎼","🪀","🦓"
        ]
        self.fr = [
            (l, f"{l} comme {w}", p)
            for l, w, p in zip(letters, french_words, french_pics)
        ]

        self.colors = [
            ("RED","Red Circle","🔴"),("BLUE","Blue Circle","🔵"),
            ("GREEN","Green Circle","🟢"),("YELLOW","Yellow Circle","🟡"),
            ("ORANGE","Orange Circle","🟠"),("PURPLE","Purple Circle","🟣"),
            ("○","Circle","⭕"),("□","Square","🟦"),("△","Triangle","🔺"),
            ("★","Star","⭐"),("♥","Heart","💜"),("◇","Diamond","🔷")
        ]

    def _build_ui(self):
        self.setStyleSheet("background:#0D0A2B;")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 22)
        root.setSpacing(12)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("🎓  Study & Learn")
        title.setStyleSheet("color:white;font-size:29px;font-weight:950;")
        subtitle = QLabel("Choose a learning world, then explore it at your own pace.")
        subtitle.setStyleSheet("color:#B8B2E2;font-size:12px;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.back_button = QPushButton("←  Study Home")
        self.back_button.setFixedHeight(40)
        self.back_button.clicked.connect(self.show_hub)
        self.back_button.setStyleSheet(
            "QPushButton{color:white;background:#21185A;border:1px solid #6048D8;"
            "border-radius:12px;padding:0 15px;font-size:10px;font-weight:900;}"
        )
        header.addLayout(title_box, 1)
        header.addWidget(self.back_button, 0, Qt.AlignBottom)
        root.addLayout(header)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        # Page 0: Settings-style category hub.
        hub = QWidget()
        hub_layout = QVBoxLayout(hub)
        hub_layout.setContentsMargins(0, 8, 0, 0)
        hub_layout.setSpacing(14)

        intro = QFrame()
        intro.setObjectName("StudyIntro")
        intro_box = QHBoxLayout(intro)
        intro_box.setContentsMargins(22, 18, 22, 18)
        intro_icon = QLabel("🌈")
        intro_icon.setStyleSheet("font-size:38px;")
        intro_copy = QVBoxLayout()
        intro_title = QLabel("Pick what you want to learn")
        intro_title.setStyleSheet("color:white;font-size:20px;font-weight:950;")
        intro_text = QLabel(
            "Letters, numbers, Hindi, French, colors & shapes, or interactive kids math."
        )
        intro_text.setStyleSheet("color:#C4BEEA;font-size:11px;")
        intro_copy.addWidget(intro_title)
        intro_copy.addWidget(intro_text)
        intro_box.addWidget(intro_icon)
        intro_box.addSpacing(10)
        intro_box.addLayout(intro_copy, 1)
        intro.setStyleSheet(
            "QFrame#StudyIntro{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #233F9C,stop:1 #6939C6);border:1px solid #5D52B7;border-radius:20px;}"
        )
        hub_layout.addWidget(intro)

        grid = QGridLayout()
        grid.setSpacing(12)
        categories = [
            ("🔤","Alphabets","A–Z with large visual examples","#8F78FF"),
            ("🔢","Numbers 1–100","Count, read and understand tens & ones","#6ED4FF"),
            ("🇮🇳","हिंदी वर्णमाला","स्वर और व्यंजन चित्रों के साथ","#FFB15A"),
            ("🇫🇷","French Alphabet","A–Z with simple French vocabulary","#FF7DAE"),
            ("🎨","Colors & Shapes","Colors, circles, squares, stars & more","#6FE0A9"),
            ("🧮","Kids Math","Addition, subtraction, multiplication & division","#FFD75A"),
        ]
        for i, data in enumerate(categories):
            card = StudyCategoryCard(i, *data, hub)
            card.requested.connect(self.open_category)
            row, col = divmod(i, 3)
            grid.addWidget(card, row, col)
        hub_layout.addLayout(grid)
        hub_layout.addStretch()
        self.stack.addWidget(hub)

        detail_pages = [
            LearningDeck("Tap a letter and visualize the word.", self.eng, 9, parent=self),
            LearningDeck("Explore every number from 1 to 100.", self.nums, 10, parent=self),
            LearningDeck("स्वर और व्यंजन चित्र के साथ सीखें।", self.hindi, 10, parent=self),
            LearningDeck("Choisis une lettre et découvre un mot.", self.fr, 9, parent=self),
            LearningDeck("Learn colors and simple shapes.", self.colors, 9, parent=self),
            MathPlayground(self),
        ]
        for page in detail_pages:
            self.stack.addWidget(page)

        self.setStyleSheet(self.styleSheet() + """
            QWidget { background:#0D0A2B; }
        """)

    def show_hub(self):
        self.stack.setCurrentIndex(0)
        self.back_button.hide()

    def open_category(self, index):
        self.stack.setCurrentIndex(index + 1)
        self.back_button.show()

    @staticmethod
    def number_visual(number):
        """Compact child-friendly base-ten picture for every number 1-100."""
        if number < 10:
            return f"⭐  ×  {number}"

        if number == 100:
            return "💯\n10 tens"

        tens, ones = divmod(number, 10)
        if ones == 0:
            return f"🔟  ×  {tens}"

        return f"🔟  ×  {tens}\n⭐  ×  {ones}"

    @staticmethod
    def number_word(number):
        ones = [
            "Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine",
            "Ten","Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen",
            "Seventeen","Eighteen","Nineteen"
        ]
        tens = ["","","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]
        if number < 20:
            return ones[number]
        if number < 100:
            return tens[number // 10] + (
                (" " + ones[number % 10]) if number % 10 else ""
            )
        return "One Hundred"
