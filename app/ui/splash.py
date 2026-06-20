"""Splash screen with animated GIF support (v0.3.9.5.1.2.1)."""
import sys
import time
from pathlib import Path

# v0.3.9.5.1.2.1: keep splash visible long enough for the loading bar
# in splash.gif (32 frames * 100ms = 3.2s) to visibly fill.
SPLASH_MIN_DURATION_SEC = 3.2


def _resources_dir():
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p = Path(meipass) / "resources"
        if p.exists():
            return p
    return Path(__file__).resolve().parents[2] / "resources"


def show_splash():
    """Show animated splash; returns splash with ._min_until timestamp."""
    from PySide6.QtWidgets import QSplashScreen, QApplication
    from PySide6.QtGui import QPixmap, QMovie
    from PySide6.QtCore import Qt

    res = _resources_dir() / "splash.gif"
    movie = None
    if res.exists():
        movie = QMovie(str(res))
        movie.jumpToFrame(0)
        pixmap = movie.currentPixmap()
        if pixmap.isNull():
            pixmap = QPixmap(str(res))
            movie = None
    else:
        pixmap = QPixmap(480, 320)
        pixmap.fill(Qt.black)

    splash = QSplashScreen(pixmap)
    splash.setAttribute(Qt.WA_DeleteOnClose, False)
    splash.show()

    if movie is not None:
        try:
            splash._movie = movie  # keep ref so movie isn't GC'd

            def _on_frame_changed(_):
                splash.setPixmap(movie.currentPixmap())

            movie.frameChanged.connect(_on_frame_changed)
            movie.start()
        except Exception:
            pass

    splash._min_until = time.monotonic() + SPLASH_MIN_DURATION_SEC
    QApplication.processEvents()
    return splash


def wait_for_splash(splash):
    """Block (with processEvents) until splash._min_until is reached.

    Lets MainWindow finish building during the wait if it hasn't already.
    If MainWindow took LONGER than SPLASH_MIN_DURATION_SEC, this returns
    immediately.
    """
    from PySide6.QtWidgets import QApplication
    if not hasattr(splash, "_min_until"):
        return
    end_at = splash._min_until
    while time.monotonic() < end_at:
        QApplication.processEvents()
        time.sleep(0.02)

