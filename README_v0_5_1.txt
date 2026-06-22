Rob's Code Wizard - v0.5.1 (Translation Tab Rebuild)
Phase 1 of 7 toward v1.0

WHAT CHANGED
------------
Major Translation tab UX rebuild based on direct user feedback.

REMOVED FRICTION:
  - Source dropdown is now an auto-detected read-only label
    (uses parent.codeset.name - same code set you picked on Raw Data)
  - Target dropdown defaults to opposite of source
  - "Apply Translation to Loaded Rows" button renamed to just
    "Translate Loaded Rows" - one click, no friction

NEW FEATURES:
  - Two-section table:
      USED IN LOADED FILE (sorted by frequency) - top section
      OTHER CATALOG CODES (alphabetical) - bottom section
  - Usage indicator column: * marks codes present in your file
  - Count column shows how many times each code appears
  - Dirty indicator (bullet) marks entries with unsaved overrides
  - Why column with human-readable match-basis explanation
    e.g. "Best guess: description similarity (85%), type matched"

WIDE BOTTOM REVIEW PANE:
  - Side-by-side VDT and ODOT editors (no more cramped right pane)
  - Full-width Notes textbox
  - Match-basis explanation banner above notes
  - Both VDT and ODOT side fields are editable (manual catalog edits)

COMBINED FILTERS:
  - Single search box (code, description, or type:linework)
  - Confidence checkboxes: In use, Exact, Best-guess, Unmatched, Manual

BULK ACTIONS:
  - Accept all Best-Guess in view - mass-promote visible best-guesses
    to manual overrides
  - Renamed "Reseed Map..." to "Reseed from Catalog..." with clearer
    confirmation dialog
  - Save Overrides is now visually prominent (bold)

EMPTY-STATE INTELLIGENCE:
  - When no row is selected, the review pane shows used-in-file stats:
      "47 unique codes in your data:
         35 exact matches
         8 best-guess matches (review recommended)
         4 unmatched or missing from catalog"

FILES
-----
NEW:
  app/services/usage_analyzer.py
  app/services/match_basis_descriptor.py
  tests/test_usage_analyzer.py (10 tests)
  tests/test_match_basis_descriptor.py (8 tests)

REPLACED (backed up to _backup_v0_5_1\):
  app/ui/translation_tab.py
  app/ui/translation_review_pane.py

RUN ORDER
---------
1. Extract this zip onto the Robs_Code_Wizard project root.
2. apply_v0_5_1.bat
3. Restart app and explore the new Translation tab
4. push_v0_5_1.bat

NEXT
----
v0.5.2 - Status bar + tooltips everywhere
v0.5.3 - Error handling and resilience
v0.5.4 - Performance (async re-validation, async translation)
v0.5.5 - First-launch experience + onboarding
v0.5.6 - Final cleanup + consolidation
v0.5.7 - "DO NOT TOUCH" replaced with Code Reference dialog
v1.0   - Release prep
