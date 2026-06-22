import pytest
import app


def test_version_no_literal_backslash_n():
    # Must not contain literal "\\n" (backslash-n)
    assert "\\n" not in app.__version__
    assert "\\r" not in app.__version__


def test_version_no_real_whitespace():
    assert app.__version__ == app.__version__.strip()
    assert "\n" not in app.__version__
    assert "\r" not in app.__version__


def test_version_not_empty():
    assert app.__version__
