"""v0.5.5 banner readability fix (SAFE v2)

Fixes illegible "Under Construction" banner by applying style
AFTER widget creation instead of injecting into QLabel block.

This avoids syntax breakage from multiline strings.
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 banner style fix v2"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_banner_fix_v2.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created at {backup}")

lines = src.splitlines()

# ------------------------------------------------------------
# Step 1: Find where the banner is assigned (usually self.banner = QLabel)
# ------------------------------------------------------------
insert_index = None

for i, line in enumerate(lines):
    if "QLabel(" in line and "Under construction" in src:
        # Look forward for assignment line like self.banner =
        # Instead, we insert AFTER the next line that contains QLabel(...)
        insert_index = i + 2
        break

