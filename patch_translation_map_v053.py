"""v0.5.3 patcher: add backup + safe_load to translation_map.py."""
import ast
import sys
from pathlib import Path

TM = Path("app/services/translation_map.py")
if not TM.exists():
    print(f"[ERROR] {TM} not found.")
    sys.exit(1)

src = TM.read_text(encoding="utf-8")
SENTINEL = "v0.5.3 safe_load"
if SENTINEL in src:
    print(f"[OK] {TM} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_3") / TM.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {TM}")

# Add: import for shutil/datetime + BACKUP_PATH constant
if "import shutil" not in src:
    src = src.replace(
        "import json\nfrom pathlib import Path",
        "import json\nimport shutil\nfrom datetime import datetime\nfrom pathlib import Path"
    )

# Add BACKUP_PATH constant after MAP_PATH
if "BACKUP_PATH" not in src:
    src = src.replace(
        'MAP_PATH = Path(__file__).parent.parent / "data" / "translation_map.json"',
        'MAP_PATH = Path(__file__).parent.parent / "data" / "translation_map.json"\n'
        'BACKUP_PATH = Path(__file__).parent.parent / "data" / "translation_map.backup.json"\n'
        'BACKUP_TIMESTAMPED_DIR = Path(__file__).parent.parent / "data" / "translation_map_backups"'
    )

# Modify save() to create backup before writing
old_save = '''def save(data: dict, path: Path = MAP_PATH) -> None:
    validate(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)'''

new_save = '''def save(data: dict, path: Path = MAP_PATH) -> None:
    validate(data)
    # v0.5.3: auto-backup before overwriting
    if path.exists():
        try:
            shutil.copy2(path, BACKUP_PATH)
            # Also keep a timestamped backup
            BACKUP_TIMESTAMPED_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(path, BACKUP_TIMESTAMPED_DIR / f"translation_map_{ts}.json")
            # Prune old timestamped backups - keep most recent 10
            backups = sorted(BACKUP_TIMESTAMPED_DIR.glob("translation_map_*.json"))
            for old in backups[:-10]:
                try:
                    old.unlink()
                except Exception:
                    pass
        except Exception:
            pass  # never block save on backup failure
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)'''

if old_save in src:
    src = src.replace(old_save, new_save)
    print("[OK] save() now creates backups")
else:
    print("[WARN] Could not patch save() - anchor not found")

# Add safe_load() at the end of the file (returns (data, error_msg))
# v0.5.3 safe_load
if "def safe_load(" not in src:
    safe_load_code = '''

# v0.5.3 safe_load: corruption-aware loader.
def safe_load(path: Path = MAP_PATH):
    """Load the map and return (data, error_msg).

    On success: returns (data_dict, None).
    On failure: returns (None, error_message_string).
    Caller is expected to present a recovery dialog if error_msg is not None.
    """
    if not path.exists():
        return None, f"Translation map not found at {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return None, f"JSON parse error at line {e.lineno}, col {e.colno}: {e.msg}"
    except OSError as e:
        return None, f"Could not read file: {e}"
    try:
        validate(data)
    except ValueError as e:
        return None, f"Schema validation failed: {e}"
    except Exception as e:
        return None, f"Unexpected error during validation: {e}"
    return data, None


def restore_from_backup(path: Path = MAP_PATH, backup: Path = BACKUP_PATH) -> bool:
    """v0.5.3: restore the latest backup over the corrupted map.

    Returns True if a backup was found and restored, False otherwise.
    """
    if not backup.exists():
        return False
    try:
        shutil.copy2(backup, path)
        return True
    except Exception:
        return False


def has_backup(backup: Path = BACKUP_PATH) -> bool:
    """v0.5.3: return True if a backup file exists and is readable."""
    return backup.exists() and backup.is_file()
'''
    src = src.rstrip() + "\n" + safe_load_code
    print("[OK] Added safe_load, restore_from_backup, has_backup")

# Verify and save
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup is at _backup_v0_5_3\\{TM.name}")
    sys.exit(1)

TM.write_text(src, encoding="utf-8")
print(f"[DONE] {TM} patched.")