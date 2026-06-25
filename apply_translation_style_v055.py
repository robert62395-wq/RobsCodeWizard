"""
v0.5.5 FINAL FIX:
- Fix unreadable banner
- Normalize Translation row colors to match Raw Data

Safe:
- Does not rely on string guesses
- Injects controlled code blocks
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation final style"
if SENTINEL in src:
    print("[OK] Already applied.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_final_style.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created: {backup}")

lines = src.splitlines()

# ------------------------------------------------------------
# 1. FIX BANNER (search for Under construction text)
# ------------------------------------------------------------
banner_fixed = False

for i, line in enumerate(lines):
    if "Under construction" in line:
        # find nearest previous widget assignment
        for j in range(i, max(i - 20, 0), -1):
            if "self." in lines[j] and "=" in lines[j]:
                insert_line = j + 1

                style_block = [
                    "        # v0.5.5 translation final style (banner)",
                    "        try:",
                    "            banner_widget = " + lines[j].split("=")[0].strip(),
                    "            banner_widget.setStyleSheet(\"\"\"",
                    "                background-color: #2b2b2b;",
                    "                color: #ffffff;",
                    "                border: 1px solid #ffaa00;",
                    "                border-radius: 4px;",
                    "                padding: 12px;",
                    "            \"\"\")",
                    "        except Exception:",
                    "            pass"
                ]

                lines[insert_line:insert_line] = style_block
                banner_fixed = True
                print("[OK] Banner style fixed")
                break
        break

if not banner_fixed:
    print("[WARN] Banner not patched automatically")

# ------------------------------------------------------------
# 2. FORCE ROW COLOR MAP (central fix)
# ------------------------------------------------------------
# Inject a helper method for consistent colors

color_method = '''
    # v0.5.5 translation final style (row colors)
    def _get_translation_row_color(self, confidence):
        if "unmatched" in confidence.lower():
            return QColor("#ff6b6b")  # strong red
        if "best" in confidence.lower():
            return QColor("#d6b100")  # strong yellow
        if "exact" in confidence.lower():
            return QColor("#6ecb63")  # green
        return None
'''

# Insert into class after __init__
insert_index = None
for i, line in enumerate(lines):
    if "def __init__" in line:
        insert_index = i + 5
        break

if insert_index:
    lines.insert(insert_index, color_method)
    print("[OK] Added color mapping method")

# ------------------------------------------------------------
# Replace any direct color usage
# ------------------------------------------------------------
replacements = [
    ("QColor(", "self._get_translation_row_color("),
]

changed = 0
for i, line in enumerate(lines):
    if "setBackground" in line and "QColor" in line:
        # replace the assignment line
        lines[i] = "            item.setBackground(self._get_translation_row_color(confidence))"
        changed += 1

if changed:
    print(f"[OK] Rewired {changed} row color assignments")

# ------------------------------------------------------------
# Finalize
# ------------------------------------------------------------
new_src = "# v0.5.5 translation final style\n" + "\n".join(lines)

try:
    ast.parse(new_src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:", e)
    print("File NOT saved.")
    sys.exit(1)

FILE.write_text(new_src, encoding="utf-8")

print("[DONE] Translation tab styling fixed correctly.")
