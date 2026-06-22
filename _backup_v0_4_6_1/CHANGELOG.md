## v0.4.6 - 2026-06-22 - Phase 6: Size-bearing codes + Suggestion cleanup

### Added
- `app/services/size_bearing.py` - is_size_bearing() helper
- `tests/test_size_bearing.py` (16 tests)
- `tests/test_validator.py` (7 tests)
- `tests/test_suggester.py` (4 tests)

### Changed
- `app/services/linework_parser.py` - parse() absorbs next token after
  size-bearing code into entry["size"]. Entry shape gains "size" field.
- `app/services/validator.py` - direct replacement. Size-bearing tokens
  no longer flagged. Anything after "/" treated as comment.
- `app/services/suggester.py` - direct replacement. Orphan tokens move
  behind " / " delimiter. Existing tails preserved.
- `app/services/description_translator.py` - emits size token after
  translated code so VDT <-> ODOT round-trips preserve sizes.

### Fixes
- Bug 2 (pre-v1.0): VTD 12, PI1 6, GRBR 24, etc. no longer flagged.
- Bug 3 (pre-v1.0): Non-code tokens appear in Suggestion column behind "/".
