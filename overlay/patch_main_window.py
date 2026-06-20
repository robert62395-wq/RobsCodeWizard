"""Idempotent patcher for app/ui/main_window.py to wire in the Export tab."""
import re
import sys
from pathlib import Path

MAIN_WINDOW = Path("app/ui/main_window.py")
BACKUP = Path("_backup_v0_4_5/main_window.py")

if not MAIN_WINDOW.exists():
    print(f"[ERROR] {MAIN_WINDOW} not found. Run from project root.")
    sys.exit(1)

src = MAIN_WINDOW.read_text(encoding="utf-8")

# Idempotency check
if "from app.ui.export_tab import ExportTab" in src:
    print("[OK] main_window.py already has ExportTab integration. Nothing to patch.")
    sys.exit(0)

BACKUP.parent.mkdir(parents=True, exist_ok=True)
BACKUP.write_text(src, encoding="utf-8")
print(f"[1/3] Backed up to {BACKUP}")

# 1. Add import after existing translation_tab/convert_line_connect imports
import_anchor = "from app.ui.convert_line_connect_dialog import ConvertLineConnectDialog"
if import_anchor not in src:
    print(f"[ERROR] Could not find anchor: {import_anchor}")
    print("        Your main_window.py may not be the v0.4.2.1 version.")
    sys.exit(1)
src = src.replace(
    import_anchor,
    import_anchor + "\n# v0.4.5: Export tab\nfrom app.ui.export_tab import ExportTab",
)
print("[2/3] Added ExportTab import")

# 2. Add tab after Modified Data tab
tab_anchor = 'self.tabs.addTab(self.modified_tab, "Modified Data")'
if tab_anchor not in src:
    print(f"[ERROR] Could not find tab anchor: {tab_anchor}")
    sys.exit(1)
src = src.replace(
    tab_anchor,
    tab_anchor + "\n        # v0.4.5: Export tab\n        self.export_tab = ExportTab(self)\n        self.tabs.addTab(self.export_tab, \"Export\")",
)
print("[3/3] Added Export tab to tab bar")

MAIN_WINDOW.write_text(src, encoding="utf-8")
print(f"\n[DONE] {MAIN_WINDOW} patched. Export tab will appear next launch.")
