"""Tests for v0.5.3 safe_handler decorator."""
import pytest
from app.services.safe_event_handler import safe_handler


class FakeWidget:
    """Mock widget with the helpers safe_handler looks for."""
    
    def __init__(self):
        self.flashed = None
        self.dialog_shown = None
    
    def _flash_status(self, msg, msec=5000):
        self.flashed = (msg, msec)
    
    def _error_dialog(self, title, exc):
        self.dialog_shown = (title, str(exc))


def test_minor_severity_flashes_status_bar():
    widget = FakeWidget()
    
    @safe_handler(severity="minor")
    def boom(self):
        raise ValueError("oh no")
    
    boom(widget)
    
    assert widget.flashed is not None
    assert "oh no" in widget.flashed[0]
    assert widget.dialog_shown is None


def test_severe_severity_shows_dialog():
    widget = FakeWidget()
    
    @safe_handler(severity="severe")
    def fail_hard(self):
        raise RuntimeError("catastrophe")
    
    fail_hard(widget)
    
    assert widget.dialog_shown is not None
    assert "fail_hard" in widget.dialog_shown[0]
    assert "catastrophe" in widget.dialog_shown[1]


def test_success_passes_through():
    widget = FakeWidget()
    
    @safe_handler()
    def works(self):
        return "ok"
    
    assert works(widget) == "ok"
    assert widget.flashed is None
    assert widget.dialog_shown is None


def test_fallback_message_used():
    widget = FakeWidget()
    
    @safe_handler(severity="minor", fallback_message="Custom message")
    def boom(self):
        raise ValueError("internal")
    
    boom(widget)
    assert widget.flashed[0] == "Custom message"


def test_missing_helpers_does_not_crash():
    class BareWidget:
        pass
    
    @safe_handler(severity="severe")
    def boom(self):
        raise ValueError("oops")
    
    # Should not raise even though widget has no helpers
    result = boom(BareWidget())
    assert result is None