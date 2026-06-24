"""v0.5.4 Step 3 v2: rewrite Raw Data table callers using AST line numbers.

This replaces the old QTableWidget call sites with QTableView + RawDataTableModel
methods using the actual FunctionDef line numbers from ast.parse().
"""

import ast
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

backup = Path("_backup_v0_5_4") / "main_window_before_callers_v2.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {MW} -> {backup}")

try:
    tree = ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] main_window.py is not valid before patch: {e}")
    sys.exit(1)


def find_method_nodes(tree, names):
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            found[node.name] = node
    return found


TARGETS = {
    "_populate_table",
    "_apply_row_color",
    "_jump_to_row",
    "_on_context_menu",
    "_apply_suggestion",
}

found = find_method_nodes(tree, TARGETS)
missing = sorted(TARGETS - set(found))
if missing:
    print(f"[ERROR] Missing expected methods: {missing}")
    print("        File NOT saved.")
    sys.exit(1)


NEW_METHODS = {
"_populate_table": '''    def _populate_table(self):
        """v0.5.4 raw data caller rewrite: fast model/view populate.

        Old path created thousands of QTableWidgetItems and colored cells one by one.
        New path resets RawDataTableModel once and lets Qt request visible cells on demand.
        """
        import time
        t0 = time.perf_counter()

        if not hasattr(self, "raw_data_model"):
            log.warning("populate skipped: raw_data_model is missing")
            return

        self.raw_data_model.set_data(
            getattr(self, "rows", []),
            getattr(self, "results", []),
            getattr(self, "suggestions", []),
        )

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

        try:
            self._update_status_bar()
        except Exception:
            pass

        try:
            if getattr(self, "_recovery_timer", None) is not None:
                self._recovery_timer.mark_dirty()
        except Exception:
            pass
''',

"_apply_row_color": '''    def _apply_row_color(self, i, row=None, result=None):
        """v0.5.4 raw data caller rewrite.

        No-op retained for backward compatibility. Row coloring now happens in
        RawDataTableModel.data(..., Qt.BackgroundRole).
        """
        return
''',

"_jump_to_row": '''    def _jump_to_row(self, row_index):
        """v0.5.4 raw data caller rewrite: scroll/select by model index."""
        try:
            row_index = int(row_index)
        except Exception:
            return

        if not hasattr(self, "raw_data_model"):
            return

        if row_index < 0 or row_index >= self.raw_data_model.rowCount():
            return

        index = self.raw_data_model.index(row_index, 0)
        self.table.scrollTo(index)
        self.table.selectRow(row_index)
''',

"_on_context_menu": '''    def _on_context_menu(self, pos):
        """v0.5.4 raw data caller rewrite: context menu for QTableView."""
        if not hasattr(self, "raw_data_model"):
            return

        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        suggestion = self.raw_data_model.suggestion(row)

        menu = QMenu(self)

        if suggestion:
            action = QAction("Apply Suggestion", self)
            action.triggered.connect(
                lambda _checked=False, r=row, s=suggestion: self._apply_suggestion(r, s)
            )
            menu.addAction(action)

        jump_action = QAction("Jump to Point", self)
        jump_action.triggered.connect(lambda _checked=False, r=row: self._jump_to_row(r))
        menu.addAction(jump_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))
''',

"_apply_suggestion": '''    def _apply_suggestion(self, row, suggestion=None):
        """v0.5.4 raw data caller rewrite: apply suggestion via RawDataTableModel."""
        try:
            row = int(row)
        except Exception:
            return

        if not hasattr(self, "raw_data_model"):
            return

        if suggestion is None:
            suggestion = self.raw_data_model.suggestion(row)

        if not suggestion:
            return

        self.raw_data_model.apply_suggestion(row, suggestion)

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
''',
}


# Replace methods from bottom to top so line numbers remain valid.
lines = src.splitlines()
for name, node in sorted(found.items(), key=lambda kv: kv[1].lineno, reverse=True):
    start = node.lineno - 1
    end = node.end_lineno
    replacement = NEW_METHODS[name].rstrip().splitlines()
    lines[start:end] = replacement
    print(f"[OK] Replaced {name} at lines {node.lineno}-{node.end_lineno}")

new_src = "\n".join(lines) + "\n"

# Add sentinel at top.
if SENTINEL not in new_src:
    new_src = f"# {SENTINEL}\n" + new_src

try:
    ast.parse(new_src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup at {backup}")
    sys.exit(1)

MW.write_text(new_src, encoding="utf-8")
print("[DONE] Applied 5/5 Raw Data model/view caller rewrites.")
print("")
print("Next:")
print("  1. Run syntax check.")
print("  2. Launch app.")
print("  3. Open test file.")
print("  4. Look for log line: populate: 0.xxxs (<rows> rows)")