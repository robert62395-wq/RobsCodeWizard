"""v0.5.4 repair: replace broken _build_raw_data_tab with clean model/view version.

Use this after a manual edit leaves main_window.py with syntax like:
    = QPushButton("Open CSV/TXT...")
"""
import ast
import re
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")
if not MW.exists():
    print(f"[ERROR] {MW} not found.")
    sys.exit(1)

src = MW.read_text(encoding="utf-8")

backup = Path("_backup_v0_5_4") / "main_window_before_raw_tab_repair.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up current file -> {backup}")

# Ensure QTableView is in the PySide6.QtWidgets import tuple.
if "QTableView" not in src:
    anchor = "QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QMenu, QHeaderView,"
    if anchor in src:
        src = src.replace(
            anchor,
            "QTableWidget, QTableWidgetItem, QTableView, QFileDialog, QMessageBox, QMenu, QHeaderView,",
            1,
        )
        print("[OK] Added QTableView import")
    else:
        print("[WARN] Could not automatically add QTableView import")

# Ensure RawDataTableModel import exists.
if "from app.ui.raw_data_model import RawDataTableModel" not in src:
    anchor = "from app.ui.modified_data_tab import ModifiedDataTab"
    if anchor in src:
        src = src.replace(
            anchor,
            anchor + "\nfrom app.ui.raw_data_model import RawDataTableModel  # v0.5.4 model/view",
            1,
        )
        print("[OK] Added RawDataTableModel import")
    else:
        print("[WARN] Could not automatically add RawDataTableModel import")

NEW_METHOD = '''    def _build_raw_data_tab(self):
        """Build the Raw Data tab.

        v0.5.4 model/view rewrite:
        QTableWidget is replaced by QTableView + RawDataTableModel.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Code Set:"))

        self.codeset_selector = CodeSetSelector()
        self.codeset_selector.set_active(self.codeset.name)
        self.codeset_selector.codesetChanged.connect(self._on_codeset_changed)

        bar.addWidget(self.codeset_selector)
        bar.addWidget(HelpIcon("code_set"))

        bar.addSpacing(20)

        open_btn = QPushButton("Open CSV/TXT...")
        open_btn.setToolTip("Load a PNEZD CSV or TXT point file for analysis.")
        open_btn.clicked.connect(self.on_open_file)

        linework_btn = QPushButton("Linework Fix")
        linework_btn.setToolTip("Open the Linework Fix overlay to find and repair linework grammar problems.")
        linework_btn.clicked.connect(self.on_linework_fix)

        self.export_btn = QPushButton("Export Validation Report...")
        self.export_btn.setToolTip("Export validation results, issues, notes, and suggestions to a report.")
        self.export_btn.clicked.connect(self.on_export_report)
        self.export_btn.setEnabled(False)

        bar.addWidget(open_btn)
        bar.addWidget(linework_btn)
        bar.addWidget(HelpIcon("linework_fix"))
        bar.addWidget(self.export_btn)
        bar.addStretch(1)

        layout.addLayout(bar)

        # v0.5.4 model/view: QTableView + RawDataTableModel
        self.raw_data_model = RawDataTableModel(self)
        self.table = QTableView(page)
        self.table.setModel(self.raw_data_model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)

        # v0.3.9.5.0.9: Raw Data is read-only - edits happen in the Modified Data tab
        layout.addWidget(self.table)
        return page
'''

pattern = re.compile(
    r"^    def _build_raw_data_tab\(self\):\n.*?(?=^    def |^class |\Z)",
    re.MULTILINE | re.DOTALL,
)

match = pattern.search(src)
if not match:
    print("[ERROR] Could not find _build_raw_data_tab method.")
    print("        Restore from _backup_v0_5_4\\main_window.py if needed.")
    sys.exit(1)

src = src[:match.start()] + NEW_METHOD.rstrip() + "\n\n" + src[match.end():]

try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] File would still be invalid after repair: {e}")
    print("        File NOT saved.")
    print(f"        Backup is at {backup}")
    sys.exit(1)

MW.write_text(src, encoding="utf-8")
print("[DONE] _build_raw_data_tab repaired and syntax-checked.")