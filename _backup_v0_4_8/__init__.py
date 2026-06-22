"""Rob's Code Wizard package."""
from pathlib import Path

_VERSION_FILE = Path(__file__).parent.parent / "resources" / "version.txt"


def _load_version():
    try:
        raw = _VERSION_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "0.0.0"
    cleaned = raw.strip()
    # v0.4.8: defensive - strip literal escape sequences that may have been
    # accidentally embedded (e.g. literal "\n", "\r", "\r\n" text)
    for esc in ("\\r\\n", "\\n", "\\r"):
        cleaned = cleaned.replace(esc, "")
    return cleaned.strip()


__version__ = _load_version()
__all__ = ["__version__"]
