# Rob's Code Wizard v0.3.9.5.1

> 🐕 Meet **Elkie**, your new code wizard mascot — and a whole bag of new tricks.

This release is a top-to-bottom polish pass over v0.3.9.5.0: real branding, an animated splash, a working in-app updater, and a properly threaded code-set switch.

---

## 🎨 New: Elkie branding

- **App / installer / taskbar icon** — multi-resolution `resources/icon.ico` (16, 24, 32, 48, 64, 128, 256 px) generated from the Elkie wizard logo
- **About dialog** redesigned with `resources/logo.png` (140 px tall), version + active codeset info, and a "View on GitHub" button that opens the repo
- Logo bundled into the installer via Inno Setup so `RobsCodeWizard_Setup.exe` carries the icon too

## 🚀 New: Animated splash screen

- Plays `resources/splash.gif` on launch — 480×320, 3.2 s loop, the three cartoon dogs in safety gear with survey equipment
- ✨ Drifting gold sparkles
- 📊 Yellow loading bar that fills left-to-right
- Splash now stays visible for the full 3.2 s loop (or until MainWindow finishes building, whichever is longer)
- Uses PySide6 `QMovie` for real animation; falls back gracefully to a static pixmap if the GIF can't load

## 🔄 New: GitHub Releases auto-update

The in-app updater now queries the GitHub Releases API directly — no more hand-maintained `manifest_url`. Tag a new release and users see the update prompt on next launch.

- Update flow:
  1. `Help → Check for Updates...`
  2. Background `QThread` queries `https://api.github.com/repos/robert62395-wq/RobsCodeWizard/releases/latest`
  3. If newer, shows an "Update Available" dialog
  4. Click **Yes** → installer downloads to `%TEMP%` with a live progress dialog
  5. App closes → installer runs silently with `/VERYSILENT /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /NORESTART`
  6. Installer relaunches the new version
- Gracefully handles `/releases/latest` returning 404 (prereleases, drafts, or empty repo) by falling back to `/releases` list

## 🧵 New: Threaded code-set switch

The ~15 s revalidation that used to freeze the UI now runs on a `QThread`:

- New module: `app/services/revalidation_worker.py`
- Main thread shows a `BusyDialog` and **stays responsive** — you can drag the window during the wait
- Worker emits live status: `Validating codes...` → `Building suggestions...` → done

## 🚨 New: DO NOT TOUCH menu

`Help → DO NOT TOUCH` reserves a slot for a future capability. Currently shows a placeholder warning dialog. A `# TODO: v0.3.9.6+` comment marks the spot.

## 🛠 Fixes

- **`tag_release.bat` parser bug** — the long-running `: was unexpected at this time` crash is gone. All `Y/N` prompts moved into subroutines, simplified prompt strings, and tag-pattern validation added. Now supports one-liner mode: `tag_release.bat v0.3.9.5.1 "message"`
- **Updater 404 fallback** — when `/releases/latest` returns 404, automatically falls back to `/releases` list and picks the first non-draft entry
- **Stale `test_updater.py`** replaced with a new 8-test suite matching the GitHub Releases API
- **`settings.py` migration** — silently drops the deprecated `manifest_url` key when loading older settings files

## 🐕 Under the hood

- `app/services/updater.py` rewritten from scratch: `ReleaseAsset`, `UpdateInfo`, `parse_version`, `is_newer`, `fetch_latest_release`, `fetch_releases_list`, `download_asset`, `launch_installer_and_quit`
- `app/ui/update_thread.py` adds `UpdateDownloadThread` with `progress`/`finished_with_path`/`error` signals
- `app/ui/splash.py` rewritten for `QMovie` + `_MEIPASS`-aware resource lookup + `wait_for_splash()` helper
- `app/main.py` calls `QApplication.setWindowIcon()` from `resources/icon.ico`
- `app/ui/main_window.py` patched in 6 surgical spots across phases — Phase 3 (About), Phase 5 (updater + 4 new helper methods), Phase 6 (DO NOT TOUCH + revalidation worker + 2 new helpers)
- `build/installer.iss` bundles `icon.ico` into `{app}`, adds `CloseApplications=yes` + `RestartApplications=yes` to support the auto-upgrade flow
- `run.bat` and `.github/workflows/release.yml` both prefer `resources/icon.ico` for the EXE/installer icon

## 📥 Install

- **Recommended:** Download `RobsCodeWizard_Setup.exe` from this release page, run it, accept defaults.
- **Portable:** Download `RobsCodeWizard.exe` and run from any folder.
- **From an installed v0.3.9.5.0:** The in-app updater will surface this release automatically on next launch — click `Yes` and it'll handle the upgrade automatically.

---

🐕 Many thanks to **Elkie**, **the wolfie**, and **the blue heeler** for being adorable test subjects.
