"""
v0.5.5 Step 2:
Convert Translation tab from QTableWidget → QTableView.

SAFE:
- Only replaces table construction
- Does NOT touch logic yet
- AST validated
- Backup created
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 qtableview step2"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_qtableview.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created: {backup}")


# ------------------------------------------------------------
# 1. Add QTableView import
# ------------------------------------------------------------
if "QTableView" not in src:
    src = src.replace(
        "QTableWidget, QTableWidgetItem",
        "QTableWidget, QTableWidgetItem, QTableView"
    )
    print("[OK] Added QTableView import")


# ------------------------------------------------------------
# 2. Replace table creation block
# ------------------------------------------------------------
old_block = """self.table = QTableWidget(0, len(COLUMNS))"""

new_block = """# v0.5.5 QTableView upgrade (Step 2)
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
"""

if old_block not in src:
    print("[ERROR] Could not find QTableWidget creation block.")
    sys.exit(1)

src = src.replace(old_block, new_block)
print("[OK] Replaced QTableWidget with QTableView")


# ------------------------------------------------------------
# 3. Remove QTableWidget-specific calls (non-breaking)
# ------------------------------------------------------------
src = src.replace("self.table.setHorizontalHeaderLabels(COLUMNS)", "")
src = src.replace("self.table.setEditTriggers(QTableWidget.NoEditTriggers)", "")
src = src.replace("self.table.setSelectionBehavior(QTableWidget.SelectRows)", "")

print("[OK] Removed QTableWidget-only calls")


# ------------------------------------------------------------
# 4. Add sentinel
# ------------------------------------------------------------
src = "# v0.5.5 qtableview step2\n" + src


# ------------------------------------------------------------
# Validate syntax
# ------------------------------------------------------------
try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] Syntax issue:", e)
    print("File NOT saved.")
    sys.exit(1)

FILE.write_text(src, encoding="utf-8")

print("[DONE] Step 2 complete: Translation tab now uses QTableView.")
print("NOTE: Table will appear empty until Step 3 is applied.")
``