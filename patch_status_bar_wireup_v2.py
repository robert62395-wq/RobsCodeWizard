"""v0.5.2.3 Part 2a (v2): robust wireup patcher."""
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")
if not MW.exists():
    print(f"[ERROR] {MW} not found.")
    sys.exit(1)

src = MW.read_text(encoding="utf-8")

if "v0.5.2 status bar" not in src:
    print(f"[ERROR] v0.5.2.1 patch missing. Run patch_main_window_v052.py first.")
    sys.exit(1)

# Idempotency check
SENTINEL = "v0.5.2.3 status bar wireup"
if SENTINEL in src:
    print(f"[OK] {MW} already wired up.")
    sys.exit(0)

backup = Path("_backup_v0_5_2_3") / MW.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {MW}")

WIREUP = "\n            self._update_status_bar()  # v0.5.2.3 status bar wireup"

patches_applied = 0

# Patch 1: on_open_file - after recovery.save_session
a1 = "recovery.save_session(self.rows, source_path=path, suggestions=self.suggestions)"
if a1 in src and src.count(a1) >= 1:
    src = src.replace(a1, a1 + WIREUP, 1)
    patches_applied += 1
    print(f"[OK] Patch 1: on_open_file")
else:
    print(f"[WARN] Patch 1: anchor not found")

# Patch 2: _on_revalidation_done - after the end-to-end log line
a2 = 'log.info("[diag] end-to-end code-set switch: %.3fs", t5 - self._reval_t0)'
if a2 in src:
    # This line is inside an if-block, so we need to indent the wireup differently
    indented = "\n        self._update_status_bar()  # v0.5.2.3 status bar wireup"
    src = src.replace(a2, a2 + indented, 1)
    patches_applied += 1
    print(f"[OK] Patch 2: _on_revalidation_done")
else:
    print(f"[WARN] Patch 2: anchor not found")

# Patch 3: _maybe_restore_session - use a more unique anchor than export_btn.setEnabled
# Try a few candidates in order
restore_candidates = [
    'self.modified_tab.refresh_from_parent()',  # last call in restore method
    'self.suggestions = data.get("suggestions") or build_suggestions(self.rows, self.codeset, self.results)',
]
patched3 = False
for candidate in restore_candidates:
    # We only want to match if this candidate appears inside _maybe_restore_session.
    # That method comes after _on_revalidation_error. Find that index first.
    method_start = src.find("def _maybe_restore_session(self):")
    if method_start < 0:
        continue
    # Find the next method def after _maybe_restore_session
    next_def = src.find("\n    def ", method_start + 10)
    if next_def < 0:
        next_def = len(src)
    method_text = src[method_start:next_def]
    if candidate in method_text:
        # Replace only within this method's text
        new_method = method_text.replace(candidate, candidate + "\n        self._update_status_bar()  # v0.5.2.3 status bar wireup", 1)
        src = src[:method_start] + new_method + src[next_def:]
        patches_applied += 1
        print(f"[OK] Patch 3: _maybe_restore_session (using anchor '{candidate[:40]}...')")
        patched3 = True
        break
if not patched3:
    print(f"[WARN] Patch 3: no suitable anchor found in _maybe_restore_session")

# ALWAYS write the file so any successful patches persist
MW.write_text(src, encoding="utf-8")
print(f"")
print(f"[DONE] {patches_applied}/3 patches applied. File saved.")
print(f"Restart the app and open a CSV - status bar should populate.")