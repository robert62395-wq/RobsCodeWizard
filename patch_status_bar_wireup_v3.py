"""v0.5.2.3 Part 2a (v3): indent-aware patcher."""
import re
import sys
import ast
from pathlib import Path

MW = Path("app/ui/main_window.py")
src = MW.read_text(encoding="utf-8")

if "v0.5.2 status bar" not in src:
    print("[ERROR] v0.5.2.1 patch missing.")
    sys.exit(1)

if "v0.5.2.3 status bar wireup" in src:
    print("[OK] already wired up.")
    sys.exit(0)

backup = Path("_backup_v0_5_2_3") / MW.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print("[OK] Backed up file")


def inject_after_line(src, anchor_text, comment="v0.5.2.3 status bar wireup"):
    """Insert self._update_status_bar() right after the line containing anchor_text,
    matching that line's indentation."""
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if anchor_text in line:
            indent = re.match(r"^(\s*)", line).group(1)
            new_line = f"{indent}self._update_status_bar()  # {comment}"
            lines.insert(i + 1, new_line)
            return "\n".join(lines), True
    return src, False


# Patch 1: on_open_file
src, ok1 = inject_after_line(src, "recovery.save_session(self.rows, source_path=path, suggestions=self.suggestions)")
print(f"[{'OK' if ok1 else 'WARN'}] Patch 1: on_open_file")

# Patch 2: _on_revalidation_done
src, ok2 = inject_after_line(src, 'log.info("[diag] end-to-end code-set switch: %.3fs", t5 - self._reval_t0)')
print(f"[{'OK' if ok2 else 'WARN'}] Patch 2: _on_revalidation_done")

# Patch 3: _maybe_restore_session - scoped to that method only
method_start = src.find("def _maybe_restore_session(self):")
if method_start >= 0:
    next_def = src.find("\n    def ", method_start + 30)
    if next_def < 0:
        next_def = len(src)
