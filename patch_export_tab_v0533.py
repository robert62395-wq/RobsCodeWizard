"""v0.5.3.3: fix export_tab.py to unpack 3-tuple returns + show per-row errors."""
import ast
import sys
from pathlib import Path

E = Path("app/ui/export_tab.py")
if not E.exists():
    print(f"[ERROR] {E} not found.")
    sys.exit(1)

src = E.read_text(encoding="utf-8")
SENTINEL = "v0.5.3.3 export errors"
if SENTINEL in src:
    print(f"[OK] {E} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_3_3") / E.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {E}")

# v0.5.3.1 changed export_vdt_to_civil3d, export_odot_to_civil3d, and
# export_odot_to_openroads to return 3-tuples. Update both call sites.

OLD_CIVIL = "written, conversions = exporter(rows, Path(path))"
NEW_CIVIL = "written, conversions, errors = exporter(rows, Path(path))  # v0.5.3.3 export errors"

OLD_OR = """written, conversions = export_odot_to_openroads(
                rows, Path(path), use_numeric=self.or_use_numeric.isChecked()
            )"""
NEW_OR = """written, conversions, errors = export_odot_to_openroads(
                rows, Path(path), use_numeric=self.or_use_numeric.isChecked()
            )  # v0.5.3.3 export errors"""

if OLD_CIVIL in src:
    src = src.replace(OLD_CIVIL, NEW_CIVIL, 1)
    print("[OK] Civil3D export unpacks 3-tuple")
else:
    print(f"[WARN] Civil3D anchor not found")

if OLD_OR in src:
    src = src.replace(OLD_OR, NEW_OR, 1)
    print("[OK] OpenRoads export unpacks 3-tuple")
else:
    # Try a flattened version (in case original was on one line)
    OLD_OR_FLAT = "written, conversions = export_odot_to_openroads("
    NEW_OR_FLAT = "written, conversions, errors = export_odot_to_openroads("
    if OLD_OR_FLAT in src:
        src = src.replace(OLD_OR_FLAT, NEW_OR_FLAT, 1)
        print("[OK] OpenRoads export unpacks 3-tuple (flat match)")
    else:
        print(f"[WARN] OpenRoads anchor not found")

# Wrap each success popup with an error summary if errors is non-empty.
# The Civil3D popup ends with `Line-connect conversions: {conversions}"`
# The OpenRoads popup ends similarly.
# Insert: if errors: QMessageBox.warning(self, "Export warnings", "...")

OLD_CIVIL_POPUP = '''QMessageBox.information(
            self, "Civil3D Export Complete",
            f"Wrote {written} rows to:\\n{path}\\n\\n"
            f"Grammar: {grammar_label}\\n"
            f"Line-connect conversions: {conversions}"
        )'''
NEW_CIVIL_POPUP = '''QMessageBox.information(
            self, "Civil3D Export Complete",
            f"Wrote {written} rows to:\\n{path}\\n\\n"
            f"Grammar: {grammar_label}\\n"
            f"Line-connect conversions: {conversions}"
        )
        if errors:  # v0.5.3.3 export errors
            preview = "\\n".join(
                f"  Row {e['row_index']} (Point {e['point']}): {e['error']}"
                for e in errors[:10]
            )
            more = f"\\n  ... and {len(errors) - 10} more" if len(errors) > 10 else ""
            QMessageBox.warning(
                self, "Export warnings",
                f"{len(errors)} row(s) had errors and were skipped:\\n\\n{preview}{more}"
            )'''

OLD_OR_POPUP = '''QMessageBox.information(
            self, "OpenRoads Export Complete",
            f"Wrote {written} rows to:\\n{path}\\n\\n"
            f"Grammar: ODOT {grammar}\\n"
            f"Line-connect conversions: {conversions}"
        )'''
NEW_OR_POPUP = '''QMessageBox.information(
            self, "OpenRoads Export Complete",
            f"Wrote {written} rows to:\\n{path}\\n\\n"
            f"Grammar: ODOT {grammar}\\n"
            f"Line-connect conversions: {conversions}"
        )
        if errors:  # v0.5.3.3 export errors
            preview = "\\n".join(
                f"  Row {e['row_index']} (Point {e['point']}): {e['error']}"
                for e in errors[:10]
            )
            more = f"\\n  ... and {len(errors) - 10} more" if len(errors) > 10 else ""
            QMessageBox.warning(
                self, "Export warnings",
                f"{len(errors)} row(s) had errors and were skipped:\\n\\n{preview}{more}"
            )'''

if OLD_CIVIL_POPUP in src:
    src = src.replace(OLD_CIVIL_POPUP, NEW_CIVIL_POPUP, 1)
    print("[OK] Civil3D popup shows errors")
else:
    print("[WARN] Civil3D popup anchor not found - errors will be invisible")

if OLD_OR_POPUP in src:
    src = src.replace(OLD_OR_POPUP, NEW_OR_POPUP, 1)
    print("[OK] OpenRoads popup shows errors")
else:
    print("[WARN] OpenRoads popup anchor not found - errors will be invisible")

try:
    ast.parse(src)
except SyntaxError as ex:
    print(f"[ERROR] Syntax error after patch: {ex}")
    print(f"        File NOT saved.")
    sys.exit(1)

E.write_text(src, encoding="utf-8")
print(f"[DONE] {E} patched.")