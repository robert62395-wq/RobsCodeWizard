# Rob's Code Wizard - v0.3.9.3

**Phase 3 of the v0.4.0.0 rollout: ODOT variable-attribute CSV parser**

ODOT survey files carry per-point attributes in a variable-width CSV format
(e.g. `EP BL*,Material,Asphalt`).  This release adds a dedicated parser that
understands that format and assigns the attribute key/value pairs to the right
code based on the catalog's `AttributesSchema` field.

## What's new in 0.3.9.3
- New `app/services/odot_parser.py` - variable-width CSV parser that maps
  attribute pairs to codes according to the active catalog's `AttributesSchema`.
- New `app/services/file_parser.py` - dispatcher that picks the right parser
  based on `codeset.parser_kind` (`pnezd` for VDT, `odot` for ODOT).
- Main window now uses the dispatcher transparently - opening a file in ODOT
  mode runs the new parser; VDT mode keeps the simple PNEZD parser.
- Linework commands (`BL*`, `EL*`, `CL*`, `OC*`) consume **no** attributes; they
  are passed through as command tokens.
- Trailing attribute pairs (beyond what the schemas expect) are preserved in a
  separate `trailing_attrs` dict on the row.
- Quoted values with embedded commas and doubled quotes are handled correctly
  (CSV-aware via the stdlib `csv` module).

## What's queued
- **0.3.9.4 (Phase 4)** - Grammar-driven Linework Fix UI polish.
- **0.3.9.5 (Phase 5)** - Attribute display in UI + Validation Report.
- **0.4.0.0** - Integration release.

## Quick start (Windows)
Double-click **`run.bat`** at the project root.

## Run from source manually
```
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python -m pytest tests -q
python launcher.py
```
