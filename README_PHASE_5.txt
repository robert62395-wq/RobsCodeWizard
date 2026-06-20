Rob's Code Wizard - Phase 5 Overlay (v0.4.5)
=============================================

PHASE 5 ADDS
------------
1. ODOT Exporter (app/services/odot_exporter.py)
   - export_civil3d(rows, path) - PNEZD CSV, no header, auto-converts
     numeric line-connect codes (1/2/3/4) to alphabetic (BL*/EL*/OC*/CL*)
   - export_openroads(rows, path, use_numeric=True) - PNEZD CSV, no header,
     converts alphabetic to numeric for OpenRoads field crews

2. Reverse Line-Connect Conversion (alphabetic -> numeric)
   - BL/BL* -> 1, EL/EL* -> 2, OC/OC* -> 3, CL/CL* -> 4
   - BC/EC preserved as-is (no numeric equivalents)
   - Tools > Convert Line Connect Codes... now offers BOTH directions

3. Export Tab (app/ui/export_tab.py)
   - New tab AFTER "Modified Data" in the main tab bar
   - "Export to Civil3D..." button
   - "Export to OpenRoads..." button with use_numeric toggle
   - Auto-suggests filename as <source_name>_ODOT_Civil3D.csv etc.

NEVER MODIFIED
--------------
N, E, Z, and Point numbers are NEVER touched on export. Only the D column
is rewritten (line-connect codes converted to match target format).

RUN ORDER
---------
1. Extract this zip onto the Robs_Code_Wizard project root.
2. apply_phase_5.bat
   - Backs up affected files
   - Copies overlay
   - Auto-patches main_window.py to add Export tab
   - Runs Phase 5 tests + full suite
3. Launch app. Verify:
   - "Export" tab appears after "Modified Data"
   - Tools > Convert Line Connect Codes... has both radio buttons enabled
4. push_phase_5.bat
