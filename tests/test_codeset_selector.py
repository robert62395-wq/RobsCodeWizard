import os, sys
import pytest

qtwidgets = pytest.importorskip("PySide6.QtWidgets")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from app.ui.codeset_selector import CodeSetSelector

_app = qtwidgets.QApplication.instance() or qtwidgets.QApplication(sys.argv)


def test_has_two_items():
    s = CodeSetSelector()
    assert s.count() == 2
    assert s.itemData(0) == "vdt"
    assert s.itemData(1) == "odot"


def test_set_active_no_emit():
    s = CodeSetSelector()
    captured = []
    s.codesetChanged.connect(lambda n: captured.append(n))
    s.set_active("odot")
    assert s.current_codeset() == "odot"
    assert captured == []


def test_changing_index_emits():
    s = CodeSetSelector()
    s.set_active("vdt")
    captured = []
    s.codesetChanged.connect(lambda n: captured.append(n))
    s.setCurrentIndex(1)
    assert captured == ["odot"]
