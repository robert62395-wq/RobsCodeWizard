Rob's Code Wizard - Phase 1 Overlay (v0.4.1)
=============================================

Run order (from the Robs_Code_Wizard project root):

  1. Unzip Robs_Code_Wizard_v0_4_1_0_1.zip into the project root
     (so apply_phase_1.bat and the overlay\ folder sit alongside app\, tests\, etc.)

  2. apply_phase_1.bat
     - Backs up affected files to _backup_v0_4_1\
     - Copies overlay files into place
     - Installs rapidfuzz into your .venv
     - Seeds app\data\translation_map.json (generate-if-missing)
     - Runs pytest on tests\test_translation_map.py

  3. (Optional) Inspect app\data\translation_map.json
     Review the auto-seeded VDT<->ODOT entries.
     Confidence buckets: exact / best-guess / unmatched.

  4. (Optional) reseed_translation_map.bat
     Forced regen. Discards manual overrides after a typed YES confirmation.
     Backs up the existing JSON to _backup_reseed\ first.

  5. push_phase_1.bat
     git add -A, commit, tag v0.4.1, push main + tag.
     GitHub Actions then builds EXE + Installer for the v0.4.1 release.

Next phase: v0.4.2 - Translation Tab UI + review pane.
