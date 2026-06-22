## v0.5.1 - 2026-06-22 - Phase 1 of 7: Translation Tab UX Rebuild

### Removed Friction
- Source dropdown replaced with auto-detected read-only label.
- Target dropdown defaults to opposite of source.
- Apply Translation button simplified to "Translate Loaded Rows".

### Added
- `app/services/usage_analyzer.py` - analyze_used_codes() counts how many
  times each point code appears in parent.rows. build_usage_summary()
  cross-references against the translation map.
- `app/services/match_basis_descriptor.py` - describe() and short_label()
  produce human-readable match-basis explanations.
- Two-section table on Translation tab: USED IN LOADED FILE (sorted by
  frequency) + OTHER CATALOG CODES (alphabetical).
- Dirty indicator (bullet) for entries with unsaved overrides.
- Why column with match-basis explanation per entry.
- Used indicator column + Count column.
- Bulk "Accept all Best-Guess in view" action.
- Empty-state summary in review pane (Option C - used-in-file stats).
- Manual edits to ANY entry are supported (not just ODOT side).
- `tests/test_usage_analyzer.py` (10 tests)
- `tests/test_match_basis_descriptor.py` (8 tests)

### Changed
- `app/ui/translation_tab.py` - full rebuild.
- `app/ui/translation_review_pane.py` - wide bottom-mounted layout
  with side-by-side VDT/ODOT editors and full-width notes.

### Notes
- showEvent triggers refresh of source label, used counts, target default,
  and table repopulation. No live signal connection to Modified Data tab.
- map_modified signal still fires after Save Overrides or Accept-all-best
  for external listeners.
