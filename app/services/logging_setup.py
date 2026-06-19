"""Logging setup."""
from __future__ import annotations
import logging, sys, traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGER_NAME = "robs_code_wizard"
_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def get_log_dir():
    return Path.home() / ".robs_code_wizard" / "logs"


def get_log_path():
    return get_log_dir() / "code_wizard.log"


def setup_logging(level=logging.INFO):
    logger = logging.getLogger(_LOGGER_NAME); logger.setLevel(level)
    for h in list(logger.handlers): logger.removeHandler(h)
    log_dir = get_log_dir(); log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(_FORMAT)
    fh = RotatingFileHandler(get_log_path(), maxBytes=512_000, backupCount=3, encoding="utf-8")
    fh.setLevel(level); fh.setFormatter(formatter); logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stderr); sh.setLevel(level); sh.setFormatter(formatter); logger.addHandler(sh)
    logger.propagate = False
    return logger


def install_excepthook(logger):
    def _hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb); return
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.error("Uncaught exception:\n%s", tb_str)
    sys.excepthook = _hook


def read_recent_log(max_bytes=20_000):
    p = get_log_path()
    if not p.exists(): return ""
    try:
        size = p.stat().st_size
        with p.open("rb") as fh:
            if size > max_bytes: fh.seek(size - max_bytes)
            data = fh.read()
        return data.decode("utf-8", errors="replace")
    except OSError as exc:
        return f"(could not read log: {exc})"
