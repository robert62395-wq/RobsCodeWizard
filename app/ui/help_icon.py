"""Reusable help icon button (v0.5.2)."""
from __future__ import annotations
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QToolButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
)

from app.services.settings import load_settings, set_setting
from app.ui.help_dialogs import HELP_TOPICS


class HelpIcon(QToolButton):
    def __init__(self, topic_id, parent=None):
        super().__init__(parent)
        self._topic_id = topic_id
        self.setText("?")
        self.setFixedSize(QSize(18, 18))
        font = QFont()
        font.setBold(True)
        self.setFont(font)
        self.setStyleSheet(
            "QToolButton { border: 1px solid palette(mid); border-radius: 9px;"
            " background-color: palette(button); color: palette(button-text); }"
            "QToolButton:hover { background-color: palette(highlight);"
            " color: palette(highlighted-text); }"
        )
        title, _ = HELP_TOPICS.get(topic_id, (topic_id, ""))
        self.setToolTip(f"Help: {title}")
        self.clicked.connect(self._show_help)

    def _show_help(self):
        settings = load_settings()
        suppressed = settings.get("suppressed_help", []) or []
        if self._topic_id in suppressed:
            return
        title, body = HELP_TOPICS.get(self._topic_id, (self._topic_id, "<i>No help available.</i>"))
        dlg = HelpDialog(title, body, self._topic_id, parent=self)
        dlg.exec()


class HelpDialog(QDialog):
    def __init__(self, title, body_html, topic_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Help: {title}")
        self.setMinimumWidth(450)
        self._topic_id = topic_id
        layout = QVBoxLayout(self)
        content = QLabel(body_html)
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setOpenExternalLinks(True)
        content.setMinimumWidth(420)
        layout.addWidget(content)
        self.suppress_cb = QCheckBox("Don't show this help again")
        layout.addWidget(self.suppress_cb)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok = QPushButton("Got it")
        ok.clicked.connect(self._on_ok)
        ok.setDefault(True)
        btn_row.addWidget(ok)
        layout.addLayout(btn_row)

    def _on_ok(self):
        if self.suppress_cb.isChecked():
            settings = load_settings()
            suppressed = settings.get("suppressed_help", []) or []
            if self._topic_id not in suppressed:
                suppressed.append(self._topic_id)
                set_setting("suppressed_help", suppressed)
        self.accept()