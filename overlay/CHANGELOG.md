## v0.4.2 - 2026-06-20 - Phase 2: Translation Tab UI + Convert Line Connect Codes

### Added
- `app/ui/translation_tab.py` - new "Translation" tab inserted between Raw Data
  and Linework Fix. Three-column layout, confidence/type/code filters, color
  coded rows, right-side review pane for ODOT override + notes.
- `app/ui/translation_review_pane.py` - per-entry override editor.
- `app/ui/convert_line_connect_dialog.py` - Tools menu dialog for
  Numeric -> Alphabetic line-connect conversion. Reverse direction is
  reserved for v0.4.5 (OpenRoads export phase).
- `app/services/linework_parser.py` - tokenize/classify/parse for ODOT and
  VDT linework grammars. Handles numeric line-connect commands (1=BL*,
  2=EL*, 3=OC*, 4=CL*) and distinguishes them from numeric-suffixed point
  codes (EP1, DR1, WALK1, ...).
- `app/services/line_connect_translator.py` - forward (numeric->alpha)
  conversion + preview helpers.
- `tests/fixtures/` - curated subsets of the 241867 PNEZD files used as
  canonical real-world test data.
- `tests/test_linework_parser.py` and `tests/test_line_connect_translator.py`.

### Notes
- main_window.py is NOT modified by the overlay (per the v0.4.1.1 hotfix
  rule). See `app/ui/main_window_patch.py` for the integration snippets:
    1. insertTab(1, TranslationTab(self), "Translation")
    2. Tools menu top-level entry "Convert Line Connect Codes..."
    3. _open_convert_line_connect_dialog handler
- ODOT numeric line-connect mapping (locked in):
    1 -> BL* (Begin Line)
    2 -> EL* (End Line)
    3 -> OC* (Open Curve)
    4 -> CL* (Close Shape)
- Parallel-string collection (e.g., both sides of pavement simultaneously)
  is handled by digit-suffixed POINT CODES (EP/EP1, DR/DR1, WALK/WALK1),
  not line-connect commands.
