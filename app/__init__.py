"""Rob's Code Wizard package."""
from pathlib import Path

_VERSION_FILE = Path(__file__).parent.parent / "resources" / "version.txt"
try:
    __version__ = _VERSION_FILE.read_text(encoding="utf-8").strip()
except FileNotFoundError:
    __version__ = "0.0.0"

__all__ = ["__version__"]
