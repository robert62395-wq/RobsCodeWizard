"""Tiny modal dialog with an indeterminate progress bar."""
from contextlib import contextmanager
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QApplication, QDialog, QLabel, QProgressBar, QVBoxLayout,
)


class BusyDialog(QDialog):
    """Modal please-wait dialog with an indeterminate progress bar."""

    def __init__(self, parent=None, text="Working..."):
        super().__init__(parent)
        self.setWindowTitle("Please wait")
        self.setModal(True)
        flags = Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint
        self.setWindowFlags(flags)
        self.setFixedSize(320, 110)

        layout = QVBoxLayout(self)
        self._label = QLabel(text)
        self._bar = QProgressBar()
        self._bar.setRange(0, 0)
        layout.addWidget(self._label)
        layout.addWidget(self._bar)

    def set_text(self, text):
        self._label.setText(text)
        QApplication.processEvents()

    def showEvent(self, event):
        super().showEvent(event)
        QApplication.processEvents()


@contextmanager
def busy(parent=None, text="Working..."):
    app = QApplication.instance()
    dlg = BusyDialog(parent, text)
    if app is not None:
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    dlg.show()
    QApplication.processEvents()
    try:
        yield dlg
    finally:
        dlg.close()
        if app is not None:
            QApplication.restoreOverrideCursor()
        QApplication.processEvents()
