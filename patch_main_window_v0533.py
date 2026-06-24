"""v0.5.3.3: wire parse error dialog + recovery timer into main_window.py."""
import ast
import re
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")
if not MW.exists():
    print(f"[ERROR] {MW} not found.")
    sys.exit(1)

src = MW.read_text(encoding="utf-8")
SENTINEL = "v0.5.3.3 wireup"
if SENTINEL in src:
    print(f"[OK] {MW} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_3_3") / MW.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {MW}")

# Step 1: add imports
imports_to_add = [
    "from app.services.file_parser import parse_file_with_errors  # v0.5.3.3",
    "from app.services.recovery_timer import RecoveryTimer  # v0.5.3.3",
    "from app.ui.parse_error_dialog import ParseErrorDialog  # v0.5.3.3",
]
import_anchor = "from app.services.file_parser import parse_file"
if import_anchor in src:
    insert = import_anchor + "\n" + "\n".join(imports_to_add)
    src = src.replace(import_anchor, insert, 1)
    print("[OK] Added v0.5.3.3 imports")
else:
    print(f"[WARN] Could not find import anchor")

# Step 2: create RecoveryTimer in __init__ — anchor on the existing recovery wiring
init_anchor = "if self.settings.get(\"check_on_startup\", True):"
init_insert = """# v0.5.3.3 wireup: auto-save recovery timer
        try:
            self._recovery_timer = RecoveryTimer(self)
            self._recovery_timer.set_save_callback(
                lambda: recovery.save_session(
                    self.rows,
                    source_path=self.source_path,
                    suggestions=self.suggestions,
                )
            )
            if self.settings.get("auto_save_recovery", True):
                self._recovery_timer.start()
        except Exception as exc:
            log.exception("RecoveryTimer init failed: %s", exc)
            self._recovery_timer = None
        """

if init_anchor in src:
    src = src.replace(init_anchor, init_insert + init_anchor, 1)
    print("[OK] Wired RecoveryTimer in __init__")
else:
    print("[WARN] Could not find __init__ anchor")

# Step 3: switch on_open_file to parse_file_with_errors + show dialog
open_anchor = "self.rows = parse_file(path, self.codeset)"
open_replacement = """# v0.5.3.3 wireup: collect parse errors and show dialog if any
            _parse_result = parse_file_with_errors(path, self.codeset)
            self.rows = _parse_result.rows
            if _parse_result.has_errors:
                try:
                    _dlg = ParseErrorDialog(_parse_result, source_path=path, parent=self)
                    _dlg.exec()
                except Exception as exc:
                    log.exception("ParseErrorDialog failed: %s", exc)"""

if open_anchor in src:
    src = src.replace(open_anchor, open_replacement, 1)
    print("[OK] on_open_file uses parse_file_with_errors")
else:
    print("[WARN] Could not find on_open_file anchor")

# Step 4: hook mark_dirty into every _update_status_bar call site
lines = src.split("\n")
new_lines = []
marked = 0
for line in lines:
    new_lines.append(line)
    if "self._update_status_bar()" in line and "v0.5.3.3" not in line:
        indent = re.match(r"^(\s*)", line).group(1)
        new_lines.append(
            f"{indent}if getattr(self, '_recovery_timer', None) is not None:\n"
            f"{indent}    self._recovery_timer.mark_dirty()  # v0.5.3.3 wireup"
        )
        marked += 1
src = "\n".join(new_lines)
print(f"[OK] {marked} mark_dirty() calls inserted after _update_status_bar() sites")

# Step 5: stop timer cleanly in closeEvent
close_anchor = "def closeEvent(self, event):"
close_addition = """def closeEvent(self, event):
        # v0.5.3.3 wireup: stop recovery timer before close
        try:
            if getattr(self, '_recovery_timer', None) is not None:
                self._recovery_timer.force_save_now()
                self._recovery_timer.stop()
        except Exception:
            pass
        """
if close_anchor in src:
    src = src.replace(close_anchor, close_addition, 1)
    print("[OK] closeEvent stops timer cleanly")
else:
    print("[WARN] Could not find closeEvent anchor")

# Final AST check
try:
    ast.parse(src)
except SyntaxError as ex:
    print(f"[ERROR] Syntax error after patch: {ex}")
    print(f"        File NOT saved. Backup at {backup}")
    sys.exit(1)

MW.write_text(src, encoding="utf-8")
print(f"[DONE] {MW} patched.")