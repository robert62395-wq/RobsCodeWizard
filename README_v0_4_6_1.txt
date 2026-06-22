Rob's Code Wizard - v0.4.6.1 hotfix
====================================

WHAT BROKE
----------
The Phase 6 test `test_validator_pi1_6_not_flagged` failed because:

  rows = [{"D": "PI1 6"}]
  validate_rows(rows, {"PI1"}) -> valid: False  (expected True)

Root cause: `_strip_suffix("PI1")` returns "PI" (strips trailing digit).
Then the validator checks `"PI" in {"PI1"}` -> False, flags as unknown.

The strip-suffix logic was designed for codes like EP1 (where EP is the
catalog code and 1 is a string ID). But PI1 IS the catalog code, so
stripping breaks the match.

THE FIX
-------
Check the FULL token against valid_set first. Only fall back to the
stripped form if the full token misses.

  # OLD: if _strip_suffix(token) in valid_set:
  # NEW: if token in valid_set or _strip_suffix(token) in valid_set:

Same change in suggester.py and the size-bearing "next-token" lookahead.

RUN ORDER
---------
1. Extract this zip onto the Robs_Code_Wizard project root.
2. apply_v0_4_6_1_hotfix.bat
   - Backs up validator.py and suggester.py
   - Copies fixed files
   - Re-runs Phase 6 tests (all 36 should pass)
3. push_v0_4_6_1.bat
