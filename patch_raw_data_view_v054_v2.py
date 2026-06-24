"""v0.5.4 Step 2 v2: swap QTableWidget for QTableView wired to RawDataTableModel.

Fixes the v1 patcher bug where QTableView import was inserted incorrectly
inside an existing multiline import block.
"""
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
print(f"[OK] Backed up {MW} -> {backup}")

# ------------------------------------------------------------
# Step 1: Add QTableView to existing PySide6.QtWidgets tuple.
# ------------------------------------------------------------
if "QTableView" not in src:
    # Your current import block contains:
    # QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QMenu, QHeaderView,
    # QLabel,
    #
    # Add QTableView safely inside that tuple.
    anchor = "QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QMenu, QHeaderView,"
    if anchor in src:
        src = src.replace(
            anchor,
            "QTableWidget, QTableWidgetItem, QTableView, QFileDialog, QMessageBox, QMenu, QHeaderView,",
            1,
        )
        print("[OK] Added QTableView to PySide6.QtWidgets import tuple")
    else:
        print("[ERROR] Could not find QtWidgets import anchor.")
        print("        Expected line containing:")
        print("        QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QMenu, QHeaderView,")
        sys.exit(1)
else:
    print("[OK] QTableView already imported")

# ------------------------------------------------------------
# Step 2: Add RawDataTableModel import outside Qt import block.
# ------------------------------------------------------------
if "from app.ui.raw_data_model import RawDataTableModel" not in src:
    # Put it after ModifiedDataTab import, which is a normal one-line import.
    anchor = "from app.ui.modified_data_tab import ModifiedDataTab"
    if anchor in src:
        src = src.replace(
            anchor,
            anchor + "\nfrom app.ui.raw_data_model import RawDataTableModel  # v0.5.4 model/view",
            1,
        )
        print("[OK] Added RawDataTableModel import")
    else:
        print("[ERROR] Could not find ModifiedDataTab import anchor.")
        sys.exit(1)
else:
    print("[OK] RawDataTableModel already imported")

# ------------------------------------------------------------
# Step 3: Replace old QTableWidget construction with QTableView.
# ------------------------------------------------------------
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
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)"""

if OLD_BLOCK in src:
    src = src.replace(OLD_BLOCK, NEW_BLOCK, 1)
    print("[OK] Replaced QTableWidget block with QTableView + model")
else:
    print("[ERROR] Could not find QTableWidget construction block.")
    print("        Your _build_raw_data_tab may already differ from expected.")
    print("        File NOT saved.")
    sys.exit(1)

# ------------------------------------------------------------
# Step 4: AST check before saving.
# ------------------------------------------------------------
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup at {backup}")
    sys.exit(1)

MW.write_text(src, encoding="utf-8")
print(f"[DONE] {MW} patched. Step 2 complete.")
print("")
print("IMPORTANT: Do not launch the app until Step 3 is applied.")
print("Step 2 only swaps the widget; Step 3 rewrites _populate_table and callers.")