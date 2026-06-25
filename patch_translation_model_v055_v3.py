"""
v0.5.5 Step 3 v3:
Connect TranslationTableModel to translation_tab.py safely.

Fixes prior patch issue:
- No triple-quoted replacement strings.
- Replaces methods using AST line numbers.
- Updates QTableView double-click signal usage.
- Does not globally replace rowCount() or other table APIs.

Expected precondition:
- Step 2 already converted self.table to QTableView.
- app/ui/translation_model.py already exists.
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation model step3 v3"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_model_step3_v3.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created: {backup}")

try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] translation_tab.py is already invalid before patch:")
    print(e)
    print("Restore from your latest backup before continuing.")
    sys.exit(1)


def method_text(lines):
    return "\n".join(lines) + "\n"


def replace_method(src_text, method_name, new_lines):
    tree = ast.parse(src_text)
    target = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            target = node
            break

    if target is None:
        print(f"[WARN] Method not found: {method_name}")
        return src_text, False

    lines = src_text.splitlines()
    start = target.lineno - 1
    end = target.end_lineno
    lines[start:end] = new_lines
    print(f"[OK] Replaced {method_name}")
    return "\n".join(lines) + "\n", True


# ------------------------------------------------------------
# 1. Add model import
# ------------------------------------------------------------
if "from app.ui.translation_model import TranslationTableModel" not in src:
    anchor = "from app.ui.help_icon import HelpIcon"
    if anchor in src:
        src = src.replace(
            anchor,
            anchor + "\nfrom app.ui.translation_model import TranslationTableModel",
            1,
        )
        print("[OK] Added TranslationTableModel import")
    else:
        print("[ERROR] Could not find HelpIcon import anchor.")
        sys.exit(1)


# ------------------------------------------------------------
# 2. Fix QTableView double-click signal if Step 2 left old signal
# ------------------------------------------------------------
src = src.replace(
    "self.table.cellDoubleClicked.connect(self._on_double_click)",
    "self.table.doubleClicked.connect(self._on_double_click)",
)

# Some Step 2 patch versions used QTableView.SelectRows, which can be invalid.
src = src.replace(
    "self.table.setSelectionBehavior(QTableView.SelectRows)",
    "self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)",
)


# ------------------------------------------------------------
# 3. Replace _populate
# ------------------------------------------------------------
NEW_POPULATE = [
    "    def _populate(self):",
    "        \"\"\"v0.5.5 model-based populate for Translation tab.\"\"\"",
    "        entries = self._map_data.get(\"entries\", [])",
    "",
    "        sorted_entries = sorted(entries, key=lambda e: (",
    "            (e.get(\"vdt\") or {}).get(\"code\", \"\") or (e.get(\"odot\") or {}).get(\"code\", \"\")",
    "        ))",
    "",
    "        self.translation_model = TranslationTableModel(sorted_entries, self._used_counts)",
    "        self.table.setModel(self.translation_model)",
    "",
    "        try:",
    "            self.table.resizeColumnsToContents()",
    "            self.table.horizontalHeader().setStretchLastSection(True)",
    "        except Exception:",
    "            pass",
    "",
    "        self._apply_filter()",
]
src, _ = replace_method(src, "_populate", NEW_POPULATE)


# ------------------------------------------------------------
# 4. Replace _apply_filter
# ------------------------------------------------------------
NEW_APPLY_FILTER = [
    "    def _apply_filter(self):",
    "        \"\"\"v0.5.5 model/view filter.",
    "",
    "        Filtering is implemented by hiding rows in QTableView for now.",
    "        A QSortFilterProxyModel can replace this later.",
    "        \"\"\"",
    "        if not hasattr(self, \"translation_model\"):",
    "            return",
    "",
    "        from PySide6.QtCore import QModelIndex",
    "",
    "        search = self.search_box.text().strip().lower()",
    "        model = self.translation_model",
    "",
    "        for row in range(model.rowCount()):",
    "            entry = model.entries[row]",
    "            visible = True",
    "",
    "            conf = entry.get(\"confidence\", \"unmatched\")",
    "            is_manual = entry.get(\"user_override\", False)",
    "",
    "            if is_manual and not self.show_manual.isChecked():",
    "                visible = False",
    "            elif not is_manual:",
    "                if conf == \"exact\" and not self.show_exact.isChecked():",
    "                    visible = False",
    "                elif conf == \"best-guess\" and not self.show_bestguess.isChecked():",
    "                    visible = False",
    "                elif conf == \"unmatched\" and not self.show_unmatched.isChecked():",
    "                    visible = False",
    "",
    "            if visible and self.show_used_only.isChecked():",
    "                v = (entry.get(\"vdt\") or {}).get(\"code\", \"\").upper()",
    "                o = (entry.get(\"odot\") or {}).get(\"code\", \"\").upper()",
    "                if v not in self._used_counts and o not in self._used_counts:",
    "                    visible = False",
    "",
    "            if visible and search:",
    "                vc = (entry.get(\"vdt\") or {}).get(\"code\", \"\").lower()",
    "                oc = (entry.get(\"odot\") or {}).get(\"code\", \"\").lower()",
    "                vd = (entry.get(\"vdt\") or {}).get(\"description\", \"\").lower()",
    "                od = (entry.get(\"odot\") or {}).get(\"description\", \"\").lower()",
    "                if not any(search in x for x in (vc, oc, vd, od)):",
    "                    visible = False",
    "",
    "            try:",
    "                self.table.setRowHidden(row, QModelIndex(), not visible)",
    "            except TypeError:",
    "                # Fallback for widgets exposing the 2-arg form.",
    "                self.table.setRowHidden(row, not visible)",
]
src, _ = replace_method(src, "_apply_filter", NEW_APPLY_FILTER)


# ------------------------------------------------------------
# 5. Replace _on_double_click
# ------------------------------------------------------------
NEW_DOUBLE_CLICK = [
    "    def _on_double_click(self, index):",
    "        \"\"\"v0.5.5 model/view double-click edit.\"\"\"",
    "        if not hasattr(self, \"translation_model\"):",
    "            return",
    "        if not index.isValid():",
    "            return",
    "",
    "        row = index.row()",
    "        if row < 0 or row >= self.translation_model.rowCount():",
    "            return",
    "",
    "        entry = self.translation_model.entries[row]",
    "        dlg = EntryEditDialog(entry, self._all_odot_codes(), self)",
    "        if dlg.exec():",
    "            dlg.apply_changes()",
    "            self._dirty_ids.add(entry.get(\"id\"))",
    "            self._populate()",
    "            self.map_modified.emit()",
]
src, _ = replace_method(src, "_on_double_click", NEW_DOUBLE_CLICK)


# ------------------------------------------------------------
# 6. Replace _on_bulk_accept
# ------------------------------------------------------------
NEW_BULK_ACCEPT = [
    "    def _on_bulk_accept(self):",
    "        \"\"\"v0.5.5 model/view bulk accept.\"\"\"",
    "        if not hasattr(self, \"translation_model\"):",
    "            return",
    "",
    "        targets = []",
    "        for row, entry in enumerate(self.translation_model.entries):",
    "            try:",
    "                hidden = self.table.isRowHidden(row)",
    "            except Exception:",
    "                hidden = False",
    "            if hidden:",
    "                continue",
    "            if entry and entry.get(\"confidence\") == \"best-guess\" and not entry.get(\"user_override\"):",
    "                targets.append(entry)",
    "",
    "        if not targets:",
    "            QMessageBox.information(self, \"Nothing to Accept\", \"No best-guess entries visible.\")",
    "            return",
    "",
    "        resp = QMessageBox.question(",
    "            self,",
    "            \"Accept All\",",
    "            f\"Mark all {len(targets)} visible best-guess entries as manual overrides?\",",
    "            QMessageBox.Yes | QMessageBox.No,",
    "            QMessageBox.No,",
    "        )",
    "        if resp != QMessageBox.Yes:",
    "            return",
    "",
    "        for entry in targets:",
    "            entry[\"user_override\"] = True",
    "            entry[\"confidence\"] = \"manual\"",
    "            self._dirty_ids.add(entry.get(\"id\"))",
    "",
    "        self._populate()",
    "        self.map_modified.emit()",
]
src, _ = replace_method(src, "_on_bulk_accept", NEW_BULK_ACCEPT)


# ------------------------------------------------------------
# 7. Replace _on_export
# ------------------------------------------------------------
NEW_EXPORT = [
    "    def _on_export(self):",
    "        \"\"\"v0.5.5 model/view export visible rows.\"\"\"",
    "        path, _ = QFileDialog.getSaveFileName(",
    "            self,",
    "            \"Export CSV\",",
    "            \"translation_review.csv\",",
    "            \"CSV (*.csv)\",",
    "        )",
    "        if not path:",
    "            return",
    "",
    "        if not hasattr(self, \"translation_model\"):",
    "            QMessageBox.information(self, \"Export\", \"No translation rows to export.\")",
    "            return",
    "",
    "        with open(path, \"w\", encoding=\"utf-8\", newline=\"\") as f:",
    "            w = csv.writer(f)",
    "            w.writerow(COLUMNS)",
    "",
    "            for row, entry in enumerate(self.translation_model.entries):",
    "                try:",
    "                    hidden = self.table.isRowHidden(row)",
    "                except Exception:",
    "                    hidden = False",
    "                if hidden:",
    "                    continue",
    "",
    "                vdt = entry.get(\"vdt\") or {}",
    "                odot = entry.get(\"odot\") or {}",
    "                v_code = vdt.get(\"code\", \"\")",
    "                o_code = odot.get(\"code\", \"\")",
    "                count = max(",
    "                    self._used_counts.get(v_code.upper(), 0),",
    "                    self._used_counts.get(o_code.upper(), 0),",
    "                )",
    "",
    "                w.writerow([",
    "                    v_code,",
    "                    vdt.get(\"description\", \"\"),",
    "                    o_code,",
    "                    odot.get(\"description\", \"\"),",
    "                    short_label(entry),",
    "                    str(count) if count else \"\",",
    "                    entry.get(\"notes\", \"\"),",
    "                ])",
    "",
    "        QMessageBox.information(self, \"Exported\", f\"Wrote {path}\")",
]
src, _ = replace_method(src, "_on_export", NEW_EXPORT)


# ------------------------------------------------------------
# 8. Replace _append_row with no-op
# ------------------------------------------------------------
NEW_APPEND_ROW = [
    "    def _append_row(self, entry):",
    "        \"\"\"Deprecated in v0.5.5 model/view rewrite.",
    "",
    "        Kept for compatibility; _populate now uses TranslationTableModel.",
    "        \"\"\"",
    "        return",
]
src, _ = replace_method(src, "_append_row", NEW_APPEND_ROW)


# ------------------------------------------------------------
# 9. Validate and save
# ------------------------------------------------------------
src = "# v0.5.5 translation model step3 v3\n" + src

try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:")
    print(e)
    print("File NOT saved.")
    print(f"Backup remains at: {backup}")
    sys.exit(1)

FILE.write_text(src, encoding="utf-8")
print("[DONE] Translation model/view Step 3 v3 applied successfully.")