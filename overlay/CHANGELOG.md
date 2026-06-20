## v0.4.3 - 2026-06-20 - Phase 3: VDT<->ODOT Grammar Translator + Apply Translation

### Added
- `app/services/grammar_translator.py` - bidirectional linework command translator
- `app/services/code_translator.py` - point code translator via translation_map.json
- `app/services/description_translator.py` - end-to-end translator
- `tests/test_grammar_translator.py` (18 tests)
- `tests/test_code_translator.py` (8 tests)
- `tests/test_description_translator.py` (9 tests)

### Changed
- `app/ui/translation_tab.py` - added "Translate Loaded Rows" bar with Source/Target dropdowns and Apply button. All Phase 2 features preserved.

### Notes
- No main_window.py changes needed.
- N, E, Z, and Point numbers are NEVER touched. Only D column rewritten.
