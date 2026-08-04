from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)


class TitleBar(QWidget):

    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.drag_position = QPoint()

        self.setFixedHeight(52)

        self.build_ui()

    def build_ui(self):

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(12)

        # -----------------------------
        # Logo
        # -----------------------------

        self.logo = QLabel("🎵 NirVANA")

        self.logo.setStyleSheet("""
            QLabel{
                color:white;
                font-size:24px;
                font-weight:700;
            }
        """)

        layout.addWidget(self.logo)

        layout.addStretch()

        # -----------------------------
        # Minimize Button
        # -----------------------------

        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(40,40)

        # -----------------------------
        # Maximize Button
        # -----------------------------

        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(40,40)

        # -----------------------------
        # Close Button
        # -----------------------------

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40,40)

        button_style = """
        QPushButton{
            background:transparent;
            color:white;
            border:none;
            font-size:16px;
            border-radius:8px;
        }

        QPushButton:hover{
            background:#6E44FF;
        }
        """

        self.min_btn.setStyleSheet(button_style)
        self.max_btn.setStyleSheet(button_style)
        self.close_btn.setStyleSheet(button_style)

        self.close_btn.setStyleSheet("""
        QPushButton{
            background:transparent;
            color:white;
            border:none;
            font-size:16px;
            border-radius:8px;
        }

        QPushButton:hover{
            background:#E81123;
        }
        """)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        # -----------------------------
        # Signals
        # -----------------------------

        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.max_btn.clicked.connect(self.toggle_max_restore)
        self.close_btn.clicked.connect(self.parent.close)

    # ------------------------------------
    # Maximize / Restore
    # ------------------------------------

    def toggle_max_restore(self):

        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    # ------------------------------------
    # Drag Window
    # ------------------------------------

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.parent.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.LeftButton:
            self.parent.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )