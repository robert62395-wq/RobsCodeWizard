"""v0.5.5: Fix Translation tab banner readability (under-construction warning).

Problem:
- Light background + light text = unreadable on dark theme.

Fix:
- Dark text + slightly stronger background contrast
"""

import ast
import sys
from pathlib import Path

FILE = Path("app/ui/translation_tab.py")

if not FILE.exists():
    print("[ERROR] translation_tab.py not found")
    sys.exit(1)

src = FILE.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 banner style fix"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "translation_tab_before_banner_fix.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created at {backup}")

lines = src.splitlines()

# Find the banner QLabel creation
inserted = False

for i, line in enumerate(lines):
    if "Under construction" in line:
        # Walk backward to find QLabel instantiation
        for j in range(i, max(i - 20, 0), -1):
            if "QLabel(" in lines[j]:
                insert_index = j + 1

                STYLE_FIX = [
                    "        # v0.5.5 banner style fix",
                    "        try:",
                    "            self.banner.setStyleSheet(\"\"\"",
                    "            QLabel {",
                    "                background-color: #FFF6D1;",
                    "                color: #000000;",
                    "                border: 1px solid #F0C36D;",
                    "                border-radius: 4px;",
                    "                padding: 12px;",
                    "                font-size: 13px;",
                    "            }",
                    "            \"\"\")",
                    "        except Exception:",
                    "            pass",
                ]

                lines[insert_index:insert_index] = STYLE_FIX
                inserted = True
                break
        break

if not inserted:
    print("[ERROR] Could not locate banner QLabel block.")
    sys.exit(1)

new_src = "\n".join(lines)
new_src = "# v0.5.5 banner style fix\n" + new_src

# Validate before writing
try:
    ast.parse(new_src)
except SyntaxError as e:
    print("[ERROR] Syntax error after patch:", e)
    print("File NOT saved.")
    sys.exit(1)

FILE.write_text(new_src, encoding="utf-8")

print("[DONE] Translation banner readability fixed.")