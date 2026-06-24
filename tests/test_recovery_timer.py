"""Tests for v0.5.3.1 recovery timer."""
import pytest

# Note: these tests don't run the actual QTimer - they exercise the dirty/save logic only.


class FakeTimer:
    """Drop-in for QTimer that doesn't actually tick."""
    
    def __init__(self):
        self._interval = 0
        self._active = False
        self.timeout_callback = None
    
    def setInterval(self, ms):
        self._interval = ms
    
    def interval(self):
        return self._interval
    
    def isActive(self):
        return self._active
    
    def start(self):
        self._active = True
    
    def stop(self):
        self._active = False
    
    @property
    def timeout(self):
        return self
    
    def connect(self, cb):
        self.timeout_callback = cb


def _make_timer(monkeypatch):
    """Create a RecoveryTimer with a fake QTimer for unit testing."""
    from app.services import recovery_timer as rt
    
    fake = FakeTimer()
    monkeypatch.setattr(rt, "QTimer", lambda parent=None: fake)
    timer = rt.RecoveryTimer(parent=None, interval_ms=300000)
    return timer, fake


def test_starts_clean_not_dirty(monkeypatch):
    timer, fake = _make_timer(monkeypatch)
    saved = []
    timer.set_save_callback(lambda: saved.append("save"))
    timer._tick()
    assert saved == []  # not dirty, nothing saved


def test_mark_dirty_then_tick_saves(monkeypatch):
    timer, fake = _make_timer(monkeypatch)
    saved = []
    timer.set_save_callback(lambda: saved.append("save"))
    timer.mark_dirty()
    timer._tick()
    assert saved == ["save"]


def test_tick_clears_dirty_flag(monkeypatch):
    timer, fake = _make_timer(monkeypatch)
    saved = []
    timer.set_save_callback(lambda: saved.append("save"))
    timer.mark_dirty()
    timer._tick()
    timer._tick()  # should be no-op now
    assert saved == ["save"]


def test_disables_after_repeated_failures(monkeypatch):
    timer, fake = _make_timer(monkeypatch)
    
    def boom():
        raise RuntimeError("disk full")
    
    timer.set_save_callback(boom)
    fake.start()
    
    for _ in range(3):
        timer.mark_dirty()
        timer._tick()
    
    assert fake.isActive() is False  # disabled itself


def test_force_save_now_triggers_save(monkeypatch):
    timer, fake = _make_timer(monkeypatch)
    saved = []
    timer.set_save_callback(lambda: saved.append("save"))
    timer.mark_dirty()
    timer.force_save_now()
    assert saved == ["save"]