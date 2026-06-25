"""
v0.5.5 Step 4:
Enable sorting on Translation QTableView

Safe:
- Only modifies table setup
- No logic changes
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 sorting enabled"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_sorting.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print("[OK] Backup created")

# ------------------------------------------------------------
# Find table setup and add sorting
# ------------------------------------------------------------
anchor = "self.table.setModel("

if anchor not in src:
    print("[ERROR] Could not find table.setModel() anchor")
    sys.exit(1)

insert_block = """
        # v0.5.5 sorting enabled
        try:
            self.table.setSortingEnabled(True)
        except Exception:
            pass
"""

src = src.replace(anchor, insert_block + "        " + anchor, 1)

# ------------------------------------------------------------
# Finalize
# ------------------------------------------------------------
src = "# v0.5.5 sorting enabled\n" + src

try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] Syntax issue:", e)
    print("File NOT saved.")
    sys.exit(1)

FILE.write_text(src, encoding="utf-8")

print("[DONE] Sorting enabled on Translation table")
``