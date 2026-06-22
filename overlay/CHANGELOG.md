## v0.4.8 - 2026-06-22 - Small fixes (Option A)

### Fixed
- Title bar showed "v0.4.x\n (VDT)" with literal backslash-n. Root cause
  was previous build scripts embedding version.txt content with literal
  "\\n" instead of a real newline. The version loader's .strip()
  doesn't remove literal escape sequences.
- After "Check for Updates" installed the new version, the app would
  not relaunch. Root cause was build/installer.iss [Run] entry using
  "skipifsilent" - Inno Setup correctly skipped the relaunch step
  because the updater calls the installer with /VERYSILENT.
- About dialog logo was 140px tall. Bumped to 220px.

### Added
- New [Run] entry in build/installer.iss that fires ONLY during silent
  installs (Check: WizardSilent). The original interactive entry is
  untouched, so fresh installs still show the wizard's checkbox.
- `tests/test_version_loader.py` (3 tests covering the \\n bug regression)

### Changed
- `app/__init__.py` - defensive version loader strips literal "\\n",
  "\\r", "\\r\\n" escape sequences in addition to whitespace.
- `resources/version.txt` - rewritten clean (just "0.4.8\n" with real newline).
- `app/ui/main_window.py` - About dialog logo height 140 -> 220.

### Notes
- installer.iss patch only affects installers built FROM this release
  forward. The currently-installed v0.4.7 EXE still has the old behavior.
  Auto-relaunch will work starting with v0.4.9 (or v0.4.8.1) updates.
- Idempotent patchers via sentinel strings ("v0.4.8 silent-install
  relaunch" in installer.iss, "v0.4.8 logo bump" in main_window.py).
