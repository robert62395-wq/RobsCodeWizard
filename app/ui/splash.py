"""Splash screen with animated GIF support (v0.3.9.5.1.2)."""
import sys
from pathlib import Path


def _resources_dir():
    """Locate resources/ for both dev and PyInstaller-frozen runs."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p = Path(meipass) / "resources"
        if p.exists():
            return p
    return Path(__file__).resolve().parents[2] / "resources"


def show_splash():
    """Show animated splash. Plays resources/splash.gif if present."""
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
            # Keep a reference so the movie isn't garbage-collected
            splash._movie = movie

            def _on_frame_changed(_):
                splash.setPixmap(movie.currentPixmap())

            movie.frameChanged.connect(_on_frame_changed)
            movie.start()
        except Exception:
            pass

    QApplication.processEvents()
    return splash

