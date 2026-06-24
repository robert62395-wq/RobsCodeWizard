"""v0.5.3.2: fix legacy test_odot_exporter.py to unpack 3-tuple returns."""
import ast
import sys
from pathlib import Path

T = Path("tests/test_odot_exporter.py")
if not T.exists():
    print(f"[ERROR] {T} not found.")
    sys.exit(1)

src = T.read_text(encoding="utf-8")
SENTINEL = "v0.5.3.2 three-tuple unpack"
if SENTINEL in src:
    print(f"[OK] {T} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_3_2") / T.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {T}")

# Three identical replacements for the failing test functions.
# v0.5.3.1 changed the exporter return shape from (written, conversions) to
# (written, conversions, errors). Update the unpacking everywhere.
replacements = [
    (
        "written, conversions = export_vdt_to_civil3d(rows, out)",
        "written, conversions, _errors = export_vdt_to_civil3d(rows, out)",
    ),
    (
        "written, conversions = export_odot_to_civil3d(rows, out)",
        "written, conversions, _errors = export_odot_to_civil3d(rows, out)",
    ),
    (
        "written, conversions = export_odot_to_openroads(rows, out, use_numeric=True)",
        "written, conversions, _errors = export_odot_to_openroads(rows, out, use_numeric=True)",
    ),
]

applied = 0
for old, new in replacements:
    if old in src and new not in src:
        src = src.replace(old, new)
        applied += 1
        print(f"[OK] Replaced: {old[:60]}...")
    elif new in src:
        print(f"[OK] Already updated: {new[:60]}...")
    else:
        print(f"[WARN] Anchor not found: {old[:60]}...")

# Also handle any single-value calls (without tuple unpack) that might be affected.
# Add sentinel comment.
src = "# v0.5.3.2 three-tuple unpack\n" + src

try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    sys.exit(1)

T.write_text(src, encoding="utf-8")
print(f"[DONE] Patched {applied} test unpack sites.")