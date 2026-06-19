"""Session recovery."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path


def get_recovery_path():
    return Path.home() / ".robs_code_wizard" / "recovery.json"


def save_session(rows, source_path=None, suggestions=None):
    p = get_recovery_path(); p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"saved_at": datetime.now().isoformat(timespec="seconds"),
               "source_path": str(source_path) if source_path else None,
               "rows": list(rows or []), "suggestions": list(suggestions or [])}
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_session():
    p = get_recovery_path()
    if not p.exists(): return None
    try: data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError): return None
    if not isinstance(data, dict): return None
    return data


def clear_session():
    p = get_recovery_path()
    try:
        if p.exists(): p.unlink()
    except OSError: pass


def has_session():
    return get_recovery_path().exists()
