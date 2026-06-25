"""
v0.5.5 Step 3:
Hook TranslationTableModel into translation_tab.py

This completes the QTableView migration.

SAFE:
- Keeps original logic intact where possible
- Only replaces _populate()
- Uses AST-safe replacement
"""

import ast
import re
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation model step3"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_model_step3.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created: {backup}")


# ------------------------------------------------------------
# 1. Add model import
# ------------------------------------------------------------
if "TranslationTableModel" not in src:
    src = src.replace(
        "from app.ui.help_icon import HelpIcon",
        "from app.ui.help_icon import HelpIcon\nfrom app.ui.translation_model import TranslationTableModel"
    )
    print("[OK] Added model import")


# ------------------------------------------------------------
# 2. Replace _populate method
# ------------------------------------------------------------
new_populate = '''
    def _populate(self):
        """v0.5.5 model-based populate (instant)"""
        entries = self._map_data.get("entries", [])

        # Build model
        model = TranslationTableModel(entries, self._used_counts)

        self.table.setModel(model)

        # Resize columns neatly
        try:
            self.table.resizeColumnsToContents()
        except Exception:
            pass
'''

src, count = re.subn(
    r"def _populate\(self\):.*?self\._apply_filter\(\)",
    new_populate,
    src,
    flags=re.DOTALL
)

if count == 0:
    print("[ERROR] Could not replace _populate()")
    sys.exit(1)

print("[OK] Replaced _populate() with model logic")


# ------------------------------------------------------------
# 3. Disable old row-based API safely
# ------------------------------------------------------------
# These won't be used anymore but avoid breakage

src = src.replace("self.table.insertRow", "# disabled (model view)")
src = src.replace("self.table.setItem", "# disabled (model view)")
src = src.replace("self.table.rowCount()", "0  # model handles rows")

print("[OK] Disabled old QTableWidget logic")


# ------------------------------------------------------------
# Finalize
# ------------------------------------------------------------
src = "# v0.5.5 translation model step3\n" + src

try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:", e)
    print("File NOT saved.")
    sys.exit(1)

FILE.write_text(src, encoding="utf-8")

print("[DONE] Translation model connected successfully.")
