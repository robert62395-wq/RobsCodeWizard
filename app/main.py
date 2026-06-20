"""Application bootstrap."""
import os, sys
from pathlib import Path
from app.services.logging_setup import setup_logging, install_excepthook


def _icon_path():
    """v0.3.9.5.1.1: locate resources/icon.ico for both dev and PyInstaller-frozen runs."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p = Path(meipass) / "resources" / "icon.ico"
        if p.exists():
            return p
    p = Path(__file__).resolve().parents[1] / "resources" / "icon.ico"
    if p.exists():
        return p
    return None


def _parse_args(argv):
    return {"safe": "--safe" in argv}


def run_app(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    flags = _parse_args(argv)
    if flags["safe"]:
        os.environ["ROBS_CODE_WIZARD_SAFE"] = "1"
    logger = setup_logging()
    install_excepthook(logger)
    logger.info("Starting Rob's Code Wizard (safe=%s)", flags["safe"])
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        from app.ui.splash import show_splash
        from app.ui.main_window import MainWindow
    except ImportError as exc:
        logger.error("Missing dependency: %s", exc)
        print(f"[Code Wizard] Missing dependency: {exc}")
        return 1
    try:
        app = QApplication(sys.argv)
        # v0.3.9.5.1.1: set app-wide window icon from resources/icon.ico
        icon = _icon_path()
        if icon:
            app.setWindowIcon(QIcon(str(icon)))
        splash = show_splash()
        window = MainWindow(safe_mode=flags["safe"])
        window.show()
        splash.finish(window)
        return app.exec()
    except Exception as exc:
        logger.exception("Unhandled error in main loop: %s", exc)
        raise


if __name__ == "__main__":
    sys.exit(run_app())

