"""
v0.5.5 FINAL TRANSLATION TAB FIX

Fixes:
1. Banner unreadable (light-on-light)
2. Broken `self.banner` reference
3. Incorrect table stylesheet (white override)
4. Broken row-color logic (uses undefined variable)

Safe:
- AST validated
- Backup created
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation final fix"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_final_fix.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created: {backup}")


# ------------------------------------------------------------
# 1. FIX BANNER STYLING
# ------------------------------------------------------------
src = src.replace(
    'frame.setStyleSheet(\n            "QFrame { background-color: #FFF3CD; border: 2px solid #FFB300;"\n            " border-radius: 4px; padding: 8px; }"\n        )',
    '''frame.setStyleSheet(
            "QFrame { background-color: #2b2b2b; border: 2px solid #ffaa00;"
            " border-radius: 4px; padding: 8px; }"
        )'''
)

src = src.replace(
    'msg_lbl.setStyleSheet("background: transparent; border: none;")',
    'msg_lbl.setStyleSheet("background: transparent; border: none; color: #ffffff;")'
)


# ------------------------------------------------------------
# 2. REMOVE BAD TABLE STYLESHEET (white override)
# ------------------------------------------------------------
bad_style_block = '''        try:
            self.table.setStyleSheet("""
            QTableView, QTableWidget {
                color: #000000;
                background-color: #FFFFFF;
                gridline-color: #CCCCCC;
            }
            QHeaderView::section {
                background-color: #E6E6E6;
                color: #000000;
                font-weight: bold;
            }
            """)
        except Exception:
            pass
'''

if bad_style_block in src:
    src = src.replace(bad_style_block, "")
    print("[OK] Removed bad table stylesheet")


# ------------------------------------------------------------
# 3. FIX ROW COLOR LOGIC (CRITICAL BUG)
# ------------------------------------------------------------
src = src.replace(
    '''            if color:
                # ✅ v0.5.5 match Raw Data colors
                if confidence.lower().startswith("unmatched"):
                    item.setBackground(QColor("#ff6b6b"))   # strong red
                elif confidence.lower().startswith("best"):
                    item.setBackground(QColor("#d6b100"))   # strong yellow
                elif confidence.lower().startswith("exact"):
                    item.setBackground(QColor("#6ecb63"))   # green
''',
    '''            # ✅ v0.5.5 proper row coloring (matches Raw Data)
            if conf == "unmatched":
                item.setBackground(QColor("#ff6b6b"))   # red
            elif conf == "best-guess":
                item.setBackground(QColor("#d6b100"))   # yellow
            elif conf == "exact":
                item.setBackground(QColor("#6ecb63"))   # green
            elif conf == "manual":
                item.setBackground(QColor("#7aa2f7"))   # blue
'''
)


# ------------------------------------------------------------
# 4. REMOVE BROKEN banner.setStyleSheet (invalid reference)
# ------------------------------------------------------------
src = src.replace(
    '''        # ✅ v0.5.5 banner fix (dark theme safe)
        self.banner.setStyleSheet("""
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #ffaa00;
        border-radius: 4px;
        padding: 10px;
        """)
''',
    ""
)


# ------------------------------------------------------------
# FINALIZE
# ------------------------------------------------------------
src = "# v0.5.5 translation final fix\n" + src

try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:", e)
    print("File NOT saved.")
    sys.exit(1)

FILE.write_text(src, encoding="utf-8")

print("[DONE] Translation tab fully fixed (banner + colors + logic).")
