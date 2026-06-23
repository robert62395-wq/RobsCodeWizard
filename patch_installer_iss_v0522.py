"""v0.5.2.2 hotfix: fix the v0.4.8 silent-install relaunch race condition.

Bug: the v0.4.8 [Run] entry runs RobsCodeWizard.exe during install (before
files are extracted), causing 'Failed to load Python DLL python312.dll'.
Fix: add the 'postinstall' flag so Inno Setup waits until install completes.
"""
import sys
from pathlib import Path

ISS = Path("build/installer.iss")
if not ISS.exists():
    print(f"[ERROR] {ISS} not found.")
    sys.exit(1)

src = ISS.read_text(encoding="utf-8")
SENTINEL = "v0.5.2.2 installer relaunch race fix"
if SENTINEL in src:
    print(f"[OK] {ISS} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_2_2") / "installer.iss"
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[1/2] Backed up {ISS} -> {backup}")

OLD = 'Filename: "{app}\\{#MyAppExeName}"; Flags: nowait runasoriginaluser; Check: WizardSilent'
NEW = (
    '; v0.5.2.2 installer relaunch race fix - postinstall flag required\n'
    'Filename: "{app}\\{#MyAppExeName}"; Flags: nowait postinstall runasoriginaluser; Check: WizardSilent'
)

if OLD not in src:
    print(f"[ERROR] Could not find expected [Run] entry.")
    print(f"        Search for: Filename: ...; Check: WizardSilent")
    print(f"        Inspect {ISS} manually.")
    sys.exit(1)

src = src.replace(OLD, NEW)
ISS.write_text(src, encoding="utf-8")
print(f"[2/2] Patched {ISS} - added postinstall flag to silent-install [Run] entry.")
print("")
print("NEXT: Commit and push as v0.5.2.2.")
print("The next installer built by GitHub Actions will fix the race condition.")
print("")
print("CAVEAT: This release's installer still has the bug.")
print("Currently-installed v0.5.2.1 users need to wait for v0.5.2.3 or later")
print("before the auto-updater will work without the workaround.")