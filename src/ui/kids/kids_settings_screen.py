from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QCheckBox, QMessageBox, QInputDialog, QLineEdit
)

from ui.kids.kids_parental import KidsParentalControls


class SafetyToggle(QFrame):
    changed = Signal(bool)

    def __init__(self, emoji, title, description, checked=False, parent=None):
        super().__init__(parent)
        self.setObjectName("SafetyToggle")
        row = QHBoxLayout(self)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(12)

        icon = QLabel(emoji)
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(42, 42)
        icon.setStyleSheet(
            "background:#29205E;border-radius:13px;font-size:20px;"
        )

        copy = QVBoxLayout()
        copy.setSpacing(2)
        heading = QLabel(title)
        heading.setStyleSheet("color:white;font-size:12px;font-weight:900;")
        detail = QLabel(description)
        detail.setWordWrap(True)
        detail.setStyleSheet("color:#AAA4D3;font-size:9px;")
        copy.addWidget(heading)
        copy.addWidget(detail)

        self.toggle = QCheckBox()
        self.toggle.setChecked(checked)
        self.toggle.setCursor(Qt.PointingHandCursor)
        self.toggle.stateChanged.connect(
            lambda state: self.changed.emit(state == Qt.Checked.value)
        )

        row.addWidget(icon)
        row.addLayout(copy, 1)
        row.addWidget(self.toggle)

        self.setStyleSheet("""
            QFrame#SafetyToggle {
                background:#15113C;border:1px solid #302A66;border-radius:16px;
            }
            QFrame#SafetyToggle:hover { border-color:#5549A9; }
            QCheckBox::indicator { width:42px;height:22px; }
            QCheckBox::indicator:unchecked {
                image:none;background:#37315D;border:1px solid #575079;border-radius:11px;
            }
            QCheckBox::indicator:checked {
                image:none;background:#28C891;border:1px solid #61E6B9;border-radius:11px;
            }
        """)


class KidsSettingsScreen(QWidget):
    controls_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controls = KidsParentalControls()
        self._build()
        self._refresh_pin_card()

    def _build(self):
        self.setStyleSheet("background:#0D0A2B;")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 24)
        root.setSpacing(12)

        title = QLabel("⚙️  Kids Settings")
        title.setStyleSheet("color:white;font-size:28px;font-weight:950;")
        subtitle = QLabel(
            "Parent-managed safety controls for the LYRx Kids experience."
        )
        subtitle.setStyleSheet("color:#B8B2E2;font-size:11px;")
        root.addWidget(title)
        root.addWidget(subtitle)

        safe_head = QLabel("🛡️  CONTENT & DISCOVERY")
        safe_head.setStyleSheet(
            "color:#7BEFD1;font-size:10px;font-weight:900;margin-top:8px;"
        )
        root.addWidget(safe_head)

        self.safe_search = SafetyToggle(
            "🔎", "Safe Search",
            "Rejects clearly unsafe search terms before provider discovery starts.",
            self.controls.safe_search, self
        )
        self.explicit = SafetyToggle(
            "🚫", "Block Explicit Content",
            "Adds an extra metadata filter for clearly explicit/adult-labelled results.",
            self.controls.block_explicit, self
        )
        self.harmful = SafetyToggle(
            "🛡️", "Block Harmful Content",
            "Adds an extra metadata filter for clearly harmful child-inappropriate terms.",
            self.controls.block_harmful, self
        )
        self.external = SafetyToggle(
            "🔗", "No External Links",
            "Keeps Kids Mode from opening external web links. Stored now for current/future Kids features.",
            self.controls.block_external_links, self
        )

        self.safe_search.changed.connect(lambda v:self._set("safe_search", v))
        self.explicit.changed.connect(lambda v:self._set("block_explicit", v))
        self.harmful.changed.connect(lambda v:self._set("block_harmful", v))
        self.external.changed.connect(lambda v:self._set("block_external_links", v))

        for card in (self.safe_search, self.explicit, self.harmful, self.external):
            root.addWidget(card)

        pin_head = QLabel("🔐  PARENT EXIT LOCK")
        pin_head.setStyleSheet(
            "color:#FFD76B;font-size:10px;font-weight:900;margin-top:10px;"
        )
        root.addWidget(pin_head)

        self.pin_card = QFrame()
        self.pin_card.setObjectName("PinCard")
        pin_row = QHBoxLayout(self.pin_card)
        pin_row.setContentsMargins(16, 14, 16, 14)

        pin_copy = QVBoxLayout()
        self.pin_title = QLabel()
        self.pin_title.setStyleSheet("color:white;font-size:13px;font-weight:900;")
        self.pin_text = QLabel()
        self.pin_text.setStyleSheet("color:#AAA4D3;font-size:9px;")
        pin_copy.addWidget(self.pin_title)
        pin_copy.addWidget(self.pin_text)

        self.pin_action = QPushButton()
        self.pin_action.setObjectName("Primary")
        self.pin_action.setCursor(Qt.PointingHandCursor)
        self.pin_action.setFixedHeight(38)
        self.pin_action.clicked.connect(self._pin_action)

        self.remove_pin_btn = QPushButton("Remove PIN")
        self.remove_pin_btn.setObjectName("Danger")
        self.remove_pin_btn.setCursor(Qt.PointingHandCursor)
        self.remove_pin_btn.setFixedHeight(38)
        self.remove_pin_btn.clicked.connect(self._remove_pin)

        pin_row.addLayout(pin_copy, 1)
        pin_row.addWidget(self.pin_action)
        pin_row.addWidget(self.remove_pin_btn)

        self.pin_card.setStyleSheet("""
            QFrame#PinCard {
                background:#171342;border:1px solid #554184;border-radius:17px;
            }
            QPushButton#Primary {
                color:white;background:#6D4DEB;border:none;border-radius:12px;
                padding:0 16px;font-size:10px;font-weight:900;
            }
            QPushButton#Primary:hover { background:#8261F4; }
            QPushButton#Danger {
                color:#FFD8E1;background:#51203A;border:1px solid #7B3555;
                border-radius:12px;padding:0 14px;font-size:10px;font-weight:850;
            }
            QPushButton#Danger:hover { background:#722B4A; }
        """)
        root.addWidget(self.pin_card)

        note = QLabel(
            "ℹ️  These controls are an app-level parental gate and filtering layer. "
            "Provider metadata can be incomplete, so LYRx does not treat keyword "
            "filtering as a guarantee that every online result is child-safe."
        )
        note.setWordWrap(True)
        note.setStyleSheet(
            "color:#9C96C9;background:#121035;border:1px solid #2E2960;"
            "border-radius:14px;padding:12px;font-size:9px;"
        )
        root.addWidget(note)
        root.addStretch()

    def _set(self, key, value):
        self.controls.set_bool(key, value)
        self.controls_changed.emit()

    def _ask_pin(self, title, prompt):
        value, ok = QInputDialog.getText(
            self, title, prompt, QLineEdit.Password
        )
        return str(value).strip(), ok

    def _pin_action(self):
        if self.controls.exit_pin_enabled:
            old, ok = self._ask_pin("Verify Parent PIN", "Enter current parent PIN:")
            if not ok:
                return
            if not self.controls.verify_pin(old):
                QMessageBox.warning(self, "Incorrect PIN", "That parent PIN is incorrect.")
                return

        pin, ok = self._ask_pin(
            "Set Parent PIN",
            "Create a 4–6 digit PIN required to leave Kids Mode:"
        )
        if not ok:
            return
        if not self.controls.valid_pin_format(pin):
            QMessageBox.warning(
                self, "Invalid PIN", "Please use a 4–6 digit numeric PIN."
            )
            return

        confirm, ok = self._ask_pin("Confirm Parent PIN", "Enter the new PIN again:")
        if not ok:
            return
        if pin != confirm:
            QMessageBox.warning(self, "PINs Do Not Match", "The two PINs did not match.")
            return

        self.controls.set_pin(pin)
        self._refresh_pin_card()
        self.controls_changed.emit()
        QMessageBox.information(
            self, "Parent PIN Active",
            "The parent PIN is now required when Back to LYRx is used."
        )

    def _remove_pin(self):
        if not self.controls.exit_pin_enabled:
            return
        old, ok = self._ask_pin("Remove Parent PIN", "Enter current parent PIN:")
        if not ok:
            return
        if not self.controls.verify_pin(old):
            QMessageBox.warning(self, "Incorrect PIN", "That parent PIN is incorrect.")
            return
        self.controls.remove_pin()
        self._refresh_pin_card()
        self.controls_changed.emit()

    def _refresh_pin_card(self):
        enabled = self.controls.exit_pin_enabled
        self.pin_title.setText(
            "🔒 Exit PIN is ON" if enabled else "🔓 Exit PIN is OFF"
        )
        self.pin_text.setText(
            "Back to LYRx requires the parent PIN."
            if enabled else
            "Set a PIN so a child cannot leave Kids Mode using the in-app exit button."
        )
        self.pin_action.setText("Change PIN" if enabled else "Set Parent PIN")
        self.remove_pin_btn.setVisible(enabled)
