Rob's Code Wizard - Phase 7 Overlay (v0.4.7)
=============================================

WHAT THIS PHASE ADDS
--------------------
Bug 4 from pre-v1.0 list: dialect-aware export grammar dispatch.

Grammar rules (locked in v1.0 spec):
    VDT  -> Civil3D    : VDT grammar (B, E, BC, EC, CLS - no asterisks)
    ODOT -> Civil3D    : ODOT alphabetic grammar (BL*, EL*, OC*, CL*)
    ODOT -> OpenRoads  : ODOT numeric (default) or alphabetic
    VDT  -> OpenRoads  : Not supported - translate to ODOT first

WHAT'S NEW
----------
NEW:
  - app/services/grammar_normalizer.py
    to_vdt(token), to_odot_alpha(token), to_odot_numeric(token)
    Normalizes any line-connect token to the target grammar.

REPLACED (backed up to _backup_v0_4_7\):
  - app/services/odot_exporter.py
    NEW exports: export_vdt_to_civil3d, export_odot_to_civil3d,
                 export_odot_to_openroads
    Backward-compat aliases preserved: export_civil3d, export_openroads
    Each exporter is dialect-aware via the source_dialect parameter
    passed to linework_parser. Size tokens and '/' comment tails
    preserved through export.
  - app/ui/export_tab.py
    Detects parent.codeset.name on every tab show and reconfigures:
      VDT mode: Civil3D enabled (VDT grammar), OpenRoads disabled
      ODOT mode: both enabled, Civil3D uses ODOT alpha, OpenRoads uses numeric

NEW TESTS:
  - tests/test_grammar_normalizer.py (17 tests)
  - tests/test_odot_exporter.py (10 tests covering all 3 dispatch paths)

NEVER MODIFIED
--------------
P, N, E, Z are NEVER touched on export. Only the D column is rewritten
(line-connect codes normalized to the target grammar).

NO HEADER ROW
-------------
Output CSVs have NO header row (AutoCAD/Civil3D requirement).
Verified by test_vdt_civil3d_no_header.

RUN ORDER
---------
1. Extract this zip onto the Robs_Code_Wizard project root.
2. apply_phase_7.bat
   - Backs up odot_exporter.py and export_tab.py
   - Copies new + replaced files
   - Runs Phase 7 tests + full suite
3. Restart the app.
4. Verify with code set = VDT:
   - Export tab Civil3D button says "Export to Civil3D (VDT grammar)..."
   - OpenRoads button is disabled with tooltip
   - Export a file with EP B - output has "EP B" (no asterisk added)
5. Verify with code set = ODOT:
   - Export tab Civil3D button says "Export to Civil3D (ODOT alphabetic)..."
   - OpenRoads button enabled
   - Export EP 1 to Civil3D -> "EP BL*"
   - Export EP BL* to OpenRoads -> "EP 1"
6. push_phase_7.bat

ALL FOUR PRE-V1.0 BUGS NOW FIXED
---------------------------------
v0.4.4.1: Bug 1 - PL added to ODOT catalog
v0.4.6:   Bugs 2 + 3 - size-bearing codes + suggestion cleanup
v0.4.7:   Bug 4 - dialect-aware export dispatch

NEXT: v1.0
----------
Final polish, installer, release notes, v1.0 tag.
