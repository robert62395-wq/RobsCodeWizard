"""v0.5.5: Force Translation tab table to QTableView.

Fixes:
- Error: setModel(QAbstractItemModel *model) is a private method.
- Cause: self.table is still QTableWidget while _populate() now calls setModel().
- Solution: ensure table construction uses QTableView and remove QTableWidget-only calls.

Safe:
- Backs up translation_tab.py
- AST validates before saving
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] app/ui/translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 force translation qtableview"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_force_qtableview.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created: {backup}")


# ------------------------------------------------------------
# 1. Ensure QTableView is imported.
# ------------------------------------------------------------
if "QTableView" not in src:
    src = src.replace(
        "QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,",
        "QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QTableView,",
        1,
    )
    print("[OK] Added QTableView import")
else:
    print("[OK] QTableView already imported")


# ------------------------------------------------------------
# 2. Replace QTableWidget construction with QTableView construction.
# ------------------------------------------------------------
old_creation = "        self.table = QTableWidget(0, len(COLUMNS))"

new_creation = "\n".join([
    "        # v0.5.5 force translation qtableview",
    "        self.table = QTableView()",
    "        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)",
    "        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)",
])

if old_creation in src:
    src = src.replace(old_creation, new_creation, 1)
    print("[OK] Replaced QTableWidget creation with QTableView")
else:
    print("[WARN] Exact QTableWidget creation line not found.")
    print("       Checking for alternate table creation...")

    if "self.table = QTableWidget" in src:
        lines = src.splitlines()
        changed = False
        for i, line in enumerate(lines):
            if "self.table = QTableWidget" in line:
                indent = line[:len(line) - len(line.lstrip())]
                lines[i:i + 1] = [
                    f"{indent}# v0.5.5 force translation qtableview",
                    f"{indent}self.table = QTableView()",
                    f"{indent}self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)",
                    f"{indent}self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)",
                ]
                changed = True
                break
        src = "\n".join(lines) + "\n"
        if changed:
            print("[OK] Replaced alternate QTableWidget creation with QTableView")
    elif "self.table = QTableView" in src:
        print("[OK] Table already appears to be QTableView")
    else:
        print("[ERROR] Could not find self.table creation.")
        print("        File NOT saved.")
        sys.exit(1)


# ------------------------------------------------------------
# 3. Remove QTableWidget-only calls.
# ------------------------------------------------------------
remove_lines = [
    "        self.table.setHorizontalHeaderLabels(COLUMNS)",
    "        self.table.setEditTriggers(QTableWidget.NoEditTriggers)",
    "        self.table.setSelectionBehavior(QTableWidget.SelectRows)",
    "        self.table.cellDoubleClicked.connect(self._on_double_click)",
]

for line in remove_lines:
    if line in src:
        src = src.replace(line + "\n", "")
        print(f"[OK] Removed QTableWidget-only line: {line.strip()}")


# ------------------------------------------------------------
# 4. Add QTableView-compatible double-click hookup if missing.
# ------------------------------------------------------------
if "self.table.doubleClicked.connect(self._on_double_click)" not in src:
    anchor = "        root.addWidget(self.table)"
    hook = "        self.table.doubleClicked.connect(self._on_double_click)\n"
    if anchor in src:
        src = src.replace(anchor, hook + anchor, 1)
        print("[OK] Added QTableView doubleClicked hookup")
    else:
        print("[WARN] Could not find root.addWidget(self.table) anchor for double-click hookup")


# ------------------------------------------------------------
# 5. Ensure header behavior remains.
# ------------------------------------------------------------
if "self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)" not in src:
    anchor = "        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)"
    insert = (
        "        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)\n"
        "        self.table.horizontalHeader().setStretchLastSection(True)"
    )
    if anchor in src:
        src = src.replace(anchor, anchor + "\n" + insert, 1)
        print("[OK] Added header resize behavior")


# ------------------------------------------------------------
# 6. Add sentinel and validate.
# ------------------------------------------------------------
src = "# v0.5.5 force translation qtableview\n" + src

try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:")
    print(e)
    print("File NOT saved.")
    print(f"Backup remains at: {backup}")
    sys.exit(1)

FILE.write_text(src, encoding="utf-8")
print("[DONE] Translation tab now uses QTableView correctly.")
print("       setModel() should no longer throw the private method error.")