"""v0.5.4 Step 3: rewrite Raw Data table call sites for QTableView + RawDataTableModel.

Replaces:
- _populate_table
- _apply_row_color
- _jump_to_row
- _apply_suggestion
- _on_context_menu

The old QTableWidget API created thousands of QTableWidgetItems and applied
background brushes cell-by-cell. The new model/view approach pushes data into
RawDataTableModel once and lets Qt request visible cells on demand.
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

SENTINEL = "v0.5.4 raw data caller rewrite"
if SENTINEL in src:
    print(f"[OK] {MW} already has v0.5.4 caller rewrite.")
    sys.exit(0)

backup = Path("_backup_v0_5_4") / MW.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {MW} -> {backup}")


def replace_method(src_text: str, method_name: str, new_method: str):
    """Replace a top-level MainWindow method by name.

    Looks for an indented class method:
        "    def method_name(...):"
    and replaces until the next:
        "\\n    def "
    """
    pattern = re.compile(
        rf"^    def {re.escape(method_name)}\\(.*?\\):\\n"
        rf".*?"
        rf"(?=^    def |^class |\\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(src_text)
    if not match:
        print(f"[WARN] Method not found: {method_name}")
        return src_text, False
    return src_text[:match.start()] + new_method.rstrip() + "\n\n" + src_text[match.end():], True


NEW_POPULATE_TABLE = '''    def _populate_table(self):
        """v0.5.4 raw data caller rewrite: fast model/view populate.

        Old behavior:
            Create QTableWidgetItem for every cell, set text, set color, resize.

        New behavior:
            Push rows/results/suggestions into RawDataTableModel in one reset.
            Qt asks for only visible cells on demand.
        """
        import time
        t0 = time.perf_counter()

        if not hasattr(self, "raw_data_model"):
            # Defensive fallback if _build_raw_data_tab did not complete.
            log.warning("populate skipped: raw_data_model is missing")
            return

        self.raw_data_model.set_data(
            getattr(self, "rows", []),
            getattr(self, "results", []),
            getattr(self, "suggestions", []),
        )

        # Keep row selection sane after reset.
        try:
            if self.raw_data_model.rowCount() > 0:
                self.table.selectRow(0)
        except Exception:
            pass

        elapsed = time.perf_counter() - t0
        log.info(
            "populate: %.3fs (%d rows)",
            elapsed,
            len(getattr(self, "rows", []) or []),
        )

        # v0.5.4 raw data caller rewrite
        try:
            self._update_status_bar()
        except Exception:
            pass
'''


NEW_APPLY_ROW_COLOR = '''    def _apply_row_color(self, row_idx, result):
        """v0.5.4 raw data caller rewrite.

        No-op retained for backward compatibility. Row coloring is now handled
        by RawDataTableModel.data(..., Qt.BackgroundRole).
        """
        return
'''


NEW_JUMP_TO_ROW = '''    def _jump_to_row(self, row_idx):
        """v0.5.4 raw data caller rewrite: scroll/select by model index."""
        try:
            row_idx = int(row_idx)
        except Exception:
            return

        if not hasattr(self, "raw_data_model"):
            return
        if row_idx < 0 or row_idx >= self.raw_data_model.rowCount():
            return

        index = self.raw_data_model.index(row_idx, 0)
        self.table.scrollTo(index)
        self.table.selectRow(row_idx)
'''


NEW_APPLY_SUGGESTION = '''    def _apply_suggestion(self, row_idx):
        """v0.5.4 raw data caller rewrite: apply suggestion via model."""
        try:
            row_idx = int(row_idx)
        except Exception:
            return

        if not hasattr(self, "raw_data_model"):
            return

        suggestion = self.raw_data_model.suggestion(row_idx)
        if not suggestion:
            return

        self.raw_data_model.apply_suggestion(row_idx, suggestion)

        # Underlying self.rows is the same dict list held by the model, but
        # keep downstream tabs in sync just like the old code did.
        try:
            if hasattr(self, "modified_tab"):
                self.modified_tab.refresh_from_parent()
        except Exception:
            pass

        try:
            if getattr(self, "_recovery_timer", None) is not None:
                self._recovery_timer.mark_dirty()
        except Exception:
            pass

        try:
            self._update_status_bar()
        except Exception:
            pass
'''


NEW_CONTEXT_MENU = '''    def _on_context_menu(self, pos):
        """v0.5.4 raw data caller rewrite: context menu for QTableView."""
        if not hasattr(self, "raw_data_model"):
            return

        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        row_idx = index.row()
        suggestion = self.raw_data_model.suggestion(row_idx)

        menu = QMenu(self)

        if suggestion:
            apply_action = QAction("Apply Suggestion", self)
            apply_action.triggered.connect(lambda _checked=False, r=row_idx: self._apply_suggestion(r))
            menu.addAction(apply_action)

        jump_action = QAction("Jump to Point", self)
        jump_action.triggered.connect(lambda _checked=False, r=row_idx: self._jump_to_row(r))
        menu.addAction(jump_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))
'''


replacements = [
    ("_populate_table", NEW_POPULATE_TABLE),
    ("_apply_row_color", NEW_APPLY_ROW_COLOR),
    ("_jump_to_row", NEW_JUMP_TO_ROW),
    ("_apply_suggestion", NEW_APPLY_SUGGESTION),
    ("_on_context_menu", NEW_CONTEXT_MENU),
]

applied = 0
for method_name, new_body in replacements:
    src, ok = replace_method(src, method_name, new_body)
    if ok:
        applied += 1
        print(f"[OK] Replaced {method_name}")

# Add sentinel comment near top after optional v0.5.3 diag comment/docstring area.
if SENTINEL not in src:
    src = "# v0.5.4 raw data caller rewrite\n" + src

# Final AST check before save.
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup at {backup}")
    sys.exit(1)

MW.write_text(src, encoding="utf-8")
print(f"[DONE] Applied {applied}/5 method rewrites.")
print("")
print("Next: launch the app and open your test file.")
print("Expected log line:")
print("  populate: 0.xxxs (525 rows)")