# Rob's Code Wizard v0.3.9.5.2

> Stabilization + survey-merging utilities.

## 🛠 New tools

### Tools → Apply Point Offset...
Add (or subtract) an integer from every Point number across the loaded file.

- Detects collisions **before** applying — warns if any rows would overlap with each other or with existing P values from different rows (Interpretation C: catches both kinds)
- Default value of 1000 (common for joining surveys)
- Result is sorted by P automatically

### Tools → Apply Elevation Offset...
Add (or subtract) a decimal value from every Elevation (Z).

- Skip-zero by default — zero-elev rows (yellow-flagged "missing data") are NEVER offset, since adding to a missing value doesn't fix it
- 4-decimal precision (e.g., `-0.4972` ft for Ohio NAVD88 → IGLD85 shift)
- **N and E are NEVER modified** by any offset operation (project invariant)

### Tools → Undo Last Offset (...)
Stack-based undo. Each offset push deep-copies the rows; undo pops back. Label shows what's about to be undone (e.g. "Undo Last Offset (P +1000)"). Stack resets when a new file is opened.

## 🩹 Stabilization

- **Phase A.1 diagnostic instrumentation** — 11 `[diag]` timing log lines around every step of the code-set switch flow (validate_rows, build_suggestions, _populate_table, modified_tab.refresh_from_parent). Catches future regressions and lets us pinpoint freezes when they happen.
- **pytest.ini at project root** — scopes test discovery to `tests/` only, skipping `_payload/`, `backup_*/`, `build/`, `dist/`, `.venv/`, etc. No more accidental double-collection from staging folders.

## 📐 Under the hood

- New module: `app/services/offsets.py` — pure functions, no UI dependencies, fully unit-testable
- 11 new tests in `tests/test_offsets.py` covering all three apply scenarios + collision detection (duplicate-in-new, old-new overlap, self-equal edge case)
- `app/ui/main_window.py` surgically patched in 3 spots (Tools menu, file-open enable, handler methods)

## 📥 Install

- **Recommended:** Download `RobsCodeWizard_Setup.exe`, run it, accept defaults.
- **Portable:** Download `RobsCodeWizard.exe` and run from any folder.
- **From v0.3.9.5.1:** The in-app updater will surface this release on next launch (**Help → Check for Updates**).

---

🐕 Many thanks to **Elkie**, **the wolfie**, and **the blue heeler**.
