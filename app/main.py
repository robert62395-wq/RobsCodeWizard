"""Application bootstrap."""
import os, sys
from app.services.logging_setup import setup_logging, install_excepthook


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
    logger.info("Starting Rob\'s Code Wizard (safe=%s)", flags["safe"])
    try:
        from PySide6.QtWidgets import QApplication
        from app.ui.splash import show_splash
        from app.ui.main_window import MainWindow
    except ImportError as exc:
        logger.error("Missing dependency: %s", exc)
        print(f"[Code Wizard] Missing dependency: {exc}")
        return 1
    try:
        app = QApplication(sys.argv)
        splash = show_splash()
        window = MainWindow(safe_mode=flags["safe"])
        window.show()
        splash.finish(window)
        return app.exec()
    except Exception as exc:
        logger.exception("Unhandled error in main loop: %s", exc)
        raise
