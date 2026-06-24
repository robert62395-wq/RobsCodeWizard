"""v0.5.3.1 patcher: row-level error reporting in odot_exporter.py."""
import ast
import sys
from pathlib import Path

E = Path("app/services/odot_exporter.py")
if not E.exists():
    print(f"[ERROR] {E} not found.")
    sys.exit(1)

src = E.read_text(encoding="utf-8")
SENTINEL = "v0.5.3.1 export error tracking"
if SENTINEL in src:
    print(f"[OK] {E} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_3_1") / E.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {E}")

# Wrap each writer.writerow call with a try/except.
# All three exporters have the same pattern: for row in rows: ... writer.writerow(...)
# We replace the loop body to catch per-row errors.

OLD_CIVIL_VDT = """    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            new_desc, c = _convert_description(row.get("D", ""), "vdt", to_vdt)
            conversions += c
            writer.writerow(_row_to_pnezd(row, new_desc))
            written += 1
    return written, conversions"""

NEW_CIVIL_VDT = """    errors = []
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for i, row in enumerate(rows, start=1):
            try:
                new_desc, c = _convert_description(row.get("D", ""), "vdt", to_vdt)
                conversions += c
                writer.writerow(_row_to_pnezd(row, new_desc))
                written += 1
            except Exception as exc:
                errors.append({"row_index": i, "point": row.get("P", "?"), "error": str(exc)})
    return written, conversions, errors  # v0.5.3.1 export error tracking"""

OLD_CIVIL_ODOT = """    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            new_desc, c = _convert_description(row.get("D", ""), "odot", to_odot_alpha)
            conversions += c
            writer.writerow(_row_to_pnezd(row, new_desc))
            written += 1
    return written, conversions"""

NEW_CIVIL_ODOT = """    errors = []
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for i, row in enumerate(rows, start=1):
            try:
                new_desc, c = _convert_description(row.get("D", ""), "odot", to_odot_alpha)
                conversions += c
                writer.writerow(_row_to_pnezd(row, new_desc))
                written += 1
            except Exception as exc:
                errors.append({"row_index": i, "point": row.get("P", "?"), "error": str(exc)})
    return written, conversions, errors"""

OLD_OPENROADS = """    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            new_desc, c = _convert_description(row.get("D", ""), "odot", target_fn)
            conversions += c
            writer.writerow(_row_to_pnezd(row, new_desc))
            written += 1
    return written, conversions"""

NEW_OPENROADS = """    errors = []
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for i, row in enumerate(rows, start=1):
            try:
                new_desc, c = _convert_description(row.get("D", ""), "odot", target_fn)
                conversions += c
                writer.writerow(_row_to_pnezd(row, new_desc))
                written += 1
            except Exception as exc:
                errors.append({"row_index": i, "point": row.get("P", "?"), "error": str(exc)})
    return written, conversions, errors"""

replacements = 0
for old, new in [(OLD_CIVIL_VDT, NEW_CIVIL_VDT), (OLD_CIVIL_ODOT, NEW_CIVIL_ODOT), (OLD_OPENROADS, NEW_OPENROADS)]:
    if old in src:
        src = src.replace(old, new, 1)
        replacements += 1

# Backward-compat aliases still return (written, conversions) without errors.
# Update them to unpack the new 3-tuple.
OLD_ALIAS_C3D = "def export_civil3d(rows, out_path):\n    return export_odot_to_civil3d(rows, out_path)"
NEW_ALIAS_C3D = """def export_civil3d(rows, out_path):
    written, conversions, _errors = export_odot_to_civil3d(rows, out_path)
    return written, conversions"""

OLD_ALIAS_OR = "def export_openroads(rows, out_path, use_numeric=True):\n    return export_odot_to_openroads(rows, out_path, use_numeric=use_numeric)"
NEW_ALIAS_OR = """def export_openroads(rows, out_path, use_numeric=True):
    written, conversions, _errors = export_odot_to_openroads(rows, out_path, use_numeric=use_numeric)
    return written, conversions"""

if OLD_ALIAS_C3D in src:
    src = src.replace(OLD_ALIAS_C3D, NEW_ALIAS_C3D, 1)
if OLD_ALIAS_OR in src:
    src = src.replace(OLD_ALIAS_OR, NEW_ALIAS_OR, 1)

try:
    ast.parse(src)
except SyntaxError as e:
    print(f"[ERROR] Patched odot_exporter.py has syntax error: {e}")
    sys.exit(1)

E.write_text(src, encoding="utf-8")
print(f"[DONE] {E} patched ({replacements}/3 export functions now return errors list).")
print(f"       New signature: (written, conversions, errors)")
print(f"       Legacy aliases (export_civil3d, export_openroads) unchanged.")