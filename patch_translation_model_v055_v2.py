"""
v0.5.5 Step 3 v2:
Connect TranslationTableModel to translation_tab.py safely.

Fixes v1 issue:
- v1 globally replaced self.table.rowCount(), causing syntax errors.
- v2 replaces whole methods using AST line numbers instead.

This patch expects Step 2 already done:
- self.table = QTableView()
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation model step3 v2"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_model_step3_v2.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created: {backup}")

# Parse first to ensure starting file is valid.
try:
    tree = ast.parse(src)
except SyntaxError as e:
    print("[ERROR] translation_tab.py is already invalid before patch:")
    print(e)
    print("Restore from the Step 2 backup before continuing.")
    sys.exit(1)

# ------------------------------------------------------------
# 1. Add TranslationTableModel import
# ------------------------------------------------------------
if "from app.ui.translation_model import TranslationTableModel" not in src:
    src = src.replace(
        "from app.ui.help_icon import HelpIcon",
        "from app.ui.help_icon import HelpIcon\nfrom app.ui.translation_model import TranslationTableModel",
        1,
    )
    print("[OK] Added TranslationTableModel import")

# Reparse after import insert.
tree = ast.parse(src)


def replace_method(src_text, method_name, new_method):
    """Replace a class method by AST line numbers."""
    tree_local = ast.parse(src_text)
    target = None
    for node in ast.walk(tree_local):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            target = node
            break

    if target is None:
        print(f"[WARN] Method not found: {method_name}")
        return src_text, False

    lines = src_text.splitlines()
    start = target.lineno - 1
    end = target.end_lineno
    lines[start:end] = new_method.rstrip().splitlines()
    return "\n".join(lines) + "\n", True


# ------------------------------------------------------------
# 2. Replace _populate with model-based populate
# ------------------------------------------------------------
NEW_POPULATE = '''    def _populate(self):
        """v0.5.5 model-based populate for Translation tab."""
        entries = self._map_data.get("entries", [])

        # Keep same sort order as old table.
        sorted_entries = sorted(entries, key=lambda e: (
            (e.get("vdt") or {}).get("code", "") or (e.get("odot") or {}).get("code", "")
        ))

        self.translation_model = TranslationTableModel(sorted_entries, self._used_counts)
        self.table.setModel(self.translation_model)

        try:
            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)
        except Exception:
            pass

        self._apply_filter()
'''

src, ok = replace_method(src, "_populate", NEW_POPULATE)
if ok:
    print("[OK] Replaced _populate")


# ------------------------------------------------------------
# 3. Replace _apply_filter with model/view-safe version
# ------------------------------------------------------------
NEW_APPLY_FILTER = '''    def _apply_filter(self):
        """v0.5.5 model/view filter.

        This keeps filtering simple for now by hiding rows in the QTableView.
        A QSortFilterProxyModel can replace this later.
        """
        if not hasattr(self, "translation_model"):
            return

        search = self.search_box.text().strip().lower()
        model = self.translation_model

        for row in range(model.rowCount()):
            entry = model.entries[row]
            visible = True

            conf = entry.get("confidence", "unmatched")
            is_manual = entry.get("user_override", False)

            if is_manual and not self.show_manual.isChecked():
                visible = False
            elif not is_manual:
                if conf == "exact" and not self.show_exact.isChecked():
                    visible = False
                elif conf == "best-guess" and not self.show_bestguess.isChecked():
                    visible = False
                elif conf == "unmatched" and not self.show_unmatched.isChecked():
                    visible = False

            if visible and self.show_used_only.isChecked():
                v = (entry.get("vdt") or {}).get("code", "").upper()
                o = (entry.get("odot") or {}).get("code", "").upper()
                if v not in self._used_counts and o not in self._used_counts:
                    visible = False

            if visible and search:
                vc = (entry.get("vdt") or {}).get("code", "").lower()
                oc = (entry.get("odot") or {}).get("code", "").lower()
                vd = (entry.get("vdt") or {}).get("description", "").lower()
                od = (entry.get("odot") or {}).get("description", "").lower()
                if not any(search in x for x in (vc, oc, vd, od)):
                    visible = False

            self.table.setRowHidden(row, not visible)
'''

src, ok = replace_method(src, "_apply_filter", NEW_APPLY_FILTER)
if ok:
    print("[OK] Replaced _apply_filter")


# ------------------------------------------------------------
# 4. Replace _on_double_click to use model entries
# ------------------------------------------------------------
NEW_DOUBLE_CLICK = '''    def _on_double_click(self, row, col):
        """v0.5.5 model/view double-click edit."""
        if not hasattr(self, "translation_model"):
            return
        if row < 0 or row >= self.translation_model.rowCount():
            return

        entry = self.translation_model.entries[row]
        dlg = EntryEditDialog(entry, self._all_odot_codes(), self)
        if dlg.exec():
            dlg.apply_changes()
            self._dirty_ids.add(entry.get("id"))
            self._populate()
            self.map_modified.emit()
'''

src, ok = replace_method(src, "_on_double_click", NEW_DOUBLE_CLICK)
if ok:
    print("[OK] Replaced _on_double_click")


# ------------------------------------------------------------
# 5. Replace _on_bulk_accept to use model entries
# ------------------------------------------------------------
NEW_BULK_ACCEPT = '''    def _on_bulk_accept(self):
        """v0.5.5 model/view bulk accept."""
