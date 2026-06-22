Rob's Code Wizard - Phase 6 Overlay (v0.4.6)
=============================================

WHAT THIS PHASE FIXES
---------------------
Bug 2 from pre-v1.0 list: VDT codes with size suffixes (VTD 12, PI1 6,
GRBR 24, etc.) were being flagged as invalid. Fixed.

Bug 3 from pre-v1.0 list: Anything in the D column that is NOT a recognized
code now moves to the end of the description behind a "/" delimiter.
This appears in the Suggestion column on the Modified Data tab.
(Civil3D treats anything after "/" as a comment - per VDT linework grammar.)

WHAT'S NEW / CHANGED
--------------------
NEW:
  - app/services/size_bearing.py
    is_size_bearing(code) -> bool
    Recognizes: GRBR, VTD, VTE, VTS, VBU, and ALL codes starting with PI.

UPDATED (direct replacement - your existing files are backed up):
  - app/services/linework_parser.py
    parse() now absorbs the token following a size-bearing code into
    entry["size"]. Entry dict gains a "size" field.
  - app/services/validator.py
    - Tokens following a size-bearing code are no longer flagged.
    - Anything after "/" is treated as a comment, not validated.
  - app/services/suggester.py
    - Fuzzy match still runs first for unknown tokens.
    - Tokens with no match move behind " / " in the suggestion.
    - Existing "/" tail in the D column is preserved.
  - app/services/description_translator.py
    - Now emits the size token after the translated code, so "VTD 12"
      round-trips correctly through VDT <-> ODOT translation.

NEW TESTS:
  - tests/test_size_bearing.py (16 tests)
  - tests/test_linework_parser.py (replaces old version, 10 tests)
  - tests/test_validator.py (7 tests)
  - tests/test_suggester.py (4 tests)

RUN ORDER
---------
1. Extract this zip onto the Robs_Code_Wizard project root.
2. apply_phase_6.bat
   - Backs up linework_parser.py, validator.py, suggester.py,
     description_translator.py to _backup_v0_4_6\
   - Copies new and updated files into source tree
   - Runs Phase 6 tests + full suite
3. Restart the app. Test with:
   - Open a CSV with "VTD 12" - should NOT flag invalid
   - Open a CSV with "PI1 6" - should NOT flag invalid
   - Open a CSV with "EP foobar" - Suggestion column shows "EP / FOOBAR"
4. push_phase_6.bat

NEXT
----
v0.4.7 will tackle Bug 4: dialect-aware export grammar dispatch.
  - VDT -> Civil3D: VDT grammar only (B, E, BC, EC, CLS - no asterisks)
  - ODOT -> Civil3D: alphabetic ODOT grammar (BL*, EL*, OC*, CL*)
  - ODOT -> OpenRoads: either ODOT grammar (numeric or alphabetic)
