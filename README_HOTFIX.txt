Rob's Code Wizard - v0.4.2.1 Hotfix
====================================
Integrate Phase 2 (Translation tab + Convert Line Connect Codes)
into your real app\ui\main_window.py.

WHAT THIS HOTFIX DOES
---------------------
Replaces app\ui\main_window.py with an edited version that adds:

1. Translation tab inserted at index 1 (between "Raw Data" and "Modified Data")
2. Tools > Convert Line Connect Codes... action added to the existing Tools menu
   (after the Undo Last Offset separator)
3. New handler method _on_convert_line_connect that:
   - Builds dialog rows from self.rows {"point": P, "description": D}
   - Opens ConvertLineConnectDialog
   - On Apply, writes converted descriptions back to self.rows[i]["D"]
   - Re-runs validate_rows + build_suggestions
   - Refreshes Raw Data and Modified Data tabs
   - Logs the change count and shows a confirmation dialog
4. _convert_lc_action enabled at the same points as the other Tools actions
   (on_open_file and _maybe_restore_session)

PRESERVED
---------
Every existing feature is intact:
  - Code set selector + revalidation worker
  - Linework Fix overlay
  - Export Validation Report
  - Point Offset / Elevation Offset / Undo Last Offset
  - Recovery / restore session
  - Update check + auto-install flow
  - About dialog, log viewer, Report a Problem
  - "DO NOT TOUCH" placeholder

RUN ORDER
---------
1. Extract this zip into the Robs_Code_Wizard project root.

2. apply_main_window_patch.bat
   - Backs up current app\ui\main_window.py to _backup_v0_4_2_main_window\
   - Copies overlay\app\ui\main_window.py over it
   - Runs the full pytest suite as a smoke check

3. Launch the app and confirm:
   - "Translation" tab appears between Raw Data and Modified Data
   - Tools menu shows "Convert Line Connect Codes..." (greyed out until you Open a file)
   - Open the 241867 topo CSV - the action enables
   - Click it -> dialog shows previews of EP 1 -> EP BL*, DR 2 EP1 -> DR EL* EP1, etc.

4. push_hotfix.bat
   - Commits, tags v0.4.2.1, pushes main + tag
   - GitHub Actions rebuilds EXE + Installer

PATH CORRECTION
---------------
The Phase 2 README referred to "app\main_window.py" - the actual path is
"app\ui\main_window.py" (which main.py imports as `from app.ui.main_window
import MainWindow`). This hotfix targets the correct path.
