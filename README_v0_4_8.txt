Rob's Code Wizard - v0.4.8 small-fixes (Option A)

WHAT THIS FIXES
---------------
1. Title bar showed "Rob's Code Wizard - v0.4.7\n (VDT)" with literal \n.
   Root cause: previous build scripts wrote version.txt with literal
   backslash-n text instead of a real newline character.

   Fix: app/__init__.py defensively strips literal "\n", "\r", "\r\n"
   in addition to whitespace. Version.txt rewritten clean.

2. After Help > Check for Updates installed the new version, the app
   would not relaunch.

   Root cause: build/installer.iss [Run] entry uses "skipifsilent" flag.
   Since the updater calls the installer with /VERYSILENT, Inno Setup
   correctly skipped the relaunch step.

   Fix: ADD a second [Run] entry that fires ONLY during silent installs:
     Check: WizardSilent
     (no postinstall flag, no skipifsilent flag)

   The original interactive entry is preserved, so fresh installs still
   show the "Launch Rob's Code Wizard" checkbox at the end of the wizard.

3. About dialog logo was 140px tall. Bumped to 220px.

WHAT'S NEW / CHANGED
--------------------
REPLACED:
  - app/__init__.py
    Defensive version loader.
  - resources/version.txt
    Clean "0.4.8" + single real newline.

PATCHED IN-PLACE (idempotent, backups in _backup_v0_4_8\):
  - build/installer.iss
    NEW [Run] entry added for silent-install relaunch.
    Original entry untouched.
  - app/ui/main_window.py
    About dialog logo scaledToHeight(140) -> scaledToHeight(220)

NEW TESTS:
  - tests/test_version_loader.py (3 tests)

RUN ORDER
---------
1. Extract this zip onto the Robs_Code_Wizard project root.
2. apply_v0_4_8.bat
3. Restart the app. Verify:
   - Title bar: "Rob's Code Wizard - v0.4.8 (VDT)"
   - Help > About: bigger logo
4. push_v0_4_8.bat
5. Wait for GitHub Actions to build a fresh installer with the new
   installer.iss. Once that release is published, the next call to
   Help > Check for Updates will use the patched installer and
   relaunch the app correctly.

NOTES
-----
The installer.iss patch ONLY affects future installers built from this
tagged release. The currently-installed v0.4.7 EXE still has the old
behavior (no relaunch). The cycle that fixes this is:

   1. Apply this patch.
   2. Push tag v0.4.8.
   3. GitHub Actions builds Robs_Code_Wizard_Setup.exe with the
      patched installer.iss.
   4. Help > Check for Updates downloads that installer.
   5. That installer runs /VERYSILENT, hits the new [Run] entry,
      and relaunches.
