"""v0.5.3.1 patcher: add modified_at + atomic-write to recovery.py."""
import ast
import sys
from pathlib import Path

R = Path("app/services/recovery.py")
if not R.exists():
    print(f"[ERROR] {R} not found.")
    sys.exit(1)

src = R.read_text(encoding="utf-8")
SENTINEL = "v0.5.3.1 atomic recovery write"
if SENTINEL in src:
    print(f"[OK] {R} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_3_1") / R.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {R}")

NEW_SRC = '''"""Session recovery (v0.5.3.1 with atomic write + last-modified)."""
# v0.5.3.1 atomic recovery write
from __future__ import annotations
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path


def get_recovery_path():
    return Path.home() / ".robs_code_wizard" / "recovery.json"


def save_session(rows, source_path=None, suggestions=None):
    """Atomic write so a crash mid-save leaves the previous recovery intact."""
    p = get_recovery_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "source_path": str(source_path) if source_path else None,
        "rows": list(rows or []),
        "suggestions": list(suggestions or []),
    }
    # Write to a temp file in the same directory, then rename atomically.
    tmp_fd, tmp_name = tempfile.mkstemp(
        prefix="recovery_", suffix=".json.tmp", dir=str(p.parent)
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp_name, p)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def load_session():
    p = get_recovery_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def clear_session():
    p = get_recovery_path()
    try:
        if p.exists():
            p.unlink()
    except OSError:
        pass


def has_session():
    return get_recovery_path().exists()
'''

try:
    ast.parse(NEW_SRC)
except SyntaxError as e:
    print(f"[ERROR] Patched file has syntax error: {e}")
    sys.exit(1)

R.write_text(NEW_SRC, encoding="utf-8")
print(f"[DONE] {R} patched (atomic write via temp file + os.replace).")