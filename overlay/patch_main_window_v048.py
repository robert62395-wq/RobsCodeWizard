"""v0.4.8 Option A: bump About dialog logo size only."""
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")
if not MW.exists():
    print(f"[ERROR] {MW} not found.")
    sys.exit(1)

src = MW.read_text(encoding="utf-8")
SENTINEL = "v0.4.8 logo bump"
if SENTINEL in src:
    print(f"[OK] {MW} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_4_8") / MW.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[1/2] Backed up {MW}")

OLD = "pix = pix.scaledToHeight(140, Qt.SmoothTransformation)"
NEW = "pix = pix.scaledToHeight(220, Qt.SmoothTransformation)  # v0.4.8 logo bump"
if OLD not in src:
    print(f"[WARN] Logo height line not found - may already be changed.")
    sys.exit(0)
src = src.replace(OLD, NEW)
MW.write_text(src, encoding="utf-8")
print(f"[2/2] Bumped About logo 140 -> 220")
