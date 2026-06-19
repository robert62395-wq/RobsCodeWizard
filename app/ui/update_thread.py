"""QThread wrapper around updater.check_for_update."""
from PySide6.QtCore import QThread, Signal
from app.services.updater import check_for_update


class UpdateCheckThread(QThread):
    result_ready = Signal(object)
    error = Signal(str)

    def __init__(self, current_version, manifest_url, parent=None):
        super().__init__(parent)
        self._current = current_version
        self._url = manifest_url

    def run(self):
        try:
            info = check_for_update(self._current, self._url)
            self.result_ready.emit(info)
        except Exception as exc:
            self.error.emit(str(exc))
