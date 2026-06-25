"""v0.5.5 Step 2 v2: auto-refresh Translation tab after file open.

Fixes v1 patcher issue:
- v1 inserted at the end of on_open_file using AST end_lineno, which landed
  before the body of a trailing if-block in this main_window.py layout.
- v2 inserts immediately after the first self._populate_table() inside
  on_open_file, which is the correct point after rows/results/suggestions
  are available.

This patch does NOT assume TranslationTab has set_rows() or refresh().
Your current TranslationTab reads parent.rows directly and exposes _safe_refresh().
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

SENTINEL = "v0.5.5 translation autoload"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "main_window_before_translation_autoload_v2.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created at {backup}")

# Parse first so we only patch a valid starting file.
try:
    tree = ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] main_window.py is already invalid before patch: {e}")
    print("        Restore from your latest backup before continuing.")
    sys.exit(1)

# Find on_open_file bounds.
target = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "on_open_file":
        target = node
        break

if target is None:
    print("[ERROR] Could not find on_open_file")
    sys.exit(1)

lines = src.splitlines()

# We insert after the first self._populate_table() inside on_open_file.
start = target.lineno - 1
end = target.end_lineno

insert_at = None
for i in range(start, end):
    if "self._populate_table()" in lines[i]:
        insert_at = i + 1
        indent = re.match(r"^(\s*)", lines[i]).group(1)
        break

if insert_at is None:
    print("[ERROR] Could not find self._populate_table() inside on_open_file.")
    print("        File NOT saved.")
    sys.exit(1)

insert_block = [
    f"{indent}# v0.5.5 translation autoload",
    f"{indent}try:",
    f"{indent}    if hasattr(self, 'translation_tab'):",
    f"{indent}        # TranslationTab reads parent.rows directly, so just refresh it.",
    f"{indent}        if hasattr(self.translation_tab, 'show_used_only'):",
    f"{indent}            self.translation_tab.show_used_only.setChecked(True)",
    f"{indent}        if hasattr(self.translation_tab, '_safe_refresh'):",
    f"{indent}            self.translation_tab._safe_refresh()",
    f"{indent}except Exception as exc:",
    f"{indent}    log.exception('Translation auto-load failed: %s', exc)",
]

lines[insert_at:insert_at] = insert_block
new_src = "\n".join(lines) + "\n"

# Sentinel at top.
new_src = "# v0.5.5 translation autoload\n" + new_src

try:
    ast.parse(new_src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print("        File NOT saved.")
    print(f"        Backup is at {backup}")
    sys.exit(1)

MW.write_text(new_src, encoding="utf-8")
print("[DONE] Translation tab now auto-refreshes after file open.")