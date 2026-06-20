# Changelog

## 0.3.9.3 - Phase 3 of v0.4.0 rollout: ODOT variable-attribute CSV parser
- New `app/services/odot_parser.py` understands the ODOT CSV format with
  variable-width per-point attribute key/value pairs.
- New `app/services/file_parser.py` dispatcher picks the parser based on
  `codeset.parser_kind` (`pnezd` for VDT, `odot` for ODOT).
- Main window switches parsers automatically when the catalog changes.
- Linework commands (BL*/EL*/CL*/OC*) consume no attributes.
- Trailing attribute pairs preserved separately on each row.
- CSV-aware: quoted values with embedded commas and doubled quotes parse correctly.
- New tests for the ODOT parser including real-world snippets from the sample file.

## 0.3.9.2 - Phase 2: Code-set dropdown UI + run.bat
## 0.3.9.1 - Phase 1: Multi-catalog architecture refactor
## 0.3.9.0 - Phase 0: Canonical ODOT code catalog
