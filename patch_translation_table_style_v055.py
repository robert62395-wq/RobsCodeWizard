"""v0.5.5: Fix Translation tab readability (dark theme contrast issue).

Problem:
- Light row colors + light text = unreadable in dark theme.

Solution:
- Force high-contrast table styling (dark text on light background).

Safe:
- Only modifies translation_tab.py
- AST validated before saving
- Fully reversible via backup
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation style fix"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_style_fix.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created at {backup}")

# ------------------------------------------------------------
# Find where the table is created
# ------------------------------------------------------------

lines = src.splitlines()

insert_index = None

for i, line in enumerate(lines):
    # Works for both QTableWidget or QTableView
    if "self.table =" in line:
        insert_index = i + 1
        break

if insert_index is None:
    print("[ERROR] Could not find table creation line (self.table = ...)")
    sys.exit(1)

# ------------------------------------------------------------
# Insert stylesheet directly after table creation
# ------------------------------------------------------------

STYLE_BLOCK = [
    "        # v0.5.5 translation style fix",
    "        try:",
    "            self.table.setStyleSheet(\"\"\"",
    "            QTableView, QTableWidget {",
    "                color: #000000;",
    "                background-color: #FFFFFF;",
    "                gridline-color: #CCCCCC;",
    "            }",
    "            QHeaderView::section {",
    "                background-color: #E6E6E6;",
    "                color: #000000;",
    "                font-weight: bold;",
    "            }",
    "            \"\"\")",
    "        except Exception:",
    "            pass",
]

lines[insert_index:insert_index] = STYLE_BLOCK

new_src = "\n".join(lines)

# Add sentinel
new_src = "# v0.5.5 translation style fix\n" + new_src

# ------------------------------------------------------------
# Validate syntax BEFORE writing
# ------------------------------------------------------------

try:
    ast.parse(new_src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:", e)
    print("File NOT saved. Restore from backup.")
    sys.exit(1)

FILE.write_text(new_src, encoding="utf-8")

print("[DONE] Translation tab readability fixed.")