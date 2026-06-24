"""Auto-save recovery timer (v0.5.3.1).

Manages a Qt timer that periodically calls recovery.save_session(...) during
long edit sessions. The MainWindow creates one of these on startup and feeds
it the current rows reference; the timer wakes every 5 minutes and snapshots
the data.

A 'dirty' flag is provided so callers can short-circuit no-op writes.
"""
from __future__ import annotations
import logging
from PySide6.QtCore import QTimer, QObject

log = logging.getLogger("robs_code_wizard")

DEFAULT_INTERVAL_MS = 5 * 60 * 1000   # 5 minutes


class RecoveryTimer(QObject):
    """Periodically calls a save callback with the current row snapshot.
    
    Usage:
        self._recovery_timer = RecoveryTimer(self)
        self._recovery_timer.set_save_callback(
            lambda: recovery.save_session(
                self.rows,
                source_path=self.source_path,
                suggestions=self.suggestions,
            )
        )
        self._recovery_timer.start()
        
        # When data changes:
        self._recovery_timer.mark_dirty()
    """
    
    def __init__(self, parent=None, interval_ms=DEFAULT_INTERVAL_MS):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._tick)
        self._save_callback = None
        self._dirty = False
        self._fail_count = 0
        self._max_failures_before_disable = 3
    
    def set_save_callback(self, callback):
        self._save_callback = callback
    
    def mark_dirty(self):
        """Mark that there is something new to save."""
        self._dirty = True
    
    def start(self):
        if not self._timer.isActive():
            self._timer.start()
            log.info("RecoveryTimer started (interval=%dms)", self._timer.interval())
    
    def stop(self):
        if self._timer.isActive():
            self._timer.stop()
            log.info("RecoveryTimer stopped")
    
    def force_save_now(self):
        """Trigger a save immediately if dirty."""
        self._tick()
    
    def _tick(self):
        if not self._dirty:
            return
        if self._save_callback is None:
            return
        try:
            self._save_callback()
            self._dirty = False
            self._fail_count = 0
            log.debug("RecoveryTimer auto-saved successfully")
        except Exception as exc:
            self._fail_count += 1
            log.exception("RecoveryTimer save failed: %s", exc)
            if self._fail_count >= self._max_failures_before_disable:
                log.error(
                    "RecoveryTimer disabled after %d consecutive save failures",
                    self._fail_count,
                )
                self.stop()