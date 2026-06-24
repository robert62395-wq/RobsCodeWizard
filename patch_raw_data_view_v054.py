"""v0.5.4 Step 2: swap QTableWidget for QTableView wired to RawDataTableModel."""
import ast
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")
if not MW.exists():
    print(f"[ERROR] {MW} not found.")
    sys.exit(1)

src = MW.read_text(encoding="utf-8")

SENTINEL = "v0.5.4 model/view"
if SENTINEL in src:
    print(f"[OK] {MW} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_4") / MW.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {MW}")

# Step 2a: Add imports for QTableView and RawDataTableModel.
# Anchor: the existing PySide6.QtWidgets import block.
# Strategy: insert after the existing QHeaderView line.
imports_to_add = [
    "from PySide6.QtWidgets import QTableView  # v0.5.4 model/view",
    "from app.ui.raw_data_model import RawDataTableModel  # v0.5.4 model/view",
]

# Locate a stable anchor — the existing QHeaderView import line.
import_anchor_candidates = [
    "QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QMenu, QHeaderView,",
    "from PySide6.QtWidgets import QHeaderView",
]
imports_added = False
for anchor in import_anchor_candidates:
    if anchor in src:
        replacement = anchor + "\n" + "\n".join(imports_to_add)
        src = src.replace(anchor, replacement, 1)
        imports_added = True
        print(f"[OK] Added v0.5.4 imports (anchor: {anchor[:50]}...)")
        break
if not imports_added:
    # Fallback: insert at the top of the imports section.
    src = src.replace(
        "from PySide6.QtCore import",
        "\n".join(imports_to_add) + "\nfrom PySide6.QtCore import",
        1
    )
    print("[OK] Added v0.5.4 imports via fallback anchor")

# Step 2b: Replace the QTableWidget creation block inside _build_raw_data_tab.
# The original looks like (collapsed onto multiple lines):
#
#     self.table = QTableWidget(0, len(COLUMNS))
#     self.table.setHorizontalHeaderLabels(COLUMNS)
#     self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
#     # v0.3.9.5.0.9: Raw Data is read-only - edits happen in the Modified Data tab
#     layout.addWidget(self.table)
#
# We replace it with a QTableView + model creation. The view's variable name
# stays as self.table so all downstream code (jump_to_row, context menu, etc.)
# can keep working with the new patcher in Step 3.

OLD_BLOCK = """        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)"""

NEW_BLOCK = """        # v0.5.4 model/view: QTableView + RawDataTableModel
        self.raw_data_model = RawDataTableModel(self)
        self.table = QTableView(page)
        self.table.setModel(self.raw_data_model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(False)
        # Context menu wiring is kept compatible with the old API.
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)"""

if OLD_BLOCK in src:
    src = src.replace(OLD_BLOCK, NEW_BLOCK, 1)
    print("[OK] Replaced QTableWidget block with QTableView + model")
else:
    print(f"[WARN] Could not find QTableWidget construction block.")
    print(f"        Inspect _build_raw_data_tab manually.")
    print(f"        Expected:")
    print(f"        {OLD_BLOCK}")
    sys.exit(1)

# Step 2c: Add a small import for Qt enum used by the context-menu policy
# if it isn't already imported.
if "from PySide6.QtCore import Qt" not in src and "QtCore import Qt" not in src:
    # Already there in most files but be defensive.
    print("[WARN] PySide6.QtCore.Qt does not appear to be imported. Add it manually.")

# Final AST check.
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup at {backup}")
    sys.exit(1)

MW.write_text(src, encoding="utf-8")
print(f"[DONE] {MW} patched. Step 2 complete.")
print("")
print("NEXT: run Step 3 patcher (rewrites _populate_table, _jump_to_row,")
print("      _on_context_menu, _apply_suggestion to use the model).")
print("")
print("WARNING: between Steps 2 and 3, the app will NOT populate the table")
print("         correctly because _populate_table still uses the old QTableWidget")
print("         API. Don't launch the app for testing until Step 3 is applied.")