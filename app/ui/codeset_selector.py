"""Code-set dropdown for the Raw Data toolbar."""
from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Signal


class CodeSetSelector(QComboBox):
    codesetChanged = Signal(str)
    _ITEMS = [("VDT", "vdt"), ("ODOT", "odot")]

    def __init__(self, parent=None):
        super().__init__(parent)
        for label, key in self._ITEMS:
            self.addItem(label, key)
        self.currentIndexChanged.connect(self._on_index_changed)

    def _on_index_changed(self, _):
        name = self.itemData(self.currentIndex())
        if name:
            self.codesetChanged.emit(name)

    def set_active(self, name: str):
        if not name:
            return
        target = name.strip().lower()
        for i in range(self.count()):
            if self.itemData(i) == target:
                blocked = self.blockSignals(True)
                try:
                    self.setCurrentIndex(i)
                finally:
                    self.blockSignals(blocked)
                return

    def current_codeset(self) -> str:
        return self.itemData(self.currentIndex()) or "vdt"
