"""QThread wrappers for updater operations (v0.3.9.5.1.5)."""
from PySide6.QtCore import QThread, Signal
from app.services.updater import (
    check_for_update,
    download_asset,
    DEFAULT_REPO,
)


class UpdateCheckThread(QThread):
    """Background check for newer release on GitHub."""
    result_ready = Signal(object)
    error = Signal(str)

    def __init__(self, current_version, repo=None, parent=None):
        super().__init__(parent)
        self._current = current_version
        self._repo = repo or DEFAULT_REPO

    def run(self):
        try:
            info = check_for_update(self._current, self._repo)
            self.result_ready.emit(info)
        except Exception as exc:
            self.error.emit(str(exc))


class UpdateDownloadThread(QThread):
    """Background download of a release asset with progress reporting."""
    progress = Signal(int, int)
    finished_with_path = Signal(object)
    error = Signal(str)

    def __init__(self, asset, dest_dir, parent=None):
        super().__init__(parent)
        self._asset = asset
        self._dest = dest_dir

    def run(self):
        try:
            def cb(done, total):
                self.progress.emit(done, total or 0)
            path = download_asset(self._asset, self._dest, progress_cb=cb)
            self.finished_with_path.emit(path)
        except Exception as exc:
            self.error.emit(str(exc))

