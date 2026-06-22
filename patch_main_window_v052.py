"""v0.5.2 patcher: status bar integration into main_window.py."""
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")
if not MW.exists():
    print(f"[ERROR] {MW} not found.")
    sys.exit(1)

src = MW.read_text(encoding="utf-8")
SENTINEL = "v0.5.2 status bar"
if SENTINEL in src:
    print(f"[OK] {MW} already patched.")
    sys.exit(0)

backup_dir = Path("_backup_v0_5_2")
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / MW.name).write_text(src, encoding="utf-8")
print(f"[1/4] Backed up {MW} -> {backup_dir / MW.name}")

# Edit 1: Add imports after TranslationTab/ConvertLineConnectDialog imports
import_anchor = "from app.ui.convert_line_connect_dialog import ConvertLineConnectDialog"
if import_anchor not in src:
    import_anchor = "from app.ui.translation_tab import TranslationTab"
new_imports = (
    import_anchor + "\n"
    "# v0.5.2 status bar + help icons\n"
    "from app.services.status_bar_helper import format_permanent_status\n"
    "from app.ui.help_icon import HelpIcon"
)
if import_anchor in src:
    src = src.replace(import_anchor, new_imports, 1)
    print("[2/4] Added imports for HelpIcon and format_permanent_status")
else:
    print("[WARN] Could not find import anchor")

# Edit 2: Add status bar init at end of _build_ui (after last addTab)
addtab_patterns = [
    'self.tabs.addTab(self.export_tab, "Export")',
    'self.tabs.addTab(self.modified_tab, "Modified Data")',
]
init_added = False
for pat in addtab_patterns:
    if pat in src and not init_added:
        replacement = (
            pat + "\n"
            "        # v0.5.2 status bar init\n"
            '        sb = self.statusBar()\n'
            '        sb.showMessage("Ready")'
        )
        src = src.replace(pat, replacement, 1)
        init_added = True
        print("[3/4] Added QStatusBar initialization")
        break
if not init_added:
    print("[WARN] Could not find addTab anchor")

# Edit 3: Add _update_status_bar and _flash_status methods before _populate_table
populate_anchor = "    def _populate_table(self):"
helper_methods = (
    "    def _update_status_bar(self):\n"
    '        """v0.5.2: refresh permanent status bar text."""\n'
    "        try:\n"
    "            text = format_permanent_status(\n"
    '                getattr(self, "codeset", None),\n'
    '                getattr(self, "source_path", None),\n'
    '                getattr(self, "rows", None),\n'
    '                getattr(self, "results", None),\n'
    "            )\n"
    "            self.statusBar().showMessage(text)\n"
    "        except Exception:\n"
    "            pass\n"
    "\n"
    "    def _flash_status(self, message, msec=5000):\n"
    '        """v0.5.2: transient status message."""\n'
    "        try:\n"
    "            self.statusBar().showMessage(message, msec)\n"
    "        except Exception:\n"
    "            pass\n"
    "\n"
    + populate_anchor
)
if populate_anchor in src:
    src = src.replace(populate_anchor, helper_methods, 1)
    print("[4/4] Added _update_status_bar and _flash_status methods")
else:
    print("[WARN] Could not find _populate_table anchor")

MW.write_text(src, encoding="utf-8")
print(f"[DONE] Patched {MW}")
print("MANUAL: add self._update_status_bar() calls at the end of on_open_file,")
print("        _on_revalidation_done, and _maybe_restore_session methods.")