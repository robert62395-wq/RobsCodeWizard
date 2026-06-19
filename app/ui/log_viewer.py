"""Read-only viewer for the recent log tail."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton,
)
from PySide6.QtGui import QGuiApplication


class LogViewerDialog(QDialog):
    def __init__(self, log_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recent Log")
        self.resize(720, 480)
        layout = QVBoxLayout(self)
        self._text = QPlainTextEdit(self)
        self._text.setReadOnly(True)
        self._text.setPlainText(log_text or "(log is empty)")
        layout.addWidget(self._text)
        buttons = QHBoxLayout()
        copy_btn = QPushButton("Copy to Clipboard", self)
        copy_btn.clicked.connect(self._copy)
        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.accept)
        buttons.addStretch(1); buttons.addWidget(copy_btn); buttons.addWidget(close_btn)
        layout.addLayout(buttons)

    def _copy(self):
        QGuiApplication.clipboard().setText(self._text.toPlainText())
