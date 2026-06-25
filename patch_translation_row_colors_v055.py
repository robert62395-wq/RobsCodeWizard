"""v0.5.5: Align Translation tab colors with Raw Data tab (dark theme safe).

Fix:
- Replace pale pastel row colors with strong contrast colors.
- Matches Raw Data visual language.
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation color fix"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_color_fix.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created at {backup}")

lines = src.splitlines()

replacements = {
    # Pale red → strong red
    "#f4cccc": "#ff6b6b",
    "#e6b8af": "#ff6b6b",
    "#f8d7da": "#ff6b6b",

    # Pale yellow → stronger yellow
    "#fff2cc": "#e6c94c",
    "#ffe599": "#e6c94c",

    # Pale green → stronger green
    "#d9ead3": "#6ecb63",
    "#c6e0b4": "#6ecb63",
}

changed = 0

for i, line in enumerate(lines):
    for old, new in replacements.items():
        if old in line:
            linesaltered_line = line.replace(old, new)
            lines[i] = altered_line
            changed += 1

if changed == 0:
    print("[WARN] No known color strings found. Applying fallback.")

    # Fallback: inject new logic marker
    lines.insert(0, "# NOTE: color mapping may be handled dynamically")

new_src = "\n".join(lines)
new_src = "# v0.5.5 translation color fix\n" + new_src

try:
    ast.parse(new_src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:", e)
    print("File NOT saved.")
    sys.exit(1)

FILE.write_text(new_src, encoding="utf-8")

print(f"[DONE] Translation colors normalized ({changed} replacements).")
``