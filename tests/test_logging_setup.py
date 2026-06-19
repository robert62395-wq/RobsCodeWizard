import logging, sys
from pathlib import Path
from app.services import logging_setup


def test_get_log_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert logging_setup.get_log_dir() == tmp_path / ".robs_code_wizard" / "logs"


def test_setup_writes_file(monkeypatch, tmp_path):
    log_dir = tmp_path / "logs"
    monkeypatch.setattr(logging_setup, "get_log_dir", lambda: log_dir)
    monkeypatch.setattr(logging_setup, "get_log_path", lambda: log_dir / "code_wizard.log")
    logger = logging_setup.setup_logging(level=logging.INFO)
    logger.error("hello")
    for h in logger.handlers: h.flush()
    assert "hello" in (log_dir / "code_wizard.log").read_text(encoding="utf-8")


def test_excepthook(monkeypatch, tmp_path):
    log_dir = tmp_path / "logs"
    monkeypatch.setattr(logging_setup, "get_log_dir", lambda: log_dir)
    monkeypatch.setattr(logging_setup, "get_log_path", lambda: log_dir / "code_wizard.log")
    logger = logging_setup.setup_logging(level=logging.INFO)
    logging_setup.install_excepthook(logger)
    try: raise RuntimeError("boom")
    except RuntimeError: sys.excepthook(*sys.exc_info())
    for h in logger.handlers: h.flush()
    text = (log_dir / "code_wizard.log").read_text(encoding="utf-8")
    assert "Uncaught exception" in text and "boom" in text


def test_read_tail(monkeypatch, tmp_path):
    log_dir = tmp_path / "logs"; log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "code_wizard.log"
    log_file.write_text("x" * 30000, encoding="utf-8")
    monkeypatch.setattr(logging_setup, "get_log_dir", lambda: log_dir)
    monkeypatch.setattr(logging_setup, "get_log_path", lambda: log_file)
    tail = logging_setup.read_recent_log(max_bytes=5000)
    assert len(tail) <= 5000
