"""v0.5.5: Match Translation tab colors to Raw Data tab (proper dark-theme fix)

Fixes:
- Pastel colors → unreadable
- Banner → unreadable

Approach:
- Replace weak colors with strong Raw Data equivalents
- Do NOT override theme or text color
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation color match raw"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_color_match.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created: {backup}")

# ------------------------------------------------------------
# Replace weak colors with strong dark-theme friendly colors
# ------------------------------------------------------------
replacements = {
    # BAD pale reds → GOOD strong red (same idea as Raw Data)
    "#f4cccc": "#ff6b6b",
    "#f8d7da": "#ff6b6b",
    "#e6b8af": "#ff6b6b",

    # BAD pale yellows → darker yellow
    "#fff2cc": "#d6b100",
    "#ffe599": "#d6b100",

    # BAD pale greens → stronger green
    "#d9ead3": "#6ecb63",
    "#c6e0b4": "#6ecb63",

    # Banner beige → darker background
    "#fff6d1": "#2a2a2a",
    "#fff3cd": "#2a2a2a",
    "#fff8dc": "#2a2a2a",
}

changed = 0
for old, new in replacements.items():
    if old in src:
        src = src.replace(old, new)
        changed += 1

# ------------------------------------------------------------
# FORCE banner text to be readable (targeted fix)
# ------------------------------------------------------------
if "Under construction" in src:
    # Add style once after banner creation
    if "banner.setStyleSheet" not in src:
        insert_index = src.find("Under construction")

        if insert_index != -1:
            lines = src.splitlines()

            # find surrounding block
            for i in range(len(lines)):
                if "Under construction" in lines[i]:
                    insert_line = i + 3
                    break
            else:
                insert_line = None

            if insert_line:
                lines.insert(insert_line,
                    '        self.banner.setStyleSheet("color: #ffffff; background-color: #2a2a2a;")  # v0.5.5 banner fix')
                src = "\n".join(lines)
                changed += 1

# ------------------------------------------------------------
# Add sentinel
# ------------------------------------------------------------
src = "# v0.5.5 translation color match raw\n" + src

# Validate
try:
    ast.parse(src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:", e)
    print("File NOT saved.")
    sys.exit(1)

FILE.write_text(src, encoding="utf-8")

print(f"[DONE] Translation colors fixed ({changed} changes applied).")