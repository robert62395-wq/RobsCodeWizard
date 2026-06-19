"""Smoke test for BusyDialog."""
import pytest

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    pytest.skip("PySide6 not available", allow_module_level=True)

from app.ui.busy_dialog import BusyDialog, busy


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_busy_dialog_constructs(qapp):
    dlg = BusyDialog(text="Test")
    assert dlg.windowTitle() == "Please wait"
    assert dlg.isModal()


def test_busy_context_manager(qapp):
    with busy(text="Loading...") as dlg:
        assert isinstance(dlg, BusyDialog)
