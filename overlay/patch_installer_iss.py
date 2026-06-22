"""v0.4.8 Option A: patch build/installer.iss to relaunch after silent install.

Adds a second [Run] entry that fires only during silent installs (the updater
flow). The original interactive postinstall entry is preserved untouched, so
fresh installs still show the wizard's checkbox.
"""
import sys
from pathlib import Path

ISS = Path("build/installer.iss")
if not ISS.exists():
    print(f"[ERROR] {ISS} not found.")
    sys.exit(1)

src = ISS.read_text(encoding="utf-8")
SENTINEL = "v0.4.8 silent-install relaunch"
if SENTINEL in src:
    print(f"[OK] {ISS} already patched. Skipping.")
    sys.exit(0)

backup = Path("_backup_v0_4_8") / "installer.iss"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[1/2] Backed up {ISS} -> {backup}")

OLD = 'Filename: "{app}\\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent'
NEW = (
    'Filename: "{app}\\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent\n'
    '; v0.4.8 silent-install relaunch (auto-relaunch after updater installs)\n'
    'Filename: "{app}\\{#MyAppExeName}"; Flags: nowait runasoriginaluser; Check: WizardSilent'
)

if OLD not in src:
    print(f"[ERROR] Could not find expected [Run] entry.")
    print(f"        Inspect {ISS} manually - may have been edited.")
    sys.exit(1)

src = src.replace(OLD, NEW)
ISS.write_text(src, encoding="utf-8")
print(f"[2/2] Patched {ISS} - added silent-install relaunch entry.")
