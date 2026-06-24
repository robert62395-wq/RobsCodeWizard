"""Make a v0.5.2.3 release zip from the current project state."""
import zipfile
from pathlib import Path

OUT = Path("Robs_Code_Wizard_v0_5_2_3_0_1.zip")
ROOT = Path(".")

# Files we want to include in the zip
files = [
    "app/ui/main_window.py",
    "app/ui/translation_tab.py",
    "app/ui/export_tab.py",
    "app/ui/convert_line_connect_dialog.py",
    "app/ui/help_icon.py",
    "app/ui/help_dialogs.py",
    "app/services/status_bar_helper.py",
    "resources/version.txt",
    "CHANGELOG.md",
    "build/installer.iss",
]

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        p = ROOT / f
        if p.exists():
            z.write(p, arcname=f)
            print(f"[OK] added {f}")
        else:
            print(f"[SKIP] {f} not found")

print(f"\nBuilt {OUT} ({OUT.stat().st_size:,} bytes)")