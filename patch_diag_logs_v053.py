"""v0.5.3 patcher: downgrade [diag] logging markers from INFO to DEBUG."""
import ast
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")
if not MW.exists():
    print(f"[ERROR] {MW} not found.")
    sys.exit(1)

src = MW.read_text(encoding="utf-8")
SENTINEL = "v0.5.3 diag logs downgraded"
if SENTINEL in src:
    print(f"[OK] {MW} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_3") / MW.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {MW}")

# Count and replace log.info("[diag] ...) -> log.debug("[diag] ...)
before_count = src.count('log.info("[diag]')
src = src.replace('log.info("[diag]', 'log.debug("[diag]')
after_count = src.count('log.debug("[diag]')

# Add sentinel comment so re-runs detect this
if "v0.5.3 diag logs downgraded" not in src:
    src = "# v0.5.3 diag logs downgraded - markers moved from INFO to DEBUG\n" + src

try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    sys.exit(1)

MW.write_text(src, encoding="utf-8")
print(f"[DONE] Downgraded {before_count} [diag] log calls from INFO to DEBUG")
print(f"       (now appearing in logs only when DEBUG level is enabled)")