"""v0.5.5 Step 2: auto-load Translation tab when file is opened."""

import ast
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")

src = MW.read_text(encoding="utf-8")

SENTINEL = "v0.5.5 translation autoload"
if SENTINEL in src:
    print("[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_5") / "main_window_before_translation_autoload.py"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backup created at {backup}")


tree = ast.parse(src)

target = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "on_open_file":
        target = node
        break

if not target:
    print("[ERROR] Could not find on_open_file")
    sys.exit(1)


lines = src.splitlines()

insert_block = [
    "        # v0.5.5 translation autoload",
    "        try:",
    "            if hasattr(self, 'translation_tab'):",
    "                # Push fresh data into translation tab",
    "                self.translation_tab.set_rows(self.rows)",
    "                # Default to showing only codes in this file",
    "                if hasattr(self.translation_tab, 'show_used_only'):",
    "                    self.translation_tab.show_used_only.setChecked(True)",
    "                # Refresh view",
    "                if hasattr(self.translation_tab, 'refresh'):",
    "                    self.translation_tab.refresh()",
    "        except Exception as exc:",
    "            log.exception('Translation auto-load failed: %s', exc)",
]

insert_line = target.end_lineno - 1
lines[insert_line:insert_line] = insert_block

new_src = "\n".join(lines)

new_src = "# v0.5.5 translation autoload\n" + new_src

ast.parse(new_src)  # validate

MW.write_text(new_src, encoding="utf-8")

print("[DONE] Translation tab now auto-loads after file open.")