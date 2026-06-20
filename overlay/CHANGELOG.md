## v0.4.1 - 2026-06-20 - Phase 1: Translation Map Skeleton

### Added
- `app/data/translation_map.json` - canonical VDT<->ODOT translation map (versioned asset)
- `app/services/translation_map.py` - loader, validator, lookup helpers
- `app/services/seed_translation_map.py` - auto-seeder using rapidfuzz description similarity + type matching
- `reseed_translation_map.bat` - forced regeneration with backup + confirm prompt
- `tests/test_translation_map.py` - schema validation and roundtrip tests

### Changed
- `app/catalogs/vdt_codes.py`, `app/catalogs/odot_codes.py` - added `load_all()` helpers
- `requirements.txt` - added `rapidfuzz>=3.0`

### Notes
- No UI yet - translation tab lands in v0.4.2 (Phase 2)
- Seeder is generate-if-missing; use `reseed_translation_map.bat` for forced regen
