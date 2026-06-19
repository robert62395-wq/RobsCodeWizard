"""Splash screen."""
from pathlib import Path

def show_splash():
    from PySide6.QtWidgets import QSplashScreen
    from PySide6.QtGui import QPixmap
    res = Path(__file__).resolve().parents[2] / "resources" / "splash.gif"
    pixmap = QPixmap(str(res)) if res.exists() else QPixmap(400, 250)
    splash = QSplashScreen(pixmap)
    splash.showMessage("Loading Rob\'s Code Wizard v0.3.9.3...")
    splash.show()
    return splash
