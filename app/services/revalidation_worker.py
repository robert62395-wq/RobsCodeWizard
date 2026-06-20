"""QThread worker for code-set switch revalidation (v0.3.9.5.1.6)."""
from PySide6.QtCore import QThread, Signal
from app.services.validator import validate_rows
from app.services.suggester import build_suggestions


class RevalidationWorker(QThread):
    """Run validate_rows + build_suggestions off the main thread."""
    stage = Signal(str)
    progress = Signal(int)
    finished_with_data = Signal(object, object)
    error_message = Signal(str)

    def __init__(self, rows, codeset, parent=None):
        super().__init__(parent)
        self._rows = list(rows)
        self._codeset = codeset

    def run(self):
        try:
            self.stage.emit("Validating codes...")
            self.progress.emit(10)
            results = validate_rows(self._rows, self._codeset)
            self.progress.emit(50)
            self.stage.emit("Building suggestions...")
            suggestions = build_suggestions(self._rows, self._codeset, results)
            self.progress.emit(100)
            self.finished_with_data.emit(results, suggestions)
        except Exception as exc:
            self.error_message.emit(str(exc))

