"""v0.5.2.3 Part 2a: wire up self._update_status_bar() calls.

After this patch, the status bar populates dynamically when:
  - A file is opened (on_open_file)
  - Code-set switch revalidates (_on_revalidation_done)
  - A previous session is restored (_maybe_restore_session)
"""
import sys
from pathlib import Path

MW = Path("app/ui/main_window.py")
if not MW.exists():
    print(f"[ERROR] {MW} not found.")
    sys.exit(1)

src = MW.read_text(encoding="utf-8")

# Sanity check: v0.5.2.1 patcher must have run first
PRIOR_SENTINEL = "v0.5.2 status bar"
if PRIOR_SENTINEL not in src:
    print(f"[ERROR] {MW} does not have v0.5.2.1 status bar patch applied.")
    print(f"        Run patch_main_window_v052.py first.")
    sys.exit(1)

# Idempotency check
SENTINEL = "v0.5.2.3 status bar wireup"
if SENTINEL in src:
    print(f"[OK] {MW} already wired up.")
    sys.exit(0)

backup = Path("_backup_v0_5_2_3") / MW.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[1/5] Backed up {MW} -> {backup}")

# v0.5.2.3 calls to inject
WIREUP_LINE = "            self._update_status_bar()  # v0.5.2.3 status bar wireup"

# --- Patch 1: on_open_file ---
# Anchor: the recovery.save_session call near the end of on_open_file's try block
anchor1 = 'recovery.save_session(self.rows, source_path=path, suggestions=self.suggestions)'
if anchor1 in src:
    replacement1 = anchor1 + "\n" + WIREUP_LINE
    src = src.replace(anchor1, replacement1, 1)
    print("[2/5] Added wireup to on_open_file")
else:
    print("[WARN] Could not find anchor in on_open_file - skipping")

# --- Patch 2: _on_revalidation_done ---
# Anchor: the last log.info call in that method (diagnostic timing log)
anchor2 = 'log.info("[diag] end-to-end code-set switch: %.3fs", t5 - self._reval_t0)'
if anchor2 in src:
    # The replacement adds the wireup OUTSIDE the if-block's indentation
    replacement2 = anchor2 + "\n        self._update_status_bar()  # v0.5.2.3 status bar wireup"
    src = src.replace(anchor2, replacement2, 1)
    print("[3/5] Added wireup to _on_revalidation_done")
else:
    print("[WARN] Could not find anchor in _on_revalidation_done - skipping")

# --- Patch 3: _maybe_restore_session ---
# Anchor: the export_btn.setEnabled call near the end of _maybe_restore_session
anchor3 = 'self.export_btn.setEnabled(bool(self.rows))'
