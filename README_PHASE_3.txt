Rob's Code Wizard - Phase 3 Overlay (v0.4.3)
=============================================

PHASE 3 ADDS
------------
1. VDT <-> ODOT Linework Grammar Translator (grammar_translator.py)
   VDT B/E/BC/EC/CC/RC/CLS <-> ODOT BL*/EL*/BC*/EC*/OC*/CL* + numeric 1/2/3/4
   Ambiguous mappings (CC/RC->OC*, OC*/3->BC) are flagged.
2. Point Code Translator (code_translator.py) - uses translation_map.json
3. End-to-End Description Translator (description_translator.py)
4. Translation Tab UI: new "Translate Loaded Rows" bar with Source/Target
   dropdowns and Apply Translation button.

NEVER MODIFIED
--------------
Point numbers, N, E, Z are NEVER touched by translation.

RUN ORDER
---------
1. Extract this zip onto the Robs_Code_Wizard project root.
2. apply_phase_3.bat
3. No manual main_window.py edit needed.
4. Verify in app: open CSV, set Source/Target, click Apply Translation.
5. push_phase_3.bat
