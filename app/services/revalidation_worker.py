"""QThread worker for code-set switch revalidation (v0.3.9.5.2.0.1 diagnostic)."""
import logging
import time
from PySide6.QtCore import QThread, Signal
from app.services.validator import validate_rows
from app.services.suggester import build_suggestions

log = logging.getLogger("robs_code_wizard")


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
            t0 = time.perf_counter()
            log.info("[diag] worker thread started (%d rows)", len(self._rows))
            self.stage.emit("Validating codes...")
            self.progress.emit(10)
            t1 = time.perf_counter()
            results = validate_rows(self._rows, self._codeset)
            t2 = time.perf_counter()
            log.info("[diag] validate_rows: %.3fs (%d results)", t2 - t1, len(results))
            self.progress.emit(50)
            self.stage.emit("Building suggestions...")
            t3 = time.perf_counter()
            suggestions = build_suggestions(self._rows, self._codeset, results)
            t4 = time.perf_counter()
            log.info("[diag] build_suggestions: %.3fs", t4 - t3)
            self.progress.emit(100)
            log.info("[diag] worker total: %.3fs, emitting finished_with_data", t4 - t0)
            self.finished_with_data.emit(results, suggestions)
        except Exception as exc:
            log.exception("[diag] worker raised: %s", exc)
            self.error_message.emit(str(exc))
