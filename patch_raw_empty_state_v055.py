"""v0.5.5 Step 1: Raw Data empty-state panel.

Adds a first-launch / no-file-loaded message to the Raw Data tab and wires it
to _populate_table so it hides after rows are loaded.

Backs up main_window.py to _backup_v0_5_5/.
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

SENTINEL = "v0.5.5 raw empty state"
if SENTINEL in src:
    print(f"[OK] {MW} already has v0.5.5 raw empty state.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "main_window_before_raw_empty_state.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {MW} -> {backup}")


# ------------------------------------------------------------
# Step 1: Insert empty-state QLabel in _build_raw_data_tab.
# ------------------------------------------------------------
EMPTY_STATE_BLOCK = '''        # v0.5.5 raw empty state
        self.raw_empty_state = QLabel(
            "<h2>No point file loaded yet</h2>"
            "<p>Open a CSV/TXT point file to begin reviewing survey codes, "
            "linework, elevations, and export readiness.</p>"
            "<p><b>Tip:</b> Use the <i>Open CSV/TXT...</i> button above to start.</p>"
        )
        self.raw_empty_state.setWordWrap(True)
        self.raw_empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.raw_empty_state.setStyleSheet(
            "QLabel {"
            " background-color: #F6F8FA;"
            " border: 1px solid #D0D7DE;"
            " border-radius: 6px;"
            " padding: 24px;"
            " color: #24292F;"
            "}"
        )
        layout.addWidget(self.raw_empty_state)
'''

# Insert it after layout.addLayout(bar), before the table setup.
anchor = "        layout.addLayout(bar)\n"
if anchor in src:
    src = src.replace(anchor, anchor + EMPTY_STATE_BLOCK, 1)
    print("[OK] Added Raw Data empty-state panel")
else:
    print("[ERROR] Could not find layout.addLayout(bar) anchor in _build_raw_data_tab.")
    print("        File NOT saved.")
    sys.exit(1)


# ------------------------------------------------------------
# Step 2: Replace _populate_table with a v0.5.5-aware version.
# ------------------------------------------------------------
try:
    tree = ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] main_window.py is invalid before _populate_table rewrite: {e}")
    sys.exit(1)

populate_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_populate_table":
        populate_node = node
        break

if populate_node is None:
    print("[ERROR] Could not find _populate_table method.")
    print("        File NOT saved.")
    sys.exit(1)

NEW_POPULATE = '''    def _populate_table(self):
        """v0.5.5: fast model/view populate + empty-state refresh."""
        import time
        t0 = time.perf_counter()

        if not hasattr(self, "raw_data_model"):
            log.warning("populate skipped: raw_data_model is missing")
            return

        rows = getattr(self, "rows", []) or []
        results = getattr(self, "results", []) or []
        suggestions = getattr(self, "suggestions", []) or []

        self.raw_data_model.set_data(rows, results, suggestions)

        # v0.5.5 raw empty state
        try:
            if hasattr(self, "raw_empty_state"):
                self.raw_empty_state.setVisible(len(rows) == 0)
        except Exception:
            pass

        try:
            if self.raw_data_model.rowCount() > 0:
                self.table.selectRow(0)
        except Exception:
            pass

        elapsed = time.perf_counter() - t0
        log.info("populate: %.3fs (%d rows)", elapsed, len(rows))

        try:
            self._update_status_bar()
        except Exception:
            pass

        try:
            if getattr(self, "_recovery_timer", None) is not None:
                self._recovery_timer.mark_dirty()
        except Exception:
            pass
'''

lines = src.splitlines()
start = populate_node.lineno - 1
end = populate_node.end_lineno
lines[start:end] = NEW_POPULATE.rstrip().splitlines()
src = "\n".join(lines) + "\n"

# Add sentinel.
src = f"# {SENTINEL}\n" + src


# ------------------------------------------------------------
# Step 3: AST check before save.
# ------------------------------------------------------------
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup at {backup}")
    sys.exit(1)

MW.write_text(src, encoding="utf-8")
print("[DONE] v0.5.5 Raw Data empty-state panel added and syntax-checked.")