"""Defensive event handler wrappers (v0.5.3 resilience).

Decorator for Qt slot/event handler methods that catches any exception,
logs it, and routes feedback based on severity:
  - "minor": flashes on status bar via parent._flash_status (if available)
  - "severe": shows QMessageBox.critical via parent._error_dialog (if available)
"""
from __future__ import annotations
import logging
from functools import wraps
from typing import Callable

log = logging.getLogger("robs_code_wizard")


def safe_handler(severity: str = "minor", fallback_message: str | None = None):
    """Decorator for QWidget event handler methods.
    
    Args:
        severity: "minor" (status bar flash) or "severe" (modal dialog).
        fallback_message: Override the default exception message.
    
    Usage:
        @safe_handler(severity="severe")
        def on_export_report(self):
            ...
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except Exception as exc:
                log.exception(
                    "safe_handler caught exception in %s: %s",
                    fn.__name__, exc,
                )
                msg = fallback_message or f"{fn.__name__}: {exc}"
                if severity == "severe" and hasattr(self, "_error_dialog"):
                    try:
                        self._error_dialog(
                            f"Operation failed: {fn.__name__}", exc
                        )
                    except Exception:
                        pass
                elif hasattr(self, "_flash_status"):
                    try:
                        self._flash_status(msg, msec=8000)
                    except Exception:
                        pass
                return None
        return wrapper
    return decorator