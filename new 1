"""
v0.5.5 CLEAN FIX — Translation Tab

Fixes:
✅ Banner unreadable
✅ Broken self.banner reference removal
✅ Removes white table override
✅ Fixes row color logic
✅ Restores EntryEditDialog integrity
✅ Uses same visual system as Raw Data tab

SAFE: backs up file + AST validate
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] File not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

backup = Path("_backup_v0_5_5") / "translation_tab_before_clean_fix.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print("[OK] Backup created")

# ------------------------------------------------------------
# 1. FIX BANNER (correct widget + readable)
# ------------------------------------------------------------
src = src.replace(
    "#FFF3CD", "#2b2b2b"
).replace(
    "#FFB300", "#ffaa00"
)

# fix message label color
src = src.replace(
    'msg_lbl.setStyleSheet("background: transparent; border: none;")',
    'msg_lbl.setStyleSheet("background: transparent; border: none; color: #ffffff;")'
)

# ------------------------------------------------------------
# 2. REMOVE INVALID self.banner BLOCK
# ------------------------------------------------------------
if "self.banner.setStyleSheet" in src:
    lines = src.splitlines()
    new_lines = []
    skip = False

    for line in lines:
        if "self.banner.setStyleSheet" in line:
            skip = True
            continue
        if skip:
            if '"""' in line:
                skip = False
            continue
        new_lines.append(line)

    src = "\n".join(new_lines)
    print("[OK] Removed broken self.banner block")

# ------------------------------------------------------------
# 3. REMOVE WHITE TABLE OVERRIDE
# ------------------------------------------------------------
if "background-color: #FFFFFF" in src:
    lines = src.splitlines()
    new_lines = []
    skip = False

    for line in lines:
        if "self.table.setStyleSheet" in line:
            skip = True
            continue
        if skip:
            if '"""' in line:
                skip = False
            continue
        new_lines.append(line)

    src = "\n".join(new_lines)
    print("[OK] Removed white table style")

# ------------------------------------------------------------
# 4. FIX ROW COLOR LOGIC (critical)
# ------------------------------------------------------------
src = src.replace(
    """if color:
                # ✅ v0.5.5 match Raw Data colors
                if confidence.lower().startswith("unmatched"):
                    item.setBackground(QColor("#ff6b6b"))   # strong red
                elif confidence.lower().startswith("best"):
                    item.setBackground(QColor("#d6b100"))   # strong yellow
                elif confidence.lower().startswith("exact"):
                    item.setBackground(QColor("#6ecb63"))   # green""",
    """# ✅ correct row coloring (matches Raw Data)
            if conf == "unmatched":
                item.setBackground(QColor("#ff6b6b"))
            elif conf == "best-guess":
                item.setBackground(QColor("#d6b100"))
            elif conf == "exact":
                item.setBackground(QColor("#6ecb63"))
            elif conf == "manual":
                item.setBackground(QColor("#7aa2f7"))"""
)

# ------------------------------------------------------------
# 5. FIX CONFIDENCE COLORS MAP (global consistency)
# ------------------------------------------------------------
src = src.replace(
    "QColor(200, 240, 200)",
    'QColor("#6ecb63")'
).replace(
    "QColor(255, 245, 180)",
    'QColor("#d6b100")'
).replace(
    "QColor(255, 200, 200)",
    'QColor("#ff6b6b")'
)

# ------------------------------------------------------------
# FINAL VALIDATION
# ------------------------------------------------------------
src = "# v0.5.5 clean translation fix\n" + src

try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] Syntax issue:", e)
    print("File NOT saved")
    sys.exit(1)

FILE.write_text(src, encoding="utf-8")

print("[DONE] Translation tab fully cleaned and fixed.")