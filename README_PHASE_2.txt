Rob's Code Wizard - Phase 2 Overlay (v0.4.2)
=============================================

WHAT'S IN THIS PHASE
--------------------
1. Translation Tab UI
   - New tab inserted BETWEEN "Raw Data" and "Linework Fix" tabs
   - Three-column layout: VDT side | Confidence/Override | ODOT side
   - Filters: confidence, type (Symbol/Linework/Point), code search
   - Color-coded rows: green=exact, yellow=best-guess, red=unmatched, blue=manual
   - Right-side review pane: ODOT code override dropdown, notes editor
   - Toolbar: Reseed Map, Export Review CSV, Save Overrides

2. Convert Line Connect Codes (Numeric -> Alphabetic)
   - New menu item: Tools -> Convert Line Connect Codes...
   - Translates OpenRoads numeric line connects to Civil3D alphabetic:
       1 -> BL*   (Begin Line)
       2 -> EL*   (End Line)
       3 -> OC*   (Open Curve)
       4 -> CL*   (Close Shape)
   - Reverse direction (alphabetic -> numeric) is disabled in Phase 2.
     Lands in v0.4.5 alongside OpenRoads export.
   - Numeric-suffixed POINT CODES (EP1, DR1, WALK1) are preserved as codes.
     The parser distinguishes them from numeric line connects by position
     (line connects always FOLLOW a point code with a space separator).

3. Linework parser + grammar library foundation
   - app/services/linework_parser.py classifies tokens as:
       numeric_lc, lettered_lc, vdt_lc, or point_code
   - Real-world test fixtures from the 241867 project files cover:
       EP 1, EP 2, EP 3, DR 2 EP1, LINE_2D 1 EP 1, DR1 3 DR1 2 EP1,
       and other multi-token examples.

RUN ORDER
---------
1. Extract this zip onto the Robs_Code_Wizard project root.

2. apply_phase_2.bat
   - Backs up changed files to _backup_v0_4_2\
   - Copies overlay into source tree
   - Ensures rapidfuzz is installed
   - Runs Phase 2 parser + translator tests
   - Runs full test suite for sanity check

3. MANUAL INTEGRATION STEP (one-time):
   Open app\ui\main_window_patch.py for the three snippets to paste into
   your main_window.py:
     a) Insert TranslationTab at tab index 1 (between Raw Data and Linework Fix)
     b) Add Tools -> Convert Line Connect Codes... menu item
     c) Add the _open_convert_line_connect_dialog handler method

   The reason this isn't automated: your existing main_window.py is the
   authoritative file and an overlay would clobber any local edits.
   Same lesson learned from the v0.4.1.1 hotfix.

4. Verify by launching the app and:
   - Confirming "Translation" tab appears between Raw Data and Linework Fix
   - Opening Tools -> Convert Line Connect Codes...
   - Loading a topo file and previewing the conversion

5. push_phase_2.bat
   - Commits, tags v0.4.2, pushes main + tag
   - GitHub Actions auto-builds EXE + Installer release

WHAT'S NEXT
-----------
Phase 3 (v0.4.3): Full VDT<->ODOT linework grammar translator
   - Resolves VDT B/E vs ODOT BL*/EL* conflict
   - Uses the Phase 2 parser as foundation
   - Wires translation engine into the Translation tab's Apply button
